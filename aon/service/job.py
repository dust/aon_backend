from decimal import Decimal
import traceback
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
import pandas as pd
import requests
from flask_caching import SimpleCache

from aon.graph import *
from aon.model import *
from aon.core import db, scheduler


logger = logging.getLogger(__name__)

THIRTY_MINS = 1
STR_THIRTY_MINS = '1min'
SIMPLE_CACHE = SimpleCache()
ZERO = Decimal("0")
QUOTE_SYMBOL="BNBUSDT"

@scheduler.task('interval', id='eth_price_job', seconds=30, misfire_grace_time=900)
def eth_price():
    resp = requests.get("https://api.coingecko.com/api/v3/coins/binancecoin/tickers",headers={'accept': "application/json"})
    # resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbol="+QUOTE_SYMBOL, headers={'accept': "application/json"})
    if resp.status_code == 200:
        js = resp.json()
        if 'tickers' in js and len(js['tickers']) >0:
        # if 'price' in js:
            for ticker in js['tickers']:
                if ticker['target']=='USDT':
                    global SIMPLE_CACHE
                    SIMPLE_CACHE.set(QUOTE_SYMBOL, Decimal(str(ticker['last'])), 0)
            # SIMPLE_CACHE.set(QUOTE_SYMBOL, Decimal(str(js['price'])), 0)
    resp.close()

def eth_num(amt: np.float64):
    try:
        # t=type(amt)
        # print(f"type={t}|amt={amt}")
        return Decimal(str(amt/(10**18)))
    except Exception as ex:
        logger.error(f"eth_num: {amt}, ex:{ex}")

@scheduler.task('interval', id='fetch_all', seconds=59, misfire_grace_time=900)
def fetch_all():
    # sess = init_session()
    with db.app.app_context():
        try:
            retrieve_trade(db.session)
            retrieve_token(db.session)
            retrieve_listed(db.session)
            gen_kline(db.session)
        finally:
            pass
            # sess.close()

def gen_kline(sess: Session):
    tokens = sess.query(Token).order_by(Token.index_id.desc()).all()
    for t in tokens:
        gen_token_kline_1min(sess, t.contract_address)

def fill_0sec_trade(sess: Session, token:str, trades: List[Trade]) -> List[Any]:
    i = 0
    lst = []
    for t in trades:
        tt = datetime.fromtimestamp(t.ctime)
        # eth_price = t.eth_price
        if i == 0:
            open_ts = tt-timedelta(seconds=tt.second)
            last_kline = sess.query(Kline).filter(Kline.token_address==token, Kline.open_ts<=open_ts.timestamp()).order_by(Kline.open_ts.desc()).limit(1).first()
            if last_kline is None:
                # 第一条成交记录
                lst.append([open_ts, Decimal("0.0000000001"), ZERO, ZERO])
            elif last_kline.open_ts == open_ts.timestamp():
                # 同一周期内重复产生kline， 仍然使用周期内开盘价
                lst.append([open_ts, last_kline.o, ZERO, ZERO])
            else:
                # 本周期以前，使用上周期收盘价
                lst.append([open_ts, last_kline.c, ZERO, ZERO])
        else:
            if tt.second > 0:
                # 不是当前周期（分钟)的第0秒, 追加当前周期（分钟）的第一秒
                previous = trades[i-1]
                lst.append([tt-timedelta(seconds=tt.second),previous.last_price,ZERO,ZERO])
        i += 1
        lst.append([tt, t.last_price, t.amount, t.eth_amount])

    return lst


def gen_token_kline_1min(sess:Session, token: str):
    
    # 最后一根k线的开盘时间
    latest_open_ts = sess.query(Kline.open_ts).filter(Kline.token_address==token).order_by(Kline.open_ts.desc()).limit(1).scalar()
    
    if latest_open_ts is None:
        # kline没有数据，使用第一条的成交数据的时间
        latest_open_ts = sess.query(Trade.ctime).filter(Trade.token_address==token).order_by(Trade.ctime.asc()).limit(1).scalar()
        if latest_open_ts is None:
            # no trade
            return
    
    # 查询最后一条k线的时间 或 第一条成交数据的时间 之后（含）的所有成交数据。
    trades = sess.query(Trade).filter(Trade.token_address == token, Trade.ctime>=latest_open_ts).order_by(Trade.ctime.asc()).all()
    if trades is None or len(trades) == 0:
        return
    
    rows = fill_0sec_trade(sess, token, trades)
    
    df = pd.DataFrame(
        [
            {
                "price": np.float64(row[1]),
                "volume": np.float64(row[2]),
                "eth_vol": np.float64(row[3]),
                "ctime": row[0],
            }
            for row in rows
        ]
    )
    if df.empty:
        return
    df = df.set_index("ctime").sort_index()
    ohlcv = df.resample(STR_THIRTY_MINS).agg({'price':'ohlc', 'volume':'sum', 'eth_vol':'sum'})
    # ohlcv['volume']['volume'].replace(0, np.nan, inplace=True)
    # ohlcv['eth_vol']['eth_vol'].replace(0, np.nan, inplace=True)
    ohlcv.dropna(inplace=True)
    idx = ohlcv.index
    try:
        for i in idx:
            open_ts = i.to_pydatetime().timestamp()
            open_price = Decimal(str(ohlcv['price']['open'][i]))
            v = Decimal(str(ohlcv['volume']['volume'][i]))
            if v > ZERO:
                k = sess.query(Kline).filter(Kline.token_address==token, Kline.open_ts==open_ts).first()
                if k is not None:
                    k.h=Decimal(str(ohlcv['price']['high'][i]))
                    k.l=Decimal(str(ohlcv['price']['low'][i]))
                    k.c=Decimal(str(ohlcv['price']['close'][i]))
                    k.vol = v
                    k.amount = Decimal(str(ohlcv['eth_vol']['eth_vol'][i]))
                else:
                    k = Kline(
                        token_address=token,
                        open_ts=open_ts,
                        o=open_price,
                        h=Decimal(str(ohlcv['price']['high'][i])),
                        l=Decimal(str(ohlcv['price']['low'][i])),
                        c=Decimal(str(ohlcv['price']['close'][i])),
                        vol=v,
                        amount=Decimal(str(ohlcv['eth_vol']['eth_vol'][i])),
                        cnt=0,
                        buy_vol=0,
                        buy_amount=0,
                        close_ts=(i.to_pydatetime()+timedelta(minutes=THIRTY_MINS)).timestamp()
                    )
                    sess.add(k)
                sess.commit()
    except Exception as ex:
        sess.rollback()
        logger.error(f"gen_token_kline_1min: {ex}, {token}")

def retrieve_listed(sess: Session):
    last_index = get_listed_token_last_index(sess)
    listed_df = fetch_listed_token(last_index)
    if listed_df is not None and not listed_df.empty:
        df_idx = listed_df.index
        try:
            for i in df_idx:
                pair = listed_df['listedTokens_pair'][i]
                contract_address = listed_df['listedTokens_token_id'][i]
                index_id = int(i)
                # blk_num = listed_df['listedTokens_blockNum'][i]
                ts = datetime.datetime.fromtimestamp(listed_df['listedTokens_timestamp'][i])
                makesure_listed_token(sess, contract_address, pair, index_id, ts)
            sess.commit()
        except Exception as ex:
            sess.rollback()
            traceback.print_exception(ex)
            logger.error(f"retrieve_listed: {ex}")





def retrieve_token(sess: Session):
    last_index = get_token_last_index(sess)
    token_df = fetch_token(last_index)
    if token_df is not None and not token_df.empty:
        df_idx = token_df.index
        try:
            for i in df_idx:
                name = token_df['tokens_name'][i]
                symbol = token_df['tokens_symbol'][i]
                contract_address = token_df['tokens_id'][i]
                index_id = int(token_df['tokens_index'][i])
                listed = 1 if token_df['tokens_listed'][i] else 0
                aon_fee = eth_num(token_df['tokens_aonFee'][i])
                price = eth_num(token_df['tokens_price'][i])
                creator = token_df['tokens_creator'][i]
                holder_cnt = int(token_df['tokens_holdersCount'][i])
                makesure_token(sess, Token(
                    contract_address=contract_address,
                    name=name,
                    symbol=symbol,
                    index_id=index_id,
                    listed=listed,
                    aon_fee=aon_fee,
                    price=price,
                    creator=creator,
                    holder_cnt=holder_cnt
                    ))
            sess.commit()
        except Exception as ex:
            sess.rollback()
            logger.error(f"retrieve_token: {ex}")


def retrieve_trade(sess: Session):
    last_index = get_trade_last_index(sess)
    trade_df = fetch_trade(index=last_index)
    if trade_df is not None and not trade_df.empty:
        df_idx = trade_df.index
        global SIMPLE_CACHE
        try:
            for i in df_idx:
                # print(trade_df['tokenTrades_id'][i], trade_df['tokenTrades_transHash'][i])
                try:
                    eth_amount = eth_num(trade_df['tokenTrades_ethAmount'][i])
                    amount = eth_num(trade_df['tokenTrades_amount'][i])
                    trade = Trade(
                        id=trade_df['tokenTrades_id'][i],
                        tx_id=trade_df['tokenTrades_transHash'][i],
                        index_id=int(i),
                        token_address=trade_df['tokenTrades_token_id'][i],
                        trader=trade_df['tokenTrades_trader'][i],
                        eth_amount=eth_amount,
                        amount=amount,
                        price=eth_amount/amount,
                        last_price=eth_num(trade_df['tokenTrades_price'][i]),
                        is_buy=1 if trade_df['tokenTrades_isBuy'][i] else 0,
                        aon_fee=eth_num(trade_df['tokenTrades_aonFee'][i]),
                        eth_price=SIMPLE_CACHE.get(QUOTE_SYMBOL) if SIMPLE_CACHE.get(QUOTE_SYMBOL) else Decimal("690.4"),
                        ctime=int(trade_df['tokenTrades_timestamp'][i])
                        )
                    sess.add(trade)
                except Exception as ex:
                    traceback.print_exception(ex)
            sess.commit()
        except Exception as ex:
            sess.rollback()
            traceback.print_exception(ex)
            logger.error(f"retrieve_trade {ex}")
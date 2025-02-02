from decimal import Decimal
from datetime import datetime, timedelta
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

@scheduler.task('interval', id='eth_price_job', seconds=30, misfire_grace_time=900)
def eth_price():
    resp = requests.get("https://api.coingecko.com/api/v3/coins/ethereum/tickers",headers={'accept': "application/json"})
    if resp.status_code == 200:
        js = resp.json()
        if 'tickers' in js and len(js['tickers']) >0:
            global SIMPLE_CACHE
            SIMPLE_CACHE.set("ETHUSDT", Decimal(str(js['tickers'][0]['last'])), 0)
    resp.close()

def eth_num(amt: np.float64):
    return Decimal(str(amt/(10**18)))

@scheduler.task('interval', id='fetch_all', seconds=11, misfire_grace_time=900)
def fetch_all():
    # sess = init_session()
    with db.app.app_context():
        try:
            retrieve_trade(db.session)
            retrieve_token(db.session)
            gen_kline(db.session)
        finally:
            pass
            # sess.close()

def gen_kline(sess: Session):
    tokens = sess.query(Token).order_by(Token.index_id.desc()).all()
    for t in tokens:
        gen_token_kline_1min(sess, t.contract_address)

def gen_token_kline_1min(sess:Session, token: str):
    
    # 最后一根k线的开盘时间
    latest_open_ts = sess.query(Kline.open_ts).filter(Kline.token_address==token).order_by(Kline.open_ts.desc()).limit(1).scalar()
    
    if latest_open_ts is None:
        # kline没有数据，使用第一条的成交数据的时间
        latest_open_ts = sess.query(Trade.ctime).filter(Trade.token_address==token).order_by(Trade.ctime.asc()).limit(1).scalar()
        if latest_open_ts is None:
            # no trade
            return
    # else:
    #     latest_open_ts = latest_open_ts + timedelta(minutes=THIRTY_MINS)
    
    # latest_open_ts, 为最后一条k线的时间 或 第一条成交数据的时间 之后（含）的所有成交数据。
    rows = sess.query(Trade).filter(Trade.token_address == token, Trade.ctime>=latest_open_ts).order_by(Trade.ctime.asc()).all()
    if rows is None or len(rows) == 0:
        return
    
    df = pd.DataFrame(
        [
            {
                "price": np.float64(row.last_price),
                "volume": np.float64(row.amount),
                "eth_vol": np.float64(row.eth_amount),
                "ctime": row.ctime,
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
        count = 0
        for i in idx:
            open_ts = i.to_pydatetime().timestamp()
            if count == 0:
                last_close = sess.query(Kline.c).filter(Kline.token_address==token, Kline.open_ts<open_ts).order_by(Kline.open_ts.desc()).limit(1).scalar()
                if last_close and last_close > Decimal(0):
                    # 当前成交之前有成交记录，使用之前的收盘价
                    open_price = last_close
                else:
                    # 第一条成交记录
                    open_price = Decimal(str(ohlcv['price']['open'][i]))
            else:
                # 本批数据中，第n（大于1)成交。
                loc = ohlcv.index.get_loc(i)
                previous = ohlcv.index[loc - 1]
                open_price = Decimal(str(ohlcv['price']['close'][previous]))
            v = Decimal(str(ohlcv['volume']['volume'][i]))
            if v > Decimal(0):
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
                count += 1
    except Exception as ex:
        sess.rollback()
        logger.error(f"{ex}")

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
            logger.error(f"{ex}")


def retrieve_trade(sess: Session):
    last_index = get_trade_last_index(sess)
    trade_df = fetch_trade(index=last_index)
    if trade_df is not None and not trade_df.empty:
        df_idx = trade_df.index
        global SIMPLE_CACHE
        try:
            for i in df_idx:
                # print(df['tokens_id'][i])
                eth_amount = eth_num(trade_df['tokenTrades_ethAmount'][i])
                amount = eth_num(trade_df['tokenTrades_amount'][i])
                trade = Trade(
                    id=trade_df['tokenTrades_id'][i],
                    tx_id=trade_df['tokenTrades_transHash'][i],
                    index_id=int(trade_df['tokenTrades_index'][i]),
                    token_address=trade_df['tokenTrades_token_id'][i],
                    trader=trade_df['tokenTrades_trader'][i],
                    eth_amount=eth_amount,
                    amount=amount,
                    price=eth_amount/amount,
                    last_price=eth_num(trade_df['tokenTrades_price'][i]),
                    is_buy=1 if trade_df['tokenTrades_isBuy'][i] else 0,
                    aon_fee=eth_num(trade_df['tokenTrades_aonFee'][i]),
                    eth_price=SIMPLE_CACHE.get("ETHUSDT"),
                    ctime=i.to_pydatetime()
                            )
                sess.add(trade)
            sess.commit()
        except Exception as ex:
            sess.rollback()
            logger.error(f"{ex}")
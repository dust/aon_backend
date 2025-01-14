from decimal import Decimal
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import requests

from aon.graph import *
from aon.model import *
from aon.core import db, scheduler,cache


logger = logging.getLogger(__name__)

@scheduler.task('interval', id='eth_price_job', seconds=30, misfire_grace_time=900)
def eth_price():
    # print("my_job:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    resp = requests.get("https://api.coingecko.com/api/v3/coins/ethereum/tickers",headers={'accept': "application/json"})
    if resp.status_code == 200:
        js = resp.json()
        if 'tickers' in js and len(js['tickers']) >0:
            cache.set("ETHUSDT", Decimal(str(js['tickers'][0]['last'])), 0)
    resp.close()


def eth_num(amt: np.float64):
    return Decimal(str(amt/(10**18)))

@scheduler.task('interval', id='fetch_all', seconds=300, misfire_grace_time=900)
def fetch_all():
    sess = init_session()
    try:
        retrieve_trade(sess)
        retrieve_token(sess)
        gen_kline(sess)
    finally:
        sess.close()

def gen_kline(sess: Session):
    tokens = sess.query(Token).order_by(Token.index_id.desc()).all()
    for t in tokens:
        gen_token_kline_1min(sess, t.contract_address)

def gen_token_kline_1min(sess:Session, token: str):
    latest_open_ts = sess.query(Kline.open_ts).filter(Kline.token_address==token).order_by(Kline.open_ts.desc()).limit(1).scalar()
    if latest_open_ts is None:
        latest_open_ts = sess.query(Trade.ctime).filter(Trade.token_address==token).order_by(Trade.ctime.asc()).limit(1).scalar()
        if latest_open_ts is None:
            # no trade
            return
    else:
        latest_open_ts = datetime.fromtimestamp(latest_open_ts) + timedelta(minutes=1)
    
    rows = sess.query(Trade).filter(Trade.token_address == token, Trade.ctime>=latest_open_ts).order_by(Trade.ctime.asc()).all()
    df = pd.DataFrame(
        [
            {
                "price": np.float64(row.price),
                "volume": np.float64(row.amount),
                "eth_vol": np.float64(row.eth_amount),
                "ctime": row.ctime,
            }
            for row in rows
        ]
    ).set_index("ctime").sort_index()
    ohlcv = df.resample('1min').agg({'price':'ohlc', 'volume':'sum', 'eth_vol':'sum'})
    ohlcv = ohlcv.ffill()
    idx = ohlcv.index
    count = 0
    try:
        for i in idx:
            sess.add(Kline(
                token_address=token,
                open_ts=i.to_pydatetime(),
                o=Decimal(str(ohlcv['price']['open'][i])),
                h=Decimal(str(ohlcv['price']['high'][i])),
                l=Decimal(str(ohlcv['price']['low'][i])),
                c=Decimal(str(ohlcv['price']['close'][i])),
                vol=Decimal(str(ohlcv['volume']['volume'][i])),
                amount=Decimal(str(ohlcv['eth_vol']['eth_vol'][i])),
                cnt=0,
                buy_vol=0,
                buy_amount=0,
                close_ts=i.to_pydatetime()+timedelta(minutes=1)
            ))
            count += 1
            if count % 100 == 0 or count >= len(idx) -1:
                sess.commit()
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
                    is_buy=1 if trade_df['tokenTrades_isBuy'][i] else 1,
                    aon_fee=eth_num(trade_df['tokenTrades_aonFee'][i]),
                    eth_price=cache.get("ETHUSDT"),
                    ctime=i.to_pydatetime()
                            )
                sess.add(trade)
            sess.commit()
        except Exception as ex:
            sess.rollback()
            logger.error(f"{ex}")
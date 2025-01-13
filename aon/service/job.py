from decimal import Decimal
from datetime import datetime
import numpy as np
import requests

from aon.graph import *
from aon.model import *
from aon.core import db, scheduler,cache


logger = logging.getLogger(__name__)

@scheduler.task('interval', id='eth_price_job', seconds=30, misfire_grace_time=900)
def eth_price():
    # print("my_job:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT")
    if resp.status_code == 200:
        js = resp.json()
        print(js)
        cache.set(js['symbol'], Decimal(js['price']))
    resp.close()


def eth_num(amt: np.float64):
    return Decimal(str(amt/(10**18)))

@scheduler.task('interval', id='fetch_all', seconds=300, misfire_grace_time=900)
def fetch_all():
    sess = init_session()
    try:
        retrieve_trade(sess)
        retrieve_token(sess)
    finally:
        sess.close()

def retrieve_token(sess: Session):
    last_index = get_token_last_index(sess)
    token_df = fetch_token(last_index)
    if token_df is not None and not token_df.empty:
        df_idx = token_df.index
        sess.begin()
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
        sess.begin()
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
                    is_buy=1 if trade_df['tokenTrades_isBuy'][i] else 1,
                    aon_fee=eth_num(trade_df['tokenTrades_aonFee'][i]),
                    eth_price=cache.get("ETHUSDT")
                            )
                sess.add(trade)
            sess.commit()
        except Exception as ex:
            sess.rollback()
            logger.error(f"{ex}")
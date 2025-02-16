from decimal import Decimal
from flask import Blueprint
from flask import request
from aon.core import cache
from aon.service.token import *
import requests


digest_router = Blueprint("digest", __name__, url_prefix='/digest')


@digest_router.route("/ethPrice", methods=["GET"])
@cache.cached(timeout=30)
def eth_price():
    QUOTE_SYMBOL = "BNBUSDT"
    resp = requests.get("https://api.coingecko.com/api/v3/coins/binancecoin/tickers",headers={'accept': "application/json"})
    # resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbol="+QUOTE_SYMBOL, headers={'accept': "application/json"})
    if resp.status_code == 200:
        js = resp.json()
        #if 'price' in js:
        if 'tickers' in js and len(js['tickers']) >0:
            for ticker in js['tickers']:
                if ticker['target']=='USDT':
                    #cache.set(QUOTE_SYMBOL, Decimal(str(js['price'])), 0)
                    cache.set(QUOTE_SYMBOL, Decimal(str(ticker['last'])), 0)
    
    res = ResMsg(data=cache.get(QUOTE_SYMBOL))
    return res.data

def make_24h_key():
    token = request.args.get("token", "")
    return f"/digest/24h:{token}"

@digest_router.route("/24h", methods=['GET'])
@cache.cached(timeout=31, make_cache_key=make_24h_key)
def token_24h():
    return ticker_24h(request)
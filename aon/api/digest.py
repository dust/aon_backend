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
    resp = requests.get("https://api.coingecko.com/api/v3/coins/ethereum/tickers",headers={'accept': "application/json"})
    if resp.status_code == 200:
        js = resp.json()
        if 'tickers' in js and len(js['tickers']) >0:
            cache.set("ETHUSDT", Decimal(str(js['tickers'][0]['last'])), 0)
    res = ResMsg(data=cache.get("ETHUSDT"))
    return res.data

def make_24h_key():
    token = request.args.get("token", "")
    return f"/digest/24h:{token}"

@digest_router.route("/24h", methods=['GET'])
@cache.cached(timeout=31, make_cache_key=make_24h_key)
def token_24h():
    return ticker_24h(request)
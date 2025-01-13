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
    resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT")
    if resp.status_code == 200:
        js = resp.json()
        cache.set(js['symbol'], Decimal(js['price']))
    res = ResMsg(data=cache.get("ETHUSDT"))
    return res.data

@digest_router.route("/24h", methods=['GET'])
def token_24h():
    return ticker_24h(request)
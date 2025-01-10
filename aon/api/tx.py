from flask import Blueprint
from flask import request
from aon.service.token import *


tx_router = Blueprint("tx", __name__, url_prefix='/tx')


@tx_router.route("/recently", methods=["GET"])
def recently():
    return recent_trade(request)

@tx_router.route("/kline", methods=['GET'])
def kline():
    return kline_item(request)
import re
import logging

from aon.code import ResponseCode
from aon.response import ResMsg
from aon.core import db
from aon.model import Token, Trade, Kline, ListedToken


logger = logging.getLogger(__name__)


def create_token(request):
    symbol = request.json.get('symbol', '')
    res = ResMsg()

    if not symbol:
        res.update(code=ResponseCode.InvalidParameter)
        return res.data

    t = db.session.query(Token).filter(Token.symbol==symbol).first()
    
    if t:
       res.update(code=ResponseCode.InvalidParameter)
       return res.data
    t = Token(
        name=request.json.get("name"),
        symbol=symbol,
        contract_address=request.json.get("contract"),
        image=request.json.get("image"),
        creator=request.json.get("creator"),
        tags=request.json.get("tags"),
        description=request.json.get("description"),
        website=request.json.get("website"),
        tg=request.json.get("tg"),
        x=request.json.get("x")
    )
    db.session.add(t)
    db.session.commit()
    return res.data

def list_token(request):
    page_no = request.args.get('pageNo', default=1, type=int)
    page_size = request.args.get('pageSize', default=10, type=int)
    if page_no < 1:
        page_no = 1
    if page_size > 100 or page_size < 1:
        page_size = 10
    rows = db.session.query(Token).order_by(Token.index_id.desc()).offset((page_no-1)*page_size).limit(page_size).all()
    res = ResMsg(data=rows)

    # if not pubkey:
    #     res.update(code=ResponseCode.InvalidParameter)
    #     return res.data
    # logger.info("res.data= %s", res.data)
    return res.data

def detail_token(request):
    res = ResMsg()
    return res.data

def top_holder(request):
    res = ResMsg()
    return res.data

def my_token(request):
    res = ResMsg()
    return res.data
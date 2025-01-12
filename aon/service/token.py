import re
import logging

from aon.code import ResponseCode
from aon.response import ResMsg
from aon.core import db
from aon.model import Token, Trade, Kline, ListedToken
from aon.graph import fetch_top_holder
from aon.service.job import eth_num


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
        creator=request.json.get("createdBy"),
        tags=request.json.get("tags"),
        description=request.json.get("description"),
        website=request.json.get("website"),
        tg=request.json.get("tg"),
        x=request.json.get("x"),
        index_id=0
    )
    db.session.add(t)
    db.session.commit()
    return res.data

def list_token(request):
    (page_no, page_size) = get_page_args(request)
    rows = db.session.query(Token).order_by(Token.index_id.desc()).offset((page_no-1)*page_size).limit(page_size).all()
    res = ResMsg(data=rows)
    return res.data

def detail_token(request):
    token = request.args.get("contract", "")
    if not token:
        res.update(code=ResponseCode.InvalidParameter)
        return res.data
    t = db.session.query(Token).filter(Token.contract_address == token).one_or_none()
    res = ResMsg(data=t)
    return res.data

def recent_trade(request):
    token = request.args.get("token", "")
    if not token:
        res = ResMsg()
        res.update(code=ResponseCode.InvalidParameter)
        return res.data
    rows = db.session.query(Trade).filter(Trade.token_address == token).order_by(Trade.ctime.desc()).limit(100).all()
    res = ResMsg(data=rows)
    return res.data

def kline_item(request):
    token = request.args.get("token", "")
    if not token:
        res.update(code=ResponseCode.InvalidParameter)
        return res.data
    (page_no, page_size) = get_page_args(request)
    rows = db.session.query(Kline).filter(Kline.token_address == token).order_by(Kline.ctime.desc()).offset((page_no-1)*page_size).limit(page_size).all()
    res = ResMsg(data=rows)
    return res.data

def top_holder(request):
    token = request.args.get("token", "")
    if not token:
        res = ResMsg()
        res.update(code=ResponseCode.InvalidParameter)
        return res.data
    
    df = fetch_top_holder(token)
    rows = []
    if df is not None and not df.empty:
        idx = df.index
        rows = [{'holder': df['tokenHolders_holder'][i], 'amount':eth_num(df['tokenHolders_amount'][i]), 'id':df['tokenHolders_id'][i]} for i in idx]
    res = ResMsg(data=rows)
    return res.data

def my_token(request):
    my_address = request.args.get("address", "")
    res = ResMsg()
    if not my_address:
        res.update(code=ResponseCode.InvalidParameter)
        return res.data
    (page_no, page_size) = get_page_args(request)
    
    rows = db.session.query(Token).filter(Token.creator==my_address).order_by(Token.index_id.desc()).offset((page_no-1)*page_size).limit(page_size).all()
    res = ResMsg(data=rows)
    
    return res.data

def get_page_args(request, def_pn=1, def_ps=10):
    page_no = request.args.get('pageNo', default=1, type=int)
    page_size = request.args.get('pageSize', default=10, type=int)
    if page_no < 1:
        page_no = def_pn
    if def_ps == 10 and (page_size > 100 or page_size < 1):
        page_size = def_ps
    if def_ps > 10:
        page_size = def_ps
    return (page_no, page_size)
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from sqlalchemy import text, func
import requests

from aon.code import ResponseCode
from aon.response import ResMsg
from aon.core import db
from aon.model import Token, Trade, Kline, ListedToken, RelatedToken
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
        source=1,
        index_id=0
    )
    db.session.add(t)
    # print(f"t:{t}")
    db.session.commit()
    return res.data

def add_agent_key(request):
    app_key = request.json.get("appKey", "")
    token = request.json.get("token", "")
    res = ResMsg()

    if not app_key or not token:
        res.update(code=ResponseCode.InvalidParameter)
        return res.data
    
    resp = requests.get(f"https://api.iaon.ai/functions/v1/app/{app_key}", headers={'accept': "application/json"})
    '''
    {"code":200,"message":"","data":{"icon":"","cover":"","title":"school-uniform-app-373","url":"https://school-uniform-app-373.aonmesh.ai"}}
    '''
    if resp.status_code == 200:
        js = resp.json()
        if js['code'] == 200:
            data = js['data']
            icon = data['icon']
            cover = data['cover']
            title = data['title']
            url = data['url']
            related_token = db.session.query(RelatedToken).filter(RelatedToken.token_address==token, RelatedToken.app_key==app_key).first()
            if related_token:
                related_token.app_icon = icon
                related_token.app_cover =cover
                related_token.app_title = title
                related_token.app_url = url
            else:
                related_token = RelatedToken(
                    token_address=token,
                    app_key = app_key,
                    app_icon = icon,
                    app_cover = cover,
                    app_title= title,
                    app_url = url
                )
                db.session.add(related_token)
            db.session.commit()
            res.update(data=data)
            return res.data

    res.update(code=ResponseCode.NoResourceFound)
    return res.data

def related_app(request):
    token = request.args.get("token")
    res = ResMsg()

    if not token:
        res.update(code=ResponseCode.InvalidParameter)
        return res.data

    related_apps = db.session.query(RelatedToken).filter(RelatedToken.token_address == token).limit(3).all()
    res.update(data=related_apps)
    return res.data


def list_token(request):
    (page_no, page_size) = get_page_args(request)
    rows = db.session.query(Token).filter(Token.source==1).order_by(Token.ctime.desc()).offset((page_no-1)*page_size).limit(page_size).all()
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
    (page_no, page_size) = get_page_args(request,def_ps=1440)
    rows = db.session.query(Kline).filter(Kline.token_address == token).order_by(Kline.open_ts.asc()).offset((page_no-1)*page_size).limit(page_size).all()
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

def ticker_24h(request):
    token = request.args.get("token", "")
    if not token:
        res = ResMsg()
        res.update(code=ResponseCode.InvalidParameter)
        return res.data
    
    end = datetime.now()
    begin = datetime.now() - timedelta(days=1)
    d = {'volume': 0, 'price': 0.0000, 'change':0.00000, 'percentage':"0.00"}
    try:
        first_open = db.session.query(Trade.last_price).filter(Trade.token_address==token, Trade.ctime.between(begin, end)).order_by(Trade.ctime.asc()).limit(1).scalar()
        last_close = db.session.query(Trade.last_price).filter(Trade.token_address==token, Trade.ctime.between(begin, end)).order_by(Trade.ctime.desc()).limit(1).scalar()
        sum_amount = db.session.query(func.sum(Trade.amount)).filter(Trade.token_address==token, Trade.ctime.between(begin, end)).limit(1).scalar()
        last_price = db.session.query(Trade.last_price).filter(Trade.token_address==token).order_by(Trade.ctime.desc()).limit(1).scalar()
        
        d.update({
            'change': last_close - first_open if last_close else Decimal(0),
            'percentage': Decimal(0) if last_close is None or first_open == Decimal(0) else (last_close - first_open)/first_open,
            'volume': sum_amount if sum_amount else Decimal(0),
            'price': last_price if last_price else Decimal(0)
        })
    except Exception as ex:
        logger.error(f"{ex}")
    res = ResMsg(data=d)
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
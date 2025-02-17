import datetime
import decimal
import uuid

from flask_caching import Cache
from flask.json import JSONEncoder as BaseJSONEncoder
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler

from aon.model import Token, Comment, Trade, Kline, RelatedToken

scheduler = APScheduler()

db = SQLAlchemy()
cache = Cache()


class JSONEncoder(BaseJSONEncoder):

    def default(self, o):
        """
        如有其他的需求可直接在下面添加
        :param o:
        :return:
        """
        if isinstance(o, Token):
            return JSONEncoder.fmt_token(o)
        if isinstance(o, Comment):
            return JSONEncoder.fmt_comment(o)
        if isinstance(o, Trade):
            return JSONEncoder.fmt_trade(o)
        if isinstance(o, Kline):
            return JSONEncoder.fmt_kline(o)
        if isinstance(o, RelatedToken):
            return JSONEncoder.fmt_related(o)
        if isinstance(o, datetime.datetime):
            # 格式化时间
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, datetime.date):
            # 格式化日期
            return o.strftime('%Y-%m-%d')
        if isinstance(o, decimal.Decimal):
            # 格式化高精度数字
            return "{:.18f}".format(o)
        if isinstance(o, uuid.UUID):
            # 格式化uuid
            return str(o)
        if isinstance(o, bytes):
            # 格式化字节数据
            return o.decode("utf-8")
        return super(JSONEncoder, self).default(o)
    
    @staticmethod
    def fmt_trade(o: Trade):
        return {
            'txId': o.tx_id,
            'id': o.id,
            'index': o.index_id,
            'price': o.price * o.eth_price,
            'trader': o.trader,
            'qty': o.amount,
            'quoteQty': o.eth_amount,
            'isBuy': True if o.is_buy == 1 else False,
            'ctime': o.ctime,
            'aonFee': o.aon_fee,
            'ethPrice': o.eth_price,
            'token': o.token_address
        }
    
    @staticmethod
    def fmt_related(o: RelatedToken):
        return {
            'appKey': o.app_key,
            'appIcon': o.app_icon,
            'appCover': o.app_cover,
            'appTitle': o.app_title,
            'appUrl': o.app_url
        }

    @staticmethod
    def fmt_kline(o: Kline):
        return [
            o.open_ts,
            o.o,
            o.h,
            o.l,
            o.c,
            o.vol,
            o.close_ts,
            o.amount,
            o.cnt,
            o.buy_vol,
            o.buy_amount,
            (o.c - o.o)/o.o
        ]

    @staticmethod
    def fmt_comment(o: Comment):
        base =  {
            'contract': o.contract_address,
            'creator': o.created_by,
            'content': o.content,
            'ctime': o.ctime,
            'id': o.id
        }
        return base

    @staticmethod
    def fmt_token(o: Token):
        base =  {
            'contract': o.contract_address,
            'name': o.name,
            'symbol': o.symbol,
            'price': o.price,
            'listed': True if o.listed else False,
            'creator': o.creator,
            'aonFee': o.aon_fee,
            'holderCnt': o.holder_cnt
        }
        dynamic_fields = []
        if o.listed_ctime:
            dynamic_fields.append(("listedCtime", o.listed_ctime))
        if o.pair_contract:
            dynamic_fields.append(("pair", o.pair_contract))
        if o.image:
            dynamic_fields.append(("image", o.image))
        if o.tags:
            dynamic_fields.append(("tags", o.tags))
        if o.description:
            dynamic_fields.append(("description", o.description))
        if o.website:
            dynamic_fields.append(("website", o.website))
        if o.tg:
            dynamic_fields.append(("tg", o.tg))
        if o.x:
            dynamic_fields.append(("x", o.x))
        if len(dynamic_fields) > 0:
            base.update(dynamic_fields)
        return base
import datetime
import decimal
import uuid

from flask.json import JSONEncoder as BaseJSONEncoder
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler

from aon.model import Token

scheduler = APScheduler()

db = SQLAlchemy()


class JSONEncoder(BaseJSONEncoder):

    def default(self, o):
        """
        如有其他的需求可直接在下面添加
        :param o:
        :return:
        """
        if isinstance(o, Token):
            return JSONEncoder.fmt_token(o)
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
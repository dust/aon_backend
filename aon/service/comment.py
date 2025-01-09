import re
import logging

from aon.code import ResponseCode
from aon.response import ResMsg
from aon.core import db
from aon.model import Comment, Token


logger = logging.getLogger(__name__)


def post_comment(request):
    token = request.json.get('token', '')
    if not token:
        res.update(code=ResponseCode.InvalidParameter)
        return res.data
    t = db.session.query(Token).filter(Token.contract_address==token).first()
    if t is None:
        res.update(code=ResponseCode.InvalidParameter)
        return res.data

    c = Comment(
        token=request.json.get('token'),
        content=request.json.get('content'),
        created_by=request.json.get('createdBy')
    )
    db.session.add(c)
    db.session.commit()

    res = ResMsg()
    return res.data

def list_comment(request):
    token = request.args.get("token")
    if not token:
        res.update(code=ResponseCode.InvalidParameter)
        return res.data
    page_no = request.args.get('pageNo', default=1, type=int)
    page_size = request.args.get('pageSize', default=10, type=int)
    if page_no < 1:
        page_no = 1
    if page_size > 1000 or page_size < 1:
        page_size = 10
    
    rows = db.session.query(Comment).filter(Comment.contract_address == token).order_by(Comment.ctime.desc()).offset((page_no-1)*page_size).limit(page_size).all()
    res = ResMsg(data=rows)
    return res.data
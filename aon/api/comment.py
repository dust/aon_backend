from flask import Blueprint
from flask import request
from aon.service.comment import *


comment_router = Blueprint("comment", __name__, url_prefix='/comment')


@comment_router.route("/post", methods=["POST"])
def post():
    return post_comment(request)

@comment_router.route("/list", methods=['GET'])
def list():
    return list_comment(request)


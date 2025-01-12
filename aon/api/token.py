from flask import Blueprint
from flask import request
from flask_caching import Cache
from aon.service.token import *
from aon.core import cache


token_router = Blueprint("token", __name__, url_prefix='/token')


@token_router.route("/create", methods=["POST"])
def create():
    return create_token(request)

@token_router.route("/detail", methods=['GET'])
def detail():
    return detail_token(request)

@token_router.route("/list", methods=['GET'])
def list():
    return list_token(request)

def make_holer_key():
    token = request.args.get("token", "")
    return f"/token/holder:{token}"

@token_router.route("/holder", methods=['GET'])
@cache.cached(timeout=600, make_cache_key=make_holer_key)
def holder():
    return top_holder(request)

@token_router.route("/my", methods=['GET'])
def my():
    return my_token(request)
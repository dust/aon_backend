from flask import Blueprint
from flask import request
from aon.service.token import *


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

@token_router.route("/holder", methods=['GET'])
def holder():
    return top_holder(request)

@token_router.route("/my", methods=['GET'])
def my():
    return my_token(request)
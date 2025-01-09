# _*_ coding=utf-8 _*_
from aon.code import ResponseCode


class BaseError(Exception):
    def __init__(self, response_code=0):
        self.response_code = response_code


class SystemError(BaseError):
    def __init__(self):
        super().__init__(ResponseCode.SystemError)

class ApiTokenError(BaseError):
    def __init__(self):
        super().__init__(ResponseCode.ApiTokenError)


class CurrencyValError(BaseError):
    def __init__(self):
        super().__init__(ResponseCode.ApiTokenError)


class ParamValidateError(BaseError):
    def __init__(self):
        super().__init__(ResponseCode.ParamValidateError)
from aon.api.token import token_router
from aon.api.comment import comment_router
from aon.api.tx import tx_router


router = [
    token_router,
    comment_router,
    tx_router
]

import os
import logging
import urllib.parse
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, SMALLINT, text, TIMESTAMP
from sqlalchemy.orm import sessionmaker, Session, declarative_base


SUPABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URI", "postgresql://postgres.exsligkuvicrfiirsmdg:H2FrhBZv1PRE9sf2@aws-0-eu-central-1.pooler.supabase.com:6543/postgres")
parsed = urllib.parse.urlparse(SUPABASE_URL)
database_url = f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}{parsed.path}"

engine = create_engine(database_url, echo=True)

Base = declarative_base()

class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_address = Column(String, nullable=False)
    avatar = Column(String)
    content = Column(String, nullable=False)
    created_by = Column(String, nullable=False)
    ctime = Column(TIMESTAMP, nullable=False, server_default=text("current_timestamp"))

class RelatedToken(Base):
    __tablename__ = 'related_token'

    token_address = Column(String, nullable=False, primary_key=True)
    app_key = Column(String, nullable=False, primary_key=True)
    app_icon = Column(String, nullable=False)
    app_cover = Column(String, nullable=False)
    app_title = Column(String, nullable=False)
    app_url = Column(String, nullable=False)
    ctime = Column(TIMESTAMP, nullable=False, server_default=text("current_timestamp"))


class Token(Base):
    __tablename__ = "token"

    contract_address = Column(String, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    price = Column(DECIMAL(36,18), nullable=False, server_default=text("0.0000"))
    index_id = Column(Integer, nullable=False, server_default=text("0"))
    listed = Column(SMALLINT, nullable=False, server_default=text("0"))
    pair_contract = Column(String)
    creator = Column(String, nullable=False)
    aon_fee = Column(DECIMAL(36,18), server_default=text("0"))
    holder_cnt = Column(Integer, server_default=text("0"))
    image = Column(String)
    tags = Column(String)
    description = Column(String)
    website = Column(String)
    tg = Column(String)
    x = Column(String)
    initial_buy = Column(DECIMAL(36,18))

    def __repr__(self):
        return f"<Token({self.symbol}, ('{self.name}'))>"

class ListedToken(Base):
    __tablename__ = "listed_token"

    contract_address = Column(String, nullable=False, primary_key=True)
    block_num = Column(Integer, nullable=False, server_default=text("0"))
    index_id = Column(Integer, nullable=False, server_default=text("0"))
    pair = Column(String, nullable=False)
    ctime = Column(TIMESTAMP, nullable=False, server_default=text("current_timestamp"))

class Trade(Base):
    __tablename__ = "trade"

    tx_id = Column(String, nullable=False, primary_key=True)
    id = Column(String)
    index_id = Column(Integer, nullable=False)
    token_address = Column(String, nullable=False)
    last_price = Column(DECIMAL(36,18), nullable=False)
    trader = Column(String, nullable=False)
    eth_amount = Column(DECIMAL(36,18), nullable=False, server_default=text("0.0000"))
    amount = Column(DECIMAL(36,18), nullable=False, server_default=text("0.0000"))
    price = Column(DECIMAL(36,18), nullable=False, server_default=text("0.0000"))
    is_buy = Column(SMALLINT, nullable=False)
    aon_fee = Column(DECIMAL(36,18))
    eth_price = Column(DECIMAL(36,18), nullable=False, server_default=text("0.0000"))
    ctime = Column(TIMESTAMP, nullable=False, server_default=text("current_timestamp"))

class Kline(Base):
    __tablename__ = "kline_1min"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    token_address = Column(String, nullable=False)
    open_ts = Column(Integer, nullable=False)
    o = Column(DECIMAL(36,18), nullable=False)
    h = Column(DECIMAL(36,18), nullable=False)
    l = Column(DECIMAL(36,18), nullable=False)
    c = Column(DECIMAL(36,18), nullable=False)
    vol = Column(DECIMAL(36,18), nullable=False)
    amount = Column(DECIMAL(36,18), nullable=False)
    cnt = Column(DECIMAL(36,18), nullable=False)
    buy_vol = Column(DECIMAL(36,18), nullable=False)
    buy_amount = Column(DECIMAL(36,18), nullable=False)
    close_ts = Column(Integer, nullable=False)
    ctime = Column(TIMESTAMP, nullable=False, server_default="current_timestamp")


def init_session():
    Session = sessionmaker(bind=engine)
    return Session()

def get_trade_last_index(sess: Session):
    latest_index = sess.query(Trade.index_id).order_by(Trade.index_id.desc()).limit(1).scalar()
    return latest_index if latest_index else 0

def get_token_last_index(sess: Session):
    latest_index = sess.query(Token.index_id).order_by(Token.index_id.desc()).limit(1).scalar()
    return latest_index if latest_index else 0

def get_listed_token_last_index(sess: Session):
    latest_index = sess.query(ListedToken.index_id).order_by(ListedToken.index_id.desc()).limit(1).scalar()
    return latest_index if latest_index else 0

def makesure_token(sess: Session, token: Token):
    t = sess.query(Token).filter(Token.contract_address == token.contract_address).first()
    if t is None:
        sess.add(token)
    else:
        t.holder_cnt = token.holder_cnt
        t.index_id = token.index_id
        t.listed = token.listed
        sess.flush()

from subgrounds import Subgrounds
import pandas as pd

AON_SUBGRAPH_ENDPOINT = "https://api.studio.thegraph.com/query/76695/aon/version/latest"

sg = Subgrounds()

aon = sg.load_subgraph(AON_SUBGRAPH_ENDPOINT)


def fetch_token(index=0):
    token = aon.Token
    latest = aon.Query.tokens(where=[token.index > index])
    df = sg.query_df([latest.aonFee, latest.creator, latest.holdersCount, latest.id, latest.index, latest.listed, latest.symbol, latest.name,latest.price ])
    return df

def fetch_trade(index=0):
    trade = aon.TokenTrade
    latest = aon.Query.tokenTrades(where=[trade.index > index])
    df = sg.query_df([latest.id, latest.transHash, latest.index, latest.price, latest.amount, latest.ethAmount, latest.aonFee, latest.isBuy, latest.timestamp, latest.trader, latest.token.id])
    if df is not None and not df.empty:
        df = df.set_index('tokenTrades_index')
    return df

def fetch_listed_token(index=0):
    list_token = aon.ListedToken
    latest = aon.Query.listedTokens(where=[list_token.index > index])
    df = sg.query_df([latest.blockNum, latest.id, latest.index, latest.pair, latest.timestamp, latest.token.id])
    return df

def fetch_top_holder(contract_address):
    holder = aon.TokenHolder
    latest = aon.Query.tokenHolders(where=[holder.token.id == contract_address])
    df = sg.query_df([latest.amount, latest.id, latest.holder, latest.index, latest.amount])
    return df
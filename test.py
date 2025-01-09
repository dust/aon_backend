from subgrounds import Subgrounds
import pandas as pd

AON_SUBGRAPH_ENDPOINT = "https://api.studio.thegraph.com/query/76695/aon/version/latest"

sg = Subgrounds()

aon = sg.load_subgraph(AON_SUBGRAPH_ENDPOINT)


def fetch_token(index=0):
    token = aon.Token
    latest = aon.Query.tokens(where=[token.index > index], first=5)
    df = sg.query_df([latest.aonFee, latest.creator, latest.holdersCount, latest.id, latest.index, latest.listed, latest.symbol, latest.name,latest.price ])
    if df is not None and not df.empty:
        df_idx = df.index
        for i in df_idx:
            print(df['tokens_id'][i])


def fetch_trade(index=0):
    trade = aon.TokenTrade
    latest = aon.Query.tokenTrades(where=[trade.index > index], first=100)
    df = sg.query_df([latest.id, latest.transHash, latest.index, latest.price, latest.amount, latest.ethAmount, latest.aonFee, latest.isBuy, latest.timestamp, latest.trader, latest.token.id])
    df = df.set_index('tokenTrades_timestamp')
    df.index = pd.to_datetime(df.index, unit='s')
    return df

def fetch_listed_token(index=0):
    list_token = aon.ListedToken
    latest = aon.Query.listedTokens(where=[list_token.index > index], first=100)
    df = sg.query_df([latest.blockNum, latest.id, latest.index, latest.pair, latest.timestamp, latest.token.id])
    return df


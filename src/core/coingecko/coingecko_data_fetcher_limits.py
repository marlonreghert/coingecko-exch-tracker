

class CoingeckoDataFetcherLimits:
    '''
        Limits for the coingecko data fetcher:
        - exchanges_with_similar_trades_limit: maximum number of exchanges with similar trades to fetch
        - exchanges_to_lookup_limit: maximum number of exchanges to lookup for trade data
    '''
    def __init__(self, 
                 exchanges_with_similar_trades_limit, \
                 exchanges_to_lookup_limit):
        self.exchanges_with_similar_trades_limit = exchanges_with_similar_trades_limit
        self.exchanges_to_lookup_limit = exchanges_to_lookup_limit


from src.core.coingecko.coingecko_tickers_utils import get_coingecko_id, get_vs_currency
from src.core.coingecko.coingecko_data_fetcher_limits import CoingeckoDataFetcherLimits
from src.constants.constants import HISTORICAL_VOLUME_DATE_FORMAT
from datetime import datetime
import logging

class CoingeckoSimilarExchangesDataAnalyzer:
    '''
        Fetches data from Coingecko API as dataframes.
        Accepts limits for the amount of data fetched
        Limits: {
        
        }
    '''
    def __init__(self, coingecko_api, limits: CoingeckoDataFetcherLimits):
        self.coingecko_api = coingecko_api
        self.limits = limits
        self.logger = logging.getLogger(self.__class__.__name__)


    def generate_exchanges_with_similar_trades(self, bitso_markets):
        exchanges = self.coingecko_api.fetch_exchanges()
        shared_markets = []
        similar_exchanges = []
        exchanges_lookup_count = 0

        for exchange in exchanges:
            if exchanges_lookup_count >= self.limits.exchanges_to_lookup_limit:
                self.logger.info("Reached the limit of exchanges to lookup")
                break

            markets = self.coingecko_api.fetch_markets(exchange["id"]).get("tickers", [])
            exchanges_lookup_count += 1

            has_market_in_common = False
            markets_count = 0

            for market in markets:
                if (market["base"], market["target"]) in bitso_markets:
                    shared_markets.append({
                        "exchange_id": exchange.get("id"),
                        "market_id": f"{market['base']}_{market['target']}",
                        "base": market.get("base"),
                        "target": market.get("target"),
                        "name": market.get("market").get("name"),
                    })
                    has_market_in_common = True
                    markets_count += 1
                     
            if has_market_in_common:
                similar_exchanges.append({
                    "exchange_id": exchange.get("id"),
                    "exchange_name": exchange.get("name"),
                    "year_established": exchange.get("year_established"),
                    "country": exchange.get("country"),
                    "trust_score": exchange.get("trust_score"),
                    "trust_score_rank": exchange.get("trust_score_rank"),
                })       
                if len(similar_exchanges) >= self.limits.exchanges_with_similar_trades_limit:
                    self.logger.info("Reached the limit of exchanges with similar trades necessary")
                    break

        return (similar_exchanges, \
            shared_markets)

    def generate_markets_historical_volume_table(self, shared_markets):
        historical_volume = []
        markets_processed = set()

        for shared_market in shared_markets:
            market_id = shared_market["market_id"]
            if market_id in markets_processed:
                continue
            markets_processed.add(market_id)

            # Map market into Coingecko accepted vs currency id 
            self.logger.info("Market: " + str(market_id))
            base, target = market_id.split('_')

            data = self.coingecko_api.fetch_historical_volume( \
                get_coingecko_id(base),
                get_vs_currency(target)
            )

            for point in data.get("prices", []):
                date = datetime.utcfromtimestamp(point[0] / 1000).strftime(HISTORICAL_VOLUME_DATE_FORMAT)
                volume = point[1]
                historical_volume.append({
                    "market_id": market_id,
                    "date": date,
                    "volume_usd": volume,
                })
                
        return historical_volume
    
    def generate_exchanges_trade_volume(self, exchanges, days):
        today_date = datetime.utcnow().strftime(HISTORICAL_VOLUME_DATE_FORMAT)
        volume_table = []

        for exchange in exchanges:
            exchange_id = exchange.get("exchange_id")
            try:
                # Fetch rolling 30-day volume
                rolling_30_day_volume_entries = self.coingecko_api.fetch_exchange_volume_chart(exchange_id, \
                                                                                       days=days)

                total_volume_btc = sum(float(point[1]) for point in rolling_30_day_volume_entries)                

                volume_table.append({
                    "exchange_id": exchange_id,
                    "date": today_date,
                    "volume_btc": total_volume_btc
                })
                self.logger.info(f"Fetched volume for {exchange_id}: {total_volume_btc:.12f} BTC")
            except Exception as e:
                self.logger.error(f"Failed to fetch data for {exchange_id}: {e}")

        return volume_table    
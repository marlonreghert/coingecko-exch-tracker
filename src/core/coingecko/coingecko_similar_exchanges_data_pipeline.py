from src.core.coingecko.coingecko_data_analyzer import CoingeckoDataAnalyzer
from src.core.coingecko.coingecko_data_fetcher_limits import CoingeckoDataFetcherLimits
from src.config.app_config import AppConfig
from src.adapters.coingecko_api import CoingeckoAPI
from src.adapters.bitso_api import BitsoAPI
from src.constants.constants import TMP_DATA_BASE_OUTPUT_PATH
import os
import pandas as pd
import logging


ANALYZED_DATA_OUTPUT_PATH= f"{TMP_DATA_BASE_OUTPUT_PATH}/analyzed"
EXCHANGES_TABLE_RELATIVE_PATH = f"{ANALYZED_DATA_OUTPUT_PATH}/exchange_table.csv"
SHARED_MARKETS_TABLE_RELATIVE_PATH = f"{ANALYZED_DATA_OUTPUT_PATH}/shared_markets_table.csv"
MARKETS_HISTORICAL_VOLUME = f"{ANALYZED_DATA_OUTPUT_PATH}/markets_historical_volume_df.csv"
EXCHANGES_HISTORICAL_TRADE_VOLUME_RELATIVE_PATH = f"{ANALYZED_DATA_OUTPUT_PATH}/exchanges_historical_trade_volume.csv"

class CoingeckoSimilarExchangesDataPipeline:
    def __init__(self, coingecko_api: CoingeckoAPI,
                  coingecko_data_analyzer: CoingeckoDataAnalyzer,
                  s3_handler,
                  app_config: AppConfig):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.coingeck_api = coingecko_api
        self.coingecko_data_analyzer = coingecko_data_analyzer
        self.s3_handler = s3_handler
        self.app_config = app_config

    def run(self):
        self.logger.info(f"Running with rate_limiter_max_retries:{self.app_config.rate_limiter_max_retries}, \
                        exchanges_with_similar_trades_to_analyze:{self.app_config.exchanges_with_similar_trades_to_analyze} \
                        exchanges_to_analyze_limit:{self.app_config.exchanges_to_analyze_limit} \
                        write_to_s3: {self.app_config.write_to_s3}")     

        bitsoAPI = BitsoAPI()
        bitso_markets = bitsoAPI.fetch_markets()

        exchanges_with_similar_markets, shared_markets = self.coingecko_data_analyzer.fetch_exchanges_with_similar_trades(bitso_markets)

        markets_historical_volume = self.coingecko_data_analyzer.fetch_markets_historical_volume_table(shared_markets)
        exchanges_historical_trade_volume = self.coingecko_data_analyzer.fetch_exchange_trade_volume(exchanges_with_similar_markets,
                                                                                                     self.app_config.historical_data_lookback_days)
        
        # Save the tables locally
        os.makedirs(ANALYZED_DATA_OUTPUT_PATH, exist_ok=True)

        # Create tables
        exchanges_with_similar_markets_df = pd.DataFrame(exchanges_with_similar_markets)
        shared_markets_df = pd.DataFrame(shared_markets)
        markets_historical_volume_df = pd.DataFrame(markets_historical_volume)
        exchanges_historical_trade_volume_df = pd.DataFrame(exchanges_historical_trade_volume)

        # Save to csv locally
        exchanges_with_similar_markets_df.to_csv(EXCHANGES_TABLE_RELATIVE_PATH, index=False)
        shared_markets_df.to_csv(SHARED_MARKETS_TABLE_RELATIVE_PATH, index=False)
        markets_historical_volume_df.to_csv(MARKETS_HISTORICAL_VOLUME, index=False)
        exchanges_historical_trade_volume_df.to_csv(EXCHANGES_HISTORICAL_TRADE_VOLUME_RELATIVE_PATH, index=False)

        # Save the tables to S3 (Mocked)
        if self.app_config.write_to_s3:
            self.s3_handler.upload_file(EXCHANGES_TABLE_RELATIVE_PATH, "processed/exchanges_with_similar_markets_table.csv")
            self.s3_handler.upload_file(SHARED_MARKETS_TABLE_RELATIVE_PATH, "processed/shared_markets_table.csv")
            self.s3_handler.upload_file(MARKETS_HISTORICAL_VOLUME, "processed/markets_historical_volume_table.csv")
            self.s3_handler.upload_file(EXCHANGES_HISTORICAL_TRADE_VOLUME_RELATIVE_PATH, "processed/exchanges_historical_trade_table.csv")

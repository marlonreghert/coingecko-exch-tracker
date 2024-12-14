from src.core.coingecko.coingecko_data_analyzer import CoingeckoSimilarExchangesDataAnalyzer
from src.core.coingecko.coingecko_data_fetcher_limits import CoingeckoDataFetcherLimits
from src.core.coingecko.coingecko_similar_exchanges_analysis_exporter import CoingeckoSimilarExchangesDataAnalysisExporter
from src.config.app_config import AppConfig
from src.adapters.bitso_api import BitsoAPI
from src.constants.constants import TMP_DATA_BASE_OUTPUT_PATH
import os
import pandas as pd
import logging

class CoingeckoSimilarExchangesDataPipeline:
    def __init__(self,
                  coingecko_data_analyzer: CoingeckoSimilarExchangesDataAnalyzer,
                  coingecko_data_analysis_exporter: CoingeckoSimilarExchangesDataAnalysisExporter,
                  app_config: AppConfig):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.coingecko_data_analyzer = coingecko_data_analyzer
        self.coingecko_data_analysis_exporter = coingecko_data_analysis_exporter
        self.app_config = app_config

    def run(self):
        self.logger.info(f"Running with rate_limiter_max_retries:{self.app_config.rate_limiter_max_retries}, \
                        exchanges_with_similar_trades_to_analyze:{self.app_config.exchanges_with_similar_trades_to_analyze} \
                        exchanges_to_analyze_limit:{self.app_config.exchanges_to_analyze_limit} \
                        write_to_s3: {self.app_config.write_to_s3}")     

        self.logger.info("Fetching Bitso markets")
        bitsoAPI = BitsoAPI()
        bitso_markets = bitsoAPI.fetch_markets()
        self.logger.info(f"Bitso Markets: {bitso_markets}")

        self.logger.info("Analyzing exchanges with similar trades")
        exchanges_with_similar_markets, shared_markets = self.coingecko_data_analyzer.generate_exchanges_with_similar_trades(bitso_markets)

        self.logger.info("Generating markets historical volume table")
        markets_historical_volume = self.coingecko_data_analyzer.generate_markets_historical_volume_table(shared_markets)

        self.logger.info("Generating similar exchanges historical trade volume")
        exchanges_historical_trade_volume = self.coingecko_data_analyzer.generate_exchanges_trade_volume(exchanges_with_similar_markets,
                                                                                                     self.app_config.historical_data_lookback_days)
        
        self.logger.info("Exporting tables")
        self.coingecko_data_analysis_exporter.export(exchanges_with_similar_markets,
                                                     shared_markets,
                                                     markets_historical_volume,
                                                     exchanges_historical_trade_volume)

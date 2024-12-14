
from src.constants.constants import TMP_DATA_BASE_OUTPUT_PATH
from src.config.app_config import AppConfig
from src.adapters.s3_handler import S3Handler
import os
import pandas as pd
import logging 

ANALYZED_DATA_OUTPUT_PATH= f"{TMP_DATA_BASE_OUTPUT_PATH}/analyzed/{{YEAR}}/{{MONTH}}/{{DAY}}"

EXCHANGES_TABLE_RELATIVE_LOCAL_OUTPUT_PATH = f"{ANALYZED_DATA_OUTPUT_PATH}/exchange_table.csv"
SHARED_MARKETS_TABLE_LOCAL_OUTPUT_PATH = f"{ANALYZED_DATA_OUTPUT_PATH}/shared_markets_table.csv"
MARKETS_HISTORICAL_VOLUME_LOCAL_OUTPUT_PATH = f"{ANALYZED_DATA_OUTPUT_PATH}/markets_historical_volume_df.csv"
EXCHANGES_HISTORICAL_TRADE_VOLUME_LOCAL_OUTPUT_PATH = f"{ANALYZED_DATA_OUTPUT_PATH}/exchanges_historical_trade_volume.csv"

PIPELINE_S3_OUTPUT_PATH = f"coingecko/analyzed/{{YEAR}}/{{MONTH}}/{{DAY}}"
EXCHANGES_TABLE_RELATIVE_S3_PATH = f"{PIPELINE_S3_OUTPUT_PATH}/exchange_table.csv"
SHARED_MARKETS_TABLE_RELATIVE_S3_OUTPUT_PATH = f"{PIPELINE_S3_OUTPUT_PATH}/shared_markets_table.csv"
MARKETS_HISTORICAL_VOLUME_S3_OUTPUT_PATH = f"{PIPELINE_S3_OUTPUT_PATH}/markets_historical_volume_df.csv"
EXCHANGES_HISTORICAL_TRADE_VOLUME_S3_OUTPUT_PATH = f"{PIPELINE_S3_OUTPUT_PATH}/exchanges_historical_trade_volume.csv"

class CoingeckoSimilarExchangesDataAnalysisExporter:

    def __init__(self, app_config: AppConfig, s3_handler: S3Handler):
        self.app_config = app_config
        self.s3_handler = s3_handler
        self.logger = logging.getLogger(self.__class__.__name__)

    def export(self, 
                      exchanges_with_similar_markets, 
                      shared_markets,
                      markets_historical_volume,
                      exchanges_historical_trade_volume):
        self.logger.info(f"Exporting tables to base path: {ANALYZED_DATA_OUTPUT_PATH}")
        # Save the tables locally
        os.makedirs(ANALYZED_DATA_OUTPUT_PATH, exist_ok=True)

        # Create tables
        exchanges_with_similar_markets_df = pd.DataFrame(exchanges_with_similar_markets)
        shared_markets_df = pd.DataFrame(shared_markets)
        markets_historical_volume_df = pd.DataFrame(markets_historical_volume)
        exchanges_historical_trade_volume_df = pd.DataFrame(exchanges_historical_trade_volume)

        # Save to csv locally
        exchanges_with_similar_markets_df.to_csv(EXCHANGES_TABLE_RELATIVE_LOCAL_OUTPUT_PATH, index=False)
        shared_markets_df.to_csv(SHARED_MARKETS_TABLE_LOCAL_OUTPUT_PATH, index=False)
        markets_historical_volume_df.to_csv(MARKETS_HISTORICAL_VOLUME_LOCAL_OUTPUT_PATH, index=False)
        exchanges_historical_trade_volume_df.to_csv(EXCHANGES_HISTORICAL_TRADE_VOLUME_LOCAL_OUTPUT_PATH, index=False)

        # Save the tables to S3
        if self.app_config.write_to_s3:
            self.logger.info(f"Writing to S3")

            self.write_to_s3(EXCHANGES_TABLE_RELATIVE_LOCAL_OUTPUT_PATH, EXCHANGES_TABLE_RELATIVE_S3_PATH)
            self.write_to_s3(SHARED_MARKETS_TABLE_LOCAL_OUTPUT_PATH, SHARED_MARKETS_TABLE_RELATIVE_S3_OUTPUT_PATH)
            self.write_to_s3(MARKETS_HISTORICAL_VOLUME_LOCAL_OUTPUT_PATH, MARKETS_HISTORICAL_VOLUME_S3_OUTPUT_PATH)
            self.write_to_s3(EXCHANGES_HISTORICAL_TRADE_VOLUME_LOCAL_OUTPUT_PATH, EXCHANGES_HISTORICAL_TRADE_VOLUME_S3_OUTPUT_PATH)

    def write_to_s3(self, local_file, s3_path):
        self.logger.info(f"Writing: {local_file} -> {s3_path}")
        self.s3_handler.upload_file(local_file, s3_path)

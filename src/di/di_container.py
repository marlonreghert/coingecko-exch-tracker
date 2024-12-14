import os
import boto3
import logging
from src.adapters.coingecko_api import CoingeckoAPI
from src.core.coingecko.coingecko_similar_exchanges_data_pipeline import CoingeckoSimilarExchangesDataPipeline
from src.core.coingecko.coingecko_data_analyzer import CoingeckoSimilarExchangesDataAnalyzer
from src.core.coingecko.coingecko_data_analyzer import CoingeckoDataFetcherLimits
from src.core.coingecko.coingecko_similar_exchanges_analysis_exporter import CoingeckoSimilarExchangesDataAnalysisExporter
from src.adapters.s3_handler import S3Handler
from src.constants.constants import AWS_REQUIRED_CONFIGS
from src.config.app_config import AppConfig


class DIContainer:
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config
        self.logger = logging.getLogger(self.__class__.__name__)

    def init_deps(self):
        self.logger.info("Initializing CoingeckoAPI...")
        self.coingecko_api = CoingeckoAPI(rate_limiter_retries=self.app_config.rate_limiter_max_retries)
        self.logger.info("CoingeckoAPI initialized succesfully.")

        self.logger.info("Initializing S3Handler...")

        # AWS client initialization
        if self.app_config.write_to_s3:
            aws_bucket = os.environ.get("AWS_BUCKET", "")

            self.logger.info("Initializing S3 boto client")
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=os.environ.get("S3_ENDPOINT", ""),
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", ""),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
                region_name=os.environ.get("AWS_REGION", ""),
            )
            self.logger.info("S3 boto client initialized succesfully.")   

            self.logger.info("Initializing S3Handler")
            self.s3_handler = S3Handler(
                s3_client=self.s3_client,
                bucket_name=aws_bucket
            )
            self.logger.info("S3Handler initialized succesfully.")
        else:
            self.logger.info("Skipping S3 client and handler")
            self.s3_client = None
            self.s3_handler = None

        self.logger.info("Initializing CoingeckoDataAnalysisExporter...")
        self.coingecko_data_analysis_exporter = CoingeckoSimilarExchangesDataAnalysisExporter( \
            self.app_config, self.s3_handler)
        self.logger.info("CoingeckoDataAnalysisExporter initialized succesfully.")   

        self.logger.info("Initializing CoingeckoDataAnalyzer...")
        self.coingecko_data_analyzer = CoingeckoSimilarExchangesDataAnalyzer(self.coingecko_api, \
                                                CoingeckoDataFetcherLimits( \
                                                   self.app_config.exchanges_with_similar_trades_to_analyze, \
                                                    self.app_config.exchanges_to_analyze_limit \
                                                    ))
        self.logger.info("CoingeckoDataAnalyzer initialized succesfully.")        

        self.logger.info("Initializing CoingeckoSimilarExchangesDataPipeline...")
        self.coingecko_similar_exchanges_data_pipeline = CoingeckoSimilarExchangesDataPipeline(self.coingecko_data_analyzer,
                                                                        self.coingecko_data_analysis_exporter,
                                                                        self.app_config)
        self.logger.info("CoingeckoSimilarExchangesDataPipeline initialized succesfully.")        

    def validate_aws_config(self):
        for aws_config in AWS_REQUIRED_CONFIGS:
            if not aws_config in os.environ or os.environ.get(aws_config) == "":
                self.logger.error(f"Missing aws config: {aws_config}")
                raise Exception(f"Missing env var for aws config: {aws_config}")
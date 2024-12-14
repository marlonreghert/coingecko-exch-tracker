import unittest
from unittest.mock import MagicMock, patch
from src.core.coingecko.coingecko_similar_exchanges_analysis_exporter import CoingeckoSimilarExchangesDataAnalysisExporter
from src.config.app_config import AppConfig
from src.adapters.s3_handler import S3Handler
import pandas as pd
import os

class TestCoingeckoSimilarExchangesDataAnalysisExporter(unittest.TestCase):
    def setUp(self):
        self.mock_app_config = AppConfig(
            rate_limiter_max_retries=3,
            historical_data_lookback_days=30,
            log_level="INFO",
            exchanges_with_similar_trades_to_analyze=5,
            exchanges_to_analyze_limit=10,
            write_to_s3=True
        )
        self.mock_s3_handler = MagicMock(spec=S3Handler)
        self.exporter = CoingeckoSimilarExchangesDataAnalysisExporter(self.mock_app_config, self.mock_s3_handler)

    @patch("os.makedirs")
    @patch("pandas.DataFrame.to_csv")
    def test_export_with_s3(self, mock_to_csv, mock_makedirs):
        exchanges_with_similar_markets = [{"exchange_id": "binance", "trust_score": 10}]
        shared_markets = [{"market_id": "BTC_USDT"}]
        markets_historical_volume = [{"market_id": "BTC_USDT", "volume_usd": 10000}]
        exchanges_historical_trade_volume = [{"exchange_id": "binance", "volume_btc": 300}]

        self.exporter.export(
            exchanges_with_similar_markets,
            shared_markets,
            markets_historical_volume,
            exchanges_historical_trade_volume,
        )

        self.mock_s3_handler.upload_file.assert_any_call(
            os.path.join("./", "output", "data", "analyzed", "exchange_table.csv"),
            "coingecko/analyzed/exchange_table.csv"
        )
        self.mock_s3_handler.upload_file.assert_any_call(
            os.path.join("./", "output", "data", "analyzed", "shared_markets_table.csv"),
            "coingecko/analyzed/shared_markets_table.csv"
        )
        self.mock_s3_handler.upload_file.assert_any_call(
            os.path.join("./", "output", "data", "analyzed", "markets_historical_volume_df.csv"),
            "coingecko/analyzed/markets_historical_volume_df.csv"
        )
        self.mock_s3_handler.upload_file.assert_any_call(
            os.path.join("./", "output", "data", "analyzed", "exchanges_historical_trade_volume.csv"),
            "coingecko/analyzed/exchanges_historical_trade_volume.csv"
        )
        mock_makedirs.assert_called_once_with(os.path.join("./", "output", "data", "analyzed"), exist_ok=True)
        self.assertEqual(mock_to_csv.call_count, 4)

    @patch("os.makedirs")
    @patch("pandas.DataFrame.to_csv")
    def test_export_without_s3(self, mock_to_csv, mock_makedirs):
        self.mock_app_config.write_to_s3 = False

        exchanges_with_similar_markets = [{"exchange_id": "binance", "trust_score": 10}]
        shared_markets = [{"market_id": "BTC_USDT"}]
        markets_historical_volume = [{"market_id": "BTC_USDT", "volume_usd": 10000}]
        exchanges_historical_trade_volume = [{"exchange_id": "binance", "volume_btc": 300}]

        self.exporter.export(
            exchanges_with_similar_markets,
            shared_markets,
            markets_historical_volume,
            exchanges_historical_trade_volume,
        )

        self.mock_s3_handler.upload_file.assert_not_called()
        mock_makedirs.assert_called_once_with(os.path.join("./", "output", "data", "analyzed"), exist_ok=True)
        self.assertEqual(mock_to_csv.call_count, 4)

if __name__ == "__main__":
    unittest.main()

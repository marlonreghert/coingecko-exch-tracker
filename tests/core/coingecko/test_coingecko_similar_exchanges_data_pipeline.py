import unittest
from unittest.mock import MagicMock, patch
from src.core.coingecko.coingecko_similar_exchanges_data_pipeline import CoingeckoSimilarExchangesDataPipeline
from src.config.app_config import AppConfig
from src.adapters.bitso_api import BitsoAPI
from src.core.coingecko.coingecko_data_analyzer import CoingeckoSimilarExchangesDataAnalyzer
from src.core.coingecko.coingecko_similar_exchanges_analysis_exporter import CoingeckoSimilarExchangesDataAnalysisExporter

class TestCoingeckoSimilarExchangesDataPipeline(unittest.TestCase):
    def setUp(self):
        self.mock_app_config = AppConfig(
            rate_limiter_max_retries=3,
            historical_data_lookback_days=30,
            log_level="INFO",
            exchanges_with_similar_trades_to_analyze=5,
            exchanges_to_analyze_limit=10,
            write_to_s3=True
        )
        self.mock_data_analyzer = MagicMock(spec=CoingeckoSimilarExchangesDataAnalyzer)
        self.mock_data_exporter = MagicMock(spec=CoingeckoSimilarExchangesDataAnalysisExporter)
        self.pipeline = CoingeckoSimilarExchangesDataPipeline(
            coingecko_data_analyzer=self.mock_data_analyzer,
            coingecko_data_analysis_exporter=self.mock_data_exporter,
            app_config=self.mock_app_config
        )

    @patch("src.core.coingecko.coingecko_similar_exchanges_data_pipeline.BitsoAPI")
    def test_pipeline_run(self, MockBitsoAPI):
        mock_bitso_api = MockBitsoAPI.return_value
        mock_bitso_api.fetch_markets.return_value = [("BTC", "USDT"), ("ETH", "USDT")]

        self.mock_data_analyzer.generate_exchanges_with_similar_trades.return_value = (
            [{"exchange_id": "binance", "trust_score": 10}],
            [{"market_id": "BTC_USDT", "base": "BTC", "target": "USDT"}]
        )
        self.mock_data_analyzer.generate_markets_historical_volume_table.return_value = [
            {"market_id": "BTC_USDT", "date": "2023-01-01", "volume_usd": 10000}
        ]
        self.mock_data_analyzer.generate_exchanges_trade_volume.return_value = [
            {"exchange_id": "binance", "date": "2023-01-01", "volume_btc": 300}
        ]

        self.pipeline.run()

        mock_bitso_api.fetch_markets.assert_called_once()
        self.mock_data_analyzer.generate_exchanges_with_similar_trades.assert_called_once_with([("BTC", "USDT"), ("ETH", "USDT")])
        self.mock_data_analyzer.generate_markets_historical_volume_table.assert_called_once_with(
            [{"market_id": "BTC_USDT", "base": "BTC", "target": "USDT"}]
        )
        self.mock_data_analyzer.generate_exchanges_trade_volume.assert_called_once_with(
            [{"exchange_id": "binance", "trust_score": 10}],
            self.mock_app_config.historical_data_lookback_days
        )
        self.mock_data_exporter.export.assert_called_once_with(
            [{"exchange_id": "binance", "trust_score": 10}],
            [{"market_id": "BTC_USDT", "base": "BTC", "target": "USDT"}],
            [{"market_id": "BTC_USDT", "date": "2023-01-01", "volume_usd": 10000}],
            [{"exchange_id": "binance", "date": "2023-01-01", "volume_btc": 300}]
        )

if __name__ == "__main__":
    unittest.main()

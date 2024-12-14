import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from src.core.coingecko.coingecko_data_analyzer import CoingeckoDataAnalyzer
from src.core.coingecko.coingecko_data_fetcher_limits import CoingeckoDataFetcherLimits


class TestCoingeckoDataFetcher(unittest.TestCase):
    def setUp(self):
        # Mock the coingecko_api and limits
        self.coingecko_api = Mock()
        self.limits = CoingeckoDataFetcherLimits(
            exchanges_to_lookup_limit=5,
            exchanges_with_similar_trades_limit=3
        )
        self.data_fetcher = CoingeckoDataAnalyzer(self.coingecko_api, self.limits)

    @patch("src.utils.coingecko_tickers_utils.get_coingecko_id", return_value="mock_base_id")
    @patch("src.utils.coingecko_tickers_utils.get_vs_currency", return_value="mock_target_id")
    def test_fetch_exchanges_with_similar_trades(self, mock_get_vs_currency, mock_get_coingecko_id):
        # Setup mocks
        bitso_markets = {("BTC", "USD"), ("ETH", "BTC")}
        self.coingecko_api.fetch_exchanges.return_value = [
            {"id": "binance", "name": "Binance"},
            {"id": "kraken", "name": "Kraken"}
        ]
        self.coingecko_api.fetch_markets.side_effect = [
            {"tickers": [{"base": "BTC", "target": "USD", "market": {"name": "Binance"}}]},
            {"tickers": [{"base": "ETH", "target": "BTC", "market": {"name": "Kraken"}}]}
        ]

        # Call the method
        similar_exchanges, shared_markets = self.data_fetcher.fetch_exchanges_with_similar_trades(bitso_markets)

        # Assertions
        self.assertEqual(len(similar_exchanges), 2)
        self.assertEqual(len(shared_markets), 2)
        self.assertEqual(shared_markets[0]["market_id"], "BTC_USD")
        self.assertEqual(shared_markets[1]["market_id"], "ETH_BTC")

    @patch("src.utils.coingecko_tickers_utils.get_coingecko_id", return_value="mock_base_id")
    @patch("src.utils.coingecko_tickers_utils.get_vs_currency", return_value="mock_target_id")
    def test_fetch_markets_historical_volume_table(self, mock_get_vs_currency, mock_get_coingecko_id):
        # Setup mocks
        shared_markets = [
            {"market_id": "BTC_USD"},
            {"market_id": "ETH_BTC"}
        ]
        self.coingecko_api.fetch_historical_volume.return_value = {
            "prices": [[1638316800000, 1000], [1638403200000, 2000]]
        }

        # Call the method
        historical_volume = self.data_fetcher.fetch_markets_historical_volume_table(shared_markets)

        # Assertions
        self.assertEqual(len(historical_volume), 4)
        self.assertEqual(historical_volume[0]["date"], "2021-12-01")
        self.assertEqual(historical_volume[0]["volume_usd"], 1000)
        self.assertEqual(historical_volume[1]["volume_usd"], 2000)

    def test_fetch_exchange_trade_volume(self):
        # Setup mocks
        exchanges = [{"exchange_id": "binance"}, {"exchange_id": "kraken"}]
        self.coingecko_api.fetch_exchange_volume_chart.side_effect = [
            [[1638316800000, "10"], [1638403200000, "20"]],
            [[1638316800000, "5"], [1638403200000, "15"]]
        ]

        # Call the method
        volume_table = self.data_fetcher.fetch_exchange_trade_volume(exchanges, days=30)

        # Assertions
        self.assertEqual(len(volume_table), 2)
        self.assertEqual(volume_table[0]["exchange_id"], "binance")
        self.assertEqual(volume_table[0]["volume_btc"], 30.0)
        self.assertEqual(volume_table[1]["volume_btc"], 20.0)


if __name__ == "__main__":
    unittest.main()

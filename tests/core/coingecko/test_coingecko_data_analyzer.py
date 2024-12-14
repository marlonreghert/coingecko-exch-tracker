import unittest
from unittest.mock import MagicMock
from src.core.coingecko.coingecko_data_analyzer import CoingeckoSimilarExchangesDataAnalyzer
from src.core.coingecko.coingecko_data_fetcher_limits import CoingeckoDataFetcherLimits

class TestCoingeckoSimilarExchangesDataAnalyzer(unittest.TestCase):
    def setUp(self):
        self.mock_coingecko_api = MagicMock()
        self.limits = CoingeckoDataFetcherLimits(
            exchanges_to_lookup_limit=2,
            exchanges_with_similar_trades_limit=1
        )
        self.analyzer = CoingeckoSimilarExchangesDataAnalyzer(self.mock_coingecko_api, self.limits)

    def test_generate_exchanges_with_similar_trades(self):
        self.mock_coingecko_api.fetch_exchanges.return_value = [
            {"id": "binance", "name": "Binance", "year_established": 2017, "country": "Cayman Islands",
             "trust_score": 10, "trust_score_rank": 1},
            {"id": "coinbase", "name": "Coinbase", "year_established": 2012, "country": "USA",
             "trust_score": 9, "trust_score_rank": 2}
        ]
        self.mock_coingecko_api.fetch_markets.side_effect = [
            {"tickers": [{"base": "BTC", "target": "USDT", "market": {"name": "Binance"}}]},
            {"tickers": [{"base": "BTC", "target": "ETH", "market": {"name": "Coinbase"}}]}
        ]

        bitso_markets = [("BTC", "USDT")]
        similar_exchanges, shared_markets = self.analyzer.generate_exchanges_with_similar_trades(bitso_markets)

        self.assertEqual(len(similar_exchanges), 1)
        self.assertEqual(similar_exchanges[0]["exchange_id"], "binance")
        self.assertEqual(len(shared_markets), 1)
        self.assertEqual(shared_markets[0]["market_id"], "BTC_USDT")

    def test_generate_markets_historical_volume_table(self):
        self.mock_coingecko_api.fetch_historical_volume.return_value = {
            "prices": [[1609459200000, 10000], [1609545600000, 20000]]
        }

        shared_markets = [{"market_id": "BTC_USDT"}]
        historical_volume = self.analyzer.generate_markets_historical_volume_table(shared_markets)

        self.assertEqual(len(historical_volume), 2)
        self.assertEqual(historical_volume[0]["market_id"], "BTC_USDT")
        self.assertEqual(historical_volume[0]["volume_usd"], 10000)

    def test_generate_exchanges_trade_volume(self):
        self.mock_coingecko_api.fetch_exchange_volume_chart.return_value = [
            [1609459200000, "100"], [1609545600000, "200"]
        ]

        exchanges = [{"exchange_id": "binance"}]
        trade_volume = self.analyzer.generate_exchanges_trade_volume(exchanges, 30)

        self.assertEqual(len(trade_volume), 1)
        self.assertEqual(trade_volume[0]["exchange_id"], "binance")
        self.assertAlmostEqual(trade_volume[0]["volume_btc"], 300)

    def test_generate_exchanges_trade_volume_with_exception(self):
        self.mock_coingecko_api.fetch_exchange_volume_chart.side_effect = Exception("API error")

        exchanges = [{"exchange_id": "binance"}]
        trade_volume = self.analyzer.generate_exchanges_trade_volume(exchanges, 30)

        self.assertEqual(len(trade_volume), 0)

if __name__ == "__main__":
    unittest.main()

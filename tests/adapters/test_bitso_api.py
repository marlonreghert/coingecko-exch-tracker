import unittest
from src.adapters.bitso_api import BitsoAPI

class TestBitsoAPI(unittest.TestCase):
    def test_fetch_markets(self):
        bitso_api = BitsoAPI()
        expected_markets = [("BTC", "ETH"), ("BTC", "USDT")]

        markets = bitso_api.fetch_markets()
        self.assertEqual(markets, expected_markets)

if __name__ == "__main__":
    unittest.main()

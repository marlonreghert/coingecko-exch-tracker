import unittest
from unittest.mock import patch, MagicMock
from src.adapters.coingecko_api import CoingeckoAPI
from src.utils.http_call_retrier import HTTPCallRetrier

class TestCoingeckoAPI(unittest.TestCase):
    @patch("src.adapters.coingecko_api.requests.get")
    @patch("time.sleep", return_value=None)  # Prevent actual sleep during tests
    def test_fetch_exchanges_success(self, mock_sleep, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "binance", "name": "Binance"}]
        mock_requests_get.return_value = mock_response

        api = CoingeckoAPI(rate_limiter_retries=3)
        exchanges = api.fetch_exchanges()

        self.assertEqual(exchanges, [{"id": "binance", "name": "Binance"}])
        mock_requests_get.assert_called_once_with("https://api.coingecko.com/api/v3/exchanges")

    @patch("src.adapters.coingecko_api.requests.get")
    @patch("time.sleep", return_value=None)
    def test_fetch_exchanges_retry_on_throttling(self, mock_sleep, mock_requests_get):
        throttled_response = MagicMock()
        throttled_response.status_code = 429
        throttled_response.headers = {"Retry-After": "2"}
        successful_response = MagicMock()
        successful_response.status_code = 200
        successful_response.json.return_value = [{"id": "binance", "name": "Binance"}]

        mock_requests_get.side_effect = [throttled_response, successful_response]

        api = CoingeckoAPI(rate_limiter_retries=3)
        exchanges = api.fetch_exchanges()

        self.assertEqual(exchanges, [{"id": "binance", "name": "Binance"}])
        self.assertEqual(mock_requests_get.call_count, 2)
        mock_sleep.assert_called_with(2)

    @patch("src.adapters.coingecko_api.requests.get")
    @patch("time.sleep", return_value=None)
    def test_fetch_exchanges_failure_after_retries(self, mock_sleep, mock_requests_get):
        failed_response = MagicMock()
        failed_response.status_code = 500
        failed_response.text = "Internal Server Error"

        mock_requests_get.return_value = failed_response

        api = CoingeckoAPI(rate_limiter_retries=3)
        with self.assertRaises(Exception) as context:
            api.fetch_exchanges()

        self.assertIn("Maximum retries reached", str(context.exception))
        self.assertEqual(mock_requests_get.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)  # Called twice before final failure

    @patch("src.adapters.coingecko_api.requests.get")
    @patch("time.sleep", return_value=None)
    def test_fetch_exchange_volume_chart(self, mock_sleep, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [[1609459200000, 1000000], [1609545600000, 2000000]]
        mock_requests_get.return_value = mock_response

        api = CoingeckoAPI(rate_limiter_retries=3)
        volume_chart = api.fetch_exchange_volume_chart("binance", 30)

        self.assertEqual(volume_chart, [[1609459200000, 1000000], [1609545600000, 2000000]])
        mock_requests_get.assert_called_once_with(
            "https://api.coingecko.com/api/v3/exchanges/binance/volume_chart?days=30"
        )

if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch
from src.utils.http_call_retrier import HTTPCallRetrier

class TestHTTPCallRetrier(unittest.TestCase):
    def setUp(self):
        self.retrier = HTTPCallRetrier(max_retries=3, exponential_backoff_rate=2, initial_wait_time_seconds=1)

    @patch("time.sleep", return_value=None)
    def test_successful_call(self, mock_sleep):
        mock_api_call = MagicMock(return_value=MagicMock(status_code=200))
        response = self.retrier.call_api(mock_api_call, "test_namespace")
        self.assertEqual(response.status_code, 200)
        mock_api_call.assert_called_once()
        mock_sleep.assert_not_called()

    @patch("time.sleep", return_value=None)
    def test_retry_on_throttling(self, mock_sleep):
        mock_api_call = MagicMock()
        mock_api_call.side_effect = [
            MagicMock(status_code=429, headers={"Retry-After": "2"}),
            MagicMock(status_code=200)
        ]
        response = self.retrier.call_api(mock_api_call, "test_namespace")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_api_call.call_count, 2)
        mock_sleep.assert_called_once_with(2)

    @patch("time.sleep", return_value=None)
    def test_failure_after_max_retries(self, mock_sleep):
        mock_api_call = MagicMock(return_value=MagicMock(status_code=500, text="Internal Server Error"))
        with self.assertRaises(Exception) as context:
            self.retrier.call_api(mock_api_call, "test_namespace")
        self.assertIn("Maximum retries reached", str(context.exception))
        self.assertEqual(mock_api_call.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("time.sleep", return_value=None)
    def test_exponential_backoff(self, mock_sleep):
        mock_api_call = MagicMock()
        mock_api_call.side_effect = [
            MagicMock(status_code=500, headers={}),
            MagicMock(status_code=500, headers={}),
            MagicMock(status_code=200)
        ]
        response = self.retrier.call_api(mock_api_call, "test_namespace")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_api_call.call_count, 3)
        mock_sleep.assert_any_call(1)
        mock_sleep.assert_any_call(2)

if __name__ == "__main__":
    unittest.main()

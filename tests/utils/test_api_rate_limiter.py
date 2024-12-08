import unittest
from unittest.mock import Mock, patch
from src.utils.api_rate_limiter import APIRateLimiter


class TestAPIRateLimiter(unittest.TestCase):
    def setUp(self):
        self.rate_limiter = APIRateLimiter(max_retries=3)

    @patch("time.sleep", return_value=None)  # Avoid delays
    def test_successful_call(self, _):
        response = Mock(status_code=200)
        api_call = Mock(return_value=response)

        result = self.rate_limiter.call_api(api_call)

        self.assertEqual(result, response)
        api_call.assert_called_once()

    @patch("time.sleep", return_value=None)
    def test_throttled_then_successful(self, mock_sleep):
        throttled = Mock(status_code=429, headers={"Retry-After": "1"})
        success = Mock(status_code=200)
        api_call = Mock(side_effect=[throttled, success])

        result = self.rate_limiter.call_api(api_call)

        self.assertEqual(result, success)
        self.assertEqual(api_call.call_count, 2)
        mock_sleep.assert_called_once_with(1)

    @patch("time.sleep", return_value=None)
    def test_exceeded_retries(self, mock_sleep):
        throttled = Mock(status_code=429, headers={"Retry-After": "1"})
        api_call = Mock(return_value=throttled)

        with self.assertRaises(Exception) as context:
            self.rate_limiter.call_api(api_call)

        self.assertEqual(str(context.exception), "Maximum retries reached. Could not fetch data.")
        self.assertEqual(api_call.call_count, 3)
        mock_sleep.assert_called_with(1)

    def test_non_throttling_error(self):
        error_response = Mock(status_code=500, text="Internal Server Error")
        api_call = Mock(return_value=error_response)

        with self.assertRaises(Exception) as context:
            self.rate_limiter.call_api(api_call)

        self.assertIn("API call failed with status code 500", str(context.exception))
        api_call.assert_called_once()

    @patch("time.sleep", return_value=None)
    def test_retry_after_missing(self, mock_sleep):
        throttled = Mock(status_code=429, headers={})
        success = Mock(status_code=200)
        api_call = Mock(side_effect=[throttled, success])

        result = self.rate_limiter.call_api(api_call)

        self.assertEqual(result, success)
        self.assertEqual(api_call.call_count, 2)
        mock_sleep.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()

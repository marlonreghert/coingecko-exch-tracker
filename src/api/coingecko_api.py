import requests
from datetime import datetime
from ratelimit import limits, sleep_and_retry
from src.utils.api_rate_limiter import APIRateLimiter

# Base URL for the CoinGecko API
BASE_ROUTE = "https://api.coingecko.com/api/v3"

# API routes for different endpoints
FETCH_EXCHANGE_ROUTE = f"{BASE_ROUTE}/exchanges"  # Fetches all exchanges
FETCH_EXCHANGE_VOLUME_BY_ID_ROUTE = f"{BASE_ROUTE}/exchanges/{{exchange_id}}/volume_chart?days={{days}}"  # Fetch volume chart for an exchange
FETCH_MARKETS_ROUTE_FORMAT = f"{BASE_ROUTE}/exchanges/{{exchange_id}}/tickers"  # Fetch market tickers for an exchange
FETCH_HISTORICAL_VOLUME_ROUTE = f"{BASE_ROUTE}/coins/{{base_coin}}/market_chart?vs_currency={{target_coin}}&days={{lookback_days}}"  # Fetch historical volume for a coin pair

# Default configurations for historical volume data
HISTORICAL_VOLUME_DEFAULT_CURRENCY = "usd"  # Default currency for historical volume data
HISTORICAL_VOLUME_DEFAULT_LOOKBACK_DAYS = "30"  # Default lookback period in days for historical data

class CoingeckoAPI:
    """
    Wrapper class for interacting with the CoinGecko API.
    This class uses a rate-limited API wrapper to handle retries and throttling.
    """

    def __init__(self, rate_limiter_retries):
        """
        Initialize the CoinGeckoAPI with a rate limiter.

        :param rate_limiter_retries: Number of retries for API calls before raising an exception.
        """
        self.APIRateLimiter = APIRateLimiter(rate_limiter_retries)  # Initialize the rate limiter with specified retries
            
    def fetch_exchanges(self):
        """
        Fetch a list of all available exchanges from the CoinGecko API.

        :return: A JSON object containing exchange information.
        """
        return self.APIRateLimiter.call_api(lambda: self._fetch_exchanges()).json()
    
    def _fetch_exchanges(self):
        """
        Internal method to make the raw API request for fetching exchanges.

        :return: A Response object from the CoinGecko API.
        """
        response = requests.get(FETCH_EXCHANGE_ROUTE)
        return response
    
    def fetch_markets(self, exchange_id):
        """
        Fetch a list of markets for a specific exchange.

        :param exchange_id: The ID of the exchange.
        :return: A JSON object containing market ticker information.
        """
        return self.APIRateLimiter.call_api(lambda: self._fetch_markets(exchange_id)).json()

    def _fetch_markets(self, exchange_id):
        """
        Internal method to make the raw API request for fetching markets for an exchange.

        :param exchange_id: The ID of the exchange.
        :return: A Response object from the CoinGecko API.
        """
        fetch_markets_url = str.format(FETCH_MARKETS_ROUTE_FORMAT, exchange_id=exchange_id)
        response = requests.get(fetch_markets_url)
        return response

    def fetch_historical_volume(self, base_coin_id, target_vs_currency):
        """
        Fetch historical volume data for a given coin pair.

        :param base_coin_id: The CoinGecko ID of the base coin.
        :param target_vs_currency: The currency against which the volume is measured.
        :return: A JSON object containing historical volume data.
        """
        return self.APIRateLimiter.call_api(lambda: self._fetch_historical_volume(base_coin_id, target_vs_currency)).json()
    
    def _fetch_historical_volume(self, base_coin_id, target_vs_currency):
        """
        Internal method to make the raw API request for fetching historical volume data.

        :param base_coin_id: The CoinGecko ID of the base coin.
        :param target_vs_currency: The currency against which the volume is measured.
        :return: A Response object from the CoinGecko API.
        """
        fetch_historical_volume_url = str.format(FETCH_HISTORICAL_VOLUME_ROUTE, 
                                                 base_coin=base_coin_id,
                                                 target_coin=target_vs_currency,
                                                 lookback_days=HISTORICAL_VOLUME_DEFAULT_LOOKBACK_DAYS)
        response = requests.get(fetch_historical_volume_url)
        return response
    
    def fetch_exchange_volume_chart(self, exchange_id, days):
        """
        Fetch the trade volume chart for a specific exchange over a specified number of days.

        :param exchange_id: The ID of the exchange.
        :param days: Number of days for which to fetch the volume chart.
        :return: A JSON object containing volume chart data.
        """
        return self.APIRateLimiter.call_api(lambda: self._fetch_exchange_volume_chart(exchange_id, days)).json()
    
    def _fetch_exchange_volume_chart(self, exchange_id, days=30):
        """
        Internal method to make the raw API request for fetching an exchange's volume chart.

        :param exchange_id: The ID of the exchange.
        :param days: Number of days for which to fetch the volume chart (default: 30).
        :return: A Response object from the CoinGecko API.
        """
        url = str.format(FETCH_EXCHANGE_VOLUME_BY_ID_ROUTE, exchange_id=exchange_id, days=days)
        print("Fetching exchange volume chart from:", url)  # Debug log for the API URL
        return requests.get(url)

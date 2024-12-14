# Mocked API to fetch Bitso markets
class BitsoAPI:
    def __init__(self):
        # Initialize the mock Bitso API. In real use, this might accept configuration or API keys.
        pass

    def fetch_markets(self):
        """
        Simulate fetching markets from the Bitso API.

        :return: A list of tuples representing markets, 
                 where each tuple contains a base currency and a target currency.
        Example:
            [("BTC", "ETH"), ("BTC", "USDT")]
        """
        # Mock response with some example markets
        return [("BTC", "ETH"), ("BTC", "USDT")]
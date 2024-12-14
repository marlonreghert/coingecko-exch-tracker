import json

class AppConfig:
    """
    A class to represent configuration values.
    """
    def __init__(self, rate_limiter_max_retries: int, \
                 historical_data_lookback_days: int, \
                 log_level: str,
                 exchanges_with_similar_trades_to_analyze: int,
                 exchanges_to_analyze_limit: int,
                 write_to_s3: bool):
        self.rate_limiter_max_retries = rate_limiter_max_retries
        self.historical_data_lookback_days = historical_data_lookback_days
        self.log_level = log_level
        self.exchanges_with_similar_trades_to_analyze = exchanges_with_similar_trades_to_analyze
        self.exchanges_to_analyze_limit = exchanges_to_analyze_limit
        self.write_to_s3 = write_to_s3



    
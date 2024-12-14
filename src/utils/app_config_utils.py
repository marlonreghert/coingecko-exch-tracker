import json
from src.config.app_config import AppConfig

class AppConfigUtils:
    @staticmethod
    def from_json(json_str: str):
        """
        Create a Config instance from a JSON string.

        :param json_str: JSON string containing configuration values.
        :return: Config instance.
        """
        data = json.loads(json_str)
        return AppConfig( \
            rate_limiter_max_retries=data.get("rate_limiter_max_retries"), \
            historical_data_lookback_days=data.get("historical_data_lookback_days"), \
            log_level=data.get("log_level"), \
            exchanges_with_similar_trades_limit=data.get("exchanges_with_similar_trades_limit"), \
            exchanges_to_analyze_limit=data.get("exchanges_with_similar_trades_to_analyze"), \
            write_to_s3=data.get("write_to_s3") \
        )
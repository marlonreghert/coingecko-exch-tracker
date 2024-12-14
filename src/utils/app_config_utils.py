import json
from datetime import datetime
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
        app_config = AppConfig( \
            rate_limiter_max_retries=data.get("rate_limiter_max_retries"), \
            historical_data_lookback_days=data.get("historical_data_lookback_days"), \
            log_level=data.get("log_level"), \
            exchanges_with_similar_trades_limit=data.get("exchanges_with_similar_trades_limit"), \
            exchanges_to_analyze_limit=data.get("exchanges_with_similar_trades_to_analyze"), \
            write_to_s3=data.get("write_to_s3") \
        )

        logical_date_input = data.get("logical_date", "")

        AppConfigUtils.set_logical_date(app_config, logical_date_input)

        return app_config
    
    @staticmethod
    def from_args(args):
        """
        Create a Config instance from a Command line args (dict).

        :param args: Dict of command line args
        :return: Config instance.
        """
        app_config = AppConfig( \
            rate_limiter_max_retries=args.rate_limiter_max_retries, \
            historical_data_lookback_days=args.historical_data_lookback_days, \
            log_level=args.log_level, \
            exchanges_with_similar_trades_to_analyze=args.exchanges_with_similar_trades_to_analyze, \
            exchanges_to_analyze_limit=args.exchanges_to_analyze_limit, \
            write_to_s3=args.write_to_s3 \
        )   

        AppConfigUtils.set_logical_date(app_config, args.logical_date)

        return app_config
    
    @staticmethod
    def set_logical_date(app_config, logical_date_input):
        if logical_date_input == "":
            current_date = datetime.now()
            app_config.set_logical_date(str(current_date.year), str(current_date.month), str(current_date.day))
        else:
            logical_date_entries = logical_date_input.split('-')
            app_config.set_logical_date(logical_date_entries[0], logical_date_entries[1], logical_date_entries[2])            
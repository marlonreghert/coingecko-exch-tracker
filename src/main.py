import argparse
import logging
import sys
import json
import logging
from src.core.coingecko.coingecko_similar_exchanges_data_pipeline import CoingeckoSimilarExchangesDataPipeline
from src.constants.constants import *
from src.di.di_container import DIContainer
from src.config.app_config import AppConfig

def parse_args():
    # Create the parser
    parser = argparse.ArgumentParser(description="A script to extract insights related to exchanges and markets related to Bitso.")
    parser.add_argument("--rate_limiter_max_retries", type=int, default=RATE_LIMITER_MAX_RETRIES_DEFAULT,\
                         help=f"Number of retries for when throttled by an external API rate limiter (default: {RATE_LIMITER_MAX_RETRIES_DEFAULT})")
    
    parser.add_argument("--exchanges_with_similar_trades_to_analyze", type=int, default=EXCHANGES_WITH_SIMILAR_TRADES_TO_ANALYZE_DEFAULT,\
                         help=f"Maximum number of exchanges with similar trades to fetch default: {EXCHANGES_WITH_SIMILAR_TRADES_TO_ANALYZE_DEFAULT}")

    parser.add_argument("--exchanges_to_analyze_limit", type=int, default=EXCHANGES_TO_ANALYZE_DEFAULT_LIMIT,\
                         help=f"Maximum number of exchanges to lookup for trades (default: {EXCHANGES_TO_ANALYZE_DEFAULT_LIMIT})") 
    
    parser.add_argument("--historical_data_lookback_days", type=int, default=HISTORICAL_DATA_LOOKBACK_DAYS_DEFAULT,\
                         help=f"Number of days to lookback when calculating historical volume data (default: {HISTORICAL_DATA_LOOKBACK_DAYS_DEFAULT})") 
        

    parser.add_argument("--write_to_s3", action="store_true", help="If the output files should be uploaded to s3") 

    parser.add_argument("--log_level", type=str, default=LOGGING_DEFAULT_LEVEL, help="Application log level (info, debug, error, ...)")     

    parser.add_argument("--config", type=str, default="", help="Config file with all configs (overrides previous args)") 

    return parser.parse_args()

def create_config_from_args(args):
    # If --config is provided, load settings from the file and override other arguments
    if args.config and args.config != "":
        try:
            with open(args.config, 'r') as f:
                config_args = json.load(f)
                return AppConfig(config_args)
        except Exception as e:
            print(f"Error loading configuration file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        return AppConfig( \
            rate_limiter_max_retries=args.rate_limiter_max_retries, \
            historical_data_lookback_days=args.historical_data_lookback_days, \
            log_level=args.log_level, \
            exchanges_with_similar_trades_to_analyze=args.exchanges_with_similar_trades_to_analyze, \
            exchanges_to_analyze_limit=args.exchanges_to_analyze_limit, \
            write_to_s3=args.write_to_s3 \
        )
    
if __name__ == "__main__":
    # Read args & app config
    args = parse_args()
    app_config = create_config_from_args(args)

    # Set log levels
    logging.basicConfig(level=getattr(logging, app_config.log_level.upper(), LOGGING_DEFAULT_LEVEL)) 

    # Init dependencies
    di_container = DIContainer(app_config)
    di_container.init_deps()

    # Run app 
    di_container.exchanges_analyzer.run()
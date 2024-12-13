from src.services.coingecko.coingecko_data_fetcher import CoingeckoDataFetcher
from src.services.coingecko.coingecko_data_fetcher_limits import CoingeckoDataFetcherLimits

from src.api.coingecko_api import CoingeckoAPI
from src.api.bitso import BitsoAPI
from src.s3.s3_handler import S3Handler
import os
import pandas as pd
import argparse

EXCHANGE_VOLUME_TRADE_DAYS=30

EXCHANGES_TABLE_RELATIVE_PATH = "../data/processed/exchange_table.csv"
SHARED_MARKETS_TABLE_RELATIVE_PATH = "../data/processed/shared_markets_table.csv"
MARKETS_HISTORICAL_VOLUME = "../data/processed/markets_historical_volume_df.csv"
EXCHANGES_HISTORICAL_TRADE_VOLUME_RELATIVE_PATH = "../data/processed/exchanges_historical_trade_volume.csv"
def parse_args():
    # Create the parser
    parser = argparse.ArgumentParser(description="A script to extract insights related to exchanges and markets related to Bitso.")
    parser.add_argument("--coingecko_retries", type=int, default=3, help="Number of retries for when coingecko API fails (default: 3)")
    parser.add_argument("--exchanges_with_similar_trades_limit", type=int, default=2, help="Maximum number of exchanges with similar trades to fetch (default: 2)")
    parser.add_argument("--exchanges_to_lookup_limit", type=int, default=5, help="Maximum number of exchanges to lookup for trades (default: 5)") 
    parser.add_argument("--write_to_s3", action="store_true", help="If the upload to S3 should be skipped") 

    return parser.parse_args()

def run(args):
    print(f"Running with args: {args}")
    
    # Init classes and dependencies
    coingecko_api = CoingeckoAPI(rate_limiter_retries=args.coingecko_retries)

    coingecko_data_fetcher = CoingeckoDataFetcher(coingecko_api, \
                                                      CoingeckoDataFetcherLimits( \
                                                          args.exchanges_with_similar_trades_limit, \
                                                          args.exchanges_to_lookup_limit \
                                                          ))

    bitsoAPI = BitsoAPI()
    bitso_markets = bitsoAPI.fetch_markets()

    exchanges_with_similar_markets, shared_markets = coingecko_data_fetcher.fetch_exchanges_with_similar_trades(bitso_markets)

    markets_historical_volume = coingecko_data_fetcher.fetch_markets_historical_volume_table(shared_markets)
    exchanges_historical_trade_volume = coingecko_data_fetcher.fetch_exchange_trade_volume(exchanges_with_similar_markets, EXCHANGE_VOLUME_TRADE_DAYS)
    

    # Save the tables locally
    os.makedirs("../data/processed", exist_ok=True)

    # Create tables
    exchanges_with_similar_markets_df = pd.DataFrame(exchanges_with_similar_markets)
    shared_markets_df = pd.DataFrame(shared_markets)
    markets_historical_volume_df = pd.DataFrame(markets_historical_volume)
    exchanges_historical_trade_volume_df = pd.DataFrame(exchanges_historical_trade_volume)

    # Save to csv locally
    exchanges_with_similar_markets_df.to_csv(EXCHANGES_TABLE_RELATIVE_PATH, index=False)
    shared_markets_df.to_csv(SHARED_MARKETS_TABLE_RELATIVE_PATH, index=False)
    markets_historical_volume_df.to_csv(MARKETS_HISTORICAL_VOLUME, index=False)
    exchanges_historical_trade_volume_df.to_csv(EXCHANGES_HISTORICAL_TRADE_VOLUME_RELATIVE_PATH, index=False)

    # Save the tables to S3 (Mocked)
    if args.write_to_s3:
        s3 = S3Handler(
            endpoint_url=os.environ.get("S3_ENDPOINT", ""), \
            bucket_name=os.environ.get("AWS_BUCKET", ""),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", ""),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
        )

        s3.upload_file(EXCHANGES_TABLE_RELATIVE_PATH, "processed/exchanges_with_similar_markets_table.csv")
        s3.upload_file(SHARED_MARKETS_TABLE_RELATIVE_PATH, "processed/shared_markets_table.csv")
        s3.upload_file(MARKETS_HISTORICAL_VOLUME, "processed/markets_historical_volume_table.csv")
        s3.upload_file(EXCHANGES_HISTORICAL_TRADE_VOLUME_RELATIVE_PATH, "processed/exchanges_historical_trade_table.csv")

if __name__ == "__main__":
    args = parse_args()
    run(args)
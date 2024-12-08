from src.services.coingecko.coingecko_data_fetcher import CoingeckoDataFetcher
from src.services.coingecko.coingecko_data_fetcher_limits import CoingeckoDataFetcherLimits

from src.api.coingecko_api import CoingeckoAPI
from src.api.bitso import BitsoAPI
from src.s3.s3_handler import S3Handler
import os
import pandas as pd
import argparse

EXCHANGE_VOLUME_TRADE_DAYS=30

def parse_args():
    # Create the parser
    parser = argparse.ArgumentParser(description="A script to extract insights related to exchanges and markets related to Bitso.")
    parser.add_argument("--coingecko_retries", type=int, default=3, help="Number of retries for when coingecko API fails (default: 3)")
    parser.add_argument("--exchanges_with_similar_trades_limit", type=int, default=2, help="Maximum number of exchanges with similar trades to fetch (default: 2)")
    parser.add_argument("--exchanges_to_lookup_limit", type=int, default=5, help="Maximum number of exchanges to lookup for trades (default: 5)") 
    parser.add_argument("--skip_s3_upload", type=bool, default=True, help="If the upload to S3 should be skipped (default: true)") 

    return parser.parse_args()

def run(args):
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

    exchanges_with_similar_markets_df.to_csv("../data/processed/exchange_table.csv", index=False)
    shared_markets_df.to_csv("../data/processed/shared_markets_table.csv", index=False)
    markets_historical_volume_df.to_csv("../data/processed/markets_historical_volume_df.csv", index=False)
    exchanges_historical_trade_volume_df.to_csv("../data/processed/exchanges_historical_trade_volume.csv", index=False)

    # Save the tables to S3 (Mocked)
    if not args.skip_s3_upload:
        s3 = S3Handler(
            bucket_name=os.environ.get("aws-bucket", ""),
            aws_access_key_id=os.environ.get("aws-access-key", ""),
            aws_secret_access_key=os.environ.get("aws-secret-access-key", ""),
        )

        s3.upload_dataframe(exchanges_with_similar_markets_df, "processed/exchanges_with_similar_markets_table.csv")
        s3.upload_dataframe(shared_markets_df, "processed/shared_markets_table.csv")
        s3.upload_dataframe(markets_historical_volume_df, "processed/markets_historical_volume_table.csv")
        s3.upload_dataframe(exchanges_historical_trade_volume, "processed/exchanges_historical_trade_table.csv")

if __name__ == "__main__":
    args = parse_args()
    run(args)
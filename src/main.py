from src.exchanges_tracker import ExchangesTracker
import argparse

def parse_args():
    # Create the parser
    parser = argparse.ArgumentParser(description="A script to extract insights related to exchanges and markets related to Bitso.")
    parser.add_argument("--coingecko_retries", type=int, default=3, help="Number of retries for when coingecko API fails (default: 3)")
    parser.add_argument("--exchanges_with_similar_trades_limit", type=int, default=2, help="Maximum number of exchanges with similar trades to fetch (default: 2)")
    parser.add_argument("--exchanges_to_lookup_limit", type=int, default=5, help="Maximum number of exchanges to lookup for trades (default: 5)") 
    parser.add_argument("--write_to_s3", action="store_true", help="If the upload to S3 should be skipped") 

    return parser.parse_args()

    
if __name__ == "__main__":
    args = parse_args()
    exchanges_tracker = ExchangesTracker()
    exchanges_tracker.run(args.coingecko_retries,\
                                         args.exchanges_with_similar_trades_limit,\
                                         args.exchanges_to_lookup_limit,\
                                         args.write_to_s3)
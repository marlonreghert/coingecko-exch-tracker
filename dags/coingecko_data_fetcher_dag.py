from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from src.services.coingecko.coingecko_data_fetcher import CoingeckoDataFetcher
from src.services.coingecko.coingecko_data_fetcher_limits import CoingeckoDataFetcherLimits
from src.api.coingecko_api import CoingeckoAPI
from src.api.bitso import BitsoAPI
from s3.s3_handler import S3Handler
import os
import pandas as pd

# Constants
EXCHANGE_VOLUME_TRADE_DAYS = 30

# Define the function to be run as the Airflow task
def fetch_coingecko_data():
    # Set up arguments (hardcoded for Airflow execution)
    args = {
        "coingecko_retries": 3,
        "exchanges_with_similar_trades_limit": 2,
        "exchanges_to_lookup_limit": 5,
        "skip_s3_upload": False,  # Set to False to enable S3 uploads
    }

    # Initialize dependencies
    coingecko_api = CoingeckoAPI(rate_limiter_retries=args["coingecko_retries"])
    coingecko_data_fetcher = CoingeckoDataFetcher(
        coingecko_api,
        CoingeckoDataFetcherLimits(
            args["exchanges_with_similar_trades_limit"],
            args["exchanges_to_lookup_limit"],
        ),
    )
    bitso_api = BitsoAPI()

    # Fetch data
    bitso_markets = bitso_api.fetch_markets()
    exchanges_with_similar_markets, shared_markets = coingecko_data_fetcher.fetch_exchanges_with_similar_trades(
        bitso_markets
    )
    markets_historical_volume = coingecko_data_fetcher.fetch_markets_historical_volume_table(shared_markets)
    exchanges_historical_trade_volume = coingecko_data_fetcher.fetch_exchange_trade_volume(
        exchanges_with_similar_markets, EXCHANGE_VOLUME_TRADE_DAYS
    )

    # Save locally
    os.makedirs("../data/processed", exist_ok=True)
    pd.DataFrame(exchanges_with_similar_markets).to_csv("../data/processed/exchange_table.csv", index=False)
    pd.DataFrame(shared_markets).to_csv("../data/processed/shared_markets_table.csv", index=False)
    pd.DataFrame(markets_historical_volume).to_csv("../data/processed/markets_historical_volume_df.csv", index=False)
    pd.DataFrame(exchanges_historical_trade_volume).to_csv("../data/processed/exchanges_historical_trade_volume.csv", index=False)

    # Upload to S3
    s3 = S3Handler(
        bucket_name=os.environ.get("aws-bucket", ""),
        aws_access_key_id=os.environ.get("aws-access-key", ""),
        aws_secret_access_key=os.environ.get("aws-secret-access-key", ""),
    )
    s3.upload_dataframe(pd.DataFrame(exchanges_with_similar_markets), "processed/exchange_table.csv")
    s3.upload_dataframe(pd.DataFrame(shared_markets), "processed/shared_markets_table.csv")
    s3.upload_dataframe(pd.DataFrame(markets_historical_volume), "processed/markets_historical_volume_df.csv")
    s3.upload_dataframe(pd.DataFrame(exchanges_historical_trade_volume), "processed/exchanges_historical_trade_volume.csv")

# Define the Airflow DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="coingecko_data_fetcher_dag",
    default_args=default_args,
    description="A DAG to fetch and process data from the CoinGecko API",
    schedule_interval="@daily",  # Run daily
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:
    # Define the task
    fetch_data_task = PythonOperator(
        task_id="fetch_coingecko_data",
        python_callable=fetch_coingecko_data,
    )

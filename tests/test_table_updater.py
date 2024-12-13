import unittest
from unittest.mock import Mock, patch, call
import os
import pandas as pd
import argparse
from src.table_updater import run, parse_args, EXCHANGE_VOLUME_TRADE_DAYS


class TestTableUpdater(unittest.TestCase):
    @patch("src.table_updater.CoingeckoAPI")
    @patch("src.table_updater.CoingeckoDataFetcher")
    @patch("src.table_updater.BitsoAPI")
    @patch("src.table_updater.S3Handler")
    @patch("src.table_updater.pd.DataFrame.to_csv")  # Mock saving to CSV
    @patch("src.table_updater.os.makedirs")  # Mock directory creation
    def test_run_with_mocked_dependencies(
        self, mock_makedirs, mock_to_csv, MockS3Handler, MockBitsoAPI, MockCoingeckoDataFetcher, MockCoingeckoAPI
    ):
        # Mock command-line arguments
        args = Mock()
        args.coingecko_retries = 3
        args.exchanges_with_similar_trades_limit = 2
        args.exchanges_to_lookup_limit = 5
        args.write_to_s3 = False

        # Set up mocked dependencies
        MockBitsoAPI.return_value.fetch_markets.return_value = [("BTC", "USD")]

        MockCoingeckoDataFetcher.return_value.fetch_exchanges_with_similar_trades.return_value = (
            [{"exchange_id": "binance"}],
            [{"market_id": "BTC_USD"}],
        )
        MockCoingeckoDataFetcher.return_value.fetch_markets_historical_volume_table.return_value = [
            {"market_id": "BTC_USD", "date": "2023-12-01", "volume_usd": 1000}
        ]
        MockCoingeckoDataFetcher.return_value.fetch_exchange_trade_volume.return_value = [
            {"exchange_id": "binance", "date": "2023-12-01", "volume_btc": 50}
        ]

        # Mock environment variables for S3
        with patch.dict(
            os.environ,
            {"aws-bucket": "mock-bucket", "aws-access-key": "mock-access", "aws-secret-access-key": "mock-secret"},
        ):
            # Run the script logic
            run(args)

        # Verify directories were created
        mock_makedirs.assert_called_once_with("../data/processed", exist_ok=True)

        # Verify data fetch calls
        MockBitsoAPI.return_value.fetch_markets.assert_called_once()
        MockCoingeckoDataFetcher.return_value.fetch_exchanges_with_similar_trades.assert_called_once_with(
            [("BTC", "USD")]
        )
        MockCoingeckoDataFetcher.return_value.fetch_markets_historical_volume_table.assert_called_once_with(
            [{"market_id": "BTC_USD"}]
        )
        MockCoingeckoDataFetcher.return_value.fetch_exchange_trade_volume.assert_called_once_with(
            [{"exchange_id": "binance"}], EXCHANGE_VOLUME_TRADE_DAYS
        )

        # Verify CSV saving
        self.assertEqual(mock_to_csv.call_count, 4)

        # Verify S3 uploads are skipped
        MockS3Handler.return_value.upload_dataframe.assert_not_called()

    @patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(
        coingecko_retries=3,
        exchanges_with_similar_trades_limit=2,
        exchanges_to_lookup_limit=5,
        write_to_s3=False
    ))
    def test_parse_args(self, mock_parse_args):
        # Test that parse_args correctly parses command-line arguments
        args = parse_args()
        self.assertEqual(args.coingecko_retries, 3)
        self.assertEqual(args.exchanges_with_similar_trades_limit, 2)
        self.assertEqual(args.exchanges_to_lookup_limit, 5)
        self.assertEqual(args.write_to_s3, False)

if __name__ == "__main__":
    unittest.main()

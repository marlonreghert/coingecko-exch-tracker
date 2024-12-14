import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from src.adapters.s3_handler import S3Handler


class TestS3Handler(unittest.TestCase):
    @patch("os.remove")
    def test_upload_file(self, mock_remove):
        mock_s3_client = MagicMock()
        handler = S3Handler(mock_s3_client, "test-bucket")

        handler.upload_file("test_file.csv", "test_key")

        mock_s3_client.upload_file.assert_called_once_with("test_file.csv", "test-bucket", "test_key")

    @patch("os.remove")
    def test_download_file(self, mock_remove):
        mock_s3_client = MagicMock()
        handler = S3Handler(mock_s3_client, "test-bucket")

        handler.download_file("test_key", "test_file.csv")

        mock_s3_client.download_file.assert_called_once_with("test-bucket", "test_key", "test_file.csv")

    @patch("os.remove")
    def test_upload_dataframe(self, mock_remove):
        mock_s3_client = MagicMock()
        handler = S3Handler(mock_s3_client, "test-bucket")

        df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

        with patch("pandas.DataFrame.to_csv") as mock_to_csv:
            handler.upload_dataframe(df, "test_key")

            mock_to_csv.assert_called_once_with("temp.csv", index=False)
            mock_s3_client.upload_file.assert_called_once_with("temp.csv", "test-bucket", "test_key")
            mock_remove.assert_called_once_with("temp.csv")

    @patch("os.remove")
    def test_download_dataframe(self, mock_remove):
        mock_s3_client = MagicMock()
        handler = S3Handler(mock_s3_client, "test-bucket")

        with patch("pandas.read_csv", return_value=pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})) as mock_read_csv:
            df = handler.download_dataframe("test_key")

            mock_s3_client.download_file.assert_called_once_with("test-bucket", "test_key", "temp.csv")
            mock_read_csv.assert_called_once_with("temp.csv")
            mock_remove.assert_called_once_with("temp.csv")

            self.assertTrue(isinstance(df, pd.DataFrame))
            self.assertListEqual(df.columns.tolist(), ["col1", "col2"])
            self.assertListEqual(df["col1"].tolist(), [1, 2, 3])
            self.assertListEqual(df["col2"].tolist(), ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()

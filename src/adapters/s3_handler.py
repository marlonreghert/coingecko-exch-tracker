import pandas as pd
import os
import logging 

class S3Handler:
    def __init__(self, s3_client, bucket_name):
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.logger = logging.getLogger(self.__class__.__name__)

    def upload_file(self, file_path, s3_key):
        self.logger.info(f"Uploading... {file_path} to s3://{self.bucket_name}/{s3_key}")
        self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
        self.logger.info(f"Uploaded {file_path} to s3://{self.bucket_name}/{s3_key}")

    def download_file(self, s3_key, file_path):
        self.logger.info(f"Downloading... s3://{self.bucket_name}/{s3_key} to {file_path}")
        self.s3_client.download_file(self.bucket_name, s3_key, file_path)
        self.logger.info(f"Downloaded s3://{self.bucket_name}/{s3_key} to {file_path}")

    def upload_dataframe(self, df, s3_key):
        temp_file = "temp.csv"
        df.to_csv(temp_file, index=False)
        self.upload_file(temp_file, s3_key)
        os.remove(temp_file)

    def download_dataframe(self, s3_key):
        temp_file = "temp.csv"
        self.download_file(s3_key, temp_file)
        df = pd.read_csv(temp_file)
        os.remove(temp_file)
        return df
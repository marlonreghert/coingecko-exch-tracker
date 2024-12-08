import boto3
import pandas as pd
import os

class S3Handler:
    def __init__(self, bucket_name, aws_access_key_id, aws_secret_access_key, region_name="us-east-1"):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        self.bucket_name = bucket_name

    def upload_file(self, file_path, s3_key):
        self.s3.upload_file(file_path, self.bucket_name, s3_key)
        print(f"Uploaded {file_path} to s3://{self.bucket_name}/{s3_key}")

    def download_file(self, s3_key, file_path):
        self.s3.download_file(self.bucket_name, s3_key, file_path)
        print(f"Downloaded s3://{self.bucket_name}/{s3_key} to {file_path}")

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
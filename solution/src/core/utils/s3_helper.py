from typing import IO
from botocore.exceptions import NoCredentialsError
from pydantic import HttpUrl

from src.core.data import settings
import boto3


class S3Helper:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )
        self.bucket_name = settings.s3_bucket_name

    def upload_file(self, file: IO, object_name: str) -> HttpUrl:
        self.s3_client.upload_fileobj(
            file,
            self.bucket_name,
            object_name,
            ExtraArgs={"ACL": "public-read"},
        )
        return HttpUrl(f"{settings.s3_endpoint_url}/{self.bucket_name}/{object_name}")

    def delete_file(self, object_name: str) -> None:
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)

    def download_file(self, object_name: str, file_path: str) -> None:
        self.s3_client.download_file(self.bucket_name, object_name, file_path)

    def list_files_by_prefix(self, prefix: str) -> list[HttpUrl]:
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=prefix
        )
        if "Contents" not in response:
            return []
        return [
            HttpUrl(f"{settings.s3_endpoint_url}/{self.bucket_name}/{obj['Key']}")
            for obj in response["Contents"]
        ]


s3_helper = S3Helper()

import boto3

from app.core.config import settings


class StorageService:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION,
        )

        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            self.client.head_bucket(Bucket=settings.S3_BUCKET)
        except Exception:
            self.client.create_bucket(Bucket=settings.S3_BUCKET)

    def upload(
        self,
        object_key: str,
        file_content: bytes,
        content_type: str,
    ) -> None:
        self.client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=object_key,
            Body=file_content,
            ContentType=content_type,
        )

    def download(
        self,
        object_key: str,
    ) -> bytes:
        response = self.client.get_object(
            Bucket=settings.S3_BUCKET,
            Key=object_key,
        )

        try:
            return response["Body"].read()
        finally:
            response["Body"].close()

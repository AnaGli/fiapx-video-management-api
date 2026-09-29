from unittest.mock import Mock, patch

from app.services.storage_service import StorageService


@patch("app.services.storage_service.boto3.client")
def test_init_does_not_create_bucket_when_bucket_exists(mock_client):
    client = Mock()
    mock_client.return_value = client

    service = StorageService()

    assert service.client == client
    client.head_bucket.assert_called_once()
    client.create_bucket.assert_not_called()


@patch("app.services.storage_service.boto3.client")
def test_init_creates_bucket_when_bucket_does_not_exist(mock_client):
    client = Mock()
    client.head_bucket.side_effect = Exception("bucket not found")
    mock_client.return_value = client

    StorageService()

    client.head_bucket.assert_called_once()
    client.create_bucket.assert_called_once()


@patch("app.services.storage_service.boto3.client")
def test_upload(mock_client):
    client = Mock()
    mock_client.return_value = client

    service = StorageService()

    content = b"video content"

    result = service.upload(
        object_key="videos/123/input/video.mp4",
        file_content=content,
        content_type="video/mp4",
    )

    assert result is None
    client.put_object.assert_called_once()


@patch("app.services.storage_service.boto3.client")
def test_download(mock_client):
    client = Mock()
    body = Mock()
    body.read.return_value = b"video content"

    client.get_object.return_value = {"Body": body}
    mock_client.return_value = client

    service = StorageService()

    result = service.download("videos/123/input/video.mp4")

    assert result == b"video content"
    body.read.assert_called_once()
    body.close.assert_called_once()

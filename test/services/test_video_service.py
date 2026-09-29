from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from app.models.video import VideoStatus
from app.services.video_service import VideoService


@patch("app.services.video_service.StorageService")
@patch("app.services.video_service.RabbitMQPublisher")
@patch("app.services.video_service.VideoRepository")
@patch("app.services.video_service.uuid.uuid4")
def test_create_video(
    mock_uuid4,
    mock_repository_class,
    mock_publisher_class,
    mock_storage_class,
):
    db = Mock()
    user_id = uuid4()
    video_id = uuid4()
    mock_uuid4.return_value = video_id

    repository = Mock()
    publisher = Mock()
    storage = Mock()

    mock_repository_class.return_value = repository
    mock_publisher_class.return_value = publisher
    mock_storage_class.return_value = storage

    video = Mock()
    video.id = video_id
    video.user_id = user_id
    repository.create.return_value = video

    service = VideoService(db)

    result = service.create_video(
        user_id=user_id,
        filename="video.mp4",
        file_content=b"video",
        content_type="video/mp4",
    )

    assert result == video
    storage.upload.assert_called_once()
    repository.create.assert_called_once()
    publisher.publish.assert_called_once()


@patch("app.services.video_service.StorageService")
@patch("app.services.video_service.RabbitMQPublisher")
@patch("app.services.video_service.VideoRepository")
def test_create_video_rejects_empty_file(
    mock_repository_class,
    mock_publisher_class,
    mock_storage_class,
):
    service = VideoService(Mock())

    with pytest.raises(ValueError, match="Uploaded file is empty"):
        service.create_video(
            user_id=uuid4(),
            filename="video.mp4",
            file_content=b"",
            content_type="video/mp4",
        )

    mock_storage_class.return_value.upload.assert_not_called()
    mock_repository_class.return_value.create.assert_not_called()
    mock_publisher_class.return_value.publish.assert_not_called()


@patch("app.services.video_service.StorageService")
@patch("app.services.video_service.RabbitMQPublisher")
@patch("app.services.video_service.VideoRepository")
def test_get_video(
    mock_repository_class,
    mock_publisher_class,
    mock_storage_class,
):
    service = VideoService(Mock())
    video = Mock()
    service.video_repository.find_by_id.return_value = video

    result = service.get_video(uuid4(), uuid4())

    assert result == video
    service.video_repository.find_by_id.assert_called_once()


@patch("app.services.video_service.StorageService")
@patch("app.services.video_service.RabbitMQPublisher")
@patch("app.services.video_service.VideoRepository")
def test_list_videos(
    mock_repository_class,
    mock_publisher_class,
    mock_storage_class,
):
    service = VideoService(Mock())

    videos = [Mock(), Mock()]
    service.video_repository.list_by_user.return_value = videos
    service.video_repository.count_by_user.return_value = 2

    result = service.list_videos(uuid4())

    assert result == (videos, 2)


@patch("app.services.video_service.StorageService")
@patch("app.services.video_service.RabbitMQPublisher")
@patch("app.services.video_service.VideoRepository")
def test_mark_as_completed(
    mock_repository_class,
    mock_publisher_class,
    mock_storage_class,
):
    service = VideoService(Mock())

    video = Mock()
    service.video_repository.find_by_id.return_value = video
    service.video_repository.update_status.return_value = video

    result = service.mark_as_completed(
        video_id=uuid4(),
        user_id=uuid4(),
        output_object_key="videos/123/output/frames.zip",
        frame_count=150,
    )

    assert result == video
    service.video_repository.update_status.assert_called_once_with(
        video=video,
        status=VideoStatus.COMPLETED,
        output_path="videos/123/output/frames.zip",
        frame_count=150,
    )


@patch("app.services.video_service.StorageService")
@patch("app.services.video_service.RabbitMQPublisher")
@patch("app.services.video_service.VideoRepository")
def test_mark_as_completed_when_video_does_not_exist(
    mock_repository_class,
    mock_publisher_class,
    mock_storage_class,
):
    service = VideoService(Mock())
    service.video_repository.find_by_id.return_value = None

    with pytest.raises(ValueError, match="Video not found"):
        service.mark_as_completed(
            video_id=uuid4(),
            user_id=uuid4(),
            output_object_key="output.zip",
            frame_count=10,
        )


@patch("app.services.video_service.StorageService")
@patch("app.services.video_service.RabbitMQPublisher")
@patch("app.services.video_service.VideoRepository")
def test_mark_as_failed(
    mock_repository_class,
    mock_publisher_class,
    mock_storage_class,
):
    service = VideoService(Mock())

    video = Mock()
    service.video_repository.find_by_id.return_value = video
    service.video_repository.update_status.return_value = video

    result = service.mark_as_failed(
        video_id=uuid4(),
        user_id=uuid4(),
        error_message="FFmpeg failed",
    )

    assert result == video
    service.video_repository.update_status.assert_called_once_with(
        video=video,
        status=VideoStatus.FAILED,
        error_message="FFmpeg failed",
    )


@patch("app.services.video_service.StorageService")
@patch("app.services.video_service.RabbitMQPublisher")
@patch("app.services.video_service.VideoRepository")
def test_mark_as_failed_when_video_does_not_exist(
    mock_repository_class,
    mock_publisher_class,
    mock_storage_class,
):
    service = VideoService(Mock())
    service.video_repository.find_by_id.return_value = None

    with pytest.raises(ValueError, match="Video not found"):
        service.mark_as_failed(
            video_id=uuid4(),
            user_id=uuid4(),
            error_message="FFmpeg failed",
        )


@patch("app.services.video_service.StorageService")
@patch("app.services.video_service.RabbitMQPublisher")
@patch("app.services.video_service.VideoRepository")
def test_download_video(
    mock_repository_class,
    mock_publisher_class,
    mock_storage_class,
):
    service = VideoService(Mock())

    video = Mock()
    video.output_path = "videos/123/output/frames.zip"

    service.video_repository.find_by_id.return_value = video
    service.storage_service.download.return_value = b"zip content"

    result = service.download_video(uuid4(), uuid4())

    assert result == b"zip content"
    service.storage_service.download.assert_called_once_with(
        object_key=video.output_path,
    )


@patch("app.services.video_service.StorageService")
@patch("app.services.video_service.RabbitMQPublisher")
@patch("app.services.video_service.VideoRepository")
def test_download_video_when_video_does_not_exist(
    mock_repository_class,
    mock_publisher_class,
    mock_storage_class,
):
    service = VideoService(Mock())
    service.video_repository.find_by_id.return_value = None

    result = service.download_video(uuid4(), uuid4())

    assert result is None


@patch("app.services.video_service.StorageService")
@patch("app.services.video_service.RabbitMQPublisher")
@patch("app.services.video_service.VideoRepository")
def test_download_video_when_output_does_not_exist(
    mock_repository_class,
    mock_publisher_class,
    mock_storage_class,
):
    service = VideoService(Mock())

    video = Mock()
    video.output_path = None
    service.video_repository.find_by_id.return_value = video

    result = service.download_video(uuid4(), uuid4())

    assert result is None

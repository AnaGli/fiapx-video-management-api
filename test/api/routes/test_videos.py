import asyncio
from unittest.mock import AsyncMock, Mock, patch


from uuid import uuid4
from datetime import datetime, timezone
from uuid import uuid4
import pytest
from app.models.video import VideoStatus


from fastapi import HTTPException, UploadFile

from app.api.routes.videos import download_video, get_video, list_videos, upload_video


def make_user():
    user = Mock()
    user.id = uuid4()
    return user


def test_upload_video():
    user = make_user()
    file = Mock(spec=UploadFile)
    file.filename = "video.mp4"
    file.content_type = "video/mp4"
    file.read = AsyncMock(return_value=b"video-content")

    with patch("app.api.routes.videos.VideoService") as service_class:
        video = Mock()
        service_class.return_value.create_video.return_value = video

        result = asyncio.run(
            upload_video(
                file=file,
                current_user=user,
                db=Mock(),
            )
        )

    assert result == video
    service_class.return_value.create_video.assert_called_once_with(
        user_id=user.id,
        filename="video.mp4",
        file_content=b"video-content",
        content_type="video/mp4",
    )


def test_upload_video_default_content_type():
    user = make_user()
    file = Mock(spec=UploadFile)
    file.filename = "video.mp4"
    file.content_type = None
    file.read = AsyncMock(return_value=b"video-content")

    with patch("app.api.routes.videos.VideoService") as service_class:
        service_class.return_value.create_video.return_value = Mock()
        asyncio.run(
            upload_video(
                file=file,
                current_user=user,
                db=Mock(),
            )
        )

    service_class.return_value.create_video.assert_called_once_with(
        user_id=user.id,
        filename="video.mp4",
        file_content=b"video-content",
        content_type="application/octet-stream",
    )


def make_video():
    video = Mock()
    video.id = uuid4()
    video.original_filename = "video.mp4"
    video.status = VideoStatus.COMPLETED
    video.frame_count = 150
    video.error_message = None
    video.created_at = datetime.now(timezone.utc)
    video.updated_at = datetime.now(timezone.utc)
    return video


def test_list_videos():
    user = make_user()
    videos = [make_video(), make_video()]

    with patch("app.api.routes.videos.VideoService") as service_class:
        service_class.return_value.list_videos.return_value = (videos, 2)

        result = list_videos(
            current_user=user,
            db=Mock(),
        )

    assert len(result.items) == 2
    assert result.total == 2
    assert result.items[0].original_filename == "video.mp4"
    assert result.items[0].frame_count == 150

    service_class.return_value.list_videos.assert_called_once_with(
        user_id=user.id,
    )


def test_get_video_success():
    user = make_user()
    video_id = uuid4()
    video = Mock()

    with patch("app.api.routes.videos.VideoService") as service_class:
        service_class.return_value.get_video.return_value = video
        result = get_video(video_id=video_id, current_user=user, db=Mock())

    assert result == video


def test_get_video_not_found():
    user = make_user()
    video_id = uuid4()

    with patch("app.api.routes.videos.VideoService") as service_class:
        service_class.return_value.get_video.return_value = None
        with pytest.raises(HTTPException) as exc:
            get_video(video_id=video_id, current_user=user, db=Mock())

    assert exc.value.status_code == 404
    assert exc.value.detail == "Video not found"


def test_download_video_success():
    user = make_user()
    video_id = uuid4()

    with patch("app.api.routes.videos.VideoService") as service_class:
        service_class.return_value.download_video.return_value = b"zip-content"
        result = download_video(video_id=video_id, current_user=user, db=Mock())

    assert result.body == b"zip-content"
    assert result.media_type == "application/zip"
    assert result.headers["content-disposition"] == 'attachment; filename="frames.zip"'


def test_download_video_not_found():
    user = make_user()
    video_id = uuid4()

    with patch("app.api.routes.videos.VideoService") as service_class:
        service_class.return_value.download_video.return_value = None
        with pytest.raises(HTTPException) as exc:
            download_video(video_id=video_id, current_user=user, db=Mock())

    assert exc.value.status_code == 404
    assert exc.value.detail == "Processed video not available"

from unittest.mock import Mock
from uuid import uuid4

from app.models.video import VideoStatus
from app.repositories.video_repository import VideoRepository


def test_create():
    db = Mock()
    repository = VideoRepository(db)
    video = Mock()

    result = repository.create(video)

    assert result == video
    db.add.assert_called_once_with(video)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(video)


def test_find_by_id():
    db = Mock()
    repository = VideoRepository(db)

    video_id = uuid4()
    user_id = uuid4()
    video = Mock()
    db.scalar.return_value = video

    result = repository.find_by_id(video_id, user_id)

    assert result == video
    db.scalar.assert_called_once()


def test_list_by_user():
    db = Mock()
    repository = VideoRepository(db)

    user_id = uuid4()
    videos = [Mock(), Mock()]
    db.scalars.return_value.all.return_value = videos

    result = repository.list_by_user(user_id)

    assert result == videos
    db.scalars.assert_called_once()


def test_count_by_user():
    db = Mock()
    repository = VideoRepository(db)

    user_id = uuid4()
    db.scalar.return_value = 5

    result = repository.count_by_user(user_id)

    assert result == 5
    db.scalar.assert_called_once()


def test_count_by_user_returns_zero_when_scalar_is_none():
    db = Mock()
    repository = VideoRepository(db)

    user_id = uuid4()
    db.scalar.return_value = None

    result = repository.count_by_user(user_id)

    assert result == 0


def test_update_status_with_all_optional_fields():
    db = Mock()
    repository = VideoRepository(db)
    video = Mock()

    result = repository.update_status(
        video=video,
        status=VideoStatus.COMPLETED,
        output_path="videos/123/output/frames.zip",
        frame_count=150,
        error_message="previous error",
    )

    assert result == video
    assert video.status == VideoStatus.COMPLETED
    assert video.output_path == "videos/123/output/frames.zip"
    assert video.frame_count == 150
    assert video.error_message == "previous error"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(video)


def test_update_status_without_optional_fields():
    db = Mock()
    repository = VideoRepository(db)
    video = Mock()

    result = repository.update_status(
        video=video,
        status=VideoStatus.PROCESSING,
    )

    assert result == video
    assert video.status == VideoStatus.PROCESSING
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(video)

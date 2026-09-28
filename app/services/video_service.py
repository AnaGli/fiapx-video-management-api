import uuid

from sqlalchemy.orm import Session

from app.messaging.rabbitmq import RabbitMQPublisher
from app.models.video import Video, VideoStatus
from app.repositories.video_repository import VideoRepository
from app.schemas.events import VideoProcessingRequested
from app.services.storage_service import StorageService


class VideoService:
    def __init__(self, db: Session):
        self.video_repository = VideoRepository(db)
        self.rabbitmq_publisher = RabbitMQPublisher()
        self.storage_service = StorageService()

    def create_video(
        self,
        user_id,
        filename: str,
        file_content: bytes,
        content_type: str,
    ):
        if not file_content:
            raise ValueError(f"Uploaded file is empty: {filename}")

        video_id = uuid.uuid4()

        object_key = f"videos/{video_id}/input/{filename}"

        self.storage_service.upload(
            object_key=object_key,
            file_content=file_content,
            content_type=content_type,
        )

        video = Video(
            id=video_id,
            user_id=user_id,
            original_filename=filename,
            status=VideoStatus.QUEUED,
            input_path=object_key,
        )

        video = self.video_repository.create(video)

        event = VideoProcessingRequested(
            video_id=video.id,
            user_id=video.user_id,
            input_object_key=object_key,
        )

        self.rabbitmq_publisher.publish(
            message=event.model_dump(mode="json"),
        )

        return video

    def get_video(
        self,
        video_id,
        user_id,
    ):
        return self.video_repository.find_by_id(
            video_id=video_id,
            user_id=user_id,
        )

    def list_videos(
        self,
        user_id,
    ):
        videos = self.video_repository.list_by_user(
            user_id=user_id,
        )

        total = self.video_repository.count_by_user(
            user_id=user_id,
        )

        return videos, total

    def mark_as_completed(
        self,
        video_id,
        user_id,
        output_object_key: str,
        frame_count: int,
    ):
        video = self.video_repository.find_by_id(
            video_id=video_id,
            user_id=user_id,
        )

        if video is None:
            raise ValueError(f"Video not found: {video_id}")

        return self.video_repository.update_status(
            video=video,
            status=VideoStatus.COMPLETED,
            output_path=output_object_key,
            frame_count=frame_count,
        )

    def mark_as_failed(
        self,
        video_id,
        user_id,
        error_message: str,
    ):
        video = self.video_repository.find_by_id(
            video_id=video_id,
            user_id=user_id,
        )

        if video is None:
            raise ValueError(f"Video not found: {video_id}")

        return self.video_repository.update_status(
            video=video,
            status=VideoStatus.FAILED,
            error_message=error_message,
        )

    def download_video(
        self,
        video_id,
        user_id,
    ):
        video = self.video_repository.find_by_id(
            video_id=video_id,
            user_id=user_id,
        )

        if video is None:
            return None

        if not video.output_path:
            return None

        return self.storage_service.download(
            object_key=video.output_path,
        )

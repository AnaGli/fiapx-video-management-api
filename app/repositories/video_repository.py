import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.video import Video, VideoStatus


class VideoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, video: Video) -> Video:
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        return video

    def find_by_id(
        self,
        video_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Video | None:
        statement = select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id,
        )

        return self.db.scalar(statement)

    def list_by_user(
        self,
        user_id: uuid.UUID,
    ) -> list[Video]:
        statement = (
            select(Video)
            .where(Video.user_id == user_id)
            .order_by(Video.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def count_by_user(
        self,
        user_id: uuid.UUID,
    ) -> int:
        statement = (
            select(func.count()).select_from(Video).where(Video.user_id == user_id)
        )

        return self.db.scalar(statement) or 0

    def update_status(
        self,
        video: Video,
        status: VideoStatus,
        output_path: str | None = None,
        frame_count: int | None = None,
        error_message: str | None = None,
    ) -> Video:
        video.status = status

        if output_path is not None:
            video.output_path = output_path

        if frame_count is not None:
            video.frame_count = frame_count

        if error_message is not None:
            video.error_message = error_message

        self.db.commit()
        self.db.refresh(video)

        return video

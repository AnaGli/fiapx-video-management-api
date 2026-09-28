from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.video import VideoStatus


class VideoResponse(BaseModel):
    id: UUID
    original_filename: str
    status: VideoStatus
    frame_count: int | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class VideoListResponse(BaseModel):
    items: list[VideoResponse]
    total: int
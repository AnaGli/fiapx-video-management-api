import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.video import VideoListResponse, VideoResponse
from app.services.video_service import VideoService
from fastapi.responses import Response

router = APIRouter()


@router.post(
    "",
    response_model=VideoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_content = await file.read()

    service = VideoService(db)

    return service.create_video(
        user_id=current_user.id,
        filename=file.filename,
        file_content=file_content,
        content_type=file.content_type or "application/octet-stream",
    )


@router.get(
    "/",
    response_model=VideoListResponse,
)
def list_videos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = VideoService(db)

    videos, total = service.list_videos(
        user_id=current_user.id,
    )

    return VideoListResponse(
        items=videos,
        total=total,
    )


@router.get(
    "/{video_id}",
    response_model=VideoResponse,
)
def get_video(
    video_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = VideoService(db)

    video = service.get_video(
        video_id=video_id,
        user_id=current_user.id,
    )

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    return video


@router.get(
    "/{video_id}/download",
)
@router.get(
    "/{video_id}/download",
)
def download_video(
    video_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = VideoService(db)

    file_content = service.download_video(
        video_id=video_id,
        user_id=current_user.id,
    )

    if file_content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processed video not available",
        )

    return Response(
        content=file_content,
        media_type="application/zip",
        headers={
            "Content-Disposition": (f'attachment; filename="frames.zip"'),
        },
    )

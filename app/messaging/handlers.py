import json
import logging

from app.dependencies.database import SessionLocal
from app.schemas.events import (
    VideoProcessingCompleted,
    VideoProcessingFailed,
)
from app.services.video_service import VideoService

logger = logging.getLogger(__name__)


def handle_video_completed(
    channel,
    method,
    properties,
    body: bytes,
) -> None:
    try:
        event = VideoProcessingCompleted.model_validate(json.loads(body))

        logger.info(
            "Received video processing completed event: %s",
            event.video_id,
        )

        db = SessionLocal()

        try:
            service = VideoService(db)

            service.mark_as_completed(
                video_id=event.video_id,
                user_id=event.user_id,
                output_object_key=event.output_object_key,
                frame_count=event.frame_count,
            )

            logger.info(
                "Video %s marked as COMPLETED",
                event.video_id,
            )

            channel.basic_ack(delivery_tag=method.delivery_tag)

        finally:
            db.close()

    except Exception:
        logger.exception("Error handling video completed event")

        channel.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False,
        )


def handle_video_failed(
    channel,
    method,
    properties,
    body: bytes,
) -> None:
    try:
        event = VideoProcessingFailed.model_validate(json.loads(body))

        logger.info(
            "Received video processing failed event: %s",
            event.video_id,
        )

        db = SessionLocal()

        try:
            service = VideoService(db)

            service.mark_as_failed(
                video_id=event.video_id,
                user_id=event.user_id,
                error_message=event.error_message,
            )

            logger.info(
                "Video %s marked as FAILED",
                event.video_id,
            )

            channel.basic_ack(delivery_tag=method.delivery_tag)

        finally:
            db.close()

    except Exception:
        logger.exception("Error handling video failed event")

        channel.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False,
        )

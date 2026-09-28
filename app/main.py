import logging
from contextlib import asynccontextmanager
from threading import Thread

from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.videos import router as videos_router
from app.core.config import settings
from app.messaging.handlers import (
    handle_video_completed,
    handle_video_failed,
)
from app.messaging.rabbitmq import (
    RabbitMQConsumer,
    RabbitMQInitializer,
)

logging.basicConfig(
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def start_rabbitmq_consumer() -> None:
    logger.info("Starting RabbitMQ result consumer")

    consumer = RabbitMQConsumer()

    consumer.consume_results(
        completed_callback=handle_video_completed,
        failed_callback=handle_video_failed,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the queues owned by the API.
    rabbitmq_initializer = RabbitMQInitializer()
    rabbitmq_initializer.initialize()

    logger.info("RabbitMQ queues initialized")

    # Start result consumer in a separate thread.
    consumer_thread = Thread(
        target=start_rabbitmq_consumer,
        name="rabbitmq-result-consumer",
        daemon=True,
    )

    consumer_thread.start()

    logger.info("RabbitMQ result consumer started")

    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API responsible for user management " "and video processing requests."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


@app.get(
    "/health",
    tags=["Health"],
)
def health_check():
    return {"status": "ok"}


app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

app.include_router(
    videos_router,
    prefix="/api/videos",
    tags=["Videos"],
)

from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.clients import router as clients_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.parts import router as parts_router
from app.api.routes.service_order_approval import (
    router as service_order_approval_router
)
from app.api.routes.service_orders import router as service_orders_router
from app.api.routes.services import router as services_router
from app.api.routes.stock_movements import router as stock_router
from app.api.routes.vehicles import router as vehicles_router

from app.core.logging_config import setup_logging
from app.core.middleware.correlation_id import CorrelationIdMiddleware
from ddtrace import patch_all
from ddtrace.contrib.asgi import TraceMiddleware


patch_all()

setup_logging()

app = FastAPI(
    title="Tech Challenge API",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

app.add_middleware(TraceMiddleware)


@app.get("/health", tags=["Health"])
def health():

    return {
        "status": "healthy"
    }


app.include_router(auth_router)

app.include_router(clients_router)

app.include_router(vehicles_router)

app.include_router(services_router)

app.include_router(parts_router)

app.include_router(stock_router)

app.include_router(service_orders_router)

app.include_router(service_order_approval_router)

app.include_router(metrics_router)
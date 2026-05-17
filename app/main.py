from fastapi import FastAPI

from app.api.routes.clients import router as clients_router
from app.api.routes.vehicles import router as vehicles_router
from app.api.routes.services import router as services_router
from app.api.routes.parts import router as parts_router
from app.api.routes.stock_movements import router as stock_router
from app.api.routes.service_orders import router as service_orders_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.service_order_approval import router as service_order_approval_router

app = FastAPI()

API_PREFIX = "/api"

app.include_router(
    service_order_approval_router,
    prefix=API_PREFIX
)

app.include_router(
    metrics_router,
    prefix=API_PREFIX
)

app.include_router(
    service_orders_router,
    prefix=API_PREFIX
)

app.include_router(
    stock_router,
    prefix=API_PREFIX
)

app.include_router(
    parts_router,
    prefix=API_PREFIX
)

app.include_router(
    services_router,
    prefix=API_PREFIX
)

app.include_router(
    vehicles_router,
    prefix=API_PREFIX
)

app.include_router(
    clients_router,
    prefix=API_PREFIX
)
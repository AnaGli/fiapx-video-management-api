from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.services.service_order_service import ServiceOrderService
from app.schemas.service_order import (
    ServiceOrderCreate,
    ServiceOrderItemCreate,
    ServiceOrderResponse,
    ServiceOrderPut,
    ServiceOrderStatusUpdate,
)

router = APIRouter(
    prefix="/service-orders",
    tags=["Service Orders"],
    dependencies=[Depends(get_current_user)],
)

def get_so_service(db: Session = Depends(get_db)):
    return ServiceOrderService(db)

@router.get("/", response_model=List[ServiceOrderResponse])
def list_service_orders(
    client_id: int | None = None,
    vehicle_id: int | None = None,
    status: str | None = None,
    service: ServiceOrderService = Depends(get_so_service),
):
    return service.list_all(client_id, vehicle_id, status)

@router.get("/{order_id}", response_model=ServiceOrderResponse)
def get_service_order(order_id: int, service: ServiceOrderService = Depends(get_so_service)):
    return service.get_by_id(order_id)

@router.post("/", response_model=ServiceOrderResponse, status_code=status.HTTP_201_CREATED)
def create_service_order(data: ServiceOrderCreate, service: ServiceOrderService = Depends(get_so_service)):
    return service.create(data)

@router.post("/{order_id}/items", response_model=ServiceOrderResponse)
def add_item_to_order(order_id: int, data: ServiceOrderItemCreate, service: ServiceOrderService = Depends(get_so_service)):
    return service.add_item(order_id, data)

@router.put("/{order_id}", response_model=ServiceOrderResponse)
def replace_service_order(order_id: int, data: ServiceOrderPut, service: ServiceOrderService = Depends(get_so_service)):
    return service.replace_order(order_id, data)

@router.put("/{order_id}/status", response_model=ServiceOrderResponse)
def update_service_order_status(order_id: int, data: ServiceOrderStatusUpdate, service: ServiceOrderService = Depends(get_so_service)):
    return service.update_status(order_id, data.status)

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_order(order_id: int, service: ServiceOrderService = Depends(get_so_service)):
    service.delete(order_id)
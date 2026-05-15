# app/routers/service_order_approval.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.services.service_order_approval_service import ServiceOrderApprovalService
from app.schemas.service_order import (
    ApproveServiceOrderRequest,
    ServiceOrderResponse,
)

router = APIRouter(
    prefix="/service-orders",
    tags=["Service Orders"],
)

def get_approval_service(db: Session = Depends(get_db)):
    return ServiceOrderApprovalService(db)

@router.post(
    "/{order_id}/approve",
    response_model=ServiceOrderResponse,
    status_code=status.HTTP_200_OK,
)
def approve_order(
    order_id: int,
    payload: ApproveServiceOrderRequest,
    service: ServiceOrderApprovalService = Depends(get_approval_service),
):
    return service.approve(order_id, payload.cpf)
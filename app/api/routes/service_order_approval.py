# app/routers/service_order_approval.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.services.service_order_approval_service import ServiceOrderApprovalService
from app.schemas.service_order import (
    ApproveServiceOrderRequest,
    ServiceOrderResponse,
)
from app.dependencies.auth import get_jws_cpf

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
    service: ServiceOrderApprovalService = Depends(get_approval_service),
    token_cpf: str = Depends(get_jws_cpf),
):
    return service.approve(order_id, token_cpf)
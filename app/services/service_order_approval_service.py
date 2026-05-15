from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories import service_order_repository as so_repo
from app.repositories import client_repository as client_repo
from app.models.service_order import ServiceOrderStatus

class ServiceOrderApprovalService:
    def __init__(self, db: Session):
        self.db = db

    def approve(self, order_id: int, cpf: str):
        client = client_repo.get_by_cpf(self.db, cpf)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        order = so_repo.get_by_id(self.db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Service order not found")

        if order.client_id != client.id:
            raise HTTPException(
                status_code=400, 
                detail="Order does not belong to client"
            )

        if order.status != ServiceOrderStatus.AGUARDANDO_APROVACAO:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot approve order in status {order.status}"
            )

        try:
            return so_repo.update_status(self.db, order, ServiceOrderStatus.EM_EXECUCAO)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
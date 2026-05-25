import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories import service_order_repository as repo
from app.models.service_order import ServiceOrder
from app.schemas.service_order import ServiceOrderCreate, ServiceOrderItemCreate, ServiceOrderPut
from app.core.logging_config import set_log_context

logger = logging.getLogger(__name__)

class ServiceOrderService:
    def __init__(self, db: Session):
        self.db = db

    def _get_order_or_404(self, order_id: int) -> ServiceOrder:
        order = self.db.query(ServiceOrder).filter(ServiceOrder.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Service order not found")
        return order

    def list_all(self, client_id=None, vehicle_id=None, order_status=None):
        return repo.list_orders(self.db, client_id, vehicle_id, order_status)

    def get_by_id(self, order_id: int):
        return self._get_order_or_404(order_id)

    def create(self, data: ServiceOrderCreate):
        try:
            order = repo.create_order(
                self.db,
                data.client_id,
                data.vehicle_id
            )

            set_log_context(
                service_order_id=order.id,
                business_operation="service_order_created"
            )

            logger.info(
                "Service order created successfully",
                extra={
                    "event_type": "service_order_created",
                    "business_status": "success",
                    "service_order_id": order.id,
                    "client_id": data.client_id,
                    "vehicle_id": data.vehicle_id,
                }
            )

            return order

        except Exception as exc:

            set_log_context(
                business_operation="service_order_created"
            )

            logger.exception(
                "Failed to create service order",
                extra={
                    "event_type": "service_order_created",
                    "business_status": "error",
                    "client_id": data.client_id,
                    "vehicle_id": data.vehicle_id,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
            )

            raise

    def add_item(self, order_id: int, data: ServiceOrderItemCreate):
        order = self._get_order_or_404(order_id)
        try:
            repo.add_item(self.db, order, data)
            self.db.refresh(order)
            return order
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def replace_order(self, order_id: int, data: ServiceOrderPut):
        order = self._get_order_or_404(order_id)
        try:
            return repo.replace_order(
                db=self.db,
                order=order,
                client_id=data.client_id,
                vehicle_id=data.vehicle_id,
                items=data.items,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def update_status(self, order_id: int, new_status: str):
        order = self._get_order_or_404(order_id)
        try:
            return repo.update_status(self.db, order, new_status)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def delete(self, order_id: int):
        order = self._get_order_or_404(order_id)
        repo.delete_order(self.db, order)
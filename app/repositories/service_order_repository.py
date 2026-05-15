import datetime
from sqlalchemy.orm import Session
from app.models.service_order import ServiceOrder, ServiceOrderStatus
from app.models.service_order_item import ServiceOrderItem
from app.models.stock_movement import StockMovement
from app.models.part import Part
from app.schemas.service_order import ServiceOrderItemCreate

def get_by_id(db: Session, order_id: int) -> ServiceOrder | None:
    return db.query(ServiceOrder).filter(ServiceOrder.id == order_id).first()

def list_orders(db: Session, client_id: int = None, vehicle_id: int = None, status: str = None):
    query = db.query(ServiceOrder)
    if client_id is not None:
        query = query.filter(ServiceOrder.client_id == client_id)
    if vehicle_id is not None:
        query = query.filter(ServiceOrder.vehicle_id == vehicle_id)
    if status is not None:
        query = query.filter(ServiceOrder.status == status)
    return query.order_by(ServiceOrder.created_at.desc()).all()

def create_order(db: Session, client_id: int, vehicle_id: int):
    order = ServiceOrder(
        client_id=client_id,
        vehicle_id=vehicle_id,
        status=ServiceOrderStatus.RECEBIDA,
        total_amount=0,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def update_status(db: Session, order: ServiceOrder, new_status: ServiceOrderStatus):
    current_status = order.status
    now = datetime.datetime.utcnow()

    if current_status != ServiceOrderStatus.EM_EXECUCAO and new_status == ServiceOrderStatus.EM_EXECUCAO:
        if order.execution_started_at is None:
            order.execution_started_at = now

    if current_status == ServiceOrderStatus.EM_EXECUCAO and new_status == ServiceOrderStatus.FINALIZADA:
        if order.execution_finished_at is None:
            order.execution_finished_at = now

    if current_status == ServiceOrderStatus.AGUARDANDO_APROVACAO and new_status == ServiceOrderStatus.EM_EXECUCAO:
        for item in order.items:
            if item.item_type == "PART":
                part = db.query(Part).filter(Part.id == item.item_id).with_for_update().first()
                if not part or part.quantity < item.quantity:
                    raise ValueError(f"Insufficient stock for part: {part.name if part else item.item_id}")
                
                part.quantity -= item.quantity
                db.add(StockMovement(
                    part_id=part.id,
                    movement_type="OUT",
                    quantity=item.quantity,
                    reference=f"OS:{order.id}"
                ))

    order.status = new_status
    db.commit()
    db.refresh(order)
    return order

def recalculate_total(db: Session, order: ServiceOrder):
    total = sum(item.quantity * item.price for item in order.items)
    order.total_amount = total
    db.commit()

def delete_order(db: Session, order: ServiceOrder):
    db.delete(order)
    db.commit()

def replace_order(self, order_id: int, order_data: ServiceOrder) -> ServiceOrder | None:
       
    db_order = self.db.query(ServiceOrder).filter(ServiceOrder.id == order_id).first()
    
    if db_order:
        update_data = order_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_order, key, value)
        
        self.db.commit()
        self.db.refresh(db_order)
        return db_order
    return None

def add_item(self, order_id: int, item_data: ServiceOrderItemCreate) -> ServiceOrderItem | None:

    db_order = self.db.query(ServiceOrder).filter(ServiceOrder.id == order_id).first()
    
    if not db_order:
        return None

    db_item = ServiceOrderItem(
        **item_data.model_dump(),
        service_order_id=order_id
    )
    
    self.db.add(db_item)
    self.db.commit()
    self.db.refresh(db_item)
    return db_item
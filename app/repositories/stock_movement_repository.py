from sqlalchemy.orm import Session
from app.models.part import Part
from app.models.stock_movement import StockMovement
from app.schemas.stock_movement import StockMovementCreate

def create_movement(db: Session, part: Part, data: StockMovementCreate, new_quantity: int):
    movement = StockMovement(
        part_id=part.id,
        movement_type=data.movement_type,
        quantity=data.quantity,
        reference=data.reference,
    )

    part.quantity = new_quantity
    db.add(movement)
    db.commit()
    db.refresh(part)
    return part
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories import part_repository
from app.repositories import stock_movement_repository as repo
from app.schemas.stock_movement import StockMovementCreate

class StockService:
    def __init__(self, db: Session):
        self.db = db

    def move_stock(self, part_id: int, data: StockMovementCreate):
        part = part_repository.get_by_id(self.db, part_id)
        if not part:
            raise HTTPException(status_code=404, detail="Part not found")

        if data.movement_type == "OUT" and part.quantity < data.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock. Available: {part.quantity}"
            )

        if data.movement_type == "IN":
            new_quantity = part.quantity + data.quantity
        elif data.movement_type == "OUT":
            new_quantity = part.quantity - data.quantity
        else: # ADJUST
            new_quantity = data.quantity

        return repo.create_movement(self.db, part, data, new_quantity)
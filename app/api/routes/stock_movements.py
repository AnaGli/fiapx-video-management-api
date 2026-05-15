from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.schemas.stock_movement import StockMovementCreate
from app.schemas.part import PartResponse
from app.services.stock_service import StockService

router = APIRouter(
    prefix="/parts/{part_id}/stock",
    tags=["Stock"],
    dependencies=[Depends(get_current_user)],
)

def get_stock_service(db: Session = Depends(get_db)):
    return StockService(db)

@router.post("/", response_model=PartResponse)
def move_stock(
    part_id: int,
    data: StockMovementCreate,
    service: StockService = Depends(get_stock_service),
):
    return service.move_stock(part_id, data)
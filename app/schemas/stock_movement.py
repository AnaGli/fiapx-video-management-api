from pydantic import BaseModel, Field, field_validator
from typing import Literal

MovementType = Literal["IN", "OUT", "ADJUST"]

class StockMovementCreate(BaseModel):
    movement_type: MovementType
    quantity: float = Field(..., gt=0)
    reference: str | None = None

    @field_validator("movement_type")
    @classmethod
    def normalize_type(cls, value: str) -> str:
        return value.upper()

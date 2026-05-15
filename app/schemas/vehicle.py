from pydantic import BaseModel, field_validator
from app.core.validators import validate_and_normalize_plate

class VehicleBase(BaseModel):
    plate: str
    brand: str
    model: str
    year: int

    @field_validator("plate")
    @classmethod
    def normalize_plate(cls, value: str) -> str:
        return value.upper().replace("-", "").strip()


class VehicleCreate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: int

    class Config:
        from_attributes = True

class VehicleUpdate(BaseModel):
    plate: str | None = None
    brand: str | None = None
    model: str | None = None
    year: int | None = None

    @field_validator("plate")
    @classmethod
    def validate_plate(cls, value: str) -> str:
        return validate_and_normalize_plate(value)
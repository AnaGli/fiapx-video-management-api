from pydantic import BaseModel, Field

class PartBase(BaseModel):
    name: str
    description: str | None = None
    unit: str
    price: float = Field(..., gt=0)


class PartCreate(PartBase):
    quantity: float = Field(..., ge=0)


class PartUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    unit: str | None = None
    price: float | None = Field(None, gt=0)
    active: bool | None = None


class PartResponse(BaseModel):
    id: int
    name: str
    description: str | None
    unit: str
    quantity: float
    price: float
    active: bool

    class Config:
        from_attributes = True

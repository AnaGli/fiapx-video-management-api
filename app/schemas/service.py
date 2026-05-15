from pydantic import BaseModel, Field

class ServiceCreate(BaseModel):
    name: str
    description: str | None = None
    price: float = Field(..., gt=0)


class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(None, gt=0)


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float

    class Config:
        from_attributes = True

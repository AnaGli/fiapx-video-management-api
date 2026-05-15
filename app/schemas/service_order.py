from pydantic import BaseModel, Field, field_validator
from typing import Literal
from app.core.validators import validate_and_normalize_cpf_cnpj
from app.models.service_order import ServiceOrderStatus

ItemType = Literal["SERVICE", "PART"]


class ServiceOrderCreate(BaseModel):
    client_id: int
    vehicle_id: int


class ServiceOrderItemCreate(BaseModel):
    item_type: ItemType
    item_id: int
    quantity: float = Field(..., gt=0)


class ServiceOrderItemResponse(BaseModel):
    id: int
    item_type: ItemType
    item_id: int
    description: str
    quantity: float
    price: float

    class Config:
        from_attributes = True


class ServiceOrderResponse(BaseModel):
    id: int
    client_id: int
    vehicle_id: int
    status: ServiceOrderStatus
    total_amount: float
    items: list[ServiceOrderItemResponse]

    class Config:
        from_attributes = True

class ServiceOrderItemPut(BaseModel):
    item_type: Literal["SERVICE", "PART"]
    item_id: int
    quantity: float = Field(..., gt=0)


class ServiceOrderPut(BaseModel):
    client_id: int
    vehicle_id: int
    items: list[ServiceOrderItemPut]

class ServiceOrderStatusUpdate(BaseModel):
    status: ServiceOrderStatus

class ApproveServiceOrderRequest(BaseModel):
    cpf: str

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        # reaproveita a validação já existente
        cpf_normalized = validate_and_normalize_cpf_cnpj(value)

        if len(cpf_normalized) != 11:
            raise ValueError("CPF inválido")

        return cpf_normalized
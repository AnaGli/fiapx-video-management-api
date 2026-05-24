from pydantic import BaseModel, field_validator

from app.core.validators import validate_and_normalize_cpf_cnpj

class ClientBase(BaseModel):
    name: str
    cpf: str
    email: str

    @field_validator("cpf")
    @classmethod
    def validate_cpf_cnpj(cls, value: str) -> str:
        return validate_and_normalize_cpf_cnpj(value)


class ClientCreate(ClientBase):
    is_active: bool = True


class ClientUpdate(BaseModel):
    name: str | None = None
    cpf: str | None = None
    email: str | None = None
    is_active: bool | None = None


class ClientResponse(ClientBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

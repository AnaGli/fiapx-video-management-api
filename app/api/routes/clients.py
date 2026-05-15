from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.services.client_service import ClientService
router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
    dependencies=[Depends(get_current_user)],
)

def get_client_service(db: Session = Depends(get_db)):
    return ClientService(db)

@router.get("/", response_model=list[ClientResponse])
def list_clients(service: ClientService = Depends(get_client_service)):
    return service.list_all()

@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, service: ClientService = Depends(get_client_service)):
    return service.get_by_id(client_id)

@router.get("/cpf/{cpf}", response_model=ClientResponse)
def get_client_by_cpf(cpf: str, service: ClientService = Depends(get_client_service)):
    return service.get_by_cpf(cpf)

@router.post("/", response_model=ClientResponse, status_code=201)
def create_client(data: ClientCreate, service: ClientService = Depends(get_client_service)):
    return service.create(data)

@router.put("/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, data: ClientUpdate, service: ClientService = Depends(get_client_service)):
    return service.update(client_id, data)

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, service: ClientService = Depends(get_client_service)):
    service.delete(client_id)
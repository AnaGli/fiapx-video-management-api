from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.schemas.part import PartCreate, PartUpdate, PartResponse
from app.services.part_service import PartService

router = APIRouter(
    prefix="/parts",
    tags=["Parts"],
    # Centralizado aqui: todas as rotas abaixo exigem login
    dependencies=[Depends(get_current_user)], 
)

def get_part_service(db: Session = Depends(get_db)):
    return PartService(db)

@router.get("/", response_model=list[PartResponse])
def list_parts(service: PartService = Depends(get_part_service)):
    return service.list_all()

@router.get("/{part_id}", response_model=PartResponse)
def get_part(part_id: int, service: PartService = Depends(get_part_service)):
    return service.get_by_id(part_id)

@router.post("/", response_model=PartResponse, status_code=status.HTTP_201_CREATED)
def create_part(data: PartCreate, service: PartService = Depends(get_part_service)):
    return service.create(data)

@router.put("/{part_id}", response_model=PartResponse)
def update_part(part_id: int, data: PartUpdate, service: PartService = Depends(get_part_service)):
    return service.update(part_id, data)

@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_part(part_id: int, service: PartService = Depends(get_part_service)):
    service.delete(part_id)
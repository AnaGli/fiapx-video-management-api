# app/routers/services.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.services.service_catalog_service import ServiceService

router = APIRouter(
    prefix="/services",
    tags=["Services"],
    dependencies=[Depends(get_current_user)],
)

def get_service_manager(db: Session = Depends(get_db)):
    return ServiceService(db)

@router.get("/", response_model=list[ServiceResponse])
def list_services(service_manager: ServiceService = Depends(get_service_manager)):
    return service_manager.list_all()

@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, service_manager: ServiceService = Depends(get_service_manager)):
    return service_manager.get_by_id(service_id)

@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(data: ServiceCreate, service_manager: ServiceService = Depends(get_service_manager)):
    return service_manager.create(data)

@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(service_id: int, data: ServiceUpdate, service_manager: ServiceService = Depends(get_service_manager)):
    return service_manager.update(service_id, data)

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(service_id: int, service_manager: ServiceService = Depends(get_service_manager)):
    service_manager.delete(service_id)
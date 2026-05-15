from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories import service_repository as repo
from app.schemas.service import ServiceCreate, ServiceUpdate

class ServiceService:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self):
        return repo.get_all(self.db)

    def get_by_id(self, service_id: int):
        service = repo.get_by_id(self.db, service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        return service

    def create(self, data: ServiceCreate):
        if repo.get_by_name(self.db, data.name):
            raise HTTPException(
                status_code=400,
                detail="Service with this name already exists",
            )
        return repo.create(self.db, data)

    def update(self, service_id: int, data: ServiceUpdate):
        service = self.get_by_id(service_id)
        
        if data.name:
            existing = repo.get_by_name(self.db, data.name)
            if existing and existing.id != service_id:
                raise HTTPException(
                    status_code=400,
                    detail="Service with this name already exists",
                )
        
        return repo.update(self.db, service, data)

    def delete(self, service_id: int):
        service = self.get_by_id(service_id)
        repo.delete(self.db, service)
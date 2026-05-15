# app/services/part_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories import part_repository as repo
from app.schemas.part import PartCreate, PartUpdate

class PartService:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self):
        return repo.get_all(self.db)

    def get_by_id(self, part_id: int):
        part = repo.get_by_id(self.db, part_id)
        if not part:
            raise HTTPException(status_code=404, detail="Part not found")
        return part

    def create(self, data: PartCreate):
        if repo.get_by_name(self.db, data.name):
            raise HTTPException(
                status_code=400,
                detail="Part with this name already exists",
            )
        return repo.create(self.db, data)

    def update(self, part_id: int, data: PartUpdate):
        part = self.get_by_id(part_id)  
        
        if data.name:
            existing = repo.get_by_name(self.db, data.name)
            if existing and existing.id != part_id:
                raise HTTPException(status_code=400, detail="Another part already has this name")
                
        return repo.update(self.db, part, data)

    def delete(self, part_id: int):
        part = self.get_by_id(part_id)
        repo.delete(self.db, part)
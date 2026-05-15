from sqlalchemy.orm import Session
from app.repositories import client_repository as repo
from app.schemas.client import ClientCreate, ClientUpdate
from fastapi import HTTPException

class ClientService:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self):
        return repo.get_all(self.db)

    def get_by_id(self, client_id: int):
        client = repo.get_by_id(self.db, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client

    def get_by_cpf(self, cpf: str):
        client = repo.get_by_cpf(self.db, cpf)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client

    def create(self, data: ClientCreate):
        if repo.get_by_cpf(self.db, data.cpf):
            raise HTTPException(status_code=400, detail="Client with this CPF already exists")
        return repo.create(self.db, data)

    def update(self, client_id: int, data: ClientUpdate):
        client = self.get_by_id(client_id)
        return repo.update(self.db, client, data)

    def delete(self, client_id: int):
        client = self.get_by_id(client_id)
        repo.delete(self.db, client)
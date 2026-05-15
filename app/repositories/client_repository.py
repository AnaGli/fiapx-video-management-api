from sqlalchemy.orm import Session
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate

def get_all(db: Session):
    return db.query(Client).all()

def get_by_id(db: Session, client_id: int):
    return db.query(Client).filter(Client.id == client_id).first()

def get_by_cpf(db: Session, cpf: str):
    return db.query(Client).filter(Client.cpf == cpf).first()

def create(db: Session, data: ClientCreate):
    client = Client(**data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

def update(db: Session, client: Client, data: ClientUpdate):
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    return client

def delete(db: Session, client: Client):
    db.delete(client)
    db.commit()
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.client import Client
from app.repositories import client_repository as repo
from app.schemas.client import ClientCreate, ClientUpdate
from app.database import Base

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_create_client(db_session):
    data = ClientCreate(name="João Silva", cpf="86440020072", email="joao@email.com")
    client = repo.create(db_session, data)
    assert client.id is not None
    assert client.cpf == "86440020072"

def test_get_client_by_cpf(db_session):
    data = ClientCreate(name="Maria Souza", cpf="98765432100", email="maria@email.com")
    repo.create(db_session, data)
    client = repo.get_by_cpf(db_session, "98765432100")
    assert client is not None
    assert client.name == "Maria Souza"
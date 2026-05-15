import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.part import Part
from app.repositories import part_repository as repo
from app.schemas.part import PartCreate, PartUpdate
from app.database import Base

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_create_part(db_session):
    data = PartCreate(name="Pastilha de Freio", price=150.0, quantity=20, unit="1")
    part = repo.create(db_session, data)
    assert part.id is not None
    assert part.name == "Pastilha de Freio"
    assert part.quantity == 20

def test_get_part_by_id(db_session):
    data = PartCreate(name="Amortecedor", price=450.0, quantity=4, unit="1")
    created_part = repo.create(db_session, data)
    
    part = repo.get_by_id(db_session, created_part.id)
    assert part is not None
    assert part.name == "Amortecedor"


def test_delete_part(db_session):
    data = PartCreate(name="Filtro", price=30.0, quantity=5, unit="1")
    part = repo.create(db_session, data)
    
    repo.delete(db_session, part)
    deleted_part = repo.get_by_id(db_session, part.id)
    assert deleted_part is None
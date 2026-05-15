import sys
import os
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.client import Client
from app.models.vehicle import Vehicle
from app.models.part import Part
from app.models.service import Service



# 🔹 Garante que /app esteja no PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# 🔹 Cria e remove o schema UMA VEZ por sessão de testes
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# 🔹 Sessão de banco por teste
@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    def override_get_current_user():
        return {"id": 1, "email": "test@test.com"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def vehicle(db_session):
    vehicle = Vehicle(plate="ABC1234", model="Car")
    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)
    return vehicle


@pytest.fixture
def service(db_session):
    service = Service(name="Troca de óleo", price=100)
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)
    return service


@pytest.fixture
def part(db_session):
    part = Part(name="Filtro", price=50, quantity=10)
    db_session.add(part)
    db_session.commit()
    db_session.refresh(part)
    return part

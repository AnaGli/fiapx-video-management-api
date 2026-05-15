import pytest
from app.repositories import service_order_repository as repo
from app.models.service_order import ServiceOrderStatus
from app.models.client import Client
from app.models.vehicle import Vehicle

def test_create_service_order(db_session):
    # Setup: Precisa de um cliente e veículo existentes
    client = Client(name="Test", cpf="1", email="t@t.com")
    db_session.add(client)
    db_session.commit()
    
    order = repo.create_order(db_session, client_id=client.id, vehicle_id=1)
    assert order.status == ServiceOrderStatus.RECEBIDA
    assert order.total_amount == 0

def test_update_order_status(db_session):
    order = repo.create_order(db_session, client_id=1, vehicle_id=1)
    updated_order = repo.update_status(db_session, order, ServiceOrderStatus.AGUARDANDO_APROVACAO)
    assert updated_order.status == ServiceOrderStatus.AGUARDANDO_APROVACAO
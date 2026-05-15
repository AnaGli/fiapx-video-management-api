import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from pydantic import ValidationError
from app.services.client_service import ClientService
from app.schemas.client import ClientCreate, ClientUpdate


@pytest.fixture
def db_mock():
    return MagicMock()


@pytest.fixture
def service(db_mock):
    return ClientService(db_mock)


# ---------------------------
# list_all
# ---------------------------
@patch("app.services.client_service.repo.get_all")
def test_list_all(mock_get_all, service, db_mock):
    mock_get_all.return_value = ["client1", "client2"]

    result = service.list_all()

    mock_get_all.assert_called_once_with(db_mock)
    assert result == ["client1", "client2"]


# ---------------------------
# get_by_id
# ---------------------------
@patch("app.services.client_service.repo.get_by_id")
def test_get_by_id_success(mock_get_by_id, service, db_mock):
    mock_get_by_id.return_value = {"id": 1}

    result = service.get_by_id(1)

    assert result["id"] == 1


@patch("app.services.client_service.repo.get_by_id")
def test_get_by_id_not_found(mock_get_by_id, service, db_mock):
    mock_get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_by_id(1)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Client not found"


# ---------------------------
# get_by_cpf
# ---------------------------
@patch("app.services.client_service.repo.get_by_cpf")
def test_get_by_cpf_success(mock_get_by_cpf, service, db_mock):
    mock_get_by_cpf.return_value = {"cpf": "88646715019"}

    result = service.get_by_cpf("88646715019")

    assert result["cpf"] == "88646715019"


@patch("app.services.client_service.repo.get_by_cpf")
def test_get_by_cpf_not_found(mock_get_by_cpf, service, db_mock):
    mock_get_by_cpf.return_value = None

    with pytest.raises(HTTPException):
        service.get_by_cpf("88646715019")


# ---------------------------
# create
# ---------------------------
@patch("app.services.client_service.repo.create")
@patch("app.services.client_service.repo.get_by_cpf")
def test_create_success(mock_get_by_cpf, mock_create, service, db_mock):
    mock_get_by_cpf.return_value = None
    mock_create.return_value = {"id": 1}

    data = ClientCreate(name="Ana", email="test@test.com", cpf="88646715019")

    result = service.create(data)

    mock_create.assert_called_once_with(db_mock, data)
    assert result["id"] == 1


@patch("app.services.client_service.repo.get_by_cpf")
def test_create_duplicate_cpf(mock_get_by_cpf, service, db_mock):
    mock_get_by_cpf.return_value = {"cpf": "88646715019"}

    data = ClientCreate(name="Ana", email="test@test.com", cpf="88646715019")

    with pytest.raises(HTTPException) as exc:
        service.create(data)

    assert exc.value.status_code == 400


# ---------------------------
# update
# ---------------------------
@patch("app.services.client_service.repo.update")
@patch("app.services.client_service.repo.get_by_id")
def test_update_success(mock_get_by_id, mock_update, service, db_mock):
    mock_get_by_id.return_value = {"id": 1}
    mock_update.return_value = {"id": 1, "name": "Updated"}

    data = ClientUpdate(name="Updated")

    result = service.update(1, data)

    assert result["name"] == "Updated"


# ---------------------------
# delete
# ---------------------------
@patch("app.services.client_service.repo.delete")
@patch("app.services.client_service.repo.get_by_id")
def test_delete_success(mock_get_by_id, mock_delete, service, db_mock):
    mock_get_by_id.return_value = {"id": 1}

    service.delete(1)

    mock_delete.assert_called_once()

def test_create_invalid_cpf_should_fail():
    with pytest.raises(ValidationError) as exc:
        ClientCreate(
            name="Ana",
            cpf="123",  # inválido
            email="ana@email.com"
        )

    errors = exc.value.errors()

    assert any("CPF/CNPJ deve ter 11 ou 14 dígitos" in err["msg"] for err in errors)
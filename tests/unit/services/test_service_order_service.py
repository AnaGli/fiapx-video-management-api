import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from app.services.service_order_service import ServiceOrderService


# ---------------------------
# Fixtures
# ---------------------------
@pytest.fixture
def db_mock():
    return MagicMock()


@pytest.fixture
def service(db_mock):
    return ServiceOrderService(db_mock)


@pytest.fixture
def order_mock():
    order = MagicMock()
    order.id = 1
    return order


# ---------------------------
# _get_order_or_404
# ---------------------------
def test_get_order_or_404_success(service, db_mock, order_mock):
    db_mock.query().filter().first.return_value = order_mock

    result = service._get_order_or_404(1)

    assert result == order_mock


def test_get_order_or_404_not_found(service, db_mock):
    db_mock.query().filter().first.return_value = None

    with pytest.raises(HTTPException) as exc:
        service._get_order_or_404(1)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Service order not found"


# ---------------------------
# list_all
# ---------------------------
@patch("app.services.service_order_service.repo.list_orders")
def test_list_all(mock_list_orders, service, db_mock):
    mock_list_orders.return_value = ["order1"]

    result = service.list_all(client_id=1)

    mock_list_orders.assert_called_once_with(db_mock, 1, None, None)
    assert result == ["order1"]


# ---------------------------
# get_by_id
# ---------------------------
def test_get_by_id(service, db_mock, order_mock):
    db_mock.query().filter().first.return_value = order_mock

    result = service.get_by_id(1)

    assert result == order_mock


# ---------------------------
# create
# ---------------------------
@patch("app.services.service_order_service.repo.create_order")
def test_create(mock_create, service, db_mock):
    data = MagicMock()
    data.client_id = 1
    data.vehicle_id = 2

    mock_create.return_value = {"id": 1}

    result = service.create(data)

    mock_create.assert_called_once_with(db_mock, 1, 2)
    assert result["id"] == 1


# ---------------------------
# add_item
# ---------------------------
@patch("app.services.service_order_service.repo.add_item")
def test_add_item_success(mock_add_item, service, db_mock, order_mock):
    db_mock.query().filter().first.return_value = order_mock

    data = MagicMock()

    result = service.add_item(1, data)

    mock_add_item.assert_called_once()
    db_mock.refresh.assert_called_once_with(order_mock)
    assert result == order_mock


@patch("app.services.service_order_service.repo.add_item")
def test_add_item_value_error(mock_add_item, service, db_mock, order_mock):
    db_mock.query().filter().first.return_value = order_mock
    mock_add_item.side_effect = ValueError("Invalid item")

    data = MagicMock()

    with pytest.raises(HTTPException) as exc:
        service.add_item(1, data)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid item"


# ---------------------------
# replace_order
# ---------------------------
@patch("app.services.service_order_service.repo.replace_order")
def test_replace_order_success(mock_replace, service, db_mock, order_mock):
    db_mock.query().filter().first.return_value = order_mock

    data = MagicMock()
    data.client_id = 1
    data.vehicle_id = 2
    data.items = []

    mock_replace.return_value = {"id": 1}

    result = service.replace_order(1, data)

    assert result["id"] == 1


@patch("app.services.service_order_service.repo.replace_order")
def test_replace_order_value_error(mock_replace, service, db_mock, order_mock):
    db_mock.query().filter().first.return_value = order_mock
    mock_replace.side_effect = ValueError("Invalid replace")

    data = MagicMock()

    with pytest.raises(HTTPException) as exc:
        service.replace_order(1, data)

    assert exc.value.status_code == 400


# ---------------------------
# update_status
# ---------------------------
@patch("app.services.service_order_service.repo.update_status")
def test_update_status_success(mock_update_status, service, db_mock, order_mock):
    db_mock.query().filter().first.return_value = order_mock

    mock_update_status.return_value = {"status": "DONE"}

    result = service.update_status(1, "DONE")

    assert result["status"] == "DONE"


@patch("app.services.service_order_service.repo.update_status")
def test_update_status_value_error(mock_update_status, service, db_mock, order_mock):
    db_mock.query().filter().first.return_value = order_mock
    mock_update_status.side_effect = ValueError("Invalid status")

    with pytest.raises(HTTPException) as exc:
        service.update_status(1, "INVALID")

    assert exc.value.status_code == 400


# ---------------------------
# delete
# ---------------------------
@patch("app.services.service_order_service.repo.delete_order")
def test_delete_success(mock_delete, service, db_mock, order_mock):
    db_mock.query().filter().first.return_value = order_mock

    service.delete(1)

    mock_delete.assert_called_once_with(db_mock, order_mock)
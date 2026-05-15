import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace

from app.repositories.service_repository import (
    get_all,
    get_by_id,
    get_by_name,
    create,
    update,
    delete,
)


# -------------------------
# Helpers
# -------------------------

def make_db():
    return MagicMock()


def make_service(id=1, name="Troca de óleo", price=100):
    return SimpleNamespace(
        id=id,
        name=name,
        price=price,
    )


class FakeServiceCreate:
    def __init__(self, **kwargs):
        self._data = kwargs

    def model_dump(self):
        return self._data


class FakeServiceUpdate:
    def __init__(self, **kwargs):
        self._data = kwargs

    def model_dump(self, exclude_unset=False):
        return self._data


# -------------------------
# Tests: GETs
# -------------------------

def test_get_all_services():
    db = make_db()
    expected = ["service1", "service2"]

    db.query().all.return_value = expected

    result = get_all(db)

    assert result == expected


def test_get_service_by_id():
    db = make_db()
    service = make_service()

    db.query().filter().first.return_value = service

    result = get_by_id(db, service_id=1)

    assert result == service


def test_get_service_by_name():
    db = make_db()
    service = make_service(name="Troca de óleo")

    db.query().filter().first.return_value = service

    result = get_by_name(db, name="Troca de óleo")

    assert result == service


# -------------------------
# Tests: CREATE
# -------------------------

def test_create_service():
    db = make_db()

    data = FakeServiceCreate(
        name="Alinhamento",
        price=150,
    )

    service = create(db, data)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(service)


# -------------------------
# Tests: UPDATE
# -------------------------

def test_update_service_partial_fields():
    db = make_db()
    service = make_service(price=100)

    data = FakeServiceUpdate(price=120)

    updated = update(db, service, data)

    assert updated.price == 120
    assert updated.name == "Troca de óleo"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(service)


def test_update_service_multiple_fields():
    db = make_db()
    service = make_service(price=100, name="Troca de óleo")

    data = FakeServiceUpdate(
        name="Balanceamento",
        price=180,
    )

    updated = update(db, service, data)

    assert updated.name == "Balanceamento"
    assert updated.price == 180


# -------------------------
# Tests: DELETE
# -------------------------

def test_delete_service():
    db = make_db()
    service = make_service()

    delete(db, service)

    db.delete.assert_called_once_with(service)
    db.commit.assert_called_once()

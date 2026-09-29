from unittest.mock import Mock
from uuid import uuid4

from app.repositories.user_repository import UserRepository


def test_create():
    db = Mock()
    repository = UserRepository(db)
    user = Mock()

    result = repository.create(user)

    assert result == user
    db.add.assert_called_once_with(user)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(user)


def test_find_by_id():
    db = Mock()
    repository = UserRepository(db)

    user_id = uuid4()
    user = Mock()
    db.scalar.return_value = user

    result = repository.find_by_id(user_id)

    assert result == user
    db.scalar.assert_called_once()


def test_find_by_username():
    db = Mock()
    repository = UserRepository(db)

    user = Mock()
    db.scalar.return_value = user

    result = repository.find_by_username("john")

    assert result == user
    db.scalar.assert_called_once()


def test_find_by_email():
    db = Mock()
    repository = UserRepository(db)

    user = Mock()
    db.scalar.return_value = user

    result = repository.find_by_email("john@example.com")

    assert result == user
    db.scalar.assert_called_once()

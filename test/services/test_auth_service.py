from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from app.services.auth_service import AuthService


def test_register_success():
    db = Mock()
    service = AuthService(db)

    data = SimpleNamespace(
        username="john",
        email="john@example.com",
        password="secret",
    )

    created_user = Mock()

    with patch("app.services.auth_service.hash_password", return_value="hashed") as hash_password:
        service.user_repository.find_by_username = Mock(return_value=None)
        service.user_repository.find_by_email = Mock(return_value=None)
        service.user_repository.create = Mock(return_value=created_user)

        result = service.register(data)

    assert result == created_user
    hash_password.assert_called_once_with("secret")
    service.user_repository.create.assert_called_once()

    user = service.user_repository.create.call_args.args[0]
    assert user.username == "john"
    assert user.email == "john@example.com"
    assert user.password_hash == "hashed"


def test_register_rejects_existing_username():
    db = Mock()
    service = AuthService(db)

    data = SimpleNamespace(
        username="john",
        email="john@example.com",
        password="secret",
    )

    service.user_repository.find_by_username = Mock(return_value=Mock())

    with pytest.raises(ValueError, match="Username already exists"):
        service.register(data)


def test_register_rejects_existing_email():
    db = Mock()
    service = AuthService(db)

    data = SimpleNamespace(
        username="john",
        email="john@example.com",
        password="secret",
    )

    service.user_repository.find_by_username = Mock(return_value=None)
    service.user_repository.find_by_email = Mock(return_value=Mock())

    with pytest.raises(ValueError, match="Email already exists"):
        service.register(data)


def test_login_success():
    db = Mock()
    service = AuthService(db)

    user = Mock()
    user.id = uuid4()
    user.password_hash = "hashed"

    service.user_repository.find_by_username = Mock(return_value=user)

    with patch("app.services.auth_service.verify_password", return_value=True),          patch("app.services.auth_service.create_access_token", return_value="token") as create_token:
        result = service.login("john", "secret")

    assert result == "token"
    create_token.assert_called_once_with(str(user.id))


def test_login_rejects_unknown_user():
    db = Mock()
    service = AuthService(db)
    service.user_repository.find_by_username = Mock(return_value=None)

    with pytest.raises(ValueError, match="Invalid username or password"):
        service.login("john", "secret")


def test_login_rejects_invalid_password():
    db = Mock()
    service = AuthService(db)

    user = Mock()
    user.password_hash = "hashed"
    service.user_repository.find_by_username = Mock(return_value=user)

    with patch("app.services.auth_service.verify_password", return_value=False):
        with pytest.raises(ValueError, match="Invalid username or password"):
            service.login("john", "wrong")

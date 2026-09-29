from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.api.routes.auth import login, register
from app.schemas.auth import LoginRequest, UserCreate


def test_register_success():
    db = Mock()
    data = UserCreate(username="john", email="john@example.com", password="secret")
    user = Mock()

    with patch("app.api.routes.auth.AuthService") as service_class:
        service_class.return_value.register.return_value = user
        result = register(data=data, db=db)

    assert result == user
    service_class.return_value.register.assert_called_once_with(data)


def test_register_value_error():
    db = Mock()
    data = UserCreate(username="john", email="john@example.com", password="secret")

    with patch("app.api.routes.auth.AuthService") as service_class:
        service_class.return_value.register.side_effect = ValueError("Username already exists")
        with pytest.raises(HTTPException) as exc:
            register(data=data, db=db)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Username already exists"


def test_login_success():
    db = Mock()
    data = LoginRequest(username="john", password="secret")

    with patch("app.api.routes.auth.AuthService") as service_class:
        service_class.return_value.login.return_value = "jwt-token"
        result = login(data=data, db=db)

    assert result.access_token == "jwt-token"
    service_class.return_value.login.assert_called_once_with(username="john", password="secret")


def test_login_value_error():
    db = Mock()
    data = LoginRequest(username="john", password="wrong")

    with patch("app.api.routes.auth.AuthService") as service_class:
        service_class.return_value.login.side_effect = ValueError("Invalid username or password")
        with pytest.raises(HTTPException) as exc:
            login(data=data, db=db)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid username or password"

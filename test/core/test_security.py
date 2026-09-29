from unittest.mock import patch

from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password():
    password = "secret123"

    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$2")
    assert verify_password(password, hashed)


def test_verify_password_returns_false_for_wrong_password():
    hashed = hash_password("secret123")

    assert verify_password("wrong-password", hashed) is False


def test_create_access_token():
    user_id = "user-123"

    token = create_access_token(user_id)

    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )

    assert payload["sub"] == user_id
    assert "exp" in payload


def test_decode_access_token():
    user_id = "user-123"

    token = create_access_token(user_id)

    result = decode_access_token(token)

    assert result == user_id


def test_decode_access_token_returns_none_for_invalid_token():
    result = decode_access_token("invalid-token")

    assert result is None


def test_decode_access_token_returns_none_when_sub_is_missing():
    token = jwt.encode(
        {"exp": 9999999999},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    result = decode_access_token(token)

    assert result is None

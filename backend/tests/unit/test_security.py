from datetime import timedelta

import pytest

from app.core.exceptions import AuthenticationException
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing_and_verification():
    password = "MySecurePassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2") or hashed.startswith("$2b$")
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_create_and_decode_access_token():
    user_id = 42
    token = create_access_token(subject=user_id)
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_decode_expired_token():
    token = create_access_token(subject=10, expires_delta=timedelta(seconds=-10))
    with pytest.raises(AuthenticationException) as exc_info:
        decode_access_token(token)
    assert "expired" in exc_info.value.message.lower()


def test_decode_malformed_token():
    with pytest.raises(AuthenticationException):
        decode_access_token("this.is.not.a.valid.jwt")


def test_decode_invalid_signature():
    token = create_access_token(subject=10)
    tampered_token = token[:-5] + "aaaaa"
    with pytest.raises(AuthenticationException):
        decode_access_token(tampered_token)

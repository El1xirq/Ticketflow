import pytest
import jwt

from uuid import uuid4
from datetime import datetime, timezone, timedelta

from app.core.security import (
    get_password_hash,
    create_access_token,
    decode_token,
    verify_password,
    verify_token,
    create_refresh_token,
    hash_refresh_token,
)
from app.db.models.user_role import UserRole
from app.core.exceptions.domain import InvalidTokenException
from app.core.config import settings


def test_hash_password_not_plain():
    password = 'secret123'
    password_hash = get_password_hash(password)
    assert password != password_hash
    assert len(password_hash) > 20


def test_verify_password_correct():
    password = "secret123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    password = "secret123"
    hashed = get_password_hash(password)
    assert verify_password("wrong", hashed) is False


def test_create_access_token_returns_string():
    token = create_access_token(uuid4(), list(UserRole.CUSTOMER.value), "test@test.com")
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_payload():
    user_id = uuid4()

    access_token = create_access_token(user_id, list(UserRole.CUSTOMER.value), 'test@test.com')
    body = decode_token(access_token)

    assert body['sub'] == str(user_id)
    assert body['roles'] == list(UserRole.CUSTOMER.value)
    assert body['email'] == "test@test.com"
    assert body['type'] == 'access'
    assert 'exp' in body




def test_verify_access_token_ok():
    user_id = uuid4()
    token = create_access_token(user_id, list(UserRole.CUSTOMER.value), "test@test.com")

    payload = verify_token(token, "access")

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"


def test_create_refresh_token_returns_tuple():
    result = create_refresh_token(uuid4())
    assert isinstance(result, tuple)
    assert len(result) == 2

    token, expires_at = result
    assert isinstance(token, str)
    assert isinstance(expires_at, datetime)


def test_create_refresh_token_payload():
    user_id = uuid4()
    token, _ = create_refresh_token(user_id)

    payload = decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_create_refresh_token_expires_in_future():
    _, expires_at = create_refresh_token(uuid4())
    assert expires_at > datetime.now(timezone.utc)


def test_verify_refresh_as_access_raises():
    token, _ = create_refresh_token(uuid4())
    with pytest.raises(InvalidTokenException):
        verify_token(token, "access")


def test_verify_access_as_refresh_raises():
    token = create_access_token(uuid4(), list(UserRole.CUSTOMER.value), "test@test.com")
    with pytest.raises(InvalidTokenException):
        verify_token(token, "refresh")


def test_verify_expired_token_raises():
    expired_payload = {
        "sub": str(uuid4()),
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    token = jwt.encode(
        expired_payload, settings.secret_key, algorithm=settings.algorithm
    )

    with pytest.raises(InvalidTokenException):
        verify_token(token, "access")


def test_verify_tampered_token_raises():
    payload = {
        "sub": str(uuid4()),
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    }
    token = jwt.encode(payload, "wrong-secret-key", algorithm=settings.algorithm)

    with pytest.raises(InvalidTokenException):
        verify_token(token, "access")


def test_verify_garbage_token_raises():
    with pytest.raises(InvalidTokenException):
        verify_token("not-a-jwt", "access")


def test_hash_refresh_token_deterministic():
    token = "some-refresh-token"
    assert hash_refresh_token(token) == hash_refresh_token(token)


def test_hash_refresh_token_length():
    assert len(hash_refresh_token("any")) == 64


def test_hash_refresh_token_different_inputs():
    assert hash_refresh_token("a") != hash_refresh_token("b")
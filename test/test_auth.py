from .utils import *
from api.auth import (
    get_db,
    authenticate_user,
    create_access_token,
    secret_key,
    alg,
    get_current_user,
)
from jose import jwt
from datetime import timedelta
import pytest
from fastapi import HTTPException, status

app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, "test1234!", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username


def test_authenticate_user_non_existent(test_user):
    db = TestingSessionLocal()
    with pytest.raises(ValueError):
        authenticate_user("WrongUserNAme", "password", db)


def test_authenticate_user_wrong_password(test_user):
    db = TestingSessionLocal()
    with pytest.raises(ValueError):
        authenticate_user(test_user.username, "wrong_pass", db)


def test_create_access_token():
    username = "testuser"
    user_id = 1
    role = "user"
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)
    decoded_token = jwt.decode(
        token, secret_key, algorithms=[alg], options={"verify_signature": False}
    )
    assert decoded_token["sub"] == username
    assert decoded_token["id"] == user_id
    assert decoded_token["role"] == role


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {"sub": "testuser", "id": 1, "role": "admin"}
    token = jwt.encode(encode, secret_key, algorithm=alg)
    user = await get_current_user(token)

    assert user == {"username": "testuser", "id": 1, "user_role": "admin"}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {"role": "user"}
    token = jwt.encode(encode, secret_key, algorithm=alg)
    with pytest.raises(HTTPException) as e:
        await get_current_user(token)

    assert e.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert e.value.detail == "Could not validate user"

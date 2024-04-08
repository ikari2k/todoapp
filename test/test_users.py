from .utils import *
from api.users import get_current_user, get_db
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    response = client.get("/api/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "admin"
    assert response.json()["email"] == "admin@email.com"
    assert response.json()["first_name"] == "admin"
    assert response.json()["last_name"] == "admin"
    assert response.json()["role"] == "admin"
    assert response.json()["phone_number"] == "(111)-111-1111"


def test_change_password_success(test_user):
    response = client.put(
        "/api/user/password",
        json={"password": "test1234!", "new_password": "newpassword"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid(test_user):
    response = client.put(
        "/api/user/password",
        json={"password": "wrong_password", "new_password": "newpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Error on password change"}


def test_change_phone_number_success(test_user):
    response = client.put("/api/user/phone_number/222222222")
    assert response.status_code == status.HTTP_204_NO_CONTENT

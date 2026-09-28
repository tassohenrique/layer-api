from datetime import UTC, datetime, timedelta

import jwt
from sqlalchemy import select

from app.core.config import settings
from app.models import User


def register(client, email="tasso@teste.com", password="senha12345", name="Tasso"):
    return client.post(
        "/auth/register",
        json={"email": email, "name": name, "password": password},
    )


def login(client, email="tasso@teste.com", password="senha12345"):
    return client.post("/auth/login", data={"username": email, "password": password})


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# --- Cadastro ---


def test_register_returns_user_without_password(client):
    response = register(client, email="Tasso@Teste.com")

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "tasso@teste.com"
    assert data["role"] == "user"
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_stores_hashed_password(client, db_session):
    register(client, password="senha12345")

    user = db_session.scalar(select(User).where(User.email == "tasso@teste.com"))

    assert user.hashed_password != "senha12345"
    assert user.hashed_password.startswith("$argon2")


def test_register_with_duplicate_email_returns_409(client):
    register(client, email="tasso@teste.com")

    response = register(client, email="TASSO@teste.com")

    assert response.status_code == 409


def test_register_with_invalid_email_returns_422(client):
    response = register(client, email="isso-nao-e-um-email")

    assert response.status_code == 422


def test_register_with_short_password_returns_422(client):
    response = register(client, password="1234567")

    assert response.status_code == 422


# --- Login ---


def test_login_returns_bearer_token(client):
    register(client)

    response = login(client)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_with_wrong_password_returns_401(client):
    register(client)

    response = login(client, password="senha_errada")

    assert response.status_code == 401


def test_login_does_not_reveal_if_email_exists(client):
    register(client)

    wrong_password = login(client, password="senha_errada")
    unknown_email = login(client, email="ninguem@teste.com")

    assert unknown_email.status_code == wrong_password.status_code == 401
    assert unknown_email.json() == wrong_password.json()


# --- Usuário atual (/auth/me) ---


def test_me_returns_current_user(client):
    register(client)
    token = login(client).json()["access_token"]

    response = client.get("/auth/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["email"] == "tasso@teste.com"


def test_me_without_token_returns_401(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_with_invalid_token_returns_401(client):
    response = client.get("/auth/me", headers=auth_headers("token.totalmente.falso"))

    assert response.status_code == 401


def test_me_with_expired_token_returns_401(client):
    user_id = register(client).json()["id"]
    expired_token = jwt.encode(
        {"sub": str(user_id), "exp": datetime.now(UTC) - timedelta(minutes=1)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get("/auth/me", headers=auth_headers(expired_token))

    assert response.status_code == 401


def test_me_with_inactive_user_returns_401(client, db_session):
    register(client)
    token = login(client).json()["access_token"]

    user = db_session.scalar(select(User).where(User.email == "tasso@teste.com"))
    user.is_active = False
    db_session.commit()

    response = client.get("/auth/me", headers=auth_headers(token))

    assert response.status_code == 401

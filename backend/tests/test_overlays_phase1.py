"""Backend tests — Overlay Studio Phase 1 (auth + basic API)."""
import os
import requests
import pytest

BASE_URL = os.environ.get("BACKEND_URL", "http://localhost:8001").rstrip("/")


@pytest.fixture(scope="module")
def token():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@creatools.co", "password": "admin123"},
        timeout=10,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("token")
    return data["token"]


def test_login_admin():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@creatools.co", "password": "admin123"},
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["isAdmin"] is True
    assert data["user"]["plan"] == "pro"
    assert data["user"]["email"] == "admin@creatools.co"
    assert isinstance(data["token"], str) and len(data["token"]) > 20


def test_login_invalid():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@creatools.co", "password": "wrong"},
        timeout=10,
    )
    assert r.status_code in (400, 401)


def test_auth_me(token):
    r = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    user = data.get("user", data)
    assert user["isAdmin"] is True
    assert user["plan"] == "pro"
    assert user["email"] == "admin@creatools.co"


def test_auth_me_no_token():
    r = requests.get(f"{BASE_URL}/api/auth/me", timeout=10)
    assert r.status_code in (401, 403)

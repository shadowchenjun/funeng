"""认证与权限边界"""
import pytest


def test_health(client):
    assert client.get("/health").json() == {"status": "healthy"}


def test_register_login_me(client):
    resp = client.post("/api/auth/register", json={"username": "alice", "password": "secret123", "email": "alice@example.com"})
    assert resp.status_code == 200, resp.text

    resp = client.post("/api/auth/login", data={"username": "alice", "password": "secret123"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "alice"


def test_login_wrong_password(client):
    resp = client.post("/api/auth/login", data={"username": "johnnychenjun", "password": "wrong"})
    assert resp.status_code == 401


def test_admin_login_under_api_prefix(client, admin_headers):
    resp = client.get("/api/admin/auth/profile", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"


@pytest.mark.parametrize("path", [
    "/api/dashboard/stats",
    "/api/smart-agriculture/farm",
    "/api/digital-marketing/members",
    "/api/cold-chain/transport",
    "/api/supply-chain-finance/financing/orders",
])
def test_business_routes_require_login(client, path):
    assert client.get(path).status_code == 401


def test_business_write_requires_login(client):
    resp = client.post("/api/digital-marketing/members", json={"name": "x"})
    assert resp.status_code == 401


def test_user_token_cannot_access_admin(client, user_headers):
    assert client.get("/api/admin/dashboard/stats", headers=user_headers).status_code == 401


def test_admin_routes_require_token(client):
    assert client.get("/api/admin/dashboard/stats").status_code == 401

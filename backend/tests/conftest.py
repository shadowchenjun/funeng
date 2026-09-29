"""
测试夹具：每次测试会话使用一个全新的临时 SQLite 数据库，绝不触碰 funeng.db
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest

_tmpdir = tempfile.mkdtemp(prefix="funeng-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmpdir}/test.db"
os.environ.setdefault("SECRET_KEY", "test-secret-key-at-least-32-bytes-long")
os.environ.setdefault("ADMIN_SECRET_KEY", "test-admin-secret-key-at-least-32-bytes")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402  —— 导入时建表并写入默认数据


@pytest.fixture(scope="session")
def client():
    with TestClient(main.app) as c:
        yield c


@pytest.fixture(scope="session")
def user_headers(client):
    resp = client.post("/api/auth/login", data={"username": "johnnychenjun", "password": "test123456"})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture(scope="session")
def admin_headers(client):
    resp = client.post("/api/admin/auth/login", data={"username": "admin", "password": "admin123456"})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

"""冒烟测试：在全新数据库上，所有无路径参数的 GET 接口都不应报错"""
import pytest

import main

_SKIP_PREFIXES = ("/docs", "/redoc", "/openapi")


def _get_paths():
    paths = []
    for path, ops in main.app.openapi()["paths"].items():
        if "get" in ops and "{" not in path and not path.startswith(_SKIP_PREFIXES):
            paths.append(path)
    return sorted(paths)


@pytest.mark.parametrize("path", _get_paths())
def test_get_endpoint_ok(client, user_headers, admin_headers, path):
    parts = path.split("/")
    admin_only = path.startswith("/api/admin") or (len(parts) > 2 and parts[2] in {"export", "reports", "analytics"})
    headers = admin_headers if admin_only else user_headers
    resp = client.get(path, headers=headers)
    assert resp.status_code < 400, f"{path} -> {resp.status_code}: {resp.text[:300]}"

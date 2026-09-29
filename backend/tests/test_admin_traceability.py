"""管理后台溯源配置回归测试"""


def test_config_list_with_existing_config(client, admin_headers):
    # 回归：TraceabilityConfig 曾缺少 land_parcel 关系，列表在有数据时 500
    resp = client.post("/api/admin/traceability/configs", json={"name": "番茄溯源", "code": "TOMATO-01"}, headers=admin_headers)
    assert resp.status_code < 400, resp.text

    resp = client.get("/api/admin/traceability/configs", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    assert any(c["code"] == "TOMATO-01" and c["land_parcel_name"] is None for c in resp.json())


def test_node_data_fields_accepts_comma_text(client, admin_headers):
    # 回归：逗号分隔的 data_fields 曾导致节点列表 json.loads 崩溃
    configs = client.get("/api/admin/traceability/configs", headers=admin_headers).json()
    config_id = next(c["id"] for c in configs if c["code"] == "TOMATO-01")

    resp = client.post("/api/admin/traceability/nodes", json={
        "config_id": config_id, "name": "采收", "node_type": "harvesting", "data_fields": "temperature, humidity",
    }, headers=admin_headers)
    assert resp.status_code < 400, resp.text

    resp = client.get(f"/api/admin/traceability/configs/{config_id}/nodes", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()[0]["data_fields"] == ["temperature", "humidity"]

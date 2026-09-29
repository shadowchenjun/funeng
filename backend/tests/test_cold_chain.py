"""数字冷链接口测试：数据持久化、状态流转、校验与统计一致性"""
import math

import pytest

API = "/api/cold-chain"

LIST_PATHS = [
    "/transport", "/warehouse", "/warehouses/list", "/vehicles/list", "/owner/list", "/zone/list",
    "/monitoring/temperature", "/monitoring/alerts", "/quality/inspections", "/inventory/alerts",
    "/inbound/appointments", "/inbound/orders", "/operation/tasks", "/operation/performance",
]
STAT_PATHS = ["/analytics", "/inventory/stats", "/inventory/rules", "/operation/batch/suggestions",
              "/transport/T0001", "/warehouse/1", "/inbound/suggestions/IOR2026090003"]


@pytest.mark.parametrize("path", LIST_PATHS + STAT_PATHS)
def test_responses_are_stable(client, user_headers, path):
    first = client.get(API + path, headers=user_headers)
    second = client.get(API + path, headers=user_headers)
    assert first.status_code == 200, first.text
    assert first.json() == second.json()


@pytest.mark.parametrize("path", LIST_PATHS)
def test_lists_are_seeded(client, user_headers, path):
    assert len(client.get(API + path, headers=user_headers).json()) >= 4


def test_requires_login(client):
    assert client.get(f"{API}/quality/inspections").status_code == 401


@pytest.mark.parametrize("path", [
    "/transport/NOPE", "/warehouse/9999", "/quality/inspections/QC99999", "/inventory/alerts/IA9999",
    "/owner/9999", "/inbound/appointments/INB0", "/inbound/orders/IOR0", "/inbound/suggestions/IOR0",
    "/operation/tasks/TSK0", "/traceability/NO-BATCH",
])
def test_detail_404(client, user_headers, path):
    assert client.get(API + path, headers=user_headers).status_code == 404


# ---------- 品控 ----------

def test_create_inspection_persists(client, user_headers):
    payload = {"type": "入库检查", "product": "测试西兰花", "batch_no": "BATCH-TEST-1", "quantity": 88,
               "result": "合格", "score": 91, "temperature": 3.5, "humidity": 88, "inspector": "质检员测试"}
    resp = client.post(f"{API}/quality/inspections", json=payload, headers=user_headers)
    assert resp.status_code == 200, resp.text
    new_id = resp.json()["id"]
    rows = client.get(f"{API}/quality/inspections", headers=user_headers).json()
    assert new_id in [r["id"] for r in rows]
    detail = client.get(f"{API}/quality/inspections/{new_id}", headers=user_headers).json()
    assert detail["product"] == "测试西兰花" and detail["score"] == 91


@pytest.mark.parametrize("patch", [{"result": "优秀"}, {"quantity": 0}, {"score": 120}, {"type": "未知"}])
def test_create_inspection_validation(client, user_headers, patch):
    payload = {"type": "入库检查", "product": "x", "batch_no": "B", "quantity": 1, "result": "合格", "score": 90}
    payload.update(patch)
    assert client.post(f"{API}/quality/inspections", json=payload, headers=user_headers).status_code == 422


# ---------- 库存预警 ----------

def test_resolve_alert_changes_state_and_stats(client, user_headers):
    alerts = client.get(f"{API}/inventory/alerts", headers=user_headers).json()
    target = next(a for a in alerts if a["status"] == "待处理" and a["type"] == "库存不足")
    before = client.get(f"{API}/inventory/stats", headers=user_headers).json()

    resp = client.post(f"{API}/inventory/alerts/{target['id']}/resolve", headers=user_headers)
    assert resp.status_code == 200
    detail = client.get(f"{API}/inventory/alerts/{target['id']}", headers=user_headers).json()
    assert detail["status"] == "已解决"
    after = client.get(f"{API}/inventory/stats", headers=user_headers).json()
    assert after["low_stock_count"] == before["low_stock_count"] - 1
    assert after["today_resolved"] == before["today_resolved"] + 1
    # 重复处理被拒绝
    assert client.post(f"{API}/inventory/alerts/{target['id']}/resolve", headers=user_headers).status_code == 409
    assert client.post(f"{API}/inventory/alerts/IA9999/resolve", headers=user_headers).status_code == 404


def test_inventory_stats_match_rows(client, user_headers):
    alerts = client.get(f"{API}/inventory/alerts", headers=user_headers).json()
    stats = client.get(f"{API}/inventory/stats", headers=user_headers).json()
    open_alerts = [a for a in alerts if a["status"] != "已解决"]
    assert stats["low_stock_count"] == sum(1 for a in open_alerts if a["type"] == "库存不足")
    assert stats["overstock_count"] == sum(1 for a in open_alerts if a["type"] == "库存过多")
    assert stats["expiring_soon_count"] == sum(1 for a in open_alerts if a["type"] == "临期预警")
    assert stats["temp_alert_count"] == sum(1 for a in open_alerts if a["type"] == "温度异常")
    week = stats["this_week"]
    assert week["total_alerts"] == week["resolved"] + week["pending"]
    zones = client.get(f"{API}/zone/list", headers=user_headers).json()
    assert stats["total_stock"] == sum(z["used"] for z in zones) * 50


def test_alerts_sorted_by_level(client, user_headers):
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    levels = [order[a["level"]] for a in client.get(f"{API}/inventory/alerts", headers=user_headers).json()]
    assert levels == sorted(levels)


def test_create_and_update_rule(client, user_headers):
    payload = {"name": "湿度监控", "type": "湿度异常", "threshold": 90, "unit": "%", "notify_channels": ["APP"]}
    resp = client.post(f"{API}/inventory/rules", json=payload, headers=user_headers)
    assert resp.status_code == 200, resp.text
    rule_id = resp.json()["id"]
    rules = client.get(f"{API}/inventory/rules", headers=user_headers).json()["rules"]
    assert any(r["id"] == rule_id and r["enabled"] for r in rules)
    resp = client.put(f"{API}/inventory/rules/{rule_id}", json={"enabled": False}, headers=user_headers)
    assert resp.status_code == 200 and resp.json()["rule"]["enabled"] is False
    assert client.put(f"{API}/inventory/rules/RULE999", json={"enabled": False},
                      headers=user_headers).status_code == 404
    bad = dict(payload, type="不存在的类型")
    assert client.post(f"{API}/inventory/rules", json=bad, headers=user_headers).status_code == 422


# ---------- 入库：预约 -> 签到 -> 收货 -> 上架 ----------

def test_inbound_full_flow(client, user_headers):
    payload = {"owner_code": "OW1001", "vehicle_no": "京T00001", "driver": "测试司机",
               "estimated_arrival": "2026-10-02T09:00:00", "dock": "D9", "zone": "冷藏区A",
               "items": [{"sku": "SKU900", "name": "测试蓝莓", "quantity": 120, "storage_type": "冷藏"},
                         {"sku": "SKU901", "name": "测试冻虾", "quantity": 60, "storage_type": "冷冻"}]}
    resp = client.post(f"{API}/inbound/appointments", json=payload, headers=user_headers)
    assert resp.status_code == 200, resp.text
    appt_id = resp.json()["id"]
    appts = client.get(f"{API}/inbound/appointments", headers=user_headers).json()
    appt = next(a for a in appts if a["id"] == appt_id)
    assert appt["status"] == "待签到" and appt["owner"] == "本来生活网"
    assert appt["expected_items"] == 2 and appt["expected_quantity"] == 180

    # 未签到不能开始收货
    assert client.put(f"{API}/inbound/appointments/{appt_id}/receive", headers=user_headers).status_code == 409
    assert client.put(f"{API}/inbound/appointments/{appt_id}/checkin", headers=user_headers).status_code == 200
    assert client.put(f"{API}/inbound/appointments/{appt_id}/checkin", headers=user_headers).status_code == 409
    resp = client.put(f"{API}/inbound/appointments/{appt_id}/receive", headers=user_headers)
    assert resp.status_code == 200
    order_id = resp.json()["order_id"]

    order = client.get(f"{API}/inbound/orders/{order_id}", headers=user_headers).json()
    assert order["status"] == "待收货" and order["total_quantity"] == 180 and order["warehouse"] == "北京冷链中心"

    # 收货校验
    bad = {"sku": "SKU900", "quantity": 10, "qualified_qty": 11}
    assert client.post(f"{API}/inbound/orders/{order_id}/receive", json=bad, headers=user_headers).status_code == 422
    over = {"sku": "SKU900", "quantity": 500, "qualified_qty": 0}
    assert client.post(f"{API}/inbound/orders/{order_id}/receive", json=over, headers=user_headers).status_code == 400
    unknown = {"sku": "NOPE", "quantity": 1, "qualified_qty": 1}
    assert client.post(f"{API}/inbound/orders/{order_id}/receive", json=unknown,
                       headers=user_headers).status_code == 404

    r = client.post(f"{API}/inbound/orders/{order_id}/receive",
                    json={"sku": "SKU900", "quantity": 120, "qualified_qty": 118}, headers=user_headers)
    assert r.status_code == 200 and r.json()["order"]["status"] == "收货中"
    r = client.post(f"{API}/inbound/orders/{order_id}/receive",
                    json={"sku": "SKU901", "quantity": 60, "qualified_qty": 60}, headers=user_headers)
    order = r.json()["order"]
    assert order["status"] == "已入库"
    assert order["received_quantity"] == 180 and order["qualified_quantity"] == 178
    assert [i["status"] for i in order["items"]] == ["已完成", "已完成"]
    appts = client.get(f"{API}/inbound/appointments", headers=user_headers).json()
    assert next(a for a in appts if a["id"] == appt_id)["status"] == "已完成"

    # 上架建议：温度类型匹配，数量为合格数
    sugg = client.get(f"{API}/inbound/suggestions/{order_id}", headers=user_headers).json()
    zones = {z["id"]: z for z in client.get(f"{API}/zone/list", headers=user_headers).json()}
    by_sku = {s["sku"]: s for s in sugg}
    assert zones[by_sku["SKU900"]["zone_id"]]["type"] in ("冷藏区", "恒温区")
    assert zones[by_sku["SKU901"]["zone_id"]]["type"] == "冷冻区"
    assert by_sku["SKU900"]["quantity"] == 118
    for s in sugg:
        assert 0 < s["confidence"] <= 1

    s = by_sku["SKU901"]
    zone_before = zones[s["zone_id"]]["used"]
    r = client.post(f"{API}/inbound/orders/{order_id}/putaway",
                    json={"sku": s["sku"], "zone_id": s["zone_id"], "location": s["suggested_location"]},
                    headers=user_headers)
    assert r.status_code == 200, r.text
    zones = {z["id"]: z for z in client.get(f"{API}/zone/list", headers=user_headers).json()}
    assert zones[s["zone_id"]]["used"] == zone_before + math.ceil(60 / 50)
    remaining = client.get(f"{API}/inbound/suggestions/{order_id}", headers=user_headers).json()
    assert [x["sku"] for x in remaining] == ["SKU900"]
    # 已上架的 SKU 不能重复上架
    assert client.post(f"{API}/inbound/orders/{order_id}/putaway",
                       json={"sku": s["sku"], "zone_id": s["zone_id"], "location": "X"},
                       headers=user_headers).status_code == 404


def test_create_appointment_validation(client, user_headers):
    base = {"owner_code": "OW1001", "vehicle_no": "京T1", "estimated_arrival": "2026-10-02T09:00:00",
            "items": [{"sku": "S", "name": "n", "quantity": 1}]}
    assert client.post(f"{API}/inbound/appointments", json=dict(base, items=[]),
                       headers=user_headers).status_code == 422
    assert client.post(f"{API}/inbound/appointments", json=dict(base, owner_code="OW0000"),
                       headers=user_headers).status_code == 404
    no_owner = {k: v for k, v in base.items() if k != "owner_code"}
    assert client.post(f"{API}/inbound/appointments", json=no_owner, headers=user_headers).status_code == 422


def test_putaway_suggestions_respect_temperature_and_capacity(client, user_headers):
    zones = {z["id"]: z for z in client.get(f"{API}/zone/list", headers=user_headers).json()}
    order = client.get(f"{API}/inbound/orders/IOR2026090005", headers=user_headers).json()
    storage = {i["sku"]: i["storage_type"] for i in order["items"]}
    expected_type = {"冷藏": ("冷藏区", "恒温区"), "冷冻": ("冷冻区",), "常温": ("常温区", "恒温区")}
    for s in client.get(f"{API}/inbound/suggestions/IOR2026090005", headers=user_headers).json():
        z = zones[s["zone_id"]]
        assert z["type"] in expected_type[storage[s["sku"]]]
        assert z["status"] == "正常"
        assert z["available"] >= math.ceil(s["quantity"] / 50)


# ---------- 作业任务 ----------

def test_task_lifecycle(client, user_headers):
    tasks = client.get(f"{API}/operation/tasks", headers=user_headers).json()
    task = next(t for t in tasks if t["status"] == "待执行" and t["type"] == "盘点")
    tid = task["id"]
    # 未开始不能完成 / 扫描
    assert client.post(f"{API}/operation/tasks/{tid}/complete", headers=user_headers).status_code == 409
    assert client.post(f"{API}/operation/tasks/{tid}/scan", json={"barcode": task["barcode"]},
                       headers=user_headers).status_code == 409
    r = client.post(f"{API}/operation/tasks/{tid}/start", headers=user_headers)
    assert r.status_code == 200
    assert client.post(f"{API}/operation/tasks/{tid}/start", headers=user_headers).status_code == 409

    detail = client.get(f"{API}/operation/tasks/{tid}", headers=user_headers).json()
    assert detail["status"] == "执行中"
    item_barcode = detail["items"][0]["barcode"]
    r = client.post(f"{API}/operation/tasks/{tid}/scan", json={"barcode": item_barcode}, headers=user_headers)
    assert r.status_code == 200 and r.json()["item"]["sku"] == detail["items"][0]["sku"]
    assert client.post(f"{API}/operation/tasks/{tid}/scan", json={"barcode": "WRONG"},
                       headers=user_headers).status_code == 404
    assert client.post(f"{API}/operation/tasks/{tid}/scan", json={}, headers=user_headers).status_code == 422

    before = {p["name"]: p for p in client.get(f"{API}/operation/performance", headers=user_headers).json()}
    assert client.post(f"{API}/operation/tasks/{tid}/complete", headers=user_headers).status_code == 200
    detail = client.get(f"{API}/operation/tasks/{tid}", headers=user_headers).json()
    assert detail["status"] == "已完成"
    assert [h["action"] for h in detail["history"]][-3:] == ["开始执行", "扫描商品", "完成任务"]
    after = {p["name"]: p for p in client.get(f"{API}/operation/performance", headers=user_headers).json()}
    who = task["assigned_to"]
    assert after[who]["tasks_completed"] == before[who]["tasks_completed"] + 1


def test_performance_matches_tasks(client, user_headers):
    tasks = client.get(f"{API}/operation/tasks", headers=user_headers).json()
    for p in client.get(f"{API}/operation/performance", headers=user_headers).json():
        done = [t for t in tasks if t["assigned_to"] == p["name"] and t["status"] == "已完成"]
        assert p["tasks_completed"] == len(done)
        assert 0 <= p["accuracy_rate"] <= 1 and 0 <= p["score"] <= 100


def test_batch_suggestions_and_create(client, user_headers):
    data = client.get(f"{API}/operation/batch/suggestions", headers=user_headers).json()
    assert data["stats"]["suggested_batches"] == len(data["suggestions"]) >= 1
    tasks = {t["id"]: t for t in client.get(f"{API}/operation/tasks", headers=user_headers).json()}
    for s in data["suggestions"]:
        assert len(s["orders"]) >= 2
        assert s["total_items"] == sum(tasks[t]["quantity"] for t in s["orders"])
        assert {tasks[t]["location"][0] for t in s["orders"]} == {s["zone"][0]}

    first = data["suggestions"][0]
    r = client.post(f"{API}/operation/batch/create", json={"task_ids": first["orders"]}, headers=user_headers)
    assert r.status_code == 200, r.text
    batch_id = r.json()["batch_id"]
    assert client.get(f"{API}/operation/tasks/{first['orders'][0]}", headers=user_headers).json()["batch_id"] == batch_id
    after = client.get(f"{API}/operation/batch/suggestions", headers=user_headers).json()
    assert first["id"] not in [s["id"] for s in after["suggestions"]]
    # 已入批次的任务不能再次入批
    assert client.post(f"{API}/operation/batch/create", json={"task_ids": first["orders"]},
                       headers=user_headers).status_code == 409
    assert client.post(f"{API}/operation/batch/create", json={"task_ids": ["TSK0"]},
                       headers=user_headers).status_code == 404
    assert client.post(f"{API}/operation/batch/create", json={"task_ids": []},
                       headers=user_headers).status_code == 422


# ---------- 监控 / 分析 ----------

def test_temperature_monitoring_and_ingest(client, user_headers):
    sensors = client.get(f"{API}/monitoring/temperature", headers=user_headers).json()
    for s in sensors:
        assert s["min_temp"] <= s["current_temp"] <= s["max_temp"]
        assert s["status"] in ("正常", "告警")
    assert any(s["status"] == "告警" for s in sensors)

    target = sensors[0]
    alerts_before = len(client.get(f"{API}/monitoring/alerts", headers=user_headers).json())
    r = client.post(f"{API}/monitoring/readings", json={
        "sensor_id": target["sensor_id"], "temperature": target["target_temp"] + 10, "humidity": 50,
        "recorded_at": "2026-12-31T23:59:00"}, headers=user_headers)
    assert r.status_code == 200 and r.json()["alert_id"]
    now = {s["id"]: s for s in client.get(f"{API}/monitoring/temperature", headers=user_headers).json()}
    assert now[target["id"]]["current_temp"] == target["target_temp"] + 10
    assert now[target["id"]]["status"] == "告警"
    alerts = client.get(f"{API}/monitoring/alerts", headers=user_headers).json()
    assert len(alerts) == alerts_before + 1 and alerts[0]["severity"] == "critical"
    assert client.post(f"{API}/monitoring/readings", json={"sensor_id": "NOPE", "temperature": 1},
                       headers=user_headers).status_code == 404


def test_analytics_consistent_with_rows(client, user_headers):
    a = client.get(f"{API}/analytics", headers=user_headers).json()
    vehicles = client.get(f"{API}/vehicles/list", headers=user_headers).json()
    warehouses = client.get(f"{API}/warehouse", headers=user_headers).json()
    inspections = client.get(f"{API}/quality/inspections", headers=user_headers).json()
    assert a["transport"]["total_vehicles"] == len(vehicles)
    assert a["transport"]["active"] == sum(1 for v in vehicles if v["status"] == "运输中")
    assert a["warehouse"]["total_capacity"] == sum(w["capacity"] for w in warehouses)
    assert a["quality"]["total_batches"] == len({i["batch_no"] for i in inspections})
    passed = sum(1 for i in inspections if i["result"] == "合格")
    assert a["quality"]["pass_rate"] == round(passed / len(inspections) * 100, 1)
    assert a["quality"]["complaints"] == sum(1 for i in inspections if i["result"] == "不合格")
    assert a["cost"]["electricity"] > 0


def test_transport_detail(client, user_headers):
    d = client.get(f"{API}/transport/T0001", headers=user_headers).json()
    assert d["vehicle_no"] == "京A12345" and d["driver_phone"]
    assert [p["location"] for p in d["route_points"]] == [w["name"] for w in d["waypoints"]]
    assert "当前位置" in [p["status"] for p in d["route_points"]]
    assert len(d["temperature_history"]) > 0


def test_owner_list_counts_come_from_zones(client, user_headers):
    zones = client.get(f"{API}/zone/list", headers=user_headers).json()
    for o in client.get(f"{API}/owner/list", headers=user_headers).json():
        mine = [z for z in zones if z["owner_code"] == o["code"]]
        assert o["zone_count"] == len(mine)
        assert o["warehouse_count"] == len({z["warehouse"] for z in mine})


# ---------- 档案 CRUD ----------

def test_warehouse_crud(client, user_headers):
    payload = {"name": "测试冷库", "address": "济南市", "capacity": 800, "area": 300, "temperature": -18,
               "humidity": 45, "status": "正常", "inventory": 0}
    r = client.post(f"{API}/warehouses", json=payload, headers=user_headers)
    assert r.status_code == 200, r.text
    wid = r.json()["id"]
    assert isinstance(wid, int)
    assert client.put(f"{API}/warehouses/{wid}", json={"capacity": 900}, headers=user_headers).status_code == 200
    row = next(w for w in client.get(f"{API}/warehouses/list", headers=user_headers).json() if w["id"] == wid)
    assert row["capacity"] == 900 and row["name"] == "测试冷库"
    assert client.post(f"{API}/warehouses", json={"address": "x"}, headers=user_headers).status_code == 422
    assert client.delete(f"{API}/warehouses/{wid}", headers=user_headers).status_code == 200
    assert client.delete(f"{API}/warehouses/{wid}", headers=user_headers).status_code == 404


def test_vehicle_crud(client, user_headers):
    r = client.post(f"{API}/vehicles", json={"plate": "鲁A99999", "driver": "测试", "volume": "50立方米"},
                    headers=user_headers)
    assert r.status_code == 200, r.text
    vid = r.json()["id"]
    row = next(v for v in client.get(f"{API}/vehicles/list", headers=user_headers).json() if v["id"] == vid)
    assert row["volume"] == 50 and row["status"] == "空闲"
    assert client.put(f"{API}/vehicles/{vid}", json={"status": "运输中"}, headers=user_headers).status_code == 200
    assert client.put(f"{API}/vehicles/99999", json={"status": "运输中"}, headers=user_headers).status_code == 404
    assert client.delete(f"{API}/vehicles/{vid}", headers=user_headers).status_code == 200


def test_owner_crud(client, user_headers):
    r = client.post(f"{API}/owner", json={"name": "测试货主", "contact": "张三"}, headers=user_headers)
    assert r.status_code == 200, r.text
    oid = r.json()["id"]
    assert client.put(f"{API}/owner/{oid}", json={"name": "测试货主2", "status": "暂停"},
                      headers=user_headers).status_code == 200
    detail = client.get(f"{API}/owner/{oid}", headers=user_headers).json()
    assert detail["name"] == "测试货主2" and detail["status"] == "暂停"
    assert client.post(f"{API}/owner", json={"name": ""}, headers=user_headers).status_code == 422
    assert client.delete(f"{API}/owner/{oid}", headers=user_headers).status_code == 200
    assert client.delete(f"{API}/owner/{oid}", headers=user_headers).status_code == 404

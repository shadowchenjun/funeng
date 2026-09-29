"""管理后台写接口：JSON body 契约测试

覆盖每个管理模块的 create + update（JSON body）、非法 body 的 422，
以及密码字段只能放在 body 中（仅放在 query 时被拒绝）。
"""
import uuid
from datetime import datetime, timedelta

import pytest

from app.database import SessionLocal
from app.models.admin import AdoptionOrder, RentalOrder
from app.models.user import User

A = "/api/admin"


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _created_id(resp) -> int:
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["message"] == "创建成功"
    return body["id"]


def _ok(resp):
    assert resp.status_code == 200, resp.text
    return resp.json()


# ============ 认证 / 个人信息 ============

def test_login_and_profile_role_shape_consistent(client, admin_headers):
    login = client.post(f"{A}/auth/login", data={"username": "admin", "password": "admin123456"})
    assert login.status_code == 200, login.text
    profile = _ok(client.get(f"{A}/auth/profile", headers=admin_headers))
    login_role = login.json()["admin"]["role"]
    assert login_role == profile["role"]
    if login_role is not None:
        assert set(login_role) == {"id", "name", "code", "permissions"}


def test_update_profile_json_body(client, admin_headers):
    _ok(client.put(f"{A}/auth/profile", json={"full_name": "超级管理员", "phone": "13800000000"}, headers=admin_headers))
    profile = _ok(client.get(f"{A}/auth/profile", headers=admin_headers))
    assert profile["full_name"] == "超级管理员"
    assert profile["phone"] == "13800000000"

    resp = client.put(f"{A}/auth/profile", json={"email": "not-an-email"}, headers=admin_headers)
    assert resp.status_code == 422
    resp = client.put(f"{A}/auth/profile", json={"unknown_field": 1}, headers=admin_headers)
    assert resp.status_code == 422


def test_change_password_body_only(client, admin_headers):
    # 仅通过 query 传密码 -> 缺少 body，422
    resp = client.post(
        f"{A}/auth/change-password",
        params={"old_password": "admin123456", "new_password": "newpass123"},
        headers=admin_headers,
    )
    assert resp.status_code == 422

    resp = client.post(f"{A}/auth/change-password", json={"old_password": "wrong-pass", "new_password": "newpass123"},
                       headers=admin_headers)
    assert resp.status_code == 400

    resp = client.post(f"{A}/auth/change-password", json={"old_password": "admin123456", "new_password": "123"},
                       headers=admin_headers)
    assert resp.status_code == 422  # 新密码过短

    _ok(client.post(f"{A}/auth/change-password", json={"old_password": "admin123456", "new_password": "newpass123"},
                    headers=admin_headers))
    assert client.post(f"{A}/auth/login", data={"username": "admin", "password": "newpass123"}).status_code == 200
    # 还原，避免影响其他测试
    _ok(client.post(f"{A}/auth/change-password", json={"old_password": "newpass123", "new_password": "admin123456"},
                    headers=admin_headers))


# ============ 管理员 / 角色 ============

def test_admin_user_and_role_crud(client, admin_headers):
    role_id = _created_id(client.post(f"{A}/admin-user/roles", json={
        "name": _uid("运营"), "code": _uid("ops"), "description": "运营角色", "permissions": ["order:read", "order:write"],
    }, headers=admin_headers))
    _ok(client.put(f"{A}/admin-user/roles/{role_id}", json={"description": "新描述", "is_active": False}, headers=admin_headers))
    role = next(r for r in _ok(client.get(f"{A}/admin-user/roles", headers=admin_headers)) if r["id"] == role_id)
    assert role["description"] == "新描述" and role["is_active"] is False
    assert role["permissions"] == '["order:read", "order:write"]'
    assert client.post(f"{A}/admin-user/roles", json={"name": "缺代码"}, headers=admin_headers).status_code == 422
    assert client.put(f"{A}/admin-user/roles/{role_id}", json={"name": None}, headers=admin_headers).status_code == 422

    username = _uid("op")
    # 仅在 query 中传密码：拒绝
    resp = client.post(f"{A}/admin-user/admins", params={"username": username, "password": "secret123"}, headers=admin_headers)
    assert resp.status_code == 422

    admin_id = _created_id(client.post(f"{A}/admin-user/admins", json={
        "username": username, "password": "secret123", "email": f"{username}@funeng.com",
        "full_name": "运营小王", "phone": "", "role_id": role_id,
    }, headers=admin_headers))
    assert client.post(f"{A}/auth/login", data={"username": username, "password": "secret123"}).status_code == 200

    _ok(client.put(f"{A}/admin-user/admins/{admin_id}", json={"full_name": "运营老王", "is_active": False}, headers=admin_headers))
    detail = _ok(client.get(f"{A}/admin-user/admins/{admin_id}", headers=admin_headers))
    assert detail["full_name"] == "运营老王" and detail["is_active"] is False
    assert detail["email"] == f"{username}@funeng.com"  # 未传的字段不变

    assert client.post(f"{A}/admin-user/admins", json={"username": _uid("x"), "password": "123"},
                       headers=admin_headers).status_code == 422
    assert client.put(f"{A}/admin-user/admins/{admin_id}", json={"email": "bad"}, headers=admin_headers).status_code == 422

    # 重置密码：query 拒绝，body 生效
    resp = client.put(f"{A}/admin-user/admins/{admin_id}/password", params={"password": "another123"}, headers=admin_headers)
    assert resp.status_code == 422
    _ok(client.put(f"{A}/admin-user/admins/{admin_id}/password", json={"password": "another123"}, headers=admin_headers))


# ============ 认养 ============

def test_adoption_category_config_and_orders(client, admin_headers):
    cat_id = _created_id(client.post(f"{A}/adoption/categories", json={
        "name": "果树认养", "code": _uid("tree"), "icon": "", "description": "描述",
    }, headers=admin_headers))
    _ok(client.put(f"{A}/adoption/categories/{cat_id}", json={"sort_order": 3, "is_active": False}, headers=admin_headers))
    cat = next(c for c in _ok(client.get(f"{A}/adoption/categories", headers=admin_headers)) if c["id"] == cat_id)
    assert cat["sort_order"] == 3 and cat["is_active"] is False and cat["description"] == "描述"
    assert client.post(f"{A}/adoption/categories", json={"name": "", "code": "c"}, headers=admin_headers).status_code == 422

    cfg_id = _created_id(client.post(f"{A}/adoption/configs", json={
        "category_id": cat_id, "name": "苹果树一年", "price": 999, "duration_days": 365,
        "unit": "year", "benefits": ["采摘", "挂牌"], "images": [], "stock": 10,
    }, headers=admin_headers))
    _ok(client.put(f"{A}/adoption/configs/{cfg_id}", json={"price": 888.5, "benefits": ["采摘"]}, headers=admin_headers))
    cfg = _ok(client.get(f"{A}/adoption/configs/{cfg_id}", headers=admin_headers))
    assert cfg["price"] == 888.5 and cfg["benefits"] == ["采摘"] and cfg["stock"] == 10

    for bad in ({"category_id": cat_id, "name": "x", "price": -1, "duration_days": 1},
                {"category_id": cat_id, "name": "x", "price": 1, "duration_days": 1, "unit": "week"},
                {"category_id": cat_id, "name": "x", "price": 1, "duration_days": 1, "benefits": "not json"}):
        assert client.post(f"{A}/adoption/configs", json=bad, headers=admin_headers).status_code == 422
    assert client.put(f"{A}/adoption/configs/{cfg_id}", json={"stock": -1}, headers=admin_headers).status_code == 422

    # 订单状态 / 分配土地
    parcel_id = _created_id(client.post(f"{A}/land/parcels", json={"name": "认养地块", "code": _uid("AD"), "area": 50},
                                        headers=admin_headers))
    db = SessionLocal()
    try:
        user = db.query(User).first()
        order = AdoptionOrder(order_no=_uid("AO"), user_id=user.id, config_id=cfg_id, total_amount=999)
        db.add(order)
        db.commit()
        order_id = order.id
    finally:
        db.close()

    resp = client.put(f"{A}/adoption/orders/{order_id}/status", params={"status": "active"}, headers=admin_headers)
    assert resp.status_code == 422  # query 不再接受
    assert client.put(f"{A}/adoption/orders/{order_id}/status", json={"status": "bogus"},
                      headers=admin_headers).status_code == 422
    _ok(client.put(f"{A}/adoption/orders/{order_id}/status", json={"status": "active", "remark": "已开通"},
                   headers=admin_headers))
    order = _ok(client.get(f"{A}/adoption/orders/{order_id}", headers=admin_headers))
    assert order["status"] == "active" and order["remark"] == "已开通" and order["end_date"] is not None

    assert client.put(f"{A}/adoption/orders/{order_id}/allocate", json={}, headers=admin_headers).status_code == 422
    _ok(client.put(f"{A}/adoption/orders/{order_id}/allocate", json={"land_parcel_id": parcel_id}, headers=admin_headers))
    assert _ok(client.get(f"{A}/land/parcels/{parcel_id}", headers=admin_headers))["status"] == "rented"


# ============ 土地 ============

def test_land_parcel_and_rental_status(client, admin_headers):
    parcel_id = _created_id(client.post(f"{A}/land/parcels", json={
        "name": "一号地", "code": _uid("L"), "area": 120.5, "type": "orchard", "location": "东区",
    }, headers=admin_headers))
    _ok(client.put(f"{A}/land/parcels/{parcel_id}", json={"area": 200, "description": "肥沃"}, headers=admin_headers))
    parcel = _ok(client.get(f"{A}/land/parcels/{parcel_id}", headers=admin_headers))
    assert parcel["area"] == 200 and parcel["description"] == "肥沃" and parcel["type"] == "orchard"

    assert client.post(f"{A}/land/parcels", json={"name": "x", "code": _uid("L"), "area": 0},
                       headers=admin_headers).status_code == 422
    assert client.put(f"{A}/land/parcels/{parcel_id}", json={"type": "desert"}, headers=admin_headers).status_code == 422
    assert client.put(f"{A}/land/parcels/{parcel_id}", json={"code": "NEW"}, headers=admin_headers).status_code == 422

    db = SessionLocal()
    try:
        user = db.query(User).first()
        now = datetime.now()
        order = RentalOrder(order_no=_uid("RO"), user_id=user.id, land_parcel_id=parcel_id, area=10, unit_price=5,
                            total_amount=50, start_date=now, end_date=now + timedelta(days=30), status="active")
        db.add(order)
        db.commit()
        order_id = order.id
    finally:
        db.close()

    assert client.put(f"{A}/land/rental-orders/{order_id}/status", json={"status": "done"},
                      headers=admin_headers).status_code == 422
    _ok(client.put(f"{A}/land/rental-orders/{order_id}/status", json={"status": "completed", "remark": "到期"},
                   headers=admin_headers))
    order = _ok(client.get(f"{A}/land/rental-orders/{order_id}", headers=admin_headers))
    assert order["status"] == "completed"


# ============ 设备 ============

def test_device_type_device_and_points(client, admin_headers):
    type_id = _created_id(client.post(f"{A}/device/types", json={
        "name": "温湿度传感器", "code": _uid("TH"), "specifications": {"range": "-40~85"},
    }, headers=admin_headers))
    _ok(client.put(f"{A}/device/types/{type_id}", json={"description": "新描述"}, headers=admin_headers))
    t = next(t for t in _ok(client.get(f"{A}/device/types", headers=admin_headers)) if t["id"] == type_id)
    assert t["description"] == "新描述" and t["specifications"] == {"range": "-40~85"}
    assert client.post(f"{A}/device/types", json={"name": "x"}, headers=admin_headers).status_code == 422

    device_id = _created_id(client.post(f"{A}/device/devices", json={
        "name": "1号传感器", "code": _uid("D"), "device_type_id": type_id, "location": "", "config": {"interval": 60},
    }, headers=admin_headers))
    _ok(client.put(f"{A}/device/devices/{device_id}", json={"status": "maintenance", "firmware_version": "1.2.0"},
                   headers=admin_headers))
    device = _ok(client.get(f"{A}/device/devices/{device_id}", headers=admin_headers))
    assert device["status"] == "maintenance" and device["config"] == {"interval": 60}
    assert client.put(f"{A}/device/devices/{device_id}", json={"status": "broken"}, headers=admin_headers).status_code == 422
    assert client.post(f"{A}/device/devices", json={"name": "x", "code": _uid("D"), "device_type_id": 0},
                       headers=admin_headers).status_code == 422

    point_id = _created_id(client.post(f"{A}/device/monitoring-points", json={
        "device_id": device_id, "name": "温度", "data_type": "temperature", "unit": "℃",
        "threshold_min": 0, "threshold_max": 40,
    }, headers=admin_headers))
    _ok(client.put(f"{A}/device/monitoring-points/{point_id}", json={"threshold_max": 35}, headers=admin_headers))
    assert client.put(f"{A}/device/monitoring-points/{point_id}", json={"threshold_min": 50},
                      headers=admin_headers).status_code == 422
    assert client.post(f"{A}/device/monitoring-points", json={
        "device_id": device_id, "name": "湿度", "data_type": "humidity", "threshold_min": 10, "threshold_max": 1,
    }, headers=admin_headers).status_code == 422


# ============ 溯源 ============

def test_traceability_config_node_record(client, admin_headers):
    cfg_id = _created_id(client.post(f"{A}/traceability/configs", json={"name": "苹果溯源", "code": _uid("APPLE")},
                                     headers=admin_headers))
    _ok(client.put(f"{A}/traceability/configs/{cfg_id}", json={"description": "全流程"}, headers=admin_headers))
    cfg = next(c for c in _ok(client.get(f"{A}/traceability/configs", headers=admin_headers)) if c["id"] == cfg_id)
    assert cfg["description"] == "全流程" and cfg["is_active"] is True

    node_id = _created_id(client.post(f"{A}/traceability/nodes", json={
        "config_id": cfg_id, "name": "种植", "node_type": "planting", "data_fields": ["品种", "日期"],
    }, headers=admin_headers))
    _ok(client.put(f"{A}/traceability/nodes/{node_id}", json={"data_fields": '["温度"]', "sort_order": 2},
                   headers=admin_headers))
    node = _ok(client.get(f"{A}/traceability/configs/{cfg_id}/nodes", headers=admin_headers))[0]
    assert node["data_fields"] == ["温度"] and node["sort_order"] == 2
    assert client.post(f"{A}/traceability/nodes", json={"config_id": cfg_id, "name": "x", "node_type": "flying"},
                       headers=admin_headers).status_code == 422

    record_id = _created_id(client.post(f"{A}/traceability/records", json={
        "node_id": node_id, "data": {"品种": "红富士"},
    }, headers=admin_headers))
    record = _ok(client.get(f"{A}/traceability/records/{record_id}", headers=admin_headers))
    assert record["data"] == {"品种": "红富士"}
    assert client.post(f"{A}/traceability/records", json={"node_id": node_id, "data": "{broken"},
                       headers=admin_headers).status_code == 422


# ============ C 端用户 / 分组 ============

def test_user_status_and_groups(client, admin_headers):
    users = _ok(client.get(f"{A}/user/users", params={"page_size": 100}, headers=admin_headers))["items"]
    user_id = users[0]["id"]
    assert client.put(f"{A}/user/users/{user_id}/status", params={"is_active": False},
                      headers=admin_headers).status_code == 422
    assert client.put(f"{A}/user/users/{user_id}/status", json={"is_active": "maybe"},
                      headers=admin_headers).status_code == 422
    _ok(client.put(f"{A}/user/users/{user_id}/status", json={"is_active": False}, headers=admin_headers))
    assert _ok(client.get(f"{A}/user/users/{user_id}", headers=admin_headers))["is_active"] is False
    _ok(client.put(f"{A}/user/users/{user_id}/status", json={"is_active": True}, headers=admin_headers))

    group_id = _created_id(client.post(f"{A}/user/groups", json={
        "name": "VIP", "code": _uid("vip"), "criteria": {"min_orders": 5},
    }, headers=admin_headers))
    _ok(client.put(f"{A}/user/groups/{group_id}", json={"name": "超级VIP"}, headers=admin_headers))
    group = next(g for g in _ok(client.get(f"{A}/user/groups", headers=admin_headers)) if g["id"] == group_id)
    assert group["name"] == "超级VIP" and group["criteria"] == '{"min_orders": 5}'
    assert client.post(f"{A}/user/groups", json={"name": "无代码"}, headers=admin_headers).status_code == 422


# ============ 营销 ============

def test_coupon_and_activity(client, admin_headers):
    coupon_id = _created_id(client.post(f"{A}/marketing/coupons", json={
        "name": "满100减10", "code": _uid("C"), "type": "cash", "discount_value": 10, "min_amount": 100,
        "valid_from": "2026-01-01T00:00:00", "valid_until": "2026-12-31T23:59:59",
    }, headers=admin_headers))
    _ok(client.put(f"{A}/marketing/coupons/{coupon_id}", json={"total_count": 50, "is_active": False}, headers=admin_headers))
    coupon = _ok(client.get(f"{A}/marketing/coupons/{coupon_id}", headers=admin_headers))
    assert coupon["total_count"] == 50 and coupon["is_active"] is False and coupon["type"] == "cash"

    base = {"name": "x", "code": _uid("C"), "discount_value": 10,
            "valid_from": "2026-01-01T00:00:00", "valid_until": "2026-12-31T00:00:00"}
    assert client.post(f"{A}/marketing/coupons", json={**base, "type": "gift"}, headers=admin_headers).status_code == 422
    assert client.post(f"{A}/marketing/coupons", json={**base, "valid_until": "2025-01-01T00:00:00"},
                       headers=admin_headers).status_code == 422
    assert client.put(f"{A}/marketing/coupons/{coupon_id}", json={"valid_until": "2025-01-01T00:00:00"},
                      headers=admin_headers).status_code == 422

    activity_id = _created_id(client.post(f"{A}/marketing/activities", json={
        "name": "秋收节", "type": "flash_sale", "start_time": "2026-09-01 00:00:00", "end_time": "2026-09-30 23:59:59",
        "rules": {"limit": 1},
    }, headers=admin_headers))
    _ok(client.put(f"{A}/marketing/activities/{activity_id}", json={"status": "active"}, headers=admin_headers))
    activity = _ok(client.get(f"{A}/marketing/activities/{activity_id}", headers=admin_headers))
    assert activity["status"] == "active" and activity["rules"] == {"limit": 1}
    assert client.put(f"{A}/marketing/activities/{activity_id}", json={"status": "paused"},
                      headers=admin_headers).status_code == 422
    assert client.post(f"{A}/marketing/activities", json={"name": "x", "type": "t", "start_time": "not a date",
                                                          "end_time": "2026-09-30T00:00:00"},
                       headers=admin_headers).status_code == 422


# ============ 系统配置 ============

@pytest.mark.parametrize("type_, value, expected", [
    ("string", "hello", "hello"),
    ("json", {"a": 1}, {"a": 1}),
])
def test_system_config(client, admin_headers, type_, value, expected):
    key = _uid("cfg").replace("-", "_")
    _created_id(client.post(f"{A}/system/configs", json={"key": key, "value": value, "type": type_, "group": "site"},
                            headers=admin_headers))
    assert _ok(client.get(f"{A}/system/configs/{key}", headers=admin_headers))["value"] == expected

    new_value = "world" if type_ == "string" else [1, 2]
    _ok(client.put(f"{A}/system/configs/{key}", json={"value": new_value}, headers=admin_headers))
    assert _ok(client.get(f"{A}/system/configs/{key}", headers=admin_headers))["value"] == new_value

    assert client.put(f"{A}/system/configs/{key}", params={"value": "q"}, headers=admin_headers).status_code == 422
    if type_ == "json":
        assert client.put(f"{A}/system/configs/{key}", json={"value": "{bad"}, headers=admin_headers).status_code == 422


def test_system_config_invalid_body(client, admin_headers):
    assert client.post(f"{A}/system/configs", json={"key": "k_no_value"}, headers=admin_headers).status_code == 422
    assert client.post(f"{A}/system/configs", json={"key": _uid("k"), "value": "1", "type": "yaml"},
                       headers=admin_headers).status_code == 422


def test_blank_strings_from_forms(client, admin_headers):
    # 表单未填写的输入框提交 ""：有默认值的字段回落默认值，可空字段存为 null
    key = _uid("blank").replace("-", "_")
    _created_id(client.post(f"{A}/system/configs", json={"key": key, "value": "", "type": "string", "group": "",
                                                        "description": ""}, headers=admin_headers))
    cfg = _ok(client.get(f"{A}/system/configs/{key}", headers=admin_headers))
    assert cfg["group"] == "general" and cfg["value"] == "" and cfg["description"] is None

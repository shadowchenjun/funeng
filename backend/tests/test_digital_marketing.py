"""数字营销：订单与分析接口来自数据库"""
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models.smart_agriculture import MarketingOrder, MarketingTrafficDaily

BASE = "/api/digital-marketing"


def test_orders_are_stable_and_from_db(client, user_headers):
    first = client.get(f"{BASE}/orders", headers=user_headers)
    second = client.get(f"{BASE}/orders", headers=user_headers)
    assert first.status_code == 200, first.text
    assert first.json() == second.json()
    orders = first.json()
    assert len(orders) == 20
    assert {"id", "customer_name", "product", "quantity", "price", "status", "channel", "created_at"} <= set(orders[0])
    with SessionLocal() as db:
        row = db.query(MarketingOrder).filter(MarketingOrder.order_no == orders[0]["id"]).one()
        assert row.amount == orders[0]["price"]
        assert round(row.unit_price * row.quantity, 2) == row.amount


def test_orders_filter(client, user_headers):
    orders = client.get(f"{BASE}/orders", params={"status": "已完成", "limit": 500}, headers=user_headers).json()
    assert orders and all(o["status"] == "已完成" for o in orders)


def test_analytics_consistent_with_rows(client, user_headers):
    first = client.get(f"{BASE}/analytics", headers=user_headers)
    assert first.status_code == 200, first.text
    data = first.json()
    assert data == client.get(f"{BASE}/analytics", headers=user_headers).json()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    with SessionLocal() as db:
        valid = db.query(MarketingOrder).filter(MarketingOrder.status != "已取消").all()
        pending = db.query(MarketingOrder).filter(MarketingOrder.status.in_(("待付款", "待发货"))).count()
        traffic = db.query(MarketingTrafficDaily).filter(
            MarketingTrafficDaily.date == today.strftime("%Y-%m-%d")).one()
    todays = [o for o in valid if today <= o.created_at < today + timedelta(days=1)]
    assert data["overview"]["total_orders"] == len(valid)
    assert data["overview"]["total_revenue"] == round(sum(o.amount for o in valid), 2)
    assert data["today"]["sales"] == round(sum(o.amount for o in todays), 2)
    assert data["today"]["visitors"] == traffic.visitors
    assert data["channels"]["ecommerce"]["pending_orders"] == pending
    assert data["channels"]["social"]["followers"] == traffic.followers_total


def test_update_order_status_persists(client, user_headers):
    order = client.get(f"{BASE}/orders", params={"status": "待发货"}, headers=user_headers).json()[0]
    resp = client.put(f"{BASE}/orders/{order['id']}/status", json={"status": "配送中"}, headers=user_headers)
    assert resp.status_code == 200, resp.text
    with SessionLocal() as db:
        assert db.query(MarketingOrder).filter(MarketingOrder.order_no == order["id"]).one().status == "配送中"
    assert client.put(f"{BASE}/orders/{order['id']}/status", json={"status": "乱写"},
                      headers=user_headers).status_code == 400
    assert client.put(f"{BASE}/orders/NOPE/status", json={"status": "已完成"},
                      headers=user_headers).status_code == 404

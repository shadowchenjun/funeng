"""公开统计接口"""


def test_public_stats_without_login(client):
    resp = client.get("/api/public/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert set(data) == {"user_count", "order_count", "total_revenue", "product_count"}
    assert data["user_count"] >= 1  # 默认账号
    assert data["product_count"] >= 1  # 默认产品

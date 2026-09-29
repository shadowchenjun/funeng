"""供应链金融接口测试：数据持久化、统计一致性、写接口与校验"""
import pytest

API = "/api/supply-chain-finance"

LIST_PATHS = ["/financing/orders", "/receivables", "/insurance", "/credit/assessment"]
STAT_PATHS = ["/financing/stats", "/receivables/stats", "/insurance/stats", "/analytics"]


@pytest.mark.parametrize("path", LIST_PATHS + STAT_PATHS + ["/products"])
def test_responses_are_stable(client, user_headers, path):
    first = client.get(API + path, headers=user_headers)
    second = client.get(API + path, headers=user_headers)
    assert first.status_code == 200
    assert first.json() == second.json()


@pytest.mark.parametrize("path", LIST_PATHS)
def test_lists_are_seeded(client, user_headers, path):
    assert len(client.get(API + path, headers=user_headers).json()) >= 10


def test_financing_stats_match_rows(client, user_headers):
    orders = client.get(f"{API}/financing/orders", headers=user_headers).json()
    stats = client.get(f"{API}/financing/stats", headers=user_headers).json()
    assert stats["total_amount"] == pytest.approx(sum(o["amount"] for o in orders))
    assert stats["total_financed"] == pytest.approx(
        sum(o["financed_amount"] for o in orders if o["status"] in ("放款中", "已放款", "已结清")))
    assert stats["avg_rate"] == pytest.approx(round(sum(o["rate"] for o in orders) / len(orders), 2))
    assert stats["active_orders"] == sum(1 for o in orders if o["status"] in ("审核中", "已批准", "放款中", "已放款"))
    assert sum(stats["by_status"].values()) == len(orders)
    for status, count in stats["by_status"].items():
        assert count == sum(1 for o in orders if o["status"] == status)


def test_receivables_stats_match_rows(client, user_headers):
    rows = client.get(f"{API}/receivables", headers=user_headers).json()
    stats = client.get(f"{API}/receivables/stats", headers=user_headers).json()
    total = sum(r["amount"] for r in rows)
    paid = sum(r["paid_amount"] for r in rows)
    assert stats["total_amount"] == pytest.approx(total)
    assert stats["collected"] == pytest.approx(paid)
    assert stats["outstanding"] == pytest.approx(total - paid)
    assert stats["overdue"] == pytest.approx(
        sum(r["amount"] - r["paid_amount"] for r in rows if r["status"] == "已逾期"))
    assert sum(stats["by_status"].values()) == pytest.approx(total)


def test_insurance_stats_match_rows(client, user_headers):
    rows = client.get(f"{API}/insurance", headers=user_headers).json()
    stats = client.get(f"{API}/insurance/stats", headers=user_headers).json()
    assert stats["total_policies"] == len(rows)
    assert stats["active_policies"] == sum(1 for p in rows if p["status"] == "生效中")
    assert stats["total_coverage"] == pytest.approx(sum(p["coverage"] for p in rows))
    assert stats["total_premium"] == pytest.approx(sum(p["premium"] for p in rows))
    assert sum(stats["by_type"].values()) == len(rows)


def test_create_financing_order_appears_in_list_and_stats(client, user_headers):
    before = client.get(f"{API}/financing/stats", headers=user_headers).json()
    resp = client.post(f"{API}/financing/orders", headers=user_headers,
                       json={"amount": 120000, "term": 60, "collateral": "质押"})
    assert resp.status_code == 201, resp.text
    order = resp.json()
    assert order["status"] == "审核中"
    assert order["financed_amount"] == 120000
    assert order["applicant"] == "johnnychenjun"
    assert order["id"].startswith("F") and order["order_no"].startswith("ORD")

    ids = [o["id"] for o in client.get(f"{API}/financing/orders", headers=user_headers).json()]
    assert order["id"] in ids

    after = client.get(f"{API}/financing/stats", headers=user_headers).json()
    assert after["by_status"]["审核中"] == before["by_status"]["审核中"] + 1
    assert after["active_orders"] == before["active_orders"] + 1
    assert after["total_amount"] == pytest.approx(before["total_amount"] + 120000)


@pytest.mark.parametrize("payload", [
    {"amount": -1, "term": 30},
    {"amount": 0, "term": 30},
    {"amount": 1000, "term": 45},
    {"amount": 1000, "term": 30, "collateral": "口头承诺"},
    {"amount": 5000, "order_amount": 1000, "term": 30},
    {"term": 30},
])
def test_create_financing_order_invalid_payload(client, user_headers, payload):
    assert client.post(f"{API}/financing/orders", headers=user_headers, json=payload).status_code == 422


def test_financing_status_update(client, user_headers):
    order = client.post(f"{API}/financing/orders", headers=user_headers,
                        json={"amount": 50000, "term": 30}).json()
    url = f"{API}/financing/orders/{order['id']}/status"

    resp = client.patch(url, headers=user_headers, json={"status": "已批准"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "已批准"

    # 非法流转
    assert client.patch(url, headers=user_headers, json={"status": "已结清"}).status_code == 400
    # 非法状态值
    assert client.patch(url, headers=user_headers, json={"status": "随便"}).status_code == 422
    # 不存在的订单
    assert client.patch(f"{API}/financing/orders/F9999/status", headers=user_headers,
                        json={"status": "已批准"}).status_code == 404

    listed = {o["id"]: o for o in client.get(f"{API}/financing/orders", headers=user_headers).json()}
    assert listed[order["id"]]["status"] == "已批准"


def test_create_insurance_policy(client, user_headers):
    before = client.get(f"{API}/insurance/stats", headers=user_headers).json()
    resp = client.post(f"{API}/insurance", headers=user_headers,
                       json={"type": "种植保险", "crop": "小麦", "coverage": 200000, "term_months": 6})
    assert resp.status_code == 201, resp.text
    policy = resp.json()
    assert policy["status"] == "生效中"
    assert policy["premium"] == pytest.approx(200000 * 0.035)
    assert policy["policy_no"].startswith("POL")

    ids = [p["id"] for p in client.get(f"{API}/insurance", headers=user_headers).json()]
    assert policy["id"] in ids
    after = client.get(f"{API}/insurance/stats", headers=user_headers).json()
    assert after["total_policies"] == before["total_policies"] + 1
    assert after["total_coverage"] == pytest.approx(before["total_coverage"] + 200000)


@pytest.mark.parametrize("payload", [
    {"type": "种植保险", "crop": "小麦", "coverage": 0},
    {"type": "寿险", "crop": "小麦", "coverage": 1000},
    {"type": "种植保险", "crop": "", "coverage": 1000},
    {"type": "种植保险", "crop": "小麦", "coverage": 1000, "term_months": 5},
])
def test_create_insurance_invalid_payload(client, user_headers, payload):
    assert client.post(f"{API}/insurance", headers=user_headers, json=payload).status_code == 422


def test_credit_detail(client, user_headers):
    first = client.get(f"{API}/credit/assessment", headers=user_headers).json()[0]
    detail = client.get(f"{API}/credit/{first['id']}", headers=user_headers)
    assert detail.status_code == 200
    body = detail.json()
    assert body["entity_name"] == first["entity_name"]
    assert body["credit_score"] == first["credit_score"]
    assert set(body["factors"]) == {"financial", "operation", "management", "industry"}


@pytest.mark.parametrize("entity_id", ["CR9999", "999999", "unknown"])
def test_credit_detail_unknown_404(client, user_headers, entity_id):
    assert client.get(f"{API}/credit/{entity_id}", headers=user_headers).status_code == 404


def test_write_endpoints_require_login(client):
    assert client.post(f"{API}/financing/orders", json={"amount": 1000, "term": 30}).status_code == 401
    assert client.post(f"{API}/insurance", json={"type": "种植保险", "crop": "小麦", "coverage": 1000}).status_code == 401


# ---------------------------------------------------------------------------
# 应收账款转让
# ---------------------------------------------------------------------------

def _transferable_receivable(client, user_headers):
    rows = client.get("/api/supply-chain-finance/receivables", headers=user_headers).json()
    return next(r for r in rows if r["status"] in ("未到期", "即将到期") and not r["financing_order_id"])


def test_transfer_receivable_creates_financing_order(client, user_headers):
    r = _transferable_receivable(client, user_headers)
    resp = client.post(f"/api/supply-chain-finance/receivables/{r['id']}/transfer", json={"term": 60}, headers=user_headers)
    assert resp.status_code == 201, resp.text
    order = resp.json()
    assert order["status"] == "审核中"
    assert order["collateral"] == "应收账款质押"
    assert order["financed_amount"] == round((r["amount"] - r["paid_amount"]) * 0.8, 2)

    rows = client.get("/api/supply-chain-finance/receivables", headers=user_headers).json()
    assert next(x for x in rows if x["id"] == r["id"])["financing_order_id"] == order["id"]
    orders = client.get("/api/supply-chain-finance/financing/orders", headers=user_headers).json()
    assert any(o["id"] == order["id"] for o in orders)

    # 同一笔账款不能重复转让
    again = client.post(f"/api/supply-chain-finance/receivables/{r['id']}/transfer", json={}, headers=user_headers)
    assert again.status_code == 400


def test_transfer_receivable_amount_limit(client, user_headers):
    r = _transferable_receivable(client, user_headers)
    too_much = round((r["amount"] - r["paid_amount"]) * 0.95, 2)
    resp = client.post(f"/api/supply-chain-finance/receivables/{r['id']}/transfer", json={"amount": too_much}, headers=user_headers)
    assert resp.status_code == 400


def test_transfer_receivable_rejects_closed_status(client, user_headers):
    rows = client.get("/api/supply-chain-finance/receivables", headers=user_headers).json()
    closed = next(r for r in rows if r["status"] in ("已收回", "坏账", "已逾期"))
    resp = client.post(f"/api/supply-chain-finance/receivables/{closed['id']}/transfer", json={}, headers=user_headers)
    assert resp.status_code == 400


def test_transfer_receivable_not_found(client, user_headers):
    resp = client.post("/api/supply-chain-finance/receivables/AR9999/transfer", json={}, headers=user_headers)
    assert resp.status_code == 404

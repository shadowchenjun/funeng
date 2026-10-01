"""Snapshot import checks for corruption, provenance and rerun identity."""
import base64
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path

import pytest

from app.industry_data.import_bundle import (
    batch_sql, build_bundle, deduplicate, normalize_price, sql_batches, verification_definition,
)

ROOT = Path(__file__).resolve().parents[2]
INDUSTRY = ROOT / "docs/prototypes/agri-industry-dashboard.snapshot.json"
MARKET = ROOT / "docs/prototypes/agri-market-dashboard.snapshot.json"


def test_snapshot_union_removes_overlap_and_keeps_history_and_missing_units():
    bundle = build_bundle(INDUSTRY, MARKET)
    prices = bundle["tables"]["market_price_observations"]
    assert len(prices) == 1148 and bundle["manifest"]["price_overlap_removed"] == 11
    assert any(r["observed_date"] == "2026-09-22" for r in prices)
    missing = [r for r in prices if r["quality_flag"] != "ok"]
    assert len(missing) == 14
    assert len([r for r in missing if r["quality_flag"] == "missing_unit"]) == 1
    assert len([r for r in missing if r["quality_flag"] == "unknown_unit"]) == 13
    assert all(r["price_avg_yuan_per_kg"] is None for r in missing)
    assert all(r["source_url"] for r in prices)


def test_import_keeps_lower_bounds_manual_status_and_no_fake_platform_balance():
    tables = build_bundle(INDUSTRY, MARKET)["tables"]
    indicators = tables["industry_observations"]
    premium = next(r for r in indicators if r["metric"] == "agri_insurance_premium")
    assert premium["value"] == "1550" and premium["qualifier"] == "gt"
    credit = next(r for r in indicators if r["metric"] == "agricultural_related_credit")
    assert Decimal(credit["value"]) == Decimal("53.57")
    assert credit["period_start"] == credit["period_end"] == "2025-12-31"
    assert len([r for r in indicators if r["review_status"] == "manual_reviewed"]) == 12
    assert not any(r["source_id"] == "platform_finance" for r in indicators)
    pending = next(s for s in tables["agri_data_sources"] if s["source_id"] == "platform_finance")
    assert pending["status"] == "pending"


def test_repeated_snapshot_identity_and_batches_are_stable():
    first = build_bundle(INDUSTRY, MARKET)
    assert first == build_bundle(INDUSTRY, MARKET)
    batches = sql_batches(first)
    assert all(0 < b["rows"] <= 200 for b in batches)
    assert batches[-1]["table"] == "agri_data_import_runs"
    assert "IS DISTINCT FROM" in batches[0]["sql"]


def test_dedup_refuses_conflicting_value_instead_of_silently_choosing():
    assert deduplicate([{"key": "same", "price": 1}] * 2, "key")[1] == 1
    with pytest.raises(ValueError, match="Conflicting"):
        deduplicate([{"key": "same", "price": 1}, {"key": "same", "price": 2}], "key")


def test_price_rejects_tampered_conversion_key_and_nonfinite_money():
    row = json.loads(MARKET.read_text())["rows"][0]
    changed = deepcopy(row)
    changed["price_avg_yuan_per_kg"] = "9999"
    with pytest.raises(ValueError, match="normalization"):
        normalize_price(changed)
    for value in ("-1", "NaN", "Infinity", "100000000", "0.00001"):
        changed = deepcopy(row)
        changed["price_avg"] = value
        with pytest.raises(ValueError):
            normalize_price(changed)


def test_failed_source_snapshot_cannot_be_imported(tmp_path):
    content = json.loads(INDUSTRY.read_text())
    content["errors"] = [{"source_id": "pbc_credit", "error": "failed"}]
    path = tmp_path / "failed.json"
    path.write_text(json.dumps(content))
    with pytest.raises(ValueError, match="unresolved"):
        build_bundle(path, MARKET)


def test_sql_binds_data_without_interpolating_quotes_or_allowing_table_injection():
    payload = [{"name": "广州'); DROP TABLE products;--"}]
    query = batch_sql("agri_data_sources", payload)
    assert payload[0]["name"] not in query
    assert "jsonb_to_recordset($1)" in query
    encoded = query.split("decode('", 1)[1].split("'", 1)[0]
    assert json.loads(base64.b64decode(encoded)) == payload
    with pytest.raises(ValueError, match="Unknown"):
        batch_sql("products;DROP TABLE users", payload)


def test_content_comparison_preserves_exact_money_and_equivalent_decimal_scale():
    bundle = build_bundle(INDUSTRY, MARKET)
    before = verification_definition(bundle)
    changed = deepcopy(bundle)
    row = changed["tables"]["industry_observations"][0]
    row["value"] += "0"
    # The first value is 119408.9, so appending zero changes only its decimal scale.
    assert before["expected"] == verification_definition(changed)["expected"]
    row["value"] = str(Decimal(row["value"]) + Decimal("0.01"))
    assert before["expected"]["industry_observations"] != verification_definition(changed)["expected"]["industry_observations"]

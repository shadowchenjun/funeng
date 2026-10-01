"""Meaningful extraction and boundary checks, independent of external availability."""
from datetime import date
from decimal import Decimal

import pytest

from app.industry_data.collectors import (
    PROVINCES, parse_agricultural_credit, parse_fisheries, parse_grain, parse_insurance_subsidy,
)
from app.industry_data.types import IndustryObservation


def grain_table() -> str:
    rows = "".join(f"<tr><td>{name}</td><td>100.0</td><td>60.0</td><td>6000.0</td></tr>"
                   for name in PROVINCES)
    return "<table><tr><th>地区</th><th>播种面积（千公顷）</th><th>总产量（万吨）</th></tr>" + rows + "</table>"


def test_grain_deduplicates_mobile_copy_and_keeps_grain_and_units():
    rows = parse_grain(grain_table() * 2, 2025, "https://www.stats.gov.cn/example")
    assert len(rows) == 96
    assert len({r.external_key for r in rows}) == 96
    area = next(r for r in rows if r.region == "广西壮族自治区" and r.metric == "grain_area")
    assert area.value == Decimal("100.0")
    assert area.unit == "千公顷" and area.measure_type == "sown_area"
    assert area.period_end == date(2025, 12, 31)


def test_grain_rejects_incomplete_coverage_and_malformed_measurement():
    with pytest.raises(ValueError, match="Incomplete"):
        parse_grain("<table></table>", 2025, "https://example.com")
    with pytest.raises(ValueError, match="Invalid grain"):
        parse_grain(grain_table().replace("100.0", "—", 1), 2025, "https://example.com")
    with pytest.raises(ValueError, match="Conflicting"):
        parse_grain(grain_table() + grain_table().replace("100.0", "101.0", 1),
                    2025, "https://example.com")


CREDIT = """<p>五、涉农贷款持续增加</p><p>2025年四季度末，本外币涉农贷款<sup>3</sup>余额53.57万亿元，同比增长6.5%。
农村贷款余额39.24万亿元，同比增长6.3%。农户贷款余额18.42万亿元，同比增长1.0%。农业贷款余额6.89万亿元，同比增长8.3%。
</p><p>六、房地产贷款有所放缓</p>"""


def test_credit_preserves_exact_money_balance_and_growth_separately():
    rows = parse_agricultural_credit(CREDIT, 2025, 4, "https://www.pbc.gov.cn/example")
    assert [r.value for r in rows] == list(map(Decimal, ["53.57", "39.24", "18.42", "6.89"]))
    assert rows[0].yoy_percent == Decimal("6.5")
    assert rows[0].period_start == rows[0].period_end == date(2025, 12, 31)
    assert rows[0].to_dict()["value"] == "53.57"
    assert all(r.measure_type == "balance" for r in rows)


def test_credit_rejects_partial_report_instead_of_filling_zero():
    with pytest.raises(ValueError, match="Missing credit"):
        parse_agricultural_credit(CREDIT.replace("农户贷款余额", "住户贷款余额"),
                                  2025, 4, "https://example.com")


def test_fiscal_lower_bounds_are_not_converted_to_exact_values():
    report = "2025年，中央财政拨付农业保险保费补贴517亿元，支持我国农业保险保费规模超1550亿元、为农户提供风险保障超5万亿元、向农户支付赔款超1200亿元。"
    rows = parse_insurance_subsidy(report, 2025, "https://www.mof.gov.cn/example")
    assert rows[0].value == Decimal("517") and rows[0].qualifier == "exact"
    assert all(r.qualifier == "gt" for r in rows[1:])


def test_fisheries_separates_areas_from_outputs_and_rejects_wrong_year():
    report = ("2025年全国水产养殖面积7760.60千公顷，海水养殖面积2408.52千公顷，"
              "淡水养殖面积5352.08千公顷。全国水产品总产量7652.14万吨，"
              "其中，养殖产量6325.62万吨。")
    rows = parse_fisheries(report, 2025, "https://example.com")
    assert rows[0].value == rows[1].value + rows[2].value
    assert rows[0].value == Decimal("7760.60")
    assert rows[0].unit == "千公顷" and rows[3].unit == "万吨"
    assert rows[3].measure_type == "annual_flow"
    with pytest.raises(ValueError, match="year mismatch"):
        parse_fisheries(report, 2024, "https://example.com")
    with pytest.raises(ValueError, match="Missing fisheries"):
        parse_fisheries(report.replace("2408.52千公顷", "—"),
                        2025, "https://example.com")


def test_observation_revisions_keep_identity_and_reject_invalid_value():
    args = ("source", "https://example.com", "balance", "余额", "全国", "金融",
            date(2025, 12, 31), date(2025, 12, 31), "quarterly")
    original = IndustryObservation(*args, Decimal("1.01"), "亿元", "balance", "原文")
    revised = IndustryObservation(*args, Decimal("1.02"), "亿元", "balance", "修订")
    assert original.external_key == revised.external_key
    with pytest.raises(ValueError, match="finite"):
        IndustryObservation(*args, Decimal("NaN"), "亿元", "balance", "原文")


def test_cli_reports_partial_failure_without_touching_a_database(monkeypatch, capsys):
    from scripts import collect_industry_data as command

    monkeypatch.setattr(command, "SOURCES", {"ok": {}, "failed": {}})

    def collect(name):
        if name == "failed":
            raise ValueError("source unavailable")
        return parse_agricultural_credit(CREDIT, 2025, 4, "https://example.com"), {"source_id": name}

    monkeypatch.setattr(command, "collect_source", collect)
    assert command.main([]) == 1
    import json
    output = json.loads(capsys.readouterr().out)
    assert len(output["observations"]) == 4
    assert output["errors"][0]["source_id"] == "failed"

"""行情采集的解析、单位和重复入库测试；外部网站由固定样本代替。"""
from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.market_data.collectors import (
    parse_guangzhou_workbook,
    parse_moa_daily,
    parse_moa_milk,
    parse_mofcom,
    parse_wuhan,
    parse_xinfadi,
)
from app.market_data.persistence import upsert_observations
from app.market_data.types import normalize_price
from app.models.base import Base
from app.models.market_price import MarketPriceObservation


def test_normalize_price_preserves_unknown_units():
    assert normalize_price(Decimal("3.75"), "斤") == Decimal("7.50")
    assert normalize_price(Decimal("3.75"), "元/市斤") == Decimal("7.50")
    assert normalize_price(Decimal("3.75"), "元/公斤") == Decimal("3.75")
    assert normalize_price(Decimal("3.75"), "") is None
    assert normalize_price(Decimal("3.75"), "筐") is None


def test_parse_mofcom_keeps_market_and_date():
    html = """<h1>2026-09-28西红柿批发价格行情</h1><table id="goaler">
    <tr><td>地区</td><td>市场</td><td>当日价格</td></tr>
    <tr><td>河南省</td><td>河南万邦市场</td><td>4.11</td></tr></table>"""
    rows = parse_mofcom(html, "西红柿", date(2026, 9, 28), "https://cif.mofcom.gov.cn/example")
    assert len(rows) == 1
    assert rows[0].category == "蔬菜"
    assert rows[0].province == "河南省"
    assert rows[0].price_avg == Decimal("4.11")
    assert rows[0].price_avg_yuan_per_kg == Decimal("4.11")


def test_parse_xinfadi_keeps_specs_and_missing_unit():
    payload = {"list": [
        {"prodCat": "水产", "prodName": "草鱼", "specInfo": "750g-1000g", "place": "",
         "lowPrice": "7.8", "avgPrice": "7.9", "highPrice": "8.0", "unitInfo": "斤",
         "pubDate": "2026-09-29 00:00:00"},
        {"prodCat": "水果", "prodName": "菠萝", "specInfo": "", "place": "",
         "lowPrice": "2.8", "avgPrice": "2.9", "highPrice": "3.0", "unitInfo": "",
         "pubDate": "2026-09-29 00:00:00"},
    ]}
    rows = parse_xinfadi(payload, date(2026, 9, 29))
    assert rows[0].price_avg_yuan_per_kg == Decimal("15.8")
    assert rows[0].specification == "750g-1000g"
    assert rows[1].price_avg_yuan_per_kg is None
    assert rows[1].quality_flag == "missing_unit"


def test_parse_wuhan_preserves_reported_bulk_and_range():
    html = """<h1>9月28日武汉四季美市场蔬菜批发价格</h1>
    <table><tr><td>市场名称</td><td>蔬菜名称</td><td>最高价</td><td>最低价</td><td>大宗价</td><td>上报时间</td></tr>
    <tr><td>四季美</td><td>西红柿</td><td>4.6</td><td>3.2</td><td>3.9</td><td>2026/9/28</td></tr></table>"""
    rows = parse_wuhan(html, "蔬菜", date(2026, 9, 28), "https://nyncj.wuhan.gov.cn/example")
    assert len(rows) == 1
    assert rows[0].price_min == Decimal("3.2")
    assert rows[0].price_avg == Decimal("3.9")
    assert rows[0].price_max == Decimal("4.6")


def test_parse_wuhan_accepts_unit_suffix_in_live_header():
    html = """<table><tr><td>市场名称</td><td>水产名称</td><td>最高价 (元/公斤)</td>
    <td>最低价 (元/公斤)</td><td>上报时间</td></tr>
    <tr><td>白沙洲</td><td>鲈鱼</td><td>22</td><td>21</td><td>2026/9/28</td></tr></table>"""
    rows = parse_wuhan(html, "水产", date(2026, 9, 28), "https://example.com")
    assert len(rows) == 1
    assert rows[0].price_min == Decimal("21")


class _Sheet:
    def __init__(self, name, rows):
        self.name, self.rows, self.nrows = name, rows, len(rows)

    def row_values(self, index):
        return self.rows[index]


class _Workbook:
    def __init__(self, sheets):
        self._sheets = sheets

    def sheets(self):
        return self._sheets


def test_guangzhou_chooses_matching_sheet_and_skips_bad_price():
    old = _Sheet("旧年", [["天平水果市场行情分析（9月12日—9月18日）"], ["品名", "单位", "批发价"], ["旧品", "元/公斤", 1]])
    current = _Sheet("2026年", [
        ["天平水果市场行情分析（9月12日—9月18日）"],
        ["价格基本持平的产品"], ["品名", "单位", "批发价"],
        ["青提", "元/公斤", 12], ["坏数据", "元/公斤", "13..5"],
        ["价格上升幅度较大的产品"], ["品名", "单位", "最低价", "最高价"],
        ["黑美人西瓜", "元/公斤", 3, 4.4],
    ])
    rows = parse_guangzhou_workbook(
        _Workbook([old, current]), "水果", "天平水果市场", date(2026, 9, 12),
        date(2026, 9, 18), "https://nyncj.gz.gov.cn/example",
    )
    assert [row.commodity for row in rows] == ["青提", "黑美人西瓜"]
    assert rows[1].price_min == Decimal("3")
    assert rows[1].price_avg is None
    assert rows[1].period_start == date(2026, 9, 12)


def test_guangzhou_accepts_shifted_columns_in_xls():
    book = _Workbook([_Sheet("Sheet1", [
        ["", "天平水果市场行情分析（9月12日—9月18日）"],
        ["", "品名", "产地", "单位", "批发价"],
        ["", "青提", "国产", "元/公斤", 12],
    ])])
    rows = parse_guangzhou_workbook(book, "水果", "天平水果市场", date(2026, 9, 12),
                                   date(2026, 9, 18), "https://example.com")
    assert len(rows) == 1
    assert rows[0].price_avg == Decimal("12")


def test_moa_reports_keep_national_and_milk_price_types():
    daily = "全国农产品批发市场猪肉平均价格为16.24元/公斤。重点监测的28种蔬菜平均价格为4.35元/公斤。"
    rows = parse_moa_daily(daily, date(2026, 9, 29), "https://scs.moa.gov.cn/example")
    assert {(r.commodity, r.price_avg) for r in rows} == {
        ("猪肉", Decimal("16.24")), ("28种蔬菜", Decimal("4.35"))
    }
    assert all(r.quote_type == "national_wholesale_mean" for r in rows)
    milk = "9月第4周（采集日为9月24日）生鲜乳价格。内蒙古、河北等10个主产省份生鲜乳平均价格3.09元/公斤。"
    milk_rows = parse_moa_milk(milk, date(2026, 9, 30), "https://xmsyj.moa.gov.cn/example")
    assert milk_rows[0].observed_date == date(2026, 9, 24)
    assert milk_rows[0].quote_type == "producer_raw_milk"


def test_upsert_is_idempotent_and_updates_corrected_price():
    engine = create_engine("sqlite:///:memory:")
    MarketPriceObservation.__table__.create(engine)
    html = """<h1>2026-09-28西红柿批发价格行情</h1><table id="goaler">
    <tr><td>地区</td><td>市场</td><td>当日价格</td></tr>
    <tr><td>河南省</td><td>河南万邦市场</td><td>4.11</td></tr></table>"""
    corrected = html.replace("4.11", "4.12")
    with Session(engine) as session:
        assert upsert_observations(session, parse_mofcom(html, "西红柿", date(2026, 9, 28), "https://example.com")) == (1, 0)
        assert upsert_observations(session, parse_mofcom(corrected, "西红柿", date(2026, 9, 28), "https://example.com")) == (0, 1)
        saved = session.scalar(select(MarketPriceObservation))
        assert saved.price_avg == Decimal("4.12")
        assert session.query(MarketPriceObservation).count() == 1


def test_cli_defaults_to_jsonl_without_database_write(monkeypatch, capsys):
    from scripts import collect_market_prices as command
    rows = parse_mofcom("""<table id="goaler"><tr><td>地区</td><td>市场</td><td>当日价格</td></tr>
        <tr><td>河南省</td><td>万邦</td><td>4.11</td></tr></table>""",
                        "西红柿", date(2026, 9, 28), "https://example.com")
    monkeypatch.setitem(command.COLLECTORS, "mofcom", lambda day: rows)
    assert command.main(["--source", "mofcom", "--date", "2026-09-28"]) == 0
    output = capsys.readouterr()
    assert '"commodity": "西红柿"' in output.out
    assert "database:" not in output.err

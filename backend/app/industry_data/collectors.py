"""Bounded parsers for official statistics. No database or network side effects."""
from datetime import date
from decimal import Decimal
import re

from bs4 import BeautifulSoup

from .types import IndustryObservation as Row

PROVINCES = {
    "北京": "北京市", "天津": "天津市", "河北": "河北省", "山西": "山西省",
    "内蒙古": "内蒙古自治区", "辽宁": "辽宁省", "吉林": "吉林省",
    "黑龙江": "黑龙江省", "上海": "上海市", "江苏": "江苏省", "浙江": "浙江省",
    "安徽": "安徽省", "福建": "福建省", "江西": "江西省", "山东": "山东省",
    "河南": "河南省", "湖北": "湖北省", "湖南": "湖南省", "广东": "广东省",
    "广西": "广西壮族自治区", "海南": "海南省", "重庆": "重庆市", "四川": "四川省",
    "贵州": "贵州省", "云南": "云南省", "西藏": "西藏自治区", "陕西": "陕西省",
    "甘肃": "甘肃省", "青海": "青海省", "宁夏": "宁夏回族自治区",
    "新疆": "新疆维吾尔自治区", "全国总计": "全国",
}


def plain_text(html: str) -> str:
    """Remove navigation scripts and normalize inline footnote numbers."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["script", "style", "sup"]):
        tag.decompose()
    return re.sub(r"\s+", "", soup.get_text())


def parse_grain(html: str, year: int, url: str) -> list[Row]:
    """Parse the provincial total-grain table; fail on incomplete coverage."""
    soup = BeautifulSoup(html, "html.parser")
    selected: dict[str, list[str]] = {}
    for table in soup.find_all("table"):
        content = table.get_text()
        if "播种面积" not in content or "千公顷" not in content or "总产量" not in content:
            continue
        for tr in table.find_all("tr"):
            cells = [re.sub(r"\s+", "", c.get_text()) for c in tr.find_all(["td", "th"])]
            if len(cells) != 4 or cells[0] not in PROVINCES:
                continue
            if any(not re.fullmatch(r"\d+(?:\.\d+)?", n) for n in cells[1:]):
                raise ValueError(f"Invalid grain values for {cells[0]}")
            if cells[0] in selected and selected[cells[0]] != cells:
                raise ValueError(f"Conflicting duplicated grain row: {cells[0]}")
            selected[cells[0]] = cells
    if set(selected) != set(PROVINCES):
        raise ValueError(f"Incomplete grain table: expected 31 provinces + national, got {len(selected)}")
    metrics = [
        ("grain_area", "粮食播种面积", "千公顷", "sown_area"),
        ("grain_production", "粮食产量", "万吨", "annual_flow"),
        ("grain_yield", "粮食单位面积产量", "公斤/公顷", "rate"),
    ]
    return [Row("nbs_grain", url, code, label, PROVINCES[name], "粮食",
                date(year, 1, 1), date(year, 12, 31), "annual", Decimal(cells[i + 1]),
                unit, kind, " | ".join(cells))
            for name, cells in selected.items()
            for i, (code, label, unit, kind) in enumerate(metrics)]


def parse_agricultural_credit(html: str, year: int, quarter: int, url: str) -> list[Row]:
    """Extract four overlapping balances and their separately reported growth rates."""
    text = plain_text(html)
    month = quarter * 3
    if quarter not in (1, 2, 3, 4):
        raise ValueError("Invalid quarter")
    end = date(year, month, 31 if month in (3, 12) else 30)
    prefix = f"{year}年"
    if prefix not in text:
        raise ValueError("Credit report year does not match requested year")
    # Scope extraction to the agricultural section, avoiding household totals elsewhere.
    section = re.search(r"[五四六七]、涉农贷款(.+?)(?:[六七八]、|注[123])", text)
    if not section:
        raise ValueError("Agricultural credit section not found")
    content = section.group(1)
    patterns = [
        ("agricultural_related_credit", "涉农贷款余额", r"本外币涉农贷款(?:\d)?余额"),
        ("rural_credit", "农村贷款余额", r"农村贷款余额"),
        ("farm_household_credit", "农户贷款余额", r"农户贷款余额"),
        ("agriculture_credit", "农业贷款余额", r"农业贷款余额"),
    ]
    rows = []
    for code, label, pattern in patterns:
        match = re.search(pattern + r"([\d.]+)万亿元，同比增长([\d.]+)%", content)
        if not match:
            raise ValueError(f"Missing credit metric: {label}")
        rows.append(Row("pbc_credit", url, code, label, "全国", "涉农金融",
                        end, end, "quarterly", Decimal(match[1]), "万亿元", "balance",
                        match[0], yoy_percent=Decimal(match[2])))
    return rows


def parse_fisheries(html: str, year: int, url: str) -> list[Row]:
    """Capture nationwide area and output, preserving different dimensions."""
    text = plain_text(html)
    patterns = [
        ("aquaculture_area", "水产养殖面积", r"全国水产养殖面积([\d.]+)千公顷", "千公顷", "area"),
        ("marine_aquaculture_area", "海水养殖面积", r"海水养殖面积([\d.]+)千公顷", "千公顷", "area"),
        ("freshwater_aquaculture_area", "淡水养殖面积", r"淡水养殖面积([\d.]+)千公顷", "千公顷", "area"),
        ("aquatic_production", "水产品总产量", r"全国水产品总产量([\d.]+)万吨", "万吨", "annual_flow"),
        ("aquaculture_production", "水产养殖产量", r"其中，养殖产量([\d.]+)万吨", "万吨", "annual_flow"),
    ]
    if f"{year}年" not in text:
        raise ValueError("Fisheries report year mismatch")
    rows = []
    for code, label, pattern, unit, kind in patterns:
        match = re.search(pattern, text)
        if not match:
            raise ValueError(f"Missing fisheries metric: {label}")
        rows.append(Row("moa_fisheries", url, code, label, "全国", "水产",
                        date(year, 1, 1), date(year, 12, 31), "annual", Decimal(match[1]),
                        unit, kind, match[0]))
    return rows


def parse_insurance_subsidy(html: str, year: int, url: str) -> list[Row]:
    """Preserve exact subsidy and lower-bound insurance disclosures."""
    text = plain_text(html)
    section = re.search(rf"{year}年，中央财政拨付农业保险保费补贴(.+?)亿元。", text)
    if not section:
        raise ValueError("Agricultural insurance fiscal section not found")
    evidence = section.group(0)
    specs = [
        ("agri_insurance_subsidy", "中央农业保险保费补贴", r"保费补贴([\d.]+)亿元", "亿元", "exact"),
        ("agri_insurance_premium", "农业保险保费规模", r"保费规模超([\d.]+)亿元", "亿元", "gt"),
        ("agri_insurance_coverage", "农业保险风险保障金额", r"风险保障超([\d.]+)万亿元", "万亿元", "gt"),
        ("agri_insurance_claims", "农业保险赔款", r"支付赔款超([\d.]+)亿元", "亿元", "gt"),
    ]
    rows = []
    for code, label, pattern, unit, qualifier in specs:
        match = re.search(pattern, evidence)
        if not match:
            raise ValueError(f"Missing fiscal metric: {label}")
        rows.append(Row("mof_agri_insurance", url, code, label, "全国", "农业保险",
                        date(year, 1, 1), date(year, 12, 31), "annual", Decimal(match[1]),
                        unit, "annual_flow", evidence, qualifier))
    return rows

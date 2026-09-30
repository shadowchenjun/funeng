"""Parsers for public market reports. Network access is kept in fetch.py."""
from datetime import date
import re

from bs4 import BeautifulSoup

from .types import MarketObservation as Row, decimal_or_none as dec


def _text(cell):
    return cell.get_text(" ", strip=True)


def _category(value):
    value = str(value)
    if any(token in value for token in ("鱼", "虾", "蟹", "水产", "贝")):
        return "水产"
    if any(token in value for token in ("肉", "禽", "蛋", "鸡", "鸭", "牛", "羊", "猪")):
        return "肉蛋禽"
    if any(token in value for token in ("水果", "果", "瓜")):
        return "水果"
    return "蔬菜"


def parse_mofcom(html, commodity, day, url):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="goaler")
    if table is None:
        raise ValueError("MOFCOM price table not found")
    result = []
    for index, tr in enumerate(table.find_all("tr")):
        cells = [_text(c) for c in tr.find_all(["td", "th"])]
        if len(cells) < 3 or index == 0:
            continue
        price = dec(cells[2])
        if price is None:
            continue
        result.append(Row("mofcom", url, cells[1], _category(commodity), commodity, day,
                          "market_wholesale", "元/公斤", province=cells[0], price_avg=price,
                          source_row_key=str(index)))
    return result


def parse_xinfadi(payload, day):
    result = []
    for index, item in enumerate(payload.get("list", [])):
        commodity = str(item.get("prodName") or "").strip()
        if not commodity:
            continue
        raw_day = str(item.get("pubDate") or "")[:10]
        observed = date.fromisoformat(raw_day) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_day) else day
        low, avg, high = (dec(item.get(field)) for field in ("lowPrice", "avgPrice", "highPrice"))
        if all(value is None for value in (low, avg, high)):
            continue
        result.append(Row("xinfadi", "http://www.xinfadi.com.cn/priceDetail.html",
                          "北京新发地", _category(item.get("prodPcat") or item.get("prodCat") or commodity),
                          commodity, observed, "market_wholesale", str(item.get("unitInfo") or ""),
                          province="北京市", specification=str(item.get("specInfo") or ""),
                          origin=str(item.get("place") or ""), price_min=low, price_avg=avg,
                          price_max=high, source_row_key=str(item.get("id") or index)))
    return result


def parse_wuhan(html, category, day, url):
    soup = BeautifulSoup(html, "html.parser")
    result = []
    for table in soup.find_all("table"):
        trs = table.find_all("tr")
        if not trs:
            continue
        headers = [_text(c).split(" ")[0] for c in trs[0].find_all(["td", "th"])]
        if "市场名称" not in headers or not any("价" in h for h in headers):
            continue
        for index, tr in enumerate(trs[1:], start=1):
            cells = [_text(c) for c in tr.find_all(["td", "th"])]
            if len(cells) < len(headers):
                continue
            data = dict(zip(headers, cells))
            name = data.get("蔬菜名称") or data.get("水产名称") or data.get("产品名称")
            if not name:
                continue
            low, avg, high = (dec(data.get(field)) for field in ("最低价", "大宗价", "最高价"))
            if all(value is None for value in (low, avg, high)):
                continue
            raw_date = data.get("上报时间", "")
            found = re.search(r"(20\d{2})[/-](\d{1,2})[/-](\d{1,2})", raw_date)
            observed = date(*map(int, found.groups())) if found else day
            result.append(Row("wuhan", url, data["市场名称"], category, name, observed,
                              "market_wholesale", "元/公斤", province="湖北省",
                              specification=data.get("等级规格", ""), price_min=low,
                              price_avg=avg, price_max=high, source_row_key=str(index)))
    if not result:
        raise ValueError("Wuhan price rows not found")
    return result


def parse_guangzhou_workbook(workbook, category, market, period_start, period_end, url):
    sheets = workbook.sheets()
    current = [sheet for sheet in sheets if sheet.nrows and
               (str(period_start.year) in sheet.name or str(period_start.year)[-2:] in sheet.name)]
    if not current:
        current = [sheet for sheet in sheets if sheet.nrows and any(
            f"{period_start.month}月{period_start.day}日" in str(cell)
            for cell in sheet.row_values(0))]
    if not current:
        raise ValueError("Guangzhou workbook has no matching period sheet")
    sheet = current[-1]
    result = []
    headers = []
    for index in range(sheet.nrows):
        cells = [str(value).strip() for value in sheet.row_values(index)]
        while cells and not cells[0]:
            cells.pop(0)
        if "品名" in cells and "单位" in cells:
            headers = cells
            continue
        if not headers or not cells or not cells[0] or cells[0].startswith("价格"):
            continue
        mapped = dict(zip(headers, cells))
        name = mapped.get("品名", "")
        if not name:
            continue
        low = dec(mapped.get("最低价"))
        high = dec(mapped.get("最高价"))
        avg = dec(mapped.get("批发价"))
        if all(value is None for value in (low, avg, high)):
            continue
        result.append(Row("guangzhou", url, market, category, name, period_end,
                          "market_weekly", mapped.get("单位", ""), province="广东省",
                          period_start=period_start, period_end=period_end, price_min=low,
                          price_avg=avg, price_max=high, source_row_key=str(index)))
    return result


_DAILY_PATTERNS = [
    ("猪肉", "肉蛋禽", r"猪肉平均价格(?:为)?\s*([\d.]+)\s*元/公斤"),
    ("牛肉", "肉蛋禽", r"牛肉(?:平均价格为)?\s*([\d.]+)\s*元/公斤"),
    ("羊肉", "肉蛋禽", r"羊肉(?:平均价格为)?\s*([\d.]+)\s*元/公斤"),
    ("鸡蛋", "肉蛋禽", r"鸡蛋(?:平均价格为)?\s*([\d.]+)\s*元/公斤"),
    ("白条鸡", "肉蛋禽", r"白条鸡(?:平均价格为)?\s*([\d.]+)\s*元/公斤"),
    ("28种蔬菜", "蔬菜", r"28种蔬菜平均价格(?:为)?\s*([\d.]+)\s*元/公斤"),
    ("6种水果", "水果", r"6种水果平均价格(?:为)?\s*([\d.]+)\s*元/公斤"),
    ("鲫鱼", "水产", r"鲫鱼(?:平均价格为)?\s*([\d.]+)\s*元/公斤"),
    ("鲤鱼", "水产", r"鲤鱼(?:平均价格为)?\s*([\d.]+)\s*元/公斤"),
    ("白鲢鱼", "水产", r"白鲢鱼(?:平均价格为)?\s*([\d.]+)\s*元/公斤"),
    ("大带鱼", "水产", r"大带鱼(?:平均价格为)?\s*([\d.]+)\s*元/公斤"),
]


def parse_moa_daily(text, day, url):
    result = []
    for commodity, category, pattern in _DAILY_PATTERNS:
        match = re.search(pattern, text)
        if match and (price := dec(match.group(1))) is not None:
            result.append(Row("moa_daily", url, "全国农产品批发市场", category, commodity,
                              day, "national_wholesale_mean", "元/公斤", price_avg=price))
    return result


def parse_moa_milk(text, published, url):
    text = re.sub(r"\s+", "", text)
    observed = published
    match = re.search(r"采集日为(\d{1,2})月(\d{1,2})日", text)
    if match:
        observed = date(published.year, int(match.group(1)), int(match.group(2)))
    match = re.search(r"生鲜乳平均价格(?:为)?\s*([\d.]+)\s*元/公斤", text)
    price = dec(match.group(1)) if match else None
    return [Row("moa_milk", url, "10个主产省份", "奶", "生鲜乳", observed,
                "producer_raw_milk", "元/公斤", price_avg=price)] if price is not None else []

"""Bounded collection from public publisher pages; no access-control bypass."""
from datetime import date
import re
import subprocess
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests
import xlrd

from .collectors import (parse_guangzhou_workbook, parse_moa_daily, parse_moa_milk,
                         parse_mofcom, parse_wuhan, parse_xinfadi)

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0 (compatible; FunengMarketData/0.1)"})
TIMEOUT = 15


def _get(url):
    response = SESSION.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response


def _matching_links(index_url, pattern, max_links=5):
    soup = BeautifulSoup(_get(index_url).text, "html.parser")
    found = []
    for a in soup.find_all("a", href=True):
        label = a.get_text(" ", strip=True)
        if pattern.search(label):
            url = urljoin(index_url, a["href"])
            if urlparse(url).hostname == urlparse(index_url).hostname and url not in found:
                found.append(url)
        if len(found) >= max_links:
            break
    return found


MOFCOM_COMMODITIES = {"170120": "西红柿", "170130": "黄瓜", "130010": "白条猪",
                      "280020": "白条鸡", "150010": "鸡蛋"}


def collect_mofcom(day):
    result = []
    for code, commodity in MOFCOM_COMMODITIES.items():
        url = f"https://cif.mofcom.gov.cn/cif/seach.fhtml?commdityid={code}"
        # This publisher currently rejects Python's TLS handshake; system curl
        # verifies TLS normally and is bounded in both time and response size.
        body = subprocess.run(["curl", "--fail", "--silent", "--show-error", "--location",
                               "--max-time", "15", "--max-filesize", "4000000", "--data",
                               f"searchDate={day.isoformat()}", url], capture_output=True,
                              check=True, timeout=18).stdout
        result.extend(parse_mofcom(body.decode("utf-8", errors="replace"), commodity, day, url))
    return result


XINFADI_CATEGORIES = ("1186", "1187", "1189", "1190")


def collect_xinfadi(day):
    result = []
    for cat in XINFADI_CATEGORIES:
        for page in range(1, 11):
            response = SESSION.post("http://www.xinfadi.com.cn/getPriceData.html", data={
                "limit": 100, "current": page, "pubDateStartTime": day.isoformat(),
                "pubDateEndTime": day.isoformat(), "prodPcatid": cat, "prodCatid": "",
                "prodName": ""}, timeout=TIMEOUT)
            response.raise_for_status()
            payload = response.json()
            result.extend(parse_xinfadi(payload, day))
            if page * 100 >= int(payload.get("count", 0)):
                break
    return result


WUHAN_INDEX = "https://nyncj.wuhan.gov.cn/zwgk_25/fdzdgknr/snsj/"


def collect_wuhan(day):
    result = []
    label = re.compile(rf"{day.month}月{day.day}日.*(?:蔬菜|水产).*批发价格")
    for path, category in (("scpfjg/", "蔬菜"), ("scppfjg/", "水产")):
        for url in _matching_links(urljoin(WUHAN_INDEX, path), label, max_links=4):
            result.extend(parse_wuhan(_get(url).text, category, day, url))
    return result


GUANGZHOU_INDEX = "https://nyncj.gz.gov.cn/fw/sjfb/gzscxq/"
GUANGZHOU_MARKETS = (("天平水果", "水果"), ("黄沙水产", "水产"), ("江村家禽", "肉蛋禽"))


def collect_guangzhou(day):
    # Weekly reports: day selects a week-ending article, not a daily price.
    soup = BeautifulSoup(_get(GUANGZHOU_INDEX).text, "html.parser")
    result = []
    for market, category in GUANGZHOU_MARKETS:
        links = [(a.get_text(" ", strip=True), urljoin(GUANGZHOU_INDEX, a["href"]))
                 for a in soup.find_all("a", href=True) if market in a.get_text(" ", strip=True)]
        chosen = []
        for label, url in links:
            match = re.search(r"(\d{1,2})月(\d{1,2})日\s*[—–-]\s*(\d{1,2})月(\d{1,2})日", label)
            if not match:
                continue
            sm, sd, em, ed = map(int, match.groups())
            start, end = date(day.year, sm, sd), date(day.year, em, ed)
            if end != day:
                continue
            chosen.append((url, start, end))
        for article_url, start, end in chosen[:1]:
            article = BeautifulSoup(_get(article_url).text, "html.parser")
            attachments = [urljoin(article_url, a["href"]) for a in article.find_all("a", href=True)
                           if a["href"].lower().endswith(".xls")]
            if not attachments:
                raise ValueError(f"Guangzhou XLS not found: {article_url}")
            attachment = attachments[0]
            workbook = xlrd.open_workbook(file_contents=_get(attachment).content)
            result.extend(parse_guangzhou_workbook(workbook, category, market, start, end, attachment))
    return result


def collect_moa_daily(day):
    index = "https://scs.moa.gov.cn/jcyj/"
    pattern = re.compile(rf"{day.month}月{day.day}日.*农产品批发价格200指数")
    urls = _matching_links(index, pattern, max_links=1)
    if not urls:
        return []
    text = BeautifulSoup(_get(urls[0]).text, "html.parser").get_text(" ", strip=True)
    return parse_moa_daily(text, day, urls[0])


def collect_moa_milk(day):
    index = "https://xmsyj.moa.gov.cn/jcyj/"
    pattern = re.compile(r"畜产品和饲料集贸市场价格情况")
    for url in _matching_links(index, pattern, max_links=8):
        if day.strftime("%Y%m%d") not in url:
            continue
        text = BeautifulSoup(_get(url).text, "html.parser").get_text(" ", strip=True)
        return parse_moa_milk(text, day, url)
    return []


COLLECTORS = {"mofcom": collect_mofcom, "xinfadi": collect_xinfadi,
              "wuhan": collect_wuhan, "guangzhou": collect_guangzhou,
              "moa_daily": collect_moa_daily, "moa_milk": collect_moa_milk}

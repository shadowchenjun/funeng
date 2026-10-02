"""Bounded collection from public publisher pages; no access-control bypass."""
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import date, timedelta
import re
import subprocess
import time
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests
import xlrd

from .collectors import (parse_guangzhou_workbook, parse_moa_daily, parse_moa_milk,
                         parse_mofcom, parse_wuhan, parse_xinfadi)

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0 (compatible; FunengMarketData/0.1)"})
TIMEOUT = 15
_DEADLINE = ContextVar('market_deadline', default=None)
_SESSION = ContextVar('market_session', default=None)


@contextmanager
def collection_budget(seconds):
    """Per-invocation state, without sharing sessions across concurrent jobs."""
    session = requests.Session()
    session.headers.update(SESSION.headers)
    deadline_token = _DEADLINE.set(time.monotonic() + seconds)
    session_token = _SESSION.set(session)
    try:
        yield
    finally:
        session.close()
        _SESSION.reset(session_token)
        _DEADLINE.reset(deadline_token)


def _remaining():
    deadline = _DEADLINE.get()
    remaining = deadline - time.monotonic() if deadline is not None else TIMEOUT
    if remaining <= 0:
        raise TimeoutError('Market collection budget exceeded')
    return min(TIMEOUT, remaining)


def _request(method, url, **kwargs):
    for attempt in range(2):
        try:
            timeout = _remaining()
            response = (_SESSION.get() or SESSION).request(
                method, url, timeout=(min(5, timeout), timeout), stream=True, **kwargs)
            with response:
                response.raise_for_status()
                chunks, size = [], 0
                for chunk in response.iter_content(65536):
                    _remaining()
                    size += len(chunk)
                    if size > 4_000_000:
                        raise ValueError('Publisher response exceeds size limit')
                    chunks.append(chunk)
                response._content = b''.join(chunks)
                response._content_consumed = True
                return response
        except (requests.ConnectionError, requests.Timeout):
            if attempt:
                raise
        except requests.HTTPError as exc:
            if attempt or exc.response.status_code < 500:
                raise


def _get(url):
    response = _request('GET', url)
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


def _published_day(url):
    match = re.search(r'/t(\d{8})_', url)
    return date(int(match[1][:4]), int(match[1][4:6]), int(match[1][6:])) if match else None


MOFCOM_COMMODITIES = {"170120": "西红柿", "170130": "黄瓜", "130010": "白条猪",
                      "280020": "白条鸡", "150010": "鸡蛋"}


def collect_mofcom(day):
    result = []
    for code, commodity in MOFCOM_COMMODITIES.items():
        url = f"https://cif.mofcom.gov.cn/cif/seach.fhtml?commdityid={code}"
        # This publisher currently rejects Python's TLS handshake; system curl
        # verifies TLS normally and is bounded in both time and response size.
        timeout = _remaining()
        body = subprocess.run(["curl", "--fail", "--silent", "--show-error", "--location",
                               "--max-time", str(timeout), "--max-filesize", "4000000", "--data",
                               f"searchDate={day.isoformat()}", url], capture_output=True,
                              check=True, timeout=timeout + 2).stdout
        html = body.decode('utf-8', errors='replace')
        reported = BeautifulSoup(html, 'html.parser').find('input', attrs={'name': 'searchDate'})
        if reported is None or not reported.get('value'):
            raise ValueError('MOFCOM reported date missing')
        # On holidays this site silently returns the latest published date even
        # after a requested searchDate. Never stamp that old price as today's.
        if date.fromisoformat(reported['value']) != day:
            continue
        result.extend(parse_mofcom(html, commodity, day, url))
    return result


XINFADI_CATEGORIES = ("1186", "1187", "1189", "1190")


def collect_xinfadi(day):
    result = []
    for cat in XINFADI_CATEGORIES:
        for page in range(1, 11):
            response = _request('POST', "http://www.xinfadi.com.cn/getPriceData.html", data={
                "limit": 100, "current": page, "pubDateStartTime": day.isoformat(),
                "pubDateEndTime": day.isoformat(), "prodPcatid": cat, "prodCatid": "",
                "prodName": ""})
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
            published = _published_day(url)
            if published and published.year != day.year:
                continue
            result.extend(parse_wuhan(_get(url).text, category, day, url))
    return result


GUANGZHOU_INDEX = "https://nyncj.gz.gov.cn/fw/sjfb/gzscxq/"
GUANGZHOU_MARKETS = (("天平水果", "水果"), ("黄沙水产", "水产"), ("江村家禽", "肉蛋禽"))


def collect_guangzhou(day, *, latest=False):
    # Weekly reports: day selects a week-ending article, not a daily price.
    soup = BeautifulSoup(_get(GUANGZHOU_INDEX).text, "html.parser")
    result = []
    for market, category in GUANGZHOU_MARKETS:
        links = [(a.get_text(" ", strip=True), urljoin(GUANGZHOU_INDEX, a["href"]),
                  a.parent.get_text(' ', strip=True))
                 for a in soup.find_all("a", href=True) if market in a.get_text(" ", strip=True)]
        chosen = []
        for label, url, surrounding in links:
            match = re.search(r"(\d{1,2})月(\d{1,2})日\s*[—–-]\s*(\d{1,2})月(\d{1,2})日", label)
            if not match:
                continue
            sm, sd, em, ed = map(int, match.groups())
            published = re.search(r'(20\d{2})[-/](\d{1,2})[-/](\d{1,2})', surrounding)
            if latest and not published:
                continue
            year = int(published[1]) if published else day.year
            start, end = date(year, sm, sd), date(year, em, ed)
            if start > end:
                start = date(year - 1, sm, sd)
            if (not latest and end != day) or (latest and not day - timedelta(days=21) <= end <= day):
                continue
            if urlparse(url).hostname != urlparse(GUANGZHOU_INDEX).hostname:
                continue
            chosen.append((url.replace('http://', 'https://', 1), start, end))
        for article_url, start, end in chosen[:1]:
            article = BeautifulSoup(_get(article_url).text, "html.parser")
            attachments = [urljoin(article_url, a["href"]) for a in article.find_all("a", href=True)
                           if a["href"].lower().endswith(".xls")]
            if not attachments:
                raise ValueError(f"Guangzhou XLS not found: {article_url}")
            attachment = attachments[0].replace('http://', 'https://', 1)
            workbook = xlrd.open_workbook(file_contents=_get(attachment).content)
            result.extend(parse_guangzhou_workbook(workbook, category, market, start, end, attachment))
    return result


def collect_moa_daily(day):
    index = "https://scs.moa.gov.cn/jcyj/"
    pattern = re.compile(rf"{day.month}月{day.day}日.*农产品批发价格200指数")
    urls = _matching_links(index, pattern, max_links=1)
    if not urls or _published_day(urls[0]) != day:
        return []
    text = BeautifulSoup(_get(urls[0]).text, "html.parser").get_text(" ", strip=True)
    return parse_moa_daily(text, day, urls[0])


def collect_moa_milk(day, *, latest=False):
    index = "https://xmsyj.moa.gov.cn/jcyj/"
    pattern = re.compile(r"畜产品和饲料集贸市场价格情况")
    for url in _matching_links(index, pattern, max_links=8):
        published = day
        if latest:
            match = re.search(r'/t(\d{8})_', url)
            if not match:
                continue
            published = date(int(match[1][:4]), int(match[1][4:6]), int(match[1][6:]))
            if not day - timedelta(days=21) <= published <= day:
                continue
        elif day.strftime("%Y%m%d") not in url:
            continue
        text = BeautifulSoup(_get(url).text, "html.parser").get_text(" ", strip=True)
        return parse_moa_milk(text, published, url)
    return []


COLLECTORS = {"mofcom": collect_mofcom, "xinfadi": collect_xinfadi,
              "wuhan": collect_wuhan, "guangzhou": collect_guangzhou,
              "moa_daily": collect_moa_daily, "moa_milk": collect_moa_milk}

"""Official release registry and single-request collectors; no scheduler installed."""
from collections.abc import Callable
from datetime import datetime, timezone

import requests

from .collectors import (parse_agricultural_credit, parse_fisheries,
                         parse_grain, parse_insurance_subsidy)
from .types import IndustryObservation

SOURCES = {
    "nbs_grain": {"name": "国家统计局粮食产量公告", "year": 2025,
                  "url": "https://www.stats.gov.cn/sj/zxfb/202512/t20251212_1962049.html"},
    "pbc_credit": {"name": "人民银行贷款投向报告", "year": 2025, "quarter": 4,
                   "url": "https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/2026012715000280533/index.html"},
    "moa_fisheries": {"name": "农业农村部渔业统计公报", "year": 2025,
                      "url": "https://yyj.moa.gov.cn/gzdt/202607/t20260727_6486230.htm"},
    "mof_agri_insurance": {"name": "财政部财政政策执行报告", "year": 2025,
                           "url": "https://www.mof.gov.cn/zhengwuxinxi/caizhengxinwen/202603/t20260317_3985436.htm"},
}

PARSERS: dict[str, Callable] = {
    "nbs_grain": parse_grain, "pbc_credit": parse_agricultural_credit,
    "moa_fisheries": parse_fisheries, "mof_agri_insurance": parse_insurance_subsidy,
}


def collect_source(source_id: str) -> tuple[list[IndustryObservation], dict]:
    """Fetch one pinned release and return provenance; updates require a new release."""
    source = SOURCES[source_id]
    response = requests.get(source["url"], timeout=(5, 20),
                            headers={"User-Agent": "FunengIndustryResearch/1.0"})
    response.raise_for_status()
    # The releases use UTF-8; requests otherwise assumes ISO-8859-1 for some pages.
    html = response.content.decode("utf-8-sig")
    args = [html, source["year"]]
    if source_id == "pbc_credit":
        args.append(source["quarter"])
    rows = PARSERS[source_id](*args, source["url"])
    metadata = {**source, "source_id": source_id, "record_count": len(rows),
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "status": "collected", "release_policy": "pinned_official_release"}
    return rows, metadata

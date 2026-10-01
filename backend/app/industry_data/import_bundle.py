"""Validate reviewed snapshots and prepare parameter-bound Postgres imports."""
import base64
from collections import Counter
from datetime import date
from decimal import Decimal
from hashlib import md5, sha256
import json
from pathlib import Path
from urllib.parse import urlparse

from app.market_data.persistence import FIELDS as PRICE_FIELDS
from app.market_data.types import MarketObservation
from .types import IndustryObservation

VERSION = 1
PRICE_COLUMNS = {"external_key": "text", **{k: "text" for k in PRICE_FIELDS}}
for field in ("observed_date", "period_start", "period_end"):
    PRICE_COLUMNS[field] = "date"
for field in PRICE_COLUMNS:
    if field.startswith("price_"):
        PRICE_COLUMNS[field] = "numeric"

TABLE_COLUMNS = {
    "agri_data_sources": {k: "text" for k in
                          ("source_id", "name", "domain", "source_url", "status", "coverage")},
    "market_price_observations": PRICE_COLUMNS,
    "industry_observations": {k: "text" for k in
        ("external_key", "source_id", "source_url", "metric", "metric_name", "region",
         "category", "frequency", "unit", "measure_type", "qualifier", "evidence", "review_status")},
    "cold_chain_reference_nodes": {k: "text" for k in
        ("external_key", "source_id", "source_url", "name", "province", "city", "reported", "scope")},
    "agri_data_import_runs": {"snapshot_sha256": "text", "status": "text", "manifest": "jsonb"},
}
TABLE_COLUMNS["agri_data_sources"]["metadata"] = "jsonb"
TABLE_COLUMNS["industry_observations"].update(
    value="numeric", yoy_percent="numeric", period_start="date", period_end="date")
TABLE_COLUMNS["cold_chain_reference_nodes"]["snapshot_date"] = "date"
KEYS = {table: "external_key" for table in TABLE_COLUMNS}
KEYS.update(agri_data_sources="source_id", agri_data_import_runs="snapshot_sha256")


def check_url(value: str) -> None:
    """Only accept explicit HTTP sources, never silently synthesize a URL."""
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Invalid source URL")


def deduplicate(rows: list[dict], key: str) -> tuple[list[dict], int]:
    """Identical snapshots collapse; conflicting evidence must be reviewed."""
    seen = {}
    for row in rows:
        identity = row[key]
        if identity in seen and seen[identity] != row:
            raise ValueError(f"Conflicting snapshot identity: {identity}")
        seen[identity] = row
    return list(seen.values()), len(rows) - len(seen)


def normalize_price(row: dict) -> dict:
    """Reconstruct the collector record to detect tampered units, dates and IDs."""
    args = {key: row[key] for key in MarketObservation.__dataclass_fields__
            if key != "external_key"}
    for key in ("observed_date", "period_start", "period_end"):
        args[key] = date.fromisoformat(args[key]) if args[key] else None
    for key in ("price_min", "price_avg", "price_max"):
        if args[key] is not None:
            number = Decimal(str(args[key]))
            if not number.is_finite() or number < 0 or number >= Decimal("100000000"):
                raise ValueError("Invalid price")
            if number != number.quantize(Decimal("0.0001")):
                raise ValueError("Price exceeds database precision")
            args[key] = number
    check_url(args["source_url"])
    parsed = MarketObservation(**args).to_dict()
    if any(parsed[k] != row.get(k) for k in PRICE_COLUMNS):
        raise ValueError("Price key, normalization or quality flag mismatch")
    if args["period_start"] and args["period_end"] and args["period_start"] > args["period_end"]:
        raise ValueError("Invalid price period")
    return {key: parsed[key] for key in PRICE_COLUMNS}


def normalize_industry(row: dict, sources: dict, manual: bool = False) -> dict:
    """Keep annual samples and automatic observations in one source-aware schema."""
    source = sources[row["source_id"]]
    args = dict(row)
    args.pop("external_key", None)
    if manual:
        year = int(args.pop("period"))
        args.update(period_start=f"{year}-01-01", period_end=f"{year}-12-31", frequency="annual")
        args["source_url"] = source["url"]
        args.setdefault("category", "经济作物" if row["source_id"] == "nbs_crop_samples" else "灾害")
        args["measure_type"] = ("rate" if row["unit"] == "%" else
                                "sown_area" if row["metric"] == "cotton_area" else "area")
    for key in ("period_start", "period_end"):
        args[key] = date.fromisoformat(args[key])
    for key in ("value", "yoy_percent"):
        args[key] = Decimal(str(args[key])) if args.get(key) is not None else None
    if args["yoy_percent"] is not None and not args["yoy_percent"].is_finite():
        raise ValueError("Invalid growth rate")
    check_url(args["source_url"])
    parsed = IndustryObservation(**args).to_dict()
    if not manual and parsed["external_key"] != row["external_key"]:
        raise ValueError("Industry identity mismatch")
    parsed["review_status"] = "manual_reviewed" if manual else "collected"
    return parsed


def build_bundle(industry_path: Path, market_path: Path) -> dict:
    """Prepare all data before a write; refuses incomplete or conflicting inputs."""
    industry = json.loads(industry_path.read_text())
    market = json.loads(market_path.read_text())
    if industry.get("errors"):
        raise ValueError("Snapshot has unresolved source failures")
    source_map = {s["source_id"]: s for s in industry["sources"] + industry["reference_sources"]}
    rows = [normalize_price(r) for r in market["rows"] + market["history"]]
    prices, overlap = deduplicate(rows, "external_key")
    industry_rows = [normalize_industry(r, source_map) for r in industry["observations"]]
    industry_rows += [normalize_industry(r, source_map, manual=True) for r in industry["manual_observations"]]
    indicators, _ = deduplicate(industry_rows, "external_key")
    for sid in {r["source_id"] for r in prices}:
        sample = next(r for r in prices if r["source_id"] == sid)
        source_map[sid] = {"source_id": sid, "name": {
            "mofcom": "商务部价格公示", "xinfadi": "北京新发地", "wuhan": "武汉市农业农村局",
            "guangzhou": "广州市农业农村局", "moa_daily": "农业农村部每日监测",
            "moa_milk": "农业农村部畜产品周报"}[sid], "url": sample["source_url"],
            "status": "collected", "scope": "当前已采集价格样本；市场报价、全国均价、生鲜乳分别保留口径"}
    sources = []
    for sid, source in sorted(source_map.items()):
        if source.get("url"):
            check_url(source["url"])
        sources.append({"source_id": sid, "name": source["name"],
                        "domain": "market" if sid in {r["source_id"] for r in prices} else "industry",
                        "source_url": source.get("url"), "status": source["status"],
                        "coverage": source.get("scope", "固定官方发布页；统计期与记录分别保存"),
                        "metadata": source})
    nodes = []
    for row in industry["cold_nodes"]:
        identity = json.dumps([row[k] for k in ("source_id", "name", "region", "city")], ensure_ascii=False)
        nodes.append({"external_key": sha256(identity.encode()).hexdigest(), "source_id": row["source_id"],
                      "source_url": source_map[row["source_id"]]["url"], "name": row["name"],
                      "province": row["region"], "city": row["city"], "reported": row["reported"],
                      "scope": row["scope"], "snapshot_date": industry["snapshot_date"]})
    nodes, _ = deduplicate(nodes, "external_key")
    tables = {"agri_data_sources": sources, "market_price_observations": prices,
              "industry_observations": indicators, "cold_chain_reference_nodes": nodes}
    counts = {name: len(records) for name, records in tables.items()}
    manifest = {"normalizer_version": VERSION, "snapshot_date": industry["snapshot_date"],
                "expected_counts": counts, "price_overlap_removed": overlap,
                "price_categories": dict(Counter(r["category"] for r in prices)),
                "source_files": {p.name: sha256(p.read_bytes()).hexdigest() for p in (industry_path, market_path)}}
    digest = sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    tables["agri_data_import_runs"] = [{"snapshot_sha256": digest, "status": "completed", "manifest": manifest}]
    return {"manifest": manifest, "snapshot_sha256": digest, "tables": tables}


def batch_sql(table: str, rows: list[dict]) -> str:
    """Bind a JSON parameter; base64 transports literals without source SQL text."""
    if table not in TABLE_COLUMNS or not rows:
        raise ValueError("Unknown table or empty import")
    columns = TABLE_COLUMNS[table]
    key = KEYS[table]
    names = ", ".join(columns)
    types = ", ".join(f"{name} {kind}" for name, kind in columns.items())
    updated = [name for name in columns if name != key]
    update = ", ".join(f"{name} = excluded.{name}" for name in updated)
    left = ", ".join(f"target.{name}" for name in updated)
    right = ", ".join(f"excluded.{name}" for name in updated)
    payload = base64.b64encode(json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()).decode()
    # Only base64 alphabet is interpolated; all data is bound as $1 to the prepared statement.
    return f"""BEGIN;
PREPARE funeng_snapshot_import(jsonb) AS
INSERT INTO public.{table} AS target ({names})
SELECT {names} FROM jsonb_to_recordset($1) AS data({types}) WHERE true
ON CONFLICT ({key}) DO UPDATE SET {update}, updated_at = now()
WHERE ROW({left}) IS DISTINCT FROM ROW({right});
EXECUTE funeng_snapshot_import(convert_from(decode('{payload}', 'base64'), 'UTF8')::jsonb);
DEALLOCATE funeng_snapshot_import;
COMMIT;
SELECT '{table}' AS table_name, count(*) AS total FROM public.{table};"""


def sql_batches(bundle: dict, size: int = 200) -> list[dict]:
    """Keep batches bounded; the completed audit is written only after all records."""
    if not 1 <= size <= 500:
        raise ValueError("Invalid batch size")
    return [{"table": table, "rows": len(rows[offset:offset + size]),
             "sql": batch_sql(table, rows[offset:offset + size])}
            for table, rows in bundle["tables"].items()
            for offset in range(0, len(rows), size)]


def verification_definition(bundle: dict) -> dict:
    """Compare all scalar columns with Postgres; JSON metadata is checked separately.

    MD5 here detects accidental content drift, not authenticity. Source files use SHA256.
    Dates and numbers become text, so no floating point financial arithmetic is involved.
    """
    expected, queries = {}, []
    for table, rows in bundle["tables"].items():
        if table == "agri_data_import_runs":
            continue
        columns = {k: v for k, v in TABLE_COLUMNS[table].items() if v != "jsonb"}
        digests = []
        for row in sorted(rows, key=lambda row: row[KEYS[table]]):
            values = [None if row[k] is None else
                      format(Decimal(str(row[k])).normalize(), "f") if kind == "numeric" else row[k]
                      for k, kind in columns.items()]
            serialized = json.dumps(values, ensure_ascii=False, separators=(", ", ": "))
            digests.append(md5(serialized.encode()).hexdigest())
        expected[table] = {"count": len(rows), "content_md5": md5("".join(digests).encode()).hexdigest()}
        fields = ", ".join(f"trim_scale({k})::text" if kind == "numeric" else f"{k}::text"
                           for k, kind in columns.items())
        queries.append(f"SELECT '{table}' AS table_name, count(*) AS count, "
                       f"md5(string_agg(md5(jsonb_build_array({fields})::text), '' "
                       f"ORDER BY {KEYS[table]} COLLATE \"C\")) AS content_md5, "
                       f"max(updated_at)::text AS last_updated FROM public.{table}")
    return {"expected": expected, "query": " UNION ALL ".join(queries) + ";"}

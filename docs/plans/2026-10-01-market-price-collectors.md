# Market Price Collectors Implementation Plan

## Status: Local verification complete; production integration pending
## Complexity: Medium
## Packages affected: backend, docs

---

## Goal

Provide a repeatable, read-only collection command for the five verified public channels: MOFCOM market quotes, Beijing Xinfadi, Wuhan market bulletins, Guangzhou weekly Excel bulletins, and MOA national/livestock reports. Preserve source, market, period, original unit, and quote type; optionally upsert validated observations into a separate database table. No product inventory or production deployment changes.

---

## Sprint Plan

### Sprint 1: Daily market collectors

**Files:** `backend/app/market_data/{types,fetch,collectors}.py`, `backend/tests/test_market_data.py`, `backend/requirements.txt`.

1. Write fixture tests for MOFCOM and Xinfadi HTML/JSON and malformed units.
2. Run the focused tests and confirm they fail before implementation.
3. Add bounded HTTP fetching, parsers, category mapping and decimal unit normalization.
4. Run focused tests and one live, bounded collection for two dates.
5. Record the four-dimension self-assessment below.

### Sprint 2: Local and national bulletin collectors

**Files:** `backend/app/market_data/collectors.py`, `backend/tests/test_market_data.py`.

1. Write fixture tests for Wuhan daily tables, Guangzhou weekly XLS sheets, and MOA daily/weekly reports.
2. Run focused tests to confirm failures.
3. Add parsers that retain market-level versus national/producer-price distinctions and reject invalid spreadsheet cells.
4. Run focused tests and live samples for each source.
5. Record the four-dimension self-assessment below.

### Sprint 3: Persistence and operator command

**Files:** `backend/app/models/market_price.py`, `backend/scripts/collect_market_prices.py`, `backend/migrations/market_price_observations.sql`, `backend/tests/test_market_data.py`, `docs/market-data-collection.md`.

1. Write failing idempotent-upsert and CLI-output tests.
2. Add a separate `market_price_observations` model/table, with decimal prices and source provenance; enable RLS in the migration and grant no public read policy.
3. Add `--source`, `--date`, `--output` and explicit `--write-db` options. Default execution only prints JSONL and never writes to the database.
4. Run `npm test` and `bash scripts/agent-lint.sh`; verify live JSONL contains every supported category.
5. Document exact source URLs, cadence, field meanings, permissions review, and scheduling prerequisites.

## Self-assessment

| Sprint | Functionality /40 | Code /30 | Visual /20 | Coverage /10 | Result |
|---|---:|---:|---:|---:|---|
| 1 | 35 | 25 | N/A | 8 | Passed locally; current page samples |
| 2 | 34 | 25 | N/A | 8 | Passed locally; current XLS and bulletins |
| 3 | 30 | 24 | N/A | 7 | CLI/migration implemented; production gate pending |

## Decisions

- Wholesale market quotes remain separate from `products` selling prices.
- Milk from the MOA livestock report is producer-area raw-milk monitoring, not wholesale dairy pricing.
- Weekly Guangzhou rows retain a date range; they are not presented as daily quotes.
- Missing units or invalid prices remain visible as collection issues and never receive an invented normalized value.
- Public-site scraping is rate bounded and does not attempt to bypass access controls. Commercial reuse and automatic scheduling require a separate source-rights check.

## Known risks

- External page structures and availability can change; each adapter has fixture tests and explicit failure reporting.
- Xinfadi currently serves its published page over HTTP; retain source provenance and do not treat a single successful request as a long-term SLA.
- Guangzhou workbooks contain historical sheets and malformed cells; sheet selection and validation are mandatory.

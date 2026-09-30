#!/usr/bin/env python3
"""Collect public price observations as JSONL; database writes require --write-db."""
import argparse
from collections import Counter
from datetime import date
import json
import sys

from app.market_data.fetch import COLLECTORS


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=["all", *COLLECTORS], default="all")
    parser.add_argument("--date", type=date.fromisoformat, default=date.today())
    parser.add_argument("--output", help="JSONL output file; stdout if omitted")
    parser.add_argument("--write-db", action="store_true", help="Upsert into an already migrated database")
    args = parser.parse_args(argv)
    sources = COLLECTORS if args.source == "all" else {args.source: COLLECTORS[args.source]}
    rows, failures = [], {}
    for source, collect in sources.items():
        try:
            collected = collect(args.date)
            if not collected:
                failures[source] = "no matching report or price rows"
            rows.extend(collected)
            print(f"{source}: {len(collected)} rows", file=sys.stderr)
        except Exception as error:
            failures[source] = f"{type(error).__name__}: {error}"
    if args.write_db and rows:
        from app.database import SessionLocal
        from app.market_data.persistence import upsert_observations
        with SessionLocal() as session:
            inserted, updated = upsert_observations(session, rows)
        print(f"database: {inserted} inserted, {updated} updated", file=sys.stderr)
    output = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    try:
        for row in rows:
            output.write(json.dumps(row.to_dict(), ensure_ascii=False) + "\n")
    finally:
        if args.output:
            output.close()
    print(f"categories: {dict(Counter(row.category for row in rows))}", file=sys.stderr)
    for source, reason in failures.items():
        print(f"FAILED {source}: {reason}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

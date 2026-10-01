"""Collect pinned public industry releases to JSON without modifying a database."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

from app.industry_data.fetch import SOURCES, collect_source


def main(argv: list[str] | None = None) -> int:
    """Collect sources independently; preserve failure details and successful evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=["all", *SOURCES], default="all")
    parser.add_argument("--output", type=Path, help="JSON snapshot path; stdout when omitted")
    args = parser.parse_args(argv)
    result = {"schema_version": 1, "observations": [], "sources": [], "errors": []}
    names = list(SOURCES) if args.source == "all" else [args.source]
    for name in names:
        try:
            rows, metadata = collect_source(name)
            result["observations"].extend(row.to_dict() for row in rows)
            result["sources"].append(metadata)
            print(f"{name}: {len(rows)} observations", file=sys.stderr)
        except Exception as exc:
            result["errors"].append({"source_id": name, "error": str(exc)})
            print(f"{name}: {exc}", file=sys.stderr)
    content = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=args.output.parent, encoding="utf-8",
                                         delete=False) as file:
            file.write(content + "\n")
            tmp = file.name
        os.replace(tmp, args.output)
    else:
        print(content)
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

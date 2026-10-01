"""Prepare reviewed agricultural snapshots for an explicitly authorized import."""
import argparse
import json
from pathlib import Path

from app.industry_data.import_bundle import build_bundle, sql_batches, verification_definition


def main() -> int:
    """Generate a local manifest, normalized JSON, and bounded SQL; no credentials."""
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--industry", type=Path, default=root / "docs/prototypes/agri-industry-dashboard.snapshot.json")
    parser.add_argument("--market", type=Path, default=root / "docs/prototypes/agri-market-dashboard.snapshot.json")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--batch-size", type=int, default=50)
    args = parser.parse_args()
    bundle = build_bundle(args.industry, args.market)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, value in (("normalized.json", bundle), ("manifest.json", bundle["manifest"]),
                        ("batches.json", sql_batches(bundle, size=args.batch_size)),
                        ("verification-definition.json", verification_definition(bundle))):
        (args.output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"snapshot_sha256": bundle["snapshot_sha256"], **bundle["manifest"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

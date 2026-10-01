"""Generate an additive Supabase migration for ORM tables not yet created by any migration.

Run from the repository root:

    PYTHONPATH=backend backend/.venv/bin/python backend/migrations/generate_supabase_delta.py \
        > supabase/migrations/<timestamp>_<name>.sql

Only CREATE TABLE / CREATE INDEX / ENABLE RLS statements are emitted, all idempotent
(IF NOT EXISTS). Column drift on existing tables is reported to stderr, never altered.
Review the output before applying it through Supabase's migration tool.
"""
import re
import sys
from pathlib import Path

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from app.models import Base
import app.models.smart_agriculture  # noqa: F401 - registers tables
import app.api.digital_marketing  # noqa: F401 - registers legacy columns

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "supabase" / "migrations"
CREATE_RE = re.compile(r'CREATE TABLE IF NOT EXISTS (?:public\.)?"?(\w+)"? \((.*?)\n\)', re.S)


def applied_tables() -> dict:
    """Map table name -> column names, from every migration already in the repo."""
    tables = {}
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        for name, body in CREATE_RE.findall(path.read_text(encoding="utf-8")):
            tables[name] = set(re.findall(r'^\s*"?(\w+)"? ', body, re.M))
    return tables


def main() -> None:
    dialect = postgresql.dialect()
    existing = applied_tables()
    missing = [t for t in Base.metadata.sorted_tables if t.name not in existing]

    for table in Base.metadata.sorted_tables:
        if table.name in existing:
            drift = set(table.columns.keys()) - existing[table.name]
            if drift:
                print(f"-- WARNING column drift on {table.name}: {sorted(drift)}", file=sys.stderr)

    print(f"-- Additive migration: {len(missing)} tables defined in ORM but absent from prior migrations.")
    print("-- Idempotent; touches no existing table. All new tables enable RLS (backend-only access).")
    print("BEGIN;")
    for table in missing:  # sorted_tables already orders FK parents first
        print()
        print(str(CreateTable(table, if_not_exists=True).compile(dialect=dialect)).strip() + ";")
        for index in sorted(table.indexes, key=lambda item: item.name):
            print(str(CreateIndex(index, if_not_exists=True).compile(dialect=dialect)) + ";")
        print(f'ALTER TABLE public."{table.name}" ENABLE ROW LEVEL SECURITY;')
        # Supabase 默认给 public 新表授予 anon/authenticated 权限；后端用数据库连接访问，Data API 不开放
        print(f'REVOKE ALL ON public."{table.name}" FROM anon, authenticated;')
    print()
    print("COMMIT;")


if __name__ == "__main__":
    main()

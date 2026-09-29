"""Render one transaction for Supabase execute_sql without a DB password.

The output contains private source data and password hashes. Pipe it directly
to the Supabase connector; never commit it or print it in a review log.
"""
import argparse
import json
import sqlite3
from pathlib import Path

from sqlalchemy import Integer

from app.models import Base
import app.models.smart_agriculture  # noqa: F401
import app.api.digital_marketing  # noqa: F401
from migrate_sqlite_to_supabase import _convert_row, _rotate_known_accounts, _source_rows, _write_initial_credentials


EXPECTED_TARGET = {
    "users": (1, [1]),
    "categories": (5, [1, 2, 3, 4, 5]),
    "products": (14, list(range(1, 15))),
    "lands": (4, [1, 2, 3, 4]),
    "crops": (7, list(range(1, 8))),
    "farm_info": (1, [1]),
}


def render(source: Path, credentials_out: Path) -> str:
    connection = sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    source_tables = {
        row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    if source_tables != set(Base.metadata.tables) - {"uploaded_files", "export_tasks"}:
        raise RuntimeError("SQLite source table list does not match the reviewed baseline")
    rows_by_table = {name: _source_rows(connection, name) for name in source_tables}
    if sum(map(len, rows_by_table.values())) != 53:
        raise RuntimeError("SQLite source row count changed; review before migrating")
    passwords = _write_initial_credentials(credentials_out, include_user=False)
    parts = ["BEGIN;"]
    # Stop if the reviewed destination changes before the merge runs.
    guard_checks = []
    for table in Base.metadata.sorted_tables:
        expected_count, expected_ids = EXPECTED_TARGET.get(table.name, (0, []))
        guard_checks.append(f'(SELECT count(*) FROM public."{table.name}") <> {expected_count}')
        if expected_ids:
            guard_checks.append(
                f'(SELECT array_agg(id ORDER BY id) FROM public."{table.name}") '
                f'IS DISTINCT FROM ARRAY{expected_ids}::integer[]'
            )
    guard_checks.append('(SELECT count(*) FROM public.funeng_migration_conflicts) <> 0')
    parts.append(
        f"DO $guard$ BEGIN IF {' OR '.join(guard_checks)} THEN "
        "RAISE EXCEPTION 'Funeng target changed since merge review'; "
        "END IF; END $guard$;"
    )
    # Preserve the local values that differ materially from the existing rows.
    # Password hashes are deliberately excluded; the existing user login stays intact.
    farm = next(row for row in rows_by_table["farm_info"] if row["id"] == 1)
    local_farm = {key: farm[key] for key in ("lat", "lng", "coords", "established_date")}
    local_user = rows_by_table["users"][0]
    for table_name, local_values, remote_sql in (
        (
            "farm_info", local_farm,
            "(SELECT jsonb_build_object('lat',lat,'lng',lng,'coords',coords,'established_date',established_date) FROM public.farm_info WHERE id=1)",
        ),
        (
            "users", {"full_name": local_user["full_name"]},
            "(SELECT jsonb_build_object('full_name',full_name) FROM public.users WHERE id=1)",
        ),
    ):
        literal = json.dumps(local_values, ensure_ascii=False, default=str).replace("'", "''")
        parts.append(
            "INSERT INTO public.funeng_migration_conflicts "
            "(source_table,source_pk,local_values,remote_values) "
            f"VALUES ('{table_name}','1','{literal}'::jsonb,{remote_sql});"
        )
    for table in Base.metadata.sorted_tables:
        rows = rows_by_table.get(table.name, [])
        if not rows:
            continue
        if table.name == "users":
            rows = []  # Existing Supabase user and password take precedence.
        _rotate_known_accounts(table.name, rows, passwords)
        if not rows:
            continue
        converted = [_convert_row(table, row) for row in rows]
        payload = json.dumps(converted, ensure_ascii=False, default=str, separators=(",", ":"))
        tag = f"$funeng_{table.name}$"
        if tag in payload:
            raise RuntimeError("Unsafe SQL delimiter in source data")
        columns = list(rows[0])
        column_sql = ", ".join(f'"{name}"' for name in columns)
        parts.append(
            f'INSERT INTO public."{table.name}" ({column_sql}) '
            f'SELECT {column_sql} FROM jsonb_populate_recordset('
            f'NULL::public."{table.name}", {tag}{payload}{tag}::jsonb) '
            'ON CONFLICT (id) DO NOTHING;'
        )
        if "id" in table.columns and isinstance(table.columns["id"].type, Integer):
            parts.append(
                f"SELECT setval(pg_get_serial_sequence('public.{table.name}', 'id'), "
                f'(SELECT max(id) FROM public."{table.name}"), true);'
            )
    parts.append("COMMIT;")
    return "\n".join(parts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite", required=True, type=Path)
    parser.add_argument("--credentials-out", required=True, type=Path)
    arguments = parser.parse_args()
    print(render(arguments.sqlite, arguments.credentials_out))

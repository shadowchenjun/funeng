"""One-time, audited SQLite -> Supabase Postgres data migration.

Requires DATABASE_URL for a reviewed Supabase transaction-pooler connection and
the baseline migration to have been applied first. Dry-run is the default.
"""
import argparse
import json
import mimetypes
import os
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path

import bcrypt
from sqlalchemy import Boolean, DateTime, Integer, JSON, inspect, text

from app.config import STORAGE_IMAGE_BUCKET
from app.database import engine
from app.models import Base
import app.models.smart_agriculture  # noqa: F401 - register tables
import app.api.digital_marketing  # noqa: F401 - register legacy columns
from app.models.uploaded_file import UploadedFile
from app import storage


def _source_rows(connection: sqlite3.Connection, table_name: str) -> list[dict]:
    return [dict(row) for row in connection.execute(f'SELECT * FROM "{table_name}"')]


def _convert_row(table, row: dict) -> dict:
    result = {}
    for name, value in row.items():
        column = table.columns[name]
        if value is None:
            result[name] = None
        elif isinstance(column.type, DateTime) and isinstance(value, str):
            result[name] = datetime.fromisoformat(value)
        elif isinstance(column.type, JSON) and isinstance(value, str):
            result[name] = json.loads(value)
        elif isinstance(column.type, Boolean):
            result[name] = bool(value)
        else:
            result[name] = value
    return result


def _write_initial_credentials(path: Path, include_user: bool = True) -> dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    passwords = {"admin": secrets.token_urlsafe(24)}
    if include_user:
        passwords["johnnychenjun"] = secrets.token_urlsafe(24)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as target:
        target.write("Initial funeng login credentials. Change these after first login.\n")
        target.write(f"Admin: admin / {passwords['admin']}\n")
        if include_user:
            target.write(f"User: johnnychenjun / {passwords['johnnychenjun']}\n")
    return passwords


def _rotate_known_accounts(table_name: str, rows: list[dict], passwords: dict[str, str]) -> None:
    if table_name not in ("users", "admin_users"):
        return
    for row in rows:
        password = passwords.get(row["username"])
        if password:
            row["hashed_password"] = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")


def migrate(source: Path, apply: bool, credentials_out: Path, uploads: Path | None) -> None:
    if engine.dialect.name != "postgresql":
        raise RuntimeError("DATABASE_URL must point to a Supabase Postgres database")
    if not source.is_file():
        raise FileNotFoundError(source)
    connection = sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    source_tables = {
        row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    unknown_tables = source_tables - set(Base.metadata.tables)
    if unknown_tables:
        raise RuntimeError(f"Source has tables with no migration model: {sorted(unknown_tables)}")
    rows_by_table = {}
    for name in sorted(source_tables):
        rows = _source_rows(connection, name)
        model_columns = set(Base.metadata.tables[name].columns)
        sqlite_columns = {row[1] for row in connection.execute(f'PRAGMA table_info("{name}")')}
        if sqlite_columns - model_columns:
            raise RuntimeError(f"Unmapped columns in {name}: {sorted(sqlite_columns - model_columns)}")
        rows_by_table[name] = rows
    total = sum(map(len, rows_by_table.values()))
    print(f"SQLite source: {len(source_tables)} tables, {total} rows")

    target_tables = set(inspect(engine).get_table_names(schema="public"))
    missing = set(Base.metadata.tables) - target_tables
    if missing:
        raise RuntimeError(f"Apply the baseline schema first; missing tables: {sorted(missing)}")
    with engine.connect() as target:
        nonempty = [
            name for name in source_tables
            if target.execute(text(f'SELECT count(*) FROM public."{name}"')).scalar_one() > 0
        ]
    if nonempty:
        raise RuntimeError(f"Target business tables are not empty: {sorted(nonempty)}")

    if not apply:
        print("Dry-run only. Add --apply after reviewing the target project and account rotation.")
        return
    if not storage.is_configured():
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required for uploads")
    if uploads and not uploads.is_dir():
        raise FileNotFoundError(uploads)
    passwords = _write_initial_credentials(credentials_out)
    print(f"Generated initial account passwords in {credentials_out} (mode 600)")

    # Upload existing files before committing rows. If a DB transaction fails,
    # the source files remain untouched for a controlled retry.
    uploaded_files = []
    if uploads:
        for path in sorted(uploads.iterdir()):
            if not path.is_file():
                continue
            data = path.read_bytes()
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            storage.upload(STORAGE_IMAGE_BUCKET, path.name, data, content_type)
            uploaded_files.append((path.name, len(data), content_type))

    with engine.begin() as target:
        for table in Base.metadata.sorted_tables:
            rows = rows_by_table.get(table.name, [])
            if not rows:
                continue
            _rotate_known_accounts(table.name, rows, passwords)
            target.execute(table.insert(), [_convert_row(table, row) for row in rows])
            if "id" in table.columns and isinstance(table.columns["id"].type, Integer):
                sequence = target.execute(
                    text("SELECT pg_get_serial_sequence(:table_name, 'id')"),
                    {"table_name": f"public.{table.name}"},
                ).scalar_one_or_none()
                if sequence:
                    maximum = target.execute(text(f'SELECT max(id) FROM public."{table.name}"')).scalar_one()
                    target.execute(
                        text("SELECT setval(CAST(:sequence AS regclass), :value, true)"),
                        {"sequence": sequence, "value": maximum},
                    )
        for filename, size, content_type in uploaded_files:
            target.execute(UploadedFile.__table__.insert().values(
                filename=filename, owner_id=None, size=size, content_type=content_type,
            ))

    with engine.connect() as target:
        copied = sum(
            target.execute(text(f'SELECT count(*) FROM public."{name}"')).scalar_one()
            for name in source_tables
        )
    if copied != total:
        raise RuntimeError(f"Row count mismatch after migration: expected {total}, got {copied}")
    print(f"Migration complete: {copied} business rows and {len(uploaded_files)} images")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite", required=True, type=Path)
    parser.add_argument("--uploads", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--credentials-out", type=Path,
        default=Path.home() / ".config/funeng/initial-accounts.txt",
    )
    arguments = parser.parse_args()
    migrate(arguments.sqlite, arguments.apply, arguments.credentials_out, arguments.uploads)

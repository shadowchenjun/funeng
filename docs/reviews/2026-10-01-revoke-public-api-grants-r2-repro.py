"""Review-only defect reproducers for 6ea1196; PASS means a defect was reproduced.

LC_ALL=C LANG=C uv run --python 3.12 --with pgserver --with 'psycopg[binary]' \
  --with pytest pytest -q -s docs/reviews/2026-10-01-revoke-public-api-grants-r2-repro.py

Loads reviewed code from git commit 6ea1196, regardless of current fixes.
Uses disposable embedded PostgreSQL only, never the production database.
"""
import importlib.util
import subprocess
from pathlib import Path

import psycopg
import pytest

ROOT = Path(__file__).resolve().parents[2]
REVIEW_COMMIT = "6ea1196"


def reviewed_file(path: str) -> str:
    return subprocess.run(["git", "show", f"{REVIEW_COMMIT}:{path}"], cwd=ROOT,
                          check=True, capture_output=True, text=True).stdout


spec = importlib.util.spec_from_file_location(
    "revoke_review_fixtures", ROOT / "supabase/tests/test_revoke_public_api_grants.py"
)
fixtures = importlib.util.module_from_spec(spec)
exec(compile(reviewed_file("supabase/tests/test_revoke_public_api_grants.py"),
             str(ROOT / "supabase/tests/test_revoke_public_api_grants.py"), "exec"), fixtures.__dict__)
server = fixtures.server
db = fixtures.db
REVOKE = reviewed_file("supabase/migrations/20261001150000_revoke_public_api_grants.sql")
ROLLBACK = reviewed_file("supabase/rollback/20261001150000_revoke_public_api_grants.rollback.sql")


def test_reproduce_function_defaults_abort(db):
    before = fixtures.acl_state(db)
    db.execute("ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public "
               "GRANT EXECUTE ON FUNCTIONS TO anon, authenticated, service_role")
    with pytest.raises(psycopg.errors.RaiseException,
                       match="postgres default privileges in public still grant"):
        db.execute(REVOKE)
    db.execute("ROLLBACK")
    assert fixtures.acl_state(db)[0] == before[0]
    assert db.execute("SELECT to_regclass('funeng_ops.acl_snapshot')").fetchone()[0] is None
    print("REPRODUCED R1: production function defaults abort migration; table ACL unchanged")


def test_reproduce_snapshot_appends_new_grant_on_rerun(db):
    assert not db.execute("SELECT has_table_privilege('anon', 'public.industry_observations', 'SELECT')").fetchone()[0]
    db.execute(REVOKE)
    first_count = db.execute("SELECT count(*) FROM funeng_ops.acl_snapshot").fetchone()[0]
    db.execute("GRANT SELECT ON public.industry_observations TO anon")
    db.execute(REVOKE)
    second_count = db.execute("SELECT count(*) FROM funeng_ops.acl_snapshot").fetchone()[0]
    assert second_count == first_count + 1
    db.execute(ROLLBACK)
    assert db.execute("SELECT has_table_privilege('anon', 'public.industry_observations', 'SELECT')").fetchone()[0]
    print(f"REPRODUCED R2: snapshot grew {first_count} -> {second_count}; rollback opened originally private table SELECT ACL")


def test_reproduce_preflight_missing_snapshot_table(db):
    checks = reviewed_file("supabase/checks/public_api_grants.sql")
    with pytest.raises(psycopg.errors.UndefinedTable, match="funeng_ops.acl_snapshot"):
        db.execute(checks)
    print("REPRODUCED R3: complete preflight SQL fails before first migration because funeng_ops is absent")

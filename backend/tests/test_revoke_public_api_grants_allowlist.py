"""收回 Data API 权限迁移的目标名单必须与仓库迁移所建的 funeng 表完全一致。

新增迁移建表后若未同步名单，此测试失败——防止新表漏收回，或误把非 funeng 对象纳入。
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "migrations"))
from repo_tables import MIGRATIONS_DIR, created_tables  # noqa: E402
from generate_revoke_migration import render  # noqa: E402

MIGRATION = MIGRATIONS_DIR / "20261001150000_revoke_public_api_grants.sql"
CHECKS = MIGRATIONS_DIR.parent / "checks" / "public_api_grants.sql"


def _arrays(sql: str) -> list[set[str]]:
    return [set(re.findall(r"'(\w+)'", body)) for body in re.findall(r"ANY \(ARRAY\[(.*?)\]\)", sql, re.S)]


def test_migration_allowlist_matches_repo_tables():
    expected = set(created_tables(exclude=("revoke_public_api_grants",), before=MIGRATION.name))
    arrays = _arrays(MIGRATION.read_text(encoding="utf-8"))
    assert arrays, "migration has no target array"
    assert arrays[0] == expected


def test_checks_use_the_same_allowlist():
    expected = set(created_tables(exclude=("revoke_public_api_grants",)))
    arrays = _arrays(CHECKS.read_text(encoding="utf-8"))
    assert len(arrays) == 3 and all(a == expected for a in arrays)


def test_non_funeng_objects_are_not_targeted():
    targets = _arrays(MIGRATION.read_text(encoding="utf-8"))[0]
    assert "todos" not in targets


def test_generated_migration_matches_generator():
    assert MIGRATION.read_text(encoding="utf-8") == render()

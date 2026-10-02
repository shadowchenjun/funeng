"""仓库内 Supabase 迁移所建的表 —— 即 funeng 拥有的 public 表的唯一来源。

供迁移生成器与「收回 Data API 权限」迁移的目标名单校验共用。
"""
import re
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "supabase" / "migrations"

# 兼容 `CREATE TABLE x`、`CREATE TABLE IF NOT EXISTS public."x"` 等写法
CREATE_TABLE_RE = re.compile(
    r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(?:public\.)?"?(\w+)"?\s*\((.*?)\n\)', re.S | re.I
)


def created_tables(exclude: tuple[str, ...] = (), *, before: str | None = None) -> dict[str, set[str]]:
    """表名 -> 列名集合，按迁移文件名顺序汇总；exclude 为要跳过的迁移文件名片段。"""
    tables: dict[str, set[str]] = {}
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if before is not None and path.name >= before:
            continue
        if any(part in path.name for part in exclude):
            continue
        for name, body in CREATE_TABLE_RE.findall(path.read_text(encoding="utf-8")):
            tables[name] = set(re.findall(r'^\s*"?(\w+)"? ', body, re.M))
    return tables

"""
修复旧库 warehouses 表主键类型

旧库中 warehouses.id 为 VARCHAR NOT NULL PRIMARY KEY（值如 "W001"），而 ORM 模型为 Integer，
导致 POST /api/cold-chain/warehouses（不带 id 插入）失败。本脚本把该表重建为
INTEGER PRIMARY KEY AUTOINCREMENT，并保留全部数据：

- 纯数字的旧 id 直接转为整数；
- 非数字的旧 id（如 "W001"）按原顺序分配新的整数 id（从现有最大数字 id + 1 开始）；
- 其他表中名为 warehouse_id 的列会按映射同步更新。

幂等：若 id 已是 INTEGER 主键则直接跳过。执行前会在数据库旁生成备份文件。

执行方式（在 backend/ 目录下）：
    python -m migrations.fix_warehouses_id            # 使用 DATABASE_URL
    python -m migrations.fix_warehouses_id --no-backup
"""
import os
import shutil
import sqlite3
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import sqlite_path  # noqa: E402

TABLE = "warehouses"


def _columns(conn, table):
    # cid, name, type, notnull, dflt_value, pk
    return conn.execute(f"PRAGMA table_info('{table}')").fetchall()


def _needs_migration(conn) -> bool:
    cols = _columns(conn, TABLE)
    if not cols:
        return False
    id_col = next((c for c in cols if c[1] == "id"), None)
    return id_col is not None and not (id_col[2].upper() == "INTEGER" and id_col[5] == 1)


def _build_mapping(old_ids):
    numeric = [int(i) for i in old_ids if str(i).isdigit()]
    next_id = max(numeric, default=0) + 1
    mapping = {}
    for old in old_ids:
        if str(old).isdigit():
            mapping[old] = int(old)
        else:
            mapping[old] = next_id
            next_id += 1
    return mapping


def migrate(db_path: str, backup: bool = True) -> dict:
    conn = sqlite3.connect(db_path)
    try:
        if not _needs_migration(conn):
            print(f"✅ {TABLE}.id 已是 INTEGER 主键（或表不存在），无需迁移")
            return {}

        if backup:
            backup_path = f"{db_path}.bak-{datetime.now():%Y%m%d%H%M%S}"
            shutil.copy2(db_path, backup_path)
            print(f"💾 已备份到 {backup_path}")

        cols = _columns(conn, TABLE)
        other_cols = [c for c in cols if c[1] != "id"]
        old_ids = [r[0] for r in conn.execute(f"SELECT id FROM {TABLE} ORDER BY rowid")]
        mapping = _build_mapping(old_ids)

        col_defs = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        for _, name, ctype, notnull, default, _ in other_cols:
            d = f'"{name}" {ctype or ""}'.rstrip()
            if notnull:
                d += " NOT NULL"
            if default is not None:
                d += f" DEFAULT {default}"
            col_defs.append(d)
        names = ", ".join(f'"{c[1]}"' for c in other_cols)
        placeholders = ", ".join("?" for _ in range(len(other_cols) + 1))

        # 其他表中引用仓库 id 的列
        refs = []
        for (table,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            if table in (TABLE, f"{TABLE}_new") or table.startswith("sqlite_"):
                continue
            if any(c[1] == "warehouse_id" for c in _columns(conn, table)):
                refs.append(table)

        conn.execute("PRAGMA foreign_keys=OFF")
        conn.execute("BEGIN")
        conn.execute(f"DROP TABLE IF EXISTS {TABLE}_new")
        conn.execute(f"CREATE TABLE {TABLE}_new ({', '.join(col_defs)})")
        rows = conn.execute(f"SELECT id, {names} FROM {TABLE} ORDER BY rowid").fetchall()
        conn.executemany(f"INSERT INTO {TABLE}_new (id, {names}) VALUES ({placeholders})",
                         [(mapping[r[0]], *r[1:]) for r in rows])
        for table in refs:
            for old, new in mapping.items():
                if str(old) != str(new):
                    conn.execute(f'UPDATE "{table}" SET warehouse_id = ? WHERE warehouse_id = ?', (new, old))
        conn.execute(f"DROP TABLE {TABLE}")
        conn.execute(f"ALTER TABLE {TABLE}_new RENAME TO {TABLE}")
        conn.execute(f"CREATE INDEX IF NOT EXISTS ix_{TABLE}_id ON {TABLE} (id)")
        conn.commit()

        count = conn.execute(f"SELECT COUNT(*) FROM {TABLE}").fetchone()[0]
        print(f"✅ {TABLE} 已重建为 INTEGER 主键，保留 {count} 行")
        for old, new in mapping.items():
            if str(old) != str(new):
                print(f"   {old} -> {new}")
        if refs:
            print(f"   已同步引用列: {', '.join(t + '.warehouse_id' for t in refs)}")
        return mapping
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate(sqlite_path(), backup="--no-backup" not in sys.argv)

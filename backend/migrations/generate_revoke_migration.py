"""生成 supabase/migrations/20261001150000_revoke_public_api_grants.sql。

目标名单 = 仓库迁移所建的 funeng 表（repo_tables.created_tables），保证与 backend/tests 的名单校验一致。
运行（仓库根目录）：python3 backend/migrations/generate_revoke_migration.py
"""
from pathlib import Path

from repo_tables import MIGRATIONS_DIR, created_tables

MIGRATION_NAME = "20261001150000_revoke_public_api_grants"


def table_array(names: list[str], indent: str = "    ") -> str:
    rows = [", ".join(f"'{n}'" for n in names[i:i + 5]) for i in range(0, len(names), 5)]
    return (",\n" + indent).join(rows)


def render() -> str:
    names = sorted(created_tables(exclude=(MIGRATION_NAME,)))
    arr = table_array(names)
    return f"""-- 收回 Data API 角色（anon / authenticated）对 funeng 表的权限 —— r3（按复审修订）
-- 由 backend/migrations/generate_revoke_migration.py 生成，请勿手改名单。
--
-- 范围：仅仓库迁移所建的 {len(names)} 张 funeng 表（下方名单，backend/tests/test_revoke_public_api_grants_allowlist.py 校验一致）
--       及其拥有的序列。todos 等非 funeng 对象不在名单内，本迁移不改动，且会校验其 ACL 前后一致。
-- 依据：funeng 前端/管理后台不直连 Supabase；后端以 postgres 经 pooler、Storage 以 service_role 访问。
--       products/categories/lands/crops/farm_info 上的 USING(true) 公开读取策略来自未合并的旧分支
--       feature/supabase-aliyun-oss（anon key 直连），经用户确认一并收回；策略本身保留不动（收回表权限后即失效）。
-- 默认权限：仅修改 postgres/public 的表(r)与序列(S)默认 ACL；函数等其他对象类型保持不变。
--       supabase_admin 的默认 ACL 本迁移不修改，
--       由 supabase_admin 新建的对象仍会默认授予 anon/authenticated（见 supabase/checks/public_api_grants.sql [6]）。
-- 回滚：supabase/rollback/{MIGRATION_NAME}.rollback.sql，按本迁移写入的快照精确恢复。
-- 失败即整体回滚：目标非 postgres 所有、收回后仍有有效权限（含 PUBLIC / 继承角色 / 列级）、非目标对象 ACL 被改动。
BEGIN;
SELECT pg_advisory_xact_lock(hashtextextended('funeng:{MIGRATION_NAME}', 0));

-- ===== 0. 私有快照表（不对任何 API 角色开放）=====
CREATE SCHEMA IF NOT EXISTS funeng_ops;
REVOKE ALL ON SCHEMA funeng_ops FROM PUBLIC, anon, authenticated;
CREATE TABLE IF NOT EXISTS funeng_ops.acl_snapshot_runs (
  migration text PRIMARY KEY,
  captured_at timestamptz NOT NULL DEFAULT now(),
  snapshot_version integer NOT NULL CHECK (snapshot_version = 3)
);
CREATE TABLE IF NOT EXISTS funeng_ops.acl_snapshot_objects (
  migration text NOT NULL REFERENCES funeng_ops.acl_snapshot_runs(migration),
  object_kind text NOT NULL CHECK (object_kind IN ('table', 'sequence')),
  object_name text NOT NULL,
  object_oid oid NOT NULL,
  PRIMARY KEY (migration, object_kind, object_name)
);
CREATE TABLE IF NOT EXISTS funeng_ops.acl_snapshot (
  migration     text        NOT NULL,
  object_kind   text        NOT NULL,  -- table | sequence | column | default:r | default:S | ...
  object_name   text        NOT NULL,  -- default 类为空串
  column_name   text        NOT NULL DEFAULT '',
  grantee       text        NOT NULL,
  privilege     text        NOT NULL,
  is_grantable  boolean     NOT NULL,
  grantor       text        NOT NULL,
  captured_at   timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (migration, object_kind, object_name, column_name, grantee, privilege)
);
REVOKE ALL ON funeng_ops.acl_snapshot, funeng_ops.acl_snapshot_runs, funeng_ops.acl_snapshot_objects
  FROM PUBLIC, anon, authenticated;
ALTER TABLE funeng_ops.acl_snapshot ENABLE ROW LEVEL SECURITY;
ALTER TABLE funeng_ops.acl_snapshot_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE funeng_ops.acl_snapshot_objects ENABLE ROW LEVEL SECURITY;

-- ===== 1. 目标对象 =====
CREATE TEMP TABLE _target_tables ON COMMIT DROP AS
SELECT c.oid, c.relname, c.relkind
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relkind IN ('r', 'p', 'v', 'm', 'f')
  AND c.relname = ANY (ARRAY[
    {arr}
  ]);

-- 目标表拥有的序列（serial / identity）
CREATE TEMP TABLE _target_sequences ON COMMIT DROP AS
SELECT DISTINCT s.oid, s.relname
FROM pg_depend d
JOIN pg_class s ON s.oid = d.objid AND s.relkind = 'S'
WHERE d.classid = 'pg_class'::regclass
  AND d.refclassid = 'pg_class'::regclass
  AND d.deptype IN ('a', 'i')
  AND d.refobjid IN (SELECT oid FROM _target_tables);

DO $$
DECLARE bad text;
BEGIN
  SELECT string_agg(c.relname, ', ') INTO bad
  FROM pg_class c
  WHERE c.oid IN (SELECT oid FROM _target_tables UNION SELECT oid FROM _target_sequences)
    AND c.relowner <> 'postgres'::regrole;
  IF bad IS NOT NULL THEN
    RAISE EXCEPTION 'targets not owned by postgres (REVOKE would be ineffective): %', bad;
  END IF;
END $$;

-- 非目标对象（含 todos 等其他应用）的 ACL 基线，用于结束时校验未被改动
CREATE TEMP TABLE _others_before ON COMMIT DROP AS
SELECT c.oid, c.relacl::text AS relacl,
       (SELECT string_agg(a.attname || '=' || a.attacl::text, ';' ORDER BY a.attnum)
          FROM pg_attribute a WHERE a.attrelid = c.oid AND a.attacl IS NOT NULL) AS colacl
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relkind IN ('r', 'p', 'v', 'm', 'f', 'S')
  AND c.oid NOT IN (SELECT oid FROM _target_tables UNION SELECT oid FROM _target_sequences);

-- ===== 2. 首次快照：快照头、完整对象清单与授权项在同一事务捕获；空授权也有快照头 =====
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM funeng_ops.acl_snapshot_runs WHERE migration = '{MIGRATION_NAME}')
     AND EXISTS (SELECT 1 FROM funeng_ops.acl_snapshot WHERE migration = '{MIGRATION_NAME}') THEN
    RAISE EXCEPTION 'legacy snapshot without capture marker; audit before retrying';
  END IF;
END $$;

CREATE TEMP TABLE _capture_snapshot ON COMMIT DROP AS
WITH first_run AS (
  INSERT INTO funeng_ops.acl_snapshot_runs (migration, snapshot_version)
  VALUES ('{MIGRATION_NAME}', 3)
  ON CONFLICT DO NOTHING RETURNING migration
)
SELECT migration FROM first_run;

INSERT INTO funeng_ops.acl_snapshot_objects (migration, object_kind, object_name, object_oid)
SELECT '{MIGRATION_NAME}', 'table', relname, oid FROM _target_tables
WHERE EXISTS (SELECT 1 FROM _capture_snapshot)
UNION ALL
SELECT '{MIGRATION_NAME}', 'sequence', relname, oid FROM _target_sequences
WHERE EXISTS (SELECT 1 FROM _capture_snapshot);

-- 重复执行时拒绝对象增删/同名重建，避免对未被首次快照覆盖的对象撤权。
DO $$
BEGIN
  IF EXISTS (
    WITH current_objects AS (
      SELECT 'table'::text AS kind, relname, oid FROM _target_tables
      UNION ALL SELECT 'sequence', relname, oid FROM _target_sequences
    ), saved AS (
      SELECT object_kind AS kind, object_name AS relname, object_oid AS oid
      FROM funeng_ops.acl_snapshot_objects WHERE migration = '{MIGRATION_NAME}'
    )
    (SELECT * FROM current_objects EXCEPT SELECT * FROM saved)
    UNION ALL
    (SELECT * FROM saved EXCEPT SELECT * FROM current_objects)
  ) THEN
    RAISE EXCEPTION 'target objects differ from first snapshot; audit before retrying';
  END IF;
END $$;

INSERT INTO funeng_ops.acl_snapshot (migration, object_kind, object_name, grantee, privilege, is_grantable, grantor)
SELECT '{MIGRATION_NAME}',
       CASE WHEN c.relkind = 'S' THEN 'sequence' ELSE 'table' END,
       c.relname, pg_get_userbyid(a.grantee), a.privilege_type, a.is_grantable, pg_get_userbyid(a.grantor)
FROM pg_class c
CROSS JOIN LATERAL aclexplode(c.relacl) a
WHERE c.oid IN (SELECT oid FROM _target_tables UNION SELECT oid FROM _target_sequences)
  AND a.grantee IN ('anon'::regrole, 'authenticated'::regrole)
  AND EXISTS (SELECT 1 FROM _capture_snapshot);

INSERT INTO funeng_ops.acl_snapshot (migration, object_kind, object_name, column_name, grantee, privilege, is_grantable, grantor)
SELECT '{MIGRATION_NAME}', 'column', c.relname, att.attname,
       pg_get_userbyid(a.grantee), a.privilege_type, a.is_grantable, pg_get_userbyid(a.grantor)
FROM pg_class c
JOIN pg_attribute att ON att.attrelid = c.oid AND att.attacl IS NOT NULL
CROSS JOIN LATERAL aclexplode(att.attacl) a
WHERE c.oid IN (SELECT oid FROM _target_tables)
  AND a.grantee IN ('anon'::regrole, 'authenticated'::regrole)
  AND EXISTS (SELECT 1 FROM _capture_snapshot);

INSERT INTO funeng_ops.acl_snapshot (migration, object_kind, object_name, grantee, privilege, is_grantable, grantor)
SELECT '{MIGRATION_NAME}', 'default:' || d.defaclobjtype::text, '',
       pg_get_userbyid(a.grantee), a.privilege_type, a.is_grantable, pg_get_userbyid(a.grantor)
FROM pg_default_acl d
CROSS JOIN LATERAL aclexplode(d.defaclacl) a
WHERE d.defaclrole = 'postgres'::regrole
  AND d.defaclnamespace = 'public'::regnamespace
  AND d.defaclobjtype IN ('r', 'S')
  AND a.grantee IN ('anon'::regrole, 'authenticated'::regrole)
  AND EXISTS (SELECT 1 FROM _capture_snapshot);

-- ===== 3. 收回 =====
DO $$
DECLARE r record;
BEGIN
  FOR r IN SELECT relname FROM _target_tables LOOP
    EXECUTE format('REVOKE ALL ON TABLE public.%I FROM anon, authenticated', r.relname);
  END LOOP;
  -- 列级授权不随表级 REVOKE ALL 一定清除，逐列显式收回
  FOR r IN
    SELECT c.relname, att.attname
    FROM _target_tables c
    JOIN pg_attribute att ON att.attrelid = c.oid AND att.attacl IS NOT NULL
  LOOP
    EXECUTE format('REVOKE ALL (%I) ON TABLE public.%I FROM anon, authenticated', r.attname, r.relname);
  END LOOP;
  FOR r IN SELECT relname FROM _target_sequences LOOP
    EXECUTE format('REVOKE ALL ON SEQUENCE public.%I FROM anon, authenticated', r.relname);
  END LOOP;
END $$;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon, authenticated;

-- ===== 4. 自检：有效权限（含 PUBLIC、继承角色、列级），非目标对象未改动 =====
DO $$
DECLARE
  bad text;
  table_privs text := 'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER'
                      || CASE WHEN current_setting('server_version_num')::int >= 170000 THEN ',MAINTAIN' ELSE '' END;
BEGIN
  SELECT string_agg(format('%s(%s)', t.relname, r.rolname), ', ') INTO bad
  FROM _target_tables t
  CROSS JOIN (VALUES ('anon'), ('authenticated')) r(rolname)
  WHERE has_table_privilege(r.rolname, t.oid, table_privs)
     OR has_any_column_privilege(r.rolname, t.oid, 'SELECT,INSERT,UPDATE,REFERENCES');
  IF bad IS NOT NULL THEN
    RAISE EXCEPTION 'effective table/column privileges remain (via PUBLIC or inherited role?): %', bad;
  END IF;

  SELECT string_agg(format('%s(%s)', s.relname, r.rolname), ', ') INTO bad
  FROM _target_sequences s
  CROSS JOIN (VALUES ('anon'), ('authenticated')) r(rolname)
  WHERE has_sequence_privilege(r.rolname, s.oid, 'USAGE,SELECT,UPDATE');
  IF bad IS NOT NULL THEN
    RAISE EXCEPTION 'effective sequence privileges remain: %', bad;
  END IF;

  SELECT string_agg(c.relname, ', ') INTO bad
  FROM _others_before b
  JOIN pg_class c ON c.oid = b.oid
  WHERE c.relacl::text IS DISTINCT FROM b.relacl
     OR (SELECT string_agg(a.attname || '=' || a.attacl::text, ';' ORDER BY a.attnum)
           FROM pg_attribute a WHERE a.attrelid = c.oid AND a.attacl IS NOT NULL) IS DISTINCT FROM b.colacl;
  IF bad IS NOT NULL THEN
    RAISE EXCEPTION 'non-target objects changed: %', bad;
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_default_acl d CROSS JOIN LATERAL aclexplode(d.defaclacl) a
    WHERE d.defaclrole = 'postgres'::regrole AND d.defaclnamespace = 'public'::regnamespace
      AND d.defaclobjtype IN ('r', 'S')
      AND a.grantee IN ('anon'::regrole, 'authenticated'::regrole)
  ) THEN
    RAISE EXCEPTION 'postgres default privileges in public still grant anon/authenticated';
  END IF;
END $$;

COMMIT;
"""


if __name__ == "__main__":
    out = MIGRATIONS_DIR / f"{MIGRATION_NAME}.sql"
    out.write_text(render(), encoding="utf-8")
    print(f"wrote {out}")

-- 回滚 20261001150000_revoke_public_api_grants —— 按迁移写入的快照精确恢复（r2）
--
-- 只恢复快照中记录的 anon/authenticated 授权项（表、序列、列级、postgres 的默认权限），
-- 不会给原本无授权的对象（例如 23 张业务表、5 张采集表）新增任何权限。
-- 结束时逐项比对：目标对象当前的 anon/authenticated 授权集合必须与快照完全一致，否则整体回滚。
-- 说明：GRANT 由执行者（postgres）发出，授权者（grantor）记为 postgres；快照保留原 grantor 供审计。
BEGIN;

DO $$
DECLARE
  r record;
  objtype text;
  mig constant text := '20261001150000_revoke_public_api_grants';
BEGIN
  IF NOT EXISTS (SELECT 1 FROM funeng_ops.acl_snapshot WHERE migration = mig) THEN
    RAISE EXCEPTION 'no snapshot rows for %; nothing to restore', mig;
  END IF;

  FOR r IN SELECT * FROM funeng_ops.acl_snapshot WHERE migration = mig ORDER BY object_kind, object_name, column_name LOOP
    IF r.object_kind = 'table' THEN
      EXECUTE format('GRANT %s ON TABLE public.%I TO %I%s', r.privilege, r.object_name, r.grantee,
                     CASE WHEN r.is_grantable THEN ' WITH GRANT OPTION' ELSE '' END);
    ELSIF r.object_kind = 'sequence' THEN
      EXECUTE format('GRANT %s ON SEQUENCE public.%I TO %I%s', r.privilege, r.object_name, r.grantee,
                     CASE WHEN r.is_grantable THEN ' WITH GRANT OPTION' ELSE '' END);
    ELSIF r.object_kind = 'column' THEN
      EXECUTE format('GRANT %s (%I) ON TABLE public.%I TO %I%s', r.privilege, r.column_name, r.object_name, r.grantee,
                     CASE WHEN r.is_grantable THEN ' WITH GRANT OPTION' ELSE '' END);
    ELSIF r.object_kind LIKE 'default:%' THEN
      objtype := CASE substr(r.object_kind, 9)
                   WHEN 'r' THEN 'TABLES' WHEN 'S' THEN 'SEQUENCES' WHEN 'f' THEN 'FUNCTIONS'
                   WHEN 'T' THEN 'TYPES' WHEN 'n' THEN 'SCHEMAS' END;
      EXECUTE format('ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT %s ON %s TO %I%s',
                     r.privilege, objtype, r.grantee,
                     CASE WHEN r.is_grantable THEN ' WITH GRANT OPTION' ELSE '' END);
    ELSE
      RAISE EXCEPTION 'unknown snapshot kind %', r.object_kind;
    END IF;
  END LOOP;
END $$;

-- 校验：快照中的目标对象，其 anon/authenticated 授权集合 == 快照
DO $$
DECLARE
  mig constant text := '20261001150000_revoke_public_api_grants';
  diff integer;
BEGIN
  WITH snap AS (
    SELECT object_kind, object_name, column_name, grantee, privilege, is_grantable
    FROM funeng_ops.acl_snapshot WHERE migration = mig
  ),
  objs AS (SELECT DISTINCT object_name FROM snap WHERE object_kind IN ('table', 'sequence', 'column')),
  now_acl AS (
    SELECT CASE WHEN c.relkind = 'S' THEN 'sequence' ELSE 'table' END AS object_kind, c.relname AS object_name, ''::text AS column_name,
           pg_get_userbyid(a.grantee) AS grantee, a.privilege_type AS privilege, a.is_grantable
    FROM pg_class c CROSS JOIN LATERAL aclexplode(c.relacl) a
    WHERE c.relnamespace = 'public'::regnamespace AND c.relname IN (SELECT object_name FROM objs)
      AND a.grantee IN ('anon'::regrole, 'authenticated'::regrole)
    UNION ALL
    SELECT 'column', c.relname, att.attname, pg_get_userbyid(a.grantee), a.privilege_type, a.is_grantable
    FROM pg_class c JOIN pg_attribute att ON att.attrelid = c.oid AND att.attacl IS NOT NULL
    CROSS JOIN LATERAL aclexplode(att.attacl) a
    WHERE c.relnamespace = 'public'::regnamespace AND c.relname IN (SELECT object_name FROM objs)
      AND a.grantee IN ('anon'::regrole, 'authenticated'::regrole)
    UNION ALL
    SELECT 'default:' || d.defaclobjtype::text, '', '', pg_get_userbyid(a.grantee), a.privilege_type, a.is_grantable
    FROM pg_default_acl d CROSS JOIN LATERAL aclexplode(d.defaclacl) a
    WHERE d.defaclrole = 'postgres'::regrole AND d.defaclnamespace = 'public'::regnamespace
      AND a.grantee IN ('anon'::regrole, 'authenticated'::regrole)
  )
  SELECT count(*) INTO diff FROM (
    (SELECT * FROM snap EXCEPT SELECT * FROM now_acl)
    UNION ALL
    (SELECT * FROM now_acl EXCEPT SELECT * FROM snap)
  ) d;
  IF diff > 0 THEN
    RAISE EXCEPTION 'restored ACL differs from snapshot in % entries', diff;
  END IF;
END $$;

COMMIT;

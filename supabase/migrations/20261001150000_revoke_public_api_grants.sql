-- 收回 Data API 角色（anon / authenticated）对 public schema 的表、视图、序列权限
--
-- 背景：20260929 基线迁移建表时沿用了 Supabase 默认授权，82 张表对 anon/authenticated 开放全部权限。
-- 这些表均启用 RLS 且无策略，目前默认拒绝；但一旦有人加了宽松策略即会对外暴露，需纵深防御。
-- 架构依据（docs/SUPABASE_DEPLOYMENT.md）：前端/管理后台不直连 Supabase，所有数据经后端 /api/*；
-- 后端以 postgres 角色经 transaction pooler 连库，Storage 用 service_role —— 均不受本迁移影响。
--
-- 影响：之后若要启用 Supabase Data API（anon key 直连），须为具体表显式 GRANT 并配 RLS 策略。
-- 不改动：schema USAGE、函数 EXECUTE、service_role 权限、RLS 开关、任何数据。
-- 回滚：supabase/rollback/20261001150000_revoke_public_api_grants.rollback.sql
BEGIN;

-- 1. 存量对象
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon, authenticated;     -- 含视图、物化视图
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated;

-- 2. 默认权限：今后由 postgres 创建的对象不再自动授予 anon/authenticated
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon, authenticated;

-- 3. 自检：仍有残留授权则整体回滚
DO $$
DECLARE
  leftover integer;
BEGIN
  SELECT count(*) INTO leftover
  FROM information_schema.role_table_grants
  WHERE table_schema = 'public' AND grantee IN ('anon', 'authenticated');
  IF leftover > 0 THEN
    RAISE EXCEPTION 'revoke incomplete: % table privileges remain for anon/authenticated', leftover;
  END IF;

  SELECT count(*) INTO leftover
  FROM information_schema.usage_privileges
  WHERE object_schema = 'public' AND object_type = 'SEQUENCE' AND grantee IN ('anon', 'authenticated');
  IF leftover > 0 THEN
    RAISE EXCEPTION 'revoke incomplete: % sequence privileges remain for anon/authenticated', leftover;
  END IF;
END $$;

COMMIT;

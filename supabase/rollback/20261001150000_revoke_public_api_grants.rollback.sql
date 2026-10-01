-- 回滚 20261001150000_revoke_public_api_grants：恢复 Supabase 默认的 anon/authenticated 授权。
-- 仅在确需让 Data API 直连（并已为相关表配置 RLS 策略）时执行；恢复后表的访问控制完全依赖 RLS。
BEGIN;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO anon, authenticated;
COMMIT;

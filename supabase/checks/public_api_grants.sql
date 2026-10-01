-- 只读核查：public schema 中 anon/authenticated 的表/序列授权与默认权限（执行前后各跑一次对比）
SELECT 'table' AS kind, grantee, count(DISTINCT table_name) AS objects, string_agg(DISTINCT privilege_type, ',') AS privileges
FROM information_schema.role_table_grants
WHERE table_schema = 'public' AND grantee IN ('anon', 'authenticated')
GROUP BY grantee
UNION ALL
SELECT 'sequence', grantee, count(DISTINCT object_name), string_agg(DISTINCT privilege_type, ',')
FROM information_schema.usage_privileges
WHERE object_schema = 'public' AND object_type = 'SEQUENCE' AND grantee IN ('anon', 'authenticated')
GROUP BY grantee
UNION ALL
SELECT 'default:' || CASE d.defaclobjtype WHEN 'r' THEN 'tables' WHEN 'S' THEN 'sequences' WHEN 'f' THEN 'functions' ELSE d.defaclobjtype::text END,
       pg_get_userbyid(d.defaclrole) || ' → ' || array_to_string(d.defaclacl, ' '), NULL, NULL
FROM pg_default_acl d
JOIN pg_namespace n ON n.oid = d.defaclnamespace
WHERE n.nspname = 'public'
ORDER BY 1, 2;

-- 执行迁移前确认：public 下所有表/视图/序列应归 postgres 所有（否则以 postgres 执行 REVOKE 会失败并整体回滚）
SELECT c.relkind AS kind, pg_get_userbyid(c.relowner) AS owner, count(*) AS objects
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public' AND c.relkind IN ('r', 'v', 'm', 'S', 'p')
GROUP BY 1, 2
ORDER BY 1, 2;

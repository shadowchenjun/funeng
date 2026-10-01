-- 只读快照核查：仅在 20261001150000_revoke_public_api_grants 成功执行后运行。
-- 首次迁移前请运行 public_api_grants.sql，不运行本文件。
-- 回滚后也保留首次快照，便于审计或再次撤权。
SELECT migration, captured_at, snapshot_version
FROM funeng_ops.acl_snapshot_runs
WHERE migration = '20261001150000_revoke_public_api_grants';

SELECT object_kind, count(*) AS captured_objects
FROM funeng_ops.acl_snapshot_objects
WHERE migration = '20261001150000_revoke_public_api_grants'
GROUP BY 1 ORDER BY 1;

SELECT object_kind, grantee, count(*) AS entries
FROM funeng_ops.acl_snapshot
WHERE migration = '20261001150000_revoke_public_api_grants'
GROUP BY 1, 2 ORDER BY 1, 2;

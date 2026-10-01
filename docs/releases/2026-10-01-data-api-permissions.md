# Supabase Data API 权限收回：生产执行记录

## 发布结果

- 用户于 2026-10-01 明确授权推送、合并 main 并执行审查过的权限脚本。
- 源提交：`89aa36290e06ac2a2694551c7bc02162e17a108c`。
- `chore/revoke-public-api-grants` 已推送；main 从 `c65dca7` 正常快进合并并推送到 `89aa362`，未强推。
- GitHub 连接器创建 PR 返回 403（Resource not accessible by integration），因此通过已可用的 Git SSH 完成用户授权的快进合并；没有创建 PR。仓库 main 中未配置 `.github` workflow，前后端 Vercel commit checks 在源提交上均为 success。
- Supabase 项目：`uzxmomyfgkqkbxxkzskc`，实际执行角色 postgres，PostgreSQL 17.6。
- 应用原始审查文件 `supabase/migrations/20261001150000_revoke_public_api_grants.sql`，经 MCP apply_migration 返回 success，迁移名称 `funeng_revoke_public_api_grants_r3`，线上历史版本 **`20261001105858`**。
- 生产生效时间：**2026-10-01 18:58:58（北京时间）**，对应快照捕获时间 `2026-10-01T10:58:58.637929+00:00`。

## 执行前后核查

| 检查 | 执行前 | 执行后 |
|---|---:|---:|
| 目标业务表数 | 69 | 69 |
| 目标序列数 | 49 | 49 |
| anon 有效表权限 | 40 | 0 |
| authenticated 有效表权限 | 40 | 0 |
| anon 有效序列权限 | 49 | 0 |
| authenticated 有效序列权限 | 49 | 0 |
| postgres / service_role 可访问目标表 | 各 69 | 各 69 |
| postgres / service_role 可访问目标序列 | 各 49 | 各 49 |
| 目标业务表精确行数合计 | 1354 | 1354 |

- 所有 69 张表逐表行数不变；本迁移仅更改权限，没有修改业务数据。
- `todos` 及其序列的 ACL 不变；public 下全部 RLS 策略不变。
- postgres/public 的表和序列默认权限中，anon/authenticated 授权项为 0。
- postgres 的函数默认权限、supabase_admin 的全部默认权限以及其他范围外默认权限均与执行前一致。
- 首次不可变快照：版本 3，完整对象清单 **118** 项、原始授权 **956** 项。三张快照表 RLS 开启，anon/authenticated 均无直接权限。
- 原始 `public_api_grants.sql` 已在执行前后运行，`public_api_snapshot.sql` 在执行后运行；另用单个聚合审计查询保留所有核查项，避免 MCP 多语句结果只返回最后一段。

## 线上验收

| 检查 | 执行前 | 执行后 |
|---|---|---|
| 前端 /login | HTTP 200 | HTTP 200 |
| 后端 /health | HTTP 200，healthy | HTTP 200，healthy |
| 前端代理 /api/products/?limit=1000 | HTTP 200，14 条 | HTTP 200，14 条 |
| 前端代理 /api/categories/ | HTTP 200，5 条 | HTTP 200，5 条 |
| 冷链 /api/cold-chain/warehouse（未登录） | 未测试 | HTTP 401，认证保护生效 |
| 金融 /api/supply-chain-finance/financing/stats（未登录） | 未测试 | HTTP 401，认证保护生效 |

供应链金融最初探测的 `/overview` 返回 404；该路径未在仓库定义，随后改用真实的 `/financing/stats` 路径核查。未使用用户账户进行登录后全业务流程或写操作验收，不能将未登录保护检查当成登录后完整业务测试。

## 审计证据与回滚

- [执行前原始核查](2026-10-01-data-api-permissions-before.json)
- [执行后原始核查、权限快照统计与 HTTP 检查](2026-10-01-data-api-permissions-after.json)
- 原始数据文件仅包含对象名、ACL、策略及精确行数，没有密钥、密码或业务记录内容。
- 回滚文件：`supabase/rollback/20261001150000_revoke_public_api_grants.rollback.sql`。**生产没有运行回滚**；快照继续保留，回滚须在需要恢复原始直接授权时另行执行。
- 函数默认授权和 supabase_admin 的默认授权保留属于已审查范围；本次并未宣称关闭整个 Supabase Data API。

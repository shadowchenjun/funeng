# 赋能平台 Supabase / Vercel 部署手册

> 状态：数据库结构及合并导入已完成；Storage 文件和 Vercel 后端部署待验证。

## 目标架构

```text
浏览器
  → Vercel funeng-7p1i（Vue 3 / Vite 静态前端）
  → /api/* rewrite → Vercel funeng（FastAPI 函数，backend/）
  → Supabase Postgres（SQLAlchemy，经 transaction pooler）
  → Supabase Storage（私有 funeng-images / funeng-exports bucket）
```

前端不直接持有数据库连接串或 service role key。前端商品/分类查询及登录走同源 `/api/*`；后端负责鉴权及对 Supabase 的访问。导出任务元数据在 `export_tasks` 表，CSV 在 `funeng-exports`；上传图片元数据在 `uploaded_files` 表，图片在 `funeng-images`。图片仍通过后端原有 `/api/upload/files/{filename}` 路径读取；导出文件只能由创建任务的管理员下载。

## 资源归属与数据基线

- Vercel 前端项目：`funeng-7p1i`，生产域名 `https://funeng-7p1i.vercel.app`，Root Directory 为 `frontend`，框架 Vite。
- Vercel 后端项目：`funeng`，生产域名 `https://funeng.vercel.app`。发布前需将 Root Directory 设为 `backend`，框架 FastAPI。
- 现有前端项目的 `SUPABASE_URL` 指向 Supabase 项目 `uzxmomyfgkqkbxxkzskc`，组织 `shadowchenjun's Org`。2026-09-29 已从 `INACTIVE` 恢复至 `ACTIVE_HEALTHY`。
- 本地迁移来源：`/Users/chenjun/Documents/funeng/backend/funeng.db`，38 张表、53 行（12 张表非空）；`backend/uploads/` 实际有 4 张图片，其中 2 张被 Git 忽略。`frontend/funeng.db` 为 0 字节，不作为迁移来源。
- 合并前线上已有 32 条业务记录，其中 30 条与本地 ID 重叠、2 条仅在线上。已保留线上重叠行并补入本地独有的 23 条；现为 55 条。`users.full_name` 和 `farm_info` 的 4 个差异字段保存在 `funeng_migration_conflicts`，未覆盖线上值，也未复制旧用户密码哈希。
- 已迁移的 `admin` 账号密码是新生成的随机值，保存在本机权限为 600 的 `/Users/chenjun/.config/funeng/initial-accounts-20260929.txt`。现有 `johnnychenjun` 用户密码保持线上值，无法从哈希反推出明文。

## 环境变量

| 位置 | 变量 | 用途 |
|---|---|---|
| Vercel 后端，Secret | `DATABASE_URL` | Supabase Postgres transaction pooler URI，端口 6543；不可使用 SQLite |
| Vercel 后端，Secret | `SECRET_KEY` | 前台用户 JWT 签名，随机且至少 32 字符 |
| Vercel 后端，Secret | `ADMIN_SECRET_KEY` | 管理员 JWT 签名，与前台密钥不同 |
| Vercel 后端，Config | `SUPABASE_URL` | 对应项目的 HTTPS API URL |
| Vercel 后端，Secret | `SUPABASE_SERVICE_ROLE_KEY` | 服务端 Storage 访问，绝不使用 `VITE_` 前缀 |
| Vercel 后端，Config | `STORAGE_IMAGE_BUCKET` | 默认 `funeng-images` |
| Vercel 后端，Config | `STORAGE_EXPORT_BUCKET` | 默认 `funeng-exports` |
| Vercel 后端，Config | `CORS_ORIGINS` | 需要跨域调用时的允许来源，逗号分隔 |

`DATABASE_URL` 应优先使用 Supabase transaction pooler，SQLAlchemy 使用 `NullPool` 并禁用驱动端 prepared statements。现有前端 Vercel 项目存有 Supabase/数据库/OSS 变量；本平台的 Vue 前端没有使用这些变量的代码路径。后端连通后应清理前端项目中多余的服务端密钥，并将当前被 Vercel 标为 Config 的数据库密码等敏感值改为 Secret。

## 迁移与验收

1. 已检查目标 Supabase 的精确行数，保留原 SQLite 文件和 4 张图片作为迁移前快照。
2. 已应用 [`20260929_funeng_baseline.sql`](../supabase/migrations/20260929_funeng_baseline.sql) 与 [`20260929_funeng_merge_conflict_audit.sql`](../supabase/migrations/20260929_funeng_merge_conflict_audit.sql)。41 张应用表启用 RLS，2 个 Storage bucket 为私有；无 Data API 客户端策略，后端通过数据库连接访问。
3. 已用 [`prepare_mcp_migration.py`](../backend/scripts/prepare_mcp_migration.py) 在精确目标行数/ID 保护下执行一次事务式合并；核对了 55 条业务行、1 个管理员与 2 条冲突审计。原 SQLite 和现有线上用户密码均未改动。空目标迁移脚本 [`migrate_sqlite_to_supabase.py`](../backend/scripts/migrate_sqlite_to_supabase.py) 仅用于全新数据库，不能再次对本项目执行。
4. 待将 4 张原图放入私有 `funeng-images` bucket，并核对对象大小、内容及 `uploaded_files` 元数据。
5. 待配置 Vercel 后端环境变量，发布后核验 `/health`、登录、商品/分类查询、冷链鉴权、图片上传/读取/删除、管理员 CSV 导出。
6. 待发布前端并验证 `/api/auth/me` 返回 JSON 401 而非 HTML、正常登录返回用户信息；刷新页面及再次调用接口后数据仍存在。

## 已知限制

- FastAPI `BackgroundTasks` 在无状态函数中无法保证任务完成，因此导出改为在请求内生成并持久化。大批量导出需要后续改为持久任务队列。
- 当前源代码仍包含大量随机生成的演示响应；这些响应本身不代表持久化业务记录。
- 独立 `admin/` Vue 应用尚无已核实的 Vercel 项目，管理员界面部署需单独验收。

## 业务模块补充迁移（2026-10-01）

合入 `optimize/full-pass` 后 ORM 新增 23 张表（冷链 WMS 14、供应链金融 4、智慧农业环境/灌溉 3、数字营销 2），此前线上核查均不存在。**2026-10-01 已按用户授权完成生产补建并核验**，目标项目 `uzxmomyfgkqkbxxkzskc`。生产不执行 `create_all`，部署步骤及当前状态：

1. **已应用** [`20261001120000_funeng_business_module_tables.sql`](../supabase/migrations/20261001120000_funeng_business_module_tables.sql)：仅 `CREATE TABLE/INDEX IF NOT EXISTS`，不触碰已有表；全部启用 RLS，并收回 `anon`/`authenticated` 权限。由 [`generate_supabase_delta.py`](../backend/migrations/generate_supabase_delta.py) 按「ORM − 已有迁移」生成。远端迁移名称 `funeng_business_module_tables`、实际版本 `20261001002742`；本地保留原文件名，后续部署须按名称核对，不能误判为未执行。
2. 可选：执行 [`supabase/seeds/20261001_business_module_demo_data.sql`](../supabase/seeds/20261001_business_module_demo_data.sql) 写入演示数据（1054 行，仅新表，`ON CONFLICT DO NOTHING`，可重复执行）。不执行则对应页面为空态。
3. 部署后端。

本次生产核验：23 张表的 259 个字段、23 个二级索引及 ORM 主键/外键/唯一约束匹配；有效权限满足后端专用访问。原有 47 张表共 1376 行的数据及结构指纹未改变。新表为空，演示数据尚未执行。本地门禁 258 项测试通过、0 lint 错误。[执行计划与验收](plans/2026-10-01-business-module-production-migration.md)，[核验记录](data/business-module-migration-2026-10-01.json)。此次仅更新数据库，未进行应用生产发布。

本地验证：嵌入式 Postgres 依次应用全部迁移（新迁移重复应用一次），后端以迁移建出的表结构运行，`create_all` 未补建任何表；后端测试在该库上 242 项通过（排除 2 个依赖仓库相对路径的未跟踪测试文件）。

## 收回 Data API 角色对 funeng 表的权限（r2，按 review 修订，待执行）

Review：[`docs/reviews/2026-10-01-revoke-public-api-grants-review.md`](reviews/2026-10-01-revoke-public-api-grants-review.md)。r1 草稿的三项问题（回滚扩大权限、全量收回波及非 funeng 对象、自检不检查有效权限）均已修正。

**生产现状（review 只读核查）**：public 70 张表（69 张 funeng + `todos`），全部属主 `postgres`、RLS 开启；`anon`/`authenticated` 各对 41 张表（40 funeng + `todos`）、49 个序列有权限；29 张为后端专用无授权。9 条 RLS 策略：`products`/`categories`/`lands`/`crops`/`farm_info` 有 `USING(true)` 公开读取——当前可被 anon key 读取（含 `farm_info` 负责人电话）；`todos` 有 4 条 `auth.uid()` 策略，属其他应用。公开读取策略来源于未合并旧分支 `feature/supabase-aliyun-oss` 的 anon key 直连代码，用户已确认一并收回。

**范围与机制**：
- 目标：仓库迁移所建 69 张 funeng 表及其序列（名单由 `backend/migrations/generate_revoke_migration.py` 生成，`backend/tests/test_revoke_public_api_grants_allowlist.py` 校验与迁移/核查 SQL 一致）。`todos` 等非 funeng 对象不改动，迁移内校验其 ACL 前后一致
- 执行前将目标对象上 anon/authenticated 的表级、列级、序列与 `postgres` 默认 ACL 授权项写入私有快照 `funeng_ops.acl_snapshot`（对 API 角色不可见）；回滚只按快照恢复，不给原本无授权的对象新增权限
- 自检按有效权限（`has_table_privilege` / `has_any_column_privilege` / `has_sequence_privilege`，覆盖 PUBLIC 与继承角色）；有残留、目标非 `postgres` 所有、或非目标对象被改动即整体回滚
- 默认权限只改 `postgres` 在 public 的默认 ACL。**`supabase_admin` 的默认 ACL 不在本迁移范围**：由其新建的对象仍会默认开放（核查 SQL [6] 可见），需另行处理或确保建表统一由 `postgres` 执行
- RLS 策略本身保留不动；表权限收回后 funeng 表上面向 anon/authenticated 的策略即不再生效

| 步骤 | 文件 |
|------|------|
| 1. 执行前核查（只读，保存输出） | [`supabase/checks/public_api_grants.sql`](../supabase/checks/public_api_grants.sql)：[1][2] 有效权限、[3] 非 funeng 对象、[4] 策略、[5] 属主、[6] 默认 ACL |
| 2. 应用迁移 | [`20261001150000_revoke_public_api_grants.sql`](../supabase/migrations/20261001150000_revoke_public_api_grants.sql) |
| 3. 执行后核查 | 同步骤 1：[1][2] 应全为 0；[3] 与执行前一致；[7] 出现快照 |
| 回滚 | [`supabase/rollback/…rollback.sql`](../supabase/rollback/20261001150000_revoke_public_api_grants.rollback.sql)：按快照精确恢复并校验 |

**验证**：`uv run --python 3.12 --with pgserver --with "psycopg[binary]" --with pytest pytest -q supabase/tests`（嵌入式 Postgres 模拟上述生产事实，含 postgres 与 supabase_admin 两套默认 ACL、`todos` 及其策略、5 条公开读取策略）。r2 14/14 通过；同一套测试对 r1 草稿 11 项失败。覆盖：有效权限清零、`service_role`/属主不受影响、公开读取策略失效但保留、`todos` 不变、回滚与原 ACL 逐项一致（含 29 张私有表不被开放）、幂等与快照保留、快照不对 API 角色开放、经 PUBLIC / 继承角色的残留被检测并整体回滚、序列仅 SELECT 与列级 SELECT 的收回和恢复、非 `postgres` 属主中止、默认权限范围仅 `postgres`。

**未核实（执行前需确认）**：Supabase 项目是否绑定 GitHub 自动应用迁移；是否有 funeng 仓库之外的客户端依赖上述 5 张表的公开读取（旧分支已确认，其他未知）。

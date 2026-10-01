# Execution Plan: 业务模块 23 张表生产补建

## Status: Complete（生产迁移与核验完成；外部 Evaluator 评估待填写）
## Complexity: Medium
## Packages affected: Supabase migrations / docs

## Goal

按用户授权，将已有 `20261001120000_funeng_business_module_tables.sql` 应用到项目 `uzxmomyfgkqkbxxkzskc`。核验新增 23 张表的结构、索引、约束、RLS 和后端权限，并对比已有表的数据与结构指纹。此次只执行建表迁移；可选演示数据不在本次执行范围。

## Sprint 1: 执行并验收生产迁移

- [x] 核对目标、迁移内容及线上迁移历史。
- [x] 保存已有表数据和结构指纹。
- [x] 事务应用已有补充迁移。
- [x] 核验 23 张新表、所有字段/约束/索引及有效权限。
- [x] 核对已有表未被迁移修改，保存核验记录。
- [x] 运行 agent-lint，并更新部署说明。

## 自评估

| 维度 | 自评分 | 说明 |
|---|---|---|
| 功能完整性 | 40/40 | 23 张表、259 个字段、23 个二级索引及 ORM 主键/外键/唯一约束全部匹配 |
| 代码质量 | 27/30 | 使用已有迁移；无业务代码修改；门禁 0 错误，已有警告保留 |
| 视觉设计 | N/A | 无界面修改 |
| 测试覆盖 | 9/10 | 全部新表结构/权限核验，全部已有表结构及内容指纹比对；258 项测试通过；未声称量化覆盖率 |

Evaluator（龙主）评估待独立填写，本记录不替代外部评估。

## 执行证据

- 北京时间 2026-10-01 08:30 完成核验。远端实际版本 `20261001002742`，名称 `funeng_business_module_tables`；本地保留用户指定的原迁移文件名 `20261001120000_funeng_business_module_tables.sql`。后续发布须按名称识别已执行迁移，不能只按本地时间戳重复推送。
- 新表 23 张全部 RLS=true；anon/authenticated 对 SELECT/INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER 的有效权限全无；service_role 的 SELECT/INSERT/UPDATE/DELETE 全部可用。
- 原有 47 张表共 1376 行，结构、索引、约束、RLS/ACL 与全部内容指纹一致，未受此次迁移修改。
- 新表全部空，未执行 1054 行演示数据 SQL。
- `bash scripts/agent-lint.sh`：258 项测试通过，4 条 pytest 警告，前台/后台类型检查通过，0 lint 错误。
- 安全 advisor 对新表仅 INFO `rls_enabled_no_policy`，这是后端专用表不开放客户端策略的预期结果。[说明及整改指南](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy)。
- [机器可核验记录](../data/business-module-migration-2026-10-01.json)。此次未执行应用生产发布或前端页面验收。

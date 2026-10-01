# Execution Plan: 修复 Supabase 权限收回迁移复审问题

## Status: Complete
## Complexity: Medium
## Packages affected: backend/migrations, backend/tests, supabase, docs

## Goal

修复 r2 的默认 ACL 自检、首次快照可变和首次核查报错；仅修改待执行迁移及相关工具，在临时 PostgreSQL 验证后提交当前分支。生产执行不属于本次提交范围。

## Sprint Plan

### Sprint 1: 默认权限范围及迁移前核查

- [x] 同步生成器、迁移和文档，默认权限仅处理 postgres/public 的表 r 与序列 S。
- [x] 核查不依赖尚未创建的快照表，覆盖执行前后及回滚后。
- [x] 夹具加入生产函数默认授权，验证保持不变。

### Sprint 2: 不可变快照与精确回滚

- [x] 事务内首次捕获标记、完整目标对象清单（含空 ACL），重复执行不追加快照。
- [x] 回滚基于原始清单恢复、清除后来新增的直接授权并核对所有原始目标。
- [x] 覆盖新增授权、grant option 变化、空授权首次捕获、回滚后再执行。
- [x] 数据库测试、backend 测试和 agent-lint；提交时审查 staged diff。

## Decisions

| Decision | Rationale | Date |
|---|---|---|
| 修改既有未执行迁移 | 保留草稿迁移身份及允许表清单 | 2026-10-01 |
| 快照头与对象清单保存在私有 funeng_ops | 可识别空快照并核查原本私有对象 | 2026-10-01 |
| 不扩大函数撤权范围 | 函数默认权限不在本次范围 | 2026-10-01 |

## Known risks

- 已有旧版快照但缺乏首次捕获标记时应报错，不静默重新采集。
- 迁移和回滚改变权限，必须事务原子执行；生成器与生成结果需一致。
- 外部 Evaluator 评分由用户填写，不以自评冒充验收。

## Verification and self-assessment

| 维度 | Sprint 1 自评 | Sprint 2 自评 | 依据 |
|---|---|---|---|
| 功能完整性 | 39/40 | 39/40 | 三项修复和回滚边界均实现；生产执行不在本次范围 |
| 代码质量 | 28/30 | 28/30 | 生成器一致、事务原子、首次不可变快照、明确失败路径 |
| 视觉设计 | N/A | N/A | 仅数据库权限变更 |
| 测试覆盖 | 10/10 | 10/10 | 生产函数默认权限、空快照、grant option、对象替换及错误回滚均覆盖 |

自动验证：修复前补充生产夹具与回归后 19 failed / 4 passed；修复后 27 个数据库用例通过。另有 3 个固定读取 r2 提交的历史复现用例通过（含义为旧缺陷仍可复现）。最终 `agent-lint` 0 errors，后端 262 passed；额外生成器/名单针对性测试 4 passed。现有 104 处 any 警告及依赖弃用警告不在本次数据库修改范围。

Evaluator：未进行外部龙主评分；以上是本地自动验证与自评，不冒充外部验收。当前修改在 `chore/revoke-public-api-grants` 提交，生产未执行。

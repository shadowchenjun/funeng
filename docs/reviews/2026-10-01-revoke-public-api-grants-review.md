# 收回 public Data API 权限迁移 Review

日期：2026-10-01，北京时间。对象：分支 `chore/revoke-public-api-grants`，提交 `0af2ed3`。目标项目：`uzxmomyfgkqkbxxkzskc`。

## 结论

**修改后再确认执行。** 本次仅只读检查，没有应用迁移、修改生产权限或推送/合并分支。方向适用于 funeng 后端专用表，但当前“整个 public 安全收回”和回滚正确性的依据不充分。

## 当前生产事实

- public 表/视图类对象 70 个（本次实际查询均为普通表），全部属主 postgres、RLS=true。
- anon 与 authenticated 各有 41 张表的有效权限；不是 82 张不同表。82 可能是两个角色重复计数，不能作为不同表总数。
- 49 个序列，两角色各有有效权限，全部属主 postgres。
- 6 张表共 9 个 RLS 策略：categories、products、lands、crops、farm_info 有公开 SELECT USING(true)；todos 有 authenticated 按 auth.uid 进行 SELECT/INSERT/UPDATE/DELETE 的 4 个策略。
- 29 张表目前两角色均无表权限，其中包含已经按后端专用模式配置的 23 张新业务表、5 张农业采集表，以及冲突审计表。
- 默认权限由 postgres 和 supabase_admin 分别配置；两者均会授予 anon/authenticated 表及序列权限。
- 远端迁移历史中尚无 revoke_public_api_grants，确认此次草稿未执行。

## Findings

### R1 [P1] 回滚不是恢复原状，会扩大 29 张私有表权限

位置：supabase/rollback/20261001150000_revoke_public_api_grants.rollback.sql:4–7。

GRANT ALL ON ALL TABLES/SEQUENCES 会给所有现有对象授权，并非恢复执行前 ACL。当前原本无表权限的 29 张表也会获得授权；迁移后新建对象同样会被无条件开放。即使无 RLS 策略暂时拒绝行访问，这也破坏之前明确设定的后端专用权限边界；不能作为安全回滚。

修改要求：执行前逐对象保存并导出 ACL、grantor/grantee、权限种类/grant option、默认 ACL；回滚精确恢复快照中原有授权，不增加未授权对象或新对象权限。验证回滚前后有效权限与原始快照一致，而非只验证“能访问”。

### R2 [P1] public 全量收回覆盖了未经确认的其他应用对象

位置：supabase/migrations/20261001150000_revoke_public_api_grants.sql:14–15；背景说明 :3–6。

生产实际存在 todos 表与 4 个 authenticated 行级访问策略，它不在 funeng ORM 模型中。只能从当前仓库确认 funeng 前台/后台不直连 Supabase，不能因此证明共享项目的全部对象都没有其他客户端。是否仍有 todos 使用方本次未核实，不能断言使用方不存在。五张业务表的公开读取策略也意味着现状不是“全无策略、默认拒绝”。

修改要求：迁移先限定已核实为 funeng 的对象清单；或核实并获得整个 public 使用方的停用授权。记录现有策略与 consumers，说明默认权限变化对整个 schema 的后续建表影响。

验收：所有目标对象的使用方可验证；其他应用对象权限保持不变，或其停用有明确授权及回归证据。

### R3 [P2] 自检和核查视图无法证明有效权限清零

位置：supabase/migrations/20261001150000_revoke_public_api_grants.sql:26–35；supabase/checks/public_api_grants.sql:2–10。

role_table_grants 忽略通过 PUBLIC 获得的表权限；过滤 grantee 也不检查继承角色产生的有效权限。usage_privileges 对序列只展示 USAGE，不包括 SELECT/UPDATE。因此现有 SELECT 检查为空不足以保证没有残留有效访问。当前生产没有据此发现可利用残留，这里指出的是草稿保障与测试矩阵不完整。

修改要求：通过 pg_class 枚举目标关系，使用 has_table_privilege（SELECT/INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER）与 has_sequence_privilege（USAGE/SELECT/UPDATE）分别检查有效权限，并检查列级授权。加残留权限模拟用例：PUBLIC 表 SELECT、继承角色授权、序列仅 SELECT 或 UPDATE、列级 SELECT；预期检测并回滚。

依据：[PostgreSQL role_table_grants](https://www.postgresql.org/docs/current/infoschema-role-table-grants.html)、[usage_privileges](https://www.postgresql.org/docs/current/infoschema-usage-privileges.html)。

## 默认权限范围补充

草稿仅更改 postgres 的 public 默认表/序列 ACL。线上还存在 supabase_admin 的同类默认 ACL。因此“postgres 创建的新对象不再开放”可以作为限定结论，“以后所有新对象都不再开放”不能这样声称。先确认实际建表角色，再决定处理范围。默认权限基于创建对象时的当前角色，不继承其他角色的默认 ACL；schema 内撤销也不能消除全局默认 ACL 的授权。依据：[PostgreSQL ALTER DEFAULT PRIVILEGES](https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html)。

## 其他说明

- 提交实际修改 4 个文件，不是描述中的 3 个（部署文档也变更）。
- Supabase 是否绑定 GitHub 自动发布，本次未核实。不能仅依据迁移文件进入 main 推断生产一定执行；必须核查该项目集成与 workflow。
- funeng 后端使用 postgres / Storage service_role 的架构使该平台通常不依赖 anon/authenticated 表授权；这不替代共享数据库使用方核查。
- 未重复运行草稿的本地测试；现有 242 passed 属作者验证记录，不能替代此次线上 ACL/策略核查。

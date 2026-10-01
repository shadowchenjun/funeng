# Supabase Data API 权限收回复审（r2）

日期：2026-10-01。分支：`chore/revoke-public-api-grants`。复审提交：`6ea1196`，对比初稿 `0af2ed3`。生产项目：`uzxmomyfgkqkbxxkzskc`。

## 结论

**复审完成，当前版本仍不能通过生产执行审查：1 项 P1、2 项 P2。** 本次只读核查生产，在临时嵌入式 PostgreSQL 复现问题；没有应用生产迁移、合并、推送或修改生产权限。

上次的范围问题已修复：目标限定仓库的 69 张表及其拥有的序列，`todos` 等非目标对象不再一并撤权。有效权限检查也已修复，覆盖 PUBLIC、继承角色、列授权及序列 SELECT/UPDATE。回滚改成按快照恢复，普通执行/回滚场景通过，但首次快照的不可变性仍有缺陷。

## R1 [P1] 默认 ACL 自检范围与撤权范围不一致，生产执行会回滚

- 位置：`supabase/migrations/20261001150000_revoke_public_api_grants.sql:178–183`。
- 同源生成器：`backend/migrations/generate_revoke_migration.py:185–190`。
- 测试缺口：`supabase/tests/test_revoke_public_api_grants.py:49–51`。

撤权 SQL 141–142 行仅处理表（`r`）与序列（`S`）的默认 ACL，但最终 `pg_default_acl` 自检没有限制对象类型。**本次只读查询确认生产的 postgres/public 函数默认 ACL（`f`）仍授予 anon/authenticated EXECUTE**：

```text
postgres / public / f:
{postgres=X/postgres,anon=X/postgres,authenticated=X/postgres,service_role=X/postgres}
```

这类授权未被迁移撤销，因此最终自检必然抛出 `postgres default privileges in public still grant anon/authenticated`，整笔迁移回滚。现有夹具只创建表、序列默认授权，遗漏线上函数默认授权，14 项通过不能证明适配生产。

复现：在现有夹具加入与生产一致的 `ALTER DEFAULT PRIVILEGES ... GRANT EXECUTE ON FUNCTIONS ...`，执行原始迁移，得到上述异常；ROLLBACK 后业务表 ACL 不变，快照表也未创建。

修改要求：同步修改生成器和生成结果，明确默认 ACL 撤权/快照/验收范围。当前范围下自检限定 `d.defaclobjtype IN ('r','S')`；核查脚本 [6] 和文档也需注明只验证表与序列，不能扩大撤销函数权限来掩盖范围错误。添加含生产函数默认 ACL 的成功迁移及精确回滚用例。

## R2 [P2] ON CONFLICT 并没有冻结首次快照，重复执行后回滚会恢复后来新增的权限

- 位置：`supabase/migrations/20261001150000_revoke_public_api_grants.sql:90–119`。
- 同源生成器：`backend/migrations/generate_revoke_migration.py:97–126`。
- 回滚使用方：`supabase/rollback/20261001150000_revoke_public_api_grants.rollback.sql:48–52`。

三段 INSERT 每次执行都会重新采集现有授权，`ON CONFLICT DO NOTHING` 仅防止覆盖已有键，不能防止插入新的授权键。原有重复执行测试没有在两次迁移之间改变 ACL，因此未覆盖这一路径。

在现有夹具复现：

1. 确认 anon 对 `industry_observations` 没有 SELECT 权限。
2. 第一次执行迁移，快照为 874 项。
3. 临时 `GRANT SELECT ON public.industry_observations TO anon`。
4. 再次执行同一迁移，快照增加到 875 项。
5. 执行原始回滚：成功，但 anon 对原本私有表获得 SELECT ACL。

这没有自动新增 RLS 策略，因此不能据此声称行数据已经泄露；但它违反“精确恢复首次执行前权限”的承诺，回滚后的权限边界发生扩大。

修改要求：增加持久的首次捕获标记/快照头，在同一事务内只捕获一次；标记必须能表达首次快照为空的情况，不能仅根据授权行是否存在判断。重复执行不得追加或覆盖首次快照。记录完整目标对象集合及原本空授权状态，以便回滚校验覆盖私有对象。增加两次迁移之间新增授权，以及授权选项变化的测试。

## R3 [P2] 首次迁移前整体执行核查 SQL 会报不存在的快照表

- 位置：`supabase/checks/public_api_grants.sql:101–105`。
- 使用说明：同文件第 2 行称可在 SQL Editor 整体执行，供执行前后对比。

[7] 无条件查询 `funeng_ops.acl_snapshot`，该表只在迁移执行后创建。本次生产只读查询 `to_regclass('funeng_ops.acl_snapshot')` 返回 NULL，迁移历史中也尚无本草稿。在全新夹具执行整份核查文件，直接得到 `UndefinedTable: relation "funeng_ops.acl_snapshot" does not exist`。SQL Editor 的整份执行会报错，不能按当前说明直接用它完成首次迁移前核查。

修改要求：把 [7] 分离为明确的执行后查询，或用有存在性判断的动态查询安全返回空结果；不要只加 WHERE 条件引用一个不存在的关系。验收应分别覆盖迁移前、迁移后、回滚后运行核查文件。

## 验证结果与复现脚本

现有集成测试：**14 passed**。首次启动因环境 locale 无效导致 initdb 失败；设置 `LC_ALL=C LANG=C` 后完整重跑通过，属于测试启动环境问题。

新增 review 专用复现脚本：`docs/reviews/2026-10-01-revoke-public-api-grants-r2-repro.py`。**三个复现用例均确认上述缺陷存在，PASS 表示缺陷复现成功，不表示迁移通过上线验收。** 脚本调用现有夹具，仅在本地临时数据库执行 SQL，不连接生产。

```bash
LC_ALL=C LANG=C uv run --python 3.12 --with pgserver --with 'psycopg[binary]' --with pytest pytest -q supabase/tests
LC_ALL=C LANG=C uv run --python 3.12 --with pgserver --with 'psycopg[binary]' --with pytest pytest -q -s docs/reviews/2026-10-01-revoke-public-api-grants-r2-repro.py
```

修订时应更新生成器、生成结果、核查/回滚文档及相关测试，再复审生产适配。此次未重复运行后端全量测试或 agent-lint，未修改迁移实现；生产运行与页面回归仍属于执行阶段的验收工作。

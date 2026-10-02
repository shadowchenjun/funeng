# Execution Plan: Vercel 行情定时采集

## Status: Published — 生产配置及手动试跑完成，新发地历史补查异常待解决
## Complexity: High
## Packages affected: backend, supabase, docs

## Goal

生产后端每天按六个来源独立采集行情，增量写入 Supabase，保留历史价格；记录成功、未发布、失败和超时，拒绝无密钥访问，同源重叠执行由数据库租约拦截。首先自动化行情，固定年报/季度统计仍需人工选择新报告。

## Sprint 1: 有鉴权、限时和运行记录的定时任务

- [x] 编写失败用例，然后实现接口和服务。
- [x] 每次采集回看最近 3 天；周报从官方索引发现最近 21 天的报告。
- [x] 单来源采集预算 200 秒，HTTP 单请求最多 15 秒；瞬时网络/5xx 重试一次。
- [x] 数据库原子租约 6 分钟；租约持有者才能完成写入，重复数据不增加。
- [x] 采集失败不删除历史；记录来源、日期、状态、计数和脱敏错误类型。
- [x] 新日志表 RLS，撤销 PUBLIC/anon/authenticated，保留后端。
- [x] 新 API 文档和 agent-lint 验证。

## Sprint 2: 生产配置和发布验收

- [x] backend/vercel.json 六个每天一次的 Cron，UTC 12 点（北京时间 20 点）。
- [x] 后端专用 Production CRON_SECRET；无配置时接口关闭。
- [x] 应用迁移、main 提交发布，核对 READY 和 Cron 注册。
- [x] 实际触发任务，核对运行记录与新增行情；核对无鉴权返回 401。
- [ ] 新发地 2026-09-30 生产补查 HTTPError 排查；首次自然定时触发及长期稳定性核对。

## Decisions

| Decision | Rationale | Date |
|---|---|---|
| 六来源分开触发 | 避免故障传播和串行采集超时 | 2026-10-02 |
| 定时读取最近 3 天 | 补迟发布或漏触发；允许价格更正 | 2026-10-02 |
| 周报直接发现近期报告 | 不依赖某天恰好是周报日期 | 2026-10-02 |
| 新增日志表，不更改审核导入记录 | 既有导入表只允许 completed，保留审计含义 | 2026-10-02 |
| 不使用 BackgroundTasks | Vercel 请求结束后不能保证继续运行 | 2026-10-02 |

## Known risks

- Vercel Hobby 可能在指定小时内触发，不能保证精确分钟；失败不会自动重试，应用仅重试瞬时请求。
- 上游假期不发布、阻断或格式变化：状态分别记录 no_data/failed，保留已入库历史。
- 单次预算有限，分页/补采超过预算时记录 failed，次日重复扫描；长期缺口需受控人工补采。
- CRON_SECRET 属于后端专用密钥，不能进入前端、仓库、日志或截图。

## Self evaluation / Evaluator

实现与验证完成后填写自评估；外部 Evaluator 由项目负责人填写，不伪造外部验收。

## Sprint 1 验证记录

- 新接口先跑失败测试：5 failed、6 errors（接口/模型尚未实现），实现后通过。
- 本地 PostgreSQL：迁移连续执行两次；RLS=true，anon SELECT=false、authenticated INSERT=false、service_role SELECT=true；两个并发租约申请只有一个获得；no_data 完成可提交。
- 实站只读试采：新发地 2026-10-01 为 477 条，广州近三周 32 条，生鲜乳 1 条（统计日 2026-09-24）。武汉、全国日报当日无发布。
- 商务部回退到 2026-09-30 的行为被发现并修复，禁止将旧日期标成 10 月 1 日；已补回归测试。
- 前台打包通过。权限迁移生成器增加截止文件参数，保持已经发布的旧迁移不因新增后续表而改变；只读核查名单包含新表。

| 维度 | 自评分 | 依据 |
|---|---|---|
| 功能完整性 | 38/40 | 六来源独立采集、补查、日志、鉴权、租约；生产验证待完成 |
| 代码质量 | 28/30 | 有界网络请求、批量查已有价格、错误脱敏；无新依赖 |
| 视觉设计 | 18/20 | 保持大屏版式，状态文字通过真实接口控制；生产渲染待核对 |
| 测试覆盖 | 9/10 | 鉴权、时区、去重、更正、租约、部分失败、超时、403、报告日期 |
| **总分** | **93/100** | 外部 Evaluator 仍待项目负责人填写 |

## Sprint 2 进度

- 生产迁移 `20261002012452_agri_collection_cron_runs.sql` 已通过 Supabase MCP 应用并登记；本地文件名与远端版本一致。
- 生产核查：日志表 RLS=true，anon SELECT=false、authenticated INSERT=false、service_role SELECT=true。
- agent-lint：前端 12 项测试、后端 282 项测试、前台/后台类型检查全部通过，0 error；104 处既有 any 警告未新增。
- 前台生产打包通过（15.14 秒）；已有 Element Plus 大包警告。
- 生产 CRON_SECRET：初次发布时等待浏览器当场确认，后续用户确认与实际配置见最终发布记录。
- 初次发布尚未实际生产调用；后续真实调用与大屏渲染见最终发布记录。

## 初次发布核查（历史记录：当时尚待密钥确认）

- `b76704dbc0744c1ff780f366adaa64745bba152f` 已推送 main。
- 后端 `dpl_A9LSgCfxFsW2GiZ1ALzrwJ29LMcU`，前端 `dpl_DQrgdxMJ2g8Ygqer9FR2NCYzjmP8`，均 Production READY。
- Vercel Settings / Cron Jobs 已列出六个来源、每天一次、Enabled。截图：`/Users/chenjun/.codex/visualizations/2026/10/02/funeng-vercel-cron-registered.png`。
- 实际生产采集接口返回 503 `Cron is not configured`，符合未设密钥时关闭接口的设计；尚未实际采集写入。
- 登录生产读取 snapshot 成功，原有 121 条产业资料、1148 条行情保留，automatic_collection=false。
- Chrome 实际渲染大屏确认“定时采集未启用”；已发现并更新两处原模板的固定文字，使启用后说明一致。

## Sprint 2 最终发布记录

用户 2026-10-02 当场确认创建密钥后，Production CRON_SECRET 已保存，后端重新部署 dpl_EWsNbyiRKTJU4RXtucevoVVPCq1r READY。六来源均经 Vercel Run 真实执行：五个 completed、新发地 partial（9 月 30 日补查 HTTPError，10 月 1 日行情成功）。新增 1,073、更新 9，行情共 2,221，产业资料 121 条保留。广州与新发地重复运行新增/更新均为 0。匿名请求 401，登录与 snapshot 200，automatic_collection=true；浏览器大屏实际展示定时状态和异常来源。

生产手动试跑验证了任务鉴权、访问来源、数据库提交和大屏读取；首次自然定时触发尚未到来，新发地部分失败也未解决。详见 docs/VERCEL_AGRI_CRON.md 的逐来源记录。

| 维度 | Sprint 2 自评分 | 依据 |
|---|---|---|
| 功能完整性 | 36/40 | 配置、六任务试跑、入库闭环完成；一来源历史补查异常 |
| 代码质量 | 28/30 | 原有验证门禁通过，无本轮实现变更 |
| 视觉设计 | 18/20 | 生产浏览器已核对正常数据与异常提示 |
| 测试覆盖 | 9/10 | 生产鉴权、六来源、去重实测；自然触发尚待核对 |
| **总分** | **91/100** | 外部 Evaluator 仍由项目负责人填写，未代替其验收 |

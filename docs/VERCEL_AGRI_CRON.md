# 行情自动采集（Vercel Cron）

## 范围与日程

Cron 部署在后端项目 `funeng`（Root Directory: `backend`），前端 `funeng-7p1i` 读取同一个 Supabase 数据库。

| 来源 | UTC 表达式 | 北京时间 | 检查范围 |
|---|---|---|---|
| 商务部全国市场行情 | `0 12 * * *` | 每日 20 点 | 五个现有品种，最近三天 |
| 北京新发地 | `5 12 * * *` | 每日 20 点 | 蔬菜、水果、肉禽蛋、水产，最近三天 |
| 武汉市农业农村局 | `10 12 * * *` | 每日 20 点 | 蔬菜、水产，最近三天 |
| 广州市农业农村局 | `15 12 * * *` | 每日 20 点 | 三个市场的近期周报，每市场最新一篇 |
| 农业农村部全国日报 | `20 12 * * *` | 每日 20 点 | 全国均价，最近三天 |
| 农业农村部生鲜乳 | `25 12 * * *` | 每日 20 点 | 最近 21 天最新畜产品周报 |

Hobby 方案可能在指定小时内任意时间触发；Pro 在指定分钟内触发。六个任务互相独立，不能依赖其执行顺序。Cron 仅运行 Production，配置见 `backend/vercel.json`。价格统计日期以来源实际日期为准，假期未发布属于 no_data。

年度种植、水产公报、季度金融等产业资料目前仍选择官方新报告后审核入库，未纳入此次自动发现。不得把旧报告重复采集当成新一期数据。

## 安全配置

在 **后端 funeng → Settings → Environment Variables** 添加 `CRON_SECRET`，范围只选 Production，值为随机至少 32 字符，设为 Sensitive。不要使用前端公开变量前缀，不要复用 JWT / 数据库 / Supabase Storage 密钥。修改环境后重新部署。

Vercel 自动发送 `Authorization: Bearer <CRON_SECRET>`。未配置或长度不足时接口 503；错误密钥 401。普通用户 JWT 无权触发。密钥不进入仓库、响应或审计日志。

## API

`GET /api/cron/market-prices/{source}`，来源只能是上表六个英文 ID：`mofcom`、`xinfadi`、`wuhan`、`guangzhou`、`moa_daily`、`moa_milk`。日期取 Asia/Shanghai 当天，没有任意 URL 或任意历史范围参数。

响应：`run_id, source, status, observed, inserted, updated, errors`。无缓存。

- `completed`：有数据且本轮无错误，200。
- `no_data`：页面正常但无匹配新报告，200，不删除历史。
- `partial`：部分日期出错，其他日期的数据已提交，502。
- `failed`：本轮未写入有效数据且有错误，502。
- `skipped_running`：同源已有活跃任务，200。
- `lease_lost`：原工作进程租约已失效，拒绝其写入，502。

Cron 请求只在任务和数据库事务完成后结束，不使用 BackgroundTasks。HTTP 单请求最多 15 秒，网络超时/连接失败/5xx 重试一次（403/404 不重试）。商务部用系统 curl 验证 TLS，不绕过访问控制；其 HTTP 错误留待下次补采。上游响应上限 4 MB；预算 200 秒在请求及流式读取之间检查。Vercel 整个 FastAPI 函数最长 300 秒。

## 数据与运行记录

迁移新增 `public.agri_collection_runs`，不修改原已审核快照导入表。六分钟数据库租约和部分唯一索引防止同源并发；入库与租约所有权核查在一个事务里完成。租约过期的进程不能继续写入。价格按 external_key 去重，价格修订会更新，历史日期保留。

运行表 RLS 已开启，PUBLIC/anon/authenticated 无直接权限；后端 postgres 读写。错误只保存异常类型，禁止保存可能含连接串的完整异常消息。

大屏刷新后显示最近实际入库时间、行情日更说明和最近失败来源。仅设置密钥不等于 Cron 已注册，必须验证部署及下述列表。

## 发布与验收

1. 应用新增日志表迁移，查询 RLS 和权限确认 anon/authenticated 无权访问。
2. 完成后端 Production CRON_SECRET 配置，提交 main 触发部署。
3. 后端 READY 后，在 **Settings → Cron Jobs** 确认六个路径及日程，启用状态正确。
4. 在该页对各任务按 **Run** 试跑（Vercel 自动附带密钥）。
5. 查询 `agri_collection_runs` 的状态、计数和错误；比较行情总数/最近日期。再运行成功来源验证无重复新增。
6. 未带 Authorization 请求接口，应为 401；登录前端刷新大屏核对真实数据和更新状态。

```sql
select source_id, status, target_date, started_at, finished_at, observed, inserted, updated, errors
from public.agri_collection_runs order by started_at desc limit 30;
select source_id, count(*), max(observed_date) from public.market_price_observations group by source_id;
```

Vercel 对失败调用不会自动重试。应用在请求内处理瞬时重试，并在第二天补查三天。连续失败或长期缺口需要运维在 Cron 页面手动重跑，或使用已有 CLI 指定历史日期；本阶段尚未接入邮件/短信报警。

## 回滚

Vercel 回滚到前一部署会恢复此前 Cron 配置，已有行情和日志保留。也可在 Cron Jobs 页面暂停触发。禁止为停任务删除数据库表。停用密钥会让接口关闭。

平台行为参考：[管理 Cron](https://vercel.com/docs/cron-jobs/manage-cron-jobs)、[函数时长](https://vercel.com/docs/functions/configuring-functions/duration)。

## 2026-10-02 生产发布与试跑记录

用户当场确认后，已在后端 `funeng` 保存 Production 专用 Secret `CRON_SECRET`，重新部署 main `131c27c`。后端部署 `dpl_EWsNbyiRKTJU4RXtucevoVVPCq1r` 已 READY，并绑定 `funeng.vercel.app`。密钥值不写入本记录。

在 Vercel Cron Jobs 页面手动 Run 六个任务，生产 Supabase 的审计结果如下（北京时间 09:48–09:50；这是生产手动试跑，尚非首次自然定时触发）：

| 来源 | 状态 | 读取条数 | 新增 | 更新 |
|---|---|---:|---:|---:|
| 北京新发地 | partial | 477 | 477 | 0 |
| 广州周报 | completed | 32 | 23 | 9 |
| 生鲜乳周报 | completed | 1 | 0 | 0 |
| 全国日报 | completed | 11 | 0 | 0 |
| 武汉市场 | completed | 171 | 171 | 0 |
| 商务部 | completed | 402 | 402 | 0 |

- 合计新增 1,073 条、更新 9 条，行情总数从 1,148 增至 2,221，原有产业资料仍为 121 条。最新实际行情日为 2026-10-01，不把未发布的 10 月 2 日当成新行情。
- 广州、新发地再次 Run 均 inserted=0、updated=0，没有重复新增。
- 新发地两次均在补查 2026-09-30 时记录 HTTPError，其 2026-10-01 的 477 条已正常入库。相同日期在本机读取正常，说明存在生产访问差异；现有脱敏日志没有 HTTP 状态码，不能断言具体阻断原因。该问题未解决，不把六来源宣称全部成功。9 月 30 日已有历史行情保留，大屏会展示该来源异常，下一轮继续补查。
- 无 Authorization 的生产采集请求返回 401；生产登录和 snapshot 均 200，automatic_collection=true。
- 浏览器实际大屏显示“行情每日定时采集”、2,221 条行情及新发地异常提示。最近成功入库时间为北京时间 2026-10-02 09:50:27。
- 每天北京时间 20:00–20:59 的六个 Cron 已 Enabled。自然定时触发及长期稳定性需用之后的审计记录确认；年度/季度产业资料仍按报告更新。

验收截图：/Users/chenjun/.codex/visualizations/2026/10/02/funeng-cron-dashboard-live.png；Secret 配置成功截图：/Users/chenjun/.codex/visualizations/2026/10/02/funeng-cron-secret-configured.png。

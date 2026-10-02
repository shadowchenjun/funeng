# Sprint Handoff: Vercel 行情定时采集

## Sprint 基本信息

Sprint 1 已实现并通过测试；Sprint 2 已注册生产任务，待 CRON_SECRET 创建确认后完成真实试跑。

## 已完成

- 六来源每天一次的 backend/vercel.json；GET /api/cron/market-prices/{source} 仅接受专用 Bearer secret。
- Supabase migration 20261002012452_agri_collection_cron_runs 已执行，RLS、anon/auth 禁止、backend 允许均核查。
- 6 分钟数据库租约、200 秒采集预算、三天补查、周报近 21 天发现、网络/5xx 一次重试、日志脱敏、批量查已有价格。
- 商务部假期忽略请求日期返回旧价格：核对页面 searchDate，拒绝伪造当天行情。
- 282 backend + 12 frontend tests、两端类型检查和 agent-lint 通过；frontend build 通过。Postgres 实测重复 DDL 和并发租约通过。
- main b76704d 已推送，后端/前端 Production READY；Cron Jobs 页面 Enabled 且六条齐全。
- 原 1148 行情 + 121 产业资料保留，登录读 snapshot 成功。

## 未完成 / 所需确认

用户已批准采用 Vercel Cron 并有生产发布授权。浏览器创建安全凭据要求当场确认，已通过 request_user_input_async 询问：允许生成随机 CRON_SECRET，只保存到后端 funeng Production Secret（不进入仓库/前端/聊天）。当前无确认回复，未输入密钥。

Chrome tab 2124554053：Vercel funeng 环境变量创建弹窗，Key=CRON_SECRET、Secret 类型、Production 范围，Value 仍空。需要取得该问题的用户确认后才可创建，不能以先前部署授权替代浏览器当场确认。

## 下一步

1. 收到确认后重新读 CUA 文档并查弹窗。使用随机 32 字节生成密钥，不打印、不截图值。填入 Secret 并保存；凭据值只能短期存在工具内存，不写 repo。
2. Redeploy 后端 Production 才可读到新变量（可推送文档完成提交触发，但记录应先注明试跑待完成）。
3. Cron Settings tab 2124554166 在 Run 六来源，核查 Supabase agri_collection_runs，逐项报告真实状态；Vercel US iad1 是否能访问各来源必须实测，不可用本地采集代替。
4. 重跑一次已成功来源验证 inserted=0 / 无重复，同源重叠一次应 skipped_running。
5. 未带 header 应 401，登录前台刷新 automatic_collection=true 与最新入库计数，保存截图，补最终发布记录。

## 当前生产证据

后端部署 dpl_A9LSgCfxFsW2GiZ1ALzrwJ29LMcU；前端 dpl_DQrgdxMJ2g8Ygqer9FR2NCYzjmP8。
未设 CRON_SECRET，生产请求目前 503 `Cron is not configured`；automatic_collection=false、collection_runs=[]。这是关闭接口，不是自动采集验收通过。

## 评估

自评分 Sprint 1：功能 38/40、质量 28/30、视觉 18/20、测试 9/10，共 93/100。外部 Evaluator 由项目负责人填写，未伪造。

## 风险 / 注意

Hobby 在指定小时内触发（北京时间 20:00–20:59），Vercel 不自动重试失败调用。年报、季报仍需人工选新报告；不要宣称已经自动采集全产业资料。backend Cron env 未设置时不能绕过鉴权试跑。保留无关 frontend/public/logo.b64。

## 文件

详见 docs/VERCEL_AGRI_CRON.md、docs/plans/2026-10-02-vercel-agri-cron.md。

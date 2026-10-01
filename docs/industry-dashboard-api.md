# 产业大数据大屏接口

## 入口与认证

- 前台菜单「产业大屏」，路由 `/industry-dashboard`，需要平台用户登录。
- `GET /api/industry-dashboard/snapshot`；`Authorization: Bearer <平台登录 token>`。
- 未登录或认证失效返回 `401`；接口只读，不抓取网页、不导入数据、不修改权限。
- 后端使用原有数据库连接。浏览器无 Supabase 密钥，原有 RLS 和 anon/authenticated 权限保持有效。

## 响应

| 字段 | 含义 |
|---|---|
| `meta.last_import_at` | 最近 completed 入库批次的核验时间，未核验时为批次创建时间；UTC ISO8601，界面转北京时间 |
| `meta.generated_at` | 本次接口响应生成时间，不是行情时间或采集时间 |
| `meta.automatic_collection` | 当前固定 false；未配置生产采集调度 |
| `meta.industry_total` | 产业原始记录总数，包含历史版本 |
| `meta.market_total / market_returned / market_truncated` | 数据库行情数、本次返回数、是否截断 |
| `meta.price_from / price_to` | 本次行情数据的最早和最晚发布日期，空库返回 null |
| `industry.observations / manual_observations` | 程序采集 / 人工核对指标；每个 metric、region、category、unit、measure_type 保留最新统计期版本 |
| `industry.sources / cold_nodes` | 产业来源目录、已核对冷链样本，非全国基地完整名单 |
| `market.rows / history / sources` | 行情记录、其中的全国均价记录、行情来源目录 |

产业数值和价格使用十进制字符串，保留单位、`qualifier=gt/ge/approx`、同比、统计期、证据、来源 URL 和审核状态。年度数据展示年份，季度数据展示起止日期；不同贷款分类不能相加。非公斤报价的原始单位不自动猜测换算。

## 边界与交互

- 最新行情按 observed_date 倒序，最多返回 10,000 条；达到上限时明确提示本次样本范围。未来历史规模扩大需分页和服务端聚合。
- 缺失为空状态/「待接入」，不以演示数据或 0 替代。全国基地总数没有入库指标，不展示旧原型中的固定 105。
- 六页为总览、种植养殖、行情、冷链、风险、金融；公共金融统计和平台运营待接入状态分别展示。
- 地图、品类、搜索及 CSV 使用当前筛选范围。CSV 文本转义引号并处理公式前缀；来源仅允许 HTTP(S)。
- 返回 private/no-store；前台请求 25 秒超时、支持取消、错误重试及手动刷新。「刷新数据」重新读取数据库，不触发网页采集。
- iframe 隔离原型样式并使用 sandbox，不允许访问宿主认证存储；内嵌 JSON 对 script/HTML 分隔符转义。市场页面继续在内层展示。
- 没有新增生产表或迁移。五类映射对应已审核的农业采集迁移。

## 验证

后端测试覆盖认证、空库、最新统计期筛选、数值精度、来源和入库时间；前端测试覆盖脚本转义、空数据六页、季度金融精度、省份及行情筛选和零价格趋势。真实浏览器和生产发布结果见接入计划。

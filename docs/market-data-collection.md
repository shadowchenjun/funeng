# 农产品行情采集（试运行）

行情与平台商品库存、售价分表管理。本采集命令默认只输出 JSONL，不修改数据库，也不会自动发布到前台大屏。

## 来源与口径

| `--source` | 原始来源 | 周期与口径 | 覆盖 |
|---|---|---|---|
| `mofcom` | [商务部全国农产品商务信息公共服务平台](https://cif.mofcom.gov.cn/cif/seach.fhtml?commdityid=170120) | 指定日、各批发市场、元/公斤 | 西红柿、黄瓜、白条猪、白条鸡、鸡蛋（首批样本） |
| `xinfadi` | [北京新发地价格页面](http://www.xinfadi.com.cn/priceDetail.html) | 指定日、北京市场、原始单位可能为斤或缺失 | 蔬菜、水果、肉蛋禽、水产 |
| `wuhan` | [武汉市农业农村局价格公示](https://nyncj.wuhan.gov.cn/zwgk_25/fdzdgknr/snsj/) | 指定日、当地市场、最高/最低/大宗价 | 蔬菜、水产 |
| `guangzhou` | [广州市农业农村局市场行情](https://nyncj.gz.gov.cn/fw/sjfb/gzscxq/) | 周报 XLS，`--date` 取周末日期，保留起止时间 | 水果、水产、家禽 |
| `moa_daily` | [农业农村部每日监测](https://scs.moa.gov.cn/jcyj/) | 全国均价，不能视为某市场报价 | 肉蛋禽、蔬菜、水果、水产 |
| `moa_milk` | [农业农村部畜产品周报](https://xmsyj.moa.gov.cn/jcyj/) | 10 个主产省生鲜乳采集价，不能视为批发奶制品价 | 奶 |

曾尝试访问全国农产品批发市场价格信息系统 `pfsc.agri.cn`，其页面返回 403；采集器没有绕过该限制。

## 2026-09 实际采集样本

| 品类 | 来源/日期 | 样本 | 原始价格 | 口径 |
|---|---|---|---:|---|
| 蔬菜 | 商务部，9 月 29 日 | 北京大洋路·西红柿 | 4.50 元/公斤 | 市场批发价 |
| 蔬菜 | 新发地，9 月 29 日 | 大白菜 | 0.45 元/斤，换算 0.90 元/公斤 | 市场均价 |
| 水果 | 广州天平，9 月 12–18 日 | 青提（国产） | 12.00 元/公斤 | 周报市场价 |
| 水产 | 武汉，9 月 28 日 | 白沙洲·鲈鱼（条重＜500） | 21–22 元/公斤 | 市场最低/最高价 |
| 肉蛋禽 | 农业农村部，9 月 29 日 | 全国猪肉 | 16.24 元/公斤 | 全国批发均价 |
| 奶 | 农业农村部，9 月 24 日采集 | 10 省生鲜乳 | 3.09 元/公斤 | 主产区采集价 |

上述样本来自一次只读试跑，不是持续更新的数据服务。单日样本行数会随发布情况变化。

## 本地试跑

在项目根目录安装依赖后，从 `backend/` 运行：

```bash
.venv/bin/python -m scripts.collect_market_prices --source xinfadi --date 2026-09-29 --output /tmp/xinfadi.jsonl
.venv/bin/python -m scripts.collect_market_prices --source guangzhou --date 2026-09-18 --output /tmp/guangzhou.jsonl
.venv/bin/python -m scripts.collect_market_prices --source moa_milk --date 2026-09-30 --output /tmp/milk.jsonl
```

`--source all` 对同一个日期逐站查询；部分站点只按周发布，没有对应数据时返回非零状态并在标准错误中标明来源。每条记录保留来源 URL、市场、品类、品种、原单位、报价口径、日期和周期。只有单位明确为公斤或市斤时才产生 `*_yuan_per_kg` 换算值；缺单位原价保留并标为 `missing_unit`。

## 入库与上线条件

1. 先在目标 PostgreSQL 执行 [迁移脚本](../backend/migrations/market_price_observations.sql)。表启用 RLS，没有公开读取策略；前台/API 接口尚未实现。
2. 在已授权的数据库环境中显式追加 `--write-db`。该参数按 `external_key` 幂等写入，原始来源修订价格会更新旧记录。
3. 上线定时采集前，逐站核实转载、商业展示、抓取频次和数据授权；广州页面及农业农村部页面存在禁止未经许可复制镜像的声明。当前仅以低频、有限样本验证技术可行性。
4. 再设计异常告警、人工审核、缓存和大屏展示 API。现在没有生产调度，也没有自动写入 Supabase 或更新 Vercel。

外部网页结构、历史索引范围和站点可用性可能变化。采集器每个请求有 15 秒超时，Xinfadi 最多每类 10 页，武汉每类最多 4 篇，异常会按来源报告。不能把一个成功日当作长期稳定性承诺。

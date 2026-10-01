# 农业采集数据入库报告 · 2026-10-01

## 结果

已写入现有赋能 Supabase 项目 `uzxmomyfgkqkbxxkzskc`（控制台名称 `shadowchenjun's Project`）。通过既有 `funeng_baseline_20260929` 迁移及业务表确认目标；无需获取或重置数据库密码。

| 表 | 实际记录数 | 内容 |
|---|---:|---|
| `market_price_observations` | 1,148 | 市场报价、市场周报、全国均价、生鲜乳采集价 |
| `industry_observations` | 121 | 109条程序采集和12条人工核对，含8条涉农金融/保险指标 |
| `cold_chain_reference_nodes` | 5 | 人工核对基地节点及披露能力，保留资料时点 |
| `agri_data_sources` | 17 | 10个已采集、4个人工核对、1个参考、2个待接入来源 |
| `agri_data_import_runs` | 1 | 文件SHA256、去重记录、统计清单及远端核验结果 |

价格原始快照1,095条加历史点64条，共1,159条输入；11条完全相同的记录去重，得到1,148条。品类数量：蔬菜438、水果150、水产186、肉蛋禽373、奶1。

价格按报价口径分为市场批发1,049、周报34、全国均价64、生鲜乳1；报价日期为2026-09-18至09-30，广州周报保留09-12至09-18的实际周期。年度产业指标以2025年为主，经济作物人工样本为2024年。不能把不同年份或报价口径直接汇总。

## 数据整理规则

- 来源、地区、品类、指标、原始单位、日期、证据和稳定键一起保存；不会将历史报价写成商品库存或售价。
- 1条报价单位缺失；13条按个、只、筐或箱报价，无法换算公斤价。全部保留原价、原单位和质量标记，公斤价格为NULL，没有补造价格。
- 价格使用NUMERIC(12,4)，产业及金融指标使用精确NUMERIC。导入前以Decimal校验，不用浮点计算金额。
- 农业保险的“超1550亿元”等保留`qualifier=gt`，不是精确余额；中央补贴517亿元为`exact`。
- 涉农、农村、农户和农业贷款存在统计交叉，不能相加，也不是平台供应链融资总量。
- 银行真实放款、订单融资、应收融资、仓单质押和气象动态还未接入，仅保存待接入来源目录，没有生成零值或虚构台账。
- 相同稳定键与相同内容可重复导入；输入中同键不同内容拒绝导入，先人工复核。新快照不包含的旧数据不会被删除。

## 核验

入库批次SHA256：`60a57bbc47cf763cf4cfa479d82f1318e26f6abc45116692622a05be301c54e5`。

远端核验完成于2026-10-01 07:41:15（北京时间），结果已回写导入批次的`verification`和`verified_at`。

- 四张数据/来源表全部标量字段内容摘要与本地规范化数据一致；17条来源JSON元数据另行完整比对一致。摘要比较先规范化数值尾零，避免浮点误差。MD5用于发现意外内容漂移，文件完整性采用SHA256。
- **整份快照重复导入一次**：四张数据/来源表条数、内容摘要、最大更新时间均未变化；没有重复记录或无意义更新。
- 孤立来源0、重复价格键0、非法公斤换算0、虚构平台融资指标0。
- 既有业务表前后基线一致：商品14、分类5、用户2、仓库4、运输5、上传文件4；本次迁移和导入没有修改这些表。
- 新增5表均启用RLS，anon和authenticated无SELECT权限；service_role具有SELECT/INSERT/UPDATE权限。正式前台沿用后端API访问，不将服务端密钥放入浏览器。
- `bash scripts/agent-lint.sh`通过；258项测试通过，前台与后台类型检查通过，lint零错误。原有any、UI规则及依赖弃用警告另行保留。

Supabase针对新表仅有INFO提示：

- [RLS已开启且没有客户端策略](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy)：符合目前仅后端访问设计，未为清除提示开放客户端读取。
- [索引尚未使用](https://supabase.com/docs/guides/database/database-linter?lint=0005_unused_index)：目前尚无正式大屏查询，保留指标/地域/日期及来源索引用于后续读取。

## 文件与复用

- [规范化数据](data/agri-2026-10-01/normalized.json)
- [来源文件SHA256及统计清单](data/agri-2026-10-01/manifest.json)
- [实际远端核验结果](data/agri-2026-10-01/verification.json)
- [迁移](../supabase/migrations/20260930232846_agri_industry_snapshot_storage.sql)：CLI生成文件，按MCP实际远端版本对齐，没有再次应用迁移。
- [整理工具](../backend/scripts/prepare_agri_import.py)

在backend目录运行：

```bash
.venv/bin/python -m scripts.prepare_agri_import --output /tmp/funeng-agri-import
```

生成规范化JSON、manifest、50条一批的参数绑定SQL，以及`verification-definition.json`（预期摘要与远端查询）。命令仅整理文件，不读取密码或自动写数据库。本次实际写入通过已授权Supabase连接器执行；数据库数据必须由同等已授权连接执行迁移/批次并核验。

## 后续范围

本次已完成持久化。现有原型仍使用本地快照，正式大屏读取接口、Vue路由接入、生产发布和定时更新尚未实施。已入库数据的人工评审和补齐剩余省级/品类数据继续保留，不将本次入库描述为全量全国采集完成。

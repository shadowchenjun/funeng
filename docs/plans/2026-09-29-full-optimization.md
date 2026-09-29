# Execution Plan: 全面优化（Full Optimization Pass）

## Status: 完成（已通过最终验证 2026-09-29）
## Complexity: High
## Packages affected: backend, frontend, admin, docs/scripts

---

## Goal

全新克隆的仓库能一键装好依赖、启动后端、跑通测试；管理后台能连上本仓库的 FastAPI 后端；
业务接口有鉴权；前台页面读真实数据而不是写死或随机的数据；补上后台订单管理；
仓库卫生和文档与实际状态一致。

## 现状审计发现（2026-09-29）

| # | 问题 | 严重度 |
|---|------|--------|
| 1 | `requirements.txt` 固定的 pydantic 2.5.3 在 Python 3.14 下编译失败；缺 `PyJWT`、`email-validator`，全新环境后端无法启动 | 阻断 |
| 2 | 管理后台 API 挂在 `/admin/*`，而 admin 前端请求 `/api/admin/*`，后台所有请求都会 404 | 阻断 |
| 3 | 冷链、智慧农业、数字营销、供应链金融、仪表盘共约 45 个写接口无鉴权 | 高 |
| 4 | JWT 密钥硬编码在源码中，且两套认证分别使用 jose 和 PyJWT | 高 |
| 5 | `cold_chain.py` 写死 `funeng.db` 路径、绕过 `DATABASE_URL`；`vehicles`、`cargo_owners` 表没有 ORM 模型，全新数据库缺表 | 高 |
| 6 | 后端没有自动化测试 | 中 |
| 7 | 供应链金融、首页、看板前端没有调用 API，全是写死的数据 | 中 |
| 8 | 后台订单管理页缺失（`admin/src/views/order/` 为空） | 中 |
| 9 | `__pycache__` 被 git 跟踪；前端存在重复的 `Dashboard.vue`；AGENTS.md 未填写；根目录无测试入口 | 低 |

## Sprint Plan

### Sprint 1: 后端基础
- [x] requirements 升级到支持 3.14 的版本，统一使用 PyJWT，并补齐缺失的依赖
- [x] `app/config.py`：密钥和 CORS 从环境变量读取
- [x] 管理后台路由挂载到 `/api/admin`
- [x] 业务路由加用户鉴权；前端 axios 全局附带 token，401 时跳转登录
- [x] 冷链模块改走 `DATABASE_URL`，补全 ORM 模型
- [x] 用 pytest 覆盖冒烟、鉴权和后台登录

### Sprint 2: 前端接入真实数据
- [x] 供应链金融页接入 `/api/supply-chain-finance/*`
- [x] 首页和看板接入 `/api/dashboard/*`
- [x] 删除无引用的重复视图

### Sprint 3: 后台订单管理
- [x] 订单页（认养订单和租赁订单），接入已有的后端接口

### Sprint 5: 供应链金融持久化
- [x] 4 张 scf_ 表 + 固定种子数据，GET 由数据计算，新增申请融资/改状态/投保接口

### Sprint 6: 后台类型与接口契约
- [x] vue-tsc 1.8→2.2，45 个类型错误清零；逐页核对并修复 12 类契约不一致
- [x] 修复溯源配置列表 500、data_fields 解析崩溃（含回归测试）

### Sprint 4: 工程化与文档
- [x] 从 git 中移除 pyc 缓存，完善 `.gitignore`
- [x] 根目录 `package.json` 提供 test/lint 脚本，修正 agent-lint
- [x] 更新 AGENTS.md 和 admin/TEST.md

### Sprint 7: 冷链仓储持久化
- [x] 14 个冷链 ORM 模型（仓储/质检/库存/入库/操作/温控/成本）
- [x] 固定种子数据（零随机，温控曲线为确定性正弦波并标注为模拟 IoT）
- [x] `cold_chain.py` 重写：全部走 `Depends(get_db)`，POST/PUT 持久化 + 422/404/409
- [x] 入库闭环：预约签到 → 收货 → 验收（含超额/未知 SKU） → 上架（含确定性评分）
- [x] 前端 `ColdChain.vue` 移除全部 `Math.random`，接真实接口
- [x] 迁移脚本 `migrations/fix_warehouses_id.py`（VARCHAR→INTEGER 主键，幂可重复）
- [x] `tests/test_cold_chain.py` 68 项测试（含入库全流程回归）

## 最终验证结果（2026-09-29）

| 检查项 | 结果 |
|--------|------|
| 后端 pytest | ✅ 232 passed |
| 前端 vue-tsc + build | ✅ 0 错误，构建成功 |
| 管理后台 vue-tsc + build | ✅ 0 错误，构建成功 |
| `scripts/agent-lint.sh` | ✅ 0 error（`: any` 106 处仅警告） |
| 真实库冒烟（118 GET 路由） | ✅ 0 个 5xx / 0 异常 |
| `funeng.db` 完整性 | ✅ md5 未变（3d0e978d0513359afb72edfce33a9037） |
| 冷链 `import random` / `Math.random` | ✅ 0 处 |

## 遗留事项

原遗留事项已全部解决或显著推进：

- [x] 冷链（原 136 处）、智慧农业（原 33 处）随机数据 → 全部持久化为固定种子数据，
      后端零 `import random`，前端 ColdChain.vue 零 `Math.random`
- [x] 管理后台写接口 query→body → 已迁移为 Pydantic body + 422 校验（`app/schemas/admin.py`）
- [x] 旧库 `warehouses.id` VARCHAR → 提供迁移脚本 `backend/migrations/fix_warehouses_id.py`
      （幂等、自动备份、仅在副本上验证通过；原库未改动）
- [x] 首页统计接入 `/api/public/stats`；"转让应收款"后端接口已实现
      （`POST /api/supply-chain-finance/receivables/{id}/transfer`）
- [x] 新增冷链入库闭环：预约签到 → 收货 → 验收 → 上架，含确定性上架建议评分

仍可继续优化（非阻断）：

- `: any` 仍有 106 处（前端 69 / 后台 37），属告警级别，可逐步替换为具体类型
- 冷链迁移脚本尚未在原库执行（需线上窗口；脚本已就绪）
- 仪表盘等首屏大包 >500 kB，可做路由级 code-split

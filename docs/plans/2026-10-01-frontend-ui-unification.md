# Execution Plan: 前台 UI 统一设计系统

## Status: Review（U1–U5 全部完成，待 Evaluator 评估）
## Complexity: High
## Packages affected: frontend, scripts

---

## Goal

前台 9 个视图统一到首页（世代③）的视觉与交互：一套 `#165DFF` 品牌令牌、Element Plus 主题一处接管、共享组件（StatCard / SectionCard / PageHeader / NavCard / EmptyState）替代各页拷贝、8 项平铺导航使板块互达。纯表现层，不改 API 与数据流（冷链 tab 机制为唯一登记例外）。

规范：[`docs/superpowers/specs/2026-10-01-frontend-ui-unification-design.md`](../superpowers/specs/2026-10-01-frontend-ui-unification-design.md)（r2）

---

## Sprint Plan

### Sprint U1: 地基

**实现清单：**
- [x] 令牌：语义色 `--color-*` 为正源，`--accent-green/amber/red` 改为别名；字阶 `--font-xs…2xl`；`--radius-pill`（`App.vue`）
- [x] `src/styles/element-theme.css`：`:root:root` 覆盖五色 × 6 变体 + `-rgb`，文本/边框/填充/圆角；弹窗（16px、白底平头、分隔线、`dialog-sm/md/lg/full` 宽度档）、表格、el-card 标准
- [x] `responsive.css`：删紫色弹窗块、死选择器、首页冲突覆写、登录/注册覆写；移动端弹窗改为变量写法
- [x] 共享组件：StatCard 重写（顶部 4px 语义条、`type` 语义色、unit/trend）；新增 SectionCard、PageHeader；NavCard 16px/4px + `active`；EmptyState 令牌化；删除 PageSection
- [x] 共享组件根 class 统一 `ui-` 前缀——防止与 responsive.css 的 `.stat-card {… !important}` 及父组件 scoped 样式撞名
- [x] `utils/format.ts`：`formatMoneyCompact` / `formatMoneyExact`，金融、营销两页改为引用（显示口径不变）
- [x] App.vue：8 项平铺导航 + 管理后台（admin-only）；<1200px 汉堡抽屉（切路由自动关闭）；keep-alive include 改为组件名
- [x] Login / Register 重皮：去紫色渐变，白卡 16px + Logo + 副标题；修复 `prefix-icon` 字符串不生效
- [x] 全局组件旧色/emoji：AppLoading、ImageUpload、LazyImage
- [x] `agent-lint.sh`：新增 [5/7] 旧色、[6/7] 模板 emoji 检查（警告级，`UI_STRICT=1` 升级为 error）

**验证记录（2026-10-01，headless Chrome，后端连 funeng.db 副本）：**
- 深层路由硬刷新（`/cold-chain`、`/supply-chain-finance`、`/products`）：`--el-color-primary` = `#165DFF`，primary 按钮 `rgb(22,93,255)`，表头 `#F8FAFC`/`#475569`，success tag `#10B981` ✅
- 弹窗（产品「添加产品」）：圆角 16px、头部无渐变、底分隔线、标题 `#0F172A` ✅
- 导航：1440/1280/1200px 9 项单行、无横向溢出；1199/390px 切换为汉堡；抽屉 9 项，点击后跳转并关闭 ✅
- keep-alive：产品 → 分类 → 产品，返回时 0 个 API 请求（修复前 include 写的是路由名，按 KeepAlive 的组件名匹配规则不会命中；修复前状态未单独实测） ✅
- 9 路由 × 桌面/手机 截图走查：无横向溢出、无运行时错误（一次 Pinia 报错为 Vite 依赖预构建整页重载所致，复现 3 次未再出现）
- 共享组件临时预览页截图与 mockup 对照一致（预览路由已删除）
- `vue-tsc --noEmit` ✅；`npm run build` ✅；`bash scripts/agent-lint.sh` 0 error，后端 257 passed（旧色 24 行、emoji 83 行警告，均位于 U2–U4 待迁移视图）

**遗留 / 交接：**
- 视图内部仍是旧世代（emoji 标题、EP 灰统计块），属 U2–U4 范围
- 手机端 `.el-button { margin: 2px !important }` 等全局紧凑规则保留至 U5
- 产品弹窗宽度仍由页面自定，U4 统一到宽度档

**自评估（Generator 填写）：**
| 维度 | 自评分 | 说明 |
|------|--------|------|
| 功能完整性 | 36/40 | U1 清单全部完成并实测；共享组件尚无真实页面使用，接入效果待 U2 验证 |
| 代码质量 | 26/30 | 主题单点覆盖、权重问题有注释；responsive.css 仍有遗留 `!important`（按分阶段计划） |
| 视觉设计 | 17/20 | 导航/登录/弹窗/表格已同代；各视图内部要到 U2–U4 才统一 |
| 测试覆盖 | 7/10 | 类型检查、构建、lint、浏览器脚本走查；前端无单测体系 |
| **总分** | **86/100** | |

**Evaluator 评估（龙主填写）：**
| 维度 | 评分 | 通过？ | 反馈 |
|------|------|--------|------|
| 功能完整性 | /40 | ✅/❌ | |
| 代码质量 | /30 | ✅/❌ | |
| 视觉设计 | /20 | ✅/❌ | |
| 测试覆盖 | /10 | ✅/❌ | |
| **结果** | | **通过/打回** | |

---

### Sprint U2: 世代①清除（AdminView、SupplyChainFinance）

**实现清单：**
- [x] 全局布局类（App.vue）：`.page-container`、`.stat-grid`（4→2 列）、`.section-stack`、`.section-split`（<1024px 堆叠）
- [x] `.header` → PageHeader（刷新按钮改 plain + Refresh 图标）；统计 → StatCard；区块 → SectionCard（标题图标 + extra 插槽）
- [x] 金融：信用评估改为定义列表、空态用 EmptyState、评分环取令牌色值；保险/信用两栏用 `.section-split`；弹窗套 `dialog-sm`
- [x] 管理后台：板块入口统一品牌蓝（去掉四色身份色）、改为 `<button>` 可键盘聚焦；角色标签 primary/info
- [x] EP 灰 / `#409EFF` / emoji 清零；表格关键列 `min-width`，窄屏横向滚动而非挤压换行
- [x] responsive.css 删除 `.finance-container`、`.admin-container`、`.admin-container .module-card` 规则
- [x] StatCard 移动端紧凑（图标 36px，字号随 CSS 继承，无 `!important`）

**验证记录（2026-10-01，headless Chrome，后端连 funeng.db 副本）：**
- 两页 × 1440/390px 截图：无横向溢出、无控制台错误
- 「申请融资」弹窗：宽 480px，`class="el-dialog dialog-sm"` 生效
- `vue-tsc` ✅；`agent-lint` 0 error，旧色/emoji 警告中这两页条目清零

**自评估（Generator 填写）：**
| 维度 | 自评分 | 说明 |
|------|--------|------|
| 功能完整性 | 37/40 | 业务逻辑与接口调用未改；「详情/催收」按钮原本无行为，保持原样 |
| 代码质量 | 27/30 | 统计卡元数据与取值分离；未新增 `!important` |
| 视觉设计 | 18/20 | 与首页同代；金融页长表格无分页（原样保留，属信息架构） |
| 测试覆盖 | 7/10 | 类型检查、lint、浏览器截图；前端无单测 |
| **总分** | **89/100** | |

### Sprint U3: 世代②核心（SmartAgriculture、ColdChain）

**实现清单：**
- [x] 新组件 `ModuleNav`：NavCard 分组导航（组宽∝项数，宽屏一行、窄屏按组换行，v-model）；冷链 11 项分「监测/仓储/运输/运营」，智慧农业 7 项分「生产管理/物联监测/决策与追溯」
- [x] 全局工具类：`.tile*`（卡中卡统一浅底 12px）、`.metric*`（区块内指标）、`.subsection-title`（替代 emoji el-divider）、`.stat-grid--3`、`.w-full`；`utils/theme.ts`（SVG/地图用色值 + `levelColor`）
- [x] 两页：灰底统计 → StatCard（区块外）/ metric（区块内）；el-card → SectionCard；emoji、EP 旧色、内联样式全部清零；弹窗套宽度档，表单 `:xs=24 :sm=12` 响应式
- [x] **冷链 tab 机制（§6 例外）**：v-if → v-show；地图只建一次（`resizeEnable`），再次显示/数据变化时 `clearMap()` 重画；去掉 300ms 延时；卸载时销毁；仓库增删改后重画标记
- [x] **智慧农业地图**：农场概览图原在隐藏面板中创建（0 尺寸）且进入「农场信息」不会重建——改为同一生命周期模式，进入 farm/device 面板时重画；卸载时销毁三张地图
- [x] 修复温度监控卡片空白：接口字段（location/address/current_temp）与页面字段不一致，在 `loadMonitorData` 中映射；离线传感器（current_temp=null）显示「暂无读数」
- [x] responsive.css 删除两页容器规则

**验证记录（2026-10-01，headless Chrome，后端连 funeng.db 副本，高德地图实际加载）：**
- 18 个面板 × 1440/390px：无横向溢出、无控制台错误；导航宽屏 1 行，手机按组 4/3 行
- 冷链「仓库↔品控↔运输↔监控」切换 3 轮后，`#warehouseMap`、`#transportMap` 各仅 1 个地图实例，尺寸 1300×238
- 品控数据 3 轮切换仅请求 1 次（懒加载保持）
- 智慧农业农场概览图隐藏时创建、显示后尺寸恢复为 1300×238
- `vue-tsc`、`npm run build` ✅；`agent-lint` 0 error，`: any` 未增加；两页旧色/emoji 清零

**发现但未修（超出纯表现层）：**
- `/api/cold-chain/warehouses/list` 不返回 `lat/lng`，仓库分布图从未显示过标记（需后端补字段）
- 本地 funeng.db 中部分仓库 `status` 为英文 `normal/warning`（旧数据），页面按「正常」统计为 0；种子数据为中文，属数据清洗问题

**自评估（Generator 填写）：**
| 维度 | 自评分 | 说明 |
|------|--------|------|
| 功能完整性 | 36/40 | 18 个面板全部迁移；地图生命周期修正并实测；两项后端/数据问题仅记录 |
| 代码质量 | 27/30 | ColdChain 2121→1857 行、SA 1684→1371 行；导航/卡片沉淀为共享组件与工具类 |
| 视觉设计 | 18/20 | 与首页同代；冷链 11 项一行分组 |
| 测试覆盖 | 7/10 | 类型检查、构建、lint、浏览器脚本（地图实例数/尺寸/懒加载）；前端无单测 |
| **总分** | **88/100** | |

### Sprint U4: 世代②③收尾（DigitalMarketing、Dashboard、Products、Categories）

**实现清单：**
- [x] 数字营销：ModuleNav（单组 4 项）+ v-show；统计 → StatCard（带趋势）；渠道/会员/活动 → tile；空列表用 EmptyState；会员头像与等级标签去掉自定义色值
- [x] 看板：PageHeader（标题与导航一致为「数据看板」）+ StatCard + SectionCard；删 3 处 `:header-cell-style`；库存徽标 → el-tag；分类占比条改品牌蓝；金额用共享 `formatMoneyCompact`
- [x] 产品：PageHeader + el-button；手写搜索框 → el-input；分类/状态徽标 → el-tag；操作按钮 → link 按钮；弹窗 `dialog-md`、删 `:deep(.product-dialog)`；保留桌面表格/移动卡片双视图
- [x] 分类：PageHeader + el-button；空态/错误态 → EmptyState（含重试）；图标选择器 emoji → EP 图标；弹窗 `dialog-sm`；默认色 `#409eff` → `#165DFF`
- 说明：分类卡片中的 emoji 来自数据库 `categories.icon` 字段（用户数据），非模板文字；编辑时选择图标即替换为 EP 图标

### Sprint U5: 清扫 + 回归

**实现清单：**
- [x] HomeView 删除 101 行死 CSS（旧顶栏 `.main-nav/.nav-*`/`.btn-nav-*`）；hero CTA：已登录 → `/dashboard`，未登录 → `/login`；页脚去 emoji
- [x] 删除 `critical.css`（无引用）
- [x] responsive.css 重写：`!important` 106 → 0；移除已无匹配的旧容器/统计卡规则及强改 EP 组件尺寸的紧凑规则（含把 `.el-image` 强制为 40px 导致移动端产品缩略图变小的问题）；窄屏弹窗统一满宽减 32px
- [x] agent-lint：旧色/emoji 检查默认 error（`UI_STRICT=1`）

**最终回归（2026-10-01，headless Chrome）：**
- 9 路由 × 1440/1200/390px：无横向溢出；标题无 emoji；页面实际渲染中无 `#409EFF` / `#667eea`（遍历计算样式）
- hero CTA：未登录 → /login，已登录 → /dashboard
- 弹窗：产品 640（md）、分类 480（sm）、会员 640（md）；手机端 358px
- 移动端产品缩略图 72×72（此前被全局规则压为 40）
- 控制台 0 错误；`vue-tsc`、`npm run build` ✅；`agent-lint`（UI 检查为 error 级）0 error，后端 258 passed；`: any` 106 → 104

**整体验收（spec §7）：**
| 项 | 结果 |
|----|------|
| vue-tsc / build / agent-lint 全绿 | ✅ |
| `grep -riE "409eff\|667eea\|764ba2\|64, ?158, ?255" frontend/src` 为 0 | ✅（lint 强制） |
| 模板无 emoji（ClaudeCodeAssistant 除外） | ✅（lint 强制） |
| 8 项导航可达、<1200px 抽屉 | ✅ |
| ≤768px 逐页无破版 | ✅ |

**自评估（U4+U5）：**
| 维度 | 自评分 | 说明 |
|------|--------|------|
| 功能完整性 | 37/40 | 全部视图迁移完成；业务接口未改；CTA 行为按 spec 调整 |
| 代码质量 | 27/30 | `!important` 清零、死代码删除、共享格式化/组件复用 |
| 视觉设计 | 18/20 | 全站同代；分类卡片 emoji 图标为存量数据 |
| 测试覆盖 | 7/10 | 类型/构建/lint/三档宽度浏览器回归；前端无单测 |
| **总分** | **89/100** | |

# 前台 UI 统一设计系统 — 设计文档（Spec）

- **日期**：2026-10-01
- **状态**：已确认（用户批准设计方向与演进路线）
- **范围**：`frontend/` 前台全部 9 个视图 + 全局样式；**不含** `admin/` 管理后台（建议二期）、后端、`ClaudeCodeAssistant.vue`（内部工具页）
- **参考基线**：HomeView.vue（用户认可的质量标杆）

---

## 1. 背景与问题

用户反馈：「各板块内部不统一，没有首页好看」。全量审计（9 视图 + 全局样式 + 组件库）结论：

1. **三个设计世代共存**：
   - 世代① Element Plus 默认风（AdminView、SupplyChainFinance）——EP 蓝 `#409EFF`、灰字 `#303133`、12px 卡、左边框统计卡、emoji 标题、零令牌
   - 世代② 混合风（SmartAgriculture、ColdChain、DigitalMarketing）——外壳新风格（页面头+导航卡），卡内退回 EP 灰 `#f5f7fa` + `#409eff` 数字；section 卡圆角未覆写（EP 默认 4px）
   - 世代③ 首页 Token 风（HomeView，看板/产品/分类基本接近）——`#165DFF` 主色、slate 灰阶、16px 白卡+彩色顶条、pill 标签+大标题、无 emoji
2. **全站弹窗被 `responsive.css` 用 `!important` 强加紫色渐变头**（`#667eea→#764ba2`）
3. **统计卡 4 种实现**（光条卡/左边框卡/灰底块/未使用组件），数值字号 18/20/24/28px 不一
4. **主色分裂** `#165DFF` vs `#409EFF`；**圆角 7 种**（4/6/8/10/12/14/16px）
5. **导航缺失**：顶部仅 首页/产品/分类；看板与四大业务板块只能从首页卡片进入，进入后互相不可达
6. **杂项**：emoji 标题遍布、`responsive.css` 106 个 `!important` + 大量死选择器、`critical.css` 整文件死代码、5 个共享 UI 组件写好无人用、内联样式 87 处、`ui/` 组件与 3 份导航卡 CSS 拷贝比例各异

## 2. 已确认的决策

| 决策点 | 结论 |
|--------|------|
| 范围 | 前台全部 9 视图 + 全局修复 |
| 设计方向 | **A · 全站统一品牌蓝**：所有页面一套 `#165DFF` 令牌；彩色仅用于语义状态（成功/警告/危险），不做板块身份色 |
| 导航 | **A · 平铺导航**：8 个一级入口；<1200px 收进汉堡抽屉 |
| 改造深度 | **皮肤 + 交互模式统一**：共享组件化、tab/弹窗/表格/空态规范化；不动业务逻辑与信息架构 |
| 实施路线 | **地基先行 + 逐视图迁移**（Sprint 制，符合 AGENTS.md 工作流） |

## 3. 设计系统基石

### 3.1 设计令牌（App.vue `:root` 扩充，向后兼容）

现有变量全部保留，新增语义层：

```css
--color-success: #10B981;  --color-success-bg: rgba(16,185,129,.1);
--color-warning: #F59E0B;  --color-warning-bg: rgba(245,158,11,.1);
--color-danger:  #EF4444;  --color-danger-bg:  rgba(239,68,68,.1);
--color-info:    #64748B;  --color-info-bg:    #F1F5F9;
```

**圆角规则（4 档收死，全站唯一）**：

| 层级 | 值 | 用于 |
|------|----|------|
| 卡片 | `--radius-lg` 16px | StatCard / SectionCard / 弹窗 |
| 图标 chip 与 hero 大按钮 | `--radius-md` 12px | 52px 图标 chip、首页 hero 按钮（自定义按钮） |
| 按钮与输入 | `--radius-sm` 8px | el-button（`--el-border-radius-base`）、输入框、tab 项、表格内操作 |
| pill | 100px | 状态标签、hero badge |

**间距基准**：页面留白 24px（移动端 16px）、区块间距 24px、卡内边距 20px/24px、栅格 gap 16-24px。

### 3.2 Element Plus 主题接管（一处覆盖，全站生效）

新建 `src/styles/element-theme.css` 并在 `main.ts` 引入：

```css
:root {
  --el-color-primary: #165DFF;
  --el-color-primary-light-3: #5B8BFF;   /* 按约定计算 EP 的 light-3/5/7/8/9、dark-2 变体 */
  --el-color-success: var(--color-success);
  --el-color-warning: var(--color-warning);
  --el-color-danger: var(--color-danger);
  --el-border-radius-base: 8px;
  --el-text-color-primary: #0F172A;
  --el-text-color-regular: #475569;
  --el-border-color: #E2E8F0;
  --el-fill-color-light: #F8FAFC;
}
```

- 效果：所有 `el-button/el-table/el-tag/el-dialog/el-form/el-select…` 自动品牌蓝，`#409EFF` 全站清零
- **弹窗全站标准**：16px 圆角、白底平头（无渐变）、标题 16px/600 + 底分隔线、底部按钮右对齐、宽度三档 480/640/800px（全屏类 90%）
- **表格全站标准**：表头 `#F8FAFC` + `#475569` 600 字重、行 hover `#F8FAFC`、外框圆角 8px——删除各页内联 `:header-cell-style`

### 3.3 responsive.css 清理

- 删除：紫色弹窗块、全部死选择器（`.el-main`、旧 `.stat-info h3`、`.products-container .header`、与 HomeView 冲突的 `.module-card/.feature-card` 覆写）
- `!important` 106 → 0；移动端容器留白统一 16px
- 保留必要的移动端栅格降级规则，改为令牌化写法

### 3.4 共享组件库（`src/components/ui/` 扶正）

| 组件 | 状态 | 职责 |
|------|------|------|
| `StatCard` | 已存在，对齐令牌后启用 | **唯一统计卡**：白底 16px + 1px 边 + 顶部 4px 语义色条 + 图标 chip（52px/12px/`--bg-secondary`）+ 数值 26px/700/-0.02em + 标签 12px/`--text-tertiary` + 可选趋势 pill |
| `SectionCard` | **新增** | **唯一区块卡**：16px 圆角 + 头（20px/24px，标题 15px/600 + 可选图标）+ 底分隔线 + 体（20px/24px）；替代裸 el-card |
| `PageHeader` | **新增** | **唯一页面头**：标题 28px/700/-0.02em + 副标题 14px/`--text-secondary` + 右侧 actions slot；替代 6 份拷贝 |
| `NavCard` | 已存在，对齐令牌后启用 | 板块内导航卡：14px 圆角 + 3px 顶光条 + hover -4px；三份拷贝归一（统一 padding 20px/16px、chip 52px/12px） |
| `EmptyState` | 已存在，启用 | 列表空态统一 |
| `MotionCard` | 已存在，按需 | 通用动效卡 |

### 3.5 交互规范

- **标题零 emoji**；需要图标处用 EP icon 组件（图标 chip 形态）
- **板块内部导航**：NavCard 网格 + `v-show` 切换（保持地图等重组件状态）；冷链 11 项重排为按业务分组排序的网格（监测/仓储/运输/运营四组，允许换行），不做横向滚动
- **按钮**：主/次操作用主题化 `el-button`；自定义 `.btn-primary` 拷贝全部删除；hero 大按钮仅首页保留
- **表格操作列**：EP link 按钮（primary/危险色）
- **表单**：el-form 默认间距，内联 `margin-bottom` 清零（87 处）
- **空态/加载**：EmptyState + 现有骨架屏体系；区块级 `v-loading`
- **金额格式统一**：`formatMoney` 收敛为一份共享工具（万/亿两级）

## 4. 导航落地（App.vue）

- `navItems` 平铺 8 项：首页 / 产品 / 分类 / 看板 / 智慧农业 / 数字营销 / 冷链物流 / 供应链金融；`管理后台` 保留 admin-only
- ≥1200px 全平铺；<1200px 汉堡抽屉（EP drawer，含全部导航项 + 用户区）
- 修复首页 hero CTA：「进入控制台」（已登录）应跳看板而非产品页
- keep-alive 缓存白名单核对（现缓存 Products/Categories/Dashboard）

## 5. Sprint 演进计划

| Sprint | 内容 | 验收标准 |
|--------|------|---------|
| **U1 地基** | 令牌扩充；element-theme.css；responsive.css 清理；共享组件扶正（StatCard/SectionCard/PageHeader/NavCard/EmptyState）；App.vue 平铺导航 + 汉堡菜单；Login/Register 重皮 | 全站 EP 组件品牌蓝、弹窗白底、导航可达全部板块；`vue-tsc`+`build`+`agent-lint` 通过；全路由走查无回归 |
| **U2 世代①清除** | AdminView、SupplyChainFinance：`.header`→PageHeader；统计→StatCard；区块→SectionCard；EP 灰→令牌；去 emoji；金额格式统一 | 两页与首页同代；上述工具全绿 |
| **U3 世代②核心** | SmartAgriculture、ColdChain 内部：灰底统计块→StatCard；section 卡统一 SectionCard（修冷链 4px 圆角）；导航卡→NavCard 组件（冷链 11 项重排）；内联样式清零；tab 统一 v-show | 四板块外壳与内部完全一致；工具全绿 |
| **U4 世代②③收尾** | DigitalMarketing 列表模式统一；Dashboard/Products/Categories 轻对齐：去 emoji、删 `:header-cell-style`、自定义按钮→el-button、dialog `:deep` 覆盖删除 | 全站无旧世代残留；工具全绿 |
| **U5 清扫+回归** | HomeView 死 CSS（~90 行）删除、hero CTA 修复；`critical.css` 删除；全路由人工走查 + 前后截图对比 | 交付；`agent-lint` 0 error |

每个 Sprint 收尾：自评估表（4 维度）+ 测试通过后才进入下一个。

## 6. 边界与风险

- **纯表现层**：不改任何 API 调用、数据流、业务逻辑；不碰后端与 `funeng.db`
- 唯一行为变化 = 导航新增入口（新增链接，路由表不动）
- AMap 地图实例依赖 v-show 保持不重建（统一 tab 机制时验证）
- EP 主题变量覆盖需逐个核对 light-3/5/7/8/9 变体，防止 hover/disabled 态颜色失真
- 移动端回归：responsive.css 重写后逐页核对 ≤768px 表现

## 7. 整体验收

1. `npx vue-tsc --noEmit`、`npm run build`、`bash scripts/agent-lint.sh` 全绿
2. 9 视图人工走查：同代视觉、无 emoji 标题、无 `#409EFF`、无紫弹窗（`grep -r "409EFF\|409eff\|667eea" src` 为 0）
3. 导航 8 项可达各板块，板块间一键互达；<1200px 汉堡抽屉可用
4. 移动端（≤768px）逐页走查无破版

## 附录 A：视图现状审计表

| 视图 | 色彩体系 | 卡片圆角 | 页头模式 | 世代 |
|------|---------|---------|---------|------|
| HomeView（基准） | 100% 令牌 | 16px | pill 标签+36px 标题 | ③ |
| DashboardView | 令牌+回退 | 16px | 28px 标题（含 emoji） | ③ |
| ProductsView | 令牌+回退 | 16px | 28px 标题（含 emoji） | ③ |
| CategoriesView | 令牌（默认色 bug `#165DFF`vs`#409eff`） | 16px | 28px 标题（含 emoji） | ③ |
| SmartAgriculture | 外令牌/内 EP | 16px 区块卡；内卡 4px | 28px 标题 + emoji 卡头 | ② |
| ColdChain | 外令牌/内 EP | section 卡未覆写（4px） | 28px 标题 + emoji 卡头 | ② |
| DigitalMarketing | 外令牌/内 EP+品牌色 | section 卡 4px | 28px 标题 + emoji 卡头 | ② |
| AdminView | 无令牌，EP 灰 | 12px | `.header h2` 24px `#303133` | ① |
| SupplyChainFinance | 无令牌，EP 灰 | 12px | `.header h2` 24px `#303133` | ① |

（完整审计：三个 nav-card CSS 拷贝比例差异、36/35/16 处内联样式、4 种统计卡字号、7 种圆角——详见会话审计记录；本表为迁移核对清单。）

# Sprint Handoff Artifact

> 结构化 handoff 用于 Context Reset 时传递状态给下一个 Agent
> 灵感来自 Anthropic 的长运行 Agent harness 设计

---

## Sprint 基本信息

| 字段 | 值 |
|------|-----|
| **Sprint 编号** | [1/2/3/...] |
| **功能名称** | [功能描述] |
| **开始时间** | YYYY-MM-DD HH:mm |
| **结束时间** | YYYY-MM-DD HH:mm |
| **耗时** | [X] 小时 |
| **状态** | [✅ 完成 / ❌ 打回 / ⏸️ 暂停] |

---

## 完成状态

### ✅ 已完成
- [ ] [功能点 1]
- [ ] [功能点 2]
- [ ] [功能点 3]

### ❌ 未完成
- [ ] [功能点 + 原因]

### ⚠️ 已知问题
- [ ] [问题描述 + 影响范围]

---

## Sprint 评估结果

### Generator 自评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 功能完整性 | /40 | |
| 代码质量 | /30 | |
| 视觉设计 | /20 | |
| 测试覆盖 | /10 | |
| **总分** | **/100** | |

### Evaluator 评估

| 维度 | 评分 | 通过？ | 反馈 |
|------|------|--------|------|
| 功能完整性 | /40 | ✅/❌ | |
| 代码质量 | /30 | ✅/❌ | |
| 视觉设计 | /20 | ✅/❌ | |
| 测试覆盖 | /10 | ✅/❌ | |
| **结果** | | **通过/打回** | |

**打回原因（如适用）：**
```
[详细描述需要改进的地方]
```

---

## 下一步计划

### 立即可做的（Next Agent 优先处理）
1. [具体步骤 + 预计时间]
2. [具体步骤 + 预计时间]
3. [具体步骤 + 预计时间]

### 需要龙主决策的
- [ ] [决策点 + 选项 A/B/C]

### 风险与注意事项
- ⚠️ [风险描述 + 缓解措施]

---

## 关键决策记录

| 决策 | 原因 | 日期 | 影响 |
|------|------|------|------|
| | | | |

---

## 代码变更摘要

### 新增文件
```
- frontend/src/views/NewFeature.vue
- backend/app/api/new_feature.py
```

### 修改文件
```
- frontend/src/router/index.ts (添加路由)
- backend/app/main.py (注册 API)
```

### 关键代码片段
```typescript
// 重要实现细节或复杂逻辑
```

---

## 测试验证清单

- [ ] 本地运行通过
- [ ] Lint 检查通过 (`bash scripts/agent-lint.sh`)
- [ ] 类型检查通过 (`npx tsc --noEmit`)
- [ ] 核心功能手动测试通过
- [ ] 无控制台错误

---

## Context Reset 说明（如适用）

**重置原因：**
- [ ] 上下文窗口接近限制
- [ ] 任务超过 [X] 小时
- [ ] Agent 表现下降（context anxiety）
- [ ] 其他：[说明]

**下一 Agent 需要知道的关键信息：**
1. [关键状态]
2. [未完成的工作]
3. [需要避免的陷阱]

**下一 Agent 的起始指令：**
```
[明确的起始任务描述]
```

---

## 附录：相关文件

- [ARCHITECTURE.md](./ARCHITECTURE.md) — 架构文档
- [QUALITY.md](./QUALITY.md) — 质量标准
- [CONVENTIONS.md](./CONVENTIONS.md) — 代码约定
- [RESILIENCE.md](./RESILIENCE.md) — Agent 恢复协议

---

*Handoff 生成时间：YYYY-MM-DD HH:mm | Generator: [Agent 名称] | Evaluator: 龙主*

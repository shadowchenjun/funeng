# Execution Plan: Vercel 部署修复

## Status: Review
## Complexity: High
## Packages affected: frontend, backend（部署配置）

---

## Goal

让前端项目从 `frontend/` 完成可复现构建并返回页面；查明后端项目的构建和运行条件，在持久化存储与生产密钥满足要求后再发布 API。

---

## Sprint Plan

### Sprint 1: 前端构建与部署

- [x] 确认 Vercel 项目根目录和框架配置
- [x] 修复依赖锁文件并通过冻结安装
- [x] 本地构建和类型检查
- [x] 生产部署并验证首页、静态资源和 API 行为

**自评估（静态前端部署）：**功能完整性 80/100（页面可访问，API 未接通）；代码质量 85/100（锁文件与构建通过）；视觉设计 80/100（首页实测呈现）；测试覆盖 80/100（构建、类型检查、HTTP 与浏览器验证）。Evaluator 尚未评估。

**证据：**提交 `151723e`；Vercel 部署 `dpl_8Q5KGZPcQCqSWMngPf1rk68zhzMG` 为 READY。首页和 JS 资源返回 200；`/api/auth/me` 返回 `text/html`，业务 API 不可用。

### Sprint 2: 后端部署准备

- [x] 定位 FastAPI 入口错误
- [x] 核对持久化数据库、文件存储和生产密钥
- [ ] 确定适合当前后端的运行环境
- [ ] 部署并验证 `/health` 与业务接口

**自评估：**后端未发布，功能完整性未达到及格线；等待持久化方案和生产凭据归属确认，Evaluator 尚未评估。

---

## Decisions

| Decision | Rationale | Date |
|----------|-----------|------|
| 使用独立工作树处理锁文件 | 原工作区有其他未提交改动 | 2026-09-29 |
| 前后端分别核验 | 两个 Vercel 项目独立构建、状态不同 | 2026-09-29 |

## Known risks

- 后端默认 SQLite 与本地上传目录不适合作为无状态函数的持久存储。
- 后端源码包含测试账号初始化逻辑，生产发布前需消除默认凭据风险。
- 后端 Vercel 项目根目录为空，构建报 `FASTAPI_ENTRYPOINT_NOT_FOUND`；前端的 SPA rewrite 把 `/api/*` 返回为 HTML。

# Execution Plan: Supabase 持久化与生产部署

## Status: Review
## Complexity: High
## Packages affected: backend, frontend, deployment configuration

## Goal

将赋能平台现有 SQLite 业务数据安全迁移到该平台专用的 Supabase Postgres；将上传图片与导出文件保存在 Supabase Storage，导出状态保存在 Postgres；完成 Vercel 后端和前端 API 接线，验证重启及跨请求的数据持久性。生产密钥通过平台环境变量保存，避免将已有测试口令作为生产凭据。

## Sprint Plan

### Sprint 1: 资源与数据盘点

- [x] 盘点本地 SQLite 的 38 张表、53 条记录、2 个图片文件及内存状态
- [x] 核对已有 Supabase 项目归属与运行状态
- [x] 确定项目组织、费用、区域及数据迁移边界
- [x] 核对 Vercel 环境变量的实际资源归属

**自评估：**38/40 功能完整性，27/30 代码质量，18/20 视觉设计（前端未改视觉），9/10 测试覆盖，总分 92/100。**Evaluator：**待龙主评估。

### Sprint 2: 后端持久化改造

- [x] Postgres 连接与迁移脚本，原 SQLite 保留备份
- [x] 将冷链原生 SQLite 查询接入 SQLAlchemy
- [x] 将上传图片及导出结果接入私有或受控 Storage bucket
- [x] 将导出任务状态接入 Postgres，移除跨实例内存依赖
- [x] 去掉生产环境默认测试账号与硬编码 JWT 密钥
- [x] 补充核心路径和失败路径测试，运行本地门禁

**自评估：**34/40 功能完整性，25/30 代码质量，18/20 视觉设计（无视觉变更），8/10 测试覆盖，总分 85/100。**Evaluator：**待龙主评估。

### Sprint 3: 迁移及部署验证

- [x] 建立 Supabase 表、bucket、访问策略
- [x] 迁移本地业务数据和已有上传文件，核对数量与关系
- [x] 配置 Vercel 后端环境变量与 FastAPI 入口
- [ ] 配置前端 API 路由，重新部署并验证登录、查询、上传、导出
- [ ] 记录生产访问地址、管理员账号交付方式与残余风险

**自评估：**30/40 功能完整性（缺生产数据库连接串和线上回归），27/30 代码质量，18/20 视觉设计（无视觉变更），7/10 测试覆盖，总分 82/100。**Evaluator：**待龙主评估。

## Decisions

| Decision | Rationale | Date |
|----------|-----------|------|
| 待确定恢复现有项目或新建项目 | Vercel 前端的 SUPABASE_URL 已指向暂停的 `uzxmomyfgkqkbxxkzskc`，其组织为免费套餐 | 2026-09-29 |
| 在现有管理工作树实施 | 原工作区有其他未提交工作，须完整保留 | 2026-09-29 |

## Known risks

- 本地数据库包含用户和管理员账户密码哈希，迁移前须确认项目归属及生产账号策略。
- 旧代码在模块导入时自动建表和创建测试账号，不能原样发布到生产。
- 现有 Vercel 前端虽可访问，但 `/api/*` 被 SPA rewrite 返回 HTML。

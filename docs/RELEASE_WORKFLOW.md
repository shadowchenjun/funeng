# 部署与发布流程

约定日期：2026-10-02。后续发布默认遵循本流程。测试证据与平台配置必须分别核实，文档中的要求不代表自动化已经启用。

## 1. 发布主流程

```text
功能分支 / PR
  → 类型检查、单元测试、后端测试与构建
  → Preview 部署与浏览器业务验收
  → 合并到经核实的生产分支
  → 使用 Production 配置构建，暂不分配正式域名
  → 在该生产部署 URL 上验收
  → Promote 已验收的生产部署
  → 正式域名冒烟检查与发布记录
```

任一必须检查失败，停止后续阶段并修复。业务上线必须保留提交 SHA、部署 ID、验收结果和可回滚版本。平台显示 READY 只代表部署就绪，不能替代业务验收。

## 2. 本仓库的实际入口

| 内容 | 本地检查 | 发布对象 |
| --- | --- | --- |
| 前台 Vue 3 / TypeScript | `npm --prefix frontend test`、`npm run lint`、`npm run build` | Vercel `funeng-7p1i`，根目录 `frontend` |
| 管理后台 Vue 3 / TypeScript | `npm run lint`、`npm run build` | 发布前核实目标项目与域名 |
| FastAPI / SQLAlchemy 后端 | `npm test` | Vercel `funeng`，根目录 `backend` |
| 仓库综合门禁 | `bash scripts/agent-lint.sh` | 类型、前端测试、pytest、密钥与界面规范检查 |
| 数据与文件 | 迁移核查、权限核查、对象读写验证 | 外部 PostgreSQL 与私有 Storage，详见部署手册 |

`npm run lint` 当前是 Vue 类型检查，不是 ESLint；`npm test` 当前是后端 pytest，不能代表浏览器 E2E 已通过。前台已有 Node 测试；管理后台与页面交互需要另行验收。

截至本次整理，仓库没有 `.github/workflows/`。上述脚本存在，GitHub 自动执行、受保护分支的必需状态检查、Vercel Deployment Checks 和自动 E2E 门禁仍需单独配置、验证。配置前由发布执行者逐项运行和记录，不得称为已经自动阻断。

## 3. Preview 验收

1. 确认前端、后端目标 SHA 与 PR 一致；记录各项目独立的部署 ID。
2. Preview 前端必须调用对应 Preview 后端；检查 `/api/*` rewrite，不能只验证页面外壳。
3. 使用隔离的测试数据库、测试账号和 Storage；测试写入与补采不应默认写到生产数据。
4. 业务变更验证登录、权限、产品列表、大屏/API 数据一致性、空状态与失败提示；根据变更覆盖上传、导出、采集幂等和任务日志。
5. 文档发布验证目录卡片、文章正文、导航和链接。构建成功与页面可读分别留证。

## 4. 生产构建与推广

生产分支名不能靠猜测；从 Git/Vercel 配置核实。Git 集成默认可能在生产分支构建后直接绑定正式域名，即使其他 CI 还没结束。

对采用暂存生产版本的项目，在 Vercel **Settings → Environments → Production → Branch Tracking** 关闭 **Auto-assign Custom Production Domains**。每个项目分别检查设置。它控制发布时机，不需要改动 DNS。

随后使用 Production 环境配置创建生产部署，确认正式域名仍指向旧版本。在独立部署 URL 验收通过后 Promote 此生产部署；推广时不再重新构建。预览环境测试通过后仍需检查生产配置，不能直接假设两套环境相同。

已授权且登录的 CLI 也可使用 `vercel deploy --prod --skip-domain` 创建暂存生产部署，随后 `vercel promote <deployment-url-or-id>`。预构建模式须先拉取 Production 配置并执行 `vercel build --prod`；CI 固定 CLI 版本，凭据保存在 CI Secrets，不写入文档或仓库。

多项目发布采用同一目标 SHA。兼容性扩展先发布后端，再发布依赖新接口的前端；验收旧前端与新后端仍能配合。无法兼容的改动先拆分迁移阶段，不把多个项目的部署误认为一次原子切换。

## 5. 数据迁移、定时任务与回滚

- 数据库迁移优先新增表/字段，先扩展、迁移和验证，再另一次发布移除旧结构。执行前保存备份或恢复点，记录迁移版本、影响和权限核查。
- Preview 的检查与真实生产 Cron 调度分别验证。试跑使用受保护入口和隔离数据，记录新增/更新行数、重复处理、失败重试；首次计划触发后再确认真实自动调度成功。
- 正式域名检查包括登录、核心 API、关键页面、文件访问，以及实际数据源和错误日志。生产写入测试使用明确的测试账号/对象。
- 代码故障可切回上一次已知正常部署；应用回滚不会撤销数据库迁移、删除记录或恢复文件。数据恢复按独立预案执行，避免用不兼容的旧代码访问新结构。

## 6. 发布记录模板

```text
日期 / 执行者：
变更范围 / PR：
仓库 / 分支 / 完整 SHA：
本地检查：命令、结果、未通过项
Preview：前端与后端 URL、部署 ID、业务验收
生产暂存：URL、部署 ID、Production 配置核查
正式域名仍指向旧版本的证据：
推广：目标部署、时间、正式域名
正式环境验收：页面、API、数据与日志结果
迁移 / Cron：执行结果；未验证项明确列出
回滚：旧部署 ID、数据恢复点、兼容性限制
```

## 7. 相关资料

- [Supabase / Vercel 部署手册](SUPABASE_DEPLOYMENT.md)
- [质量标准](QUALITY.md)
- [官网 CI/CD 学习笔记](https://www.lobstermaster.me/project-learning/vercel-ci-release-workflow)
- [Vercel 暂存生产版本与 Promote](https://vercel.com/docs/deployments/promoting-a-deployment)
- [Vercel GitHub 集成](https://vercel.com/docs/git/vercel-for-github)
- [GitHub 分支保护](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

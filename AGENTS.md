# AGENTS.md — funeng Agent Harness

现代农业赋能平台：Vue 3 前台（冷链/智慧农业/数字营销/供应链金融）+ Vue 3 管理后台 + FastAPI/SQLite 后端。
This file is a **table of contents** — not a reference manual. Follow the links.

> **Context depth guide (progressive disclosure):**
> - **L1 (here):** orientation, commands, invariants — read this first
> - **L2 (`docs/`):** architecture, quality standards, conventions — read before coding
> - **L3 (source):** implementation details — pull on demand via grep/read tools
>
> Do not dump L2/L3 into your context unless you need it. Pull, don't pre-load.

---

## Repo Map

```
  backend/    FastAPI + SQLAlchemy + SQLite（main.py 入口，app/config.py 读环境变量，tests/ 为 pytest）
  frontend/   前台 Vue 3 + TS + Vite（:5173，代理 /api → :8000）
  admin/      管理后台 Vue 3 + TS + Vite（:3001，调用 /api/admin/*）
  docs/       架构、质量标准、执行计划（docs/plans/）
  scripts/    agent-lint.sh
```

**环境变量**（生产必须设置）：`SECRET_KEY`、`ADMIN_SECRET_KEY`、`DATABASE_URL`、`CORS_ORIGINS`

---

## Docs (start here before touching code)

| File | What it covers |
|------|---------------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Layer rules, dependency graph, key invariants |
| [`docs/QUALITY.md`](docs/QUALITY.md) | Coverage targets, security rules, **Sprint 评估标准** |
| [`docs/RELEASE_WORKFLOW.md`](docs/RELEASE_WORKFLOW.md) | 检查、Preview 验收、生产暂存与正式推广、回滚记录 |
| [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md) | Naming conventions, code style |
| [`docs/RESILIENCE.md`](docs/RESILIENCE.md) | Agent recovery protocols, 7-point checklist, VBR standards |
| [`docs/EXECUTION_PLAN_TEMPLATE.md`](docs/EXECUTION_PLAN_TEMPLATE.md) | **Sprint 制**执行计划模板 |
| [`docs/HANDOFF_TEMPLATE.md`](docs/HANDOFF_TEMPLATE.md) | Context Reset handoff artifact |

---

## How to Build & Test

```bash
npm run setup            # 安装 frontend/admin 依赖 + backend/.venv
npm test                 # 后端 pytest（临时数据库，不会改动 funeng.db）
npm run lint             # frontend + admin 类型检查
bash scripts/agent-lint.sh   # 类型检查 + 测试 + 密钥/长度检查
npm run dev:backend | dev:frontend | dev:admin
```

---

## Agent Invariants (non-negotiable)

1. **Always run tests before opening a PR.** Never break existing tests.
2. **Check docs/ARCHITECTURE.md before adding cross-package dependencies.**
3. **All new public APIs must have documentation.**
4. **Run `bash scripts/agent-lint.sh` locally.** Failures include fix instructions.
5. **For complex tasks** (multiple packages, new APIs, migrations), create an execution
   plan using `docs/EXECUTION_PLAN_TEMPLATE.md` before writing code.
6. **Work in Sprints.** One feature at a time, evaluate after each sprint.
7. **Fill HANDOFF_TEMPLATE.md** before context reset or task handoff.
8. **Follow `docs/RELEASE_WORKFLOW.md` for releases.** Verify production config before promoting the tested production deployment.

---

## Sprint Workflow（Anthropic 启发式）

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Generator  │ →   │   自评估     │ →   │  Evaluator  │
│  (实现功能)  │     │ (填评分表)   │     │  (龙主测试)  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┘
                    │
           ┌────────▼────────┐
           │  通过？          │
           │  ✅ 继续下一 Sprint │
           │  ❌ 打回重做      │
           └─────────────────┘
```

**每个 Sprint 必须：**
1. 实现一个完整功能
2. 填写自评估表（4 维度评分）
3. 通过 Evaluator 评估（任何维度低于及格线 → 打回）
4. 填写 HANDOFF_TEMPLATE.md（如需 context reset）

---

## CI Gates

Every PR must pass agent-lint + tests + lints. Automatic enforcement must be verified separately; see `docs/RELEASE_WORKFLOW.md`.

---

*This file must stay under 150 lines. See `scripts/agent-lint.sh`.*

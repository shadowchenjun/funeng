# AGENTS.md — funeng Agent Harness

[One sentence describing what this repo does.]
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
  backend/
  frontend/
```

---

## Packages (0 total)

```
  (see source directories)
```

---

## Docs (start here before touching code)

| File | What it covers |
|------|---------------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Layer rules, dependency graph, key invariants |
| [`docs/QUALITY.md`](docs/QUALITY.md) | Coverage targets, security rules, **Sprint 评估标准** |
| [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md) | Naming conventions, code style |
| [`docs/RESILIENCE.md`](docs/RESILIENCE.md) | Agent recovery protocols, 7-point checklist, VBR standards |
| [`docs/EXECUTION_PLAN_TEMPLATE.md`](docs/EXECUTION_PLAN_TEMPLATE.md) | **Sprint 制**执行计划模板 |
| [`docs/HANDOFF_TEMPLATE.md`](docs/HANDOFF_TEMPLATE.md) | Context Reset handoff artifact |

---

## How to Build & Test

```bash
# Run all tests
npm test

# Run lints
npm run lint

# Run agent-specific lints (architectural invariants)
bash scripts/agent-lint.sh
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

Every PR runs agent-lint + tests + lints. All must pass.

---

*This file must stay under 150 lines. See `scripts/agent-lint.sh`.*
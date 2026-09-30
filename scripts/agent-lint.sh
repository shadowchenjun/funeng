#!/bin/bash
# Agent harness linter — errors are agent-readable
set -uo pipefail
ERRORS=0
cd "$(git rev-parse --show-toplevel)"
echo "=== Agent Lint ==="

# Rule 1: 前台与管理后台类型检查必须通过
for pkg in frontend admin; do
  echo "[1/7] vue-tsc ($pkg)..."
  if [ ! -d "$pkg/node_modules" ]; then
    echo "LINT ERROR [missing-deps]: $pkg/node_modules not found"
    echo "  FIX: run 'npm run setup' at repo root."
    ERRORS=$((ERRORS+1))
  elif ! (cd "$pkg" && npx vue-tsc --noEmit); then
    echo "LINT ERROR [build-failure]: TypeScript compilation failed in $pkg/"
    echo "  FIX: Fix all type errors shown above."
    ERRORS=$((ERRORS+1))
  fi
done

# Rule 2: 后端测试必须通过
echo "[2/7] backend pytest..."
if [ ! -x backend/.venv/bin/python ]; then
  echo "LINT ERROR [missing-deps]: backend/.venv not found"
  echo "  FIX: run 'npm run setup' at repo root."
  ERRORS=$((ERRORS+1))
elif ! (cd backend && .venv/bin/python -m pytest -q tests); then
  echo "LINT ERROR [test-failure]: backend tests failed"
  echo "  FIX: Fix the failing tests shown above. Never delete a test to make it pass."
  ERRORS=$((ERRORS+1))
fi

# Rule 3: any 类型（警告）
echo "[3/7] Checking any types..."
ANY_COUNT=$(grep -rn ": any" frontend/src admin/src --include='*.ts' --include='*.vue' 2>/dev/null | grep -v "\.d\.ts:" | wc -l | tr -d ' ')
if [ "$ANY_COUNT" -gt 0 ]; then
  echo "LINT WARNING [unsafe-any]: $ANY_COUNT uses of ': any' in frontend/src + admin/src"
  echo "  FIX: Replace with specific types or unknown."
  echo "  REF: docs/CONVENTIONS.md"
fi

# Rule 4: 源码中不得硬编码 JWT 密钥
echo "[4/7] Checking hard-coded secrets..."
if grep -rnE "SECRET_KEY\s*=\s*['\"]" backend/app backend/main.py --include='*.py' 2>/dev/null; then
  echo "LINT ERROR [hardcoded-secret]: JWT secret assigned as a string literal"
  echo "  FIX: Read secrets from environment via backend/app/config.py."
  ERRORS=$((ERRORS+1))
fi

# Rule 5/6: 前台 UI 统一（docs/superpowers/specs/2026-10-01-frontend-ui-unification-design.md §7）
# 迁移期（U1–U4）为警告；U5 起设 UI_STRICT=1 升级为 error
UI_STRICT="${UI_STRICT:-0}"
ui_violation() {
  if [ "$UI_STRICT" = "1" ]; then
    echo "LINT ERROR [$1]: $2"
    ERRORS=$((ERRORS+1))
  else
    echo "LINT WARNING [$1]: $2"
  fi
}

echo "[5/7] Checking legacy UI colors..."
LEGACY_COLORS=$(grep -rniE "409eff|667eea|764ba2|64, ?158, ?255" frontend/src --include='*.vue' --include='*.css' --include='*.ts' 2>/dev/null)
if [ -n "$LEGACY_COLORS" ]; then
  ui_violation "legacy-color" "$(echo "$LEGACY_COLORS" | wc -l | tr -d ' ') legacy Element/purple colors in frontend/src"
  echo "$LEGACY_COLORS" | sed 's/^/    /' | head -20
  echo "  FIX: Use design tokens (var(--primary), var(--color-*)) from App.vue :root."
fi

echo "[6/7] Checking emoji in templates..."
EMOJI_HITS=$(python3 - <<'PY'
import pathlib, re
emoji = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2B55]")
for f in sorted(pathlib.Path("frontend/src").rglob("*.vue")):
    if f.name == "ClaudeCodeAssistant.vue":
        continue
    text = f.read_text(encoding="utf-8")
    end = text.rfind("</template>")
    for i, line in enumerate(text[:end].splitlines(), 1):
        if emoji.search(line):
            print(f"{f}:{i}: {line.strip()[:80]}")
PY
)
if [ -n "$EMOJI_HITS" ]; then
  ui_violation "emoji-in-template" "$(echo "$EMOJI_HITS" | wc -l | tr -d ' ') template lines with emoji in frontend/src"
  echo "$EMOJI_HITS" | sed 's/^/    /' | head -20
  echo "  FIX: Replace emoji with Element Plus icon components (see spec §3.4 icon table)."
fi

# Rule 7: AGENTS.md 长度
echo "[7/7] Checking AGENTS.md length..."
if [ -f AGENTS.md ] && [ "$(wc -l < AGENTS.md)" -gt 150 ]; then
  echo "LINT ERROR [agents-too-long]: AGENTS.md exceeds 150 lines"
  echo "  FIX: Move details to docs/ and replace with pointers."
  ERRORS=$((ERRORS+1))
fi

echo "=== Lint: $ERRORS error(s) ==="
[ $ERRORS -eq 0 ] || exit 1
echo "All checks passed. ✓"

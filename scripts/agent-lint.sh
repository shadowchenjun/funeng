#!/bin/bash
# Agent harness linter — errors are agent-readable
set -uo pipefail
ERRORS=0
cd "$(git rev-parse --show-toplevel)"
echo "=== Agent Lint ==="

# Rule 1: 前台与管理后台类型检查必须通过
for pkg in frontend admin; do
  echo "[1/5] vue-tsc ($pkg)..."
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
echo "[2/5] backend pytest..."
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
echo "[3/5] Checking any types..."
ANY_COUNT=$(grep -rn ": any" frontend/src admin/src --include='*.ts' --include='*.vue' 2>/dev/null | grep -v "\.d\.ts:" | wc -l | tr -d ' ')
if [ "$ANY_COUNT" -gt 0 ]; then
  echo "LINT WARNING [unsafe-any]: $ANY_COUNT uses of ': any' in frontend/src + admin/src"
  echo "  FIX: Replace with specific types or unknown."
  echo "  REF: docs/CONVENTIONS.md"
fi

# Rule 4: 源码中不得硬编码 JWT 密钥
echo "[4/5] Checking hard-coded secrets..."
if grep -rnE "SECRET_KEY\s*=\s*['\"]" backend/app backend/main.py --include='*.py' 2>/dev/null; then
  echo "LINT ERROR [hardcoded-secret]: JWT secret assigned as a string literal"
  echo "  FIX: Read secrets from environment via backend/app/config.py."
  ERRORS=$((ERRORS+1))
fi

# Rule 5: AGENTS.md 长度
echo "[5/5] Checking AGENTS.md length..."
if [ -f AGENTS.md ] && [ "$(wc -l < AGENTS.md)" -gt 150 ]; then
  echo "LINT ERROR [agents-too-long]: AGENTS.md exceeds 150 lines"
  echo "  FIX: Move details to docs/ and replace with pointers."
  ERRORS=$((ERRORS+1))
fi

echo "=== Lint: $ERRORS error(s) ==="
[ $ERRORS -eq 0 ] || exit 1
echo "All checks passed. ✓"

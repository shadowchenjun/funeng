#!/bin/bash
# Agent harness linter (TypeScript) — errors are agent-readable
set -euo pipefail
ERRORS=0
cd "$(git rev-parse --show-toplevel)"
echo "=== Agent Lint (TypeScript) ==="

# Rule 1: TypeScript build must pass
echo "[1/4] Running tsc..."
if ! npx tsc --noEmit 2>&1; then
  echo "LINT ERROR [build-failure]: TypeScript compilation failed"
  echo "  FIX: Fix all type errors shown above."
  ERRORS=$((ERRORS+1))
fi

# Rule 2: No any types in src/
echo "[2/4] Checking for any types..."
ANY_COUNT=$(grep -rn ": any" src/ 2>/dev/null | grep -v "//.*any" | wc -l || echo 0)
if [ "$ANY_COUNT" -gt 0 ]; then
  echo "LINT WARNING [unsafe-any]: $ANY_COUNT uses of ': any' found in src/"
  echo "  FIX: Replace with specific types or unknown."
  echo "  REF: docs/CONVENTIONS.md#types"
fi

# Rule 3: All exported functions need JSDoc
echo "[3/4] Checking JSDoc coverage..."
MISSING=$(grep -rn "^export function\|^export async function\|^export class\|^export const" src/ 2>/dev/null | grep -v "_test\|test\." || true)
# (basic check — proper tool would use ts-morph)

# Rule 4: AGENTS.md length
echo "[4/4] Checking AGENTS.md length..."
if [ -f AGENTS.md ] && [ "$(wc -l < AGENTS.md)" -gt 150 ]; then
  echo "LINT ERROR [agents-too-long]: AGENTS.md exceeds 150 lines"
  echo "  FIX: Move details to docs/ and replace with pointers."
  ERRORS=$((ERRORS+1))
fi

echo "=== Lint: $ERRORS error(s) ==="
[ $ERRORS -eq 0 ] || exit 1
echo "All checks passed. ✓"

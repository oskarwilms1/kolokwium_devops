#!/usr/bin/env bash
set -euo pipefail

fail=0

# Zabronione debugowe `print(` w app/ (kod produkcyjny).
if grep -rn '^\s*print(' app/ 2>/dev/null; then
  echo "lint: forbidden print() in app/" >&2
  fail=1
fi

# Składnia każdego pliku .py
while IFS= read -r f; do
  if ! python3 -m py_compile "$f" 2>/tmp/lint.err; then
    echo "lint: syntax error in $f" >&2
    cat /tmp/lint.err >&2
    fail=1
  fi
done < <(find app -name '*.py' -type f)

if [ "$fail" -ne 0 ]; then
  exit 1
fi

echo "lint OK"

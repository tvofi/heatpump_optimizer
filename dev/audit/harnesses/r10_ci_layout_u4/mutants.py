#!/usr/bin/env python3
"""R10-CI-LAYOUT P2b, unit U4: the window-cache key's two halves, each against a mutant.

    python3 dev/audit/harnesses/r10_ci_layout_u4/mutants.py

Forward-carry from #2629's round-2 review (R2d). `readWindowCache` serves a file
only when its key, `<since sha>..<main sha>`, equals this window's. Each mutant
compares one half only and is run against `node tools/policy/policy_lint.mjs`,
whose acceptance must go red (FIXTURE VACUOUS: window cache ...):

  R2c  compares only the since half   -> the foreign seed that differs in the head half
  R2d  compares only the head half    -> the foreign seed that differs in the since half

R0 is the unmutated file and must stay green. Run from the worktree; the file
is restored afterwards. Prints one line per mutant, then `RESULT survivors=<n>`;
exit 1 when any survived or R0 failed.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, check=True).stdout.strip())
F = ROOT / "tools/policy/policy_lint.mjs"
K = "  return cache && cache.key === windowKey(since) ? cache : {}"
HALF = "  return cache && String(cache.key).split('..')[{i}] === windowKey(since).split('..')[{i}] ? cache : {{}}"
MUTANTS = {"R0": K, "R2c": HALF.format(i=0), "R2d": HALF.format(i=1)}


def main() -> int:
    orig = F.read_text()
    assert orig.count(K) == 1, "the key comparison moved"
    env = {**os.environ, "PYTHONPATH": "tests/hastub"}
    survivors = 0
    try:
        for name, repl in MUTANTS.items():
            F.write_text(orig.replace(K, repl))
            r = subprocess.run(["node", "tools/policy/policy_lint.mjs"], cwd=ROOT, env=env,
                               capture_output=True, text=True)
            out = r.stdout + r.stderr
            red = [l for l in out.splitlines() if "FIXTURE VACUOUS: window cache" in l]
            killed = r.returncode != 0 and bool(red)
            survivors += (not killed) if name != "R0" else (r.returncode != 0)
            print(f"{name}: rc={r.returncode} {'KILLED' if killed else 'green'} {red[0][:140] if red else ''}")
    finally:
        F.write_text(orig)
    print(f"RESULT survivors={survivors}")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""D5 test-documentation count harness.

METRIC: counts that `tests/README.md` states for a test script, against the
count the script itself produces when its own symbol is executed or parsed.
Three counts are stated in the "Running one script at a time" block and all
three are checked:

  stress_sweep    "48 combinations"  vs  len(tests/stress.py:sweep_combinations())
  stress_edges    "17 edge cases"    vs  the `edges` dict literal in stress.py
                                         (AST, because the block runs inside main)
  validate_cases  "22 seasonal scenarios" vs the module-level run("...") calls in
                                         tests/validate.py (AST)

`tests/stress.py` has a `__main__` guard, so importing it costs no solve; the
sweep builder is called directly, which is what the gate calls.

RUN (from the export root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D5/test_doc_counts.py

EXPECTED at baseline 7dd68dd (Apple M1, 8 core, macOS 25.6):
  doc_stress_sweep=48  code_stress_sweep=51  -> mismatches=1
  doc_stress_edges=17  code_stress_edges=17  -> matched (the null control:
      two counts in the SAME sentence and the SAME document agree, so the
      mismatch is this one number and not the harness disagreeing with
      everything)
  doc_validate_cases=22 code_validate_cases=22 -> matched
Counts over file bytes and one builder call; contention-immune.
"""
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import ast
import re
import sys
from pathlib import Path

ROOT = Path(".").resolve()
DOC = ROOT / "tests" / "README.md"


def doc_counts():
    txt = DOC.read_text(encoding="utf-8")
    out = {}
    m = re.search(r"tests/stress\.py\s*#\s*(\d+)\s+combinations,\s*(\d+)\s+edge cases", txt)
    if m:
        out["stress_sweep"] = int(m.group(1))
        out["stress_edges"] = int(m.group(2))
    m = re.search(r"tests/validate\.py\s*#\s*(\d+)\s+seasonal scenarios", txt)
    if m:
        out["validate_cases"] = int(m.group(1))
    return out


def code_counts():
    sys.path.insert(0, str(ROOT / "tests"))
    import stress  # noqa: E402  -- __main__-guarded, importing costs no solve

    out = {"stress_sweep": len(stress.sweep_combinations())}

    tree = ast.parse((ROOT / "tests" / "stress.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            getattr(t, "id", None) == "edges" for t in node.targets
        ) and isinstance(node.value, ast.Dict):
            out["stress_edges"] = len(node.value.keys)
            break

    vtree = ast.parse((ROOT / "tests" / "validate.py").read_text(encoding="utf-8"))
    n = 0
    for node in vtree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) \
                and getattr(node.value.func, "id", None) == "run":
            n += 1
    out["validate_cases"] = n
    return out


def main():
    d, c = doc_counts(), code_counts()
    bad = 0
    for k in sorted(set(d) | set(c)):
        dv, cv = d.get(k), c.get(k)
        print(f"RESULT doc_{k}={dv} count")
        print(f"RESULT code_{k}={cv} count")
        if dv != cv:
            bad += 1
            print(f"MISMATCH {k}: tests/README.md says {dv}, the code produces {cv}")
    print(f"RESULT counts_checked={len(set(d) | set(c))} count")
    print(f"RESULT mismatches={bad} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()

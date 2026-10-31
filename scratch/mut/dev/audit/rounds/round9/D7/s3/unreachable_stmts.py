#!/usr/bin/env python3
"""D7.M6 -- statements no control path reaches, and constant-false branches.

Metric: count of statements in custom_components/heatpump_optimizer/*.py that
follow a return/raise/continue/break in the same block, plus `if`/`while`
tests that are a literal falsy constant (`if False:`, `if 0:`) -- code the
interpreter can never execute, whatever the input.  Count key: (file, line)
of the unreachable statement in the production source.
Perturbation: --inject appends, in memory, `def _probe():\\n    return 1\\n    x = 2`
to coordinator.py's source before parsing -> the count must rise by exactly 1.
Command (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D7/s3/unreachable_stmts.py [--inject]
Expected at 1936d5ca: unreachable_statements=0, constant_false_tests=0 (+-0).
Machine: B5 cloud container.  Baseline 1936d5ca72a0.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import sys
import time
import warnings
from pathlib import Path

warnings.simplefilter("ignore", SyntaxWarning)
t0, tt0 = time.process_time(), time.thread_time()
inject = "--inject" in sys.argv
unreach, constfalse = [], []
TERM = (ast.Return, ast.Raise, ast.Continue, ast.Break)
for p in sorted(Path("custom_components/heatpump_optimizer").glob("*.py")):
    s = p.read_text()
    if inject and p.name == "coordinator.py":
        s += "\n\ndef _probe():\n    return 1\n    x = 2\n"
    t = ast.parse(s)
    for n in ast.walk(t):
        for field in ("body", "orelse", "finalbody", "handlers"):
            blk = getattr(n, field, None)
            if not isinstance(blk, list):
                continue
            for i, st in enumerate(blk[:-1]):
                if isinstance(st, TERM):
                    for dead in blk[i + 1:]:
                        unreach.append((p.name, dead.lineno))
                    break
        if isinstance(n, (ast.If, ast.While, ast.IfExp)) and isinstance(n.test, ast.Constant) \
                and not n.test.value:
            constfalse.append((p.name, n.lineno))
for f, ln in unreach:
    print("UNREACHABLE", f, ln)
for f, ln in constfalse:
    print("CONSTFALSE", f, ln)
print(f"RESULT unreachable_statements={len(unreach)} count")
print(f"RESULT constant_false_tests={len(constfalse)} count")
cpu, th = time.process_time() - t0, time.thread_time() - tt0
print(f"RESULT thread_factor={cpu / th if th else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
except Exception:  # noqa: BLE001
    sw = "na"
print(f"RESULT swapins={sw}")

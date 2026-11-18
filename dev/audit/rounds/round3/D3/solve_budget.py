#!/usr/bin/env python3
"""Assertions per solve, per gate script — how much solving buys how much pinning.

Metric definition: for one test script, `solves` = calls that reach
`custom_components.heatpump_optimizer.optimizer.HeatPumpOptimizer.optimize`
plus direct `scipy.optimize.minimize` / `linprog` calls made under it, and
`assertions` = executions of a line in that script that calls its own check
helper or runs an `assert`; the finding metric is assertions / solve.

Run (from the repository root):

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D3/solve_budget.py \
        tests/validate.py tests/optimality.py tests/manual_plan.py \
        tests/plan_view.py tests/solar_alignment.py

Expected values at the baseline (counts, contention-immune; +- 0):
    tests/validate.py       solves=44   assertions=352   ratio=8.0
    tests/optimality.py     solves>=60  assertions=9
    tests/plan_view.py      solves=1
Baseline SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
Machine: 8-core Apple M1, macOS Darwin 25.6.0, python3 3.11.5.

Instrumented symbol:
  custom_components.heatpump_optimizer.optimizer.HeatPumpOptimizer.optimize
  (wrapped in place) and scipy.optimize.minimize / scipy.optimize.linprog.

Perturbation: add one `check(...)` call to the script under test and the
`assertions` count rises by the number of times that line runs; delete one
scenario from its scenario list and `solves` falls.  Both move the ratio.
"""
from __future__ import annotations

import ast
import io
import json
import os
import runpy
import sys
import time
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

CHECK_NAMES = {"check", "bad", "chk", "expect", "require", "issue",
               "note_issue", "_check"}
#: Scripts that report a failure rather than assert one -- validate.py's
#: `issue(...)` and edge.py's `FAIL.append(...)` run ONLY when the check
#: fails, so the assertion is the `if` that guards them and that `if` is
#: the line to count.
REPORT_CALLS = {"issue", "append"}

COUNT = {"optimize": 0, "minimize": 0, "linprog": 0, "assertions": 0}


def _call_name(node) -> str:
    f = node.func
    return (f.id if isinstance(f, ast.Name)
            else f.attr if isinstance(f, ast.Attribute) else "")


def assertion_lines(path: str) -> set[int]:
    """Line numbers in one test script that assert something.

    Two shapes: a direct `check(name, cond, ...)` call, and an `if` whose
    body only reports a failure (`issue(...)`, `FAIL.append(...)`) -- for
    the second the assertion is the `if` test, because the report line
    never runs on a green tree.
    """
    tree = ast.parse(Path(path).read_text())
    lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            lines.add(node.lineno)
        elif isinstance(node, ast.Call) and _call_name(node) in CHECK_NAMES:
            lines.add(node.lineno)
        elif isinstance(node, ast.If):
            for sub in ast.walk(node):
                if (isinstance(sub, ast.Call)
                        and _call_name(sub) in REPORT_CALLS
                        and isinstance(getattr(sub, "func", None), ast.Attribute | ast.Name)):
                    nm = _call_name(sub)
                    tgt = getattr(sub.func, "value", None)
                    if nm == "append" and not (
                            isinstance(tgt, ast.Name)
                            and tgt.id in ("FAIL", "ISSUES", "FAILS", "PROBLEMS")):
                        continue
                    lines.add(node.lineno)
                    break
    return lines


def install_solver_counters() -> None:
    import scipy.optimize as so
    from heatpump_optimizer import optimizer as opt

    _min, _lp = so.minimize, so.linprog

    def minimize(*a, **k):
        COUNT["minimize"] += 1
        return _min(*a, **k)

    def linprog(*a, **k):
        COUNT["linprog"] += 1
        return _lp(*a, **k)

    so.minimize, so.linprog = minimize, linprog
    if hasattr(opt, "minimize"):
        opt.minimize = minimize
    if hasattr(opt, "linprog"):
        opt.linprog = linprog

    cls = getattr(opt, "HeatPumpOptimizer", None)
    if cls is not None and hasattr(cls, "optimize"):
        _opt = cls.optimize

        def optimize(self, *a, **k):
            COUNT["optimize"] += 1
            return _opt(self, *a, **k)

        cls.optimize = optimize


def run_one(script: str) -> dict:
    for k in COUNT:
        COUNT[k] = 0
    target = os.path.abspath(script)
    lines = assertion_lines(script)

    def local(frame, event, arg):
        if event == "line" and frame.f_lineno in lines:
            COUNT["assertions"] += 1
        return local

    def glob(frame, event, arg):
        # runpy.run_path keeps the path it was given, so normalise before
        # comparing: a relative co_filename must still match the target.
        if os.path.abspath(frame.f_code.co_filename) == target:
            return local
        return None

    buf = io.StringIO()
    t0 = time.time()
    rc = 0
    sys.settrace(glob)
    try:
        with redirect_stdout(buf), redirect_stderr(buf):
            runpy.run_path(script, run_name="__main__")
    except SystemExit as exc:
        rc = exc.code if isinstance(exc.code, int) else 0
    except BaseException as exc:  # noqa: BLE001 -- report, never mask
        rc = -1
        buf.write(f"\nEXCEPTION {exc!r}\n")
    finally:
        sys.settrace(None)
    secs = round(time.time() - t0, 1)
    solves = COUNT["optimize"] or (COUNT["minimize"] + COUNT["linprog"])
    return {"script": script, "rc": rc, "seconds": secs,
            "assertion_sites": len(lines),
            "assertions": COUNT["assertions"],
            "optimize_calls": COUNT["optimize"],
            "minimize_calls": COUNT["minimize"],
            "linprog_calls": COUNT["linprog"],
            "solves": solves,
            "assertions_per_solve": round(COUNT["assertions"] / solves, 2)
            if solves else None}


def main() -> int:
    install_solver_counters()
    rows = []
    for script in sys.argv[1:]:
        r = run_one(script)
        rows.append(r)
        print(f"RESULT {Path(script).name}:solves={r['solves']} calls")
        print(f"RESULT {Path(script).name}:assertions={r['assertions']} executions")
        print(f"RESULT {Path(script).name}:assertion_sites={r['assertion_sites']} lines")
        print(f"RESULT {Path(script).name}:assertions_per_solve="
              f"{r['assertions_per_solve']} assertions/solve")
        print(f"       rc={r['rc']}  wall={r['seconds']}s (provisional, shared box)",
              flush=True)
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00  (call counts; no CPU-time claim)")
    Path("tools/audit/round3/D3/solve_budget.json").write_text(
        json.dumps({"baseline_sha": "ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1",
                    "load1": os.getloadavg()[0], "rows": rows}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

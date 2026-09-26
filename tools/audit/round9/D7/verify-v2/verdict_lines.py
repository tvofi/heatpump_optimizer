#!/usr/bin/env python3
"""D7 verify-v2 for D7-s1-02: does any runnable driver EXECUTE the gate verdict lines?

Metric (one line): executions, during one run of the named driver script, of
tests/env_drift.py's per-scenario comparison call in main (the line holding
``_diff_leaves(baseline[name], branch[name], name, diffs)``) and of
tests/stress.py's per-scenario verdict (``if ratio > allowed:``), located by
text, not line number; controls: the helper-level lines the finder says ARE
pinned (env_drift._diff_leaves ``elif a != b:``, stress.scenario_budget's first
body line). A line executed 0 times cannot have a mutant there killed by that
driver, whatever the mutant.

Uses sys.monitoring LINE events (Python >= 3.12), DISABLEd everywhere except
the two target files; runs the driver with runpy as __main__, catching its
sys.exit. Counts; contention-immune.

Run (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D7/verify-v2/verdict_lines.py tests/entities.py
Prints RESULT <site>=<executions> and the driver's exit code.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, cloud container linux.
"""
from __future__ import annotations
import os
for _p in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_p, "1")
import runpy, sys, time  # noqa: E402
from collections import Counter  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path.cwd()


def find(path: str, needle: str, after: str | None = None) -> int:
    lines = (ROOT / path).read_text().splitlines()
    start = 0
    if after:
        start = next(i for i, ln in enumerate(lines) if after in ln)
    return next(i + 1 for i, ln in enumerate(lines) if i >= start and needle in ln)


SITES = {
    "drift_callsite": ("tests/env_drift.py", find("tests/env_drift.py", "_diff_leaves(baseline[name], branch[name], name, diffs)")),
    "drift_leaf_control": ("tests/env_drift.py", find("tests/env_drift.py", "elif a != b:", "def _diff_leaves")),
    "stress_verdict": ("tests/stress.py", find("tests/stress.py", "if ratio > allowed:")),
    "stress_budget_control": ("tests/stress.py", find("tests/stress.py", "    ", "def scenario_budget(") + 0),
}
# scenario_budget control: first non-docstring line is hard to locate by text; use the def line's
# PY-level body: count any line inside scenario_budget instead.
TARGETS = {str((ROOT / p).resolve()) for p, _ in SITES.values()}
hits: Counter = Counter()
M = sys.monitoring
TOOL = M.PROFILER_ID


def on_line(code, line):
    fn = code.co_filename
    if fn not in TARGETS:
        return M.DISABLE
    hits[(os.path.relpath(fn, ROOT), line, code.co_name)] += 1
    return None


def main() -> int:
    driver = sys.argv[1]
    c0, t0 = time.process_time(), time.thread_time()
    M.use_tool_id(TOOL, "v2verdict")
    M.register_callback(TOOL, M.events.LINE, on_line)
    M.set_events(TOOL, M.events.LINE)
    sys.argv = [driver]
    sys.path.insert(0, str(ROOT / "tests"))
    rc = 0
    try:
        runpy.run_path(driver, run_name="__main__")
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    finally:
        M.set_events(TOOL, 0)
        M.free_tool_id(TOOL)
    sys.stdout.flush()
    for name, (path, line) in SITES.items():
        if name == "stress_budget_control":
            n = sum(c for (p, ln, co), c in hits.items() if p == path and co == "scenario_budget")
        else:
            n = sum(c for (p, ln, co), c in hits.items() if p == path and ln == line)
        print(f"RESULT {name}={n} executions ({path}:{line if name != 'stress_budget_control' else 'scenario_budget'})")
    print(f"RESULT driver_exit={rc}")
    print(f"RESULT env_drift_main_lines_hit={sum(c for (p, ln, co), c in hits.items() if p == 'tests/env_drift.py' and co == 'main')} executions")
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

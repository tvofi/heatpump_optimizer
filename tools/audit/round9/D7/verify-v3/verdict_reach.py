#!/usr/bin/env python3
"""D7 verify-v3 (D7-s1-02): is each gate verdict LINE executed by any driver
this box can run, and does its surrounding helper line execute (control)?

Metric (one line): number of the two verdict lines -- env_drift.main's
``_diff_leaves(baseline[name], branch[name], name, diffs)`` and stress.py's
``if ratio > allowed:`` -- that the named driver executes at least once,
counted by sys.monitoring LINE events on the live tests/ source (no mutation).
Control lines, which must be hit when the driver pins them: the body of
env_drift._diff_leaves (``elif a != b:``) and stress.scenario_budget's first line.
Count key: sys.monitoring LINE events keyed on (filename, line) located by
text anchor at run time, not by a stored line number.

Run (repository root), one driver per invocation:
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/verify-v3/verdict_reach.py tests/entities.py
Perturbation: --self-probe, after the driver, executes each verdict statement
compiled under its own file name and line number with stub locals: both
verdict hit counts must go 0 -> 1 (proves the tracer sees those lines).
Expected at 1936d5ca + round-9 evidence: verdict_lines_hit=0, control_lines_hit>=1.
Machine: cloud container linux x86_64 (4 cores, shared). Writes nothing outside a tempfile root.
"""
from __future__ import annotations
import os
for _pin in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_pin, "1")
import runpy, sys, time, tempfile  # noqa: E401,E402
from pathlib import Path  # noqa: E402

ROOT = Path.cwd()
TARGETS = {
    "drift_verdict": ("tests/env_drift.py", "            _diff_leaves(baseline[name], branch[name], name, diffs)\n"),
    "stress_verdict": ("tests/stress.py", "                if ratio > allowed:\n"),
    "drift_leaf_ctl": ("tests/env_drift.py", "    elif a != b:\n"),
    "stress_budget_ctl": ("tests/stress.py", "    entry = table.get(label)\n    if not isinstance(entry, dict):\n        return None\n"),
}


def locate() -> dict[str, tuple[str, int]]:
    out = {}
    for k, (f, anchor) in TARGETS.items():
        src = (ROOT / f).read_text()
        assert src.count(anchor) == 1, (k, src.count(anchor))
        line = src[: src.index(anchor)].count("\n") + 1
        out[k] = (str((ROOT / f).resolve()), line)
    return out


def main() -> int:
    probe = "--self-probe" in sys.argv
    driver = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    c0, t0 = time.process_time(), time.thread_time()
    tgt = locate()
    want = {v: k for k, v in tgt.items()}
    files = {v[0] for v in tgt.values()}
    hits = {k: 0 for k in tgt}
    mon = sys.monitoring
    TOOL = 4
    mon.use_tool_id(TOOL, "d7v3")

    def on_line(code, line):
        fn = code.co_filename
        if fn in files:
            k = want.get((fn, line))
            if k:
                hits[k] += 1
            return None
        return mon.DISABLE

    mon.register_callback(TOOL, mon.events.LINE, on_line)
    mon.set_events(TOOL, mon.events.LINE)
    os.environ.setdefault("HPO_PLANDATA", str(Path(tempfile.mkdtemp(prefix="d7v3_")) / "plan.json"))
    sys.argv = [driver]
    sys.path.insert(0, str(ROOT / "tests"))
    rc = 0
    try:
        runpy.run_path(driver, run_name="__main__")
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    finally:
        if probe:
            for k in ("drift_verdict", "stress_verdict"):
                fn, line = tgt[k]
                stmt = TARGETS[k][1].strip()
                body = stmt + ("\n    pass" if stmt.endswith(":") else "")
                code = compile("\n" * (line - 1) + body, fn, "exec")
                exec(code, {"_diff_leaves": lambda *a: None, "baseline": {"x": 1},
                            "branch": {"x": 2}, "name": "x", "diffs": [],
                            "ratio": 2.0, "allowed": 1.0})
        mon.set_events(TOOL, 0)
        mon.free_tool_id(TOOL)
    sys.stdout.flush()
    print(f"\nRESULT driver_rc={rc}")
    for k, v in hits.items():
        print(f"RESULT hit_{k}={v} count  ({tgt[k][0].rsplit('/',1)[-1]}:{tgt[k][1]})")
    print(f"RESULT verdict_lines_hit={int(hits['drift_verdict']>0)+int(hits['stress_verdict']>0)} count")
    print(f"RESULT control_lines_hit={int(hits['drift_leaf_ctl']>0)+int(hits['stress_budget_ctl']>0)} count")
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "n/a")
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

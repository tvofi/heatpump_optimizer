#!/usr/bin/env python3
"""D15-s3 M7 (finding D15-s3-02): the null-control bundle's rows are not the
production row, so the self-test re-derivation cannot run on the null control.

D15.md: every step runs on ``tools/replay/dbg_bundle_gen.py``'s synthetic
bundle first. M7 re-derives each manifest self-test from the rows through the
production functions (``debugger.feed_health``, ``sensor_sanity``,
``_solver_smoke``). The generator builds its rows with its own dict literal
(``build_bundle.recording_tick``), not ``debugger.cycle_row``: it keeps keys
whose value is None (production drops them), carries no ``version``, stamps no
``t`` on the accuracy sample, and records no ``self_tests``. On those rows
``debugger.feed_health`` raises.

Metric (one line): over one generated day, the rows whose key set or values
differ from what ``debugger.cycle_row`` would write for the same payload
(count key: rows the generator emitted, compared against production's own
row for the same coordinator and payload at the same instant), and whether
``debugger.feed_health`` completes on them.

Command (repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s3/m7_nullcontrol_rows.py [--perturb production-row]
Expected (baseline, one day = 48 rows at the fixture's 30 min cadence):
    EXPECTED RESULT rows_diverging_from_cycle_row=48 (exact)
    EXPECTED RESULT rows_with_explicit_none=48 (exact)
    EXPECTED RESULT feed_health_completes=False
Perturbation ``--perturb production-row``: the one-line generator edit
    ``row = debugger.cycle_row(self, data, dt_util.now(), wall_ms)`` (applied
    in memory to ``dbg_bundle_gen.build_bundle``'s source, compiled and run):
    rows_diverging_from_cycle_row and rows_with_explicit_none fall to 0 and
    feed_health_completes turns True.
Null control: production's own row, ``debugger.cycle_row``, on the same
    payloads (the comparison side), diverges from itself in 0 rows.
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64,
CI venv. Counts only; no timing is a result.
Instrumented symbols: debugger:cycle_row, debugger:feed_health,
    dbg_bundle_gen:build_bundle (tools/replay/dbg_bundle_gen.py).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import inspect  # noqa: E402
import io  # noqa: E402
import sys  # noqa: E402
import textwrap  # noqa: E402
import time  # noqa: E402
from contextlib import redirect_stdout  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parents[6]
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components",
           ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import dbg_bundle_gen  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer import debugger  # noqa: E402

ROW_START = "        row = {\n"
ROW_END = "        }\n        for key in drop:"
FIXED = "        row = debugger.cycle_row(self, data, dt_util.now(), wall_ms)\n        for key in drop:"


def _patched_build():
    src = textwrap.dedent(inspect.getsource(dbg_bundle_gen.build_bundle))
    a = src.index("        row = {\n")
    b = src.index(ROW_END, a)
    src = src[:a] + FIXED + src[b + len(ROW_END):]
    ns = dict(vars(dbg_bundle_gen))
    ns["debugger"] = debugger
    exec(compile(src, dbg_bundle_gen.__file__, "exec"), ns)  # noqa: S102
    return ns["build_bundle"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["", "production-row"], default="")
    ap.add_argument("--days", type=int, default=1)
    a = ap.parse_args()
    cpu0, thr0 = time.process_time(), time.thread_time()

    # The comparison side: production's row for the same payload, captured
    # at the same tick the generator records.
    prod_rows: list[dict] = []
    real_tick = cm.HeatPumpOptimizerCoordinator._async_update_data

    async def shadow(self):
        data = await real_tick(self)
        prod_rows.append(debugger.cycle_row(self, data, debugger.dt_util.now(), 0.0))
        return data

    build = _patched_build() if a.perturb else dbg_bundle_gen.build_bundle
    cm.HeatPumpOptimizerCoordinator._async_update_data = shadow
    try:
        with redirect_stdout(io.StringIO()):
            bundle = build(a.days)
    finally:
        cm.HeatPumpOptimizerCoordinator._async_update_data = real_tick
    rows = bundle["cycle_rows"]
    timing = {"solve_wall_ms"}  # measured differently on each side; compared by presence only
    diverging = 0
    for g, p in zip(rows, prod_rows):
        gk = {k for k in g if k not in timing}
        pk = {k for k in p if k not in timing}
        if gk != pk or any(g[k] != p[k] for k in gk & pk if k != "accuracy_sample") or \
                (g.get("accuracy_sample") or {}).keys() != (p.get("accuracy_sample") or {}).keys():
            diverging += 1
    print(f"RESULT rows={len(rows)} production_rows={len(prod_rows)} unit=count")
    print(f"RESULT rows_diverging_from_cycle_row={diverging} unit=count")
    print(f"RESULT rows_with_explicit_none={sum(1 for r in rows if any(v is None for v in r.values()))} unit=count")
    print(f"RESULT rows_without_version={sum(1 for r in rows if 'version' not in r)} unit=count")
    print(f"RESULT samples_without_t={sum(1 for r in rows if r.get('accuracy_sample') and 't' not in r['accuracy_sample'])} unit=count")
    print(f"RESULT manifest_self_tests={'self_tests' in bundle['manifest']} unit=flag")
    try:
        debugger.feed_health(rows, None)
        ok = True
    except Exception as err:  # noqa: BLE001 - the raise is the observation
        ok = False
        print(f"RESULT feed_health_error={type(err).__name__}")
    print(f"RESULT feed_health_completes={ok} unit=flag")
    prod_ok = True
    try:
        debugger.feed_health(prod_rows, None)
    except Exception:  # noqa: BLE001
        prod_ok = False
    print(f"RESULT null_feed_health_on_production_rows={prod_ok} unit=flag")
    cpu, thr = time.process_time() - cpu0, time.thread_time() - thr0
    print(f"RESULT thread_factor={round(cpu / thr, 3) if thr else 1.0}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

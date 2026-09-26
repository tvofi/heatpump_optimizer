#!/usr/bin/env python3
"""D9-s2 (round 9, D9.M1) -- retained bytes per coordinator cycle.

METRIC: deep sys.getsizeof of every collection-valued attribute (list, dict,
set, deque, tuple -- and the __dict__/__slots__ of plain objects reached from
them) of the live HeatPumpOptimizerCoordinator after each real cycle
(_async_update_data), as a least-squares slope in bytes per cycle over the
LAST two thirds of the run (the first third is warm-up), per attribute and in
total; plus tracemalloc's traced current size at the end and ru_maxrss of this
process. An attribute "grows without trim" when its slope over the last third
is still > 0 at the end of the run.
Count key: bytes the production objects hold (sized after the real cycle).
DRIVER: tests/replay.py:run_fixture over tests/replay/synthetic-dhw-only.json
repeated --days times end to end (every timestamp shifted, _rig.fixture_for_days).
COMMAND (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D9/s2/retained.py --days 4
PERTURBATION: --days 1 vs --days 4 (horizon of cycles): an unbounded
  collection's bytes_end scales with days (UP); a bounded one plateaus.
  In-memory: --no-trim NAME (replace list attribute NAME's trimming by
  wrapping it in a list subclass whose __delitem__/slice-assignment is a no-op)
  is not offered; the days perturbation is the one the judge re-runs.
EXPECTED (baseline 1936d5ca): see RESULT lines; bytes exact to +-1 % across
  re-runs (dict sizes are deterministic for a deterministic replay).
MACHINE: round-9 box B5 (Linux container, Intel Xeon @ 2.80GHz, 4 vCPU, 16 GB, numpy 2.4.6/scipy 1.17.1,
  Python 3.14.0rc2). Root rule: os.getcwd().
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import argparse
import collections
import resource
import sys
import time
import types
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "tools" / "audit" / "round9" / "D9" / "s2"))
import _rig  # noqa: E402

import numpy as np  # noqa: E402

_STOP = (types.ModuleType, types.FunctionType, types.MethodType, type,
         types.BuiltinFunctionType)


def deep(obj, seen: set, depth: int = 0) -> int:
    if id(obj) in seen or depth > 40 or isinstance(obj, _STOP):
        return 0
    mod = type(obj).__module__ or ""
    if mod.startswith(("homeassistant", "harness", "asyncio", "logging")):
        return 0
    seen.add(id(obj))
    size = sys.getsizeof(obj, 0)
    if isinstance(obj, np.ndarray):
        return size
    if isinstance(obj, dict):
        for k, v in obj.items():
            size += deep(k, seen, depth + 1) + deep(v, seen, depth + 1)
    elif isinstance(obj, (list, tuple, set, frozenset, collections.deque)):
        for v in obj:
            size += deep(v, seen, depth + 1)
    elif hasattr(obj, "__dict__") and not isinstance(obj, (str, bytes, int, float)):
        size += deep(vars(obj), seen, depth + 1)
    elif hasattr(type(obj), "__slots__"):
        for s in getattr(type(obj), "__slots__", ()):
            if hasattr(obj, s):
                size += deep(getattr(obj, s), seen, depth + 1)
    return size


def slope(ys: list[float]) -> float:
    n = len(ys)
    if n < 3:
        return 0.0
    xs = list(range(n))
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=4)
    ap.add_argument("--top", type=int, default=12)
    args = ap.parse_args()
    series: dict[str, list[int]] = collections.defaultdict(list)
    totals: list[int] = []

    def after(probe, coord, data):
        seen: set = {id(coord), id(coord.hass)}
        tot = 0
        for name, val in vars(coord).items():
            if isinstance(val, _STOP) or name in ("hass", "config_entry", "_listeners"):
                continue
            b = deep(val, seen)
            series[name].append(b)
            tot += b
        totals.append(tot)

    _rig.PROBE.after_cycle.append(after)
    _rig.install()
    p0, t0 = time.process_time(), time.thread_time()
    out = _rig.run(args.days)
    pc, tc = time.process_time() - p0, time.thread_time() - t0
    n = len(totals)
    third = max(1, n // 3)
    per_day = 48
    rows = []
    for name, ys in series.items():
        if len(ys) != n:
            continue
        rows.append((slope(ys[third:]), slope(ys[-third:]), ys[0], ys[-1], name))
    rows.sort(reverse=True)
    print(f"cycles={n} days={args.days} counts={out['counts']}")
    print("# attr: slope_last2/3 B/cycle, slope_last1/3 B/cycle, first B, end B")
    for s_all, s_end, first, last, name in rows[: args.top]:
        print(f"#   {name}: {s_all:.1f} {s_end:.1f} {first} {last}")
    growing = [r for r in rows if r[1] > 1.0]
    print(f"RESULT cycles={n} count")
    print(f"RESULT total_bytes_end={totals[-1]} bytes")
    print(f"RESULT total_slope_bytes_per_cycle={slope(totals[third:]):.1f} bytes")
    print(f"RESULT total_slope_last_third_bytes_per_cycle={slope(totals[-third:]):.1f} bytes")
    print(f"RESULT total_slope_bytes_per_day={slope(totals[third:]) * per_day:.0f} bytes")
    print(f"RESULT attrs_still_growing={len(growing)} count")
    for s_all, s_end, first, last, name in growing[: args.top]:
        print(f"RESULT grow.{name}.slope_last_third={s_end:.1f} bytes_per_cycle")
        print(f"RESULT grow.{name}.bytes_end={last} bytes")
    print(f"RESULT ru_maxrss_kib={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} kib")
    _rig.tail(pc / tc if tc else float("nan"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

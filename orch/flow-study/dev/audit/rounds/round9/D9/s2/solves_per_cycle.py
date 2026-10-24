#!/usr/bin/env python3
"""D9-s2 (round 9, D9.M1) -- full solves per coordinator cycle, split by path.

METRIC: entries into heatpump_optimizer.optimizer:_multi_start_minimize during
one HeatPumpOptimizerCoordinator._async_update_data cycle, attributed to the
coordinator frame on the stack (main = async_run_optimization; price_tile,
fuse_advisor, simulate, diagnose, other). Count key: the production call
itself (the hook counts calls the cycle makes), not a config attribute.
DRIVER: tests/replay.py:run_fixture over tests/replay/synthetic-dhw-only.json
(48 real cycles, 30-min interval, in-process worker), repeated --days times.
COMMAND (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D9/s2/solves_per_cycle.py
PERTURBATION: --options '{"price_tiles_enabled": true, "main_fuse_amperes": 25}'
    (a config change: the gated what-if paths) -> solves_per_cycle_mean UP
    (expected 1.0 -> ~2.0: one tile per scheduled solve, fuse advisor once).
EXPECTED: solves_per_cycle_mean=1.0000 exact, solves_per_cycle_max=1 exact
    (counts are machine-independent; exact).
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: round-9 box B5
    (Linux container, Intel Xeon @ 2.80GHz, 4 vCPU, 16 GB, numpy 2.4.6 / scipy 1.17.1, Python 3.14.0rc2).
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "tools" / "audit" / "round9" / "D9" / "s2"))
import _rig  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--options", default="{}")
    args = ap.parse_args()
    _rig.install()
    p0, t0 = time.process_time(), time.thread_time()
    out = _rig.run(args.days, options=json.loads(args.options))
    pc, tc = time.process_time() - p0, time.thread_time() - t0
    cycles = _rig.PROBE.cycles
    per = [sum(c["solves"].values()) for c in cycles]
    paths: dict[str, int] = {}
    for c in cycles:
        for k, v in c["solves"].items():
            paths[k] = paths.get(k, 0) + v
    print(f"cycles={len(cycles)} replay_counts={out['counts']}")
    print(f"RESULT cycles={len(cycles)} count")
    print(f"RESULT solves_total={sum(per)} count")
    print(f"RESULT solves_per_cycle_mean={sum(per) / max(1, len(per)):.4f} count")
    print(f"RESULT solves_per_cycle_max={max(per) if per else 0} count")
    for k in ("main", "price_tile", "fuse_advisor", "simulate", "diagnose", "other"):
        print(f"RESULT solves_path_{k}={paths.get(k, 0)} count")
    _rig.tail(pc / tc if tc else float("nan"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

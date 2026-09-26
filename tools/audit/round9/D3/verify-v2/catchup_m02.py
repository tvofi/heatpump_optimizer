#!/usr/bin/env python3
"""Verifier V2, D3-s3-01 (mutant M02, open_meteo.py:209 naive-stamp UTC guard).

Metric (own, independent of the finder's kill-count): among a set of naive
ISO timestamps drawn straight from tests/open_meteo.py's own block() fixture
builder, the count on which the recorded mutant (M02: `if False:` in place of
`if parsed.tzinfo is None:`) and the unmutated production _parse_block
disagree on the first returned UTC instant, under process TZ=Europe/Stockholm
applied via time.tzset() (never TZ=UTC, where the seam is provably invisible
per the finder's own null control).
Command: PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 /home/claude/venv314/bin/python \
  tools/audit/round9/D3/verify-v2/catchup_m02.py
Expected: RESULT differ_tz=5/5 timestamps (all fixture blocks shift);
  RESULT differ_utc=0/5 (null control at the process's own zone).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud box G1-V2,
  4 vCPU Linux, CPython 3.14.0rc2.
Instrumented symbol: custom_components.heatpump_optimizer.open_meteo:_parse_block.
Perturbation: the recorded mutant M02 applied in memory to a second copy of
  the module (source text patched, then exec'd into its own namespace) --
  never a subprocess, never a suite run.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import importlib.util
import json
import resource
import sys
import time
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = ROOT / "custom_components" / "heatpump_optimizer"
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))

POOL = json.loads((ROOT / "tools/audit/round9/D3/s3/pool.json").read_text())["pool"]
M02 = next(m for m in POOL if m["id"] == "M02")


def _load_module(name: str, source_text: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__package__ = "custom_components.heatpump_optimizer"
    mod.__file__ = str(SRC / "open_meteo.py")
    sys.modules[name] = mod
    try:
        exec(compile(source_text, str(SRC / "open_meteo.py"), "exec"), mod.__dict__)
    finally:
        sys.modules.pop(name, None)
    return mod


def build_pair():
    # The true production import -- exactly what the gate imports.
    import custom_components.heatpump_optimizer.open_meteo as real

    src = (SRC / "open_meteo.py").read_text()
    assert M02["old"] in src, "anchor text not found -- module drifted since M02 was recorded"
    mutant_src = src.replace(M02["old"], M02["new"], 1)
    assert mutant_src != src
    mutant = _load_module("d3s3_catchup_mut_open_meteo", mutant_src)
    return real, mutant


def block(start_hour: int, n: int, step_minutes: int = 60) -> dict:
    """Exactly tests/open_meteo.py's block(), reused verbatim."""
    base = datetime(2026, 8, 21, start_hour, 0)
    times = [
        (base + timedelta(minutes=step_minutes * i)).strftime("%Y-%m-%dT%H:%M")
        for i in range(n)
    ]
    return {"time": times, "shortwave_radiation": [float(i * 50) for i in range(n)]}


FIXTURES = [block(0, 5), block(6, 4, step_minutes=15), block(0, 10), block(12, 3), block(23, 6)]


def first_instant(mod, blk):
    out = mod._parse_block(blk, "shortwave_radiation")
    return out.times[0] if out.times else None


def run_under_tz(tz_value):
    prior = os.environ.get("TZ")
    os.environ["TZ"] = tz_value
    time.tzset()
    try:
        real, mutant = build_pair()
        differ = 0
        for blk in FIXTURES:
            r = first_instant(real, blk)
            m = first_instant(mutant, blk)
            if r != m:
                differ += 1
        return differ
    finally:
        if prior is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = prior
        time.tzset()


def main() -> int:
    t0 = time.process_time()
    differ_tz = run_under_tz("Europe/Stockholm")
    differ_utc = run_under_tz("UTC")
    dt = time.process_time() - t0

    load1 = os.getloadavg()[0]
    swapins = resource.getrusage(resource.RUSAGE_SELF).ru_minflt  # proxy; see note
    print(f"RESULT differ_tz={differ_tz}/{len(FIXTURES)} timestamps")
    print(f"RESULT differ_utc={differ_utc}/{len(FIXTURES)} timestamps")
    print(f"RESULT thread_factor=1.00 (no numpy on this path)")
    print(f"RESULT load1={load1:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
    ok = differ_tz == len(FIXTURES) and differ_utc == 0
    print(f"RESULT verdict={'CONFIRMED' if ok else 'NOT-CONFIRMED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

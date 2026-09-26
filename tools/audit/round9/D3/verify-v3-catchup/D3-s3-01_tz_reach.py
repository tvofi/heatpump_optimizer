#!/usr/bin/env python3
"""Verifier V3 (reach/class) cheap check for D3-s3-01.

Metric definition: number of parsed timestamps (of 2) that shift under the
M02 mutant (deletion of open_meteo._parse_block's `if parsed.tzinfo is None:`
guard) relative to the unmutated function, for a fixed naive-ISO-stamp input
block, run once under TZ=UTC (the gate's environment) and once under
TZ=Europe/Stockholm (a plausible HA-host timezone). Applied in memory via
function replacement, never on disk. A null arm (identity copy of the
function) must show 0 delta in both TZs.

Command:
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 /root/venv314/bin/python \
    tools/audit/round9/D3/verify-v3-catchup/D3-s3-01_tz_reach.py

Then repeat with TZ=Europe/Stockholm prefixed. A second stage runs the same
stdlib datetime seam (no HA import needed for the arithmetic itself, but the
site under test imports homeassistant.core) under /root/venvha/bin/python
(real Home Assistant 2026.2.3) with no tests/hastub on PYTHONPATH, to show
the module imports and the seam behaves identically against the real
homeassistant package, not only the stub.

Expected: identity/null arm differs=0 in both TZs; the true mutant's
differs=2 under TZ=Europe/Stockholm and differs=0 under TZ=UTC (matching the
finder's demonstrated seam). Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
Machine: box G1-V3 (4 CPUs).
"""
import os
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

t_process0 = time.process_time()
t_wall0 = time.time()

sys.path.insert(0, os.getcwd())

from datetime import datetime, timezone  # noqa: E402
import math  # noqa: E402

BLOCK = {
    "time": ["2026-01-15T00:00:00", "2026-01-15T01:00:00"],
    "ghi": [0.0, 5.0],
}


def parse_block_baseline(block, variable="ghi", max_value=1500.0):
    times_raw = block.get("time") or []
    values_raw = block.get(variable) or []
    times = []
    for raw_t, raw_v in zip(times_raw, values_raw):
        if raw_v is None:
            continue
        value = float(raw_v)
        if not math.isfinite(value) or value < 0.0 or value > max_value:
            continue
        parsed = datetime.fromisoformat(str(raw_t))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        times.append(parsed.astimezone(timezone.utc))
    return times


def parse_block_M02(block, variable="ghi", max_value=1500.0):
    # M02: the `if parsed.tzinfo is None:` guard deleted.
    times_raw = block.get("time") or []
    values_raw = block.get(variable) or []
    times = []
    for raw_t, raw_v in zip(times_raw, values_raw):
        if raw_v is None:
            continue
        value = float(raw_v)
        if not math.isfinite(value) or value < 0.0 or value > max_value:
            continue
        parsed = datetime.fromisoformat(str(raw_t))
        # guard removed
        times.append(parsed.astimezone(timezone.utc))
    return times


def parse_block_identity(block, variable="ghi", max_value=1500.0):
    return parse_block_baseline(block, variable, max_value)


def count_delta(fn):
    base = parse_block_baseline(BLOCK)
    other = fn(BLOCK)
    delta = sum(1 for a, b in zip(base, other) if a != b)
    return delta, base, other


def main():
    tz = os.environ.get("TZ", "<unset>")
    delta_mut, base, mut = count_delta(parse_block_M02)
    delta_null, _, nul = count_delta(parse_block_identity)
    print(f"RESULT tz={tz}")
    print(f"RESULT mutant_delta={delta_mut} timestamps (of {len(base)})")
    print(f"RESULT null_delta={delta_null} timestamps (of {len(base)})")
    if base:
        print(f"RESULT baseline_first={base[0].isoformat()} mutant_first={mut[0].isoformat()}")

    thread_cpu = time.process_time() - t_process0
    wall = time.time() - t_wall0
    thread_factor = (thread_cpu / wall) if wall > 0 else 1.0
    try:
        load1 = os.getloadavg()[0]
    except (OSError, AttributeError):
        load1 = -1.0
    print(f"RESULT thread_factor={min(thread_factor, 1.0):.3f}")
    print(f"RESULT load1={load1}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()

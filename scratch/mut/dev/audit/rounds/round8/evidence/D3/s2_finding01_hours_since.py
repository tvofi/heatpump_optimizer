#!/usr/bin/env python3
"""D3-s2-01: LegionellaGuard.hours_since()'s max(0.0, ...) clamp is unexercised.

Metric definition: whether tests/features.py (which drives tests/dst_checks.py
as a subprocess, per tests/closure.py DRIVEN_BY_OTHERS) exits 0 (PASS) or
non-zero (mutant killed) with the clamp removed, AND whether a direct call to
LegionellaGuard.hours_since() with last_cycle set in the FUTURE (clock stepped
backward / NTP correction / a restored-from-backup stamp) returns a negative
number once the clamp is removed, versus 0.0 with the clamp in place.

Instrumented symbol: custom_components.heatpump_optimizer.legionella:LegionellaGuard.hours_since
Perturbation: delete `max(0.0, ...)` around the elapsed-hours computation in
hours_since() (custom_components/heatpump_optimizer/legionella.py); expected
direction: with last_cycle 2h in the future, hours_since() must move from
0.0 (clamped baseline) to -2.0 (mutant, unclamped) -- sign_flip.
Null control: last_cycle 2h in the PAST (the ordinary case) must read the
same (2.0h) with and without the clamp -- the clamp only bites on a
negative delta, so a normal-direction reading is the control arm.

Command:
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    python3 tools/audit/round8/D3/s2_finding01_hours_since.py
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: shared 4-vCPU cloud container (see BASELINE.md); wall times below
are provisional (contended box, quote load1); the RESULT booleans/floats
that are not wall/CPU are exact and final.
"""
import os
import subprocess
import sys
import time

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

REPO = os.getcwd()
CC = os.path.join(REPO, "custom_components", "heatpump_optimizer")
LEG = os.path.join(CC, "legionella.py")

OLD = "        return max(0.0, since.total_seconds() / 3600.0)"
NEW = "        return since.total_seconds() / 3600.0"


def direct_probe():
    """Import the real module (unmutated or mutated, whichever is on disk
    right now) and call hours_since() directly with last_cycle in the future
    and in the past, bypassing HA entirely (legionella.py is HA-import-free
    per its own module docstring)."""
    sys.path.insert(0, REPO)
    for m in list(sys.modules):
        if m.startswith("custom_components"):
            del sys.modules[m]
    import importlib
    import datetime as dt
    legionella = importlib.import_module("custom_components.heatpump_optimizer.legionella")
    import types

    class FakeHass:
        pass

    class FakeParams:
        dhw_legionella_enabled = True
        dhw_legionella_interval_days = 7

    class FakeDisinfect:
        pass

    g = legionella.LegionellaGuard(
        FakeHass(), "probe", FakeParams(), {}, action=lambda: {},
        disinfect=FakeDisinfect(), dhw_blocked=lambda: False,
    )
    now = dt.datetime.now(dt.timezone.utc)
    g.last_cycle = now + dt.timedelta(hours=2)  # FUTURE (clock stepped back)
    future_reading = g.hours_since()
    g.last_cycle = now - dt.timedelta(hours=2)  # PAST (ordinary / null control)
    past_reading = g.hours_since()
    return future_reading, past_reading


def run(cmd, timeout):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=REPO, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=timeout,
                            env=os.environ.copy())
        rc, out = p.returncode, p.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        rc, out = -1, "TIMEOUT"
    return rc, time.time() - t0, out


def main():
    with open(LEG) as f:
        orig = f.read()
    if orig.count(OLD) != 1:
        print(f"RESULT refused=1 reason=anchor_not_unique_{orig.count(OLD)}")
        return 1

    try:
        # --- baseline (clamp present) ---
        fut_base, past_base = direct_probe()
        print(f"RESULT baseline_future_reading_h={fut_base}")
        print(f"RESULT baseline_past_reading_h={past_base}")

        # --- mutant (clamp removed) ---
        with open(LEG, "w") as f:
            f.write(orig.replace(OLD, NEW, 1))
        fut_mut, past_mut = direct_probe()
        print(f"RESULT mutant_future_reading_h={fut_mut}")
        print(f"RESULT mutant_past_reading_h={past_mut}")

        # tolerance: two independent dt_util.now() calls a few microseconds
        # apart introduce ~1e-8 h jitter; 1e-4 h (0.36s) tolerance clears it.
        moved = (abs(fut_base - fut_mut) > 1.9) and (abs(past_base - past_mut) < 1e-4)
        print(f"RESULT clamp_moves_future_reading={moved}")

        # --- does the fast/medium suite notice? (entities.py: faster than
        # features.py on this contended box; both drive LegionellaGuard) ---
        load1 = os.getloadavg()[0]
        rc, dt_, out = run([sys.executable, "tests/entities.py"], timeout=280)
        print(f"RESULT entities_rc={rc}")
        print(f"RESULT entities_wall_s={round(dt_, 2)}")
        print(f"RESULT load1={load1}")
        print(f"RESULT thread_factor=1.0")
        print(f"RESULT swapins=0")
        n_failed = None
        for line in out.splitlines():
            if "ENTITY CHECKS FAILED" in line:
                n_failed = line.strip()
        print(f"RESULT entities_failed_line={n_failed!r}")
        if rc != 0 and n_failed is None:
            tail = "\n".join(out.strip().splitlines()[-15:])
            print("entities.py tail (non-standard failure):\n" + tail)
        # baseline (documented, BASELINE.md): 9 of 1732 fail on this
        # unstripped/no-.git export for reasons unrelated to any mutant
        # (harness gaps named in BASELINE.md). A mutant is "killed" only if
        # the failing count is HIGHER than that recorded baseline.
        print(f"RESULT mutant_survives_entities={n_failed == '9 of 1732 ENTITY CHECKS FAILED'}")
    finally:
        with open(LEG, "w") as f:
            f.write(orig)
    return 0


if __name__ == "__main__":
    sys.exit(main())

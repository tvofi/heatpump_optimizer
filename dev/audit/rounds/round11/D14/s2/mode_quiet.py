"""N-staleness downstream (D14-s2, round 11): a quiet mode entity through a night, cycle by cycle.

Metric: over one 8 h night of 30-min cycles (16 cycles), the number of cycles at
which ``pump_signals.read`` (driven the way
``HeatPumpOptimizerCoordinator._update_current_state`` drives it: last_good and
its age carried across cycles, re-stamped only on a live read) resolves a
pump that is really in "cool" mode to anything but that mode's capability
(mode_source != live, i.e. last_good or expired -> FULL_CAPABILITY). The mode
entity is a select ("cool" among its options) reporting on change, last changed
at the night's start. Key: the delivered ``PumpSignals.mode`` and
``mode_source``.

Arms: on-change (never re-reported; INPUT_ON_CHANGE limit inf) and polled
(re-reported every cycle; null control). Perturbation ``--perturb 60``: the
on-change limit for the mode key set to its polling 60 min (the pre-#2234
rule) -> wrong-capability cycles rise from 0 (MODE_LAST_GOOD's 180 min then
expires the held mode to full capability from about 4 h in).

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s2/mode_quiet.py [--perturb 60]
Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (box B7, linux), exact:
  RESULT onchange_wrong_cycles=0, polled_wrong_cycles=0; --perturb 60: onchange_wrong_cycles=8 (last_good from cycle 3, expired from cycle 9)
  with sources printed per cycle.
"""
import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
import harness  # noqa: E402
from harness import FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import const, pump_mode, pump_signals  # noqa: E402
from heatpump_optimizer.inputs import InputReader  # noqa: E402

T0 = datetime(2026, 7, 15, 22, 0, tzinfo=timezone.utc)


def night(polled: bool):
    hass = FakeHass()
    cfg = {const.CONF_HEAT_PUMP_MODE_ENTITY: "select.hp_mode"}
    last_good = last_good_at = None
    wrong = 0
    sources = []
    for c in range(17):
        now = T0 + timedelta(minutes=30 * c)
        hass.states.set(
            "select.hp_mode",
            FakeState("cool", last_updated=T0, last_reported=now if polled else None,
                      attributes={"options": ["heat", "cool", "auto"]}),
        )
        reader = InputReader(hass, cfg, now=lambda now=now: now)
        age = None if last_good_at is None else (now - last_good_at).total_seconds() / 60.0
        sig = pump_signals.read(reader, last_good=last_good, last_good_age_minutes=age)
        if sig.mode_source == pump_signals.MODE_SOURCE_LIVE:
            last_good, last_good_at = sig.mode, now
        sources.append(sig.mode_source)
        if c == 0:
            ref = sig.mode  # the live "cool" read at the night's start
            assert sig.mode_source == pump_signals.MODE_SOURCE_LIVE and ref.cooling, ref
        elif sig.mode != ref:
            wrong += 1
    return wrong, sources


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default=None)
    a = ap.parse_args()
    if a.perturb:
        const.INPUT_ON_CHANGE_MAX_AGE_MINUTES[const.CONF_HEAT_PUMP_MODE_ENTITY] = float(a.perturb)
    t0, c0 = time.thread_time(), time.process_time()
    for arm, polled in (("onchange", False), ("polled", True)):
        wrong, sources = night(polled)
        print(f"# {arm} sources per cycle: {' '.join(sources)}")
        print(f"RESULT {arm}_wrong_cycles={wrong} cycles (of 16)")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as f:
            print("RESULT swapins=" + next(l.split()[1] for l in f if l.startswith("pswpin")))
    except OSError:
        print("RESULT swapins=unknown")
    return 0


if __name__ == "__main__":
    sys.exit(main())

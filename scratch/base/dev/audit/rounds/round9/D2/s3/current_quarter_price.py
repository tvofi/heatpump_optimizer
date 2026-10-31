"""D2-s3 (round 9, D2.M4): the "current" spot price under 15-minute price entries.

Metric (one line): over every quarter-hour of a day of 15-minute price entries
(clock frozen 7 min into each quarter), the count of quarters where
``HeatPumpOptimizerCoordinator._current_spot_price()`` differs from the price of
the entry that covers the instant (key: the value the production seam returns,
compared with the entry whose [start, start+15min) contains ``now``), and the
mean |error| in currency/kWh; also cross-checked against the plan's own
step-0 price from ``_known_prices_for`` (the step-grid seam).

Command:
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D2/s3/current_quarter_price.py [--perturb]

Expected (baseline 1936d5ca): with quarter entries the seam returns the
EARLIEST entry whose start lies within the last hour, i.e. the quarter up to
45 min stale. ramp arm (intra-hour ramps) mismatches 28..42 of 96 per
non-flat profile; step arm (quarter entries, hour-constant values) 12..18 of
96 -- the three quarters after every price change read the previous price.
Null controls: hourly entries (the resolution the 1-hour span was written
for) = 0 on every profile; flat profile = 0. With --perturb (the 1-hour span
in ``_current_spot_price`` shortened to 15 min, in memory) every quarter arm
reads 0 and the hourly-entries control breaks (273) -- the perturbation proves
the span is the mechanism; an honest fix derives each entry's end from the
next entry's start, as ``_known_prices_for`` already does, and must read 0 on
all three arms. Tolerance: exact (counts).
Machine: B7 audit container (linux). Root rule: cwd (run from repo root).
"""
import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import sys
import time
from datetime import datetime, timedelta, timezone
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, ".")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import custom_components.heatpump_optimizer.coordinator as coord_mod  # noqa: E402
from custom_components.heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)
import profiles  # noqa: E402

PERTURB = "--perturb" in sys.argv
DAY = datetime(2026, 1, 14, 0, 0, tzinfo=timezone.utc)  # a Wednesday
PROFILES = ["winter_typical", "winter_extreme", "summer_typical",
            "summer_negative", "shoulder", "winter_moderate", "flat"]


def quarter_prices(profile: str, arm: str) -> np.ndarray:
    """96 quarter prices. 'step': the profile as-is (constant within each hour,
    the null control); 'ramp': each hour's price linearly interpolated between
    hour mid-points, the intra-hour ramp shape a 15-min MTU produces."""
    p = profiles.prices(profile, DAY.replace(tzinfo=None))
    hourly = p.reshape(24, 4).mean(axis=1)
    if arm == "step":
        return p.astype(float)
    mids = np.arange(24) + 0.5
    t = np.arange(96) / 4.0 + 0.125
    return np.interp(t, mids, hourly)


class _FifteenMinuteSpan:
    """In-memory perturbation: `timedelta(hours=1)` inside the seam becomes
    15 minutes; any other call passes through unchanged."""

    def __call__(self, *a, **kw):
        if kw == {"hours": 1} and not a:
            return timedelta(minutes=15)
        return timedelta(*a, **kw)


def run() -> dict:
    coord = HeatPumpOptimizerCoordinator(
        FakeHass(), FakeEntry(data={"dhw_tank_volume": 180.0})
    )
    out = {}
    for arm in ("ramp", "step", "hourly"):
        for prof in PROFILES:
            if arm == "hourly":
                # Null control: hourly entries, the resolution the seam's
                # 1-hour span was written for. Truth per quarter is its hour's.
                hq = quarter_prices(prof, "step").reshape(24, 4).mean(axis=1)
                q = np.repeat(hq, 4)
                coord._prices = [
                    {"total": float(hq[h]),
                     "starts_at": (DAY + timedelta(hours=h)).isoformat()}
                    for h in range(24)
                ]
            else:
                q = quarter_prices(prof, arm)
                coord._prices = [
                    {"total": float(q[i]),
                     "starts_at": (DAY + timedelta(minutes=15 * i)).isoformat()}
                    for i in range(96)
                ]
            mism = 0
            plan_mism = 0
            abs_err = []
            for i in range(96):
                start = DAY + timedelta(minutes=15 * i)
                now = start + timedelta(minutes=7)
                dt_util.freeze(now)
                try:
                    if PERTURB:
                        with mock.patch.object(coord_mod, "timedelta", _FifteenMinuteSpan()):
                            got = coord._current_spot_price()
                    else:
                        got = coord._current_spot_price()
                finally:
                    dt_util.freeze(None)
                truth = float(q[i])
                plan0 = coord._known_prices_for([start])[0]
                if got != truth:
                    mism += 1
                if got != plan0:
                    plan_mism += 1
                abs_err.append(abs(got - truth))
            out[(arm, prof)] = (mism, plan_mism, float(np.mean(abs_err)),
                                float(np.max(abs_err)))
    return out


def main() -> None:
    c0, t0 = time.process_time(), time.thread_time()
    res = run()
    c1, t1 = time.process_time(), time.thread_time()
    for (arm, prof), (m, pm, mae, mx) in res.items():
        print(f"RESULT mismatch_{arm}_{prof}={m} quarters_of_96")
        print(f"RESULT plan_step0_mismatch_{arm}_{prof}={pm} quarters_of_96")
        print(f"RESULT mean_abs_err_{arm}_{prof}={mae:.5f} currency_per_kWh")
        print(f"RESULT max_abs_err_{arm}_{prof}={mx:.5f} currency_per_kWh")
    ramp = [res[("ramp", p)][2] for p in PROFILES if p != "flat"]
    ramp_m = [res[("ramp", p)][0] for p in PROFILES if p != "flat"]
    print(f"RESULT ramp_cells={len(ramp)}")
    print(f"RESULT ramp_mismatch_range={min(ramp_m)}..{max(ramp_m)} quarters_of_96")
    print(f"RESULT ramp_mae_range={min(ramp):.5f}..{max(ramp):.5f} currency_per_kWh")
    drop = sorted(ramp)[:-1]  # drop the single most favourable (largest) cell
    print(f"RESULT ramp_mae_mean={np.mean(ramp):.5f} currency_per_kWh")
    print(f"RESULT ramp_mae_mean_leave_max_out={np.mean(drop):.5f} currency_per_kWh")
    step_m = [res[("step", p)][0] for p in PROFILES if p != "flat"]
    print(f"RESULT step_mismatch_range={min(step_m)}..{max(step_m)} quarters_of_96")
    hourly_total = sum(res[("hourly", p)][0] for p in PROFILES)
    print(f"RESULT null_hourly_entries_total_mismatch={hourly_total} quarters")
    print(f"RESULT null_flat_step_mismatch={res[('step', 'flat')][0]} quarters")
    print(f"RESULT null_flat_ramp_mismatch={res[('ramp', 'flat')][0]} quarters")
    print(f"RESULT perturbed={int(PERTURB)}")
    tf = (c1 - c0) / max(t1 - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as fh:
            sw = [ln for ln in fh if ln.startswith("pswpin")]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()

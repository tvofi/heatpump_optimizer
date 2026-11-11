"""D1.M3 staleness: a price entity that stops updating, and the plan-age
predicate under clock jumps and DST, on an aware (Europe/Stockholm) clock.

Metric (one line): per scenario, what the production cycle publishes: the
count of horizon steps backed by a published price (``known_steps``), whether
the cycle succeeded, the published ``plan_age_minutes`` / ``plan_stale``, and
the published keys that disclose price staleness.
Count key: the payload ``_async_update_data`` returns and the coordinator's
own ``_plan_age_minutes`` / ``_plan_is_stale``.

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
        tools/audit/round9/D1/s2/staleness.py [--part prices|age|all]
Expected: see RESULT lines (exact for the frozen clock). Baseline
1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: B4.

Perturbation (age part) ``--perturb no_clamp``: ``_plan_age_minutes`` without
its ``max(0, ...)`` clamp, in memory; the backward-jump row's age sign-flips.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")
os.environ["HASTUB_TZ"] = "Europe/Stockholm"

import argparse
import asyncio
import logging
import sys
from datetime import datetime, timedelta
from unittest import mock
from zoneinfo import ZoneInfo

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402

TZ = ZoneInfo("Europe/Stockholm")
CFG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    "price_source": "entity",
    "price_entity": "sensor.prices",
}


def prices_part():
    t0 = datetime(2026, 1, 14, 12, 0, tzinfo=TZ)
    midnight = t0.replace(hour=0)
    rows = [{"start": (midnight + timedelta(hours=h)).isoformat(),
             "value": round(0.5 + 0.1 * (h % 4), 3)} for h in range(48)]
    out = []
    for k in (0, 24, 34, 35.5, 36, 42, 60):
        now = t0 + timedelta(hours=k)
        dt_util.freeze(now)
        hass = FakeHass({
            "sensor.indoor": FakeState("21.4", last_updated=now),
            "sensor.outdoor": FakeState("-3.0", last_updated=now),
            # the price entity's state was last written at t0: it stopped
            "sensor.prices": FakeState("0.5", last_updated=t0,
                                       attributes={"raw_today": rows}),
        })
        c = cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=dict(CFG)))
        ok, status, data = True, None, None
        try:
            data = asyncio.run(c._async_update_data())
        except Exception as err:  # noqa: BLE001
            ok, status = False, f"{type(err).__name__}: {str(err)[:60]}"
        h = c._forecast_arrays(now)
        known = int(sum(h.price_known))
        disclose = sorted(k2 for k2, v in (data or {}).items()
                          if "price" in k2 and ("stale" in k2 or "age" in k2 or "known" in k2))
        out.append((k, known, len(h.prices), ok, c._optimization_result is not None, status, disclose))
        cm._shutdown_process_pool()
    dt_util.freeze(None)
    for k, known, n, ok, planned, status, disclose in out:
        print(f"RESULT stuck_prices_{k}h.known_steps={known} of {n} steps "
              f"cycle_ok={int(ok)} planned={int(planned)} disclose={disclose} {status or ''}")
    blind = sum(1 for k, known, n, ok, planned, _, d in out if ok and planned and known == 0 and not d)
    print(f"RESULT stuck_prices.blind_plans={blind} of {len(out)} rows "
          "(a plan built on zero published prices with no price-staleness key)")


def age_part(perturb):
    hass = FakeHass({})
    c = cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=dict(CFG)))
    patches = []
    if perturb == "no_clamp":
        patches.append(mock.patch.object(
            cm.HeatPumpOptimizerCoordinator, "_plan_age_minutes",
            lambda self: None if self._last_optimization is None else
            cm._utc_age_seconds(dt_util.now(), self._last_optimization) / 60.0))
    for p in patches:
        p.start()
    rows = []
    cases = [
        # (name, solve instant, read instant, true minutes elapsed)
        ("plain_30m", datetime(2026, 1, 14, 12, 0, tzinfo=TZ), datetime(2026, 1, 14, 12, 30, tzinfo=TZ), 30),
        ("plain_100m", datetime(2026, 1, 14, 12, 0, tzinfo=TZ), datetime(2026, 1, 14, 13, 40, tzinfo=TZ), 100),
        # fall-back night: 02:30 CEST -> 02:30 CET is 60 real minutes
        ("dst_fold", datetime(2026, 10, 25, 2, 30, tzinfo=TZ, fold=0), datetime(2026, 10, 25, 2, 30, tzinfo=TZ, fold=1), 60),
        # spring-forward: 01:30 CET -> 03:30 CEST is 60 real minutes
        ("dst_gap", datetime(2026, 3, 29, 1, 30, tzinfo=TZ), datetime(2026, 3, 29, 3, 30, tzinfo=TZ), 60),
        # forward clock jump (NTP after a Pi boots on a saved clock)
        ("jump_fwd_6h", datetime(2026, 1, 14, 12, 0, tzinfo=TZ), datetime(2026, 1, 14, 18, 30, tzinfo=TZ), 30),
        # backward clock correction of 6 h, then 100 real minutes
        ("jump_back_6h", datetime(2026, 1, 14, 18, 0, tzinfo=TZ), datetime(2026, 1, 14, 13, 40, tzinfo=TZ), 100),
    ]
    for name, solved, read, true_min in cases:
        c._last_optimization = solved
        dt_util.freeze(read)
        age = c._plan_age_minutes()
        stale = c._plan_is_stale()
        rows.append((name, age, stale, true_min))
    dt_util.freeze(None)
    for p in patches:
        p.stop()
    wrong = 0
    for name, age, stale, true_min in rows:
        off = abs((age or 0.0) - true_min)
        wrong += int(off > 1.0)
        print(f"RESULT plan_age.{name}={age:.1f} min (true {true_min}) stale={int(stale)} off_by={off:.1f}")
    print(f"RESULT plan_age.rows_off_by_over_1min={wrong} of {len(rows)} "
          "(clock jumps included: the wall clock is the only clock the seam has)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", default="all")
    ap.add_argument("--perturb", default="")
    args = ap.parse_args()
    logging.basicConfig(level=logging.CRITICAL)
    if args.part in ("age", "all"):
        age_part(args.perturb)
    if args.part in ("prices", "all"):
        prices_part()
    print("RESULT thread_factor=1.000")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()

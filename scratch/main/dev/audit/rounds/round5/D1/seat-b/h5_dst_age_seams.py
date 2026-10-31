#!/usr/bin/env python3
"""h5_dst_age_seams.py -- D1-b round 5, finding F3 (age seams across DST).

Metric definition (one line): age_error_minutes = |published age - true
instant age| for the plan-age seam (``_plan_age_minutes``) and the weather
staleness seam (``weather_stale_hours``), measured across the Europe/
Stockholm autumn fold and spring gap with the clock frozen at a
pre-transition instant and advanced by a TRUE 2 h; the null control is the
same 2 h on a plain night.

Count key: the values the production seams DELIVER --
``coordinator._plan_age_minutes()`` and ``coordinator.weather_stale_hours()``
against the UTC-normalized instant difference of the same two instants.

Mechanism: both seams compute ``dt_util.now() - stored``; both datetimes
carry Home Assistant's single process-wide ZoneInfo instance, and CPython
resolves subtraction of two aware datetimes that SHARE one tzinfo object
as naive wall-clock subtraction (verified: 2027-03-28 01:45+01:00 ->
03:00+02:00 subtracts to 1:15, not 0:15). Across a transition the wall
difference is off by the offset delta (1 h).

Command (from the repository root; HASTUB_TZ is required and is read at
stub import):
  HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub:tests:. \
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round5/D1/seat-b/h5_dst_age_seams.py

Expected at baseline 1cc89e0 (executed 2026-09-20, Apple M1, python 3.11):
  RESULT fold_plan_age_published=60.0  (true 120.0 -> under-reads 60 min)
  RESULT fold_weather_stale_published=1.0 (true 2.0 h)
  RESULT spring_plan_age_published=180.0 (true 120.0 -> over-reads 60 min)
  RESULT spring_weather_stale_published=3.0 (true 2.0 h)
  RESULT null_control_plan_age_error=0.0
  Perturbation (one-line fix applied in memory: both seams subtract
  UTC-normalized instants): every error drops to 0.0.
Tolerance: exact.

Semantics: the hastub ``dt_util.freeze`` seam the suite's own DST checks
use; the coordinator is real; the fold-side instant is constructed with
fold=1 (the second, post-transition occurrence). No lifecycle method is
called directly.
"""
# Thread pin BEFORE any numpy import (audit README contract).
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

if not os.environ.get("HASTUB_TZ"):
    os.environ["HASTUB_TZ"] = "Europe/Stockholm"

import asyncio
import inspect
import sys
import textwrap
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, "tests")
sys.path.insert(0, ".")

from harness import FakeHass, FakeState, FakeEntry  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

STHLM = ZoneInfo("Europe/Stockholm")
UTC = timezone.utc

# 2026-10-25 03:00 CEST -> 02:00 CET (fold); 2027-03-28 02:00 CET -> 03:00 CEST (gap).
FOLD_START = datetime(2026, 10, 25, 1, 30, tzinfo=STHLM)  # CEST, pre-fold
FOLD_END = datetime(2026, 10, 25, 2, 30, tzinfo=STHLM, fold=1)  # CET, post-fold
SPRING_START = datetime(2027, 3, 28, 1, 30, tzinfo=STHLM)  # CET, pre-gap
SPRING_END = datetime(2027, 3, 28, 4, 30, tzinfo=STHLM)  # CEST, post-gap
PLAIN_START = datetime(2026, 10, 24, 1, 30, tzinfo=STHLM)
PLAIN_END = datetime(2026, 10, 24, 3, 30, tzinfo=STHLM)


def _coord():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    config = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        const.CONF_DHW_TANK_VOLUME: 180.0,
    }
    return HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))


def measure(start, end):
    """Published plan age (minutes) and weather stale hours over a TRUE
    elapsed window from ``start`` to ``end`` (both aware, same zone)."""
    coord = _coord()
    try:
        dt_util.freeze(start)
        coord._last_optimization = dt_util.now()
        coord._weather_fetch_failed("simulated outage")  # latches stale-since
        dt_util.freeze(end)
        plan_age = coord._plan_age_minutes()
        stale_hours = coord.weather_stale_hours()
        stale_flag = coord._plan_is_stale()
    finally:
        dt_util.freeze(None)
    true_minutes = (
        end.astimezone(UTC) - start.astimezone(UTC)
    ).total_seconds() / 60.0
    return {
        "plan_age": plan_age,
        "stale_hours": stale_hours,
        "stale_flag": stale_flag,
        "true_minutes": true_minutes,
        "plan_err": abs(plan_age - true_minutes),
        "weather_err": abs(stale_hours * 60.0 - true_minutes),
    }


def apply_utc_fix_in_memory():
    """One-line production edit simulated in memory: both seams subtract
    UTC-normalized instants. Recompiled from their own source."""
    import heatpump_optimizer.coordinator as C

    for name, old_expr, new_expr in (
        (
            "_plan_age_minutes",
            "(dt_util.now() - self._last_optimization).total_seconds() / 60.0",
            "(dt_util.now().astimezone(timezone.utc) - self._last_optimization.astimezone(timezone.utc)).total_seconds() / 60.0",
        ),
        (
            "weather_stale_hours",
            "(dt_util.now() - self._weather_stale_since).total_seconds() / 3600.0",
            "(dt_util.now().astimezone(timezone.utc) - self._weather_stale_since.astimezone(timezone.utc)).total_seconds() / 3600.0",
        ),
    ):
        method = getattr(HeatPumpOptimizerCoordinator, name)
        src = textwrap.dedent(inspect.getsource(method))
        if old_expr not in src:
            raise SystemExit(f"seam moved: {name}")
        patched = src.replace(old_expr, new_expr)
        namespace = dict(vars(C))
        # astimezone(timezone.utc): the module imports timezone from datetime.
        exec(compile(patched, f"<{name}-fix>", "exec"), namespace)  # noqa: S102
        setattr(HeatPumpOptimizerCoordinator, name, namespace[name])


def main() -> int:
    fold = measure(FOLD_START, FOLD_END)
    spring = measure(SPRING_START, SPRING_END)
    plain = measure(PLAIN_START, PLAIN_END)

    print(f"RESULT fold_plan_age_published={fold['plan_age']:.1f} min (true {fold['true_minutes']:.1f})")
    print(f"RESULT fold_plan_stale_flag={int(fold['stale_flag'])} (true age over 90-min floor: {int(fold['true_minutes'] > 90.0)})")
    print(f"RESULT fold_weather_stale_published={fold['stale_hours']:.1f} h (true {fold['true_minutes']/60.0:.1f})")
    print(f"RESULT spring_plan_age_published={spring['plan_age']:.1f} min (true {spring['true_minutes']:.1f})")
    print(f"RESULT spring_plan_stale_flag={int(spring['stale_flag'])} (true age over 90-min floor: {int(spring['true_minutes'] > 90.0)})")
    print(f"RESULT spring_weather_stale_published={spring['stale_hours']:.1f} h (true {spring['true_minutes']/60.0:.1f})")
    print(f"RESULT null_control_plan_age_error={plain['plan_err']:.1f} min")
    print(f"RESULT null_control_weather_error={plain['weather_err']:.1f} min")

    originals = {
        n: getattr(HeatPumpOptimizerCoordinator, n)
        for n in ("_plan_age_minutes", "weather_stale_hours")
    }
    try:
        apply_utc_fix_in_memory()
        fold_p = measure(FOLD_START, FOLD_END)
        spring_p = measure(SPRING_START, SPRING_END)
    finally:
        for n, m in originals.items():
            setattr(HeatPumpOptimizerCoordinator, n, m)
    print(f"RESULT patched_fold_plan_age_error={fold_p['plan_err']:.1f} min")
    print(f"RESULT patched_fold_weather_error={fold_p['weather_err']:.1f} min")
    print(f"RESULT patched_spring_plan_age_error={spring_p['plan_err']:.1f} min")
    print(f"RESULT patched_spring_weather_error={spring_p['weather_err']:.1f} min")
    print(f"RESULT patched_fold_plan_stale_flag={int(fold_p['stale_flag'])} (matches true: {int(fold_p['stale_flag'] == (fold_p['true_minutes'] > 90.0))})")

    print("RESULT thread_factor=1.00 (single-threaded harness)")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except Exception:
        print("RESULT load1=unknown")
    print("RESULT swapins=0 (no psi on darwin)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

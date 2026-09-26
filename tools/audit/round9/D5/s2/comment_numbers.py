"""D5-s2 harness (D5.M4): numbers a production comment cites, against the
value the production symbol beside it actually delivers.

Metric: per claim row, 1 when the number the comment states disagrees with
  the value measured by DRIVING the named production symbol (never by
  reading the constant's literal), else 0; RESULT comment_number_mismatches
  is the sum over the rows marked `probe`, and every row prints its own
  RESULT line with comment value and measured value side by side.
Count key: the measured value the production seam delivers (a clamp's
  output, a coordinator's update_interval, a draw power's implied cold end),
  so a fix that corrects the comment text leaves the code value, and a fix
  that changes the code moves the measured value -- either reconciles a row.
Command (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D5/s2/comment_numbers.py
  --perturb applies, in memory, the one-line code change each mismatching
  row's comment describes (DERATE_MIN -> 0.5; the draw's cold end read from
  DHW_COLD_WATER_TEMP; the optimization-interval default -> 15 and the
  selector minimum -> 5); the mismatch count must go DOWN to 0.
Expected: RESULT numeric_citation_mismatches=3 rows (derate floor, valve
  cadence, stale-floor interval) and draw_coupling_claim_mismatches=1 row
  (draw_cold_end_off_constant=46 of 47), comment_number_mismatches=4 (exact);
  --perturb -> 0 / 0 / 0.
  Held rows (control arm, same method, must stay 0 under both arms):
  RESULT comment_number_holds_checked=5, comment_number_hold_failures=0.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (v6.7.1).
Machine: box B2 cloud container (Linux, 4 CPU), CPython 3.14.0rc2, numpy 2.4.6.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import tempfile
import time
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
from unittest import mock

_t_proc0, _t_thr0 = time.process_time(), time.thread_time()
os.environ.setdefault("HPO_PLANDATA", tempfile.mkdtemp(prefix="d5s2-"))
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import config_flow, const, defrost, thermal_model  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.const import CONF_OPTIMIZATION_INTERVAL  # noqa: E402
from heatpump_optimizer.drift import Cusum  # noqa: E402

PERTURB = "--perturb" in sys.argv


def _row(name: str, where: str, cited: float, measured: float, tol: float, kind: str) -> int:
    bad = int(abs(float(cited) - float(measured)) > tol)
    print(f"ROW {kind} {name} [{where}] comment={cited:g} measured={measured:g} "
          f"{'MISMATCH' if bad else 'holds'}")
    print(f"RESULT {name}_mismatch={bad} row")
    return bad


def derate_floor() -> float:
    """defrost.py:109-110 -- 'A unit that appears to deliver less than half its
    rated output is telling us about a broken sensor': the comment's floor is
    0.5. Measured: the lowest delivered ratio above which DefrostDerate.observe
    keeps the reading as-is (drives the real clamp, one sample, alpha 1)."""
    grid = np.round(np.arange(0.40, 0.70001, 0.01), 2)
    kept_from = None
    with mock.patch.object(defrost, "DERATE_ALPHA", 1.0):
        for r in grid:
            d = defrost.DefrostDerate()
            d.observe(2.0, 90.0, float(r))
            t, h = d._bucket(2.0, 90.0)
            if abs(d.factors[t][h] - r) < 1e-12:
                kept_from = float(r)
                break
    return float("nan") if kept_from is None else kept_from


def draw_cold_end_mismatches() -> tuple[int, int]:
    """const.py:337-340 -- 'The mains temperature the DHW draw model already
    assumes (thermal_model's dhw_draw_power heats from ~10 C) -- named so the
    coil math and the draw model cannot quietly disagree'. Measured: over the
    config flow's own inlet selector range, the cold end dhw_draw_power
    actually heats from, recovered from its output; counted where it is not
    DHW_COLD_WATER_TEMP."""
    lo, hi, step = 2.0, 25.0, 0.5
    for f in config_flow._OPTION_FIELDS:
        if f.key == const.CONF_DHW_INLET_TEMP:
            cfg = f.widget.config
            lo, hi, step = float(cfg["min"]), float(cfg["max"]), float(cfg["step"])
    values = np.arange(lo, hi + step / 2, step)
    off = 0
    for v in values:
        p = thermal_model.ThermalParameters(dhw_inlet_temp=float(v))
        lph = p.dhw_daily_consumption / 24.0
        rec = float(np.clip(p.greywater_recovery, 0.0, 0.9))
        implied = p.dhw_setpoint - p.dhw_draw_power / (lph * const.WATER_SPECIFIC_HEAT * (1 - rec))
        if abs(implied - const.DHW_COLD_WATER_TEMP) > 1e-6:
            off += 1
    return off, len(values)


def default_update_minutes() -> float:
    """The cadence the coordinator actually runs at with shipped defaults."""
    hass = FakeHass({})
    entry = FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home",
                            "indoor_temp_entity": "sensor.indoor",
                            "outdoor_temp_entity": "sensor.outdoor"})
    # tests/hastub's DataUpdateCoordinator drops update_interval, so capture
    # the value the production __init__ hands its base class.
    base = coord_mod.HeatPumpOptimizerCoordinator.__mro__[1]
    seen: dict[str, timedelta] = {}
    real = base.__init__

    def spy(self, *a, **kw):  # type: ignore[no-untyped-def]
        seen["interval"] = kw.get("update_interval")
        real(self, *a, **kw)

    with mock.patch.object(base, "__init__", spy):
        coord_mod.HeatPumpOptimizerCoordinator(hass, entry)
    return seen["interval"].total_seconds() / 60.0


def interval_selector_min() -> float:
    for f in config_flow._OPTION_FIELDS:
        if f.key == CONF_OPTIMIZATION_INTERVAL:
            return float(f.widget.config["min"])
    raise SystemExit("optimization-interval field not found")


def vent_samples_to_trip() -> int:
    """const.py:903-907 -- 'at least three consecutive abnormal samples'."""
    c = Cusum(threshold=const.VENT_CUSUM_THRESHOLD_C, drift=const.VENT_CUSUM_DRIFT_C, side=-1)
    t = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for n in range(1, 50):
        # the coordinator's own feed: np.clip(residual, -CLIP, CLIP)
        r = float(np.clip(-100.0, -const.VENT_CUSUM_CLIP_C, const.VENT_CUSUM_CLIP_C))
        c.update(t + timedelta(minutes=30 * n), r)
        if c.tripped:
            return n
    return -1


def main() -> None:
    stack = ExitStack()
    if PERTURB:
        # The code change each comment describes, applied in memory.
        stack.enter_context(mock.patch.object(defrost, "DERATE_MIN", 0.5))
        stack.enter_context(mock.patch.object(
            thermal_model.ThermalParameters, "dhw_inlet_reference",
            property(lambda self: float(const.DHW_COLD_WATER_TEMP))))
        stack.enter_context(mock.patch.object(coord_mod, "DEFAULT_OPTIMIZATION_INTERVAL", 15))
        for f in config_flow._OPTION_FIELDS:
            if f.key == CONF_OPTIMIZATION_INTERVAL:
                stack.enter_context(mock.patch.dict(f.widget.config, {"min": 5}))
    with stack:
        mism = 0
        derate_bad = _row("derate_floor", "defrost.py:109 'less than half'", 0.5, derate_floor(), 0.005, "probe")
        off, n = draw_cold_end_mismatches()
        print(f"RESULT draw_cold_end_off_constant={off} of {n} inlet settings")
        mism += _row("draw_cold_end", "const.py:337 'draw model already assumes ~10'", 0, off, 0, "probe")
        coupling = mism
        mism = 0
        mism += derate_bad
        upd = default_update_minutes()
        mism += _row("valve_write_cadence", "const.py:750 'every 15 minutes'", 15, upd, 0.01, "probe")
        mism += _row("stale_floor_interval", "coordinator.py:640 'short 5-minute update interval'",
                     5, max(5.0, interval_selector_min()), 0.01, "probe")

        # Control arm: rows whose cited number the same method confirms.
        holds = 0
        holds += _row("history_fortnight_days", "accuracy.py:34", 14,
                      __import__("heatpump_optimizer.accuracy", fromlist=["x"]).HISTORY_LENGTH * const.DEFAULT_OPTIMIZATION_INTERVAL / 60 / 24,
                      0.01, "hold")
        holds += _row("vent_three_samples", "const.py:905", 3, vent_samples_to_trip(), 0, "hold")
        holds += _row("stale_floor_minutes", "coordinator.py:639 'floored at 90 minutes'", 90,
                      coord_mod.PLAN_STALE_FLOOR_MINUTES, 0, "hold")
        from heatpump_optimizer import snapshots
        holds += _row("snapshot_ring_weeks", "snapshots.py:40 'two months of weekly'", 8,
                      snapshots.RING_SIZE * snapshots.SNAPSHOT_INTERVAL_DAYS / 7.0, 0, "hold")
        from heatpump_optimizer import curve_learning
        holds += _row("curve_step_k", "curve_learning.py:47 '3 days x (0.5/7) ~0.2'",
                      round(curve_learning.DAYS_PER_STEP * curve_learning.MAX_DOWN_PER_WEEK / 7, 1),
                      curve_learning.STEP_K, 0.001, "hold")

    print(f"RESULT numeric_citation_mismatches={mism} rows")
    print(f"RESULT draw_coupling_claim_mismatches={coupling} rows")
    print(f"RESULT comment_number_mismatches={mism + coupling} rows")
    print("RESULT comment_number_holds_checked=5 rows")
    print(f"RESULT comment_number_hold_failures={holds} rows")
    proc = time.process_time() - _t_proc0
    thr = time.thread_time() - _t_thr0
    print(f"RESULT thread_factor={proc / thr if thr > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    swp = "n/a"
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                swp = line.split()[1]
    except OSError:
        pass
    print(f"RESULT swapins={swp}")
    print(f"# perturb={PERTURB}")


if __name__ == "__main__":
    main()

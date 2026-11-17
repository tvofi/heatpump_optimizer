"""D2.M5 tank-fall-after-charge: the tank reading's fall in the minutes after a
charge starts must not be booked as draw, on every combi_tank construction.

Drives the production learner (dhw_learning.DhwProfileLearner.async_learn_dynamics,
which calls ChargeSettle.classify/advance and async_fold_draw_stats into
dhw_draws.DrawStats) through a sampled tank trace with NO hot water drawn at all:
the only fall beyond standby is the charge-start dip (DHW_CHARGE_DIP_MAX_K's
"3-5 K within 4-10 min"). Three charge shapes per cell, 10-minute sampling:
  short   : the plan's charge flag covers one sample, the dip lands after the
            slot ends and recovers unheated (the case ChargeSettle was built for;
            the null control: booked must be ~0)
  long_a  : charge of 60 min, the 4 K dip reaches the FIRST heated sample, the
            reading then climbs while heated
  long_b  : charge of 60 min, the 4 K dip reaches the SECOND heated sample, the
            reading then climbs while heated
Standby in the trace follows the learner's own _standby_rate, so standby books 0.

Metric (one line): booked_kwh = sum of every DrawStats occurrence (closed reservoirs
plus the open one) after the trace, kWh; identity 0 (tol 0.05 kWh); key: the
production DrawStats the p90 ready target reads.
Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s3/m5_tankfall.py
      --perturb-skip-heated : async_fold_draw_stats books nothing on an interval that
      starts or ends on a heated sample (charge or the learner's heating flag): long
      shapes' booked_kwh must go to_zero.
Expected at baseline: short ~0; long_a and long_b ~ 4 K x store capacity on every cell.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B6 (shared).
"""
import _common  # noqa: F401
from _common import footer

import argparse
import asyncio
import sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "custom_components")
import harness  # noqa: F401,E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const, dhw_learning  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--perturb-skip-heated", action="store_true")
A = ap.parse_args()

if A.perturb_skip_heated:
    _orig_fold = dhw_learning.DhwProfileLearner.async_fold_draw_stats

    async def _fold(self, now, previous_temp, temp_drop, dt_h, *, charge=False, recovered_k=0.0):
        if charge or self.heating_since_sample:
            temp_drop = min(temp_drop, 0.0)
        return await _orig_fold(self, now, previous_temp, temp_drop, dt_h, charge=charge, recovered_k=recovered_k)

    dhw_learning.DhwProfileLearner.async_fold_draw_stats = _fold


def params_for(kind):
    base = ThermalParameters()
    pre = const.COMBI_TANK_PRESETS[kind]
    p = replace(base, dhw_enabled=True, dhw_combi_tank_enabled=True,
                combi_dhw_effectiveness=pre.effectiveness,
                combi_potable_volume_l=pre.potable_volume_l,
                buffer_tank_volume=500.0, mixing_valve_mode="smart_write")
    return p


def trace(shape, learner, t0, T0):
    """(time, reading, heating) rows; standby from the learner's own model."""
    rows = []
    T = T0
    t = t0
    dt = timedelta(minutes=10)
    heat_on = {"short": (2, 2), "long_a": (2, 7), "long_b": (2, 7)}[shape]
    for k in range(30):
        heating = heat_on[0] <= k <= heat_on[1]
        rows.append((t, T, heating))
        # evolve to next sample
        sb = learner._standby_rate(T) * (dt.total_seconds() / 3600.0)
        nxt = T - sb
        if shape == "long_a" and k == 1:
            nxt -= 4.0          # the dip lands at the first heated sample (k=2)
        if shape == "long_b" and k == 2:
            nxt -= 4.0          # the dip lands at the second heated sample (k=3)
        if shape in ("long_a", "long_b") and 3 <= k <= 6:
            nxt += 3.0          # the charge climbs, heated
        if shape == "short" and k == 2:
            nxt -= 4.0          # the dip after the one-sample slot (settling)
        if shape == "short" and k == 3:
            nxt += 4.0          # it recovers unheated
        T = nxt
        t = t + dt
    return rows


async def run_cell(kind, shape):
    p = params_for(kind)
    assert p.combi_tank_active, kind
    state = {"heating": False}
    learner = dhw_learning.DhwProfileLearner(
        harness.FakeHass(), "e", lambda: p, publish=lambda **k: None,
        frozen=lambda _e: None, heating_active=lambda: state["heating"],
        external_heat_active=lambda: False)

    async def _noop(*a, **k):
        return None
    learner.async_save_draws = _noop
    learner.async_save_profile = _noop
    t0 = datetime(2026, 1, 14, 6, 0, tzinfo=timezone.utc)
    for t, T, heating in trace(shape, learner, t0, 50.0):
        dt_util.freeze(t)
        state["heating"] = heating
        await learner.async_learn_dynamics(T)
    ds = learner.draw_stats
    booked = sum(sum(v) for v in ds.reservoirs.values()) + ds._open_kwh
    cap = p.dhw_store.capacity_kwh_per_c
    return booked, cap


worst_long = 0.0
worst_short = 0.0
for kind in ("external_station", "internal_coil", "tank_in_tank"):
    parts = []
    for shape in ("short", "long_a", "long_b"):
        booked, cap = asyncio.run(run_cell(kind, shape))
        parts.append(f"{shape}:booked={booked:.4f}kWh dip_equiv={4.0 * cap:.4f}kWh")
        if shape == "short":
            worst_short = max(worst_short, abs(booked))
        else:
            worst_long = max(worst_long, booked)
    print(f"CELL tank-fall-after-charge combi_tank={kind} cap={cap:.4f}kWh/K " + " ".join(parts))
dt_util.freeze(None)
print(f"RESULT booked_kwh_long_max={worst_long:.4f} kWh")
print(f"RESULT booked_kwh_short_max={worst_short:.4f} kWh")
footer()

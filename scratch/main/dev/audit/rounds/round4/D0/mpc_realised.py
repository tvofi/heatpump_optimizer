"""D0 round 4 -- is the ftol gap realised under receding-horizon re-planning?

METRIC (one line): per grid cell, the realised electricity cost of one
simulated day (SEK, sum over 96 quarter-hour steps of
``(space_kW + dhw_kW) * 0.25 * price``) under closed-loop re-planning every
2 h, production minus the same loop with the single change of L-BFGS-B's
``ftol`` 1e-6 -> 1e-14 in ``optimizer.py:_multi_start_minimize``.

A one-shot objective gap can be masked by MPC: if re-planning at the next
step reaches the same trajectory, the gap is never spent.  This closes that
hole -- it is the number a user's meter would see.

The loop replicates ``tests/rolling.py:run_rolling``'s shape (that module
runs its whole check suite at import and ``sys.exit``s, so it cannot be
imported; the loop is rebuilt here, 40 lines, with ``plant_error=1.0`` so the
only difference between the arms is the plan).

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D0/mpc_realised.py

EXPECTED (baseline 7dd68dd, this machine, +/- 0.01 SEK/day per cell):

    mean_realised_delta_priced_SEK_per_day    0.320965  +/- 0.02
    max_realised_delta_priced_SEK_per_day     1.53174   +/- 0.02
    min_realised_delta_priced_SEK_per_day    -0.280198  +/- 0.02
    loo_mean_realised_delta_priced_SEK_per_day 0.147996 +/- 0.02
    mean_realised_delta_flat_SEK_per_day     -2.11318   +/- 0.02  (null control:
        it moves the WRONG WAY and by more than the priced mean, which is what
        refuses the money claim -- see REPORT.md D0-01)
    cells_production_cheaper                  4  (of 8 priced)
    cells_challenger_worse_comfort            1  (of 10; 0.0016 degree-steps)

Runtime on this box, fully loaded: about 30 minutes.

BASELINE SHA: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, numpy/OpenBLAS, python 3.11

INSTRUMENTED SYMBOL: custom_components/heatpump_optimizer/optimizer.py
:_scoped_minimize (hooked), driving
``optimizer.py:HeatPumpOptimizer.optimize`` once per re-plan and
``thermal_model.py:ThermalModel.simulate_trajectory_with_dhw`` as the plant.

PERTURBATION: set production's ``ftol`` to 1e-14 in
``optimizer.py:_multi_start_minimize`` and ``_lbfgsb_restart``; every
realised delta must fall to 0.0 SEK.  Raising it to 1e-4 must grow them.

NULL CONTROL: the ``flat`` price rows, reported separately.
LEAVE-ONE-OUT: priced aggregate printed with the largest-delta cell dropped.

CONTENTION: realised cost is a sum of scheduled power times price -- an
arithmetic quantity, not a timing.  Contention-immune.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D0"))

import d0lib as L  # noqa: E402

import numpy as np  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from unittest import mock  # noqa: E402

from profiles import DT, house, prices, weather  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig,
)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState,
)

START = datetime(2026, 1, 15, 0, 0)
REPLAN_HOURS = 2.0
#: Four of the seven priced profiles plus the flat null control, two
#: topologies: ten cells.  The full 8x5x2 grid of ftol_gap.py is 24x the
#: solve count here (each cell is 12 re-plans per arm) and does not fit the
#: round's wall-clock budget; these four span the price shapes the gap
#: separated (sharp double peak, scarcity, moderate, negative midday).
PRICE_SUBSET = ("winter_typical", "winter_extreme", "shoulder",
                "summer_negative")
HORIZON_H = 24
MIN_TEMP = 17.0

_real_scoped = O._scoped_minimize


def tight_scoped(*a, **kw):
    kw = dict(kw)
    opts = dict(kw.get("options") or {})
    opts["ftol"] = 1e-14
    kw["options"] = opts
    return _real_scoped(*a, **kw)


def tile(series, steps):
    s = np.asarray(series, dtype=float)
    if len(s) >= steps:
        return s[:steps]
    return np.tile(s, int(np.ceil(steps / len(s))))[:steps]


def rollout(price_p, weather_p, two_zone):
    """One simulated day of closed-loop control. Returns (SEK, viol, minT)."""
    cfg = house(two_zone=two_zone, dhw=True)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = True
    model = ThermalModel(params)
    plant = ThermalModel(ThermalParameters.from_config(cfg))
    plant.params.dhw_enabled = True
    opt_cfg = OptimizationConfig(
        horizon_hours=HORIZON_H, time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"])
    optimizer = HeatPumpOptimizer(model, opt_cfg)

    total = int(24 / DT)
    hsteps = int(HORIZON_H / DT)
    span = total + hsteps + 4
    pr = tile(prices(price_p, START), span)
    ot, wi, ra, so = (tile(a, span) for a in weather(weather_p, START))

    state = ThermalState(
        room_temperature=cfg["target_temperature"],
        slab_temperature=cfg["target_temperature"] + 1.0,
        outdoor_temperature=float(ot[0]),
        upper_floor_temperature=cfg["target_temperature"],
        lower_floor_temperature=cfg["target_temperature"],
        dhw_temperature=52.0, dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0)

    every = max(1, int(REPLAN_HOURS / DT))
    plan = None
    sek = 0.0
    rooms = []
    for step in range(total):
        now = START + timedelta(hours=step * DT)
        if step % every == 0:
            plan = optimizer.optimize(
                state, pr[step:step + hsteps], ot[step:step + hsteps],
                wi[step:step + hsteps], ra[step:step + hsteps],
                so[step:step + hsteps], now)
        off = step % every
        sp = float(plan.power_schedule[off])
        dw = (float(plan.dhw_power_schedule[off])
              if plan.dhw_power_schedule else 0.0)
        room, slab, up, lo, tank, _, _ = plant.simulate_trajectory_with_dhw(
            initial_state=state,
            space_power_schedule=np.array([sp]),
            dhw_power_schedule=np.array([dw]),
            outdoor_temps=ot[step:step + 1], wind_speeds=wi[step:step + 1],
            precipitation=ra[step:step + 1], solar_radiation=so[step:step + 1],
            start_hour=now.hour + now.minute / 60.0, dt_hours=DT)
        state = ThermalState(
            room_temperature=float(room[-1]), slab_temperature=float(slab[-1]),
            outdoor_temperature=float(ot[step]),
            upper_floor_temperature=float(up[-1]),
            lower_floor_temperature=float(lo[-1]),
            dhw_temperature=float(tank[-1]),
            buffer_tank_temperature=state.buffer_tank_temperature,
            wood_tank_temperature=state.wood_tank_temperature,
            dhw_hours_since_legionella=(
                0.0 if float(tank[-1]) >= params.dhw_legionella_temp - 1.0
                else (state.dhw_hours_since_legionella or 0.0) + DT))
        sek += (sp + dw) * DT * float(pr[step])
        rooms.append(min(float(up[-1]), float(lo[-1])) if two_zone
                     else float(room[-1]))
    r = np.asarray(rooms)
    return sek, float(np.maximum(0.0, MIN_TEMP - r).sum()), float(r.min())


def main() -> int:
    cond = L.Conditions()
    rows = []
    for price_p in PRICE_SUBSET + (L.FLAT,):
        for tz in (False, True):
            a = rollout(price_p, "winter_cold", tz)
            with mock.patch.object(O, "_scoped_minimize", tight_scoped):
                b = rollout(price_p, "winter_cold", tz)
            rows.append({"price": price_p, "tz": tz,
                         "sek_a": a[0], "sek_b": b[0], "d": a[0] - b[0],
                         "viol_a": a[1], "viol_b": b[1],
                         "minT_a": a[2], "minT_b": b[2]})
            print(f"CELL {price_p:16s} tz={int(tz)} "
                  f"realised {a[0]:.4f} -> {b[0]:.4f} SEK/day "
                  f"({a[0] - b[0]:+.4f})  viol {a[1]:.4f}->{b[1]:.4f}  "
                  f"minT {a[2]:.3f}->{b[2]:.3f}", flush=True)

    priced = [r for r in rows if r["price"] != L.FLAT]
    flat = [r for r in rows if r["price"] == L.FLAT]
    dp = [r["d"] for r in priced]
    df = [r["d"] for r in flat]
    mean_p, min_p, max_p, loo_p = L.loo(dp)
    mean_f, min_f, max_f, loo_f = L.loo(df)

    L.emit("cells_priced", len(priced))
    L.emit("cells_flat_null_control", len(flat))
    L.emit("mean_realised_delta_priced_SEK_per_day", mean_p, "SEK")
    L.emit("max_realised_delta_priced_SEK_per_day", max_p, "SEK")
    L.emit("min_realised_delta_priced_SEK_per_day", min_p, "SEK")
    L.emit("loo_mean_realised_delta_priced_SEK_per_day", loo_p, "SEK")
    L.emit("mean_realised_delta_flat_SEK_per_day", mean_f, "SEK")
    L.emit("max_realised_delta_flat_SEK_per_day", max_f, "SEK")
    L.emit("mean_bill_priced_SEK_per_day",
           sum(r["sek_a"] for r in priced) / len(priced), "SEK")
    L.emit("mean_delta_share_of_bill_pct",
           100.0 * sum(dp) / sum(r["sek_a"] for r in priced), "%")
    L.emit("cells_challenger_worse_comfort",
           sum(1 for r in rows if r["viol_b"] > r["viol_a"] + 1e-6))
    L.emit("cells_production_cheaper", sum(1 for r in priced if r["d"] < -1e-4))
    L.emit("max_comfort_violation_either_arm",
           max(max(r["viol_a"], r["viol_b"]) for r in rows))
    cond.emit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

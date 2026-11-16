#!/usr/bin/env python3
"""R10-ADVISOR-STEADY-START (#2257): the carrier harness of design 55f90c7c6.

WHY IT EXISTS. The what-if's steady figure prices a schedule ask as the
difference of two reference energies. Which plan the live energy is read from,
and on which weather the reference runs, decides whether the figure keeps the
ask's sign once the scheduled plan is older than the what-if. This probe
records the periodic thermostat energy (two passes) of the what-if solve, of
the scheduled plan and of the zero ask at the what-if's instant, on the
horizon's own weather and on its mean, and counts the figures against the ask.
It measures the four alternatives by wrapping the solve's own thermostat pass
(``reference_day``'s passes are left alone), and counts the answer's steady
key itself on the ``built`` line.

Run from the tree root:

  AGE=<steps> [STEP=<kelvin>] PYTHONPATH=tests/hastub:tests:custom_components \
      python3 dev/audit/harnesses/r10_advisor_steady_carrier.py [out.json]

AGE: quarter-hour steps between the scheduled solve and the what-if (0, 1, 2).
STEP: the outdoor forecast of the calendar day after the solve is -5 + STEP
(0 = the fixture's flat -5; the null of the weather term).

Fixture: ``_solve_coord`` of tests/features.py (no hot-water tank), hours
01..23 step 2. Asks per hour: eight that move the schedule (the two tile
degrees, six panel asks) and three that do not (the zero ask, the cap tile,
hot water alone).

Keys: ``off`` and ``at`` are the live side read off the scheduled plan and at
the what-if's instant, on the horizon's own weather; ``offm`` and ``atm`` the
same on the mean weather; ``built`` is the answer's own steady key and solve
count, every ask asked with ``steady=True``. ``RESULT ... m2`` is the zero
ask's figure with the live side off the scheduled plan: what a branch chosen
by energy inequality would show.
"""
from __future__ import annotations

import ast
import asyncio as _asyncio
import json
import os
import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass, FakeState, with_config  # noqa: F401
from homeassistant.util import dt as dt_util

import heatpump_optimizer.coordinator as cmod
import heatpump_optimizer.optimizer as omod
from heatpump_optimizer import price_tiles, whatif
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord

AGE = int(os.environ.get("AGE", "0"))
STEP = float(os.environ.get("STEP", "0"))
OUT = sys.argv[1] if len(sys.argv) > 1 else None

_src = Path("tests/features.py").read_text()
_want = {"_SolveHass", "_solve_coord", "_solve_record_now"}
_ns = globals()
for node in ast.parse(_src).body:
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in _want:
        exec(compile(ast.Module([node], []), "features-slice", "exec"), _ns)  # noqa: S102
        _want.discard(node.name)
assert not _want, _want

Opt = omod.HeatPumpOptimizer


async def _no_worker(hass, fn, *args):
    return fn(*args)


cmod._await_process = _no_worker

_real_optimize = Opt.optimize
_real_cbp = Opt._compute_baseline_power
_real_held = omod._thermostat_held_state
_spun = {"state": None}
SOLVES = {"n": 0}
REF = {}


def _held(model, state, weather, target):
    if _spun["state"] is not None:
        return _spun["state"]
    return _real_held(model, state, weather, target)


def _cbp(self, weather, initial_state, dt, comfort_targets=None, start=None):
    if start is not None or _IN_REFERENCE["on"]:  # reference_day's own passes: not a solve's, not probed
        return _real_cbp(self, weather, initial_state, dt, comfort_targets, start)
    out = _real_cbp(self, weather, initial_state, dt, comfort_targets)  # the solve's own, untouched
    n = len(weather.outdoor_temps)
    _spun["state"] = out[1]
    try:
        p2, _end = _real_cbp(self, weather, initial_state, dt, comfort_targets)
    finally:
        _spun["state"] = None
    import dataclasses as _dc
    flat = _dc.replace(weather, **{
        f.name: np.full(np.shape(getattr(weather, f.name)), float(np.mean(np.asarray(getattr(weather, f.name), float))))
        for f in _dc.fields(weather) if getattr(weather, f.name) is not None and np.ndim(getattr(weather, f.name)) == 1
    })
    _m1, mend = _real_cbp(self, flat, initial_state, dt, comfort_targets)
    _spun["state"] = mend
    try:
        m2, _end = _real_cbp(self, flat, initial_state, dt, comfort_targets)
    finally:
        _spun["state"] = None
    self._probe = {
        "kwhm": float(np.sum(m2)) * dt,
        "kwh2": float(np.sum(p2)) * dt, "kwh1": float(np.sum(out[0])) * dt, "hours": n * dt,
        "targets": omod._baseline_targets(comfort_targets, n, self.config.target_temp),
    }
    return out


def _optimize(self, *a, inputs=None, **k):
    SOLVES["n"] += 1
    result = _real_optimize(self, *a, inputs=inputs, **k)
    REF[(round(float(result.baseline_cost), 9), round(float(result.predicted_cost), 9))] = {**self._probe, "mean_price": float(np.mean(inputs.forecast.prices))}
    return result


_IN_REFERENCE = {"on": False}
_real_reference = Opt.reference_day


def _reference(self, inputs):
    _IN_REFERENCE["on"] = True
    try:
        return _real_reference(self, inputs)
    finally:
        _IN_REFERENCE["on"] = False


Opt.reference_day = _reference
omod._thermostat_held_state = _held
Opt._compute_baseline_power = _cbp
Opt.optimize = _optimize

_cap = {}
_real_md = price_tiles.monthly_deltas


def _md(live, sim, extra, horizon_hours, steady=None):
    _cap["last"] = (live, sim, steady)
    return _real_md(live, sim, extra, horizon_hours, steady)


price_tiles.monthly_deltas = _md


def _ref(r):
    return REF[(round(float(r.baseline_cost), 9), round(float(r.predicted_cost), 9))]


async def _one(hour):
    coord = _solve_coord()  # noqa: F821
    if STEP:
        day0 = dt_util.now().date()
        for row in coord._weather_forecast:
            if dt_util.parse_datetime(row["datetime"]).date() > day0:
                row["temperature"] = -5.0 + STEP
    coord._fuse_advisor_at = dt_util.now()
    await coord.async_run_optimization()
    dt_util.freeze(dt_util.now() + timedelta(minutes=15 * AGE))
    record = _solve_record_now(coord)  # noqa: F821
    c = record.config
    day = c.comfort_temp_day if getattr(c, "comfort_temp_day", None) is not None else c.target_temp
    asks = [("panel_zero", {"target_temp": c.target_temp})] + list(price_tiles.specs(c, record.params.max_electrical_power)) + [
        ("panel_comfort_plus_half", {"target_temp": c.target_temp + 0.5, "comfort_temp_day": day + 0.5}),
        ("panel_comfort_minus_half", {"target_temp": c.target_temp - 0.5, "comfort_temp_day": day - 0.5}),
        ("panel_daystart_earlier", {"day_start_hour": c.day_start_hour - 1}),
        ("panel_daystart_later", {"day_start_hour": c.day_start_hour + 1}),
        ("panel_dayend_later", {"day_end_hour": c.day_end_hour + 1}),
        ("panel_dayend_earlier", {"day_end_hour": c.day_end_hour - 1}),
        ("panel_hotwater_only", {"dhw_min_temperature": float(record.params.dhw_min_temp) + 2.0}),
    ]
    rows = []
    zero = None
    for name, overrides in asks:
        whatif.state_for(coord).last_at = None
        n0 = SOLVES["n"]
        answer = await coord.async_simulate(dict(overrides), steady=True)
        if answer.get("monthly_held_cost_delta") is None:
            rows.append({"hour": hour, "ask": name, "error": answer.get("error")})
            print("ERROR", hour, name, answer.get("error"))
            continue
        live, sim, steady = _cap["last"]
        L, S = _ref(live), _ref(sim)
        if name == "panel_zero":
            zero = S
        Z = zero
        row = {
            "hour": hour, "age": AGE, "ask": name, "solves": SOLVES["n"] - n0,
            "steady_built": answer.get(whatif.STEADY_KEY), "held": answer.get("monthly_held_cost_delta"),
            "hours": S["hours"],
            "sim_kwh": S["kwh2"], "off_kwh": L["kwh2"], "at_kwh": Z["kwh2"],
            "off_price": L["mean_price"], "at_price": S["mean_price"],
            "targets_eq_at": S["targets"] == Z["targets"], "targets_eq_off": S["targets"] == L["targets"],
            "dE_off": S["kwh2"] - L["kwh2"], "dE_at": S["kwh2"] - Z["kwh2"],
        }
        row["dE_offm"] = S["kwhm"] - L["kwhm"]; row["dE_atm"] = S["kwhm"] - Z["kwhm"]
        row["targets_eq_offm"] = row["targets_eq_off"]; row["targets_eq_atm"] = row["targets_eq_at"]
        row["fig_offm"] = row["dE_offm"] * L["mean_price"] * 730.0 / 24.0
        row["fig_atm"] = row["dE_atm"] * S["mean_price"] * 730.0 / 24.0
        row["fig_off"] = row["dE_off"] * L["mean_price"] * 730.0 / 24.0
        row["fig_at"] = row["dE_at"] * S["mean_price"] * 730.0 / 24.0
        rows.append(row)
    return rows


WANT = {
    "target_minus_1": -1, "target_plus_1": 1, "panel_comfort_plus_half": 1, "panel_comfort_minus_half": -1,
    "panel_daystart_earlier": 1, "panel_daystart_later": -1, "panel_dayend_later": 1, "panel_dayend_earlier": -1,
}


def main():
    allrows = []
    for hour in range(1, 24, 2):
        dt_util.freeze(dt_util.now().replace(hour=hour, minute=7, second=0, microsecond=0))
        try:
            allrows += _asyncio.run(_one(hour))
        finally:
            dt_util.freeze(None)
    ok = [r for r in allrows if "error" not in r]
    names = []
    for r in ok:
        if r["ask"] not in names:
            names.append(r["ask"])
    for name in names:
        rs = [r for r in ok if r["ask"] == name]
        w = WANT.get(name)
        for key in ("off", "at", "offm", "atm"):
            figs = [r["fig_" + key] for r in rs]
            des = [r["dE_" + key] for r in rs]
            wrong = "-" if w is None else sum(1 for f in figs if f * w <= 0.0)
            print(f"ASK age {AGE} step {STEP:g} {name:26s} {key:3s} n {len(rs)} wrong {wrong} "
                  f"fig {min(figs):+9.2f}..{max(figs):+9.2f} dE {min(des):+.6f}..{max(des):+.6f} "
                  f"exact0 {sum(1 for d in des if d == 0.0)} targets_eq {sum(1 for r in rs if r['targets_eq_' + key])} "
                  f"solves {sorted(set(r['solves'] for r in rs))} built {min((r['steady_built'] or 0.0) for r in rs):+.1f}..{max((r['steady_built'] or 0.0) for r in rs):+.1f}")
    sched = [r for r in ok if r["ask"] in WANT]
    for key in ("off", "at", "offm", "atm"):
        print(f"RESULT age {AGE} step {STEP:g} {key}: schedule figures {len(sched)} against the ask "
              f"{sum(1 for r in sched if r['fig_' + key] * WANT[r['ask']] <= 0.0)}; "
              f"no-schedule asks (zero, cap, hot water) {sum(1 for r in ok if r['ask'] not in WANT)} "
              f"energy difference exactly 0 on {sum(1 for r in ok if r['ask'] not in WANT and r['dE_' + key] == 0.0)}, "
              f"targets equal on {sum(1 for r in ok if r['ask'] not in WANT and r['targets_eq_' + key])}")
    zeros = [r["fig_off"] for r in ok if r["ask"] == "panel_zero"]
    if zeros:
        print(f"RESULT age {AGE} step {STEP:g} m2: zero ask priced off the scheduled plan "
              f"{min(zeros):+.1f}..{max(zeros):+.1f} a month, off 0 on {sum(1 for f in zeros if f != 0.0)} of {len(zeros)}")
    print(f"RESULT age {AGE} step {STEP:g} built: schedule figures {len(sched)} against the ask "
          f"{sum(1 for r in sched if r['steady_built'] is None or r['steady_built'] * WANT[r['ask']] <= 0.0)}, "
          f"solved once on {sum(1 for r in sched if r['solves'] == 1)}; "
          f"no-schedule asks {sum(1 for r in ok if r['ask'] not in WANT)} on the pair (2 or 3 solves) "
          f"{sum(1 for r in ok if r['ask'] not in WANT and r['solves'] in (2, 3))}, "
          f"zero ask exactly 0.0 on {sum(1 for r in ok if r['ask'] == 'panel_zero' and r['steady_built'] == 0.0)} "
          f"of {sum(1 for r in ok if r['ask'] == 'panel_zero')}, "
          f"cap below -1 on {sum(1 for r in ok if r['ask'] == 'power_cap_75' and (r['steady_built'] is None or r['steady_built'] < -1.0))}")
    print("ERRORS", len(allrows) - len(ok), "horizon hours", sorted(set(r["hours"] for r in ok)))
    if OUT:
        Path(OUT).write_text(json.dumps(allrows))


main()

# Design: R10-ADVISOR-STEADY-START — the what-if's steady figure (#2257), revision after the fixer's 6 of 12

Base: origin/main ee64358be7eeccaec5178a923cb3b83a18a924a0; no predecessor (`after` is empty), so no handoff head. Built work: handoff-wip/r10-advisor-steady-start c966138ad5fa, estimator head 273079db5 on merge base 8f97247fc; every built line below is cited at 273079db5, where custom_components/heatpump_optimizer/whatif.py and the held-start flag exist (main has neither). `git diff --stat 8f97247fc ee64358be` prints nothing for optimizer.py, price_tiles.py, r10_advisor_residue.py and docs/dashboard-card.md, and changes for coordinator.py, const.py, payload.py, thermal_model.py, the card, tests/features.py and tests/structure_budgets.json: the continuation fixer rebases and re-cites. This note replaces section 2 of design.md at 3f883c9081d9 (the thermostat figure for a schedule ask) and A2 at e057b2ee2914; sections 1-6 of design.md at d2d663c32a87 stand wherever sections 2-4 below do not change them. Every figure below was run by this seat; the appendix is the probe, as run, which takes the file past designer.md's two pages.

## 1. Measured
Instruments: (i) the finder's harness, dev/audit/harnesses/r10_advisor_residue.py; (ii) the appendix probe (the carrier script of e057b2ee2914 with three additions: the panel's own asks, a periodic thermostat reference, a flat-price series), on the fixer's coordinator fixture (`_solve_coord`, tests/features.py: defaults, target 21, night 19.5, day 7 to 22, `min_temp` 19, outdoor -5 flat, a 12 h price sawtooth 0.60 to 1.06 anchored at the solve hour), hours 01..23 step 2, one frozen instant each, `async_simulate(ask, steady=True)`.

**Re-measured.** Main ee64358be, harness arm `whatif`: `rows 24 plan_moves_by_start 24 held_moves_by_start 0`, caps `plan 18/36 settled 1/36`. Built head 273079db5: `whatif` prints `steady_moves_by_start 0 degree figures against the held sign 0/36 cap figures reading a saving (< -1) 0/36 cap range -0.7..+46.0`; `steadysign` prints `rows 48 steady_wrong_sign 1 held_wrong_sign 0`. Probe arm `none`: `degree rows 24 steady_wrong 6 (minus_1@05, 07, 09, 11, 19, 21) held_wrong 0 settled_wrong 11 plan_wrong 2`; the cap ask +7.8 to +31.4, 0 of 12 below -1. The fixer's rows, to the row.

**What caused the 6** (one perturbation per run, the built estimator otherwise untouched). Comfort floor out of reach (`min_temp` 12 on both sides): **6 to 0**. Null: the settlement's room and slab caps lifted to 99 in the reported settlement: **6 to 6**, the same six rows. So the residue is the floor: with it in reach the cooler side meets it first, the two held plans stop being one plan a kelvin apart, and their money differs by which local optimum each lands in (A1 at e057b2ee2914 sized that at about 1 a day on a signal of 0.3 to 1; its seed arm, 6 to 4, was not re-run here). The estimator's own part: it differences the money of two independent solves.

**The asks the panel sends are not the tile's.** A tile ask moves every comfort level by 1 K, so the two schedules are translates. The panel (card `overrides()`, :13226-13240 at 273079db5) sends `target_temp` and `comfort_temp_day` together in 0.5 K steps and `day_start_hour` / `day_end_hour` in whole hours: the night level stays. Six panel asks (comfort +0.5 and -0.5; day start one hour earlier and later; day end one hour later and earlier) and the two tile asks, 12 hours each, 96 figures, counted against the ask's direction (more or warmer comfort hours cost):

| figure | tile asks, of 24 | panel asks, of 72 | by panel ask (+0.5, -0.5, start earlier, start later, end later, end earlier) |
|---|---|---|---|
| the plan's spend (the panel on main) | 2 | 25 | 3, 3, 5, 5, 3, 6 |
| the built steady pair (273079db5) | 6 | 18 | 7, 5, 1, 2, 1, 2 |
| the thermostat's cost from the held start (`monthly_held_cost_delta`; 3f883c9081d9's remedy) | 0 | 39 | 5, 6, 9, 8, 5, 6 |
| the thermostat's cost from a periodic start | 0 | 42 | 6, 6, 10, 8, 6, 6 |
| **the thermostat's energy from a periodic start, at the horizon's mean price** | **0** | **0** | 0, 0, 0, 0, 0, 0 |

Rows 1-3 are arm `none`, rows 4-5 arm `periodic1` (both with `PANEL=1`). The remedy of 3f883c9081d9 is wrong on more than half the panel's own asks: comfort +0.5 reads -80.7 to +108.2 by start hour.

**Why, with each control.**
- *The held start is a one-off again when only the day level moves.* `_compute_baseline_power` (optimizer.py:5612) starts from `_thermostat_held_state(..., targets[0])`: at 07:07 the warmer side is handed a day level it would still be heating towards, free. Control: the thermostat started where one pass over the horizon holding its own schedule leaves it (arm `periodic1`) reads one 12 h-periodic series with no start one-off (comfort +0.5: -12.7 to +38.3, from -80.7 to +108.2); a second spin-up pass (`periodic2`) changes no figure by more than 0.1, so one pass has converged.
- *What is left is price timing, and it is true of a thermostat.* A warmer day level buys a larger heat-up at day start and a longer coast after day end; on a sawtooth that swap outweighs a half kelvin of holding at 6 of 12 alignments. Control: the same arm on a flat price (`FLAT=1`, 0.85 every hour): the periodic thermostat's cost is wrong on **0 of 96** and equals the energy figure within 0.2 on every ask; the built pair is still wrong on 11 of 96 there (floor and basin, no timing). So **no figure that prices a schedule change's heat at its own hours holds the ask's sign at 12 of 12 on this fixture**, solver or not; for the plan the swap is not even real, since the optimiser already places its heat.
- *Energy does.* In periodic state a thermostat holding a pointwise warmer schedule loses more heat, whatever the prices: comfort +0.5 reads +0.613 to +0.618 kWh a day at all 12 hours, day start earlier +0.099 at all 12, a tile degree -1.585 at all 12. Priced at the horizon's mean price: comfort +15.5 to +15.6 and -14.9 to -14.8 a month; day window +2.4 to +2.5 and -2.6 to -2.5; tile degree +40.0 and -40.0 (held figure there: 35.9 to 42.0). Null that the periodic start carries it: the same energy difference from the held start (arm `none`) is wrong on 8 of 96 and reads -66.6 to +89.3 on comfort +0.5.

Not measured here: the new figure on harness (i)'s fixture (its asks are translates, where it is the held figure up to price timing); wall time of the two thermostat passes.

## 2. The shape
**Owning seam** unchanged: `async_simulate` (coordinator.py, `core` in tests/seam_map.json) owns the answer; price_tiles.py's `monthly_deltas` the arithmetic; optimizer.py the reference.

- **optimizer.py, added.** One method beside `_compute_baseline_power`: the periodic reference energy, kWh per day. It runs that thermostat loop twice over the first 24 h of the horizon (pass 1 from `_thermostat_held_state`, pass 2 from pass 1's end state) and returns pass 2's electrical energy; a horizon under 24 h returns nan. `_compute_baseline_power` gains the start state as an optional argument and is otherwise untouched: `baseline_cost`, the settlement and every published saving keep their held start (re-basing them is a different change with goldens of its own). `OptimizationResult` gains two floats, default nan: that energy and the mean of the solve's prices. Written on every solve: the live side of a what-if is the scheduled plan's result, which no flag reaches.
- **price_tiles.py `monthly_deltas`** (:96-120 at 273079db5; pure; signature unchanged). The steady key is:
  - **schedule ask** (both energies finite and their difference not 0): per_month of (what-if energy less live energy) x the live side's mean price, x horizon / 24, plus the what-if's spend outside its solve. Read off the measured pair `live` and `sim`; the steady pair is not consulted;
  - **no schedule change** (difference exactly 0: a cap, the fuse advisor): the built figure, the steady pair's spend plus `deferred_energy_cost`, to the cent; key absent without the pair (the failure rule stands);
  - **either energy nan**: key absent. No fallback to any cost figure.
- **coordinator.py `async_simulate(steady=True)`**: after the measured solve, the steady pair is solved only when the two energies are equal. A schedule ask costs 1 solve, what main costs today; a cap or fuse ask 3 then 2, the settled bound. Measured on the built head, three probes sharing four cores: 3 solves mean 2.39 s (max 3.58), 2 solves mean 0.93 s (max 2.52). The addition is two thermostat passes of at most 24 h of steps per solve and no solve; the fixer states their wall beside the per-solve wall for the Pi bound. `SIMULATE_MIN_INTERVAL_SECONDS`, the `limited=False` path, whatif.py's state and memo: untouched.
- **Callers.** Card and fuse advisor ask `steady=True` and read the steady key; the cap tile through `price_tiles.monthly_figure`; the degree tiles keep `monthly_held_cost_delta` (0 of 24 here; re-pricing them re-opens #2572 and #2834); `_solver_smoke` unchanged. `monthly_cost_delta`, `monthly_held_cost_delta`, `monthly_settled_cost_delta` keep their meaning. payload.py: no new key beyond the built steady key.
- **What the panel and docs say** (docs/dashboard-card.md, the what-if section and :619-622; card strings en, sv, de): "a steady-state monthly estimate. A comfort or day-window change is priced as the heating energy a thermostat holding the new schedule would use over a day against the current one, at the day's average price; any other change as the difference of two plans started as if each schedule had been held. Neither includes the one-off coast or heat-up, nor what the plan gains by timing its heat; where the lowest allowed temperature stops the plan following a cooler schedule, the saving is smaller." The last clause is measured: the steady plans deliver -0.61 to -0.81 K of a tile degree cooler and +0.77 to +1.04 K of one warmer. No draft, no key: no money and no caveat.

**Invariants.** The figure reads no measured start and no solve's money on a schedule ask (spread by start 0 by construction; by start hour at most 0.12 on any ask); a zero ask reads +0.0 (12 of 12, both branches); overrides reach only scratch copies; an error answer carries no figure.

**Against the built work** (everything not listed is KEEP per A3 at e057b2ee2914): optimizer.py as above (CHANGE, adds); price_tiles.py `monthly_deltas` and the module docstring's :20-30 (CHANGE); coordinator.py `async_simulate`, the pair made conditional (CHANGE); docs and strings as above (CHANGE); tests/features.py `_st_` block (CHANGE, section 4); tests/structure_budgets.json re-measured, pay or report before the push, never raise; BLOCKED.md DROP. A4a and A4b of e057b2ee2914 stand (the cap and fuse asks still read the pair).

## 3. Alternatives, lost; sibling sites
- *The pair's money for every ask (built):* 6 of 24 and 18 of 72; two independent solves' money.
- *The thermostat's cost, held start (3f883c9081d9):* 39 of 72. *Periodic start:* 42 of 72, and 0 of 96 only on a flat price.
- *Thermostat x delivered / shift (A2 at e057b2ee2914):* inherits the thermostat cost's sign, and delivered (the steady pair's mean room difference) is itself against the ask on 4 of 72 panel figures here (day-window asks, values within 0.015 K of 0), with two more solves per ask.
- *No money on a schedule ask; a disclosed rate:* the energy figure holds on 96 of 96, so neither is needed; a rate would have to be disclosed for the panel's commonest ask.
- *Re-basing `baseline_cost` on the periodic start:* moves every published saving and the settlement; not this group's finding. Carried.
- *The mean price computed in price_tiles.py from the horizon:* `monthly_deltas` receives results, not the horizon; a second argument at every caller against one float written where the prices already are.

Sibling sites (`git grep -n "monthly_steady_cost_delta\|STEADY_KEY\|baseline_cost - " 273079db5 -- custom_components dev/audit/harnesses tests/features.py`, the fixer re-runs it): steady-key readers price_tiles.py:153, coordinator.py:8977, card :13326, tests/features.py:31252, r10_advisor_residue.py:136 and :215, none changes; thermostat-cost differences price_tiles.py:117 (the tiles' held figure, stays: translates only) and the one this note replaces.

## 4. Evidence, by file
- **Failing first.** (a) tests/features.py, `_st_` block: over `_solve_coord` at hours 01..23 step 2, the two tile asks and the six panel asks through `async_simulate(ask, steady=True)`: 96 steady figures each strictly on the ask's side of 0, and each ask's 12 figures within 1.0 of one another; 12 cap figures none below -1. Red at 273079db5 (24 of 96; comfort +0.5 spreads 130). If the wall refuses 12 hours in the suite, every fourth hour there and all twelve in the harness. (b) the 07:07 sign check at :31370-31376 stays and turns green. (c) the appendix probe lands as dev/audit/harnesses/r10_advisor_steady_carrier.py, classified in tests/closure.py, its RESULT line counting the steady key against the ask over all eight asks. (d) `r10_advisor_residue.py whatif` and `steadysign`: green as section 1 (`steady_moves_by_start 0`, 0/36, 0/36; `steady_wrong_sign 0`). (e) tests/card.mjs as round 2.
- **Null controls.** `FLAT=1`: the thermostat cost and the energy figure agree within 0.2 on all 96; the zero ask reads 0.0; `monthly_held_cost_delta` and every cap figure identical to the cent at 273079db5 and at the head; `baseline_cost` of every solve identical to the cent (the reference's start did not move); a solve count of 1 on a schedule ask and 3 then 2 on a cap ask.
- **Mutants a reviewer runs.** (1) pass 2 dropped (energy from the held start): check (a) red, 8 of 96. (2) energy priced at its own hours (the thermostat's cost from the periodic start): red, 42 of 72 panel figures. (3) the schedule branch reading the pair: red, 24 of 96. (4) the sides exchanged: every row red. (5) the branch taken when the difference is 0: cap figures read 0.0, cap and fuse checks red. (6) a nan energy falling back to `monthly_held_cost_delta`: a check on a 12 h horizon (key absent) red. (7) the optional start argument leaking into the default call: the `baseline_cost` control red. (8) the pair solved on a schedule ask: the count check red.
- **Goldens.** Two result fields with a nan default; `GOLDEN_MODE=drift` first, a moved fixture claimed per claim-files.md, never re-recorded.

**Hot files, position.** As section 6 of design.md at d2d663c32a87, with optimizer.py now touched in `OptimizationResult` and beside `_compute_baseline_power`. After: none. Closes #2257; `fixes` lists 2257. Size L.

## Notes for the fixer
Carry: R10-ADVISOR-STEADY-START (item brief-departure) - decision: owner. The brief's "both plans are solved from a start held at each one's own schedule" is kept for a cap and the fuse advisor and left for a schedule ask, on section 1's table; the panel's comfort figure is then a thermostat's energy at the mean price, not the plan's money.
Carry: R10-ADVISOR-STEADY-START (item mixed-ask) - decision: orchestrator. The panel sends hot water, quiet windows and wood slots with every comfort ask (card :13226-13240 at 273079db5); under section 2 an ask that moves the schedule is priced by its heating energy alone, so a hot-water change sent with it adds nothing. Accepted, disclosed or priced.
Carry: R10-ADVISOR-STEADY-START (item pair-other-asks) - a hot-water, weight or floor ask alone reads the pair, whose money section 1 measures as not sign-safe on a degree; no row here measures those asks. Measure them in the carrier harness before the docs call that branch an estimate.
Carry: R10-ADVISOR-STEADY-START (item weekday-day) - one day's periodic state assumes tomorrow's schedule is today's; across a weekday-to-weekend change it is not. State it in the docs sentence or spin up on the horizon's own two days where it has them.
Carry: R10-ADVISOR-STEADY-START (item pv-price) - the mean price ignores PV surplus, which `energy_cost_of` prices piecewise; on a PV house say which mean the figure uses, with a check.
Carry: R10-ADVISOR-STEADY-START (item pass-wall) - time the two thermostat passes per solve on the fixture and add them to the Pi bound.
Carry: R10-ADVISOR-STEADY-START (item probe-side-effect) - the probe's periodic arm patches the reference's start for every solve, so its settlement moves too (built pair 5 of 24 there against 6): the built method must not, which mutant 7's control pins.
Carry: R10-ADVISOR-STEADY-START (item result-overlap) - `OptimizationResult` also gains fields in design/R10-CLONE-2238 and design/R10-WHY-NOW-WIDGET; rebase on whichever merges first.
Carry: R10-ADVISOR-STEADY-START (item worker-patch) - a perturbation patched in the test process never reaches a solve the process worker runs; the probe answers the worker seam in place.
Carry: dismissed: measured in section 1, 39 of 72 (item thermostat-held-figure)
Carry: dismissed: measured in section 1, 4 of 72 (item part2-delivered)
Carry: dismissed: superseded by section 2, schedule asks solve no pair (item part2-skip-pair)
Standing, unchanged: recite-a4, floor-zero, docstring-half (3f883c9081d9); round 2's verdict carries (0fdadfe92458) and that note's own (d2d663c32a87).
Received: carry 0 of this group (from R10-ADVISOR-WHATIF, #2963).

Seat tokens: not reported by the harness for the seat; its one locator subagent reported 39860.

---
# Appendix: the probe, as run at 273079db5 (to land as dev/audit/harnesses/r10_advisor_steady_carrier.py)

`[PANEL=1] [FLAT=1] PYTHONPATH=tests/hastub:tests:custom_components python3 probe.py <arm> [out.json]` from the tree root; arms used here: none, caps_report, floor, periodic1, periodic2. The energy figure of section 1 is (`sim.ref_kwh` - `live.ref_kwh`) x `live.mean_price` x 730 / 24 over the out.json rows; the built steady key is the row's `steady`, the thermostat's cost its `held`.

```python
"""Scratch probe: the steady figure's sign on the coordinator fixture, with one perturbation.

Run from the worktree root:
  PYTHONPATH=tests/hastub:tests:custom_components python3 probe.py <pert> [out.json]
pert: none | caps_report | caps_all | caps_common | floor | basin | floor_basin | refill_mean | refill_max | amend1 | amend2
"""
from __future__ import annotations

import ast
import os
import asyncio as _asyncio
import json
import sys
import time
from datetime import timedelta
from pathlib import Path

import numpy as np
from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass, FakeState, with_config
from homeassistant.util import dt as dt_util

import heatpump_optimizer.coordinator as cmod
import heatpump_optimizer.optimizer as omod
from heatpump_optimizer import price_tiles, whatif
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord

PERT = sys.argv[1] if len(sys.argv) > 1 else "none"
OUT = sys.argv[2] if len(sys.argv) > 2 else None

# The fixture, sliced out of tests/features.py by name: no check runs.
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
    return fn(*args)  # in-process, so a perturbation patched here reaches the solve


cmod._await_process = _no_worker
_flag = {"settling": False}
_real_caps = Opt._settlement_caps
_real_settle = Opt._settle_horizon
_real_def = Opt._deferred_energy_cost
LIVE_TARGET = 21.0


def _settle(self, h, weather, reference_targets, baseline_end, optimized_end, *a, **k):
    self._probe_end = optimized_end
    a = (h, weather, reference_targets, baseline_end, optimized_end, *a)
    _flag["settling"] = True
    try:
        return _real_settle(self, *a, **k)
    finally:
        _flag["settling"] = False


def _caps(self, *a, **k):
    if PERT == "caps_common" and _flag["settling"]:
        # both sides settled at the live schedule's caps
        keep = self.config.target_temp
        self.config.target_temp = LIVE_TARGET
        try:
            return _real_caps(self, *a, **k)
        finally:
            self.config.target_temp = keep
    caps = _real_caps(self, *a, **k)
    if PERT == "caps_all" or (PERT == "caps_report" and _flag["settling"]):
        caps = {**caps, "room": 99.0, "slab": 99.0}
    return caps


def _deferred(self, baseline_end, optimized_end, prices, *a, **k):
    if PERT.startswith("refill_") and _flag["settling"]:
        f = {"refill_mean": np.mean, "refill_max": np.max, "refill_min": np.min}[PERT]
        prices = np.full_like(np.asarray(prices, dtype=float), float(f(prices)))
    return _real_def(self, baseline_end, optimized_end, prices, *a, **k)


_real_optimize = Opt.optimize
SOLVES = {"n": 0}
REF = {}


def _optimize(self, *a, inputs=None, **k):
    from dataclasses import replace as _rep
    SOLVES["n"] += 1
    result = _real_optimize(self, *a, inputs=inputs, **k)
    REF[round(float(result.baseline_cost), 9)] = (getattr(self, '_probe_kwh', None), float(np.mean(inputs.forecast.prices)) if inputs is not None else None)
    if PERT.startswith("amend") and inputs is not None and inputs.held_start:
        for _ in range(int(PERT[5:6])):
            SOLVES["n"] += 1
            result = _real_optimize(self, *a, inputs=_rep(inputs, held_start=False, state=_rep(self._probe_end)), **k)
    return result


Opt.optimize = _optimize

# periodic: the thermostat reference starts where a day of holding its own schedule leaves it.
_real_cbp = Opt._compute_baseline_power
_real_held = omod._thermostat_held_state
_spun = {"state": None}


def _held(model, state, weather, target):
    if _spun["state"] is not None:
        return _spun["state"]
    return _real_held(model, state, weather, target)


def _cbp(self, weather, initial_state, dt, comfort_targets=None):
    if not PERT.startswith("periodic"):
        out = _real_cbp(self, weather, initial_state, dt, comfort_targets)
        self._probe_kwh = float(np.sum(out[0])) * dt
        return out
    end = None
    for _ in range(int(PERT[8:] or 1)):
        _power, end = _real_cbp(self, weather, initial_state, dt, comfort_targets)
        _spun["state"] = end
    try:
        out = _real_cbp(self, weather, initial_state, dt, comfort_targets)
        self._probe_kwh = float(np.sum(out[0])) * dt
        return out
    finally:
        _spun["state"] = None


omod._thermostat_held_state = _held
Opt._compute_baseline_power = _cbp
Opt._settle_horizon, Opt._settlement_caps, Opt._deferred_energy_cost = _settle, _caps, _deferred

# Basin: the what-if's held solve gets the live held plan as an extra candidate
# and the live one the what-if's (second pass), through the optimizer's own
# previous-plan seam.
_seed = {"plan": None}
_real_ws = Coord._whatif_solve


def _whatif_solve(self, overrides, config, params, state, horizon, solve_at, held_start):
    opt, inputs, extra = _real_ws(self, overrides, config, params, state, horizon, solve_at, held_start)
    if "basin" in PERT and held_start and _seed["plan"] is not None:
        opt._prev_shipped_plan = np.asarray(_seed["plan"], dtype=float)
    return opt, inputs, extra


Coord._whatif_solve = _whatif_solve

_cap = {}
_real_md = price_tiles.monthly_deltas


def _md(live, sim, extra, horizon_hours, steady=None):
    _cap["last"] = (live, sim, steady)
    return _real_md(live, sim, extra, horizon_hours, steady)


price_tiles.monthly_deltas = _md


def _res(r):
    if r is None:
        return None
    room = r.room_temp_trajectory
    return {
        "ref_kwh": REF.get(round(float(r.baseline_cost), 9), (None, None))[0], "mean_price": REF.get(round(float(r.baseline_cost), 9), (None, None))[1],
        "spend": r.predicted_cost, "deferred": r.deferred_energy_cost, "baseline": r.baseline_cost,
        "obj": r.objective_value, "kwh": float(np.sum(r.power_schedule)) * 24.0 / len(r.power_schedule),
        "room0": room[0], "roomN": room[-1], "room_min": min(room), "room_mean": float(np.mean(room)),
        "slab0": r.slab_temp_trajectory[0], "slabN": r.slab_temp_trajectory[-1],
        "power": [round(float(x), 4) for x in r.power_schedule],
        "room": [round(float(x), 3) for x in room],
    }


async def _one(hour, extra):
    coord = _solve_coord()  # noqa: F821
    if os.environ.get('FLAT'):
        coord._prices = [{**p, 'total': 0.85} for p in coord._prices]
    if extra:
        with_config(coord, extra)
        getattr(coord, "_ctx", coord)._opt_config.min_temp = extra["min_temperature"]
    coord._fuse_advisor_at = dt_util.now()
    await coord.async_run_optimization()
    record = _solve_record_now(coord)  # noqa: F821
    asks = price_tiles.specs(record.config, record.params.max_electrical_power)
    if os.environ.get("PANEL"):
        c = record.config
        day = c.comfort_temp_day if getattr(c, "comfort_temp_day", None) is not None else c.target_temp
        print("PANELCFG target", c.target_temp, "day", getattr(c, "comfort_temp_day", None), "night", getattr(c, "comfort_temp_night", None),
              "ds", c.day_start_hour, "de", c.day_end_hour)
        asks = list(asks) + [
            ("panel_comfort_plus_half", {"target_temp": c.target_temp + 0.5, "comfort_temp_day": day + 0.5}),
            ("panel_comfort_minus_half", {"target_temp": c.target_temp - 0.5, "comfort_temp_day": day - 0.5}),
            ("panel_daystart_earlier", {"day_start_hour": c.day_start_hour - 1}),
            ("panel_daystart_later", {"day_start_hour": c.day_start_hour + 1}),
            ("panel_dayend_later", {"day_end_hour": c.day_end_hour + 1}),
            ("panel_dayend_earlier", {"day_end_hour": c.day_end_hour - 1}),
            ("panel_zero", {"target_temp": c.target_temp}),
        ]
    print("CONFIG", hour, "min_temp", record.config.min_temp, "target", record.config.target_temp, "horizon", record.config.horizon_hours)
    rows = []
    for name, overrides in asks:
        passes = 2 if "basin" in PERT else 1
        best = None
        for p in range(passes):
            whatif.state(coord).last_at = None
            if "basin" in PERT:
                whatif.state(coord).live_steady = None
                # pass 0 unseeded; pass 1: both sides seeded with the other side's pass-0 plan
                _seed["plan"] = None
            if "basin" in PERT and p == 1:
                # seed live with the what-if plan, then the what-if with the live plan
                live_plan, sim_plan = best["live_s"]["power"], best["sim_s"]["power"]
                order = iter([sim_plan, live_plan])
                real = _real_ws

                def seeded(self, o, c, pa, s, h, at, hs, _order=order):
                    opt, inputs, ex = real(self, o, c, pa, s, h, at, hs)
                    if hs:
                        opt._prev_shipped_plan = np.asarray(next(_order), dtype=float)
                    return opt, inputs, ex

                Coord._whatif_solve = seeded
            t0 = time.monotonic(); n0 = SOLVES["n"]
            answer = await coord.async_simulate(dict(overrides), steady=True)
            wall = time.monotonic() - t0
            if answer.get("monthly_held_cost_delta") is None:
                print("ANSWER", {k: v for k, v in answer.items() if not isinstance(v, (list, dict))})
                raise SystemExit(2)
            Coord._whatif_solve = _whatif_solve
            live, sim, steady = _cap["last"]
            row = {
                "hour": hour, "ask": name, "pass": p, "wall_s": round(wall, 3), "solves": SOLVES["n"] - n0,
                "steady": answer.get(whatif.STEADY_KEY), "held": answer.get("monthly_held_cost_delta"),
                "settled": answer.get("monthly_settled_cost_delta"), "plan": answer.get("monthly_cost_delta"),
                "live": _res(live), "sim": _res(sim),
                "live_s": _res(steady[0]) if steady else None, "sim_s": _res(steady[1]) if steady else None,
            }
            best = best or row
            rows.append(row)
    return rows


def main():
    extra = {"min_temperature": 12.0} if "floor" in PERT else None
    allrows = []
    for hour in range(1, 24, 2):
        dt_util.freeze(dt_util.now().replace(hour=hour, minute=7, second=0, microsecond=0))
        try:
            allrows += _asyncio.run(_one(hour, extra))
        finally:
            dt_util.freeze(None)
    last = max(r["pass"] for r in allrows)
    for p in range(last + 1):
        rows = [r for r in allrows if r["pass"] == p]
        deg = [r for r in rows if r["ask"].startswith("target_")]
        cap = [r for r in rows if not r["ask"].startswith("target_")]
        want = {"target_minus_1": -1.0, "target_plus_1": 1.0}
        wrong = [r for r in deg if r["steady"] is None or r["steady"] * want[r["ask"]] <= 0.0]
        held_wrong = [r for r in deg if r["held"] * want[r["ask"]] <= 0.0]
        settled_wrong = [r for r in deg if r["settled"] * want[r["ask"]] <= 0.0]
        plan_wrong = [r for r in deg if r["plan"] * want[r["ask"]] <= 0.0]
        for r in deg + cap:
            print(f"ROW {PERT} pass {p} {r['hour']:02d} {r['ask']:15s} steady {r['steady']!s:>8} held {r['held']:+8.1f} "
                  f"settled {r['settled']:+8.1f} plan {r['plan']:+8.1f} wall {r['wall_s']} solves {r['solves']}")
        print(f"RESULT {PERT} pass {p} degree rows {len(deg)} steady_wrong {len(wrong)} "
              f"({', '.join(f'{r['ask'][7:]}@{r['hour']:02d}' for r in wrong)}) held_wrong {len(held_wrong)} "
              f"settled_wrong {len(settled_wrong)} plan_wrong {len(plan_wrong)} | cap rows {len(cap)} "
              f"steady saving(<-1) {sum(1 for r in cap if r['steady'] is not None and r['steady'] < -1.0)} "
              f"settled saving {sum(1 for r in cap if r['settled'] < -1.0)} plan saving {sum(1 for r in cap if r['plan'] < -1.0)}")
    if OUT:
        Path(OUT).write_text(json.dumps(allrows))


main()
```

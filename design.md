# Design: R10-ADVISOR-STEADY-START — the what-if's steady figure (#2257), re-cut after `revise 4c87fa385f2b harness`

Base: origin/main ee64358be7eeccaec5178a923cb3b83a18a924a0; no predecessor (`after` is empty), so no handoff head. Built work: handoff-wip/r10-advisor-steady-start, estimator head 273079db5 on merge base 8f97247fc; built lines are cited at 273079db5, where custom_components/heatpump_optimizer/whatif.py exists (main has none). This note answers the one revise point of design-verdict 6cd70cf27b and restates the harness of both harness verdicts (6cd70cf27b on 4c87fa385f2b, 05e5b517b1 on e057b2ee2914). It replaces section 2's schedule branch and section 4 of design.md at 4c87fa385f2b; section 1 (the measurement), section 3 and the docs wording of that note stand, and so does everything design.md at d2d663c32a87 settled: the cap tile and the fuse advisor read the steady pair, to the cent; the held reference, the wood side, the whatif.py seam, the failure rule, the docs and string sites. Every figure below was run by this seat at 273079db5 with the appendix probe; the appendix takes the file past designer.md's two pages.

## 1. Measured: the revise point, and one thing it uncovers
Instrument: the appendix probe, `AGE=<steps> STEP=<kelvin> PYTHONPATH=tests/hastub:tests:custom_components python3 probe_age.py out.json` from the tree root. Fixture: `_solve_coord` (tests/features.py: target 21, night 19.5, day 7 to 22, outdoor -5, a 12 h price sawtooth), hours 01..23 step 2. The plan is solved at hh:07; the clock then moves AGE quarter-hours and the what-if is asked there. STEP adds that many kelvin to the outdoor forecast of the calendar day after the solve, so the 24 h horizon always holds both days. Asks per hour: the two tile degrees and the six panel asks of 4c87fa385f2b's section 1 (96 schedule figures), and three asks that move no schedule: the zero ask, the cap tile's `power_cap_75`, the panel's hot water alone (`dhw_min_temperature` + 2) (36). Four reference energies per ask, all the two-pass thermostat energy over the horizon, differenced and priced at the mean price:

| live side read from | weather of the two passes | schedule figures against the ask, of 96: AGE 0 / 1 / 2 at STEP 4 | AGE 2, STEP 0 | no-schedule asks with energy difference exactly 0, of 36: AGE 0 / 1 / 2 at STEP 4 | AGE 2, STEP 0 |
|---|---|---|---|---|---|
| the scheduled plan (4c87fa385f2b) | the horizon's own | 3 / 8 / 18 | 0 | 36 / 0 / 0 | 15 |
| the scheduled plan | the horizon's mean | 0 / 24 / 24 | 0 | 36 / 0 / 0 | 15 |
| the what-if's instant (fix i alone) | the horizon's own | 3 / 3 / 3 | 0 | 36 / 36 / 36 | 36 |
| **the what-if's instant** | **the horizon's mean** | **0 / 0 / 0** | **0** | **36 / 36 / 36** | **36** |

- **The reviewer's point holds as stated.** Row 1: with the plan one step old the zero ask reads -6.0 to -1.3 a month and two steps old -11.8 to -2.6; the cap and the hot-water ask read the same numbers, taking the schedule branch on 36 of 36; day start one hour earlier is against the ask on 7 of 12 and 12 of 12. Null that the term is the forecast's: STEP 0 at AGE 2 is wrong on 0 of 96, yet the energies are still unequal on 21 of 36 (differences up to 0.00004 kWh), so exact equality across two instants fails with no weather at all.
- **Fix (i) alone is not enough, which no earlier note measured.** Row 3: both sides at the what-if's instant on the same arrays, 3 of 96 still against the ask at every age (day start earlier -11.4, later +10.7). A day-window ask moves heat across the window's edge, the second pass starts from an end state bought in tomorrow's weather, and the difference carries the two days' COP. Null: STEP 0, 0 of 96. 4c87fa385f2b's "0 of 96" was measured on a flat outdoor series only.
- **The two passes on the horizon's mean weather.** Row 4: each weather array replaced by its mean over the first 24 h before both passes, both sides. 0 of 96 at AGE 0, 1 and 2; day start earlier +2.20 to +2.49 at all 36 (hour, age) points, comfort +0.5 +15.36 to +15.76, a tile degree +35.0 to +39.8 (the spread is the mean weather's own, by how much of each day the window holds). No-schedule asks: targets equal and difference exactly 0.0 on 108 of 108.
- **The pair branch at age.** Solves at the built head, which always solves the pair: zero ask 3, cap 2, hot water 2, at every age. Cap figure +7.9 to +30.0 over AGE 0, 1, 2 at STEP 4, none below -1; zero ask +0.0 on 36 of 36; hot water alone +0.0 on 36 of 36 on this fixture.

Not measured: a diurnal outdoor series; the wall of the passes; whether `_solve_coord` has a hot-water tank (the hot-water ask's +0.0 may be a house without one: item pair-other-asks).

## 2. The shape (replaces 4c87fa385f2b section 2, first three bullets)
**Owning seam** unchanged: `async_simulate` (coordinator.py, `core` in tests/seam_map.json) owns the answer, price_tiles.py the arithmetic, optimizer.py the reference.

- **optimizer.py, added, no result field.** One method beside `_compute_baseline_power`: from one solve's inputs, with no solve, it returns the reference's per-step targets over the first 24 h and the reference day energy in kWh: the thermostat loop twice (pass 1 from `_thermostat_held_state`, pass 2 from pass 1's end state) on the horizon's weather with every array replaced by its mean over those 24 h; nan under 24 h. It builds weather and targets by the code `optimize` uses, never a second derivation. `_compute_baseline_power` gains the start state as an optional argument and is otherwise untouched; `OptimizationResult` gains nothing, so `baseline_cost`, the settlement, both result-assembly paths and every golden are out of the diff.
- **coordinator.py `async_simulate(steady=True)`.** After the measured solve it calls that method on two scratch optimizers built by `_whatif_solve` from the same `config`, `params`, `state`, `horizon` and `solve_at`: one with the overrides, one with none. Nothing for this key is read off `_optimization_result` or `base`'s result. **Branch, by what the ask changes:** the two target lists compared element by element. Unequal: schedule ask, the pair is not solved (1 solve). Equal: the steady pair as built (3 then 2). The energies are never compared to choose.
- **price_tiles.py.** One pure function for the schedule figure: `per_month` of (what-if energy less live energy) x the mean of the what-if's price array x horizon / 24, plus the what-if's spend outside its solve; nan in, no key out. `monthly_deltas` keeps its built signature and its steady key for the pair; `async_simulate` puts exactly one of the two under `whatif.STEADY_KEY`.
- **Energy tie (the verdict's carry, decided).** A schedule ask whose energies tie (the thermostat held at the pump's maximum both ways) reads the spend outside the solve, 0.0 with no wood: true of that thermostat. An ask whose level has no hours in the first 24 h changes no target and reads the pair.
- Callers, payload, docs and strings: as 4c87fa385f2b, the docs sentence reading "at the day's average weather and average price".

**Invariants.** Both sides of either branch are computed at one instant on one set of arrays; the scheduled plan's age, a failed solve and a fixed mode reach no figure; a zero ask reads 0.0 by identical inputs, not by cancellation; no solve is added.

**Alternatives, lost.** Live energy off the scheduled result: rows 1-2. The horizon's own weather: row 3. Energies compared to choose the branch: correct once the instant is shared (36 of 36) but sends an energy tie to the pair, whose money 4c87fa385f2b measures wrong on 18 of 72 panel asks. Two result fields written per scheduled solve: the wall on every solve and three open designs' field overlap, for a value this shape never reads.

## 3. Every harness finding of both verdicts, and what now measures it
Commands run from the tree root; C is the carrier harness, the appendix probe landed as dev/audit/harnesses/r10_advisor_steady_carrier.py (classified in tests/closure.py), its RESULT lines counted on the steady key of the answer once the shape is built.

| finding | measurement (command, fixture) | must move | must not move (null) | perturbation / mutant |
|---|---|---|---|---|
| 6cd70cf27b (i): two windows | C at `AGE=1 STEP=4` and `AGE=2 STEP=4`, `_solve_coord`, 12 hours | schedule figures against the ask: 0 of 96 | the same at `AGE=0`: 0 of 96 | mutant M1, live energy read off the scheduled result: 24 of 96 at AGE 1 and at AGE 2, 0 at AGE 0 |
| 6cd70cf27b (ii): branch by float equality | C, the 36 no-schedule asks at AGE 0, 1, 2, STEP 4 and AGE 2, STEP 0 | targets equal and pair solved on 36 of 36; solve count 3 (first) then 2 | schedule asks: solve count 1 on 96 of 96 | M1: 0 of 36 at AGE 1, 2; M2, branch on energy inequality with M1: zero ask reads -6.1 to -2.4 at AGE 1 |
| 6cd70cf27b (iii): start and age rows, two-day outdoor | check (a) below; C over AGE 0, 1, 2 x STEP 0, 4 | zero ask 0.0 on 12 of 12 per cell; hot water alone and cap on the pair; each panel ask on its side of 0 | cap figure, none below -1 (here +7.9 to +30.0) | M3, the passes on the horizon's own weather: 3 of 96 at STEP 4, 0 of 96 at STEP 0 (STEP 0 is M3's null: a flat fixture cannot see it) |
| 6cd70cf27b (iv): the mutant | M1 | red on (a) at AGE 1, 2 | green at AGE 0 | - |
| 05e5b517b1 point 1: the panel's own asks | C, the six panel asks x 12 hours x AGE 0, 1, 2 | 0 of 72 per age against the ask (built pair at AGE 0, STEP 0: 18 of 72) | the two tile asks: 0 of 24 | M4, energy priced at its own hours: 42 of 72 (4c87fa385f2b section 1) |
| 05e5b517b1 point 1: the zero ask null, the bound | C, `panel_zero` | 0.0 exactly, 12 of 12 per cell, with equal targets | - | the 0.05 K bound and its ratio are gone; no threshold is left to size |
| 05e5b517b1 point 2: a small schedule ask on the rejected estimator | (a2) below | any unequal target takes the energy branch: solve count 1 | an ask moving no target: pair | M5, the branch taken on a target difference over 0.05 only: (a2) red |

- **Failing first, tests/features.py `_st_` block.** (a) Over `_solve_coord` with the next day's outdoor forecast at -1, hours 01..23 step 2, the what-if asked 0, 1 and 2 steps after `async_run_optimization`: the eight schedule asks each strictly on the ask's side of 0 with solve count 1; the zero ask exactly 0.0, the cap ask not below -1 and the hot-water ask, each on the pair with count 3 then 2. Red at 273079db5 (key from the pair on every ask: count 3 on schedule asks; 24 of 96 at AGE 0, STEP 0). If the suite's wall refuses 36 cells, hours 07 and 19 at each age there (07 is where row 3 fails) and all cells in C. (a2) one ask of `comfort_temp_day` + 0.01: count 1, figure above 0. (a3) energy tie: `max_electrical_power` set below the held demand, comfort +0.5: key present and 0.0, count 1. (b), (d), (e) as 4c87fa385f2b section 4.
- **Null controls.** `monthly_held_cost_delta`, every cap and fuse figure and every solve's `baseline_cost` identical to the cent at 273079db5 and at the head; `GOLDEN_MODE=drift` prints no moved fixture (no result field is added).
- **Mutants.** M1-M5 above; M6 the sides exchanged (every row red); M7 a nan energy falling back to any cost figure (12 h horizon check red); M8 the optional start argument leaking into the default call (`baseline_cost` control red); M9 the pair solved on a schedule ask (count check red).

**Open question for the orchestrator (a harness this seat cannot name).** Finding (iii) asks each panel ask on its side of 0 on an outdoor series that differs between the days. That is met only by the mean-weather passes, which make the figure blind to within-day weather by construction; a check that the figure is also *right in size* on a real diurnal forecast has no reference to compare against (the plan's and the thermostat's own-hour costs are both measured unsafe in sign). The note asserts sign and start-invariance, not magnitude.

**Hot files, position.** optimizer.py (beside `_compute_baseline_power` only), coordinator.py `async_simulate`, price_tiles.py, tests/features.py, tests/closure.py. After: none. Closes #2257. Size L.

## Notes for the fixer
Carry: R10-ADVISOR-STEADY-START (item brief-departure) - decision: owner, as 4c87fa385f2b routes it and the verdict repeats: the schedule branch is not started before it is answered. The figure is now a thermostat's day energy at the day's mean weather and mean price.
Carry: R10-ADVISOR-STEADY-START (item mixed-ask) - decision: orchestrator, unchanged: a comfort ask sent with a hot-water or quiet-window change prices its heating energy alone.
Carry: R10-ADVISOR-STEADY-START (item horizon-builder) - the new method must obtain weather and per-step targets through the code path `optimize` uses (optimizer.py:3814 and :4138 at 273079db5), on both the space-only and the hot-water path; a check on a house without hot water.
Carry: R10-ADVISOR-STEADY-START (item pass-wall) - time the four thermostat loops per what-if on the fixture; state whether they run on the loop or with the solve, with the Pi bound.
Carry: R10-ADVISOR-STEADY-START (item pair-other-asks) - the hot-water ask reads +0.0 on `_solve_coord`; confirm the fixture has a tank or measure on one that has, before the docs call that branch an estimate.
Carry: R10-ADVISOR-STEADY-START (item measured-fields) - both sides now start from one `state`, so a measured wood side or buffer cancels in a no-schedule ask; state the bound for a schedule ask on a throttling-valve two-tank fixture.
Carry: R10-ADVISOR-STEADY-START (item diurnal) - run C once on a diurnal outdoor series (not run here) and report the count.
Carry: R10-ADVISOR-STEADY-START (item residue-fixture) - run `whatif` and `steadysign` of dev/audit/harnesses/r10_advisor_residue.py on the new figure before the body quotes their lines.
Carry: R10-ADVISOR-STEADY-START (item docstring-cap) - price_tiles.py:20-30 rewritten with the docs paragraph.
Carry: R10-ADVISOR-STEADY-START (item baseline-overlap) - design/R10-COMBI-TANK-PR-B also works in `_compute_baseline_power`; rebase on whichever merges first.
Carry: dismissed: no result field is added (item result-overlap)
Carry: dismissed: no result field is added (item both-paths)
Carry: dismissed: decided in section 2 with check a3 (item energy-tie)
Standing, unchanged: weekday-day, pv-price, probe-side-effect, worker-patch (4c87fa385f2b), and the standing ones that note lists.
Received: carry 0 of this group (from R10-ADVISOR-WHATIF, #2963).

Seat tokens: not reported by the harness for the seat; its one extractor subagent reported 46768.

---
# Appendix: the probe, as run at 273079db5 (to land as dev/audit/harnesses/r10_advisor_steady_carrier.py)

Keys in its output: `off` and `at` are the live side read off the scheduled plan and at the what-if's instant on the horizon's own weather; `offm` and `atm` the same on the mean weather. Section 1's rows are off, offm, at, atm. Schedule asks were asked with `steady=False` to save the pair's solves; the built steady figure is therefore printed for the no-schedule asks only.

```python
"""Probe: the steady figure's two energies, the plan AGE steps older than the what-if.

Run from the worktree root (built head 273079db5):
  AGE=<steps> [STEP=<kelvin>] PYTHONPATH=tests/hastub:tests:custom_components python3 probe_age.py out.json
AGE: quarter-hour steps between the scheduled solve and the what-if (0, 1, 2).
STEP: the outdoor forecast of the calendar day after the solve is -5 + STEP (0 = the fixture's flat -5).
Per ask it records the periodic thermostat energy (two passes) of the what-if solve, of the scheduled
plan (the shape of design 4c87fa38: "off") and of the zero ask at the what-if's instant ("at").
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


def _cbp(self, weather, initial_state, dt, comfort_targets=None):
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
        whatif.state(coord).last_at = None
        n0 = SOLVES["n"]
        answer = await coord.async_simulate(dict(overrides), steady=name not in WANT)
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
    print("ERRORS", len(allrows) - len(ok), "horizon hours", sorted(set(r["hours"] for r in ok)))
    if OUT:
        Path(OUT).write_text(json.dumps(allrows))


main()
```

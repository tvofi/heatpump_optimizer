#!/usr/bin/env python
"""D2 harness -- objective and settlement identities on every committed golden fixture.

Metric: for each of the 49 plan fixtures in tests/golden/*.json, the absolute error of
  predicted_cost   vs HeatPumpOptimizer._energy_cost_fn(prices, dt)(space + dhw)
                     (piecewise in the fixture's own pv_surplus, pv_export_price = 0),
  dhw_heating_cost vs predicted_cost - energy(space),
  predicted_savings vs baseline_cost - predicted_cost - deferred_energy_cost,
  savings_percentage vs optimizer._savings_percentage(savings, baseline),
  pv_self_consumed_kwh vs sum(min(total, surplus))*dt,
  peak_cost / projected_peak_kw / compressor_starts vs HeatPumpOptimizer._grid_report,
plus the physical bounds every trajectory must respect (buffer <= buffer_max_temp,
DHW <= dhw_hard_max_temp, wood <= 95, space + dhw <= max_electrical_power and caps).
On the 11 space-only fixtures, baseline_cost and deferred_energy_cost are re-derived by
re-running _compute_baseline_power / _replay_end_state / _deferred_energy_cost.
Command: PYTHONPATH=tests/hastub python tools/audit/round2/D2/fixture_identities.py
Expected (c398fc84): every *_max_err <= 2e-4 (6-dp fixture rounding), bound violations = 0;
  deferred_identity_max_err ~1 SEK on the committed may-drift fixtures (plans recorded on
  another BLAS) but deferred_identity_fresh_capture_max_err <= 1e-3 on fresh captures.
Perturbation: config price_weight 2.0 on a re-derived cell moves the objective but none
  of these identities (they are price_weight-free); editing _energy_cost_fn to drop
  "* dt" moves cost_identity_max_err up by ~3x the cost.
Instrumented: optimizer:HeatPumpOptimizer._energy_cost_fn, _grid_report, _savings_percentage,
  _pv_self_consumed, _compute_baseline_power, _replay_end_state, _deferred_energy_cost.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import resource
import sys
import time
from pathlib import Path
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
_T_PROC0 = time.process_time()
_T_THR0 = time.thread_time()

import golden
from heatpump_optimizer import mixing_valve
from heatpump_optimizer import optimizer as optmod

START = golden.START
errs = {"cost": 0.0, "dhw_cost": 0.0, "savings": 0.0, "pct": 0.0, "pv": 0.0, "peak_cost": 0.0,
        "peak_kw": 0.0, "starts": 0, "baseline": 0.0, "deferred": 0.0}
bounds_viol = {"buffer": 0, "dhw": 0, "wood": 0, "power": 0, "pct": 0}
n_fix = 0
n_space_only = 0
n_fresh = 0
fresh_err = 0.0
worst_cell = {}
for name, spec in golden.SCENARIOS.items():
    path = Path("tests/golden") / f"{name}.json"
    if not path.exists():
        print(f"CELL {name}: no fixture")
        continue
    fx = json.loads(path.read_text())
    built = golden.make(**spec)
    opt = built["optimizer"]
    p = opt.model.params
    dt = opt.config.dt_hours
    prices = np.asarray(fx["prices"], dtype=float)
    n = prices.size
    space = np.asarray(fx["power_schedule"], dtype=float)
    dhw = np.asarray(fx["dhw_power_schedule"], dtype=float) if fx["dhw_power_schedule"] else np.zeros(n)
    total = space + dhw
    surplus = np.asarray(fx["pv_surplus"], dtype=float) if fx["pv_surplus"] else np.zeros(n)
    opt._pv_surplus = surplus
    cost_fn = opt._energy_cost_fn(prices, dt)
    e_cost = abs(cost_fn(total) - fx["predicted_cost"])
    e_dhw = abs((fx["predicted_cost"] - cost_fn(space)) - fx["dhw_heating_cost"]) if fx["dhw_power_schedule"] else 0.0
    e_sav = abs((fx["baseline_cost"] - fx["predicted_cost"] - fx["deferred_energy_cost"]) - fx["predicted_savings"])
    e_pct = abs(optmod._savings_percentage(fx["predicted_savings"], fx["baseline_cost"]) - fx["savings_percentage"])
    e_pv = abs(opt._pv_self_consumed(total, dt) - fx["pv_self_consumed_kwh"])
    grid = opt._grid_report(total, opt.config.baseline_load_array(n), dt, START)
    e_pk = abs(grid["peak_cost"] - fx["peak_cost"])
    e_pkw = abs(grid["peak_kw"] - fx["projected_peak_kw"])
    e_st = abs(grid["starts"] - fx["compressor_starts"])
    for k, v in (("cost", e_cost), ("dhw_cost", e_dhw), ("savings", e_sav), ("pct", e_pct), ("pv", e_pv),
                 ("peak_cost", e_pk), ("peak_kw", e_pkw), ("starts", e_st)):
        if v > errs[k]:
            errs[k] = v
            worst_cell[k] = name
    # physical bounds
    if fx["buffer_temp_trajectory"] and mixing_valve.is_throttling(p.mixing_valve_mode):
        if max(fx["buffer_temp_trajectory"][1:]) > p.buffer_max_temp + 1e-6:
            bounds_viol["buffer"] += 1
    if fx["dhw_temp_trajectory"] and max(fx["dhw_temp_trajectory"][1:]) > p.dhw_hard_max_temp + 1e-6:
        bounds_viol["dhw"] += 1
    if fx["wood_temp_trajectory"] and max(fx["wood_temp_trajectory"]) > 95.0 + 1e-6:
        bounds_viol["wood"] += 1
    cap = np.full(n, p.max_electrical_power)
    if name in golden.CAP_SCENARIOS:
        cap = np.full(n, p.max_electrical_power * 0.6)
    if name in golden.ENVELOPE_CAP_SCENARIOS:
        cap = np.clip(p.max_electrical_power * np.linspace(1.0, 0.6, n), 0.6 * p.max_electrical_power, p.max_electrical_power)
    if np.any(total > cap + 1e-6) or np.any(total < -1e-9):
        bounds_viol["power"] += 1
    if fx["savings_percentage"] > 100.0 + 1e-6:
        bounds_viol["pct"] += 1
    n_fix += 1
    # Re-derive the settlement on the space-only fixtures.
    if not fx["dhw_power_schedule"]:
        h = golden.make(**spec)
        o2 = h["optimizer"]
        st = h["state"]
        out = np.asarray(fx["outdoor_temps"], dtype=float)
        wi, ra, so = h["wind"][:n], h["rain"][:n], h["solar"][:n]
        if name in golden.SNOW_SCENARIOS:
            ra = ra * np.where(np.arange(n) < n // 2, 0.0, 1.0)
        ext = golden.external_heat_for(n) if name in golden.EXTERNAL_HEAT_SCENARIOS else None
        hours = np.array([((START.hour + i * dt) % 24.0) for i in range(n)])
        targets = np.array([o2.config.get_comfort_temp(hh) for hh in hours])
        o2._pv_surplus = surplus
        o2._initial_buffer_temp = float(st.buffer_tank_temperature) if p.buffer_is_store else None
        cost2 = o2._energy_cost_fn(prices, dt)
        bp, bend = o2._compute_baseline_power(st, out, wi, ra, so, dt, targets, external_heat_kw=ext)
        vt = np.asarray(fx["valve_target_schedule"], dtype=float) if fx["valve_target_schedule"] else None
        oend = o2._replay_end_state(st, space, out, wi, ra, so, dt, external_heat_kw=ext, valve_targets=vt)
        deferred = o2._deferred_energy_cost(bend, oend, prices, out, caps=o2._settlement_caps(out))
        e_b = abs(cost2(bp) - fx["baseline_cost"])
        e_d = abs(deferred - fx["deferred_energy_cost"])
        if e_b > errs["baseline"]:
            errs["baseline"] = e_b; worst_cell["baseline"] = name
        if e_d > errs["deferred"]:
            errs["deferred"] = e_d; worst_cell["deferred"] = name
        n_space_only += 1
        if e_b > 1e-4 or e_d > 1e-4:
            print(f"CELL {name}: baseline err {e_b:.3e} deferred err {e_d:.3e} (fixture plan vs this box: "
                  f"may-drift set or a discontinuous branch; re-deriving from a FRESH capture below)")
            fresh = golden.capture(name, spec)
            h3 = golden.make(**spec)
            o3 = h3["optimizer"]
            st3 = h3["state"]
            sp3 = np.asarray(fresh["power_schedule"], dtype=float)
            vt3 = np.asarray(fresh["valve_target_schedule"], dtype=float) if fresh["valve_target_schedule"] else None
            pr3 = np.asarray(fresh["prices"], dtype=float)
            out3 = np.asarray(fresh["outdoor_temps"], dtype=float)
            o3._pv_surplus = surplus
            o3._initial_buffer_temp = float(st3.buffer_tank_temperature) if p.buffer_is_store else None
            bp3, bend3 = o3._compute_baseline_power(st3, out3, wi, ra, so, dt, targets, external_heat_kw=ext)
            oend3 = o3._replay_end_state(st3, sp3, out3, wi, ra, so, dt, external_heat_kw=ext, valve_targets=vt3)
            d3 = o3._deferred_energy_cost(bend3, oend3, pr3, out3, caps=o3._settlement_caps(out3))
            e_d3 = abs(d3 - fresh["deferred_energy_cost"])
            e_b3 = abs(o3._energy_cost_fn(pr3, dt)(bp3) - fresh["baseline_cost"])
            print(f"CELL {name} fresh capture: baseline err {e_b3:.3e} deferred err {e_d3:.3e} "
                  f"(schedule L1 fixture-vs-fresh {float(np.sum(np.abs(sp3 - space)) * dt):.2f} kWh)")
            fresh_err = max(fresh_err, e_d3, e_b3)
            n_fresh += 1

print(f"RESULT fixtures_checked={n_fix} count")
print(f"RESULT fixtures_space_only_rederived={n_space_only} count")
for k, v in errs.items():
    print(f"RESULT {k}_identity_max_err={v:.3e} SEK_or_kW_or_pct (worst: {worst_cell.get(k, '-')})")
print(f"RESULT deferred_identity_fresh_capture_cells={n_fresh} count")
print(f"RESULT deferred_identity_fresh_capture_max_err={fresh_err:.3e} SEK")
for k, v in bounds_viol.items():
    print(f"RESULT bound_violations_{k}={v} count")

proc = time.process_time() - _T_PROC0
thr = time.thread_time() - _T_THR0
print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")

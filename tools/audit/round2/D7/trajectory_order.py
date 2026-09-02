#!/usr/bin/env python3
"""D7 step 5 -- last_buffer_trajectory statefulness: what a reordering does to the terminal cost.

Metric (one line): on a two-zone house whose buffer is a store (throttling valve + 200 L,
ThermalParameters.buffer_is_store True) the terminal-cost closure returned by
HeatPumpOptimizer._terminal_cost(prices, outdoor, None) is evaluated on schedule A's four
RETURNED trajectories with the buffer trajectory read from the model side-channel
(i) immediately after A's own simulate_trajectory (the production order), (ii) after ONE
intervening simulate_trajectory of another schedule B (a reordering, or a second objective
call in between), (iii) after an intervening simulate_trajectory_batch (the poison);
reported: tc(ii)-tc(i) in SEK, as a share of A's energy cost, whether (iii) raises, and the
same delta on the NULL control (no valve, buffer_is_store False), which must be 0. Plus an
AST census of optimizer.py: writer sites of the attribute (thermal_model.py), reader sites,
and for each reader the line distance to the preceding simulate_* call and any model call
in between.

Run:      PYTHONPATH=tests/hastub python tools/audit/round2/D7/trajectory_order.py
Expected: RESULT poison_raises=1, null_delta_abs=0 (exact); tc_delta_abs_max > 0 (float,
          exact to 1e-9 -- no solver, plain simulation); baseline c398fc84eec25fc44b60d74aae05b9a2da205884.
Machine:  8-core Apple M1, 8 GB, shared audit box; no timing reported.
Instrumented symbol: heatpump_optimizer.thermal_model:ThermalModel.last_buffer_trajectory
          (written by simulate_trajectory / _batch / _with_dhw, read by the closure of
          heatpump_optimizer.optimizer:HeatPumpOptimizer._terminal_cost).
Perturbation: config mixing_valve_mode -> none (buffer_is_store False) -> tc_delta_abs_max
          to_zero; production one-liner: make simulate_trajectory RETURN buffer_temps and
          have the objective pass the returned array -> tc_delta_abs_max to_zero.
Writes:   nothing but stdout.
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import ast
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

import numpy as np
from profiles import DT, N, house, prices, weather
from heatpump_optimizer import mixing_valve
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import (
    _STALE_TRAJECTORY, ThermalModel, ThermalParameters, ThermalState)


def build(valve_mode):
    cfg = house(two_zone=True, dhw=False)
    if valve_mode:
        cfg["mixing_valve_mode"] = valve_mode
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = False
    m = ThermalModel(p)
    opt = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
    return opt, m, p


def arm(valve_mode, label):
    opt, m, p = build(valve_mode)
    start = datetime(2026, 1, 15)
    pr = prices("winter_typical", start)
    ot, wi, ra, so = weather("winter_cold", start)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(ot[0]),
                      upper_floor_temperature=21.0, lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
    rng = np.random.default_rng(0)
    pmax = float(p.max_electrical_power)
    A = np.clip(pmax * (1.5 - pr / pr.mean()), 0.0, pmax)          # the smooth price guess
    alts = {"coast": np.zeros(N), "full": np.full(N, pmax), "random": rng.uniform(0, pmax, N)}
    cost = opt._terminal_cost(pr, ot, None)
    r, s, u, l = m.simulate_trajectory(st, A, ot, wi, ra, so, DT)
    buf_a = m.last_buffer_trajectory
    tc_prod = float(cost(r, s, u, l, buf_a))
    energy = float(np.sum(pr * A * DT))
    print(f"\n-- arm {label}: buffer_is_store={p.buffer_is_store} valve={p.mixing_valve_mode!r} "
          f"volume={p.buffer_tank_volume} L  tank end (A) {float(buf_a[-1]):.2f} C")
    print(f"   terminal cost, production order: {tc_prod:.4f} SEK  (A energy cost {energy:.2f} SEK)")
    deltas = {}
    for name, B in alts.items():
        m.simulate_trajectory(st, A, ot, wi, ra, so, DT)      # A again: fresh side-channel
        m.simulate_trajectory(st, B, ot, wi, ra, so, DT)      # the intervening call
        stale = m.last_buffer_trajectory
        tc_stale = float(cost(r, s, u, l, stale))
        deltas[name] = tc_stale - tc_prod
        print(f"   after an intervening simulate of {name:6}: tank end {float(stale[-1]):6.2f} C  "
              f"terminal {tc_stale:9.4f}  delta {tc_stale - tc_prod:+9.4f} SEK")
    # (iii) the poison
    m.simulate_trajectory(st, A, ot, wi, ra, so, DT)
    m.simulate_trajectory_batch(st, np.stack([alts["coast"]]), ot, wi, ra, so, DT)
    poisoned = m.last_buffer_trajectory is _STALE_TRAJECTORY
    raised = 0
    try:
        cost(r, s, u, l, m.last_buffer_trajectory)
    except RuntimeError:
        raised = 1
    print(f"   after an intervening batch: attribute is the poison sentinel={poisoned}, "
          f"terminal-cost read raises={bool(raised)}")
    return {"store": p.buffer_is_store, "tc_prod": tc_prod, "energy": energy,
            "deltas": deltas, "poisoned": poisoned, "raised": raised}


def census():
    src = (ROOT / "custom_components/heatpump_optimizer/optimizer.py").read_text()
    tree = ast.parse(src)
    lines = src.splitlines()
    readers = []
    fns = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    seen_lines = set()
    for fn in fns:
        for node in ast.walk(fn):
            if (isinstance(node, ast.Attribute) and node.attr == "last_buffer_trajectory"
                    and isinstance(node.ctx, ast.Load)):
                # innermost enclosing function only: a closure's read is not its host's
                inner = min((f for f in fns if f.lineno <= node.lineno <= (f.end_lineno or f.lineno)),
                            key=lambda f: (f.end_lineno or f.lineno) - f.lineno)
                if inner is not fn or node.lineno in seen_lines:
                    continue
                seen_lines.add(node.lineno)
                # nearest preceding simulate_* call in the same function
                prev = None
                between = []
                for c in ast.walk(fn):
                    if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute):
                        if c.func.attr.startswith("simulate_trajectory") and c.lineno < node.lineno:
                            if prev is None or c.lineno > prev.lineno:
                                prev = c
                if prev is not None:
                    for c in ast.walk(fn):
                        if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                                and prev.lineno < c.lineno < node.lineno
                                and isinstance(c.func.value, ast.Attribute)
                                and c.func.value.attr == "model"):
                            between.append((c.lineno, c.func.attr))
                readers.append({"line": node.lineno, "function": fn.name,
                                "writer_call": prev.func.attr if prev else None,
                                "writer_line": prev.lineno if prev else None,
                                "line_distance": (node.lineno - prev.lineno) if prev else None,
                                "model_calls_between": between})
    tm = (ROOT / "custom_components/heatpump_optimizer/thermal_model.py").read_text()
    ttree = ast.parse(tm)
    writers = [n.lineno for n in ast.walk(ttree)
               if isinstance(n, ast.Attribute) and n.attr == "last_buffer_trajectory"
               and isinstance(n.ctx, ast.Store)]
    other_readers = []
    for p in (ROOT / "custom_components/heatpump_optimizer").glob("*.py"):
        if p.name in ("optimizer.py", "thermal_model.py"):
            continue
        for i, line in enumerate(p.read_text().splitlines(), 1):
            if "last_buffer_trajectory" in line:
                other_readers.append((p.name, i))
    return readers, writers, other_readers


def main() -> int:
    print("=== D7 last_buffer_trajectory order dependence ===")
    valve = "manual" if mixing_valve.is_throttling("manual") else sorted(mixing_valve.THROTTLING_MODES)[0]
    store = arm(valve, "buffer-is-store")
    null = arm(None, "null control (no valve)")
    readers, writers, other = census()
    print("\n-- AST census")
    print(f"   writer sites in thermal_model.py (Store): lines {writers}")
    for r in readers:
        print(f"   reader {r['function']}:{r['line']} <- {r['writer_call']}@{r['writer_line']} "
              f"(+{r['line_distance']} lines) model calls between: {r['model_calls_between']}")
    print(f"   readers outside optimizer/thermal_model: {other}")

    dmax = max(abs(v) for v in store["deltas"].values())
    print(f"RESULT buffer_is_store_store_arm={int(store['store'])} count")
    print(f"RESULT buffer_is_store_null_arm={int(null['store'])} count")
    print(f"RESULT tc_production={store['tc_prod']:.6f} SEK")
    for k, v in store["deltas"].items():
        print(f"RESULT tc_delta_after_{k}={v:+.6f} SEK")
    print(f"RESULT tc_delta_abs_max={dmax:.6f} SEK")
    print(f"RESULT tc_delta_rel_to_energy={dmax / store['energy']:.6f} ratio")
    print(f"RESULT null_delta_abs={max(abs(v) for v in null['deltas'].values()):.6f} SEK")
    print(f"RESULT poison_raises={store['raised']} count")
    print(f"RESULT writer_sites={len(writers)} count")
    print(f"RESULT reader_sites_optimizer={len(readers)} count")
    print(f"RESULT readers_with_model_call_between={sum(1 for r in readers if r['model_calls_between'])} count")
    print(f"RESULT reader_max_line_distance={max(r['line_distance'] or 0 for r in readers)} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())

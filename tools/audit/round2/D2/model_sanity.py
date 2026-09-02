#!/usr/bin/env python
"""D2 harness -- thermal-model sanity: dt order, monotonicity, cap semantics, wood share,
objective term scaling.

Metrics (each one line):
  dt_error_ratio: |T(dt=1h) - T_ref| / |T(4x15min) - T_ref| after 6 h against a
    dt=1/64 h reference (first-order Euler predicts ~4);
  monotonic_violations: over 5 states x 25 power levels x 3 topologies, the count of
    stores whose next-step temperature DEcreases when electrical power increases;
  cap_rate_semantics: a buffer read 5 K above buffer_max_temp cools at its physical rate
    (next temp > cap, refused == 0) rather than being snapped to the cap;
  wood_share_max_jump: the largest jump in wood_share (and w*drawn) across a 1e-6 K
    change of wood_temp at the flow curve, with hp_temp inside the switch margin;
  wood_share_vec_parity: max |_wood_share_vec - wood_share| over a grid (bitwise = 0);
  price_weight_scaling_resid: |J(pw) - pw*(energy+cycling+capacity+terminal_1) - comfort|
    from the production closures (_energy_cost_fn, _grid_terms, _terminal_cost,
    _comfort_terms) at pw in {0.5, 1, 2};
  survival/settlement bounds.
Command: PYTHONPATH=tests/hastub python tools/audit/round2/D2/model_sanity.py
         PYTHONPATH=tests/hastub python tools/audit/round2/D2/model_sanity.py --perturb
Expected (c398fc84): dt_error_ratio in [3, 5]; monotonic_violations = 0;
  cap_rate_semantics = 1; wood_share_max_jump = 0.5 (a documented-continuous law that
  is not); wood_share_vec_parity = 0; price_weight_scaling_resid <= 1e-9.
Perturbation: WOOD_TANK_MIN_MARGIN -> 0 makes wood_share_max_jump -> 1.0 (up); making
  region 3 use (wood_temp - flow_set) instead of (wood_temp - hp_temp) makes it -> 0.
Instrumented: thermal_model:ThermalModel.simulate_step, wood_share, _wood_share_vec,
  optimizer:HeatPumpOptimizer._terminal_cost/_grid_terms/_energy_cost_fn/_comfort_terms,
  optimizer:stored_heat_survival, slab_settlement_cap.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import resource
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
_T_PROC0 = time.process_time()
_T_THR0 = time.thread_time()

import argparse
import golden
from profiles import house
from heatpump_optimizer import mixing_valve
from heatpump_optimizer import optimizer as optmod
from heatpump_optimizer import thermal_model as tm
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, wood_share, _wood_share_vec

START = golden.START
ap = argparse.ArgumentParser()
ap.add_argument("--perturb", action="store_true")
args = ap.parse_args()
if args.perturb:
    # The one-line production edit (thermal_model.py:1115): region 3 reaches 1.0 as the
    # wood tank reaches the curve, so it meets region 1 continuously.
    def wood_share(wood_temp, hp_temp, flow_set, floor_temp, margin=tm.WOOD_TANK_MIN_MARGIN):
        if wood_temp >= flow_set:
            return 1.0
        if hp_temp > flow_set:
            f_w = (hp_temp - flow_set) / (hp_temp - wood_temp)
            useful = max(0.0, wood_temp - floor_temp)
            span = max(flow_set - floor_temp, 1e-6)
            return min(1.0, max(0.0, f_w * useful / span))
        return min(1.0, max(0.0, max(wood_temp - hp_temp, wood_temp - flow_set + margin) / max(margin, 1e-6)))


def params_for(two_zone, valve=None, wood=False, **over):
    cfg = house(two_zone=two_zone, dhw=False)
    if valve:
        cfg.update({"mixing_valve_mode": valve, "buffer_tank_volume": 750.0})
    if wood:
        cfg.update({"wood_tank_top_entity": "sensor.wood_top", "wood_tank_volume": 500.0})
    cfg.update(over)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = False
    return p


def state(wood=None, **over):
    s = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=-5.0,
                     upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                     buffer_tank_temperature=45.0, wood_tank_temperature=wood)
    for k, v in over.items():
        setattr(s, k, v)
    return s


def vec(s):
    return np.array([s.room_temperature, s.slab_temperature, s.upper_floor_temperature,
                     s.lower_floor_temperature, s.buffer_tank_temperature,
                     s.wood_tank_temperature if s.wood_tank_temperature is not None else 0.0])


# ---- dt order ----
def run(model, s, dt, hours, P=3.0):
    for _ in range(int(round(hours / dt))):
        s = model.simulate_step(s, P, -5.0, 2.0, 0.0, 0.0, dt)
    return vec(s)


for label, p in (("two_zone_valve", params_for(True, "manual")), ("single", params_for(False))):
    m = ThermalModel(p)
    ref = run(m, state(), 1.0 / 64.0, 6.0)
    e1 = np.max(np.abs(run(m, state(), 1.0, 6.0) - ref))
    e4 = np.max(np.abs(run(m, state(), 0.25, 6.0) - ref))
    print(f"CELL dt {label}: err(1h)={e1:.4e} err(15min)={e4:.4e} ratio={e1 / max(e4, 1e-15):.2f}")
    print(f"RESULT dt_error_ratio_{label}={e1 / max(e4, 1e-15):.3f} ratio")
    print(f"RESULT dt_error_1h_{label}={e1:.4e} degC")

# ---- monotonicity in electrical power ----
viol = 0
cells = 0
rng = np.random.default_rng(9)
topos = (("single", params_for(False), None), ("two_zone_valve", params_for(True, "manual"), None),
         ("two_tank", params_for(True, "manual", wood=True), 55.0))
for label, p, wood in topos:
    m = ThermalModel(p)
    for _ in range(5):
        s = state(wood=wood, room_temperature=float(rng.uniform(17, 24)), slab_temperature=float(rng.uniform(18, 30)),
                  upper_floor_temperature=float(rng.uniform(17, 24)), lower_floor_temperature=float(rng.uniform(17, 24)),
                  buffer_tank_temperature=float(rng.uniform(30, 69)))
        out = float(rng.uniform(-15, 10))
        prev = None
        for P in np.linspace(0.0, 6.0, 25):
            v = vec(m.simulate_step(s, float(P), out, 2.0, 0.0, 0.0, 0.25))
            if prev is not None:
                viol += int(np.sum(v < prev - 1e-12))
                cells += v.size
            prev = v
print(f"RESULT monotonic_cells={cells} count")
print(f"RESULT monotonic_violations={viol} count")

# ---- the buffer cap clamps a rate, not a state; the DHW rating likewise ----
p = params_for(True, "manual")
m = ThermalModel(p)
s = state(buffer_tank_temperature=p.buffer_max_temp + 5.0)
n1 = m.simulate_step(s, 0.0, -5.0, 0.0, 0.0, 0.0, 0.25)
ok = (n1.buffer_tank_temperature > p.buffer_max_temp) and (m._step_buffer_refused == 0.0)
print(f"CELL cap: start={s.buffer_tank_temperature} next={n1.buffer_tank_temperature:.3f} cap={p.buffer_max_temp} refused={m._step_buffer_refused}")
print(f"RESULT cap_rate_semantics={int(ok)} bool")
n2 = m.simulate_step(state(buffer_tank_temperature=p.buffer_max_temp - 0.1), 6.0, -5.0, 0.0, 0.0, 0.0, 0.25)
print(f"RESULT cap_charging_clamped_at={n2.buffer_tank_temperature:.6f} degC (cap {p.buffer_max_temp}) refused={m._step_buffer_refused:.3f} kW")
pd = params_for(False)
pd.dhw_enabled = True
md = ThermalModel(pd)
t_hot = pd.dhw_hard_max_temp + 5.0
t_next = md.simulate_dhw_step(t_hot, 0.0, 12.0, dt_hours=0.25, draw_power=0.0)
print(f"RESULT dhw_rating_rate_semantics={int(t_next > pd.dhw_hard_max_temp and md._step_dhw_refused == 0.0)} bool")
# closed-form coast vs simulation (no draw)
hold = md.dhw_coast_hours(55.0, 45.0)
T = 55.0
h = 0.0
while T > 45.0 and h < 200:
    T = md.simulate_dhw_step(T, 0.0, 12.0, dt_hours=1.0 / 60.0, draw_power=0.0)
    h += 1.0 / 60.0
print(f"RESULT dhw_coast_closed_form_vs_sim_h={abs(hold - h):.3f} h (closed {hold:.2f}, sim {h:.2f})")

# ---- wood_share continuity and vector parity ----
flow_set, floor = 45.0, 21.0
max_jump = 0.0
worst = None
jumps = []
for hp in np.linspace(flow_set - tm.WOOD_TANK_MIN_MARGIN, flow_set, 21):
    a = wood_share(flow_set - 1e-6, hp, flow_set, floor)
    b = wood_share(flow_set, hp, flow_set, floor)
    jumps.append(abs(b - a))
    if abs(b - a) >= max_jump:
        max_jump = abs(b - a); worst = (hp, a, b)
print(f"CELL wood_share worst jump: hp_temp={worst[0]:.3f} w(flow-1e-6)={worst[1]:.3f} w(flow)={worst[2]:.3f}")
print(f"RESULT wood_share_max_jump={max_jump:.4f} ratio")
print(f"RESULT wood_share_jump_cells={len(jumps)} count")
print(f"RESULT wood_share_jump_min={min(jumps):.4f} ratio")
print(f"RESULT wood_share_jump_drop_most_favourable={sorted(jumps)[-2]:.4f} ratio")
# the drawn heat is continuous there, so w*drawn jumps by the same fraction of the draw
ua = 0.4 * 6.0 * 3.5 / 15.0
t_mix_a = min(max(flow_set - 1e-6, worst[0]), flow_set)
drawn = mixing_valve.emitter_delivery(mix_temp=t_mix_a, zone_temp=21.0, ua=ua)
print(f"RESULT wood_share_times_drawn_jump={max_jump * drawn:.4f} kW (drawn {drawn:.3f} kW)")
grid_w = np.linspace(20.0, 70.0, 101)
grid_h = np.linspace(20.0, 70.0, 101)
W, H = np.meshgrid(grid_w, grid_h)
vecv = _wood_share_vec(W.ravel(), H.ravel(), flow_set, np.full(W.size, floor))
scal = np.array([tm.wood_share(float(w), float(h), flow_set, floor) for w, h in zip(W.ravel(), H.ravel())])
print(f"RESULT wood_share_vec_parity={float(np.max(np.abs(vecv - scal))):.3e} ratio")
print(f"RESULT wood_share_range_ok={int(np.all((vecv >= 0) & (vecv <= 1)))} bool")

# ---- objective terms scale with price_weight ----
built = golden.make(**golden.SCENARIOS["everything_on"])
opt = built["optimizer"]
n = 96
dt = opt.config.dt_hours
prices, out = built["prices"], built["outdoor"]
hours = np.array([((START.hour + i * dt) % 24.0) for i in range(n)])
targets = np.array([opt.config.get_comfort_temp(h) for h in hours])
b = [opt.config.get_temp_bounds(h) for h in hours]
tmin = np.array([lo for lo, _ in b]); tmax = np.array([hi for _, hi in b])
band = np.maximum(targets - tmin, 1.0)
solar_gains = np.array([opt.model.compute_solar_gain(v) for v in built["solar"]])
opt._pv_surplus = np.zeros(n)
P = np.random.default_rng(1).uniform(0, 6, size=n)
r, s, u, l = opt.model.simulate_trajectory(built["state"], P, out, built["wind"], built["rain"], built["solar"], dt)
buf = opt.model.last_buffer_trajectory
def terms(pw):
    opt.config.price_weight = pw
    e = opt._energy_cost_fn(prices, dt)(P) * pw
    pen, cc = opt._comfort_terms(r, u, l, targets, tmin, tmax, band)
    cyc, cap, _ = opt._grid_terms(n, dt, START)
    g = (cyc(P) + cap(P)) * pw
    t = opt._terminal_cost(prices, out, solar_gains)(r, s, u, l, buf)
    return e, pen + cc, g, t
e1, c1, g1, t1 = terms(1.0)
resid = 0.0
for pw in (0.5, 2.0):
    e, c, g, t = terms(pw)
    J = e + c + g + t
    resid = max(resid, abs(J - (pw * (e1 + g1 + t1) + c1)))
opt.config.price_weight = 1.0
print(f"CELL terms@pw=1: energy={e1:.3f} comfort={c1:.3f} grid={g1:.3f} terminal={t1:.3f}")
print(f"RESULT price_weight_scaling_resid={resid:.3e} objective")

# ---- survival and settlement bounds ----
vals = [optmod.stored_heat_survival(ua, cap, dem) for ua in (0.0, 0.01, 0.1, 1.0) for cap in (20.0, 45.0, 70.0) for dem in (0.0, 0.1, 1.0, 5.0)]
print(f"RESULT survival_in_unit_interval={int(all(0.0 <= v <= 1.0 for v in vals))} bool")
p2 = params_for(True, "manual")
caps = [optmod.slab_settlement_cap(p2, 21.0, t) for t in np.arange(-25.0, 25.1, 5.0)]
print(f"RESULT slab_cap_le_buffer_max={int(all(c <= p2.buffer_max_temp for c in caps))} bool")

proc = time.process_time() - _T_PROC0
thr = time.thread_time() - _T_THR0
print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")

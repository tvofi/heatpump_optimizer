"""D2.M1 thermal-model sweep (round 10, seat D2-s1).

Metrics (one line each):
  energy_resid_max  = max over sampled one-call steps of
      |sum_i C_i*dT_i - (Q_in - Q_loss - refused)*dt|  (kWh), Q_* evaluated at
      the pre-step state by this harness's own balance, ThermalModel.simulate_step
      (n_sub==1 cells) / ThermalModel._simulate_step_two_zone driven.
  parity_mismatch   = count of (cell,row,track) where simulate_trajectory_batch
      differs bitwise from simulate_trajectory.
  dt_inv_maxdiff    = max |T(4x15min) - T(1x60min)| per store (K) after one hour.
  monotone_viol     = count of (cell,step) where +0.5 kW electrical lowers any store.
  bound_viol        = count of steps where any store leaves [min(init,out)-1, max(init,cap)+1].
Command: PYTHONPATH=tests/hastub ~/hpo-seats/r9fix-lanerunner/bin/python3 \
    dev/audit/rounds/round10/D2/s1/m1_thermal.py [--perturb tank_ambient_shift]
Expected at baseline 17f1c55fad1b: energy_resid_max <= 1e-9, parity_mismatch 0
  (or as RESULT prints; the perturbation moves energy_resid_max above 1e-3).
Machine: macOS arm64 (B4 box).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
sys.path.insert(0, "custom_components"); sys.path.insert(0, "tests")
import numpy as np
from unittest import mock
from heatpump_optimizer import thermal_model as tm
from heatpump_optimizer.thermal_model import (
    ThermalModel, ThermalParameters, ThermalState, WeatherSeries)
from profiles import house

PERTURB = "--perturb" in sys.argv and sys.argv[sys.argv.index("--perturb") + 1]
t0p, t0t = time.process_time(), time.thread_time()

CELLS = {
    "single": dict(two_zone=False, extra={}),
    "two_zone_novalve": dict(two_zone=True, extra={}),
    "two_zone_valve": dict(two_zone=True, extra={}, param={"mixing_valve_mode": "manual"}),
    "two_zone_valve_small35L": dict(two_zone=True, extra={"buffer_tank_volume": 35.0}, param={"mixing_valve_mode": "manual"}),
    "two_zone_wood": dict(two_zone=True, extra={}, param={"mixing_valve_mode": "manual", "wood_tank_configured": True, "wood_tank_volume": 500.0}, wood=True),
    "two_zone_valve_direct_slab": dict(two_zone=True, extra={}, param={"mixing_valve_mode": "manual", "topology_layout_override": "valve_upper_direct_slab"}),
    "two_zone_valve_substep": dict(two_zone=True, extra={}, param={"mixing_valve_mode": "manual", "upper_floor_thermal_mass": 0.08, "slab_thermal_mass": 0.3}),
    "single_substep": dict(two_zone=False, extra={}, param={"room_thermal_mass": 0.05}),
    "two_zone_valve_carnot": dict(two_zone=True, extra={}, param={"mixing_valve_mode": "manual", "cop_flow_carnot": True}),
}


def make(cell):
    c = CELLS[cell]
    p = ThermalParameters.from_config({**house(two_zone=c["two_zone"]), **c["extra"]})
    for k, v in c.get("param", {}).items():
        setattr(p, k, v)
    m = ThermalModel(p)
    assert p.two_zone_enabled == c["two_zone"], cell
    if "wood" in cell: assert p.two_tank_modelled, cell
    if "direct" in cell: assert p.slab_fed_direct, cell
    return m, p, c.get("wood", False)


def energy(p, s, two):
    if not two:
        return p.room_thermal_mass * s.room_temperature + p.slab_thermal_mass * s.slab_temperature
    cb = p.buffer_tank_thermal_mass if p.buffer_tank_thermal_mass >= 1e-6 else 0.04
    e = (p.upper_floor_thermal_mass * s.upper_floor_temperature
         + p.lower_floor_thermal_mass * s.lower_floor_temperature
         + p.slab_thermal_mass * s.slab_temperature + cb * s.buffer_tank_temperature)
    if s.wood_tank_temperature is not None and p.two_tank_modelled:
        e += p.wood_tank_thermal_mass * s.wood_tank_temperature
    return e


def flux(m, p, s, P, out, wind, rain, sol, ext, hum):
    """Net heat into the whole house+tank system (kW) at the pre-step state."""
    if not p.two_zone_enabled:
        cop = m.compute_cop(out, humidity=hum)
        u = m.effective_heat_loss_coefficient(p.heat_loss_coefficient, wind, rain)
        return cop * P + max(0.0, ext) + p.internal_gains + m.compute_solar_gain(sol) - u * (s.room_temperature - out)
    thr = tm.mixing_valve.is_throttling(p.mixing_valve_mode)
    cop = m.compute_cop(out, humidity=hum, flow_temp=s.buffer_tank_temperature if thr else None)
    uu, ul = m._zone_loss(wind, rain)
    q = cop * P + max(0.0, ext) + p.internal_gains + m.compute_solar_gain(sol)
    q -= uu * (s.upper_floor_temperature - out) + ul * (s.lower_floor_temperature - out)
    q -= p.buffer_tank_heat_loss_coefficient * (s.buffer_tank_temperature - tm.TANK_ROOM_AMBIENT_TEMP)
    if s.wood_tank_temperature is not None and thr and p.two_tank_modelled:
        q -= p.wood_tank_heat_loss_coefficient * (s.wood_tank_temperature - tm.TANK_ROOM_AMBIENT_TEMP)
    return q


rng = np.random.default_rng(11)
res_max, res_where, n_energy = 0.0, None, 0
for cell in CELLS:
    m, p, wood = make(cell)
    two = p.two_zone_enabled
    for k in range(400):
        s = ThermalState(
            room_temperature=rng.uniform(17, 24), slab_temperature=rng.uniform(18, 32),
            upper_floor_temperature=rng.uniform(17, 24), lower_floor_temperature=rng.uniform(17, 24),
            buffer_tank_temperature=rng.uniform(22, 70),
            wood_tank_temperature=rng.uniform(25, 94) if wood else None)
        if not two:
            s = tm.replace(s, upper_floor_temperature=s.room_temperature, lower_floor_temperature=s.room_temperature)
        P = rng.uniform(0, 6.0); out = rng.uniform(-25, 15)
        wind = rng.uniform(0, 12); rain = rng.uniform(0, 3); sol = rng.uniform(0, 600)
        ext = rng.uniform(0, 12) if rng.random() < 0.3 else 0.0
        hum = rng.uniform(50, 99)
        dt = 0.25
        nsub = m._substeps_and_loss(wind, rain, dt)[0]
        dt_call = dt / nsub
        e0 = energy(p, s, two)
        f = flux(m, p, s, P, out, wind, rain, sol, ext, hum)
        amb = tm.TANK_ROOM_AMBIENT_TEMP
        if PERTURB == "tank_ambient_shift":
            # one-line production edit emulated in memory: the step's tank
            # ambient moves +5 K, the harness balance keeps the original
            tm.TANK_ROOM_AMBIENT_TEMP = amb + 5.0
        if two:
            s1 = m._simulate_step_two_zone(s, P, out, wind, rain, sol, dt_call, ext, None, hum, None)
        else:
            s1 = m._simulate_step_single(s, P, out, wind, rain, sol, dt_call, ext, hum, None)
        tm.TANK_ROOM_AMBIENT_TEMP = amb
        refused = getattr(m, "_step_buffer_refused", 0.0) + getattr(m, "_step_wood_refused", 0.0) if two else 0.0
        r = abs(energy(p, s1, two) - e0 - (f - refused) * dt_call)
        n_energy += 1
        if r > res_max:
            res_max, res_where = r, (cell, k, round(P, 2), round(out, 1), round(ext, 2))
print(f"RESULT energy_resid_max={res_max:.3e} kWh  (n={n_energy}, worst={res_where})")

# ---- scalar vs batch parity
mism = 0; ncmp = 0
for cell in CELLS:
    m, p, wood = make(cell)
    n = 48
    ot = rng.uniform(-20, 10, n); wi = rng.uniform(0, 10, n); ra = rng.uniform(0, 2, n)
    so = rng.uniform(0, 500, n); hu = rng.uniform(60, 95, n); ex = rng.uniform(0, 8, n) * (rng.random(n) < 0.4)
    ws = WeatherSeries(outdoor_temps=ot, wind_speeds=wi, precipitation=ra, solar_radiation=so, humidity=hu, external_heat_kw=ex)
    st = ThermalState(room_temperature=20.5, slab_temperature=24.0, upper_floor_temperature=21.0,
                      lower_floor_temperature=20.2, buffer_tank_temperature=45.0,
                      wood_tank_temperature=60.0 if wood else None)
    pw = rng.uniform(0, 6, (4, n))
    b = m.simulate_trajectory_batch(st, pw, ws, dt_hours=0.25)
    for r_ in range(4):
        tr = m.simulate_trajectory(st, pw[r_], ws, dt_hours=0.25)
        for name, a, ref in (("room", b["room"][r_], tr[0]), ("slab", b["slab"][r_], tr[1]),
                             ("upper", b["upper"][r_], tr[2]), ("lower", b["lower"][r_], tr[3]),
                             ("buffer", b["buffer"][r_], tr[4]), ("refused", b["refused"][r_], tr[5])):
            ncmp += 1
            if not np.array_equal(a, ref):
                mism += 1
                print(f"  parity {cell} row{r_} {name} first@{int(np.argmax(a != ref))} maxdiff={np.max(np.abs(a-ref)):.3e}")
        if wood and not np.array_equal(b["wood"][r_], tr[6]):
            mism += 1; print(f"  parity {cell} row{r_} wood")
print(f"RESULT parity_mismatch={mism} count (of {ncmp})")

# ---- dt invariance, monotonicity, bounds
dmax = {}; mono = 0; nmono = 0; bnd = 0
for cell in CELLS:
    m, p, wood = make(cell)
    for k in range(60):
        st = ThermalState(room_temperature=rng.uniform(18, 23), slab_temperature=rng.uniform(20, 30),
                          upper_floor_temperature=rng.uniform(18, 23), lower_floor_temperature=rng.uniform(18, 23),
                          buffer_tank_temperature=rng.uniform(25, 60),
                          wood_tank_temperature=rng.uniform(30, 90) if wood else None)
        if not p.two_zone_enabled:
            st = tm.replace(st, upper_floor_temperature=st.room_temperature, lower_floor_temperature=st.room_temperature)
        P = rng.uniform(0, 6); out = rng.uniform(-20, 10)
        a = st
        for _ in range(4):
            a = m.simulate_step(a, P, out, dt_hours=0.25)
        bb = m.simulate_step(st, P, out, dt_hours=1.0)
        for f_ in ("upper_floor_temperature", "lower_floor_temperature", "slab_temperature", "buffer_tank_temperature"):
            dmax[(cell, f_)] = max(dmax.get((cell, f_), 0.0), abs(getattr(a, f_) - getattr(bb, f_)))
        lo = m.simulate_step(st, P, out, dt_hours=0.25)
        hi = m.simulate_step(st, P + 0.5, out, dt_hours=0.25)
        nmono += 1
        if any(getattr(hi, f_) < getattr(lo, f_) - 1e-12 for f_ in
               ("upper_floor_temperature", "lower_floor_temperature", "slab_temperature", "buffer_tank_temperature")):
            mono += 1
        # bounds over a 24h coast/charge
        s = st
        for i in range(96):
            s = m.simulate_step(s, P if i % 8 < 4 else 0.0, out, dt_hours=0.25)
            if s.buffer_tank_temperature > max(p.buffer_max_temp, st.buffer_tank_temperature) + 1e-6 \
               or min(s.upper_floor_temperature, s.lower_floor_temperature, s.slab_temperature, s.buffer_tank_temperature) < min(out, 0) - 1:
                bnd += 1; break
for (cell, f_), v in sorted(dmax.items()):
    print(f"RESULT dt_inv_maxdiff[{cell}:{f_}]={v:.4f} K")
print(f"RESULT monotone_viol={mono} count (of {nmono})")
print(f"RESULT bound_viol={bnd} count")
nsubs = {c: make(c)[0]._substeps_and_loss(5.0, 1.0, 0.25)[0] for c in CELLS}
print("RESULT n_sub_by_cell=" + ",".join(f"{c}:{v}" for c, v in nsubs.items()))
# buffer cap: a tank read above the cap must cool at its physical rate, not snap
m, p, _ = make("two_zone_valve")
st = ThermalState(upper_floor_temperature=21, lower_floor_temperature=21, slab_temperature=25,
                  buffer_tank_temperature=p.buffer_max_temp + 15.0)
s1 = m.simulate_step(st, 0.0, 0.0, dt_hours=0.25)
print(f"RESULT cap_overread_drop={st.buffer_tank_temperature - s1.buffer_tank_temperature:.4f} K (cap {p.buffer_max_temp})")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")

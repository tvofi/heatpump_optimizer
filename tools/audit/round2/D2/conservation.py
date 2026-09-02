#!/usr/bin/env python
"""D2 harness -- energy conservation of the thermal model, per kernel call and per trajectory.

Metric: |E_end - E_start - sum over kernel calls of (heat in - losses - refused)*dt| in kWh,
where E is the enthalpy of every modelled store (room/slab or upper/lower/slab/buffer/wood,
plus the DHW tank on the with-DHW path), the kernels are ThermalModel._simulate_step_single,
ThermalModel._simulate_step_two_zone and ThermalModel.simulate_dhw_step (hooked on the
instance), and the fluxes are recomputed from the pre-call state with the model's own
public helpers (compute_cop, effective_heat_loss_coefficient, compute_solar_gain,
internal_gains_at). Reported as the maximum over 49 golden configurations x 3 random
schedules x 96 steps, for simulate_trajectory, simulate_trajectory_with_dhw (coil
included) and simulate_step in the sub-step regime.
Command: PYTHONPATH=tests/hastub python tools/audit/round2/D2/conservation.py
Expected (c398fc84): conservation_max_resid_space <= 1e-9 kWh; _dhw <= 1e-9 kWh;
  _substep <= 1e-9 kWh; wood_cap_deleted_kwh > 0 only in the deliberate cap cell.
Perturbation: a one-line production edit dropping "- q_buf_loss" from dT_buf in
  _simulate_step_two_zone moves conservation_max_resid_space up (to ~0.1 kWh per step).
Instrumented: thermal_model:ThermalModel._simulate_step_two_zone, _simulate_step_single,
  simulate_dhw_step, simulate_trajectory, simulate_trajectory_with_dhw, simulate_step.
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

import golden
from profiles import house
from heatpump_optimizer import mixing_valve
from heatpump_optimizer import thermal_model as tm
from heatpump_optimizer.thermal_model import (
    DHW_AMBIENT_TEMP, ThermalModel, ThermalParameters, ThermalState, dhw_coil_draw_reduction,
)

START = golden.START
rng = np.random.default_rng(23)


class Ledger:
    """Hooks the three kernels on one model instance and books every flux."""

    def __init__(self, model: ThermalModel):
        self.m = model
        self.net = 0.0          # kWh into the stores, by the kernels' own fluxes
        self.wood_cap = 0.0     # kWh the wood ceiling deleted (documented, unbooked)
        self.calls = 0
        self.last_wood = None
        self.coil = 0.0         # kWh the DHW coil pulled from the wood tank

    def install(self):
        m = self.m
        p = m.params
        o2, o1, od = m._simulate_step_two_zone, m._simulate_step_single, m.simulate_dhw_step

        def two(state, P, out, wind=0.0, rain=0.0, solar=0.0, dt=0.25, ext=0.0, vt=None, hum=None, hour=None):
            throttled = mixing_valve.is_throttling(p.mixing_valve_mode)
            two_tank = throttled and p.two_tank_modelled and state.wood_tank_temperature is not None
            T_buf = state.buffer_tank_temperature
            cop = m.compute_cop(out, humidity=hum, flow_temp=T_buf if throttled else None)
            e = max(0.0, ext)
            u_up = m.effective_heat_loss_coefficient(p.upper_floor_heat_loss, wind, rain)
            u_lo = m.effective_heat_loss_coefficient(p.lower_floor_heat_loss_learned, wind * 0.5, rain * 0.5)
            q_solar = m.compute_solar_gain(solar)
            q_int = m.internal_gains_at(hour) if hour is not None else p.internal_gains
            losses = (p.buffer_tank_heat_loss_coefficient * (T_buf - 20.0)
                      + u_up * (state.upper_floor_temperature - out)
                      + u_lo * (state.lower_floor_temperature - out))
            if two_tank:
                if self.last_wood is not None:
                    # Anything that moved the wood tank between kernel calls is the coil.
                    self.coil += (self.last_wood - state.wood_tank_temperature) * max(p.wood_tank_thermal_mass, 0.01)
                losses += p.wood_tank_heat_loss_coefficient * (state.wood_tank_temperature - 20.0)
            new = o2(state, P, out, wind, rain, solar, dt, e, vt, hum, hour)
            self.net += (cop * P + e + q_solar + q_int - losses - m._step_buffer_refused) * dt
            if two_tank:
                # The wood ceiling deletes heat without booking it: measure it here.
                C_w = max(p.wood_tank_thermal_mass, 0.01)
                if new.wood_tank_temperature >= tm.WOOD_TANK_MAX_TEMP - 1e-12:
                    self.wood_cap += 1e-30  # marker only; the residual carries the amount
                self.last_wood = new.wood_tank_temperature
            self.calls += 1
            return new

        def single(state, P, out, wind=0.0, rain=0.0, solar=0.0, dt=0.25, ext=0.0, hum=None, hour=None):
            cop = m.compute_cop(out, humidity=hum)
            e = max(0.0, ext)
            u_eff = m.effective_heat_loss_coefficient(p.heat_loss_coefficient, wind, rain)
            q_solar = m.compute_solar_gain(solar)
            q_int = m.internal_gains_at(hour) if hour is not None else p.internal_gains
            loss = u_eff * (state.room_temperature - out)
            new = o1(state, P, out, wind, rain, solar, dt, e, hum, hour)
            self.net += (cop * P + e + q_solar + q_int - loss) * dt
            self.calls += 1
            return new

        def dhw(dhw_temp, dhw_power_thermal, hour_of_day, ambient_temp=DHW_AMBIENT_TEMP, dt_hours=0.25, draw_power=None):
            C = p.dhw_tank_thermal_mass
            new = od(dhw_temp, dhw_power_thermal, hour_of_day, ambient_temp, dt_hours, draw_power)
            if C >= 0.01:
                q_loss = p.dhw_tank_heat_loss_coefficient * (dhw_temp - ambient_temp)
                self.net += (dhw_power_thermal - m._step_dhw_draw_kw - q_loss
                             - m._step_dhw_refused + m._step_dhw_floor_injected) * dt_hours
            self.calls += 1
            return new

        m._simulate_step_two_zone = two
        m._simulate_step_single = single
        m.simulate_dhw_step = dhw


def energy(p: ThermalParameters, room, slab, upper, lower, buf, wood, dhw=None):
    if p.two_zone_enabled:
        C_buf = p.buffer_tank_thermal_mass
        if C_buf < 1e-6:
            C_buf = 0.04
        e = (max(C_buf, 0.01) * buf + p.slab_thermal_mass * slab
             + p.upper_floor_thermal_mass * upper + p.lower_floor_thermal_mass * lower)
        throttled = mixing_valve.is_throttling(p.mixing_valve_mode)
        if throttled and p.two_tank_modelled and wood is not None:
            e += max(p.wood_tank_thermal_mass, 0.01) * wood
    else:
        e = p.room_thermal_mass * room + p.slab_thermal_mass * slab
    if dhw is not None:
        e += p.dhw_tank_thermal_mass * dhw
    return e


def check_space(name, params, state, ot, wi, ra, so, ext, n=96):
    n = min(n, len(ot))
    worst = 0.0
    for _ in range(3):
        P = rng.uniform(0.0, params.max_electrical_power, size=n)
        m = ThermalModel(params)
        led = Ledger(m)
        led.install()
        r, s, u, l = m.simulate_trajectory(state, P, ot[:n], wi[:n], ra[:n], so[:n], 0.25, ext, None, None, 7.0)
        buf = m.last_buffer_trajectory
        wood = m.last_wood_trajectory
        e0 = energy(params, r[0], s[0], u[0], l[0], buf[0], None if wood is None else wood[0])
        e1 = energy(params, r[-1], s[-1], u[-1], l[-1], buf[-1], None if wood is None else wood[-1])
        resid = (e1 - e0) - led.net
        worst = max(worst, abs(resid))
    return worst


def check_dhw(name, params, state, ot, wi, ra, so, ext, n=96):
    n = min(n, len(ot))
    worst = 0.0
    for _ in range(3):
        P = rng.uniform(0.0, params.max_electrical_power * 0.6, size=n)
        D = rng.uniform(0.0, params.max_electrical_power * 0.4, size=n)
        m = ThermalModel(params)
        led = Ledger(m)
        led.install()
        r, s, u, l, d = m.simulate_trajectory_with_dhw(state, P, D, ot[:n], wi[:n], ra[:n], so[:n], 7.0, 0.25,
                                                        None, ext, None, None)
        buf = m.last_buffer_trajectory
        wood = m.last_wood_trajectory
        e0 = energy(params, r[0], s[0], u[0], l[0], buf[0], None if wood is None else wood[0], d[0])
        e1 = energy(params, r[-1], s[-1], u[-1], l[-1], buf[-1], None if wood is None else wood[-1], d[-1])
        coil = led.coil
        if wood is not None and led.last_wood is not None:
            coil += (led.last_wood - wood[-1]) * max(params.wood_tank_thermal_mass, 0.01)
        resid = (e1 - e0) - (led.net - coil)
        worst = max(worst, abs(resid))
    return worst


worst_space = 0.0
worst_dhw = 0.0
cells_space = 0
cells_dhw = 0
per_family = {}
for name, spec in golden.SCENARIOS.items():
    built = golden.make(**spec)
    p = built["optimizer"].model.params
    st = built["state"]
    ot, wi, ra, so = built["outdoor"], built["wind"], built["rain"], built["solar"]
    ext = golden.external_heat_for(min(96, len(ot))) if name in golden.EXTERNAL_HEAT_SCENARIOS else None
    d = check_space(name, p, st, ot, wi, ra, so, ext)
    worst_space = max(worst_space, d)
    cells_space += 1
    fam = p.topology_layout if p.two_zone_enabled else "single"
    per_family[fam] = max(per_family.get(fam, 0.0), d)
    if p.dhw_enabled:
        dd = check_dhw(name, p, st, ot, wi, ra, so, ext)
        worst_dhw = max(worst_dhw, dd)
        cells_dhw += 1
        if dd > 1e-9:
            print(f"CELL dhw {name}: resid={dd:.3e} kWh")
    if d > 1e-9:
        print(f"CELL space {name}: resid={d:.3e} kWh")
for fam, v in per_family.items():
    print(f"CELL family {fam}: max_resid={v:.3e} kWh")
print(f"RESULT conservation_space_cells={cells_space} count")
print(f"RESULT conservation_max_resid_space={worst_space:.3e} kWh")
print(f"RESULT conservation_dhw_cells={cells_dhw} count")
print(f"RESULT conservation_max_resid_dhw={worst_dhw:.3e} kWh")

# Learned internal-gains profile and a humidity series (the #53/#21 paths).
built = golden.make(two_zone=True, dhw=False)
p = built["optimizer"].model.params
p.internal_gains_profile = [0.2 + 0.3 * (h % 6) / 5.0 for h in range(24)]
m = ThermalModel(p)
led = Ledger(m)
led.install()
P = rng.uniform(0.0, 6.0, size=96)
hum = rng.uniform(40.0, 95.0, size=96)
r, s, u, l = m.simulate_trajectory(built["state"], P, built["outdoor"], built["wind"], built["rain"],
                                   built["solar"], 0.25, None, None, hum, 7.0)
buf = m.last_buffer_trajectory
resid = energy(p, r[-1], s[-1], u[-1], l[-1], buf[-1], None) - energy(p, r[0], s[0], u[0], l[0], buf[0], None) - led.net
print(f"RESULT conservation_resid_gains_profile={abs(resid):.3e} kWh")

# Sub-step regime through simulate_step (two-zone, valve, floored upper mass).
cfg = house(two_zone=True, dhw=False)
cfg.update({"upper_floor_thermal_mass": 0.25, "inter_zone_heat_transfer": 3.0, "mixing_valve_mode": "manual",
            "buffer_tank_volume": 750.0})
p = ThermalParameters.from_config(cfg)
p.dhw_enabled = False
m = ThermalModel(p)
print(f"CELL substep n_sub={m._stability_substeps(2.0, 0.0, 0.25)}")
led = Ledger(m)
led.install()
r, s, u, l = m.simulate_trajectory(built["state"], P, built["outdoor"], built["wind"], built["rain"],
                                   built["solar"], 0.25, None, None, None, None)
buf = m.last_buffer_trajectory
resid = energy(p, r[-1], s[-1], u[-1], l[-1], buf[-1], None) - energy(p, r[0], s[0], u[0], l[0], buf[0], None) - led.net
print(f"RESULT conservation_max_resid_substep={abs(resid):.3e} kWh")

# The wood ceiling: a deliberate cell that drives the wood tank to WOOD_TANK_MAX_TEMP.
built = golden.make(**golden.SCENARIOS["wood_two_tank"])
p = built["optimizer"].model.params
st = built["state"]
st.wood_tank_temperature = 94.5
m = ThermalModel(p)
led = Ledger(m)
led.install()
ext = np.full(96, 8.0)
r, s, u, l = m.simulate_trajectory(st, np.zeros(96), built["outdoor"], built["wind"], built["rain"],
                                   built["solar"], 0.25, ext, None, None, None)
buf = m.last_buffer_trajectory
wood = m.last_wood_trajectory
resid = energy(p, r[-1], s[-1], u[-1], l[-1], buf[-1], wood[-1]) - energy(p, r[0], s[0], u[0], l[0], buf[0], wood[0]) - led.net
print(f"CELL wood cap: wood max={float(np.max(wood)):.2f} C, deleted={-resid:.3f} kWh of {float(np.sum(ext) * 0.25):.1f} kWh burn")
print(f"RESULT wood_cap_deleted_kwh={-resid:.3f} kWh")

# The coil identity, bitwise, over a sweep.
viol = 0
worst_coil = 0.0
for draw in np.linspace(0.0, 3.0, 31):
    for tw in np.linspace(5.0, 95.0, 46):
        red, coil = dhw_coil_draw_reduction(float(draw), float(tw), 55.0, 10.0)
        if red + coil != draw or red < 0 or coil < 0:
            viol += 1
            worst_coil = max(worst_coil, abs(red + coil - draw))
print(f"RESULT coil_identity_bitwise_violations={viol} count of {31 * 46}")
print(f"RESULT coil_identity_max_abs_err={worst_coil:.3e} kW (ulp-level rounding of draw - reduced)")

proc = time.process_time() - _T_PROC0
thr = time.thread_time() - _T_THR0
print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")

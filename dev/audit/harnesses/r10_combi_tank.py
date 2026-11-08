"""R10-COMBI-TANK-STORE (#3225): one store for space heating and hot water.

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r10_combi_tank.py [ARM ...]

Synthetic installs only; no private data. The install is the issue's shape:
a 504 l store behind a smart-write valve with a 40 l potable coil, eps 0.85
unless an arm says otherwise. Every arm prints ``RESULT name=value`` lines;
no arm asserts, tests/features.py's R10-COMBI-TANK-STORE block does that.

``issue``: the battery's components and stored kWh at 55 degC for the
workaround base offers (a 504 l "DHW tank" beside the 504 l buffer, both on
one probe) against the combi store: the workaround counts the water twice.

``off_identity``: the store view with the option off, field for field
against the separate tank's own properties (1 when bitwise equal).

``balance`` / ``ua_zero`` / ``eps_null``: ``store_step`` over a 48-step day;
the kWh residual of ``C * dT`` against its booked terms, the same with UA 0,
and the end temperatures at eps 0.6 and 1.0 of a store cooling from 64.5 degC
with the tap kept above 40 degC (a 65 degC setpoint keeps the rating above it).

``legionella_eps``: the cycle's (due, step, hour) at eps 0.6 and 1.0.

``lp_flux``: kWh the DHW planner buys with no space flux and with a 2 kW
valve draw over the four hours before a 19-21 window, combi and separate.

``exchange``: a joint solve at a two-tier price day: the rounds the flux
exchange took, the worst shortfall below the hot-water requirement, and the
same solve with zero exchange rounds (the null), plus the solve's seconds.
"""
from __future__ import annotations

import math
import sys
import time
from dataclasses import replace
from datetime import datetime

import numpy as np

from heatpump_optimizer import battery, mixing_valve
from heatpump_optimizer import optimizer as optmod
from heatpump_optimizer import thermal_model as tm
from heatpump_optimizer.dhw_planner import DhwPlanner
from heatpump_optimizer.dhw_schedule import parse_windows
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig, _Horizon
from profiles import solve_inputs


def params(combi=True, eps=0.85, **kw):
    base = dict(buffer_tank_volume=504.0, mixing_valve_mode=mixing_valve.MODE_SMART_WRITE,
                dhw_enabled=True, dhw_tank_volume=200.0, combi_potable_volume_l=40.0)
    base.update(kw)
    return tm.ThermalParameters(dhw_combi_tank_enabled=combi, combi_dhw_effectiveness=eps, **base)


def state(t=50.0, since=1.0):
    return tm.ThermalState(room_temperature=21.0, slab_temperature=23.0,
                           buffer_tank_temperature=t, dhw_temperature=t,
                           outdoor_temperature=0.0, dhw_hours_since_legionella=since)


def horizon(st, n=96, dt=0.25):
    return _Horizon(
        initial_state=st, prices=np.full(n, 1.0), outdoor_temps=np.full(n, 0.0),
        wind_speeds=np.zeros(n), precipitation=np.zeros(n), solar_radiation=np.zeros(n),
        start_time=None, n_steps=n, dt=dt, comfort_targets=np.full(n, 21.0),
        temp_min_bounds=np.full(n, 17.0), temp_max_bounds=np.full(n, 23.0),
        step_hours=np.arange(n) * dt, solar_gains=np.zeros(n), heat_loss_factors=np.ones(n),
        forecast={}, t_start=0.0)


def opt_for(p):
    return HeatPumpOptimizer(tm.ThermalModel(p), OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0))


def planner(p):
    o = opt_for(p)
    return DhwPlanner(o.model, o.config, o._pv_surplus, o._price_known)


def arm_issue():
    for label, p in (("workaround", params(combi=False, dhw_tank_volume=504.0)),
                     ("combi", params())):
        b = battery.build(p, state(55.0), comfort_min=20.0, comfort_max=23.0,
                          dhw_min=45.0, dhw_max=60.0, cop=3.0)
        tanks = [c for c in b.components if c.name in ("buffer_tank", "dhw_tank")]
        print(f"RESULT {label}_tank_components={len(tanks)}")
        print(f"RESULT {label}_tank_kwh_per_c={sum(c.capacity_kwh_per_c for c in tanks):.4f}")


def arm_off_identity():
    p = params(combi=False)
    s = p.dhw_store
    same = (s.capacity_kwh_per_c == p.dhw_tank_thermal_mass
            and s.ua_kw_per_c == p.dhw_tank_heat_loss_coefficient
            and s.charge_max_temp == p.dhw_max_temp and s.rating_max_temp == p.dhw_hard_max_temp
            and s.inlet_c == p.dhw_inlet_reference and not s.combi)
    print(f"RESULT off_store_bitwise={int(same)}")


def walk(store, t0, heat, draw, dt=0.5):
    temps, terms = [t0], []
    for q_in, q_draw in zip(heat, draw):
        t = temps[-1]
        new, refused, injected, debited = tm.store_step(store, t, q_in, q_draw, 20.0, dt)
        terms.append((q_in - debited - store.ua_kw_per_c * (t - 20.0) - refused + injected) * dt)
        temps.append(new)
    return temps, terms


def arm_balance(ua_zero=False):
    store = params().dhw_store
    if ua_zero:
        store = replace(store, ua_kw_per_c=0.0)
    heat = [3.0 * math.sin(i / 5.0) - 1.0 for i in range(48)]
    draw = [0.0 if i % 7 else 6.0 for i in range(48)]
    temps, terms = walk(store, 58.0, heat, draw)
    gap = store.capacity_kwh_per_c * (temps[-1] - temps[0]) - math.fsum(terms)
    print(f"RESULT {'ua_zero' if ua_zero else 'balance'}_residual_kwh={gap:.3e}")


def arm_eps_null():
    for eps in (0.6, 1.0):
        temps, _ = walk(params(eps=eps, dhw_setpoint=65.0).dhw_store, 64.5, [1.6] * 6, [2.0] * 6)
        print(f"RESULT eps_{eps}_end_c={temps[-1]:.12f}")


def arm_legionella_eps():
    for eps in (0.6, 1.0):
        p = params(eps=eps, dhw_legionella_enabled=True, dhw_legionella_temp=60.0,
                   dhw_legionella_interval_days=7.0, dhw_daily_consumption=0.0,
                   dhw_min_temp=30.0, dhw_schedule_enabled=True,
                   dhw_windows=parse_windows("18:00-19:00"))
        plan, _ = planner(p)._build_dhw_requirements(
            horizon(state(50.0, since=7 * 24.0 - 6.0)), p_max=4.0)
        print(f"RESULT legionella_eps_{eps}=({plan.legionella_due},{plan.legionella_step},"
              f"{plan.legionella_hour})")


def arm_lp_flux():
    exo = np.zeros(96)
    exo[60:76] = -2.0
    for combi in (True, False):
        for label, series in (("none", np.zeros(96)), ("draw", exo)):
            p = params(combi=combi, dhw_schedule_enabled=True,
                       dhw_windows=parse_windows("19:00-21:00"), dhw_min_temp=40.0)
            plan, _ = planner(p)._build_dhw_requirements(
                horizon(state(50.0)), p_max=4.0, tank_exo_kw=series)
            kind = "combi" if combi else "separate"
            print(f"RESULT lp_flux_{kind}_{label}_kwh={float(np.sum(plan.schedule)) * 0.25:.4f}")


def arm_exchange():
    prices = np.full(96, 1.5)
    prices[:20] = 0.8
    prices[64:80] = 4.0
    rounds_taken = []
    real = optmod._combi_flux_exchange

    def counted(opt, h, planner_, space, dhw, draws, p_max):
        calls = {"n": 0}
        build = planner_._build_dhw_requirements

        def wrapped(*a, **k):
            calls["n"] += 1
            return build(*a, **k)

        planner_._build_dhw_requirements = wrapped
        try:
            return real(opt, h, planner_, space, dhw, draws, p_max)
        finally:
            rounds_taken.append(calls["n"])

    for label, rounds in (("exchange", None), ("null", 0)):
        o = opt_for(params())
        saved = optmod._COMBI_EXCHANGE_ROUNDS
        optmod._combi_flux_exchange = counted
        if rounds is not None:
            optmod._COMBI_EXCHANGE_ROUNDS = rounds
        try:
            t0 = time.perf_counter()
            r = o.optimize(inputs=solve_inputs(
                initial_state=state(50.0), prices=prices, outdoor_temps=np.full(96, 0.0),
                wind_speeds=np.zeros(96), precipitation=np.zeros(96),
                solar_radiation=np.zeros(96), start_time=datetime(2026, 1, 15)))
            secs = time.perf_counter() - t0
        finally:
            optmod._combi_flux_exchange = real
            optmod._COMBI_EXCHANGE_ROUNDS = saved
        req = np.asarray(o._dhw_requirement)
        gap = float(np.max(req - np.asarray(r.dhw_temp_trajectory)[1:req.size + 1]))
        print(f"RESULT {label}_rounds={rounds_taken[-1] if rounds_taken else 0}")
        print(f"RESULT {label}_worst_shortfall_c={gap:.3f}")
        print(f"RESULT {label}_dhw_kwh={float(np.sum(r.dhw_power_schedule)) * 0.25:.3f}")
        print(f"RESULT {label}_solve_s={secs:.2f}")


ARMS = {
    "issue": arm_issue, "off_identity": arm_off_identity, "balance": arm_balance,
    "ua_zero": lambda: arm_balance(ua_zero=True), "eps_null": arm_eps_null,
    "legionella_eps": arm_legionella_eps, "lp_flux": arm_lp_flux, "exchange": arm_exchange,
}

if __name__ == "__main__":
    for name in sys.argv[1:] or list(ARMS):
        ARMS[name]()

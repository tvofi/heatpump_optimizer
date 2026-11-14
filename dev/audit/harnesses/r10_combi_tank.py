"""R10-COMBI-TANK-STORE (#3225): one store for space heating and hot water.

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r10_combi_tank.py [ARM ...]

Synthetic installs only; no private data. The install is the issue's shape:
a 504 l store behind a smart-write valve with a 40 l potable coil and the
manual's 111 W standing loss at 65 degC (UA 111/45 W/K), eps 0.85 unless an
arm says otherwise. Every arm prints ``RESULT name=value`` lines;
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
same solve with zero exchange rounds (the null), plus the solve's seconds,
the published ``dhw_heating_cost`` and the tap's draw on the same day.

``equiv``: the two comparison mutants the mutation ledger triages as
equivalent, each the operator's own text compiled over the head's function
(``dhw_store_of``'s ``eps >=`` to ``>``, ``store_step``'s ``d_temp >`` to
``>=`` and ``new_temp <`` to ``<=``), against the head over a grid holding
each comparison's tie; the
cases that differ, the ties the grid reaches, and a tie-only control that
moves only the tied result (it must differ on every tie, or the grid does not
reach one).
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


#: The MFS 600 S's ErP standing loss, 111 W at 65 degC (carry 4, item 1), as
#: the cooling rate its UA of 111/45 W/K gives at 25 K over 544 l.
RATE = 0.111 / 45.0 * 25.0 / (tm.WATER_SPECIFIC_HEAT * 544.0)


def params(combi=True, eps=0.85, **kw):
    base = dict(buffer_tank_volume=504.0, mixing_valve_mode=mixing_valve.MODE_SMART_WRITE,
                dhw_enabled=True, dhw_tank_volume=200.0, combi_potable_volume_l=40.0,
                buffer_cooling_rate=RATE)
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
    print(f"RESULT combi_store_ua_w_per_k={params().dhw_store.ua_kw_per_c * 1000.0:.4f}")


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
        # What the user sees for the same day: the published DHW Heating Cost
        # (next 24 h), and the tap's own draw the store serves (kWh_th).
        print(f"RESULT {label}_published_dhw_heating_cost={r.dhw_heating_cost:.3f}")
        draws = o.model.dhw_draw_rates(np.arange(96) * 0.25 % 24.0)
        print(f"RESULT {label}_tap_draw_kwh_th={float(np.sum(draws)) * 0.25:.3f}")
        print(f"RESULT {label}_solve_s={secs:.2f}")


def _swapped(fn, old, new):
    """``fn`` recompiled with ``old`` replaced once in its source, over its globals."""
    import inspect
    import textwrap
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(old) == 1, (fn.__name__, old)
    ns: dict = {}
    exec(compile(src.replace(old, new), f"<{fn.__name__} mutant>", "exec"), fn.__globals__, ns)
    return ns[fn.__name__]


def _same(a, b):
    return all(x == y or (x != x and y != y) for x, y in zip(a, b))


def arm_equiv():
    floor = tm.COMBI_DHW_EFFECTIVENESS_FLOOR
    cond = "eps = min(1.0, eps) if eps >= COMBI_DHW_EFFECTIVENESS_FLOOR else COMBI_DHW_EFFECTIVENESS_FLOOR"
    mut = _swapped(tm.dhw_store_of, cond, cond.replace(" >= ", " > ", 1))
    tie = _swapped(tm.dhw_store_of, cond, cond.replace(
        "min(1.0, eps) if", "(min(1.0, eps) if eps != COMBI_DHW_EFFECTIVENESS_FLOOR else 0.5) if", 1))
    grid = [0.0, -1.0, math.nextafter(floor, 0.0), floor, math.nextafter(floor, 1.0), 0.5, 0.85,
            1.0, 1.5, math.inf, math.nan]
    rows = [(tm.dhw_store_of(params(eps=e)).effectiveness, mut(params(eps=e)).effectiveness,
             tie(params(eps=e)).effectiveness, e == floor) for e in grid]
    print(f"RESULT equiv_eps_cases={len(rows)}")
    print(f"RESULT equiv_eps_ties={sum(r[3] for r in rows)}")
    print(f"RESULT equiv_eps_differ={sum(not _same((r[0],), (r[1],)) for r in rows)}")
    print(f"RESULT equiv_eps_tie_control_differ_on_ties="
          f"{sum(not _same((r[0],), (r[2],)) for r in rows if r[3])}")
    print(f"RESULT equiv_eps_tie_control_differ_off_ties="
          f"{sum(not _same((r[0],), (r[2],)) for r in rows if not r[3])}")

    step = "    if d_temp > cap:\n        refused, d_temp = (d_temp - cap) * capacity, cap"
    smut = _swapped(tm.store_step, step, step.replace("d_temp > cap", "d_temp >= cap", 1))
    stie = _swapped(tm.store_step, step, "    if d_temp == cap:\n        refused += 1.0\n" + step)
    base = replace(params().dhw_store, capacity_kwh_per_c=1.0, ua_kw_per_c=0.0)
    cases = []
    # Ties: C = 1, no loss and no draw make d_temp the heat in, and the
    # rating's distance over dt an exact binary fraction, so heat == cap exactly.
    for below, dt in ((10.0, 0.5), (4.0, 0.25), (1.0, 1.0)):
        cases.append((base, base.rating_max_temp - below, below / dt, 0.0, 20.0, dt))
    store = params().dhw_store
    for temp in (10.0, 45.0, 60.0, store.rating_max_temp, store.rating_max_temp + 3.0):
        for heat in (-2.0, 0.0, 1.5, 6.0, 40.0):
            for draw in (0.0, 2.0):
                cases.append((store, temp, heat, draw, 15.0, 0.25))
    ties = differ = tie_hit = tie_off = 0
    for c in cases:
        head = tm.store_step(*c)
        d_temp = ((c[2] - c[3] * tm.dhw_draw_scale(c[0].tap_temp_for_store(c[1]), c[0].inlet_c)
                   - c[0].ua_kw_per_c * (c[1] - c[4])) / c[0].capacity_kwh_per_c)
        is_tie = d_temp == max(0.0, c[0].rating_max_temp - c[1]) / max(c[5], 1e-6)
        ties += is_tie
        differ += not _same(head, smut(*c))
        moved = not _same(head, stie(*c))
        tie_hit += moved and is_tie
        tie_off += moved and not is_tie
    print(f"RESULT equiv_step_cases={len(cases)}")
    print(f"RESULT equiv_step_ties={ties}")
    print(f"RESULT equiv_step_differ={differ}")
    print(f"RESULT equiv_step_tie_control_differ_on_ties={tie_hit}")
    print(f"RESULT equiv_step_tie_control_differ_off_ties={tie_off}")

    fl = "    if new_temp < floor:\n        injected, new_temp ="
    fmut = _swapped(tm.store_step, fl, fl.replace("new_temp < floor", "new_temp <= floor", 1))
    ftie = _swapped(tm.store_step, fl, "    if new_temp == floor:\n        injected += 1.0\n" + fl)
    # Floor ties: ambient 8 below the inlet makes the floor 8, and an exact
    # binary heat over dt lands the step on it.
    fcases = [(base, temp, (8.0 - temp) / dt, 0.0, 8.0, dt)
              for temp, dt in ((12.0, 0.5), (9.0, 0.25), (16.0, 1.0))]
    fcases += cases
    fties = fdiffer = fhit = foff = 0
    for c in fcases:
        head = tm.store_step(*c)
        pre = c[1] + min((c[2] - c[3] * tm.dhw_draw_scale(c[0].tap_temp_for_store(c[1]), c[0].inlet_c)
                          - c[0].ua_kw_per_c * (c[1] - c[4])) / c[0].capacity_kwh_per_c,
                         max(0.0, c[0].rating_max_temp - c[1]) / max(c[5], 1e-6)) * c[5]
        is_tie = pre == min(c[0].inlet_c, c[4])
        fties += is_tie
        fdiffer += not _same(head, fmut(*c))
        moved = not _same(head, ftie(*c))
        fhit += moved and is_tie
        foff += moved and not is_tie
    print(f"RESULT equiv_floor_cases={len(fcases)}")
    print(f"RESULT equiv_floor_ties={fties}")
    print(f"RESULT equiv_floor_differ={fdiffer}")
    print(f"RESULT equiv_floor_tie_control_differ_on_ties={fhit}")
    print(f"RESULT equiv_floor_tie_control_differ_off_ties={foff}")


ARMS = {
    "issue": arm_issue, "off_identity": arm_off_identity, "balance": arm_balance,
    "ua_zero": lambda: arm_balance(ua_zero=True), "eps_null": arm_eps_null,
    "legionella_eps": arm_legionella_eps, "lp_flux": arm_lp_flux, "exchange": arm_exchange,
    "equiv": arm_equiv,
}

if __name__ == "__main__":
    for name in sys.argv[1:] or list(ARMS):
        ARMS[name]()

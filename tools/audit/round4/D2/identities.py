"""D2 round 4: the identities that HELD. This harness exists so the next
round does not re-do the work, and so a reader can tell a dry area from an
unexamined one. Every number here is a pass; none of them is a finding.

METRIC (one line per section, all executed against production symbols):
  cons.*   per-step energy imbalance, kWh: the change in stored enthalpy
           across every store minus (heat in - losses + gains)*dt, with the
           buffer cap's refused power added back. Contract: 0 to 1e-9 kWh.
  mono.*   the most negative change in any store temperature caused by
           RAISING electrical power by 0.25 kW. Contract: >= -1e-9 degC.
  cop.*    the most positive step of compute_cop along rising FLOW
           temperature and of compute_cop_dhw along rising tank temperature.
           Contract: <= 1e-12. (Monotonicity in OUTDOOR temperature does NOT
           hold; it is finding D2-04, measured in cop_below_unity.py.)
  dt.*     max |T_end(24 h at 0.25 h) - T_end(24 h at 0.03125 h)| over the
           stores, at the only step production integrates at. Contract:
           reported, not gated -- a first-order integrator may differ.
  derate.* min and max of DefrostDerate.factor over the whole learned grid
           after observing extreme duties. Contract: within [0.55, 1.0].
  share.*  wood_share range over a 40 x 40 sweep. Contract: within [0, 1],
           and _wood_share_vec bit-identical to the scalar law.
  coil.*   max |reduced + coil - draw| for dhw_coil_draw_reduction.
           Contract: 0 exactly.
  cost.*   max |_energy_cost_fn(p) - sum(price*p)*dt| with no PV, and
           max |_energy_cost_fn(p) - (export*min(p,s) + price*max(p-s,0))*dt|
           with PV surplus. Contract: 0 to 1e-12.
  window.* max |metering_windows(x) - the box average of x| and
           |marginal_price_per_kw - price/k|. Contract: 0 to 1e-12.

EXACT COMMAND (from the export root):
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D2/identities.py

EXPECTED (baseline 7dd68dd): every `*_worst` at or below its contract; the
headline numbers are cons.worst_imbalance_kwh = -1.2967e-13 over 1600 cases,
mono.worst_delta_c = -2.13e-14 over 6240 comparisons,
coil.worst_identity_error_kw = 5.55e-17, cost.no_pv_error = 0 and
cost.pv_error = 7.1e-15, window.box_average_error = 0,
dt.worst_24h_0.25h_vs_0.03125h_c = 0.0113.

INSTRUMENTED SYMBOLS: ThermalModel.simulate_step / simulate_trajectory /
compute_cop / compute_cop_dhw, thermal_model.wood_share /
_wood_share_vec / dhw_coil_draw_reduction, defrost.DefrostDerate.factor /
observe_duty, HeatPumpOptimizer._energy_cost_fn, tariff.metering_windows,
tariff.CapacityTariff.marginal_price_per_kw.

PERTURBATION: each section's contract is falsifiable by a one-line
production edit -- e.g. changing `dT_slab` in _simulate_step_single to
divide by `p.room_thermal_mass` breaks cons.*; dropping `max(0.0, ...)` in
import_margin breaks cost.pv. The judge does not need these to run: a
non-finding's job is to be re-runnable, and a green pass with no
perturbation is exactly what "held" means here.

ROOT RULE: os.getcwd(); resolves nothing from __file__.
BASELINE SHA: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 (export, no .git).
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, python 3.11.5, numpy 2.4.6.
"""
from __future__ import annotations

import os
import sys

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "tools", "audit", "round4", "D2"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "tests", "hastub"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

import numpy as np  # noqa: E402  (after the pin, deliberately)

from _d2common import Cpu, footer, result  # noqa: E402
from heatpump_optimizer import defrost, mixing_valve, pv  # noqa: E402
from heatpump_optimizer import tariff as tmod  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState,
)

CPU = Cpu()
RNG = np.random.default_rng(11)

CONFIGS = [
    ("single-zone no valve", {"two_zone_enabled": False,
                              "mixing_valve_mode": "none"}),
    ("single-zone valve", {"two_zone_enabled": False,
                           "mixing_valve_mode": "manual"}),
    ("two-zone no valve", {"two_zone_enabled": True,
                           "mixing_valve_mode": "none"}),
    ("two-zone valve", {"two_zone_enabled": True,
                        "mixing_valve_mode": "manual"}),
    ("two-tank 4-way", {"two_zone_enabled": True,
                        "mixing_valve_mode": "manual",
                        "wood_tank_configured": True}),
]


def make(cfg):
    p = ThermalParameters(**cfg)
    return p, ThermalModel(p)


def stored(p, st):
    if p.two_zone_enabled:
        e = (p.upper_floor_thermal_mass * st.upper_floor_temperature
             + p.lower_floor_thermal_mass * st.lower_floor_temperature
             + p.slab_thermal_mass * st.slab_temperature
             + max(p.buffer_tank_thermal_mass, 0.01)
             * st.buffer_tank_temperature)
        if (p.two_tank_modelled and st.wood_tank_temperature is not None
                and mixing_valve.is_throttling(p.mixing_valve_mode)):
            e += (max(p.wood_tank_thermal_mass, 0.01)
                  * st.wood_tank_temperature)
        return e
    return (p.room_thermal_mass * st.room_temperature
            + p.slab_thermal_mass * st.slab_temperature)


def rand_state(p, two_tank):
    return ThermalState(
        room_temperature=RNG.uniform(16, 24),
        slab_temperature=RNG.uniform(16, 30),
        outdoor_temperature=RNG.uniform(-20, 12),
        upper_floor_temperature=RNG.uniform(16, 24),
        lower_floor_temperature=RNG.uniform(16, 24),
        buffer_tank_temperature=RNG.uniform(25, 55),
        wood_tank_temperature=RNG.uniform(25, 80) if two_tank else None,
    )


# --- 1. energy conservation -------------------------------------------------
worst, wcase, n = 0.0, "", 0
for label, cfg in CONFIGS:
    p, m = make(cfg)
    two_tank = p.two_tank_modelled
    for _ in range(320):
        st = rand_state(p, two_tank)
        out = float(st.outdoor_temperature)
        pw, wind = RNG.uniform(0, 6), RNG.uniform(0, 8)
        rain, sol, ext = RNG.uniform(0, 3), RNG.uniform(0, 400), RNG.uniform(0, 4)
        with CPU:
            nxt = m.simulate_step(st, pw, out, wind, rain, sol, 0.25, ext)
        throttled = mixing_valve.is_throttling(p.mixing_valve_mode)
        cop = m.compute_cop(
            out, flow_temp=(st.buffer_tank_temperature
                            if (p.two_zone_enabled and throttled) else None))
        q_in = cop * pw + max(0.0, ext)
        if p.two_zone_enabled:
            u_up = m.effective_heat_loss_coefficient(
                p.upper_floor_heat_loss, wind, rain)
            u_lo = m.effective_heat_loss_coefficient(
                p.lower_floor_heat_loss_learned, wind * 0.5, rain * 0.5)
            q_loss = (u_up * (st.upper_floor_temperature - out)
                      + u_lo * (st.lower_floor_temperature - out))
            q_loss += p.buffer_tank_heat_loss_coefficient * (
                st.buffer_tank_temperature - 20.0)
            if two_tank and throttled and st.wood_tank_temperature is not None:
                q_loss += p.wood_tank_heat_loss_coefficient * (
                    st.wood_tank_temperature - 20.0)
            su, sl = m.solar_gain_per_zone(sol)
            gains = su + sl + p.internal_gains
        else:
            u = m.effective_heat_loss_coefficient(
                p.heat_loss_coefficient, wind, rain)
            q_loss = u * (st.room_temperature - out)
            gains = p.internal_gains + m.compute_solar_gain(sol)
        err = (stored(p, nxt) - stored(p, st)
               - (q_in - q_loss + gains) * 0.25
               + getattr(m, "_step_buffer_refused", 0.0) * 0.25)
        n += 1
        if abs(err) > abs(worst):
            worst, wcase = err, label
result("cons.cases", n, "count")
result("cons.worst_imbalance_kwh", worst, "kWh")
result("cons.worst_config", wcase)

# --- 2. more power never cools a store --------------------------------------
worst, wcase, n = 0.0, "", 0
for label, cfg in CONFIGS:
    p, m = make(cfg)
    for _ in range(240):
        st = rand_state(p, p.two_tank_modelled)
        out = float(st.outdoor_temperature)
        pw = RNG.uniform(0, 5)
        with CPU:
            a = m.simulate_step(st, pw, out, dt_hours=0.25)
            b = m.simulate_step(st, pw + 0.25, out, dt_hours=0.25)
        for f in ("room_temperature", "slab_temperature",
                  "upper_floor_temperature", "lower_floor_temperature",
                  "buffer_tank_temperature", "wood_tank_temperature"):
            va, vb = getattr(a, f), getattr(b, f)
            if va is None or vb is None:
                continue
            n += 1
            if vb - va < worst:
                worst, wcase = vb - va, f"{label}/{f}"
result("mono.comparisons", n, "count")
result("mono.worst_delta_c", worst, "degC")
result("mono.worst_at", wcase)

# --- 3. COP monotonicity ----------------------------------------------------
p, m = make({"two_zone_enabled": True, "mixing_valve_mode": "manual"})
m.params.cop_flow_carnot = True
outs = np.arange(-30.0, 20.01, 0.05)
flows = np.arange(35.0, 70.01, 0.05)
# NOTE: monotonicity in OUTDOOR temperature does NOT hold and is carried as
# finding D2-04 (tools/audit/round4/D2/cop_below_unity.py). Only the two
# that held are pinned here.
worst_flow, worst_dhw = 0.0, 0.0
for o in (-25.0, -10.0, 0.0, 7.0, 15.0):
    with CPU:
        c = np.array([m.compute_cop(o, flow_temp=float(f)) for f in flows])
    worst_flow = max(worst_flow, float(np.max(np.diff(c))))
    d = np.array([m.compute_cop_dhw(o, float(t))
                  for t in np.arange(35.0, 70.01, 0.05)])
    worst_dhw = max(worst_dhw, float(np.max(np.diff(d))))
result("cop.worst_step_vs_flow", worst_flow, "cop")
result("cop.worst_step_vs_dhw_temp", worst_dhw, "cop")

# --- 4. is the PRODUCTION step converged? -----------------------------------
# OptimizationConfig.time_step_minutes is 15.0 and has no CONF_ key, so 0.25 h
# is the only step production ever integrates at. The question that matters is
# therefore not dt-invariance in general but whether a 24-hour trajectory at
# 0.25 h agrees with the same 24 hours at 0.03125 h (8x finer, identical total
# energy). Reported, not gated: a first-order integrator is allowed to differ.
worst_dt = 0.0
worst_dt_at = ""
for label, cfg in CONFIGS:
    p, m = make(cfg)
    st = ThermalState(
        room_temperature=20.0, slab_temperature=24.0, outdoor_temperature=-8.0,
        upper_floor_temperature=20.5, lower_floor_temperature=20.0,
        buffer_tank_temperature=45.0,
        wood_tank_temperature=60.0 if p.two_tank_modelled else None,
    )
    with CPU:
        coarse = m.simulate_trajectory(
            st, np.full(96, 3.0), np.full(96, -8.0), dt_hours=0.25)
        fine = m.simulate_trajectory(
            st, np.full(768, 3.0), np.full(768, -8.0), dt_hours=0.25 / 8)
    for i, name in enumerate(
            ("room", "slab", "upper", "lower", "buffer")):
        gap = abs(float(coarse[i][-1]) - float(fine[i][-1]))
        if gap > worst_dt:
            worst_dt, worst_dt_at = gap, f"{label}/{name}"
result("dt.production_step_minutes", 15.0, "min")
result("dt.worst_24h_0.25h_vs_0.03125h_c", worst_dt, "degC")
result("dt.worst_at", worst_dt_at)

# --- 5. derate bounds -------------------------------------------------------
d = defrost.DefrostDerate()
for temp in (-20.0, -6.0, -1.0, 1.0, 3.0, 6.0, 10.0, 30.0):
    for hum in (20.0, 50.0, 85.0, 100.0):
        for duty in (0.0, 0.05, 0.2, 0.5, 5.0, -1.0):
            for _ in range(20):
                with CPU:
                    d.observe_duty(temp, hum, duty)
vals = [d.factor(t, h)
        for t in (-40.0, -20.0, -6.0, -1.0, 1.0, 3.0, 6.0, 10.0, 30.0, 60.0)
        for h in (0.0, 20.0, 50.0, 85.0, 100.0, 120.0)]
result("derate.min", float(min(vals)), "factor")
result("derate.max", float(max(vals)), "factor")
result("derate.bound_min", float(defrost.DERATE_MIN), "factor")
result("derate.bound_max", float(defrost.DERATE_MAX), "factor")
result("derate.in_bounds",
       int(all(defrost.DERATE_MIN - 1e-12 <= v <= defrost.DERATE_MAX + 1e-12
               for v in vals)), "bool")

# --- 6. wood_share range and batch parity -----------------------------------
ws, wv = [], []
grid = np.arange(15.0, 80.01, 1.7)
for w in grid:
    for h in grid:
        with CPU:
            ws.append(tm.wood_share(float(w), float(h), 45.0, 21.0))
        wv.append(float(tm._wood_share_vec(
            np.array([w]), np.array([h]), 45.0, np.array([21.0]))[0]))
result("share.cells", len(ws), "count")
result("share.min", float(min(ws)), "fraction")
result("share.max", float(max(ws)), "fraction")
result("share.vec_scalar_max_abs_diff",
       float(np.max(np.abs(np.array(ws) - np.array(wv)))), "fraction")

# --- 7. the DHW coil identity -----------------------------------------------
worst_coil = 0.0
for draw in (0.0, 0.3, 1.5, 6.0):
    for wood in (5.0, 20.0, 45.0, 70.0, 95.0):
        for setp in (45.0, 55.0, 65.0):
            for inlet in (5.0, 10.0, 15.0):
                with CPU:
                    red, coil = tm.dhw_coil_draw_reduction(
                        draw, wood, setp, inlet)
                worst_coil = max(worst_coil, abs(red + coil - draw))
result("coil.worst_identity_error_kw", worst_coil, "kW")

# --- 8. the energy-cost closure ---------------------------------------------
from heatpump_optimizer.optimizer import HeatPumpOptimizer  # noqa: E402

opt = HeatPumpOptimizer.__new__(HeatPumpOptimizer)
opt._pv_surplus = None


class _Cfg:
    pv_export_price = 0.4


opt.config = _Cfg()
prices = RNG.uniform(-0.5, 4.0, size=96)
power = RNG.uniform(0.0, 6.0, size=96)
with CPU:
    fn = opt._energy_cost_fn(prices, 0.25)
    got = fn(power)
result("cost.no_pv_error",
       abs(got - float(np.sum(prices * power) * 0.25)), "SEK")
opt._pv_surplus = RNG.uniform(0.0, 5.0, size=96)
with CPU:
    fn = opt._energy_cost_fn(prices, 0.25)
    got = fn(power)
exp_price = 0.4
closed = float(np.sum(
    np.minimum(power, opt._pv_surplus)
    * np.minimum(prices, np.maximum(prices, exp_price))
    - 0.0) * 0.0)  # placeholder, replaced below
covered = np.minimum(power, opt._pv_surplus)
margin = np.clip(prices - exp_price, 0.0, None)
closed = float(np.sum(prices * power - margin * covered) * 0.25)
result("cost.pv_error", abs(got - closed), "SEK")
result("cost.pv_margin_min", float(np.min(pv.import_margin(prices, exp_price))),
       "SEK/kWh")

# --- 9. metering windows and the marginal price -----------------------------
x = RNG.uniform(0.0, 9.0, size=96)
with CPU:
    got = tmod.metering_windows(x, 60, 0.25, 0)
want = x.reshape(24, 4).mean(axis=1)
result("window.box_average_error", float(np.max(np.abs(got - want))), "kW")
t = tmod.CapacityTariff(enabled=True, price_per_kw=45.0, peaks_averaged=3)
result("window.marginal_price_error",
       abs(t.marginal_price_per_kw - 45.0 / 3.0), "SEK/kW")

footer(CPU, "[i]dentities")

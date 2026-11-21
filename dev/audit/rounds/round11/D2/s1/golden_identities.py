#!/usr/bin/env python3
"""D2.M1 identities on every tests/golden.py SCENARIOS trajectory.

For each scenario the optimizer is run exactly as tests/golden.py:capture runs it, the
PUBLISHED call of ThermalModel.simulate_trajectory_with_dhw is recorded (its inputs are the
plan the golden fixture pins), and that call is replayed under instrumentation. Per scenario:

  energy-conservation  max |sum_i C_i dT_i - (Q_pump + Q_ext + Q_exo + gains - losses - refused)*dt|
                       over every (sub)step of ThermalModel._simulate_step_single/_two_zone, kWh;
                       the DHW tank's store_step balance and the refill coil's wood debit alike.
                       Tolerance 1e-9 kWh.
  dt-invariance        from each hour's replayed state with the hour's inputs held: max |4 x 15 min -
                       1 x 1 h| in K, and the integrator's order on the 2/4/8/16-steps-per-hour
                       sequence against a 256-step reference (first order: error halves with the
                       effective step dt/n_sub); a pair fails above 1.5x the effective-step ratio.
  power-monotone       at every step, +1 kW of space power (or -1 kW at the cap) re-simulated to the
                       horizon end through simulate_trajectory_with_dhw: count of (step, store, later
                       step) cells where the higher-power walk is colder by more than 1e-9 K; DHW
                       power alike on the DHW tank.
  store-bounds         every store of the fixture's recorded trajectories, the fresh capture's and
                       the replay's: buffer <= max(T0, buffer_max_temp) and >= min(T0, 20 C ambient,
                       coldest zone/outdoor); dhw in [min(inlet, ambient), max(T0, rating)]; wood in
                       [min(T0, inlet), max(T0, 95)]; zones in [min(T0, outdoor), hottest source].
  valve-reverse        (for D2-s1-02) emitter deliveries mixing_valve.emitter_delivery returned < 0 on
                       the replay, and the kWh they moved from a zone back into the tank.
  lift>1               (for D2-s1-01) ThermalModel.flow_lift_factor returns > 1 on the replay.
  measured-heat        (round-10 carry C1) the conservation and +1 kW monotonicity of
                       simulate_step with measured_heat_kw set (the batch twin has no such input).

Count keys: the states/ledgers the production seams return (simulate_step, the
_step_*_refused/_step_dhw_* ledgers, emitter_delivery's return value), never an input attribute.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s1/golden_identities.py
          [--only NAME[,NAME]] [--fix-lift] [--fix-emitter] [--fix-coil-clamp]
Perturbations (in memory): --fix-lift (D2-s1-01), --fix-emitter (D2-s1-02), see batch_parity.py.
Expected: printed per scenario; RESULT lines summarise. Tolerances as above.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B4 (4 vCPU container). Wall ~4 min (provisional).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import inspect  # noqa: E402
import json  # noqa: E402
from contextlib import ExitStack  # noqa: E402
from dataclasses import replace  # noqa: E402
from unittest import mock  # noqa: E402

import numpy as np  # noqa: E402

import golden  # noqa: E402
from heatpump_optimizer import mixing_valve  # noqa: E402
from heatpump_optimizer import thermal_model as TM  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, WeatherSeries  # noqa: E402
import batch_parity as BP  # noqa: E402

TOL_E = 1e-9
TOL_T = 1e-9
STORES = ("room_temperature", "slab_temperature", "upper_floor_temperature",
          "lower_floor_temperature", "buffer_tank_temperature", "wood_tank_temperature")

SIG_2Z = inspect.signature(ThermalModel._simulate_step_two_zone)
SIG_1Z = inspect.signature(ThermalModel._simulate_step_single)
ORIG_2Z = ThermalModel._simulate_step_two_zone
ORIG_1Z = ThermalModel._simulate_step_single
ORIG_DHW = ThermalModel.simulate_dhw_step
ORIG_COIL = ThermalModel.apply_dhw_coil
ORIG_EMIT = mixing_valve.emitter_delivery
ORIG_LIFT = ThermalModel.flow_lift_factor


class Ledger:
    def __init__(self):
        self.reset()

    def reset(self):
        self.space_max = 0.0
        self.space_worst = None
        self.space_n = 0
        self.dhw_max = 0.0
        self.dhw_n = 0
        self.coil_max = 0.0
        self.coil_n = 0
        self.emit_neg = 0
        self.emit_neg_kwh = 0.0
        self.emit_calls = 0
        self.lift_gt1 = 0
        self.lift_calls = 0
        self.cur_dt = 0.25
        self.armed = False


L = Ledger()


def _gains(m, two_zone, sol, hour):
    p = m.params
    q_int = m.internal_gains_at(hour) if hour is not None else p.internal_gains
    q_sol = sum(m.solar_gain_per_zone(sol)) if two_zone else m.compute_solar_gain(sol)
    return q_int + q_sol


def balance_2z(self, a, out_state):
    p = self.params
    s = a["state"]
    thr = mixing_valve.is_throttling(p.mixing_valve_mode)
    two_tank = thr and p.two_tank_modelled and s.wood_tank_temperature is not None
    cop = self.compute_cop(a["outdoor_temp"], humidity=a["humidity"],
                           flow_temp=s.buffer_tank_temperature if thr else None)
    mh = a["measured_heat_kw"]
    pump = cop * TM.heat_per_cop_kw(p, a["electrical_power"]) if mh is None else mh
    ext = max(0.0, a["external_heat_kw"])
    q_in = pump + ext + (a["buffer_exo_kw"] if thr and a["buffer_exo_kw"] else 0.0)
    u_up, u_lo = self._zone_loss(a["wind_speed"], a["precipitation"]) if a["_loss"] is None else a["_loss"]
    to = a["outdoor_temp"]
    loss = (u_up * (s.upper_floor_temperature - to) + u_lo * (s.lower_floor_temperature - to)
            + p.buffer_tank_heat_loss_coefficient * (s.buffer_tank_temperature - TM.TANK_ROOM_AMBIENT_TEMP))
    if two_tank:
        loss += p.wood_tank_heat_loss_coefficient * (s.wood_tank_temperature - TM.TANK_ROOM_AMBIENT_TEMP)
    gains = _gains(self, True, a["solar_radiation"], a["hour_of_day"])
    refused = self._step_buffer_refused + self._step_wood_refused
    dt = a["dt_hours"]
    lhs = (p.upper_floor_thermal_mass * (out_state.upper_floor_temperature - s.upper_floor_temperature)
           + p.lower_floor_thermal_mass * (out_state.lower_floor_temperature - s.lower_floor_temperature)
           + p.slab_thermal_mass * (out_state.slab_temperature - s.slab_temperature)
           + TM._buffer_capacity(p) * (out_state.buffer_tank_temperature - s.buffer_tank_temperature))
    if two_tank:
        lhs += p.wood_tank_thermal_mass * (out_state.wood_tank_temperature - s.wood_tank_temperature)
    return lhs - (q_in + gains - loss - refused) * dt


def balance_1z(self, a, out_state):
    p = self.params
    s = a["state"]
    thr = (p.mixing_valve_mode or mixing_valve.MODE_NONE) in mixing_valve.THROTTLING_MODES
    cop = self.compute_cop(a["outdoor_temp"], humidity=a["humidity"],
                           flow_temp=s.buffer_tank_temperature if thr else None)
    mh = a["measured_heat_kw"]
    pump = cop * TM.heat_per_cop_kw(p, a["electrical_power"]) if mh is None else mh
    q_in = pump + max(0.0, a["external_heat_kw"])
    u = self.effective_heat_loss_coefficient(p.heat_loss_coefficient, a["wind_speed"], a["precipitation"])
    loss = u * (s.room_temperature - a["outdoor_temp"])
    lhs = (p.room_thermal_mass * (out_state.room_temperature - s.room_temperature)
           + p.slab_thermal_mass * (out_state.slab_temperature - s.slab_temperature))
    refused = 0.0
    if thr:
        q_in += a["buffer_exo_kw"]
        loss += p.buffer_tank_heat_loss_coefficient * (s.buffer_tank_temperature - TM.TANK_ROOM_AMBIENT_TEMP)
        lhs += TM._buffer_capacity(p) * (out_state.buffer_tank_temperature - s.buffer_tank_temperature)
        refused = self._step_buffer_refused
    gains = _gains(self, False, a["solar_radiation"], a["hour_of_day"])
    return lhs - (q_in + gains - loss - refused) * a["dt_hours"]


def _record_space(r, a, out):
    L.space_n += 1
    if abs(r) > L.space_max:
        L.space_max = abs(r)
        L.space_worst = (float(a["electrical_power"]), float(a["outdoor_temp"]), float(a["dt_hours"]),
                         a["measured_heat_kw"], float(a["state"].buffer_tank_temperature))


def wrap_2z(self, *args, **kw):
    out = ORIG_2Z(self, *args, **kw)
    if L.armed:
        b = SIG_2Z.bind(self, *args, **kw)
        b.apply_defaults()
        _record_space(balance_2z(self, b.arguments, out), b.arguments, out)
    return out


def wrap_1z(self, *args, **kw):
    out = ORIG_1Z(self, *args, **kw)
    if L.armed:
        b = SIG_1Z.bind(self, *args, **kw)
        b.apply_defaults()
        _record_space(balance_1z(self, b.arguments, out), b.arguments, out)
    return out


def wrap_dhw(self, dhw_temp, dhw_power_thermal, hour_of_day, ambient_temp=TM.TANK_ROOM_AMBIENT_TEMP,
             dt_hours=0.25, draw_power=None, exo_kw=0.0, store=None):
    new = ORIG_DHW(self, dhw_temp, dhw_power_thermal, hour_of_day, ambient_temp, dt_hours, draw_power, exo_kw, store)
    if L.armed:
        st = self.params.dhw_store if store is None else store
        if st.capacity_kwh_per_c > 0:
            rhs = (dhw_power_thermal + exo_kw - self._step_dhw_draw_kw - st.ua_kw_per_c * (dhw_temp - ambient_temp)
                   - self._step_dhw_refused + self._step_dhw_floor_injected) * dt_hours
            r = st.capacity_kwh_per_c * (new - dhw_temp) - rhs
            L.dhw_n += 1
            L.dhw_max = max(L.dhw_max, abs(r))
    return new


def wrap_coil(self, state, draw_kw, dhw_temp, dt_hours):
    wood0 = state.wood_tank_temperature
    out = ORIG_COIL(self, state, draw_kw, dhw_temp, dt_hours)
    if L.armed and wood0 is not None:
        p = self.params
        _, q_coil = TM.dhw_coil_draw_reduction(draw_kw, wood0, p.dhw_setpoint, inlet_temp=p.dhw_inlet_reference)
        spared = q_coil * TM.dhw_draw_scale(dhw_temp, p.dhw_inlet_reference) if q_coil > 0 else 0.0
        r = p.wood_tank_thermal_mass * (state.wood_tank_temperature - wood0) + spared * dt_hours
        L.coil_n += 1
        L.coil_max = max(L.coil_max, abs(r))
    return out


def wrap_emit(*, mix_temp, zone_temp, ua):
    q = ORIG_EMIT(mix_temp=mix_temp, zone_temp=zone_temp, ua=ua)
    if L.armed:
        L.emit_calls += 1
        if q < 0:
            L.emit_neg += 1
            L.emit_neg_kwh += -q * L.cur_dt
    return q


def wrap_lift(self, outdoor_temp, flow_temp):
    f = ORIG_LIFT(self, outdoor_temp, flow_temp)
    if L.armed:
        L.lift_calls += 1
        if f > 1.0:
            L.lift_gt1 += 1
    return f


# ---------------------------------------------------------------------------

def capture_published(name, spec):
    """golden.capture(name, spec), recording every simulate_trajectory_with_dhw and
    simulate_trajectory call; the published one is the last call whose room trajectory the
    payload carries (a DHW-free plan publishes through simulate_trajectory)."""
    calls = []
    o_dhw = ThermalModel.simulate_trajectory_with_dhw
    o_sp = ThermalModel.simulate_trajectory

    def rec_dhw(self, *args, **kw):
        out = o_dhw(self, *args, **kw)
        calls.append((self, "dhw", args, dict(kw), out))
        return out

    def rec_sp(self, *args, **kw):
        out = o_sp(self, *args, **kw)
        calls.append((self, "space", args, dict(kw), out))
        return out

    err = None
    with mock.patch.object(ThermalModel, "simulate_trajectory_with_dhw", rec_dhw), \
            mock.patch.object(ThermalModel, "simulate_trajectory", rec_sp):
        try:
            payload = golden.capture(name, spec)
        except AssertionError as e:  # assert_invariants
            err = str(e)[:200]
            payload = None
    pub = None
    if payload is not None:
        room = np.asarray(payload["room_temp_trajectory"], float)
        for c in calls:
            if len(c[4][0]) == len(room) and np.allclose(np.round(c[4][0], 6), room, atol=2e-6):
                pub = c
    if pub is None:
        return payload, None, err
    model, kind, args, kw, _ = pub
    fn = ThermalModel.simulate_trajectory_with_dhw if kind == "dhw" else ThermalModel.simulate_trajectory
    b = inspect.signature(fn).bind(model, *args, **kw)
    b.apply_defaults()
    a = dict(b.arguments)
    a.pop("self")
    a["_kind"] = kind
    if kind == "space":
        a["space_power_schedule"] = a.pop("power_schedule")
        a["dhw_power_schedule"] = np.zeros(0)
    return payload, (model, a), err


def replay(model, a, space=None, dhw=None, end=None):
    """The published call again, optionally with another schedule; always the 7-tuple
    (room, slab, upper, lower, dhw or None, buffer, wood)."""
    kw = dict(a)
    kind = kw.pop("_kind")
    if space is not None:
        kw["space_power_schedule"] = space
    if kind == "space":
        kw.pop("dhw_power_schedule")
        kw["power_schedule"] = kw.pop("space_power_schedule")
        r = model.simulate_trajectory(**kw)
        return (r[0], r[1], r[2], r[3], None, r[4], r[6])
    if dhw is not None:
        kw["dhw_power_schedule"] = dhw
    kw["end_state"] = end
    kw["coil_wood_read"] = None
    return model.simulate_trajectory_with_dhw(**kw)


def per_step_states(model, a):
    """The replay's state entering each step (ThermalState objects), recorded at simulate_step."""
    states, inputs = [], []
    orig = ThermalModel.simulate_step

    def rec(self, *args, **kw):
        sig = inspect.signature(orig).bind(self, *args, **kw)
        sig.apply_defaults()
        d = dict(sig.arguments)
        d.pop("self")
        states.append(replace(d["state"]))
        inputs.append(d)
        return orig(self, *args, **kw)

    with mock.patch.object(ThermalModel, "simulate_step", rec):
        replay(model, a)
    return states, inputs


def dt_invariance(model, states, inputs):
    """4 x 15 min against 1 x 1 h, and the integrator's order, with the hour's inputs held.

    Reports max |4x15 min - 1x1 h| per store. The order is judged on the refinement sequence
    1, 2, 4, 8, 16 steps per hour against a 256-step reference: simulate_step subdivides a step
    for stability (_substeps_and_loss), so each level's effective step is (1/n)/n_sub, and first
    order means e(fine)/e(coarse) equals the ratio of effective steps. A pair fails when its
    normalised ratio exceeds 1.5; the error is the stores' heat-capacity-weighted
    sum sum_i C_i |x_i - x_ref| in kWh (judged where the coarse level's is over 1e-6 kWh), so one
    store's error crossing zero does not read as a lost order. A single 1 h step is not judged
    against 15 min alone: there the error can cross zero (seen at 1.6e-5 K against 6e-4 K)."""
    worst_ratio, worst_d, nonconv, blocks = 0.0, 0.0, 0, 0
    levels = (1, 2, 4, 8, 16)
    for k in range(0, len(states) - 3, 4):
        s0, inp = states[k], dict(inputs[k])
        inp.pop("state")
        inp.pop("dt_hours")

        def walk(n):
            s = replace(s0)
            for _ in range(n):
                s = model.simulate_step(s, dt_hours=1.0 / n, **inp)
            return s
        h = {n: (1.0 / n) / model._substeps_and_loss(inp["wind_speed"], inp["precipitation"], 1.0 / n)[0]
             for n in levels}
        w = {n: walk(n) for n in levels + (256,)}
        blocks += 1
        pp = model.params
        cap = {"room_temperature": pp.room_thermal_mass, "slab_temperature": pp.slab_thermal_mass,
               "upper_floor_temperature": pp.upper_floor_thermal_mass,
               "lower_floor_temperature": pp.lower_floor_thermal_mass,
               "buffer_tank_temperature": TM._buffer_capacity(pp),
               "wood_tank_temperature": pp.wood_tank_thermal_mass}
        if not pp.two_zone_enabled:
            cap["upper_floor_temperature"] = cap["lower_floor_temperature"] = 0.0
        e = {n: 0.0 for n in levels}
        for f in STORES:
            if getattr(w[1], f) is None:
                continue
            xr = getattr(w[256], f)
            worst_d = max(worst_d, abs(getattr(w[4], f) - getattr(w[1], f)))
            for n in levels:
                e[n] += cap[f] * abs(getattr(w[n], f) - xr)
        for c, fi in zip(levels[1:-1], levels[2:]):
            if e[c] > 1e-6:
                ratio = (e[fi] / e[c]) / (h[fi] / h[c])
                worst_ratio = max(worst_ratio, ratio)
                if ratio > 1.5:
                    nonconv += 1
    return blocks, worst_ratio, worst_d, nonconv


def power_monotone(model, a, base):
    p = model.params
    space = np.asarray(a["space_power_schedule"], float)
    dhw = np.asarray(a["dhw_power_schedule"], float)
    pmax = p.max_electrical_power
    viol, worst = 0, 0.0
    base_arr = [np.asarray(x, float) if x is not None else None for x in base]
    idx = {"room": 0, "slab": 1, "upper": 2, "lower": 3, "dhw": 4, "buffer": 5, "wood": 6}
    for i in range(len(space)):
        hi = space.copy()
        lo_arr = base_arr
        if space[i] + 1.0 <= pmax:
            hi[i] = space[i] + 1.0
        else:
            hi = space.copy()
            lo = space.copy()
            lo[i] = max(0.0, space[i] - 1.0)
            lo_arr = [np.asarray(x, float) if x is not None else None for x in replay(model, a, space=lo)]
        hi_arr = [np.asarray(x, float) if x is not None else None for x in replay(model, a, space=hi)]
        for key, j in idx.items():
            if hi_arr[j] is None or lo_arr[j] is None:
                continue
            d = lo_arr[j][i + 1:] - hi_arr[j][i + 1:]
            v = int((d > TOL_T).sum())
            if v:
                viol += v
                worst = max(worst, float(d.max()))
    dviol, dworst = 0, 0.0
    if a["_kind"] == "dhw" and len(dhw) and np.any(np.isfinite(dhw)):
        for i in range(len(dhw)):
            hi = dhw.copy()
            hi[i] = dhw[i] + 1.0
            hi_arr = replay(model, a, dhw=hi)
            d = base_arr[4][i + 1:] - np.asarray(hi_arr[4], float)[i + 1:]
            v = int((d > TOL_T).sum())
            if v:
                dviol += v
                dworst = max(dworst, float(d.max()))
    return viol, worst, dviol, dworst


def bounds(name, model, a, arrays, T0, outdoor):
    """Count of samples outside their store's physical bound, and the worst excursion (K)."""
    p = model.params
    thr = mixing_valve.is_throttling(p.mixing_valve_mode)
    room, slab, upper, lower, dhw, buf, wood = arrays
    zones = [np.asarray(x, float) for x in (room, slab, upper, lower) if x is not None and len(x)]
    zmin = np.minimum.reduce([z for z in zones]) if zones else None
    viol, worst, where = 0, 0.0, []
    omin = float(np.min(outdoor))

    def chk(label, arr, lo, hi):
        nonlocal viol, worst
        if arr is None or len(arr) == 0:
            return
        arr = np.asarray(arr, float)
        bad_nan = ~np.isfinite(arr)
        lo_v = np.maximum(0.0, lo - arr)
        hi_v = np.maximum(0.0, arr - hi)
        over = (lo_v > 1e-6) | (hi_v > 1e-6) | bad_nan
        if over.any():
            viol += int(over.sum())
            ex = float(np.nanmax(np.maximum(lo_v, hi_v))) if not bad_nan.all() else float("inf")
            worst = max(worst, ex)
            where.append(f"{label}:{int(over.sum())}@{int(np.argmax(over))}({ex:.3g}K)")

    b0 = T0["buffer_tank_temperature"]
    if buf is not None and len(buf):
        hi_b = max(b0, p.buffer_max_temp) if thr else max(b0, TM.TANK_ROOM_AMBIENT_TEMP)
        lo_b = min(b0, TM.TANK_ROOM_AMBIENT_TEMP, omin)
        chk("buffer", buf, lo_b, hi_b)
    if dhw is not None and len(dhw) and p.dhw_enabled:
        st = p.dhw_store
        chk("dhw", dhw, min(st.inlet_c, TM.TANK_ROOM_AMBIENT_TEMP, T0["dhw_temperature"]),
            max(T0["dhw_temperature"], st.rating_max_temp))
    if wood is not None and len(wood):
        w0 = T0["wood_tank_temperature"]
        chk("wood", wood, min(w0, p.dhw_inlet_reference, TM.TANK_ROOM_AMBIENT_TEMP), max(w0, TM.WOOD_TANK_MAX_TEMP))
    src = max(p.buffer_max_temp, b0) if thr else 75.0
    for lab, z, key in (("room", room, "room_temperature"), ("slab", slab, "slab_temperature"),
                        ("upper", upper, "upper_floor_temperature"), ("lower", lower, "lower_floor_temperature")):
        if z is None or len(z) == 0:
            continue
        chk(lab, z, min(T0[key], omin), max(T0[key], src))
    return viol, worst, where


def main():
    only = None
    for i, x in enumerate(sys.argv):
        if x == "--only":
            only = set(sys.argv[i + 1].split(","))
    names = [n for n in golden.SCENARIOS if only is None or n in only]
    tot = dict(econ_fail=0, econ_max=0.0, dhw_max=0.0, coil_max=0.0, dt_nonconv=0, dt_worst_ratio=0.0,
               dt_worst_d=0.0, mono_space=0, mono_space_worst=0.0, mono_dhw=0, mono_dhw_worst=0.0,
               bounds_fix=0, bounds_cap=0, bounds_rep=0, bounds_worst=0.0, emit_neg=0, emit_neg_kwh=0.0,
               lift_gt1=0, scen=0, mh_econ_max=0.0, mh_mono=0, published=0)
    per = {}
    with ExitStack() as stack:
        if "--fix-lift" in sys.argv:
            stack.enter_context(mock.patch.object(ThermalModel, "flow_lift_factor", BP.lift_fixed))
        if "--fix-emitter" in sys.argv:
            stack.enter_context(mock.patch.object(mixing_valve, "emitter_delivery", BP.emitter_fixed))
        global ORIG_EMIT, ORIG_LIFT
        ORIG_EMIT = mixing_valve.emitter_delivery
        ORIG_LIFT = ThermalModel.flow_lift_factor
        for name in names:
            spec = golden.SCENARIOS[name]
            payload, pub, err = capture_published(name, spec)
            tot["scen"] += 1
            fix = json.load(open(f"tests/golden/{name}.json"))
            if pub is None:
                print(f"{name}: NO PUBLISHED CALL (err={err})")
                continue
            tot["published"] += 1
            model, a = pub
            init = a["initial_state"]
            T0 = {f: getattr(init, f) for f in STORES + ("dhw_temperature",)}
            T0["wood_tank_temperature"] = T0["wood_tank_temperature"] if T0["wood_tank_temperature"] is not None else 0.0
            outdoor = np.asarray(a["weather"].outdoor_temps, float)
            L.reset()
            with mock.patch.object(ThermalModel, "_simulate_step_two_zone", wrap_2z), \
                    mock.patch.object(ThermalModel, "_simulate_step_single", wrap_1z), \
                    mock.patch.object(ThermalModel, "simulate_dhw_step", wrap_dhw), \
                    mock.patch.object(ThermalModel, "apply_dhw_coil", wrap_coil), \
                    mock.patch.object(mixing_valve, "emitter_delivery", wrap_emit), \
                    mock.patch.object(ThermalModel, "flow_lift_factor", wrap_lift):
                L.cur_dt = a["dt_hours"]
                L.kind = a["_kind"]
                L.armed = True
                base = replay(model, a)
                L.armed = False
            econ = (L.space_max, L.dhw_max, L.coil_max)
            emit = (L.emit_neg, L.emit_neg_kwh, L.emit_calls, L.lift_gt1, L.lift_calls)
            states, inputs = per_step_states(model, a)
            dt = dt_invariance(model, states, inputs)
            mono = power_monotone(model, a, base)
            # measured_heat_kw: the scalar step with a meter reading (C1)
            mh_max, mh_mono = 0.0, 0
            L.reset()
            with mock.patch.object(ThermalModel, "_simulate_step_two_zone", wrap_2z), \
                    mock.patch.object(ThermalModel, "_simulate_step_single", wrap_1z):
                L.armed = True
                for s, inp in zip(states, inputs):
                    d = dict(inp)
                    d.pop("state")
                    q = 0.5 + 0.8 * model.params.max_electrical_power * float(np.cos(len(d) + s.room_temperature)) ** 2
                    d["measured_heat_kw"] = q
                    lo = model.simulate_step(replace(s), **d)
                    d["measured_heat_kw"] = q + 1.0
                    hi = model.simulate_step(replace(s), **d)
                    for f in STORES:
                        x, y = getattr(lo, f), getattr(hi, f)
                        if x is not None and x - y > TOL_T:
                            mh_mono += 1
                L.armed = False
                mh_max = L.space_max
            # store bounds on three sources
            rep_arrays = base
            cap_arrays = None
            if payload is not None:
                cap_arrays = (payload["room_temp_trajectory"], payload["slab_temp_trajectory"],
                              payload["upper_temp_trajectory"], payload["lower_temp_trajectory"],
                              payload["dhw_temp_trajectory"], payload["buffer_temp_trajectory"],
                              payload["wood_temp_trajectory"])
            fix_arrays = (fix["room_temp_trajectory"], fix["slab_temp_trajectory"], fix["upper_temp_trajectory"],
                          fix["lower_temp_trajectory"], fix["dhw_temp_trajectory"], fix["buffer_temp_trajectory"],
                          fix["wood_temp_trajectory"])
            br = bounds(name, model, a, rep_arrays, T0, outdoor)
            bc = bounds(name, model, a, cap_arrays, T0, outdoor) if cap_arrays else (0, 0.0, [])
            bf = bounds(name, model, a, fix_arrays, T0, outdoor)
            per[name] = dict(econ=econ, dt=dt, mono=mono, emit=emit, mh=(mh_max, mh_mono),
                             bounds=(br[0], bc[0], bf[0]), err=err)
            print(f"{name:28s} econ[space={econ[0]:.2e} dhw={econ[1]:.2e} coil={econ[2]:.2e}] "
                  f"dt[blocks={dt[0]} worst_ratio={dt[1]:.3f} max|4x15-1h|={dt[2]:.3g}K nonconv={dt[3]}] "
                  f"mono[space={mono[0]}({mono[1]:.3g}K) dhw={mono[2]}({mono[3]:.3g}K)] "
                  f"bounds[rep={br[0]} cap={bc[0]} fix={bf[0]} worst={max(br[1], bc[1], bf[1]):.3g}K {' '.join(br[2] + bc[2])}] "
                  f"valve_reverse={emit[0]}/{emit[2]}({emit[1]:.3g}kWh) lift>1={emit[3]}/{emit[4]} "
                  f"mh[econ={mh_max:.2e} mono={mh_mono}]" + (f" ASSERT={err}" if err else ""), flush=True)
            tot["econ_max"] = max(tot["econ_max"], econ[0])
            tot["econ_fail"] += int(econ[0] > TOL_E or econ[1] > TOL_E or econ[2] > TOL_E)
            tot["dhw_max"] = max(tot["dhw_max"], econ[1])
            tot["coil_max"] = max(tot["coil_max"], econ[2])
            tot["dt_nonconv"] += dt[3]
            tot["dt_worst_ratio"] = max(tot["dt_worst_ratio"], dt[1])
            tot["dt_worst_d"] = max(tot["dt_worst_d"], dt[2])
            tot["mono_space"] += mono[0]
            tot["mono_space_worst"] = max(tot["mono_space_worst"], mono[1])
            tot["mono_dhw"] += mono[2]
            tot["mono_dhw_worst"] = max(tot["mono_dhw_worst"], mono[3])
            tot["bounds_rep"] += br[0]
            tot["bounds_cap"] += bc[0]
            tot["bounds_fix"] += bf[0]
            tot["bounds_worst"] = max(tot["bounds_worst"], br[1], bc[1], bf[1])
            tot["emit_neg"] += emit[0]
            tot["emit_neg_kwh"] += emit[1]
            tot["lift_gt1"] += emit[3]
            tot["mh_econ_max"] = max(tot["mh_econ_max"], mh_max)
            tot["mh_mono"] += mh_mono
    C.result("scenarios", tot["scen"])
    C.result("published_calls_found", tot["published"])
    C.result("econ_space_max_residual", f"{tot['econ_max']:.3e}", "kWh")
    C.result("econ_dhw_max_residual", f"{tot['dhw_max']:.3e}", "kWh")
    C.result("econ_coil_max_residual", f"{tot['coil_max']:.3e}", "kWh")
    C.result("econ_scenarios_failing_1e-9", tot["econ_fail"], "scenarios")
    C.result("dt_nonconvergent_cells", tot["dt_nonconv"], "cells")
    C.result("dt_worst_error_ratio_normalised", f"{tot['dt_worst_ratio']:.4f}")
    C.result("dt_worst_abs_4x15_vs_1h", f"{tot['dt_worst_d']:.4g}", "K")
    C.result("power_monotone_space_violations", tot["mono_space"], "cells")
    C.result("power_monotone_space_worst", f"{tot['mono_space_worst']:.4g}", "K")
    C.result("power_monotone_dhw_violations", tot["mono_dhw"], "cells")
    C.result("store_bounds_violations_replay", tot["bounds_rep"], "samples")
    C.result("store_bounds_violations_capture", tot["bounds_cap"], "samples")
    C.result("store_bounds_violations_fixture", tot["bounds_fix"], "samples")
    C.result("store_bounds_worst_excursion", f"{tot['bounds_worst']:.4g}", "K")
    C.result("valve_reverse_deliveries", tot["emit_neg"], "calls")
    C.result("valve_reverse_kwh", f"{tot['emit_neg_kwh']:.4g}", "kWh")
    C.result("flow_lift_factor_gt1_calls", tot["lift_gt1"], "calls")
    C.result("measured_heat_econ_max_residual", f"{tot['mh_econ_max']:.3e}", "kWh")
    C.result("measured_heat_monotone_violations", tot["mh_mono"], "cells")
    C.trailer()


if __name__ == "__main__":
    main()

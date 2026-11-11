#!/usr/bin/env python3
"""R10-COP-GATE item E (carries L1/L2, 8 and 9): the ventilation freeze.

Four arms, all through production symbols at the tree under test:

  cusum    drift.Cusum with the coordinator's constants (VENT_CUSUM_*),
           fed a synthetic 30-min residual series for 30 days x seeds:
             null     zero-mean noise only (the null control: must trip ~0)
             window   noise + an open window every 2nd evening (19:00, 3 h,
                      +k_vent kW/K air exchange at the interval's dT)
             ua_bias  noise + a heat-loss scale error f (true UA = model UA
                      x (1+f)) under a diurnal outdoor swing: the shape a
                      wrong learned scale (L2, 2.09) puts in the residual
           reports trips per 30 days and the share of tripped time.
  learners which learners stop when the vent latch is set: _learning_frozen
           per learner's own keys, plus the learner entry points
           (_fold_measured_cop, DhwProfileLearner.async_learn_dynamics,
           _async_learn_buffer_cooling, _run_system_identification).
           Null control: latch clear. Perturbation (mutant): a
           _learning_frozen that drops the vent branch must un-freeze each.
  latch    carry 9: latch on, a cycle of _update_current_state, then latch
           off and another cycle; the reason must read "ventilation" then None.

    PYTHONPATH=tests/hastub python3 r10_cop_gate_vent.py
"""
from __future__ import annotations

import asyncio
import math
import sys
from datetime import datetime, timedelta, timezone

sys.path[:0] = ["tests", "custom_components"]

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.drift import Cusum  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

P = ThermalParameters()
UA, C = P.heat_loss_coefficient, P.room_thermal_mass  # kW/K, kWh/K
DT_H = 0.5


def detector() -> Cusum:
    return Cusum(threshold=const.VENT_CUSUM_THRESHOLD_C, drift=const.VENT_CUSUM_DRIFT_C, side=-1,
                 clip=const.VENT_CUSUM_CLIP_C, reference_hours=const.VENT_CUSUM_REFERENCE_HOURS)


def run_cusum(sigma: float, *, window_k: float = 0.0, f: float = 0.0, seed: int = 0,
              days: int = 30, t_mean: float = 2.0, t_swing: float = 5.0, room: float = 21.0,
              front_k: float = 0.0):
    rng = np.random.default_rng(seed)
    d = detector()
    t0 = datetime(2026, 10, 1, tzinfo=timezone.utc)
    trips = tripped_n = 0
    n = int(days * 24 / DT_H)
    for i in range(n):
        when = t0 + timedelta(hours=i * DT_H)
        hour = when.hour + when.minute / 60
        outdoor = t_mean - t_swing * math.cos(2 * math.pi * (hour - 15) / 24)  # coldest ~03:00
        # A cold front: front_k K colder for two days in every ten, stepped in.
        if front_k and when.day % 10 in (3, 4):
            outdoor -= front_k
        dT = room - outdoor
        # Price-shaped heat, not dT-shaped: the planner shifts heat to cheap hours.
        heat_kwh = (3.0 if hour < 6 or 13 <= hour < 16 else 0.6) * DT_H
        r = rng.normal(0.0, sigma) - f * UA * dT * DT_H / C
        if window_k and (when.day % 2 == 0) and 19 <= hour < 22:
            r -= window_k * dT * DT_H / C
        if d.update(when, float(r), (heat_kwh, 0.0)) and d.tripped:
            trips += 1
        tripped_n += d.tripped
    return trips, tripped_n / n


def arm_cusum() -> list[str]:
    out = ["## cusum (trips / 30 d over 8 seeds: mean [min-max]; tripped share)"]
    def row(label, **kw):
        res = [run_cusum(seed=s, **kw) for s in range(8)]
        t = [r[0] for r in res]
        share = sum(r[1] for r in res) / len(res)
        out.append(f"{label:44s} trips={np.mean(t):5.2f} [{min(t)}-{max(t)}] tripped={share:6.1%}")
    for sigma in (0.05, 0.10, 0.15, 0.20):
        row(f"null sigma={sigma}", sigma=sigma)
    for sigma in (0.05, 0.10, 0.15):
        for k in (0.15, 0.30):
            row(f"window k={k}kW/K sigma={sigma} (15 events)", sigma=sigma, window_k=k)
    for sigma in (0.05, 0.10):
        for f in (0.5, 1.09, 2.0, -0.52):
            row(f"ua_bias f={f:+.2f} sigma={sigma}", sigma=sigma, f=f)
        row(f"ua_bias f=+1.09 swing=10 sigma={sigma}", sigma=sigma, f=1.09, t_swing=10.0)
        row(f"front 8K, f=0 (null for front) sigma={sigma}", sigma=sigma, front_k=8.0)
        for f in (0.5, 1.09):
            row(f"front 8K + ua_bias f=+{f:.2f} sigma={sigma}", sigma=sigma, f=f, front_k=8.0)
    return out


CFG = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
    "heat_pump_power_entity": "sensor.pump_power",
    "dhw_temp_entity": "sensor.dhw", "buffer_tank_temp_entity": "sensor.buffer",
    "heat_pump_max_power": 14.0, "heat_pump_min_power": 1.0,
}
STATES = {
    "sensor.indoor": FakeState("21.0", unit="°C"), "sensor.outdoor": FakeState("2.0", unit="°C"),
    "sensor.pump_power": FakeState("2200", unit="W"), "sensor.dhw": FakeState("50.0", unit="°C"),
    "sensor.buffer": FakeState("40.0", unit="°C"),
}


def coordinator():
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    return HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(data=dict(CFG)))


async def learner_outcomes(tripped: bool, mutant: bool) -> dict[str, str]:
    c = coordinator()
    c._vent_cusum.tripped = tripped
    if mutant:
        real = c._learning_frozen
        c._learning_frozen = lambda *k, **kw: (None if (r := real(*k, **kw)) == "ventilation" else r)
        c._dhw_learner._frozen = c._learning_frozen
    out = {}
    # COP: the guard's refusal code; anything past the freeze gate is "passes freeze".
    c._measured_power, c._current_action = 2.2, {"power": 2.1, "dhw_power": 0.0}
    code = c._fold_measured_cop(None)
    out["cop(_fold_measured_cop)"] = f"refused:{code}" if code == const_cop_frozen() else f"passes freeze ({code})"
    # The fixer's rows: the same fold with measured heat evidence, a counter
    # install (its span gate) and a measured flow heat.
    from heatpump_optimizer import heat_energy as _he
    _he.meter_of(c).counter = True
    code = c._fold_measured_cop(None)
    out["cop counter(_fold_measured_cop)"] = f"refused:{code}" if code == const_cop_frozen() else f"passes freeze ({code})"
    _he.meter_of(c).counter = False
    c._flow_bias.heat_output_kw = 2.2 * 3.0
    code = c._fold_measured_cop(None)
    out["cop flow-heat(_fold_measured_cop)"] = f"refused:{code}" if code == const_cop_frozen() else f"passes freeze ({code})"
    c._flow_bias.heat_output_kw = None
    # DHW: returns the freeze reason, or None when it ran.
    t0 = datetime.now(timezone.utc)
    await c._dhw_learner.async_learn_dynamics(50.0)
    c._dhw_learner.last_sample_time = t0 - timedelta(minutes=30)
    r = await c._dhw_learner.async_learn_dynamics(49.8)
    out["dhw(async_learn_dynamics)"] = f"frozen:{r}" if r else "runs"
    # Buffer: sets _learner_freeze_reason on a freeze.
    c._learner_freeze_reason = None
    await c._async_learn_buffer_cooling(40.0)
    out["buffer(_async_learn_buffer_cooling)"] = f"frozen:{c._learner_freeze_reason}" if c._learner_freeze_reason else "runs"
    # sysid: aborts an active experiment with the freeze reason.
    from heatpump_optimizer import sysid as _s
    c._sysid.phase = next(v for k, v in vars(_s).items() if k.startswith("PHASE_") and v not in (_s.PHASE_ABORTED,) and k not in ("PHASE_IDLE", "PHASE_DONE", "PHASE_COMPLETE"))
    try:
        active = c._sysid.active
    except Exception:  # noqa: BLE001
        active = None
    try:
        await c._run_system_identification(np.full(48, 1.0))
    except Exception as e:  # noqa: BLE001 - past the gate the experiment needs more state
        out["sysid(_run_system_identification)"] = f"passes freeze (raised {type(e).__name__})"
    else:
        res = c._sysid.result
        out["sysid(_run_system_identification)"] = (
            f"aborted:{res.reason}" if res is not None and res.reason == "ventilation"
            else f"passes freeze (later outcome {getattr(res, 'reason', None)!r}, active-before={active})")
    # The house learner's own keys, for the record.
    out["house(_learning_frozen keys)"] = str(c._learning_frozen("indoor_temp_entity", "outdoor_temp_entity"))
    return out


def const_cop_frozen():
    from heatpump_optimizer import coordinator as co
    return co.COP_REFUSED_FROZEN


async def arm_learners() -> list[str]:
    out = ["## learners on the vent latch (latch | null: latch clear | mutant: vent branch dropped)"]
    a, b, m = (await learner_outcomes(True, False), await learner_outcomes(False, False),
               await learner_outcomes(True, True))
    for k in a:
        out.append(f"{k:40s} {a[k]:34s} | {b[k]:30s} | {m[k]}")
    return out


async def arm_latch() -> list[str]:
    c = coordinator()
    seq = []
    for tripped in (True, True, False, False):
        c._vent_cusum.tripped = tripped
        await c._update_current_state()
        seq.append(f"latch={tripped}: learner_freeze_reason={c._learner_freeze_reason}")
    return ["## latch on-then-off (carry 9), consecutive _update_current_state cycles"] + seq


# --- round 2: the window through each lifted learner's production fold ---
from heatpump_optimizer import draw_range as _dr  # noqa: E402

OUT_C, ROOM_C = -10.0, 21.0          # outside the frost band (0..4 C), so no defrost gate
DESIGN_DT = 31.0                     # steady room-outdoor dT at OUT_C


def window_excess(k_vent: float, days: int = 30) -> list[float]:
    """Per 30-min interval, the fractional rise of the emitters' heat at a FIXED
    flow temperature: a first-order room (default UA, C) whose emitter UA is
    backed out of the steady load at ``emitter_design_delta_t``; an open window
    adds ``k_vent`` kW/K from 19:00 for 3 h every second day and the room then
    recovers on the same emitters. 0.0 everywhere for k_vent=0 (the null)."""
    q0 = UA * DESIGN_DT
    u_em = q0 / P.emitter_design_delta_t_floored
    t_flow = ROOM_C + q0 / u_em
    room, out = ROOM_C, []
    n = int(days * 24 / DT_H)
    for i in range(n):
        hour, day = (i * DT_H) % 24, int(i * DT_H // 24)
        k = k_vent if (day % 2 == 0 and 19 <= hour < 22) else 0.0
        for _ in range(30):                      # 1-min Euler steps
            q_em = u_em * (t_flow - room)
            room += (q_em - (UA + k) * (room - OUT_C)) * (1 / 60) / C
        out.append(u_em * (ROOM_C - room) / q0)  # delta = extra heat / nominal heat
    return out


def cop_coordinator():
    c = coordinator()
    st = getattr(c, "_ctx", c)._current_state
    st.outdoor_temperature = OUT_C
    cop = c._thermal_model.compute_cop(OUT_C)
    ask = UA * DESIGN_DT / cop
    c._current_action = {"power": ask, "dhw_power": 0.0}
    return c, ask, cop


def follows_draw(ask: float) -> "_dr.DrawRange":
    """A draw window whose evidence says the draw follows the ask."""
    d = _dr.DrawRange()
    rng = np.random.default_rng(7)
    for _ in range(_dr.MIN_SAMPLES + 12):
        a = ask * rng.choice((0.6, 1.0, 1.4))
        d.observe(a * (1 + rng.normal(0, 0.02)), a, P.min_electrical_power, P.max_electrical_power)
    return d


def run_cop(path: str, k_vent: float, seed: int, evidence: str) -> tuple[float, int, int]:
    """Feed 30 d of intervals through the production COP fold, latch clear.

    path: inferred   _fold_measured_cop, no heat reading (cop_evidence's inference)
          flow       _fold_measured_cop with a measured flow heat (_flow_bias.heat_output_kw)
          span       _fold_cop_evidence on counter deltas, as _async_learn_heat_span calls it
    The pump's true COP never changes: at a fixed flow the emitters take (1+d)
    times the heat and the compressor draws (1+d) times the power. Returns
    (final cop_scale, folds, folds inside a window-perturbed interval)."""
    c, ask, cop = cop_coordinator()
    rng = np.random.default_rng(seed)
    draw = follows_draw(ask) if evidence == "follows" else None
    folds = wfolds = 0
    for d in window_excess(k_vent):
        noise = rng.normal(0, 0.03)
        elec = ask * (1 + d) * (1 + noise)
        heat = cop * elec   # the true COP is the model's curve at scale 1, window or not
        c._measured_power = elec
        before = c._cop_samples
        if path == "span":
            c._flow_bias.heat_output_kw = None
            c._fold_cop_evidence(ask, elec, heat, c._cop_reference_curve((heat, None)))
        else:
            c._flow_bias.heat_output_kw = heat if path == "flow" else None
            c._fold_measured_cop(draw)
        if c._cop_samples != before:
            folds += 1
            wfolds += d > 0.005
    return c._cop_scale, folds, wfolds


def arm_cop_window() -> list[str]:
    out = ["## cop under a window, latch clear (cop_scale after 30 d; truth 1.000; 8 seeds mean [min-max]; folds; folds on an interval the window raised by >0.5 %)"]
    for path, ev in (("inferred", "none"), ("inferred", "follows"), ("flow", "none"), ("span", "none")):
        for k in (0.0, 0.15, 0.30):
            res = [run_cop(path, k, s, ev) for s in range(8)]
            sc = [r[0] for r in res]
            out.append(f"{path:8s} draw-evidence={ev:7s} k={k:.2f} scale={np.mean(sc):.3f} [{min(sc):.3f}-{max(sc):.3f}] "
                       f"folds={res[0][1]} window-folds={res[0][2]}")
    ex = window_excess(0.30)
    for k in (0.15, 0.30):
        ex = window_excess(k)
        out.append(f"(window k={k:.2f}: excess peak {max(ex):+.1%}, 30-d mean {np.mean(ex):+.2%}, intervals over COP_ASK_TOLERANCE {sum(e > 0.15 for e in ex)})")
    out.append(f"(window excess at k=0.30: peak {max(ex):+.1%}, mean over perturbed intervals {np.mean([e for e in ex if e > 0.005]):+.1%};"
               f" k=0.15 peak {max(window_excess(0.15)):+.1%})")
    return out


def run_draw(k_vent: float, seed: int):
    """draw_range.fold, frozen=False, on a price-shaped ask; the drawn kW is the
    ask times the window excess. Returns follows_ask, the log-log slope, engaged
    and planned() after 30 d."""
    d = _dr.DrawRange()
    rng = np.random.default_rng(seed)
    for i, e in enumerate(window_excess(k_vent)):
        hour = (i * DT_H) % 24
        ask = 2.4 if hour < 6 or 13 <= hour < 16 else (1.6 if 16 <= hour < 23 else 1.2)
        drawn = ask * (1 + e) * (1 + rng.normal(0, 0.03))
        _dr.fold(d, drawn, (ask, 0.0), P, frozen=False, distorted=False, defrost=False, command=None)
    pairs = np.array([(dd, a) for dd, a, _ in d._evidence()], dtype=float)
    la, ld = np.log(pairs[:, 1]), np.log(pairs[:, 0])
    la = la - la.mean()
    slope = float(np.dot(la, ld - ld.mean()) / np.dot(la, la))
    return _dr.follows_ask(d), slope, d.engaged, d.planned(P.min_electrical_power, P.max_electrical_power), d.observed()


def arm_draw_window() -> list[str]:
    out = ["## draw_range.fold under a window, frozen=False (8 seeds: slope mean [min-max]; follows; engaged; planned)"]
    for k in (0.0, 0.15, 0.30):
        res = [run_draw(k, s) for s in range(8)]
        sl = [r[1] for r in res]
        out.append(f"k={k:.2f} slope={np.mean(sl):.3f} [{min(sl):.3f}-{max(sl):.3f}] follows={sorted({str(r[0]) for r in res})} "
                   f"engaged={sorted({r[2] for r in res})} planned={sorted({str(r[3]) for r in res})} observed0={res[0][4]}")
    return out


async def run_buffer(g: float, k_vent: float) -> tuple[float, int]:
    """_async_learn_buffer_cooling on pump-off 30-min intervals, latch clear.
    The tank loses to its room (standby UA_s) and, with the circulation pump
    running, ``g`` kW/K into the emitters at the ROOM's temperature, which the
    window lowers. g=0 is the modelled no-valve topology (draw == pump heat)."""
    c = coordinator()
    c._current_action = {"power": 0.0, "dhw_power": 0.0}
    cbuf = P.buffer_tank_volume * 1.163 / 1000.0          # kWh/K
    ua_s = 0.04 * cbuf                                     # ~1 C/h at the 25 K reference
    q0 = UA * DESIGN_DT
    u_em = q0 / P.emitter_design_delta_t_floored
    ex = window_excess(k_vent)
    for i, e in enumerate(ex):
        room = ROOM_C - e * q0 / u_em
        tb0 = 45.0
        k = (ua_s + g) / cbuf                               # per hour
        t_inf = (ua_s * 20.0 + g * room) / (ua_s + g)
        tb1 = t_inf + (tb0 - t_inf) * math.exp(-k * DT_H)
        c._last_buffer_temp_sample = tb0
        c._last_buffer_sample_time = datetime.now(timezone.utc) - timedelta(hours=DT_H)
        c._buffer_heating_since_sample = False
        await c._async_learn_buffer_cooling(tb1)
    return c._buffer_cooling_rate, c._buffer_cooling_samples


async def arm_buffer_window() -> list[str]:
    out = ["## buffer cooling under a window, latch clear (learned C/h after 30 d; samples)"]
    for g in (0.0, 0.0005, 0.002):
        for k in (0.0, 0.30):
            r, n = await run_buffer(g, k)
            out.append(f"g={g:.4f}kW/K k={k:.2f} rate={r:.4f} samples={n}")
    return out


# --- round 3: the window through _fold_flow_lift (coordinator.py:878) ---
SPREAD_K = 5.0      # flow-return design spread; supply = mean water + spread/2


def room_series(k_vent: float, law: str, days: int = 30) -> list[tuple[float, float]]:
    """Per 30-min interval, (room degC, emitter heat kW) under a plant law.

    a   commanded heat: the emitters deliver the nominal hold heat q0 whatever
        the room does (the reviewer's law); a window cools the room and the
        room recovers only on the house's own constant.
    a2  sensitivity, not the rule: the plan replans each interval, asking q0
        plus C*(target-room)/6 h, capped at the nameplate heat.
    b   the curve held (round 2's model): the flow temperature is fixed, so
        supply is room-independent by construction (the null by construction).
    Same window as round 2: +k_vent kW/K from 19:00 for 3 h every second day."""
    q0 = UA * DESIGN_DT
    u_em = q0 / P.emitter_design_delta_t_floored
    t_flow = ROOM_C + q0 / u_em
    qmax = P.max_electrical_power * P.cop_nominal_floored
    room, out = ROOM_C, []
    for i in range(int(days * 24 / DT_H)):
        hour, day = (i * DT_H) % 24, int(i * DT_H // 24)
        k = k_vent if (day % 2 == 0 and 19 <= hour < 22) else 0.0
        if law == "a":
            q = q0
        elif law == "a2":
            q = min(q0 + C * max(ROOM_C - room, 0.0) / 6.0, qmax)
        for _ in range(30):
            if law == "b":
                q = u_em * (t_flow - room)
            room += (q - (UA + k) * (room - OUT_C)) * (1 / 60) / C
        out.append((room, q))
    return out


def flow_coordinator():
    c = coordinator()
    ctx = getattr(c, "_ctx", c)
    ctx._current_state.outdoor_temperature = OUT_C
    return c, ctx


def run_flow(law: str, k_vent: float, seed: int, *, latch: bool = False) -> tuple[float, float, float, float, int, float]:
    """30 d of cycles through the production _fold_flow_lift, latch clear.

    Supply under law a/a2: room + Q/UA_em + SPREAD_K/2, with UA_em the model's
    own (nameplate x COP_nominal / emitter_design_delta_t, the curve's), so the
    no-window supply sits SPREAD_K/2 above the curve. Under law b: the curve
    plus SPREAD_K/2. +-0.3 K sensor noise per sample. Returns (final bias_k,
    30-d mean, min, max, folds, curve)."""
    c, ctx = flow_coordinator()
    c._vent_cusum.tripped = latch
    p = c._thermal_model.params
    ua_em = p.max_electrical_power * p.cop_nominal_floored / p.emitter_design_delta_t_floored
    from heatpump_optimizer.flow_lift import curve_supply_temp
    from heatpump_optimizer.coordinator import _fold_flow_lift
    curve = curve_supply_temp(c._thermal_model, OUT_C, c.target_temperature)
    cop = c._thermal_model.compute_cop(OUT_C)
    rng = np.random.default_rng(seed)
    hist, folds = [], 0
    now = datetime.now(timezone.utc)
    for room, q in room_series(k_vent, law):
        supply = (curve if law == "b" else room + q / ua_em) + SPREAD_K / 2 + rng.normal(0, 0.3)
        c._current_action = {"power": q / cop, "dhw_power": 0.0}
        c._flow_bias.observe_temps(supply, None, None)
        before = c._flow_bias.samples
        _fold_flow_lift(c, now)
        folds += c._flow_bias.samples != before
        hist.append(c._flow_bias.bias_k)
    return hist[-1], float(np.mean(hist)), min(hist), max(hist), folds, curve


def arm_flow_window() -> list[str]:
    out = ["## _fold_flow_lift under a window, latch clear (bias_k K after 30 d; 8 seeds: final mean [min-max] | 30-d mean [min-max] | run min..max; folds)"]
    means = {}
    for law in ("a", "b", "a2"):
        for k in (0.0, 0.15, 0.30):
            res = [run_flow(law, k, s) for s in range(8)]
            fi, mn = [r[0] for r in res], [r[1] for r in res]
            means[law, k] = float(np.mean(mn))
            out.append(f"law={law:2s} k={k:.2f} final={np.mean(fi):+.3f} [{min(fi):+.3f}..{max(fi):+.3f}] "
                       f"mean={np.mean(mn):+.3f} [{min(mn):+.3f}..{max(mn):+.3f}] "
                       f"run={min(r[2] for r in res):+.3f}..{max(r[3] for r in res):+.3f} folds={res[0][4]}")
    for law in ("a", "a2"):
        for k in (0.15, 0.30):
            rs = room_series(k, law)
            out.append(f"(law {law} k={k:.2f}: room min {min(r for r, _ in rs):.2f} C, 30-d mean {np.mean([r for r, _ in rs]):.2f} C, last {rs[-1][0]:.2f} C)")
    c, _ = flow_coordinator()
    out.append(f"(curve at {OUT_C} C, target {c.target_temperature}: {run_flow('b', 0.0, 0)[5]:.2f} C; "
               f"latch set, law a k=0.30: folds={run_flow('a', 0.30, 0, latch=True)[4]})")
    # What a shift costs where it is priced: flow_lift_factor reads curve +
    # bias only above cop_flow_reference_temp, so price each arm's 30-d mean
    # shift (window minus its own no-window null) on plants at 25/40/50 C.
    m = c._thermal_model
    curve = m.curve_flow_temp(OUT_C)
    out.append(f"(priced at {OUT_C} C; cop_flow_reference_temp={m.params.cop_flow_reference_temp} C)")
    for plant in (25.0, 40.0, 50.0):
        b0 = plant - curve
        m.params.flow_curve_bias = b0
        f0 = m.flow_lift_factor(OUT_C, m.curve_flow_temp(OUT_C))
        row = []
        for law, k in (("a", 0.15), ("a", 0.30), ("a2", 0.15), ("a2", 0.30), ("b", 0.30)):
            d = means[law, k] - means[law, 0.0]
            m.params.flow_curve_bias = b0 + d
            f = m.flow_lift_factor(OUT_C, m.curve_flow_temp(OUT_C))
            row.append(f"{law}/{k:.2f} shift {d:+.3f} K factor {f / f0 - 1:+.2%}")
        out.append(f"(plant {plant:.0f} C, bias {b0:+.2f} K, factor {f0:.4f}: " + "; ".join(row) + ")")
    m.params.flow_curve_bias = 0.0
    return out


async def main() -> None:
    lines = (arm_cusum() + await arm_learners() + await arm_latch()
             + arm_cop_window() + arm_draw_window() + await arm_buffer_window()
             + arm_flow_window())
    print("\n".join(lines))


if __name__ == "__main__":
    asyncio.run(main())

"""D2 round-5 harness 2: per-step energy conservation, parity, dt-invariance.

METRIC DEFINITIONS
------------------
* ``cons_resid_<cell>`` — the per-step energy-balance residual of
  ``ThermalModel.simulate_step``, in kWh, closed over the modelled stores:

      resid = sum_s C_s*(T_s' - T_s)
              - (cop*P + ext + q_solar + q_internal
                 - q_buf_loss - q_wood_loss - q_loss_upper - q_loss_lower)*dt
              + refused_buf*dt

  where ``cop`` is the same COP the step itself used (recomputed from the
  pre-step state exactly as the step computes it), every loss is the step's
  own pre-step expression, and ``refused_buf`` is the step's own published
  ``_step_buffer_refused``.  With a correct, fully-booked step this is 0 to
  float rounding; the buffer-cap clamp is *added back* precisely because the
  tree books it, so a non-zero residual is un-booked heat, not a clamp.
  Reported as the max |resid| over the cell's steps and the cell's signed sum.
* ``cons_cells``   — how many (config, schedule) cells were measured.
* ``cons_unbooked_kwh`` — sum of |resid| over every cell, kWh: the total heat
  the model creates or destroys without saying so.
* ``parity_max_abs`` — max |scalar ``simulate_trajectory`` - scalar on the
  same row of ``simulate_trajectory_batch``| over every state field, degC.
  The tree's contract is bitwise, so the tolerance is 0.0.
* ``drift_1h_max``  — max |one 1-hour step - four 15-minute steps| over every
  state field, degC.  Explicit Euler is first order locally; the stated
  tolerance is the local truncation of the largest rate, 1 K/h.
* ``mono_wrong_<store>`` — count of (cell, step) pairs where raising that
  step's electrical power by +0.1 kW LOWERS that store's end-of-step
  temperature by more than 1e-9 K.
* ``bound_over_<name>`` — max amount by which a simulated store crosses a
  bound the tree itself states (``buffer_max_temp``, ``WOOD_TANK_MAX_TEMP``,
  ``dhw_hard_max_temp``), K.

COMMAND
-------
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D2/conservation.py

Expected: every ``cons_resid_*`` at or below 1e-9 kWh, ``parity_max_abs`` 0,
``drift_1h_max`` under 1 K, every ``mono_wrong_*`` zero and every
``bound_over_*`` zero.  Baseline eaa2a06af16a1b5b006f58a0f36cc92131f80225.
Machine: darwin arm64, 8-core M1, 8 GB.  ROOT RULE: root from ``__file__``
(four parents up).  HPO_PLANDATA is never touched: no Node harness is run.
"""
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "custom_components"))
sys.path.insert(0, str(ROOT / "tests"))

from heatpump_optimizer import thermal_model as TM  # noqa: E402
from heatpump_optimizer.mixing_valve import (  # noqa: E402
    MODE_NONE,
    THROTTLING_MODES,
)

VALVE = sorted(THROTTLING_MODES)[0]
DT = 0.25


def emit(name, value, unit):
    text = f"{value:.6g}" if isinstance(value, float) else str(value)
    print(f"RESULT {name}={text} {unit}", flush=True)


def build(two_zone, dhw, **over):
    p = TM.ThermalParameters(
        two_zone_enabled=two_zone,
        dhw_enabled=dhw,
    )
    p.dhw_windows = TM.parse_windows("06:00-08:30, 17:00-22:00")
    p.dhw_schedule_enabled = True
    for k, v in over.items():
        setattr(p, k, v)
    return p


def mkstate(p, T_buf=40.0, wood=None, dhw_t=50.0):
    return TM.ThermalState(
        room_temperature=21.0,
        slab_temperature=22.0,
        outdoor_temperature=0.0,
        upper_floor_temperature=21.0,
        lower_floor_temperature=21.0,
        buffer_tank_temperature=T_buf,
        dhw_temperature=dhw_t,
        wood_tank_temperature=wood,
    )


def store_masses(p, two_tank):
    out = {
        "upper": p.upper_floor_thermal_mass,
        "lower": p.lower_floor_thermal_mass,
        "slab": p.slab_thermal_mass,
    }
    C_buf = p.buffer_tank_thermal_mass
    if C_buf < 1e-6:
        C_buf = 0.04
    out["buffer"] = max(C_buf, 0.01)
    if two_tank:
        out["wood"] = max(p.wood_tank_thermal_mass, 0.01)
    return out


def predicted_delta(p, m, s, power, outdoor, wind, rain, solar, ext, dt):
    """The step's own heat-in minus heat-out, in kW, computed pre-step.

    ``ext`` is an input to the modelled system in BOTH two-tank and
    single-tank form -- in the two-tank branch it charges the wood tank
    (``dT_wood``'s ``ext`` term) rather than the buffer's ``thermal_power``,
    but it still enters the balance either way.
    """
    throttled = p.mixing_valve_mode in THROTTLING_MODES
    two_tank = throttled and p.two_tank_modelled and s.wood_tank_temperature is not None
    cop = m.compute_cop(
        outdoor,
        humidity=None,
        flow_temp=s.buffer_tank_temperature if throttled else None,
    )
    q_in = cop * power + max(0.0, ext)
    if p.two_zone_enabled:
        u_upper = m.effective_heat_loss_coefficient(
            p.upper_floor_heat_loss, wind, rain
        )
        u_lower = m.effective_heat_loss_coefficient(
            p.lower_floor_heat_loss_learned, wind * 0.5, rain * 0.5
        )
    else:
        u_eff = m.effective_heat_loss_coefficient(
            p.heat_loss_coefficient, wind, rain
        )
        u_upper = u_eff
        u_lower = 0.0
    q_out = 0.0
    if p.two_zone_enabled:
        q_out += p.buffer_tank_heat_loss_coefficient * (
            s.buffer_tank_temperature - 20.0
        )
    if two_tank:
        q_out += p.wood_tank_heat_loss_coefficient * (
            s.wood_tank_temperature - 20.0
        )
    if p.two_zone_enabled:
        q_out += u_upper * (s.upper_floor_temperature - outdoor)
        q_out += u_lower * (s.lower_floor_temperature - outdoor)
    else:
        q_out += u_upper * (s.room_temperature - outdoor)
    q_solar = m.compute_solar_gain(solar) if solar > 0 else 0.0
    q_int = p.internal_gains
    return (q_in + q_solar + q_int - q_out) * dt, cop


def conservation():
    outdoor = -6.0
    wind = 3.0
    rain = 0.5
    cases = [
        ("twz_valve_notank", dict(two_zone=True, dhw=False,
                                  mixing_valve_mode=VALVE,
                                  buffer_tank_volume=200.0), None),
        ("twz_valve_twotank", dict(two_zone=True, dhw=False,
                                   mixing_valve_mode=VALVE,
                                   buffer_tank_volume=200.0,
                                   wood_tank_configured=True,
                                   wood_tank_volume=500.0), 45.0),
        ("twz_twotank_cold", dict(two_zone=True, dhw=False,
                                  mixing_valve_mode=VALVE,
                                  buffer_tank_volume=200.0,
                                  wood_tank_configured=True,
                                  wood_tank_volume=500.0), 30.0),
        ("twz_valve_slabdirect", dict(two_zone=True, dhw=False,
                                      mixing_valve_mode=VALVE,
                                      buffer_tank_volume=200.0,
                                      topology_layout_override=(
                                          TM.TOPOLOGY_VALVE_UPPER_DIRECT_SLAB)),
         None),
        ("single_novalve", dict(two_zone=False, dhw=False), None),
    ]
    unbooked = 0.0
    cells = 0
    worst = 0.0
    worst_cell = "-"
    for name, over, wood in cases:
        p = build(over.pop("two_zone"), over.pop("dhw"), **over)
        m = TM.ThermalModel(p)
        two_tank = (p.mixing_valve_mode in THROTTLING_MODES
                    and p.two_tank_modelled and wood is not None)
        masses = store_masses(p, two_tank)
        for solar in (0.0, 400.0):
            for ext in (0.0, 5.0):
                s = mkstate(p, T_buf=40.0, wood=wood)
                tot = 0.0
                for step in range(12):
                    power = 1.0 if step % 3 else 6.0
                    s0 = s
                    want, _cop = predicted_delta(
                        p, m, s0, power, outdoor, wind, rain, solar, ext,
                        DT,
                    )
                    s = m.simulate_step(
                        s0, power, outdoor, wind, rain, solar, DT,
                        external_heat_kw=ext,
                    )
                    dE = 0.0
                    if p.two_zone_enabled:
                        dE += masses["upper"] * (
                            s.upper_floor_temperature - s0.upper_floor_temperature)
                        dE += masses["lower"] * (
                            s.lower_floor_temperature - s0.lower_floor_temperature)
                        dE += masses["buffer"] * (
                            s.buffer_tank_temperature - s0.buffer_tank_temperature)
                    else:
                        # single-zone: the room IS the store; upper/lower are
                        # copies of it, not independent masses.
                        dE += p.room_thermal_mass * (
                            s.room_temperature - s0.room_temperature)
                    dE += masses["slab"] * (
                        s.slab_temperature - s0.slab_temperature)
                    if two_tank:
                        dE += masses["wood"] * (
                            s.wood_tank_temperature - s0.wood_tank_temperature)
                    resid = dE - want + m._step_buffer_refused * DT
                    tot += resid
                    if abs(resid) > worst:
                        worst = abs(resid)
                        worst_cell = f"{name}/solar{solar}/ext{ext}/step{step}"
                cells += 1
                emit(f"cons_resid_{name}_s{int(solar)}_e{int(ext)}",
                     float(tot), "kWh")
                unbooked += abs(tot)
    emit("cons_cells", cells, "count")
    emit("cons_unbooked_kwh", float(unbooked), "kWh")
    emit("cons_worst_step_abs", float(worst), "kWh")
    emit("cons_worst_step_where", worst_cell, "label")


def dhw_conservation():
    """The DHW store's own balance, with the tree's own booked terms."""
    p = build(False, True, dhw_tank_volume=300.0, dhw_cooling_rate=0.35)
    m = TM.ThermalModel(p)
    unbooked = 0.0
    worst = 0.0
    for power in (0.0, 1.0, 3.0, 6.0):
        for h in (0.0, 7.0, 18.0):
            s = TM.ThermalState(dhw_temperature=50.0)
            cop = m.compute_cop_dhw(2.0, 50.0)
            q_draw = m.dhw_draw_rate(h)
            span = max(TM.DHW_MIXED_USE_TEMP - p.dhw_inlet_reference, 1e-6)
            q_draw_eff = q_draw * min(
                1.0, max(0.0, 50.0 - p.dhw_inlet_reference) / span
            )
            q_loss = p.dhw_tank_heat_loss_coefficient * (50.0 - TM.DHW_AMBIENT_TEMP)
            new = m.simulate_dhw_step(
                dhw_temp=50.0, dhw_power_thermal=cop * power, hour_of_day=h,
                dt_hours=DT,
            )
            C = p.dhw_tank_thermal_mass
            resid = (
                C * (new - 50.0)
                - (cop * power - q_draw_eff - q_loss) * DT
                + m._step_dhw_refused * DT
                - m._step_dhw_floor_injected * DT
            )
            unbooked += abs(resid)
            worst = max(worst, abs(resid))
    emit("dhw_cons_unbooked_kwh", float(unbooked), "kWh")
    emit("dhw_cons_worst_kwh", float(worst), "kWh")
    emit("dhw_floor_injected_max", float(m._step_dhw_floor_injected), "kW")


def parity():
    rng = np.random.default_rng(3)
    n = 24
    outdoor = 2.0 + rng.normal(0, 3, n)
    wind = rng.uniform(0, 8, n)
    rain = rng.uniform(0, 1, n)
    solar = np.clip(rng.uniform(0, 500, n), 0, None)
    ext = rng.uniform(0, 6, n)
    power = rng.uniform(0, 6, n)
    rows = []
    worst = 0.0
    for name, over, wood, kw in (
        ("valve_space", dict(two_zone=True, dhw=False,
                             mixing_valve_mode=VALVE,
                             buffer_tank_volume=200.0), None, {}),
        ("valve_wood", dict(two_zone=True, dhw=False,
                            mixing_valve_mode=VALVE,
                            buffer_tank_volume=200.0,
                            wood_tank_configured=True,
                            wood_tank_volume=500.0), 42.0,
         dict(external_heat_kw=ext)),
        ("valve_pv", dict(two_zone=True, dhw=False,
                          mixing_valve_mode=VALVE,
                          buffer_tank_volume=200.0), None, {}),
        ("single", dict(two_zone=False, dhw=False), None,
         dict(external_heat_kw=ext)),
    ):
        p = build(over.pop("two_zone"), over.pop("dhw"), **over)
        p.cop_flow_carnot = p.mixing_valve_mode in THROTTLING_MODES
        m = TM.ThermalModel(p)
        s = mkstate(p, T_buf=45.0, wood=wood)
        sc = m.simulate_trajectory(
            s, power, outdoor, wind, rain, solar, DT, **kw
        )
        bt = m.simulate_trajectory_batch(
            s, power.reshape(1, -1), outdoor, wind, rain, solar, DT, **kw
        )
        fields = {
            "room": sc[0], "slab": sc[1], "upper": sc[2], "lower": sc[3],
            "buffer": sc[4],
        }
        if sc[6] is not None:
            fields["wood"] = sc[6]
            fields["wood_b"] = bt["wood"][0]
        for key, arr in fields.items():
            if key.endswith("_b"):
                continue
            b = bt[key][0]
            d = float(np.max(np.abs(np.asarray(arr) - np.asarray(b))))
            rows.append((name, key, d))
            worst = max(worst, d)
        d = float(np.max(np.abs(sc[5] - bt["refused"][0])))
        worst = max(worst, d)
        rows.append((name, "refused", d))
    emit("parity_cells", len(rows), "count")
    emit("parity_max_abs", float(worst), "degC")
    bad = [f"{a}/{b}={c:.3e}" for a, b, c in rows if c != 0.0]
    emit("parity_nonzero_fields", len(bad), "count")
    if bad:
        emit("parity_first_nonzero", bad[0], "label")


def drift():
    p = build(True, False, mixing_valve_mode=VALVE, buffer_tank_volume=200.0)
    m = TM.ThermalModel(p)
    s = mkstate(p, T_buf=40.0)
    power = 3.0
    one = m.simulate_step(s, power, 0.0, 1.0, 0.0, 100.0, 1.0)
    four = s
    for _ in range(4):
        four = m.simulate_step(four, power, 0.0, 1.0, 0.0, 100.0, 0.25)
    worst = 0.0
    for f in ("room_temperature", "slab_temperature",
              "upper_floor_temperature", "lower_floor_temperature",
              "buffer_tank_temperature"):
        worst = max(worst, abs(getattr(one, f) - getattr(four, f)))
    emit("drift_1h_max", float(worst), "degC")


def monotone_and_bounds():
    """Power-up must not cool a store; no store crosses a stated bound."""
    rng = np.random.default_rng(5)
    cells = 0
    wrong = {k: 0 for k in ("upper", "lower", "slab", "buffer", "wood")}
    worst_drop = 0.0
    for mode in (MODE_NONE, VALVE):
        for wood in (None, 42.0, 60.0):
            p = build(
                True, False, mixing_valve_mode=mode, buffer_tank_volume=200.0,
                wood_tank_configured=wood is not None, wood_tank_volume=500.0,
            )
            p.cop_flow_carnot = mode in THROTTLING_MODES
            m = TM.ThermalModel(p)
            for T_buf in (25.0, 40.0, 55.0):
                for T_zone in (14.0, 21.0, 27.0):
                    for outdoor in (-15.0, -3.0, 6.0):
                        s = mkstate(p, T_buf=T_buf, wood=wood)
                        s = TM.replace(
                            s, upper_floor_temperature=T_zone,
                            lower_floor_temperature=T_zone,
                            slab_temperature=T_zone,
                        )
                        a = m.simulate_step(s, 0.5, outdoor, 2.0, 0.2, 200.0, DT)
                        b = m.simulate_step(s, 2.5, outdoor, 2.0, 0.2, 200.0, DT)
                        cells += 1
                        for key, f in (
                            ("upper", "upper_floor_temperature"),
                            ("lower", "lower_floor_temperature"),
                            ("slab", "slab_temperature"),
                            ("buffer", "buffer_tank_temperature"),
                        ):
                            d = getattr(b, f) - getattr(a, f)
                            if d < -1e-9:
                                wrong[key] += 1
                                worst_drop = min(worst_drop, d)
                        if wood is not None:
                            d = b.wood_tank_temperature - a.wood_tank_temperature
                            if d < -1e-9:
                                wrong["wood"] += 1
    emit("mono_cells", cells, "count")
    for k, v in wrong.items():
        emit(f"mono_wrong_{k}", v, "count")
    emit("mono_worst_drop", float(worst_drop), "K")

    # bounds, over a long golden-style trajectory
    over_buf = 0.0
    over_wood = 0.0
    p = build(True, False, mixing_valve_mode=VALVE, buffer_tank_volume=200.0,
              buffer_max_temp=70.0, wood_tank_configured=True,
              wood_tank_volume=500.0)
    m = TM.ThermalModel(p)
    s = mkstate(p, T_buf=68.0, wood=68.0)
    for _ in range(96):
        s = m.simulate_step(s, 6.0, -15.0, 2.0, 0.0, 0.0, DT,
                            external_heat_kw=8.0)
        over_buf = max(over_buf, s.buffer_tank_temperature - p.buffer_max_temp)
        over_wood = max(over_wood, s.wood_tank_temperature - TM.WOOD_TANK_MAX_TEMP)
    emit("bound_over_buffer_k", float(over_buf), "K")
    emit("bound_over_wood_k", float(over_wood), "K")

    p2 = build(False, True, dhw_tank_volume=300.0, dhw_setpoint=52.0,
               dhw_legionella_enabled=True, dhw_legionella_temp=60.0)
    m2 = TM.ThermalModel(p2)
    dhw = 20.0
    over_dhw = 0.0
    for i in range(96):
        dhw = m2.simulate_dhw_step(
            dhw_temp=dhw, dhw_power_thermal=m2.compute_cop_dhw(-15.0, dhw) * 6.0,
            hour_of_day=float(i % 24), dt_hours=DT,
        )
        over_dhw = max(over_dhw, dhw - p2.dhw_hard_max_temp)
        over_dhw = max(over_dhw, p2.dhw_inlet_reference - dhw)
    emit("bound_over_dhw_k", float(over_dhw), "K")


def main():
    t0 = time.monotonic()
    for fn in (conservation, dhw_conservation, parity, drift,
               monotone_and_bounds):
        try:
            fn()
        except Exception as err:
            emit(f"ERROR_{fn.__name__}", f"{type(err).__name__}:{err}", "label")
    import resource

    thread_cpu = time.thread_time()
    process_cpu = time.process_time()
    emit("process_cpu", f"{process_cpu:.3f}", "s")
    emit("thread_cpu", f"{thread_cpu:.3f}", "s")
    emit("thread_factor", f"{process_cpu / max(thread_cpu, 1e-9):.4f}", "ratio")
    try:
        emit("load1", f"{os.getloadavg()[0]:.2f}", "count")
    except OSError:
        emit("load1", "n/a", "count")
    emit("swapins", resource.getrusage(resource.RUSAGE_SELF).ru_majflt, "count")
    emit("wall", f"{time.monotonic() - t0:.2f}", "s")


if __name__ == "__main__":
    main()

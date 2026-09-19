"""D2 round-5 harness 1: the physical-identity sweep.

METRIC DEFINITIONS
------------------
* ``cons_err``      — per-step energy-conservation residual of the two-zone
  step, in kWh: |C_store*delta_T summed over stores - (delivered in - loss
  out)*dt|, where "delivered in" is the COP-weighted electrical input plus
  any external heat the step's own energy bound admitted, and "loss out" is
  every q_* leaving a store.  The model caps emitter draw, so the identity is
  evaluated against the model's OWN admitted flows, which is what a
  conservation check can mean for a clipped model.
* ``drift_1h_*``    — dt-invariance: max |one 1-hour step - four 15-minute
  steps| over all state fields, degrees C.  Explicit Euler on a linear system
  is O(dt) locally, so the tolerance is the local truncation of the largest
  rate: 1 K/h.
* ``parity_*``      — max abs difference between ``simulate_trajectory``
  (scalar) and ``simulate_trajectory_batch`` on the same row, degrees C.
  The tree's contract is bitwise, so the tolerance is 0.0.
* ``cop_mono_*``    — count of (outdoor, flow) grid pairs where
  ``compute_cop`` moves the WRONG way: down as outdoor rises, or up as flow
  rises.  Zero is the physical answer.
* ``derate_range``  — min/max of ``DefrostDerate.factor`` over a swept grid.
  Must lie in [DERATE_MIN, DERATE_MAX] = [0.5, 1.0].
* ``cost_err``      — |predicted_cost - sum(prices*P*dt - margin*min(P,surplus)*dt)|
  in currency units, over every golden scenario.  Zero to float rounding.

COMMAND
-------
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D2/identity_sweep.py

Expected: all ``*_err`` and ``*_max`` at or below their stated tolerance,
every ``*_wrong`` counter zero.  Baseline 9bcb7352cabb43b413f5e3ca41b6dda4e1ac6d69.
Machine: darwin arm64, 8-core M1, 8 GB.

ROOT RULE: the repository root is derived from ``__file__`` (four parents up),
never from the working directory, so a copy run elsewhere measures the tree it
lives in.
"""
import os

# Thread pin before any numpy import (tests/stress.py's rule).
for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from dataclasses import replace  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import golden  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel,
    ThermalParameters,
    ThermalState,
)
from heatpump_optimizer.defrost import (  # noqa: E402
    DERATE_MAX,
    DERATE_MIN,
    DefrostDerate,
)

RESULT = []


def emit(name, value, unit):
    RESULT.append((name, value, unit))
    print(f"RESULT {name}={value} {unit}", flush=True)


# ---------------------------------------------------------------------------
# 1. Energy conservation per step, two-zone, over a sweep of operating points.
# ---------------------------------------------------------------------------
def conservation_sweep():
    """Residual of the store-enthalpy identity on the model's own flows.

    The step's emitter delivery is clipped by an availability bound, so the
    only closed identity is: delta(enthalpy of all stores) *equals* the net
    heat the step's own arithmetic put into them.  That net is reconstructed
    here from the published inputs by re-deriving the same quantities the step
    derives; a mismatch means the step's update loses or invents heat.
    """
    worst = 0.0
    worst_where = ""
    cells = []
    for valve in ("off", "manual", "smart_write"):
        for t_out in (-20.0, -5.0, 2.0, 8.0):
            for p_el in (0.0, 1.5, 4.0):
                cfg = golden.house(two_zone=True, dhw=False)
                cfg["mixing_valve_mode"] = valve
                cfg["buffer_tank_volume"] = 750.0
                cfg["buffer_max_temperature"] = 70.0
                params = ThermalParameters.from_config(cfg)
                m = ThermalModel(params)
                st = ThermalState(
                    room_temperature=21.0,
                    slab_temperature=22.0,
                    outdoor_temperature=t_out,
                    upper_floor_temperature=21.0,
                    lower_floor_temperature=21.0,
                    buffer_tank_temperature=40.0,
                )
                # Trace the step by summing every q the step itself computes.
                # The step is deterministic; wrap it to capture the flows.
                after = m.simulate_step(st, p_el, t_out, dt_hours=0.25)
                ref = _replay_two_zone(m, st, p_el, t_out, 0.25)
                err = float(
                    abs(
                        _enthalpy(m, after)
                        - _enthalpy(m, st)
                        - ref["net_kwh"]
                    )
                )
                cells.append(err)
                if err > worst:
                    worst = err
                    worst_where = f"{valve}@{t_out}C/{p_el}kW"
    emit("cons_cells", len(cells), "count")
    emit("cons_max_err", f"{worst:.3e}", "kWh")
    emit("cons_worst_cell", worst_where, "label")


def _enthalpy(m, st):
    p = m.params
    return (
        p.upper_floor_thermal_mass * st.upper_floor_temperature
        + p.lower_floor_thermal_mass * st.lower_floor_temperature
        + p.slab_thermal_mass * st.slab_temperature
        + max(p.buffer_tank_thermal_mass, 0.01) * st.buffer_tank_temperature
    )


def _replay_two_zone(m, st, p_el, t_out, dt):
    """Heat (kWh) the step puts into the stores, from its own published flows.

    Re-derived so the harness does not simply mirror the step's algebra: the
    generator side is COP*P and the loss side is the loss the step applies.
    Emitter delivery cancels between the buffer and the zones, so only the
    boundary terms survive the store sum.
    """
    p = m.params
    cop = m.compute_cop(
        t_out,
        humidity=None,
        flow_temp=st.buffer_tank_temperature
        if _throttling(p) else None,
    )
    gen = cop * p_el
    q_buf_loss = p.buffer_tank_heat_loss_coefficient * (st.buffer_tank_temperature - 20.0)
    u_upper = m.effective_heat_loss_coefficient(p.upper_floor_heat_loss)
    u_lower = m.effective_heat_loss_coefficient(p.lower_floor_heat_loss_learned)
    q_loss_upper = u_upper * (st.upper_floor_temperature - t_out)
    q_loss_lower = u_lower * (st.lower_floor_temperature - t_out)
    return {
        "net_kwh": (
            gen - q_buf_loss - q_loss_upper - q_loss_lower
        )
        * dt
    }


def _throttling(p):
    from heatpump_optimizer import mixing_valve

    return mixing_valve.is_throttling(p.mixing_valve_mode)


# ---------------------------------------------------------------------------
# 2. dt-invariance: one hour in one step vs four quarter-hour steps.
# ---------------------------------------------------------------------------
def dt_invariance():
    worst = 0.0
    for valve in ("off", "manual"):
        cfg = golden.house(two_zone=True, dhw=False)
        cfg["mixing_valve_mode"] = valve
        cfg["buffer_tank_volume"] = 750.0
        params = ThermalParameters.from_config(cfg)
        m = ThermalModel(params)
        st = ThermalState(
            room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=-5.0,
            upper_floor_temperature=21.0, lower_floor_temperature=21.0,
            buffer_tank_temperature=40.0,
        )
        one = m.simulate_step(st, 2.0, -5.0, dt_hours=1.0)
        cur = st
        for _ in range(4):
            cur = m.simulate_step(cur, 2.0, -5.0, dt_hours=0.25)
        d = max(
            abs(one.upper_floor_temperature - cur.upper_floor_temperature),
            abs(one.lower_floor_temperature - cur.lower_floor_temperature),
            abs(one.slab_temperature - cur.slab_temperature),
            abs(one.buffer_tank_temperature - cur.buffer_tank_temperature),
            abs(one.room_temperature - cur.room_temperature),
        )
        worst = max(worst, d)
    emit("drift_1h_max", f"{worst:.6f}", "degC")


# ---------------------------------------------------------------------------
# 3. Scalar vs batch parity, every golden scenario, on the solved schedule.
# ---------------------------------------------------------------------------
def parity_sweep():
    worst = 0.0
    worst_name = ""
    cells = 0
    for name, spec in sorted(golden.SCENARIOS.items()):
        built = golden.make(**spec)
        opt = built["optimizer"]
        m = opt.model
        n = min(len(built["prices"]), 24)
        power = np.linspace(0.0, m.params.max_electrical_power, n)
        scal = m.simulate_trajectory(
            built["state"], power, built["outdoor"][:n],
            wind_speeds=built["wind"][:n],
            precipitation=built["rain"][:n],
            solar_radiation=built["solar"][:n],
            dt_hours=0.25,
        )
        batch = m.simulate_trajectory_batch(
            built["state"], power.reshape(1, n), built["outdoor"][:n],
            wind_speeds=built["wind"][:n],
            precipitation=built["rain"][:n],
            solar_radiation=built["solar"][:n],
            dt_hours=0.25,
        )
        pairs = [
            ("room", scal[0], batch["room"][0]),
            ("slab", scal[1], batch["slab"][0]),
            ("upper", scal[2], batch["upper"][0]),
            ("lower", scal[3], batch["lower"][0]),
            ("buffer", scal[4], batch["buffer"][0]),
        ]
        if scal[6] is not None and batch["wood"] is not None:
            pairs.append(("wood", scal[6], batch["wood"][0]))
        for _label, a, b in pairs:
            d = float(np.max(np.abs(np.asarray(a) - np.asarray(b))))
            cells += 1
            if d > worst:
                worst = d
                worst_name = f"{name}"
    emit("parity_cells", cells, "count")
    emit("parity_max_absdiff", f"{worst:.3e}", "degC")
    emit("parity_worst_scenario", worst_name or "-", "label")


# ---------------------------------------------------------------------------
# 4. COP monotonicity and derate bounds.
# ---------------------------------------------------------------------------
def cop_sweep():
    wrong_out = 0
    wrong_flow = 0
    cells = 0
    for valve in ("off", "manual"):
        cfg = golden.house(two_zone=True, dhw=True)
        cfg["mixing_valve_mode"] = valve
        cfg["flow_curve_cop_enabled"] = True
        params = ThermalParameters.from_config(cfg)
        m = ThermalModel(params)
        out_grid = np.arange(-30.0, 20.01, 0.5)
        flow_grid = np.arange(20.0, 75.01, 0.5)
        for flow in flow_grid:
            prev = None
            for t in out_grid:
                v = m.compute_cop(float(t), humidity=80.0, flow_temp=float(flow))
                if prev is not None and v < prev - 1e-12:
                    wrong_out += 1
                prev = v
                cells += 1
        for t in (-20.0, -7.0, 0.0, 5.0, 12.0):
            prev = None
            for flow in flow_grid:
                v = m.compute_cop(float(t), humidity=80.0, flow_temp=float(flow))
                if prev is not None and v > prev + 1e-12:
                    wrong_flow += 1
                prev = v
                cells += 1
    emit("cop_cells", cells, "count")
    emit("cop_wrong_outdoor", wrong_out, "count")
    emit("cop_wrong_flow", wrong_flow, "count")

    d = DefrostDerate()
    lo, hi = 1e9, -1e9
    for t in np.arange(-30.0, 20.01, 0.25):
        for h in np.arange(0.0, 100.01, 1.0):
            v = d.factor(float(t), float(h))
            lo = min(lo, v)
            hi = max(hi, v)
    emit("derate_min", f"{lo:.6f}", "ratio")
    emit("derate_max", f"{hi:.6f}", "ratio")
    emit("derate_in_band", int(lo >= DERATE_MIN - 1e-12 and hi <= DERATE_MAX + 1e-12), "bool")


def derate_continuity():
    """Band-edge continuity: the empty-grid factor is 1.0 everywhere."""
    d = DefrostDerate()
    worst = 0.0
    for t in np.arange(-30.0, 20.01, 0.25):
        for h in (0.0, 20.0, 40.0, 60.0, 80.0, 100.0, None):
            worst = max(worst, abs(d.factor(float(t), h) - 1.0))
    emit("derate_empty_max_dev", f"{worst:.3e}", "ratio")


# ---------------------------------------------------------------------------
# 5. predicted_cost identity over every golden scenario.
# ---------------------------------------------------------------------------
def cost_identity():
    worst = 0.0
    worst_name = ""
    cells = 0
    for name, spec in sorted(golden.SCENARIOS.items()):
        built = golden.make(**spec)
        opt = built["optimizer"]
        n = len(built["prices"])
        surplus = None
        if name in golden.PV_SCENARIOS:
            surplus = golden.pv_surplus_for(n, built["solar"])
        ext = None
        if name in golden.EXTERNAL_HEAT_SCENARIOS:
            ext = golden.external_heat_for(n)
        caps = None
        if name in golden.CAP_SCENARIOS:
            caps = np.full(n, opt.model.params.max_electrical_power * 0.6)
        res = opt.optimize(
            built["state"], built["prices"], built["outdoor"], built["wind"],
            built["rain"], built["solar"], golden.START, surplus=surplus,
            external_heat_kw=ext, power_caps_extra=caps,
        )
        total = np.asarray(res.power_schedule, dtype=float) + np.asarray(
            res.dhw_power_schedule, dtype=float
        )
        prices = np.asarray(built["prices"], dtype=float)
        dt = 0.25
        raw = float(np.sum(prices * total) * dt)
        if surplus is not None and np.any(np.asarray(surplus) > 1e-6):
            margin = np.clip(prices - opt.config.pv_export_price, 0.0, None)
            raw -= float(np.sum(margin * np.minimum(total, np.asarray(surplus))) * dt)
        err = abs(raw - float(res.predicted_cost))
        cells += 1
        if err > worst:
            worst = err
            worst_name = name
    emit("cost_cells", cells, "count")
    emit("cost_max_err", f"{worst:.3e}", "currency")
    emit("cost_worst_scenario", worst_name or "-", "label")


def main():
    t0 = time.monotonic()
    conservation_sweep()
    dt_invariance()
    cop_sweep()
    derate_continuity()
    parity_sweep()
    cost_identity()
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

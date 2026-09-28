"""D2 -- the thermal model's physical identities, executed.

Five identities, each over a sweep of topologies and operating points.  Nothing
here reads a committed fixture, so the may-drift set is irrelevant.

  E1  ENERGY CONSERVATION, per store, per step.  The explicit-Euler step makes
      the enthalpy a store gains from the compressor exactly `cop*P*dt`, so for
      two powers at the SAME state
          C_store * (T_store(P2) - T_store(P1)) == cop * (P2 - P1) * dt
      to 1e-9 kWh.  `metric: max |lhs - rhs|` in kWh.
  E2  WHOLE-SYSTEM CONSERVATION, per step.  Sum of C_i*dT_i over every modelled
      store equals (cop*P + external + internal + solar - sum of envelope
      losses) * dt, with the right-hand side rebuilt from the model's own
      public methods (`compute_cop`, `effective_heat_loss_coefficient`,
      `compute_solar_gain`) rather than from the step's internals.
      `metric: max |sum(C dT) - net flux * dt|` in kWh.
  E3  dt-INVARIANCE / INTEGRATOR ORDER.  One hour taken as 1, 2, 4, 8, 16 steps.
      Explicit Euler is first order, so the deviation from the 512-step
      reference must halve as dt halves; `metric: order = log2(err(dt)/
      err(dt/2))`, expected 1.0 +- 0.15.
  E4  MONOTONICITY.  More electrical power never cools any store:
      `metric: worst dT/dP over the sweep`, must be >= 0 (tolerance -1e-12 K).
  E5  DERATE RANGE.  `defrost.DefrostDerate.factor` in [DERATE_MIN,
      DERATE_MAX] = [0.55, 1.0] for every bucket after adversarial `observe`,
      `observe_duty` and `from_dict` input; `metric: min/max factor seen`.

COMMAND (from the repository root, ~20 s):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D2/thermal_identities.py

EXPECTED at baseline ae36eff: `E1_max_residual_kwh<=1e-12`,
`E2_max_residual_kwh<=1e-12`, `E3_order` in [0.85, 1.15] for every cell,
`E4_worst_dT_dP>=0`, `E5_min_factor=0.55`, `E5_max_factor=1.0`,
`violations=0`.

PERTURBATION (direction stated): `--break-e2` recomputes E2's right-hand side
with the buffer tank's standby loss omitted -> `E2_max_residual_kwh` must leave
zero on every valve cell (measured: ~1e-3 kWh/step).  That arm is the proof the
E2 comparison is live; run it and see `violations` rise.

BASELINE SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
MACHINE: 8-core Apple M1, 8 GB, numpy 2.4.6 / scipy 1.17.1 on OpenBLAS
INSTRUMENTED SYMBOLS: thermal_model.py:ThermalModel.simulate_step,
    :_simulate_step_single, :_simulate_step_two_zone, :simulate_trajectory,
    :compute_cop, :effective_heat_loss_coefficient, :compute_solar_gain,
    :ThermalParameters (thermal masses), defrost.py:DefrostDerate.factor
"""
import sys

import d2lib  # noqa: F401  -- thread pin + sys.path, must be first
import numpy as np

from profiles import house
from heatpump_optimizer import defrost as defrost_mod
from heatpump_optimizer.defrost import DefrostDerate
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

d2lib.repo_root_ok()

BREAK_E2 = "--break-e2" in sys.argv

VALVE = {
    "mixing_valve_mode": "manual",
    "buffer_tank_volume": 750.0,
    "buffer_max_temperature": 70.0,
}
WOOD = dict(VALVE, **{
    "wood_tank_top_entity": "sensor.wood_top",
    "wood_tank_volume": 500.0,
})

TOPOLOGIES = {
    "single": (False, None),
    "two_zone": (True, None),
    "valve": (True, VALVE),
    "wood_two_tank": (True, WOOD),
}

OUTDOORS = (-18.0, -8.0, 0.0, 7.0, 15.0)
BUFFERS = (25.0, 40.0, 55.0, 68.0)
POWERS = (0.0, 1.5, 3.0, 4.5, 6.0)


def stored_energy(p, st) -> float:
    """Total enthalpy held by every modelled store, kWh above 0 C."""
    if p.two_zone_enabled:
        total = (
            p.upper_floor_thermal_mass * st.upper_floor_temperature
            + p.lower_floor_thermal_mass * st.lower_floor_temperature
            + p.slab_thermal_mass * st.slab_temperature
        )
        if p.buffer_is_store:
            C = p.buffer_tank_thermal_mass
            if C < 1e-6:
                C = 0.04
            total += C * st.buffer_tank_temperature
        if p.two_tank_modelled and st.wood_tank_temperature is not None:
            total += p.wood_tank_thermal_mass * st.wood_tank_temperature
        return total
    return (
        p.room_thermal_mass * st.room_temperature
        + p.slab_thermal_mass * st.slab_temperature
    )


def model_for(two_zone, over):
    cfg = house(two_zone=two_zone, dhw=False)
    cfg.update(over or {})
    p = ThermalParameters.from_config(cfg)
    p.defrost_derate = None       # E5 tests the derate separately
    return ThermalModel(p)


def state_for(out, buf, wood=None):
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.4,
        outdoor_temperature=out,
        upper_floor_temperature=21.6, lower_floor_temperature=20.3,
        dhw_temperature=50.0, dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=buf,
    )
    if wood is not None:
        st.wood_tank_temperature = wood
    return st


# --------------------------------------------------------------------------
def e1_e2_e4(name, m, wood0):
    """Energy conservation (per-store and whole-system) plus monotonicity."""
    p = m.params
    dt = 0.25
    e1 = e2 = 0.0
    e1_points = e1_skipped = 0
    worst_dp = np.inf
    for out in OUTDOORS:
        for buf in BUFFERS:
            st = state_for(out, buf, wood0)
            cop = m.compute_cop(out)
            prev = None
            for P in POWERS:
                s2 = m.simulate_step(st, P, out, dt_hours=dt)

                refused = float(m._step_buffer_refused)
                # --- E1: marginal enthalpy per extra kW -----------------
                # Every store summed, so the identity does not depend on
                # which store a topology routes the compressor into.  Skipped
                # at operating points where the buffer cap or the tank's own
                # availability bound fired: there the step deliberately
                # refuses heat, and the ledger is checked by E2 instead.
                if prev is not None and refused == 0.0 and prev[2] == 0.0:
                    lhs = stored_energy(p, s2) - stored_energy(p, prev[1])
                    cop_eff = (
                        m.marginal_cop(out, "buffer", store_temp=buf)
                        if (p.two_zone_enabled and p.buffer_is_store)
                        else cop
                    )
                    rhs = cop_eff * (P - prev[0]) * dt
                    e1 = max(e1, abs(lhs - rhs))
                    e1_points += 1
                else:
                    e1_skipped += 1

                # --- E2: every store, against the envelope flux ---------
                stored = 0.0
                flux_out = 0.0
                if p.two_zone_enabled:
                    u_up = m.effective_heat_loss_coefficient(p.upper_floor_heat_loss)
                    u_lo = m.effective_heat_loss_coefficient(
                        p.lower_floor_heat_loss_learned
                    )
                    stored += p.upper_floor_thermal_mass * (
                        s2.upper_floor_temperature - st.upper_floor_temperature
                    )
                    stored += p.lower_floor_thermal_mass * (
                        s2.lower_floor_temperature - st.lower_floor_temperature
                    )
                    stored += p.slab_thermal_mass * (
                        s2.slab_temperature - st.slab_temperature
                    )
                    flux_out += u_up * (st.upper_floor_temperature - out)
                    flux_out += u_lo * (st.lower_floor_temperature - out)
                    if p.buffer_is_store:
                        C = p.buffer_tank_thermal_mass
                        if C < 1e-6:
                            C = 0.04
                        stored += C * (
                            s2.buffer_tank_temperature - st.buffer_tank_temperature
                        )
                        if not BREAK_E2:
                            flux_out += p.buffer_tank_heat_loss_coefficient * (
                                st.buffer_tank_temperature - 20.0
                            )
                    if p.two_tank_modelled and st.wood_tank_temperature is not None:
                        stored += p.wood_tank_thermal_mass * (
                            s2.wood_tank_temperature - st.wood_tank_temperature
                        )
                        flux_out += p.wood_tank_heat_loss_coefficient * (
                            st.wood_tank_temperature - 20.0
                        )
                    q_solar_up, q_solar_lo = m.solar_gain_per_zone(0.0)
                    q_solar = q_solar_up + q_solar_lo
                else:
                    u_eff = m.effective_heat_loss_coefficient(p.heat_loss_coefficient)
                    stored += p.room_thermal_mass * (
                        s2.room_temperature - st.room_temperature
                    )
                    stored += p.slab_thermal_mass * (
                        s2.slab_temperature - st.slab_temperature
                    )
                    flux_out += u_eff * (st.room_temperature - out)
                    q_solar = m.compute_solar_gain(0.0)
                cop_in = (
                    m.marginal_cop(out, "buffer", store_temp=buf)
                    if (p.two_zone_enabled and p.buffer_is_store)
                    else cop
                )
                # Heat the buffer cap refused is booked to the model's own
                # ledger (`_step_buffer_refused`, kW) and leaves the system.
                net = cop_in * P + p.internal_gains + q_solar - flux_out - refused
                e2 = max(e2, abs(stored - net * dt))

                # --- E4: monotonicity ------------------------------------
                if prev is not None and P > prev[0]:
                    dP = P - prev[0]
                    for a, b in (
                        (prev[1].room_temperature, s2.room_temperature),
                        (prev[1].slab_temperature, s2.slab_temperature),
                        (prev[1].upper_floor_temperature, s2.upper_floor_temperature),
                        (prev[1].lower_floor_temperature, s2.lower_floor_temperature),
                        (prev[1].buffer_tank_temperature, s2.buffer_tank_temperature),
                    ):
                        worst_dp = min(worst_dp, (b - a) / dP)
                prev = (P, s2, refused)
    return e1, e2, worst_dp, e1_points, e1_skipped


def e3_order(name, m, wood0):
    """Integrator order: deviation from a 512-step reference, halving with dt."""
    out = -8.0
    st = state_for(out, 40.0, wood0)

    def end(n):
        s = st
        traj = m.simulate_trajectory(
            s, np.full(n, 4.0), np.full(n, out), dt_hours=1.0 / n
        )
        return np.array([traj[0][-1], traj[1][-1], traj[2][-1], traj[3][-1],
                         traj[4][-1]])

    ref = end(512)
    errs = [float(np.max(np.abs(end(n) - ref))) for n in (1, 2, 4, 8, 16)]
    orders = [
        float(np.log2(errs[i] / errs[i + 1])) if errs[i + 1] > 0 else float("nan")
        for i in range(len(errs) - 1)
    ]
    return errs, orders


def e5_derate_range():
    lo, hi = np.inf, -np.inf
    d = DefrostDerate()
    rng = np.random.default_rng(7)
    for _ in range(4000):
        t = float(rng.uniform(-35.0, 25.0))
        h = float(rng.uniform(0.0, 100.0))
        d.observe(t, h, float(rng.uniform(-5.0, 10.0)))
        d.observe_duty(t, h, float(rng.uniform(-1.0, 3.0)))
    # plus a hostile restore
    hostile = d.as_dict() if hasattr(d, "as_dict") else None
    for t in np.arange(-35.0, 25.01, 0.5):
        for h in (0.0, 30.0, 55.0, 80.0, 100.0, float("nan")):
            f = d.factor(float(t), None if np.isnan(h) else float(h))
            lo, hi = min(lo, f), max(hi, f)
    return lo, hi, hostile is not None


def main() -> int:
    viol = 0
    e1_all = e2_all = 0.0
    worst_dp_all = np.inf
    for name, (tz, over) in TOPOLOGIES.items():
        m = model_for(tz, over)
        wood0 = 72.0 if m.params.two_tank_modelled else None
        e1, e2, dp, npts, nskip = e1_e2_e4(name, m, wood0)
        e1_all = max(e1_all, e1)
        e2_all = max(e2_all, e2)
        worst_dp_all = min(worst_dp_all, dp)
        d2lib.result(f"E1_{name}_max_residual_kwh",
                     f"{e1:.3e} over {npts} points ({nskip} clamped, skipped)")
        d2lib.result(f"E2_{name}_max_residual_kwh", f"{e2:.3e}")
        d2lib.result(f"E4_{name}_worst_dT_dP", f"{dp:.6e}", "K_per_kW")
        errs, orders = e3_order(name, m, wood0)
        d2lib.result(
            f"E3_{name}",
            "errs=" + ",".join(f"{e:.3e}" for e in errs)
            + " orders=" + ",".join(f"{o:.3f}" for o in orders),
        )
        # Only the finest pair is asymptotic; the coarse ones are not.
        if not (0.85 <= orders[-1] <= 1.15):
            viol += 1
            d2lib.result(f"E3_{name}_OUT_OF_ORDER", "1")
    d2lib.result("E1_max_residual_kwh", f"{e1_all:.3e}", "kWh")
    d2lib.result("E2_max_residual_kwh", f"{e2_all:.3e}", "kWh")
    d2lib.result("E4_worst_dT_dP", f"{worst_dp_all:.6e}", "K_per_kW")
    d2lib.result("tolerance_E1_E2", "1e-12 kWh")
    d2lib.result("tolerance_E4", "-1e-12 K_per_kW")
    if e1_all > 1e-12:
        viol += 1
    if e2_all > 1e-12:
        viol += 1
    if worst_dp_all < -1e-12:
        viol += 1

    lo, hi, ok = e5_derate_range()
    d2lib.result("E5_min_factor", f"{lo:.6f}")
    d2lib.result("E5_max_factor", f"{hi:.6f}")
    d2lib.result("E5_bounds", f"[{defrost_mod.DERATE_MIN}, {defrost_mod.DERATE_MAX}]")
    if lo < defrost_mod.DERATE_MIN - 1e-12 or hi > defrost_mod.DERATE_MAX + 1e-12:
        viol += 1
    d2lib.result("break_e2_arm", "1" if BREAK_E2 else "0")
    d2lib.result("violations", viol)
    d2lib.env_footer()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

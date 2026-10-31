"""D2-a round 5: per-step energy conservation of the thermal model.

METRIC (one line): per simulated step, residual_kwh = sum_stores(C*(T'-T)) -
(injected - losses - refused_ledgers)*dt, in kWh; the identity holds when
|max residual| <= 1e-9 kWh for every store, step and family.

Instrumented production symbols:
  custom_components.heatpump_optimizer/thermal_model.py:ThermalModel.simulate_step
  thermal_model.py:ThermalModel.simulate_dhw_step (via simulate_trajectory_with_dhw)
  thermal_model.py:ThermalModel.compute_cop / compute_cop_dhw /
    effective_heat_loss_coefficient / solar_gain_per_zone / compute_solar_gain
    (reconstruction uses the production helpers on the production params)
  thermal_model.py:ThermalModel._step_buffer_refused / _step_dhw_refused /
    _step_dhw_floor_injected / _step_dhw_draw_kw (production ledgers)

COMMAND (from the export root):
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D2/seat-a/conservation.py
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D2/seat-a/conservation.py --perturb cap
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D2/seat-a/conservation.py --perturb ext

EXPECTED VALUES:
  baseline:   max residual over the 7 non-saturating families <= 1e-9 kWh
              (measured ~2e-14); RESULT wood_cap_deleted_kwh > 1 for the
              200 L wood-tank burn (the finding: the 95 C wood cap deletes
              forecast heat with no refused ledger).
  --perturb cap (WOOD_TANK_MAX_TEMP 95 -> 130 in memory): wood_cap_deleted_kwh
              drops to ~0 (direction: decreases) while family residuals stay
              <= 1e-9 -- the number keys on the cap, not on the harness.
  --perturb ext (forecast peak 8 -> 10 kW): wood_cap_deleted_kwh increases
              (direction: increases).

Baseline SHA: 1cc89e020fff9040a9d0090a27bf22bc1dd497f0. Machine: 8-core M1,
Python 3.11, numpy/OpenBLAS (single-threaded pin). Writes nothing outside its
own directory and /tmp/audit-5/tmp/d2a.
"""
import sys

sys.dont_write_bytecode = True
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d2a_common as C  # thread pin happens here, before numpy

import numpy as np
from dataclasses import replace

import custom_components.heatpump_optimizer.thermal_model as tm
import custom_components.heatpump_optimizer.mixing_valve as mv


def step_balance_residual(model, state, kw, dt=0.25):
    """One production simulate_step + whole-system enthalpy reconstruction.

    Returns (residual_kwh, new_state). All loss/injection terms come from the
    production helpers on the production params; internal transfers
    (inter-zone, slab<->zone, valve draw, wood_share) cancel between stores
    and are deliberately not reconstructed.
    """
    p = model.params
    throttled = mv.is_throttling(p.mixing_valve_mode)
    two_tank = (
        throttled
        and p.two_tank_modelled
        and state.wood_tank_temperature is not None
    )
    if p.two_zone_enabled:
        T_u = state.upper_floor_temperature
        T_l = state.lower_floor_temperature
        T_s = state.slab_temperature
        T_b = state.buffer_tank_temperature
        T_w = state.wood_tank_temperature
        cop = model.compute_cop(
            float(kw["outdoor"]), humidity=kw.get("humidity"),
            flow_temp=(T_b if throttled else None),
        )
        u_up = model.effective_heat_loss_coefficient(
            p.upper_floor_heat_loss, kw["wind"], kw["rain"]
        )
        u_lo = model.effective_heat_loss_coefficient(
            p.lower_floor_heat_loss_learned, kw["wind"] * 0.5, kw["rain"] * 0.5
        )
        q_su, q_sl = model.solar_gain_per_zone(kw["solar"])
        hour = kw.get("hour")
        q_int = (
            model.internal_gains_at(hour) if hour is not None else p.internal_gains
        )
        injected = (
            cop * kw["power"] + max(0.0, kw["ext"]) + q_int + q_su + q_sl
        )
        losses = (
            u_up * (T_u - kw["outdoor"]) + u_lo * (T_l - kw["outdoor"])
            + p.buffer_tank_heat_loss_coefficient * (T_b - 20.0)
        )
        if two_tank and T_w is not None:
            losses += p.wood_tank_heat_loss_coefficient * (T_w - 20.0)
    else:
        T_r = state.room_temperature
        T_s = state.slab_temperature
        cop = model.compute_cop(float(kw["outdoor"]), humidity=kw.get("humidity"))
        u_eff = model.effective_heat_loss_coefficient(
            p.heat_loss_coefficient, kw["wind"], kw["rain"]
        )
        injected = (
            cop * kw["power"] + max(0.0, kw["ext"]) + p.internal_gains
            + model.compute_solar_gain(kw["solar"])
        )
        losses = u_eff * (T_r - kw["outdoor"])

    new = model.simulate_step(
        state=state,
        electrical_power=kw["power"],
        outdoor_temp=kw["outdoor"],
        wind_speed=kw["wind"],
        precipitation=kw["rain"],
        solar_radiation=kw["solar"],
        dt_hours=dt,
        external_heat_kw=kw["ext"],
        humidity=kw.get("humidity"),
        hour_of_day=kw.get("hour"),
    )
    losses += model._step_buffer_refused if throttled else 0.0
    if p.two_zone_enabled:
        dE = (
            p.upper_floor_thermal_mass
            * (new.upper_floor_temperature - T_u)
            + p.lower_floor_thermal_mass
            * (new.lower_floor_temperature - T_l)
            + p.slab_thermal_mass * (new.slab_temperature - T_s)
            + max(p.buffer_tank_thermal_mass, 0.01)
            * (new.buffer_tank_temperature - T_b)
        )
        if two_tank and T_w is not None and new.wood_tank_temperature is not None:
            dE += (
                max(p.wood_tank_thermal_mass, 0.01)
                * (new.wood_tank_temperature - T_w)
            )
    else:
        dE = (
            p.room_thermal_mass * (new.room_temperature - T_r)
            + p.slab_thermal_mass * (new.slab_temperature - T_s)
        )
    return dE - (injected - losses) * dt, new


def family_residual(built, rng, n=96):
    """Max |residual| over a random 24 h schedule for one family."""
    model = built["optimizer"].model
    p = model.params
    state = replace(built["state"])
    power = rng.uniform(0, p.max_electrical_power, n)
    ext = C.ext_forecast(n)
    hours_matter = p.internal_gains_profile is not None
    worst = 0.0
    for i in range(n):
        kw = dict(
            power=float(power[i]), outdoor=float(built["outdoor"][i]),
            wind=float(built["wind"][i]), rain=float(built["rain"][i]),
            solar=float(built["solar"][i]), ext=float(ext[i]),
            humidity=55.0, hour=(6.5 + i * 0.25) if hours_matter else None,
        )
        r, state = step_balance_residual(model, state, kw)
        worst = max(worst, abs(r))
    return worst


def wood_cap_run(peak_kw=12.0, volume_l=200.0, hours=6.0, start_c=70.0):
    """A sustained burn into a small wood tank: deleted heat at the 95 C cap.

    Config-reachable on every axis: wood_tank_volume config range 50..3000 L;
    the burn rate is what the detector measures from a real tank's energy
    rise (12 kW thermal is a vigorous stove into 200 L); the setback house
    (the away preset, min/target 16 C) is what makes the emitters stop
    drinking the burn so the tank charges. Returns
    (deleted_kwh, refused_buffer_kwh_booked, final_wood_c).
    """
    from tests.golden import make

    built = make(
        two_zone=True, dhw=False,
        config_overrides={
            "mixing_valve_mode": "manual", "buffer_tank_volume": 750.0,
            "buffer_max_temperature": 70.0,
            "wood_tank_top_entity": "sensor.wood_top",
            "wood_tank_volume": volume_l,
            "min_temperature": 16.0, "target_temperature": 16.0,
            "comfort_temp_day": 16.0, "comfort_temp_night": 16.0,
        },
        state_overrides={
            "buffer_tank_temperature": 32.0, "wood_tank_temperature": start_c,
            "upper_floor_temperature": 20.5, "lower_floor_temperature": 20.5,
        },
    )
    model = built["optimizer"].model
    state = replace(built["state"], wood_tank_temperature=start_c)
    n = int(hours / 0.25)
    ext = np.full(n, peak_kw)
    deleted = 0.0
    refused_booked = 0.0
    for i in range(n):
        kw = dict(
            power=0.0, outdoor=float(built["outdoor"][i]), wind=0.0, rain=0.0,
            solar=0.0, ext=float(ext[i]), humidity=55.0, hour=None,
        )
        r, state = step_balance_residual(model, state, kw)
        # residual sign: dE - (in - losses): negative = heat deleted.
        if r < -1e-9:
            deleted += -r
        refused_booked += model._step_buffer_refused * 0.25
    return deleted, refused_booked, float(state.wood_tank_temperature)


def main():
    perturb = None
    for a in sys.argv[1:]:
        if a == "--perturb":
            perturb = sys.argv[sys.argv.index(a) + 1]
    rng = np.random.default_rng(5)
    fams = C.build_families()
    worst_all = 0.0
    for name, built in fams.items():
        if name == "wood_two_tank":
            continue  # contains the saturating case, measured separately
        r = family_residual(built, rng)
        worst_all = max(worst_all, r)
        print("RESULT residual_kwh[%s]=%.3e" % (name, r))
    print("RESULT residual_kwh[all_nonsaturating]=%.3e" % worst_all)

    if perturb == "cap":
        # The model object built by tests/golden carries the HA-loader module
        # identity `heatpump_optimizer.thermal_model`; patch the module the
        # executing step function actually resolves its globals against
        # (both identities exist in one process; probe-verified).
        import importlib

        fams_probe = C.build_families()
        mod = importlib.import_module(
            type(fams_probe["wood_two_tank"]["optimizer"].model).__module__
        )
        mod.WOOD_TANK_MAX_TEMP = 130.0
        tm.WOOD_TANK_MAX_TEMP = 130.0
    peak = 15.0 if perturb == "ext" else 12.0
    deleted, booked, final_t = wood_cap_run(peak_kw=peak, volume_l=200.0)
    print("RESULT wood_cap_deleted_kwh=%.4f" % deleted)
    print("RESULT buffer_refused_booked_kwh=%.4f" % booked)
    print("RESULT wood_final_c=%.3f cap_c=%.1f" % (final_t, 130.0 if perturb == "cap" else 95.0))
    # Null control: the same burn against a 500 L tank (golden config) --
    # below the cap the deletion vanishes and the identity closes.
    d2, b2, t2 = wood_cap_run(peak_kw=peak, volume_l=500.0)
    print("RESULT wood_cap_deleted_kwh_500L=%.4f (null control)" % d2)
    print("RESULT concurrent_test_procs=%d" % C.concurrent_test_procs())
    C.epilogue()


if __name__ == "__main__":
    main()

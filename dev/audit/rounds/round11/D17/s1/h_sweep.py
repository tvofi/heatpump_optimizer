"""D17-s1 option sweep: does each option the options flow saves have an effect?

Metric: per option line of `enumerate.py d17-features --kind option` (after_save,
modbus_prefill.* and factory_reset.* excluded: h_flow.py owns those), whether
saving it through its real options-flow step to a non-default value, then a
restart (a fresh HeatPumpOptimizerCoordinator built from the saved entry) and one
full `_async_update_data` cycle with the solve inline, moves an observable
channel against the same arm saved at the form default:
  plan    = space_plan, dhw_plan, schedule, current_action, cost keys
  writes  = hass.services.calls (the actuator and notification writes)
  publish = every other key of the published data dict, except a key named
            exactly like the option (an echo of the saved value is not an effect)
Run in named states: weekday (Thu 2026-01-15 06:00 UTC), weekend
(Sat 2026-01-17 06:00 UTC); PV options also at noon; capacity-tariff options also
in 'peaks' (weekday with three 2.0 kW peaks recorded this month). Count key: the option is NOEFFECT when no channel
moves in any state. Prerequisites and states per option are read from the
option's own strings.json description, never from the implementation.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D17/s1/h_sweep.py [--only step.field ...]
Expected: RESULT options_examined=88, RESULT options_noeffect=21 (exact, a count; each is re-run
in its documented state by h_states.py)
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13 (shared container)
Perturbation: --perturb-ignore makes the coordinator read EntryConfig from entry.data
only (options dropped), so every option saved to entry.options becomes NOEFFECT:
options_noeffect goes up to options_examined minus the options the flow writes
to entry.data.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from datetime import datetime, timezone  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
from harness import FakeState  # noqa: E402

WEEKDAY = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
WEEKEND = datetime(2026, 1, 17, 6, 0, tzinfo=timezone.utc)
STATES = {"weekday": WEEKDAY, "weekend": WEEKEND}

PLAN_KEYS = ("space_plan", "dhw_plan", "schedule", "current_action", "predicted_cost",
             "total_cost", "dhw_cost", "space_cost", "baseline_cost", "predicted_savings")

AWAY = {"away_presence_entity": "person.me"}
AWAY_ST = {"person.me": "not_home"}
POWER = {"heat_pump_power_entity": "sensor.hp_power"}
POWER_ST = {"sensor.hp_power": FakeState("1500", unit="W")}
HOUSE = {"house_power_entity": "sensor.house_power"}
HOUSE_ST = {"sensor.house_power": FakeState("9000", unit="W")}
PEAK = {"peak_tariff_enabled": True}
PV = {"pv_enabled": True, "pv_peak_kw": 8.0}
ECL = {"ecl110_displace_set_topic": "ecl/displace"}
HC = {"heat_curve_displace_entity": "number.curve"}
HC_ST = {"number.curve": FakeState("0", attributes={"min": -10, "max": 10, "step": 0.5})}
MODE_ST = {"select.hp_mode": FakeState("heat", attributes={"options": ["heat", "dhw", "heat_dhw", "cool"]})}

# step.field -> (changed value, same-page extras, other-page prerequisites in options, states)
# A prerequisite is what the option's own description says it needs.
CASES = {
    "away.away_dhw_min_temperature": (45.0, {}, AWAY, AWAY_ST),
    "away.away_presence_entity": ("person.me", {}, {}, AWAY_ST),
    "away.away_temperature": (12.0, {}, AWAY, AWAY_ST),
    "away.holiday_calendar_entity": ("calendar.hol", {}, {"holiday_comfort_temp_day": 22.5,
                                     "holiday_comfort_temp_night": 20.5}, {"calendar.hol": "on"}),
    "entities_pump.dhw_hysteresis_entity": ("sensor.dhw_hyst", {}, {"dhw_temp_entity": "sensor.dhw"},
                                            {"sensor.dhw_hyst": FakeState("8", unit="K"), "sensor.dhw": "46"}),
    "entities_pump.heat_pump_backup_heater_entity": ("binary_sensor.backup", {}, POWER, {**POWER_ST, "binary_sensor.backup": "on"}),
    "entities_pump.heat_pump_capacity_limited_entity": ("binary_sensor.silent", {}, POWER, {**POWER_ST, "binary_sensor.silent": "on"}),
    "entities_pump.heat_pump_defrost_entity": ("binary_sensor.defrost", {}, POWER, {**POWER_ST, "binary_sensor.defrost": "on"}),
    "entities_pump.heat_pump_dhw_booster_entity": ("binary_sensor.booster", {}, POWER, {**POWER_ST, "binary_sensor.booster": "on"}),
    "entities_pump.heat_pump_fault_entity": ("binary_sensor.fault", {}, {}, {"binary_sensor.fault": "on"}),
    "entities_pump.heat_pump_mode_entity": ("select.hp_mode", {}, {}, {**MODE_ST, "select.hp_mode": FakeState("cool", attributes={"options": ["heat", "dhw", "heat_dhw", "cool"]})}),
    "entities_pump.heat_pump_online_entity": ("binary_sensor.online", {}, {}, {"binary_sensor.online": "off"}),
    "entities_pump.heat_pump_return_temp_entity": ("sensor.hp_return", {}, {}, {"sensor.hp_return": FakeState("30", unit="°C")}),
    "entities_pump.heat_pump_supply_temp_entity": ("sensor.hp_supply", {}, {}, {"sensor.hp_supply": FakeState("45", unit="°C")}),
    "entities_pump.pump_duty_mode": ("control", {"heat_pump_mode_entity": "select.hp_mode"}, {}, MODE_ST),
    "entities_pump.space_hysteresis_entity": ("sensor.sp_hyst", {}, {"space_setpoint_entity": "number.flow", "space_setpoint_unit": "flow",
                                              "pump_duty_mode": "control"},
                                              {"sensor.sp_hyst": FakeState("8", unit="K"), "number.flow": FakeState("35", attributes={"min": 20, "max": 60})}),
    "grid.peak_tariff_distinct_days": (False, PEAK, {}, {}),
    "grid.peak_tariff_enabled": (True, {}, {}, {}),
    "grid.peak_tariff_hours": ("07:00-19:00", {**PEAK, "peak_tariff_offpeak_factor": 0.5}, {}, {}),
    "grid.peak_tariff_months": ("Jun-Aug", PEAK, {}, {}),
    "grid.peak_tariff_offpeak_factor": (0.5, {**PEAK, "peak_tariff_hours": "07:00-19:00"}, {}, {}),
    "grid.peak_tariff_peaks_averaged": (1, PEAK, {}, {}),
    "grid.peak_tariff_price_per_kw": (150.0, PEAK, {}, {}),
    "grid.peak_tariff_weekdays_only": (True, {**PEAK, "peak_tariff_offpeak_factor": 0.0}, {}, {}),
    "grid.peak_tariff_window_minutes": ("15", PEAK, {}, {}),
    "grid_connection.fuse_guard_enabled": (True, {"main_fuse_amperes": 16}, HOUSE, HOUSE_ST),
    "grid_connection.main_fuse_amperes": (16, {}, HOUSE, HOUSE_ST),
    "grid_connection.main_fuse_phases": (1, {"main_fuse_amperes": 16, "fuse_guard_enabled": True}, HOUSE, HOUSE_ST),
    "grid_connection.peak_guard_enabled": (True, {}, {**PEAK, **HOUSE}, HOUSE_ST),
    "grid_connection.peak_guard_margin_kw": (2.5, {"peak_guard_enabled": True}, {**PEAK, **HOUSE}, HOUSE_ST),
    "grid_connection.silent_mode_power_fraction": (0.6, {"silent_mode_windows": "00:00-23:59"}, {}, {}),
    "grid_connection.silent_mode_windows": ("00:00-23:59", {"silent_mode_power_fraction": 0.6}, {}, {}),
    "grid_fees.contract_fixed_price": (0.9, {}, {}, {}),
    "grid_fees.dso_product": ("ellevio_villa_effekt_2026", {}, {}, {}),
    "grid_fees.grid_fee_entity": ("sensor.fee", {"grid_fee_mode": "entity"}, {}, {"sensor.fee": "0.5"}),
    "grid_fees.grid_fee_fixed": (0.3, {"grid_fee_mode": "rules", "grid_fee_rules": "06:00-22:00 = 0.25"}, {}, {}),
    "grid_fees.grid_fee_mode": ("rules", {"grid_fee_rules": "06:00-22:00 = 0.25"}, {}, {}),
    "grid_fees.grid_fee_rules": ("06:00-12:00 = 0.9", {"grid_fee_mode": "rules"}, {}, {}),
    "heat_curve.ecl110_command_topic": ("ecl/cmd", {}, {}, {}),
    "heat_curve.ecl110_displace_max": (2.0, ECL, {}, {}),
    "heat_curve.ecl110_displace_min": (-2.0, ECL, {}, {}),
    "heat_curve.ecl110_displace_set_topic": ("ecl/displace", {}, {}, {}),
    "heat_curve.ecl110_mqtt_qos": (0, ECL, {}, {}),
    "heat_curve.ecl110_mqtt_retain": (True, ECL, {}, {}),
    "heat_curve.ecl110_pid_time_constant_hours": (6.0, ECL, {}, {}),
    "heat_curve.ecl110_state_topic": ("ecl/state", ECL, {}, {}),
    "heat_curve.heat_curve_displace_entity": ("number.curve", {}, {}, HC_ST),
    "heat_curve.heat_curve_offset_band_k": (0.5, HC, {}, HC_ST),
    "heat_curve.heat_curve_persistent_band_k": (0.5, {**HC, "heat_curve_target_kind": "persistent"}, {}, HC_ST),
    "heat_curve.heat_curve_persistent_min_dwell_minutes": (600, {**HC, "heat_curve_target_kind": "persistent"}, {}, HC_ST),
    "heat_curve.heat_curve_persistent_writes_per_day": (0, {**HC, "heat_curve_target_kind": "persistent"}, {}, HC_ST),
    "heat_curve.heat_curve_target_kind": ("persistent", HC, {}, HC_ST),
    "hot_water_pumps.vvc_lead_minutes": (120, {"vvc_pump_entity": "switch.vvc"}, {}, {"switch.vvc": "off"}),
    "hot_water_pumps.vvc_pump_entity": ("switch.vvc", {}, {}, {"switch.vvc": "on"}),
    "learning.comfort_learning_enabled": (True, {}, {}, {}),
    "learning.debug_collect_enabled": (True, {}, {}, {}),
    "learning.price_prior_enabled": (False, {}, {}, {}),
    "learning.staleness_max_age_scale": (10.0, {}, {}, {}),
    "learning.staleness_watchdog_enabled": (False, {}, {}, {}),
    "learning.system_identification_enabled": (True, {}, {}, {}),
    "quick_setup.buffer_tank": (True, {}, {}, {}),
    "quick_setup.building_era": ("pre_1960", {}, {}, {}),
    "quick_setup.building_foundation": ("heated_basement", {}, {}, {}),
    "quick_setup.building_structure": ("masonry", {}, {}, {}),
    "quick_setup.dhw_tank": (False, {}, {}, {}),
    "quick_setup.heated_area_m2": (300.0, {}, {}, {}),
    "quick_setup.lower_floor_emitter": ("radiators", {}, {}, {}),
    "quick_setup.two_zone": (True, {}, {}, {}),
    "quick_setup.upper_floor_emitter": ("floor", {"two_zone": True}, {}, {}),
    "quick_setup.wood_buffer_tank": (True, {"wood_furnace": True, "wood_tank_top_entity": "sensor.wood_top"}, {}, {"sensor.wood_top": "80"}),
    "quick_setup.wood_furnace": (True, {}, {}, {}),
    "quick_setup.wood_tank_bottom_entity": ("sensor.wood_bot", {"wood_furnace": True, "wood_buffer_tank": True,
                                            "wood_tank_top_entity": "sensor.wood_top"}, {}, {"sensor.wood_top": "80", "sensor.wood_bot": "40"}),
    "quick_setup.wood_tank_top_entity": ("sensor.wood_top", {"wood_furnace": True, "wood_buffer_tank": True}, {}, {"sensor.wood_top": "80"}),
    "solar_pv.pv_enabled": (True, {"pv_peak_kw": 8.0}, {}, {}),
    "solar_pv.pv_export_price": (2.0, PV, {}, {}),
    "solar_pv.pv_export_price_entity": ("sensor.export", PV, {}, {"sensor.export": "2.0"}),
    "solar_pv.pv_peak_kw": (20.0, {"pv_enabled": True}, {}, {}),
    "solar_pv.pv_production_entity": ("sensor.pv_now", PV, {}, {"sensor.pv_now": FakeState("6000", unit="W")}),
    "solar_pv.pv_system_efficiency": (0.3, PV, {}, {}),
    "thermal_model.compressor_modulation": ("on_off", {}, {}, {}),
    "thermal_model.heat_pump_cop_nominal": (5.5, {}, {}, {}),
    "thermal_model.heat_pump_cop_partload_derate": (0.15, {}, {}, {}),
    "thermal_model.heat_pump_max_power": (1.5, {}, {}, {}),
    "thermal_model.heat_pump_min_power": (1.2, {}, {}, {}),
    "thermal_model.house_heat_loss_coefficient": (0.6, {}, {}, {}),
    "thermal_model.house_thermal_mass": (40.0, {}, {}, {}),
    "thermal_model.slab_heat_transfer": (0.05, {}, {}, {}),
    "thermal_model.slab_thermal_mass": (40.0, {}, {}, {}),
}
# Sun-dependent options measured at noon too (PV and solar sit at zero before dawn).
NOON_ARM = {"solar_pv.pv_enabled", "solar_pv.pv_export_price", "solar_pv.pv_export_price_entity",
            "solar_pv.pv_peak_kw", "solar_pv.pv_production_entity", "solar_pv.pv_system_efficiency"}
NOON = datetime(2026, 1, 15, 11, 0, tzinfo=timezone.utc)
FLOW_OWNED = ("modbus_prefill.", "factory_reset.")


def seed_peaks(coord):
    """A month with three recorded 2.0 kW peaks: the capacity term is off until a peak is recorded."""
    t = coord._peak_tracker
    t.month, t.peaks, t.peak_days = "2026-01", [2.0, 2.0, 2.0], ["2026-01-10", "2026-01-11", "2026-01-12"]


# Capacity-tariff options, measured also in the 'peaks' state (weekday, history seeded).
PEAK_ARM = {i for i in CASES if i.startswith("grid.")} | {
    "grid_connection.peak_guard_enabled", "grid_connection.peak_guard_margin_kw", "grid_fees.dso_product"}


def universe():
    out = subprocess.check_output([sys.executable, "tools/audit/enumerate.py", "d17-features", "--kind", "option"],
                                  text=True)
    return [l.split()[1] for l in out.splitlines()]


def canon(o):
    return json.loads(json.dumps(o, default=str, sort_keys=True,
                                 allow_nan=True).replace("NaN", "null"), parse_float=lambda s: round(float(s), 6))


def run_arm(step, field, value, same, pre, states, now, perturb, seed=None):
    async def save():
        if value is rig_DEFAULT:
            return await rig.save_option(step, None, None, options=pre, extra=same)
        return await rig.save_option(step, field, value, options=pre, extra=same)
    res, entry = asyncio.run(save())
    if perturb:
        entry.options = {}
    hass, coord = rig.build_coord(entry, states=states, now=now, seed=seed)
    data = rig.run_cycles(coord, 1)
    stored = {**entry.data, **entry.options}
    return res, stored, data, list(hass.services.calls)


rig_DEFAULT = object()


def fingerprint(data, calls, field, volatile):
    d = {k: v for k, v in data.items() if k not in volatile}
    plan = canon({k: d.get(k) for k in PLAN_KEYS})
    pub = canon({k: v for k, v in d.items() if k not in PLAN_KEYS and k != field})
    return plan, canon(calls), pub


def main(argv):
    only = [a for a in argv if not a.startswith("--")]
    perturb = "--perturb-ignore" in argv
    uni = [u for u in universe() if not u.endswith(".after_save") and not u.startswith(FLOW_OWNED)]
    missing = [u for u in uni if u not in CASES]
    # volatile keys: two identical default arms disagree on them
    _, _, a, _ = run_arm("tuning", None, rig_DEFAULT, {}, {}, {}, WEEKDAY, False)
    _, _, b, _ = run_arm("tuning", None, rig_DEFAULT, {}, {}, {}, WEEKDAY, False)
    volatile = {k for k in set(a) | set(b) if canon(a.get(k)) != canon(b.get(k))} | {
        "last_optimization", "next_optimization", "solve_time_ms"}
    print("volatile:", sorted(volatile))
    rows, noeffect, nosave = [], [], []
    for item in uni:
        if only and item not in only:
            continue
        if item not in CASES:
            continue
        step, field = item.split(".")
        value, same, pre, states = CASES[item]
        moved = {}
        saved = None
        nows = dict(STATES)
        if item in NOON_ARM:
            nows["noon"] = NOON
        if item in PEAK_ARM:
            nows["peaks"] = WEEKDAY
        for sname, now in nows.items():
            seed = seed_peaks if sname == "peaks" else None
            res0, st0, d0, c0 = run_arm(step, field, rig_DEFAULT, same, pre, states, now, perturb, seed)
            res1, st1, d1, c1 = run_arm(step, field, value, same, pre, states, now, perturb, seed)
            saved = (res1.get("type"), res1.get("step_id"), res1.get("errors"),
                     st1.get(field, "<absent>"))
            f0, f1 = fingerprint(d0, c0, field, volatile), fingerprint(d1, c1, field, volatile)
            ch = [n for n, x, y in zip(("plan", "writes", "publish"), f0, f1) if x != y]
            if ch:
                pubdiff = sorted(k for k in f1[2] if f0[2].get(k) != f1[2].get(k))
                moved[sname] = ch + ([f"keys={pubdiff[:8]}"] if "publish" in ch else [])
        verdict = "EFFECT" if moved else "NOEFFECT"
        if not moved:
            noeffect.append(item)
        if saved[2]:
            nosave.append(item)
        rows.append(item)
        print(f"ROW {item} {verdict} saved={saved} moved={moved}", flush=True)
    print(f"RESULT options_universe={len(uni)}")
    print(f"RESULT options_examined={len(rows)}")
    print(f"RESULT options_without_case={len(missing)} {missing}")
    print(f"RESULT options_noeffect={len(noeffect)}")
    print(f"RESULT options_save_refused={len(nosave)} {nosave}")
    print("NOEFFECT", " ".join(noeffect))
    print(f"RESULT thread_factor={rig.thread_factor()}")
    print(f"RESULT load1={rig.load1()}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main(sys.argv[1:])

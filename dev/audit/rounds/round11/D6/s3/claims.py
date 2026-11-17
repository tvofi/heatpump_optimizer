#!/usr/bin/env python3
"""D6-s3 claim register: one executed check per registered claim of the seat's
cells (custom_components/heatpump_optimizer/translations/en.json and *.py),
each against the production code deciding the behaviour, never a comment.

Metric (one line): per registered claim, the value the production symbol
delivers (a constant, a rendered config/options form, a parser's verdict, a
called function) against the value the sentence states; verdict true/false.

Run (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s3/claims.py [--perturb]
It prints one `CHECK` line per claim and RESULT counts, and writes
dev/audit/rounds/round11/D6/s3/claims.json (the rows ledger.py turns into the
text_ledger.py ledger).

Expected on the export audited (box B3, linux): RESULT rules=109,
claims_checked=139, claims_false=2 (the wood packing ratio, D6-s3-02, harness
wood_packing_ratio.py; the device pre-fill description's refusal render,
D6-s3-01, harness prefill_placeholders.py), every other registered claim
true; exact. --perturb swaps const.DHW_MIN_TEMP_SETPOINT_MARGIN to 4.0 in
memory -> claims_false rises by the two dhw_min_too_close sentences (4).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (the export differs from it in
wood_fuel.py's birch row; see wood_packing_ratio.py).

Instrumented symbols: each CHECK line names its own (module:symbol).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import json  # noqa: E402
import pathlib  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from unittest import mock  # noqa: E402

ROOT = pathlib.Path.cwd()
HERE = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "custom_components"), str(ROOT / "tools/audit")]

import text_ledger as TL  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from golden import _presented_fields  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    accuracy, config_flow, const, debugger, dhw_schedule, duty_legs, external_heat,
    flow_lift, grid_fee, legionella, optimizer, price_tiles, pump_arbiter,
    quick_setup, services, silent_mode, slab_seed, thermal_model, topology, wood_fuel,
)
from heatpump_optimizer.inputs import TEMPERATURE_DELTA_MAX_K  # noqa: E402

PKG = "custom_components/heatpump_optimizer/"
EN_PATH = PKG + "translations/en.json"
EN = json.loads((ROOT / EN_PATH).read_text())


# --------------------------------------------------------------------------
# Rendered forms: every config and options step a bare entry shows, plus the
# conditional pages that need a stored answer to appear.
# --------------------------------------------------------------------------
FIELDS = {}


async def _render(flow, kind):
    for name in dir(flow):
        if not name.startswith("async_step_"):
            continue
        try:
            r = await getattr(flow, name)(None)
        except Exception:
            continue
        for k, v in _presented_fields(r.get("data_schema")):
            key = str(getattr(k, "schema", k))
            d = getattr(k, "default", None)
            try:
                dv = d() if callable(d) else (getattr(k, "description", None) or {}).get("suggested_value")
            except Exception:
                dv = None
            cfg = getattr(v, "config", None)
            FIELDS.setdefault((kind, r.get("step_id"), key), (dv, cfg if isinstance(cfg, dict) else {}))


def render_all():
    async def go():
        of = config_flow.HeatPumpOptimizerOptionsFlow(FakeEntry(data={}, options={}))
        of.hass = FakeHass()
        await _render(of, "options")
        cond = {const.CONF_SPACE_SETPOINT_ENTITY: "number.flow", "space_setpoint_unit": "flow",
                const.CONF_WOOD_FURNACE_ENABLED: True}
        of2 = config_flow.HeatPumpOptimizerOptionsFlow(FakeEntry(data={}, options=cond))
        of2.hass = FakeHass()
        await _render(of2, "options")
        cf = config_flow.HeatPumpOptimizerConfigFlow()
        cf.hass = FakeHass()
        await _render(cf, "config")
    asyncio.run(go())


def field(kind, step, key, what="default"):
    dv, cfg = FIELDS[(kind, step, key)]
    return dv if what == "default" else cfg.get(what)


# --------------------------------------------------------------------------
# The register: (en.json key path or Python file, sentence substring,
# claimed value, resolver -> observed, symbol). A sentence that occurs at
# several paths is checked at each (the path is a regex over the dotted path).
# --------------------------------------------------------------------------
def _night_drop():
    oc = optimizer.OptimizationConfig()
    day = oc.get_temp_bounds(12.0)[0]
    return round(day - oc.get_temp_bounds(2.0)[0], 6)


def _top_only_offset():
    return 60.0 - external_heat.wood_tank_bulk_temperature(60.0, None) if hasattr(
        external_heat, "wood_tank_bulk_temperature") else None


def _bulk_fn():
    for n in dir(external_heat):
        f = getattr(external_heat, n)
        if callable(f) and getattr(f, "__doc__", "") and "probe pair" in (f.__doc__ or ""):
            return f
    return None


def _silent_floor():
    cap = silent_mode.caps(datetime(2026, 1, 5, tzinfo=timezone.utc), 4, 0.25,
                           dhw_schedule.parse_windows("00:00-24:00"), 0.3, 10.0)
    return round(float(cap[0]) / 10.0, 6)


def _rain_factor(precip):
    p = thermal_model.ThermalParameters()
    m = thermal_model.ThermalModel(p) if hasattr(thermal_model, "ThermalModel") else None
    base = float(m.effective_heat_loss_coefficient(1.0, 0.0, 0.0))
    return float(m.effective_heat_loss_coefficient(1.0, 0.0, precip)) / base


def _partload_refused(derate, pmin, pmax):
    saved = {const.CONF_HEAT_PUMP_MIN_POWER: pmin, const.CONF_HEAT_PUMP_MAX_POWER: pmax,
             const.CONF_HEAT_PUMP_COP_PARTLOAD_DERATE: derate}
    return bool(config_flow._partload_errors(saved, {}))


_CB_BASE = {"target_temperature": 21.0, "min_temperature": 19.0, "max_temperature": 23.0,
            "comfort_temp_day": 21.0, "comfort_temp_night": 19.5, "day_start_hour": 7, "day_end_hour": 22}


def _cb(key, value, field_key=None):
    from heatpump_optimizer import comfort_band
    return comfort_band.errors({**_CB_BASE, key: value}, {}).get(field_key or key)


def _prefill_renders(kind="config"):
    sys.path.insert(0, str(HERE))
    import prefill_placeholders as pp
    if kind == "config":
        res = asyncio.run(pp.config_arms())
        return all(not pp.measure("config", r)[0] for r in res)
    return not pp.measure("options", asyncio.run(pp.options_arms()))[0]


def _parses(fn, s):
    try:
        out = fn(s)
        return out is not None and out != []
    except Exception:
        return False


def _fraction_unset():
    return const.CONF_SILENT_MODE_FRACTION not in services._quiet_schedule_fields(
        {const.CONF_SILENT_MODE_FRACTION: 1.0})


ECON = r"(config\.step\.temperature|options\.step\.comfort\.sections\.band)\.data_description\.min_temperature"
RULES = [
    # comfort band
    (ECON, "at night the limit is 0.5 K lower", 0.5, _night_drop, "optimizer:OptimizationConfig.get_temp_bounds"),
    (ECON, "lowers it by a further 1.5 K", 1.5, lambda: const.ECONOMY_MIN_TEMP_WIDENING, "const:ECONOMY_MIN_TEMP_WIDENING"),
    (ECON, "a detected open window by 1 K", 1.0, lambda: const.OPEN_WINDOW_RELAX_C, "const:OPEN_WINDOW_RELAX_C"),
    (ECON, "never below 15 °C", 15.0, lambda: const.ECONOMY_ABSOLUTE_FLOOR, "const:ECONOMY_ABSOLUTE_FLOOR"),
    (r"services\.set_mode\.fields\.mode\.description", "1.5 °C below your comfort floor", 1.5, lambda: const.ECONOMY_MIN_TEMP_WIDENING, "const:ECONOMY_MIN_TEMP_WIDENING"),
    (r"services\.set_mode\.fields\.mode\.description", "1.5 °C below your comfort floor", 15.0, lambda: const.ECONOMY_ABSOLUTE_FLOOR, "const:ECONOMY_ABSOLUTE_FLOOR"),
    (r"open_window_relax_enabled", "by 1 °C, never below 15 °C", 1.0, lambda: const.OPEN_WINDOW_RELAX_C, "const:OPEN_WINDOW_RELAX_C"),
    (r"open_window_relax_enabled", "by 1 °C, never below 15 °C", 15.0, lambda: const.ECONOMY_ABSOLUTE_FLOOR, "away:ECONOMY_ABSOLUTE_FLOOR"),
    (r"open_window_relax_enabled", "Off by default because it moves", False, lambda: field("options", "learning_features", "open_window_relax_enabled"), "config_flow:options learning_features form"),
    # sensors and stores
    (r"floor_return_temp_entity$", "more than 12 K above the room", 12.0, lambda: slab_seed.SLAB_SEED_MAX_ABOVE_ROOM_K, "slab_seed:SLAB_SEED_MAX_ABOVE_ROOM_K"),
    (r"buffer_tank_volume$", "holds at least 100 litres", 100.0, lambda: const.BUFFER_STORE_MIN_VOLUME, "const:BUFFER_STORE_MIN_VOLUME"),
    (r"dhw_combi_tank_enabled$", "a buffer of at least 100 L", 100.0, lambda: const.BUFFER_STORE_MIN_VOLUME, "const:BUFFER_STORE_MIN_VOLUME"),
    (r"options\.error\.combi_needs_store", "a buffer tank of at least 100 L", 100.0, lambda: const.BUFFER_STORE_MIN_VOLUME, "const:BUFFER_STORE_MIN_VOLUME"),
    (r"quick_setup\.data_description\.buffer_tank$", "(500 litres", 500.0, lambda: quick_setup.QUICK_SETUP_BUFFER_VOLUME, "quick_setup:QUICK_SETUP_BUFFER_VOLUME"),
    (r"quick_setup\.data_description\.buffer_tank$", "default of 35 litres", 35.0, lambda: field("config", "zones", "buffer_tank_volume"), "config_flow:config zones form default"),
    (r"wood_tank_top_entity$", "temperature plus 2 °C", 2.0, lambda: const.WOOD_TANK_MIN_MARGIN, "const:WOOD_TANK_MIN_MARGIN"),
    (r"wood_tank_top_entity$", "taken as 5 °C below it", 5.0, lambda: 60.0 - _bulk_fn()(60.0, None), "external_heat:<bulk temperature from probe pair>"),
    (r"wood_packing$", "billed at 0.60 of packed", 0.60, lambda: max((abs(wood_fuel.useful_kwh_m3(t, "loose", 100) / wood_fuel.useful_kwh_m3(t, "packed", 100) - 0.6), round(wood_fuel.useful_kwh_m3(t, "loose", 100) / wood_fuel.useful_kwh_m3(t, "packed", 100), 3)) for t in wood_fuel.WOOD_KWH_M3)[1], "wood_fuel:useful_kwh_m3 (worst type)"),
    (r"wood_type$", "Mixed is the default.", "mixed", lambda: const.DEFAULT_WOOD_TYPE, "const:DEFAULT_WOOD_TYPE"),
    # hot water
    (r"error\.dhw_min_too_close", "at least 5 °C below the setpoint", 5.0, lambda: const.DHW_MIN_TEMP_SETPOINT_MARGIN, "const:DHW_MIN_TEMP_SETPOINT_MARGIN"),
    (r"dhw_cooling_rate$", "measured at 45 °C in a 20 °C room", 45.0, lambda: const.DHW_COOLING_REFERENCE_TANK_TEMP, "const:DHW_COOLING_REFERENCE_TANK_TEMP"),
    (r"dhw_cooling_rate$", "measured at 45 °C in a 20 °C room", 20.0, lambda: const.DHW_COOLING_REFERENCE_AMBIENT_TEMP, "const:DHW_COOLING_REFERENCE_AMBIENT_TEMP"),
    (r"services\.set_thermal_parameters\.fields\.dhw_cooling_rate", "at 45 °C tank temperature and 20 °C ambient", 25.0, lambda: const.DHW_COOLING_REFERENCE_TANK_TEMP - const.DHW_COOLING_REFERENCE_AMBIENT_TEMP, "const:DHW_COOLING_REFERENCE_*"),
    (r"dhw_idle_min_temperature$", "roughly room temperature", 20.0, lambda: field("config", "dhw", "dhw_idle_min_temperature"), "config_flow:config dhw form default"),
    (r"dhw_inlet_temp$", "Swedish default of 10 °C", 10.0, lambda: field("options", "hot_water_tank", "dhw_inlet_temp"), "config_flow:options hot_water_tank form default"),
    (r"dhw_free_disinfection_enabled$", "held that temperature for 20 minutes", 20.0, lambda: const.DHW_LEGIONELLA_HOLD_MINUTES, "const:DHW_LEGIONELLA_HOLD_MINUTES"),
    (r"dhw_combi_legionella_force$", "With 3 L or less", 3.0, lambda: const.COMBI_LEGIONELLA_POTABLE_LIMIT_L, "const:COMBI_LEGIONELLA_POTABLE_LIMIT_L"),
    (r"dhw_combi_legionella_force$", "With 3 L or less", False, lambda: field("options", "building", "dhw_combi_legionella_force"), "config_flow:options building form default"),
    (r"combi_dhw_effectiveness$", "from 0.1 to 1", (0.1, 1.0), lambda: (field("options", "building", "combi_dhw_effectiveness", "min"), field("options", "building", "combi_dhw_effectiveness", "max")), "config_flow:options building selector"),
    (r"combi_dhw_effectiveness$", "About 0.85 for a coil", (0.85, 0.95, 0.75), lambda: tuple(const.COMBI_TANK_PRESETS[k].effectiveness for k in ("internal_coil", "tank_in_tank", "external_station")), "const:COMBI_TANK_PRESETS"),
    (r"issues\.dhw_legionella_(overdue|unreachable|off_step)\.description", "a day", 24.0, lambda: legionella.DHW_LEGIONELLA_RETRY_HOURS, "legionella:DHW_LEGIONELLA_RETRY_HOURS"),
    (r"issues\.dhw_disinfection_switch_lost\.description", "for half an hour", 30.0, lambda: const.DHW_DISINFECTION_LOST_MINUTES, "const:DHW_DISINFECTION_LOST_MINUTES"),
    # set-points and pump duty
    (r"flow_heat_c$", "55 °C suits a supply target", 55.0, lambda: field("options", "entities", "flow_heat_c"), "config_flow:options entities form default"),
    (r"flow_heat_c$", "Below 30 °C is not offered", 30, lambda: field("options", "entities", "flow_heat_c", "min"), "config_flow:options entities selector"),
    (r"flow_heat_c$", "the gate that means off is 25 °C", 25.0, lambda: pump_arbiter.FLOW_GATE_C, "pump_arbiter:FLOW_GATE_C"),
    (r"flow_heat_c$", "(up to 70 °C)", 70.0, lambda: const.FLOW_HEAT_C_MAX, "const:FLOW_HEAT_C_MAX"),
    (r"flow_min_lift_k$", "5 K suits a controller", 5.0, lambda: field("options", "entities", "flow_min_lift_k"), "config_flow:options entities form default"),
    (r"space_setpoint_power_feedback$", "After a 5-minute start hold", 300.0, lambda: pump_arbiter.FEEDBACK_START_HOLD.total_seconds(), "pump_arbiter:FEEDBACK_START_HOLD"),
    (r"space_setpoint_power_feedback$", "within 10 %", 0.1, lambda: pump_arbiter.FEEDBACK_DEADBAND_SHARE, "pump_arbiter:FEEDBACK_DEADBAND_SHARE"),
    (r"space_setpoint_power_feedback$", "On by default.", True, lambda: field("options", "entities", "space_setpoint_power_feedback"), "config_flow:options entities form default"),
    (r"pump_duty_mode$", "a share under 5 minutes", 5.0, lambda: duty_legs.SPLIT_MIN_MINUTES, "duty_legs:SPLIT_MIN_MINUTES"),
    (r"pump_duty_mode$", "the hot water one to 30 °C", 30.0, lambda: pump_arbiter.DHW_GATE_C, "pump_arbiter:DHW_GATE_C"),
    (r"pump_duty_mode$", "capped at 90 minutes", (90.0, 30.0, -10.0), lambda: (pump_arbiter.LEASE_MINUTES, pump_arbiter.COLD_LEASE_MINUTES, pump_arbiter.COLD_RAIL_C), "pump_arbiter:LEASE_MINUTES/COLD_*"),
    (r"pump_duty_mode$", "sent again every 5 minutes", 5.0, lambda: pump_arbiter.RETRY_MINUTES, "pump_arbiter:RETRY_MINUTES"),
    (r"pump_duty_mode$", "Off (the default)", "off", lambda: field("options", "entities_pump", "pump_duty_mode"), "config_flow:options entities_pump form default"),
    (r"issues\.pump_write_ignored\.description", "every five minutes", 5.0, lambda: pump_arbiter.RETRY_MINUTES, "pump_arbiter:RETRY_MINUTES"),
    (r"(space|dhw)_hysteresis_entity$", "0 to 20 K", 20.0, lambda: TEMPERATURE_DELTA_MAX_K, "inputs:TEMPERATURE_DELTA_MAX_K"),
    (r"flow_curve_cop_enabled$", "at most 15 K below", 15.0, lambda: flow_lift.FLOW_BIAS_CLAMP_K, "flow_lift:FLOW_BIAS_CLAMP_K"),
    (r"flow_curve_cop_enabled$", "a 75 °C supply", 75.0, lambda: flow_lift.FLOW_SUPPLY_MAX_C, "flow_lift:FLOW_SUPPLY_MAX_C"),
    (r"flow_curve_cop_enabled$", "Off by default.", False, lambda: field("options", "building", "flow_curve_cop_enabled"), "config_flow:options building form default"),
    # tuning and learning
    (r"confidence_margins_enabled$", "capped at 0.8 °C", 0.8, lambda: const.CONFIDENCE_MARGIN_CAP_C, "const:CONFIDENCE_MARGIN_CAP_C"),
    (r"price_tiles_enabled$", "power capped at 75 %", True, lambda: "power_cap_75" in price_tiles.TILE_NAMES, "price_tiles:TILE_NAMES"),
    (r"price_tiles_enabled$", "averaged over 30 days", 30, lambda: price_tiles.HORIZON_DAYS, "price_tiles:HORIZON_DAYS"),
    (r"price_tiles_enabled$", "Off by default because", False, lambda: field("options", "tuning", "price_tiles_enabled"), "config_flow:options tuning form default"),
    (r"heat_curve_persistent_writes_per_day$", "12 (six shift-and-return", 12, lambda: const.DEFAULT_HEAT_CURVE_PERSISTENT_WRITES_PER_DAY, "const:DEFAULT_HEAT_CURVE_PERSISTENT_WRITES_PER_DAY"),
    (r"heat_curve_persistent_min_dwell_minutes$", "60 minutes is about", 60, lambda: const.DEFAULT_HEAT_CURVE_PERSISTENT_MIN_DWELL_MINUTES, "const:DEFAULT_HEAT_CURVE_PERSISTENT_MIN_DWELL_MINUTES"),
    (r"heat_curve_offset_band_k$", "3 K is an estimate", 3.0, lambda: field("options", "heat_curve", "heat_curve_offset_band_k"), "config_flow:options heat_curve form default"),
    (r"heat_curve_persistent_band_k$", "3 K is an estimate", 3.0, lambda: const.DEFAULT_HEAT_CURVE_PERSISTENT_BAND_K, "const:DEFAULT_HEAT_CURVE_PERSISTENT_BAND_K"),
    (r"options\.error\.partload_derate_above_limit", "below 0.44 for a 1-5 kW pump", (False, True), lambda: (_partload_refused(0.44, 1.0, 5.0), _partload_refused(0.45, 1.0, 5.0)), "config_flow:_partload_errors"),
    (r"options\.error\.partload_derate_above_limit", "below 0.17 for a 4-5 kW one", (False, True), lambda: (_partload_refused(0.16, 4.0, 5.0), _partload_refused(0.17, 4.0, 5.0)), "config_flow:_partload_errors"),
    (r"capacity_curve_enabled$", "at least 60% of nameplate", 0.6, lambda: const.CAPACITY_FLOOR_FRACTION, "const:CAPACITY_FLOOR_FRACTION"),
    (r"outage_recovery_enabled$", "two-hour recovery window", (2.0, 45.0), lambda: (const.OUTAGE_RECOVERY_HOURS, const.OUTAGE_DHW_DELAY_MINUTES), "const:OUTAGE_RECOVERY_HOURS/OUTAGE_DHW_DELAY_MINUTES"),
    (r"debug_collect_enabled$", "(15 minutes at most", 900.0, lambda: debugger.SELF_TEST_BUDGET.total_seconds(), "debugger:SELF_TEST_BUDGET"),
    (r"services\.debug_collect\.description", "week-long debug collection", 7, lambda: debugger.COLLECT_SPAN.days, "debugger:COLLECT_SPAN"),
    (r"options\.step\.learning\.description", "are on by default; the rest are off", (True, True, False, False, False), lambda: tuple(field("options", "learning", k) for k in ("staleness_watchdog_enabled", "price_prior_enabled", "comfort_learning_enabled", "system_identification_enabled", "debug_collect_enabled")), "config_flow:options learning form defaults"),
    (r"prefill_offer$", "Off by default", False, lambda: field("options", "modbus_prefill", "prefill_offer"), "config_flow:options modbus_prefill form default"),
    (r"comfort_temp_day_weekend$", "Defaults to the weekday daytime value.", True, lambda: field("options", "comfort", "comfort_temp_day_weekend") == field("options", "comfort", "comfort_temp_day"), "config_flow:options comfort form defaults"),
    (r"comfort_temp_night_weekend$", "Defaults to the weekday night value.", True, lambda: field("options", "comfort", "comfort_temp_night_weekend") == field("options", "comfort", "comfort_temp_night"), "config_flow:options comfort form defaults"),
    (r"(accuracy_drift|accuracy_drift_rolled_back)\.description$", "three settled days", 3.0, lambda: accuracy.REFIT_SETTLED_DAYS, "accuracy:REFIT_SETTLED_DAYS"),
    (r"services\.restore_learned_snapshot\.description", "three settled days", 3.0, lambda: accuracy.REFIT_SETTLED_DAYS, "accuracy:REFIT_SETTLED_DAYS"),
    # silent mode, rain, COP
    (r"silent_mode_power_fraction\.description", "(a lower value is raised to 0.6)", 0.6, _silent_floor, "silent_mode:caps"),
    (r"(simulate_plan|apply_schedule)\.fields\.silent_mode_power_fraction\.description", "1.0 is the unset value", True, _fraction_unset, "services:_quiet_schedule_fields"),
    (r"grid_connection\.data_description\.silent_mode_power_fraction", "1.0 caps nothing.", True, lambda: silent_mode.caps(datetime(2026, 1, 5, tzinfo=timezone.utc), 4, 0.25, dhw_schedule.parse_windows("00:00-24:00"), 1.0, 10.0) is None, "silent_mode:caps"),
    (r"rain_heat_loss_multiplier\.description", "rain of 2 mm/h or more", (1.15, 1.15, 1.0, 1.075), lambda: tuple(round(_rain_factor(p), 6) for p in (2.0, 4.0, 0.1, 1.0)), "thermal_model:ThermalModel.effective_heat_loss_coefficient"),
    (r"heat_pump_cop_nominal\.description", "at 7°C outdoor temperature", 7.0, lambda: thermal_model.ThermalParameters().cop_reference_temp, "thermal_model:ThermalParameters.cop_reference_temp"),
    # horizon and manual plan
    (r"weather_entity$", "plans 24 hours ahead", 24.0, lambda: optimizer.OptimizationConfig().horizon_hours, "optimizer:OptimizationConfig.horizon_hours"),
    (r"services\.run_optimization\.description", "for the next 24 hours", 24.0, lambda: optimizer.OptimizationConfig().horizon_hours, "optimizer:OptimizationConfig.horizon_hours"),
    (r"entity\.sensor\.(dhw_heating_cost|plan_dhw_heating|plan_space_heating)\.name", "(next 24 h)", 24.0, lambda: optimizer.OptimizationConfig().horizon_hours, "optimizer:OptimizationConfig.horizon_hours"),
    (r"services\.apply_manual_plan\.description", "for the next 20 hours", 20, lambda: const.MANUAL_PLAN_WINDOW_HOURS, "const:MANUAL_PLAN_WINDOW_HOURS"),
    (r"services\.apply_manual_plan\.fields\.expires_at\.description", "Defaults to 20 hours from now", 20, lambda: const.MANUAL_PLAN_WINDOW_HOURS, "const:MANUAL_PLAN_WINDOW_HOURS"),
    (r"services\.apply_manual_plan\.fields\.expires_at\.description", "shorter than the optimizer's 24-hour horizon", True, lambda: const.MANUAL_PLAN_WINDOW_HOURS < optimizer.OptimizationConfig().horizon_hours == 24.0, "optimizer:OptimizationConfig.horizon_hours"),
    # examples a reader is told to type: each must pass the production parser
    (r"dhw_windows$", "'weekdays 06:00-08:30, weekend 08:00-09:30'", True, lambda: _parses(dhw_schedule.parse_weekly_windows, "weekdays 06:00-08:30, weekend 08:00-09:30") and _parses(dhw_schedule.parse_weekly_windows, "Mo 05:30-07:00, Tu-Fr 06:00-08:00, Sa,Su 08:00-09:30"), "dhw_schedule:parse_weekly_windows"),
    (r"error\.invalid_dhw_windows", '"06:00-08:30, 17:00-22:00"', True, lambda: _parses(dhw_schedule.parse_windows, "06:00-08:30, 17:00-22:00"), "dhw_schedule:parse_windows"),
    (r"grid_fee_rules$", '"Nov-Mar Mon-Fri 06:00-22:00 = 0.25"', True, lambda: _parses(grid_fee.parse_rules, "Nov-Mar Mon-Fri 06:00-22:00 = 0.25"), "grid_fee:parse_rules"),
    (r"options\.error\.invalid_grid_fee_rules", '"Nov-Mar Mon-Fri 06:00-22:00 = 0.25"', True, lambda: _parses(grid_fee.parse_rules, "Nov-Mar Mon-Fri 06:00-22:00 = 0.25"), "grid_fee:parse_rules"),
    (r"grid_fee_rules$", '"0,25" reads as 0.25', 0.25, lambda: grid_fee.parse_rules("Nov-Mar Mon-Fri 06:00-22:00 = 0,25")[0].rate, "grid_fee:parse_rules"),
    (r"options\.error\.invalid_peak_months", '"Nov-Mar" or single months like "Jul"', True, lambda: _parses(grid_fee.parse_month_range, "Nov-Mar") and _parses(grid_fee.parse_month_range, "Jul"), "grid_fee:parse_month_range"),
    (r"(peak_tariff_hours$|options\.error\.invalid_peak_hours)", '"07:00-19:00"', True, lambda: _parses(dhw_schedule.parse_windows, "07:00-19:00"), "dhw_schedule:parse_windows"),
    (r"silent_mode_windows$", '"22:00-06:00"', True, lambda: _parses(dhw_schedule.parse_windows, "22:00-06:00"), "dhw_schedule:parse_windows"),
    (r"quiet_off_windows\.description", '"weekend 23:00-07:00".', True, lambda: _parses(dhw_schedule.parse_weekly_windows, "weekend 23:00-07:00"), "dhw_schedule:parse_weekly_windows"),
    (r"services\.set_thermal_parameters\.fields\.dhw_windows\.description", "Frames may wrap past midnight.", True, lambda: dhw_schedule.parse_windows("22:00-06:00") == [(0.0, 6.0), (22.0, 24.0)], "dhw_schedule:parse_windows"),
    (r"services\.apply_topology\.fields\.layout\.description", "two_tank_4way or valve_upper_direct_slab", True, lambda: all(topology.LAYOUTS[k].selectable for k in ("two_tank_4way", "valve_upper_direct_slab")), "topology:LAYOUTS"),
    (r"services\.assign_entity\.fields\.key\.description", "buffer_tank_temp_entity", True, lambda: "buffer_tank_temp_entity" in topology.ASSIGNABLE_KEYS, "topology:ASSIGNABLE_KEYS"),
    (r"selector\.dso_product\.options\.ellevio_villa_effekt_2026", "(to 2026-05-31)", "2026-05-31", lambda: grid_fee.SWEDEN_CATALOG["ellevio_villa_effekt_2026"]["dated"].split("until ")[-1].rstrip(")"), "grid_fee:SWEDEN_CATALOG"),
    (r"solar_location$", "Defaults to your Home Assistant home location.", True, lambda: field("config", "user_sensors", "solar_location") == {"latitude": FakeHass().config.latitude, "longitude": FakeHass().config.longitude}, "config_flow:solar_location default"),
    (r"restore_learned_snapshot\.fields\.source\.description", "The weekly snapshot (default)", True, lambda: services.SERVICE_SCHEMA_RESTORE_SNAPSHOT({}).get("source", "weekly") in ("weekly", "snapshot") if hasattr(services, "SERVICE_SCHEMA_RESTORE_SNAPSHOT") else None, "services:restore schema default"),
    # form validators: each error sentence against the validator that raises it
    (r"(config|options)\.error\.min_above_target", "The minimum temperature is above the target", (True, False), lambda: (_cb("min_temperature", 21.5) == "min_above_target", _cb("min_temperature", 21.0) == "min_above_target"), "comfort_band:errors"),
    (r"(config|options)\.error\.max_below_target", "The maximum temperature is below the target", (True, False), lambda: (_cb("max_temperature", 20.5) == "max_below_target", _cb("max_temperature", 21.0) == "max_below_target"), "comfort_band:errors"),
    (r"(config|options)\.error\.night_above_day", "The night temperature is above the day", (True, False), lambda: (_cb("comfort_temp_night", 21.5) == "night_above_day", _cb("comfort_temp_night", 21.0) == "night_above_day"), "comfort_band:errors"),
    (r"(config|options)\.error\.day_window_empty", "end at or before it starts", (True, True, False), lambda: (_cb("day_end_hour", 7, "day_end_hour") == "day_window_empty", _cb("day_end_hour", 6, "day_end_hour") == "day_window_empty", _cb("day_end_hour", 8, "day_end_hour") == "day_window_empty"), "comfort_band:errors"),
    (r"(config|options)\.error\.comfort_outside_band", "must sit inside the comfort band", (True, False), lambda: (_cb("comfort_temp_day", 23.5) == "comfort_outside_band", _cb("comfort_temp_day", 23.0) == "comfort_outside_band"), "comfort_band:errors"),
    (r"(config|options)\.error\.min_power_above_max", "minimum power is above its maximum", (True, False), lambda: (bool(config_flow._power_errors({const.CONF_HEAT_PUMP_MIN_POWER: 6.0, const.CONF_HEAT_PUMP_MAX_POWER: 5.0}, {})), bool(config_flow._power_errors({const.CONF_HEAT_PUMP_MIN_POWER: 5.0, const.CONF_HEAT_PUMP_MAX_POWER: 5.0}, {}))), "config_flow:_power_errors"),
    (r"(config|options)\.error\.(dhw|silent_mode)_window_too_short", "time frame is shorter than", (True, False), lambda: (dhw_schedule.spec_problem("06:00-06:10") == dhw_schedule.ERROR_TOO_SHORT, dhw_schedule.spec_problem("06:00-06:15") == dhw_schedule.ERROR_TOO_SHORT), "dhw_schedule:spec_problem"),
    (r"(config|options)\.error\.(dhw|silent_mode)_window_too_short", "The plan is made in", True, lambda: float(dhw_schedule.MIN_WINDOW_MINUTES) == optimizer.OptimizationConfig().time_step_minutes, "dhw_schedule:MIN_WINDOW_MINUTES vs optimizer:OptimizationConfig.time_step_minutes"),
    # placeholders a page's text reads, on every render (D6-s3-01's harness)
    (r"config\.step\.device_prefill\.description", "Backup heater type register: {backup_heater_type}", True, lambda: _prefill_renders(), "config_flow:HeatPumpOptimizerConfigFlow.async_step_device_prefill (refusal render)"),
    (r"options\.step\.modbus_prefill\.description", "Backup heater type register: {backup_heater_type}", True, lambda: _prefill_renders("options"), "config_flow:HeatPumpOptimizerOptionsFlow.async_step_modbus_prefill (refusal render)"),
    # Python strings
    ("legionella.py", "it will be retried within a day", 24.0, lambda: legionella.DHW_LEGIONELLA_RETRY_HOURS, "legionella:DHW_LEGIONELLA_RETRY_HOURS"),
    ("debugger.py", "the store keeps the newest 192 samples; the live tracker more", True, lambda: accuracy.HISTORY_LENGTH > 192, "accuracy:HISTORY_LENGTH"),
    ("grid_fee.py", "Ellevio — villa effekt (to 2026-05-31)", "2026-05-31", lambda: grid_fee.SWEDEN_CATALOG["ellevio_villa_effekt_2026"]["dated"].split("until ")[-1].rstrip(")"), "grid_fee:SWEDEN_CATALOG"),
]


def _eq(a, b):
    if isinstance(a, tuple) and isinstance(b, tuple):
        return len(a) == len(b) and all(_eq(x, y) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(float(a) - float(b)) < 1e-9
    return a == b


def en_units():
    """(unit id, dotted path, sentence) for every en.json unit, in text_ledger's order."""
    out = []

    def walk(v, path):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, path + [k])
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(x, path + [str(i)])
        elif isinstance(v, str):
            out.extend((".".join(path), s) for s in TL.sentences(v))
    walk(EN, [])
    units = TL.units_of(EN_PATH, (ROOT / EN_PATH).read_text(), "D6")
    assert len(units) == len(out)
    return [(u[0], p, s) for u, (p, s) in zip(units, out)]


def py_units():
    out = []
    for f in sorted(p for p in (ROOT / PKG).glob("*.py") if not p.name.startswith("._")):
        rel = PKG + f.name
        out.extend((u[0], rel, u[3]) for u in TL.units_of(rel, f.read_text(), "D6"))
    return out


def main():
    import re
    perturb = "--perturb" in sys.argv
    t0p, t0t = time.process_time(), time.thread_time()
    render_all()
    enu, pyu = en_units(), py_units()
    rows, unmatched = [], 0
    ctx = mock.patch.object(const, "DHW_MIN_TEMP_SETPOINT_MARGIN", 4.0) if perturb else mock.patch.object(const, "DOMAIN", const.DOMAIN)
    with ctx:
        for where, sub, claimed, resolve, symbol in RULES:
            if where.endswith(".py"):
                hits = [(u, p) for u, p, s in pyu if p.endswith("/" + where) and sub in s]
            else:
                rx = re.compile(where)
                hits = [(u, p) for u, p, s in enu if rx.search(p) and sub in s]
            if not hits:
                unmatched += 1
                print(f"UNMATCHED {where} :: {sub}")
                continue
            try:
                observed = resolve()
            except Exception as err:  # a resolver that cannot run is reported, not hidden
                observed = f"error: {type(err).__name__}: {err}"
            ok = _eq(observed, claimed)
            for uid, path in hits:
                rows.append({"unit": uid, "path": path, "claim": sub, "claimed": repr(claimed),
                             "observed": repr(observed), "symbol": symbol, "verdict": "true" if ok else "false"})
                print(f"CHECK {'true ' if ok else 'FALSE'} {uid} [{path}] claimed={claimed!r} observed={observed!r} ({symbol})")
    # A unit several rules check is false if any of them is.
    by = {}
    for r in rows:
        prev = by.get(r["unit"])
        if prev is None:
            by[r["unit"]] = dict(r)
        else:
            prev["claim"] += " | " + r["claim"]
            prev["observed"] += " | " + r["observed"]
            prev["claimed"] += " | " + r["claimed"]
            prev["symbol"] += " | " + r["symbol"]
            if r["verdict"] == "false":
                prev["verdict"] = "false"
    (HERE / "claims.json").write_text(json.dumps(sorted(by.values(), key=lambda r: r["unit"]), indent=1, ensure_ascii=False))
    print(f"RESULT rules={len(RULES)} count")
    print(f"RESULT rules_unmatched={unmatched} count")
    print(f"RESULT claims_checked={len(by)} count")
    print(f"RESULT claims_false={sum(r['verdict'] == 'false' for r in by.values())} count")
    print(f"RESULT perturbed={int(perturb)}")
    dp, dt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={dp / dt if dt > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swap = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except (OSError, StopIteration):
        swap = -1
    print(f"RESULT swapins={swap}")


if __name__ == "__main__":
    main()

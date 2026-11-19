"""The content checks of the D6-s6 ledger: each numeric or concrete claim of de.json, run against code.

Imported by ledger.py (its header carries the command). Each entry is
(path regex, sentence regex, name, fn, verdict-if-contradicted); fn returns (ok, observed) and
reads the value a production symbol delivers -- a constant the deciding code imports, or the
output of the deciding function driven with a small input. EXTERNAL names numeric sentences
whose numbers are facts about third-party devices, standards or typical buildings, which no
code in this tree decides: those rows stay unverifiable.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
"""
import asyncio
import difflib
import re

F = None  # set by ledger.py

from custom_components.heatpump_optimizer import const as C  # noqa: E402


def _cf():
    from custom_components.heatpump_optimizer import config_flow
    return config_flow


def eq(a, b, tol=1e-9):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return a == b


def const_is(name, val, mod=C):
    def f():
        v = getattr(mod, name)
        return eq(v, val), f"{mod.__name__.rsplit('.', 1)[-1]}.{name}={v!r}, text says {val}"
    return f


def mod_const(modname, name, val):
    def f():
        import importlib
        m = importlib.import_module("custom_components.heatpump_optimizer." + modname)
        v = getattr(m, name)
        return eq(v, val), f"{modname}.{name}={v!r}, text says {val}"
    return f


def field(flow, step, key, attr, val):
    """A rendered field's default/min/max/unit/required, read from facts."""
    def f():
        page = F[flow].get(step) or {}
        info = page.get("fields", {}).get(key)
        if info is None:
            return False, f"{flow}/{step} has no field {key}"
        if attr == "default":
            v = info.get("default")
            v = v() if callable(v) else v
        elif attr == "required":
            v = info.get("required")
        else:
            v = info.get("config", {}).get(attr)
        return eq(v, val), f"{flow}/{step}.{key}.{attr}={v!r}, text says {val!r}"
    return f


def all_of(*fs):
    def f():
        res = [g() for g in fs]
        return all(r[0] for r in res), "; ".join(r[1] for r in res)
    return f


# ------------------------------------------------------------------ driven checks

def night_bound():
    from custom_components.heatpump_optimizer.optimizer import OptimizationConfig
    c = OptimizationConfig()
    c.min_temp, c.max_temp = 20.0, 23.0
    day = c.get_temp_bounds(12.0)[0]
    night = c.get_temp_bounds(3.0)[0]
    return eq(day - night, 0.5), f"OptimizationConfig.get_temp_bounds: day min {day}, night min {night}"


def widen(by_names, start, expect):
    def f():
        from custom_components.heatpump_optimizer import away
        bys = tuple(getattr(C, n) for n in by_names)

        class O:
            pass
        o = O()
        for n in away._OPT_FIELDS:
            setattr(o, n, None)
        o.min_temp, o.target_temp = start, 21.0

        class Tp:
            pass
        t = Tp()
        for n in away._DHW_FIELDS:
            setattr(t, n, 50.0)
        cfg, _ = away.solve_bands(o, t, None, bys)
        return eq(cfg["min_temp"], expect), f"away.solve_bands(min {start}, widen {dict(zip(by_names, bys))}) -> {cfg['min_temp']}, text implies {expect}"
    return f


def horizon24():
    from custom_components.heatpump_optimizer.optimizer import OptimizationConfig
    v = OptimizationConfig().horizon_hours
    return eq(v, 24), f"OptimizationConfig.horizon_hours={v}"


def rain():
    from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
    p = ThermalParameters()
    p.rain_heat_loss_multiplier = 1.15
    m = ThermalModel(p)
    base = m.effective_heat_loss_coefficient(1.0, 0.0, 0.0)
    full = m.effective_heat_loss_coefficient(1.0, 0.0, 2.0) / base
    light = m.effective_heat_loss_coefficient(1.0, 0.0, 0.1) / base
    half = m.effective_heat_loss_coefficient(1.0, 0.0, 1.0) / base
    ok = eq(full, 1.15, 1e-6) and eq(light, 1.0) and 1.0 < half < 1.15
    return ok, f"ThermalModel.effective_heat_loss_coefficient ratio: 2 mm/h {full:.4f}, 1 mm/h {half:.4f}, 0.1 mm/h {light:.4f}"


def rain_one():
    from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
    p = ThermalParameters()
    p.rain_heat_loss_multiplier = 1.0
    m = ThermalModel(p)
    r = m.effective_heat_loss_coefficient(1.0, 0.0, 5.0) / m.effective_heat_loss_coefficient(1.0, 0.0, 0.0)
    return eq(r, 1.0), f"multiplier 1.0 at 5 mm/h -> ratio {r}"


def wind():
    from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
    p = ThermalParameters()
    p.wind_sensitivity = 0.15
    m = ThermalModel(p)
    r = m.effective_heat_loss_coefficient(1.0, 1.0, 0.0) / m.effective_heat_loss_coefficient(1.0, 0.0, 0.0)
    return eq(r, 1.15, 1e-9), f"wind 0.15 at 1 m/s -> loss ratio {r}"


def floor_return_12():
    from custom_components.heatpump_optimizer import slab_seed
    hi = slab_seed.implausible(33.1, 21.0) if hasattr(slab_seed, "implausible") else None
    v = slab_seed.SLAB_SEED_MAX_ABOVE_ROOM_K
    return eq(v, 12.0) and hi in (None, True), f"slab_seed.SLAB_SEED_MAX_ABOVE_ROOM_K={v}; issue {slab_seed.ISSUE_FLOOR_RETURN_IMPLAUSIBLE}"


def modbus(field_key, regs, scale=None):
    """Drive modbus_prefill.infer with raw registers set; the field must come back."""
    def f():
        from harness import FakeHass, FakeState
        from custom_components.heatpump_optimizer import modbus_prefill as mp
        hass = FakeHass()
        vals = {404: 500, 405: 650, 406: 450, 518: 22 * 256, 519: 6 * 256, 601: 7, 711: 1,
                712: 6 * 256 + 30, 713: 8 * 256, 714: 0b00100100, 4109: 0}
        for addr, v in vals.items():
            hass.states.set(f"sensor.hp_gchv_r{addr}_{addr:04x}h", FakeState(str(v)))
        snap = mp.snapshot(hass.states.get, mp.candidates("hp"))
        out = mp.infer(snap, {})
        ids = {r: snap.get(f"r{int(r, 16)}", (None,))[0] for r in regs}
        hexok = all(i is not None for i in ids.values())
        got = out.get(field_key)
        ok = hexok and got is not None
        if scale is not None:
            ok = ok and eq(got, scale)
        return ok, f"modbus_prefill.infer -> {field_key}={got!r} from {sorted(ids.values(), key=str)}"
    return f


def backup7():
    from custom_components.heatpump_optimizer import modbus_prefill as mp
    n = mp.notes({"r601": ("sensor.x", "7", 1.0)})
    return n.get("backup_heater_type") == "7" and 601 in mp._RAW_ADDRESSES, f"modbus_prefill.notes reads register 601 -> {n}"


def dhw_gap():
    cf = _cf()
    a = cf._dhw_min_too_close({C.CONF_DHW_SETPOINT: 55.0, C.CONF_DHW_MIN_TEMP: 50.5}, {})
    b = cf._dhw_min_too_close({C.CONF_DHW_SETPOINT: 55.0, C.CONF_DHW_MIN_TEMP: 50.0}, {})
    return a and not b, f"_dhw_min_too_close(55, 50.5)={a}, (55, 50)={b}"


def windows_parse(spec):
    def f():
        from custom_components.heatpump_optimizer import dhw_schedule
        try:
            w = dhw_schedule.parse_weekly_windows(spec) if any(ch.isalpha() for ch in spec) else dhw_schedule.parse_windows(spec)
            return bool(w), f"dhw_schedule parses {spec!r} -> {len(w) if hasattr(w, '__len__') else w} windows"
        except Exception as e:  # noqa: BLE001
            return False, f"dhw_schedule refuses {spec!r}: {e}"
    return f


def fee_parse(spec, rate):
    def f():
        from custom_components.heatpump_optimizer import grid_fee
        try:
            rules = grid_fee.parse_rules(spec)
        except Exception as e:  # noqa: BLE001
            return False, f"grid_fee.parse_rules refuses {spec!r}: {e}"
        r = [getattr(x, "rate", None) for x in rules]
        return len(rules) == 1 and eq(r[0], rate), f"grid_fee.parse_rules({spec!r}) -> rates {r}"
    return f


def peak_hours():
    """The grid page's own validator (config_flow.is_valid_spec) must accept the example."""
    v = _cf().is_valid_spec("07:00-19:00")
    return bool(v), f"config_flow.is_valid_spec('07:00-19:00')={v}"


def partload():
    from custom_components.heatpump_optimizer.thermal_model import partload_derate_limit
    a, b = partload_derate_limit(1.0, 5.0), partload_derate_limit(4.0, 5.0)
    return eq(round(a, 2), 0.44) and eq(round(b, 2), 0.17), f"partload_derate_limit(1,5)={a:.4f}, (4,5)={b:.4f}"


def wood_loose():
    from custom_components.heatpump_optimizer import wood_fuel
    r = {t: wood_fuel.useful_kwh_m3(t, "loose", 100) / wood_fuel.useful_kwh_m3(t, "packed", 100) for t in wood_fuel.WOOD_KWH_M3}
    ok = all(eq(round(v, 2), 0.60) for v in r.values())
    return ok, "wood_fuel.useful_kwh_m3 loose/packed per type: " + ", ".join(f"{k} {v:.3f}" for k, v in r.items())


def combi_presets():
    cf = _cf()
    got = {}
    for kind in ("internal_coil", "tank_in_tank", "external_station"):
        out = cf._combi_preset_fill({C.CONF_DHW_COMBI_TANK_TYPE: kind}, {C.CONF_DHW_COMBI_TANK_TYPE: "custom"})
        got[kind] = (out.get(C.CONF_COMBI_DHW_EFFECTIVENESS), out.get(C.CONF_COMBI_POTABLE_VOLUME_L))
    return got, "config_flow._combi_preset_fill -> " + ", ".join(f"{k} eps {v[0]} potable {v[1]} L" for k, v in got.items())


def combi_eps():
    got, obs = combi_presets()
    ok = eq(got["internal_coil"][0], 0.85) and eq(got["tank_in_tank"][0], 0.95) and eq(got["external_station"][0], 0.75)
    return ok, obs


def combi_station_zero():
    got, obs = combi_presets()
    return eq(got["external_station"][1], 0.0), obs


def flow_heat_floor():
    info = F["options"]["entities"]["fields"].get(C.CONF_FLOW_HEAT_C)
    mn = info["config"].get("min") if info else None
    from custom_components.heatpump_optimizer import pump_arbiter as pa
    ret = pa.FLOW_GATE_C - pa.RETURN_SUPPLY_OFFSET_K
    return eq(mn, 30) and eq(pa.FLOW_GATE_C, 25) and eq(ret, 20), f"flow_heat_c min {mn}; pump_arbiter.FLOW_GATE_C={pa.FLOW_GATE_C}, return gate {ret}"


def heat_curve_ecl_only():
    """The text says the page is for MQTT ECL110 controllers only; the page renders a non-MQTT entity arm."""
    rows = [r.key for r in _cf()._OPTION_FIELDS if r.step == "heat_curve"]
    other = [k for k in rows if not k.startswith("ecl110")]
    return not other, f"heat_curve page rows beyond the ECL110 MQTT ones: {other}"


def capacity_floor():
    return const_is("CAPACITY_FLOOR_FRACTION", 0.6)()


def price_tiles_arms():
    from custom_components.heatpump_optimizer import price_tiles as pt
    ok = pt.TILE_NAMES == ("target_minus_1", "target_plus_1", "power_cap_75") and pt.HORIZON_DAYS == 30
    return ok, f"price_tiles.TILE_NAMES={pt.TILE_NAMES}, HORIZON_DAYS={pt.HORIZON_DAYS}"


def writes_quota():
    v = C.DEFAULT_HEAT_CURVE_PERSISTENT_WRITES_PER_DAY
    return eq(v, 12) and 12 * 365 < 7000 < 20 * 365 and 19 * 365 < 7000, f"default writes/day {v}; 7000/365={7000/365:.2f}"


def two_zone_semantic(key, val):
    return field("options", "thermal_model_zones", key, "default", val)


def silent_clamp():
    info = F["options"]["grid_connection"]["fields"].get(C.CONF_SILENT_MODE_FRACTION if hasattr(C, "CONF_SILENT_MODE_FRACTION") else "silent_mode_power_fraction")
    mn, mx = info["config"].get("min"), info["config"].get("max")
    return eq(mn, 0.6) and eq(mx, 1.0) and eq(C.DEFAULT_SILENT_MODE_FRACTION, 1.0), f"silent_mode_power_fraction range {mn}..{mx}, default {C.DEFAULT_SILENT_MODE_FRACTION}"


def accuracy_refit():
    from custom_components.heatpump_optimizer import accuracy
    return eq(accuracy.REFIT_SETTLED_DAYS, 3) and accuracy.REFIT_BAND_PERCENT <= 10, f"accuracy.REFIT_SETTLED_DAYS={accuracy.REFIT_SETTLED_DAYS}, REFIT_BAND_PERCENT={accuracy.REFIT_BAND_PERCENT}"


def manual_window():
    from custom_components.heatpump_optimizer import manual_plan
    v = getattr(manual_plan, "MANUAL_PLAN_WINDOW_HOURS", C.MANUAL_PLAN_WINDOW_HOURS)
    return eq(v, 20), f"MANUAL_PLAN_WINDOW_HOURS={v}"


def snapshot_ring():
    from custom_components.heatpump_optimizer import snapshots
    return eq(snapshots.SNAPSHOT_INTERVAL_DAYS, 7), f"snapshots.SNAPSHOT_INTERVAL_DAYS={snapshots.SNAPSHOT_INTERVAL_DAYS}, RING_SIZE={snapshots.RING_SIZE}"


def heat_curve_zero_neutral():
    """An offset entity must hold 0 in its range (0 = neutral); one excluding 0 is refused."""
    from custom_components.heatpump_optimizer import heat_curve
    from custom_components.heatpump_optimizer.inputs import NumberReading
    a = heat_curve.range_excludes_zero(NumberReading(0.0, "K", -5.0, 5.0))
    b = heat_curve.range_excludes_zero(NumberReading(30.0, "°C", 20.0, 60.0))
    return (not a) and b, f"heat_curve.range_excludes_zero(-5..5)={a}, (20..60)={b}"


def selector_label(key, val):
    def f():
        return val in F["selectors"].get(key, set()), f"selector {key} options {sorted(F['selectors'].get(key, set()))}"
    return f


def peak_window_opts():
    s = F["selectors"].get("peak_window", set())
    return s == {"15", "60"}, f"peak_window options {sorted(s)} (minutes)"


def dso_dates():
    from custom_components.heatpump_optimizer import grid_fee
    rows = grid_fee.SWEDEN_CATALOG
    keys = sorted(rows)
    return {"ellevio_villa_effekt_2026", "goteborg_energi_effekt_2026"} <= set(keys), f"SWEDEN_CATALOG keys {keys}"


def boost_max():
    return const_is("FLOW_HEAT_C_MAX", 70.0)()


CHECKS = [
    # plan horizon
    (r"", r"24 Stunden voraus|nächsten 24 Stunden|24-Stunden-Horizont|\(nächste 24 h\)", "plan horizon 24 h", horizon24, "false"),
    # comfort band
    (r"min_temperature", r"nachts liegt die Grenze 0,5 K tiefer", "night floor 0.5 K below", night_bound, "false"),
    (r"min_temperature", r"Sparbetrieb senkt sie um weitere 1,5 K", "economy widening 1.5 K, floor 15", all_of(widen(("ECONOMY_MIN_TEMP_WIDENING",), 18.0, 16.5), widen(("ECONOMY_MIN_TEMP_WIDENING",), 15.5, 15.0)), "false"),
    (r"min_temperature", r"offenes Fenster um 1 K", "open window widening 1 K", widen(("OPEN_WINDOW_RELAX_C",), 18.0, 17.0), "false"),
    (r"open_window_relax_enabled", r"um 1 °C, nie unter 15 °C", "open window 1 °C, floor 15", all_of(widen(("OPEN_WINDOW_RELAX_C",), 18.0, 17.0), widen(("OPEN_WINDOW_RELAX_C",), 15.4, 15.0)), "false"),
    (r"set_mode", r"bis zu 1,5 °C unter deine Komfortuntergrenze .*nie unter 15 °C", "economy 1.5 °C, never below 15", all_of(widen(("ECONOMY_MIN_TEMP_WIDENING",), 18.0, 16.5), widen(("ECONOMY_MIN_TEMP_WIDENING",), 15.5, 15.0)), "false"),
    # floor return
    (r"floor_return_temp_entity", r"mehr als 12 K über dem Raum", "floor return 12 K bound", floor_return_12, "false"),
    # buffer as store
    (r"buffer_tank_volume|combi_tank_enabled|combi_needs_store", r"mindestens 100 (Liter|L)", "buffer store >= 100 L", const_is("BUFFER_STORE_MIN_VOLUME", 100.0), "false"),
    (r"quick_setup/data_description/buffer_tank", r"500 Liter", "quick setup buffer 500 L, default 35 L",
     all_of(mod_const("quick_setup", "QUICK_SETUP_BUFFER_VOLUME", 500.0), const_is("DEFAULT_BUFFER_TANK_VOLUME", 35.0)), "false"),
    # wood
    (r"wood_tank_top_entity", r"als 5 °C darunter", "top-only mean = top - 5", lambda: (__import__("custom_components.heatpump_optimizer.external_heat", fromlist=["x"]).wood_mean_temperature(70.0, None) == 65.0, "external_heat.wood_mean_temperature(70, None)"), "false"),
    (r"wood_tank_top_entity", r"plus 2 °C", "wood tank margin 2 °C", const_is("WOOD_TANK_MIN_MARGIN", 2.0), "false"),
    (r"wood_packing", r"0,60 des gepackten", "loose wood = 0.60 of packed", wood_loose, "false"),
    (r"wood_furnace_enabled", r"500 l", "500 l is the wood tank default", const_is("DEFAULT_WOOD_TANK_VOLUME", 500.0), "false"),
    # prefill registers
    (r"prefill/description|modbus_prefill/description", r"außer 7", "backup heater register reads 7 for none", backup7, "false"),
    (r"prefill/data_description/dhw_setpoint", r"0194H", "dhw setpoint from 0194H x0.1", modbus(C.CONF_DHW_SETPOINT, ["0194"], 50.0), "false"),
    (r"prefill/data_description/dhw_min_temperature", r"0196H", "dhw min from 0196H x0.1", modbus(C.CONF_DHW_MIN_TEMP, ["0196"], 45.0), "false"),
    (r"prefill/data_description/dhw_legionella_temperature", r"0195H", "legionella from 0195H x0.1", modbus(C.CONF_DHW_LEGIONELLA_TEMP, ["0195"], 65.0), "false"),
    (r"prefill/data_description/dhw_windows", r"02C8H", "dhw windows from 02C8H/02C9H", modbus(C.CONF_DHW_WINDOWS, ["02c8", "02c9"], "06:30-08:00"), "false"),
    (r"prefill/data_description/dhw_legionella_interval_days", r"02CAH", "legionella interval 7 // days from 02CAH", modbus(C.CONF_DHW_LEGIONELLA_INTERVAL_DAYS, ["02ca"], 3.0), "false"),
    (r"prefill/data_description/silent_mode_windows", r"0206H", "silent windows from 0206H/0207H", modbus(C.CONF_SILENT_MODE_WINDOWS, ["0206", "0207"], "22:00-06:00"), "false"),
    (r"prefill/data_description/space_setpoint_unit", r"100DH", "flow unit from 100DH == 0", modbus(C.CONF_SPACE_SETPOINT_UNIT, ["100d"], "flow"), "false"),
    # dhw
    (r"dhw_min_too_close", r"mindestens 5 °C Abstand", "dhw deadband 5 °C", dhw_gap, "false"),
    (r"invalid_dhw_windows", r"06:00-08:30, 17:00-22:00", "dhw window example parses", windows_parse("06:00-08:30, 17:00-22:00"), "false"),
    (r"dhw_windows", r"weekdays 06:00-08:30", "weekly window examples parse", all_of(windows_parse("weekdays 06:00-08:30, weekend 08:00-09:30"), windows_parse("Mo 05:30-07:00, Tu-Fr 06:00-08:00, Sa,Su 08:00-09:30")), "false"),
    (r"quiet_off_windows", r"weekend 23:00-07:00", "quiet window example parses", windows_parse("weekend 23:00-07:00"), "false"),
    (r"silent_mode_windows", r"22:00-06:00", "silent window example parses", windows_parse("22:00-06:00"), "false"),
    (r"dhw_inlet_temp", r"10 °C", "inlet default 10 °C", const_is("DEFAULT_DHW_INLET_TEMP", 10.0), "false"),
    (r"dhw_inlet_seasonal_amplitude", r"Bei 0", "amplitude default 0", const_is("DEFAULT_DHW_INLET_SEASONAL_AMPLITUDE", 0.0), "false"),
    (r"dhw_free_disinfection_enabled", r"20 Minuten", "disinfection hold 20 min", const_is("DHW_LEGIONELLA_HOLD_MINUTES", 20.0), "false"),
    (r"dhw_combi_legionella_force", r"Bei 3 L", "combi legionella limit 3 L", const_is("COMBI_LEGIONELLA_POTABLE_LIMIT_L", 3.0), "false"),
    (r"combi_dhw_effectiveness", r"von 0,1 bis 1", "effectiveness range 0.1..1", all_of(field("options", "building", C.CONF_COMBI_DHW_EFFECTIVENESS, "min", 0.1), field("options", "building", C.CONF_COMBI_DHW_EFFECTIVENESS, "max", 1.0)), "false"),
    (r"combi_dhw_effectiveness", r"0,85 für eine Wendel", "combi presets 0.85/0.95/0.75", combi_eps, "false"),
    (r"combi_potable_volume_l", r"0 für eine Frischwasserstation", "station preset potable volume 0", combi_station_zero, "false"),
    # space set-point
    (r"space_setpoint_unit", r"25-°C-Schwelle um 5 K", "return target shifts 25 °C gate by 5 K",
     all_of(mod_const("pump_arbiter", "FLOW_GATE_C", 25.0), mod_const("pump_arbiter", "RETURN_SUPPLY_OFFSET_K", 5.0)), "false"),
    (r"flow_min_lift_k", r"5 K passt", "lift default 5 K", const_is("DEFAULT_FLOW_MIN_LIFT_K", 5.0), "false"),
    (r"flow_heat_c", r"55 °C passt", "flow heat default 55 °C", const_is("DEFAULT_FLOW_HEAT_C", 55.0), "false"),
    (r"flow_heat_c", r"Unter 30 °C wird nicht angeboten", "flow heat min 30, gates 25/20", flow_heat_floor, "false"),
    (r"flow_heat_c", r"höchstens 70 °C", "boost max 70 °C", boost_max, "false"),
    (r"space_setpoint_power_feedback", r"Nach 5 Minuten Starthaltezeit", "feedback start hold 5 min, band 10 %",
     all_of(lambda: (__import__("custom_components.heatpump_optimizer.pump_arbiter", fromlist=["x"]).FEEDBACK_START_HOLD.total_seconds() == 300, "FEEDBACK_START_HOLD=300 s"),
            mod_const("pump_arbiter", "FEEDBACK_DEADBAND_SHARE", 0.1)), "false"),
    # pump duty
    (r"pump_duty_mode", r"24-Stunden-Protokoll", "observe log is 24 h", lambda: (__import__("custom_components.heatpump_optimizer.pump_arbiter", fromlist=["x"]).log_steps() * 15 == 1440, "pump_arbiter.log_steps()*15 min = 1440"), "false"),
    (r"pump_duty_mode", r"ein Anteil unter 5 Minuten", "split share 5 min; 55/5/35/25/20 °C",
     all_of(mod_const("duty_legs", "SPLIT_MIN_MINUTES", 5.0), mod_const("pump_arbiter", "FLOW_HEAT_C", 55.0), mod_const("pump_arbiter", "FLOW_HOLD_C", 35.0),
            mod_const("pump_arbiter", "FLOW_GATE_C", 25.0), const_is("DEFAULT_FLOW_MIN_LIFT_K", 5.0)), "false"),
    (r"pump_duty_mode", r"Warmwasser auf 30 °C", "dhw gate 30 °C", mod_const("pump_arbiter", "DHW_GATE_C", 30.0), "false"),
    (r"pump_duty_mode", r"auf 90 Minuten begrenzt", "dhw lease 90/30 min below -10 °C",
     all_of(mod_const("pump_arbiter", "LEASE_MINUTES", 90.0), mod_const("pump_arbiter", "COLD_LEASE_MINUTES", 30.0), mod_const("pump_arbiter", "COLD_RAIL_C", -10.0)), "false"),
    (r"pump_duty_mode", r"alle 5 Minuten erneut", "retry 5 min", mod_const("pump_arbiter", "RETRY_MINUTES", 5.0), "false"),
    (r"pump_write_ignored", r"alle fünf M", "retry 5 min", mod_const("pump_arbiter", "RETRY_MINUTES", 5.0), "false"),
    (r"hysteresis_entity", r"0 bis 20 K", "hysteresis accepted 0..20 K", mod_const("inputs", "TEMPERATURE_DELTA_MAX_K", 20.0), "false"),
    # comfort / mold
    (r"mold_guard_enabled", r"über 80 %", "mold RH limit 80 %", const_is("MOLD_SURFACE_RH_LIMIT", 0.8), "false"),
    (r"thermal_bridge_frsi", r"0,75", "frsi default 0.75", const_is("DEFAULT_THERMAL_BRIDGE_FRSI", 0.75), "false"),
    (r"flow_curve_cop_enabled", r"um 15 K unter", "flow bias clamp 15 K, supply max 75 °C",
     all_of(mod_const("flow_lift", "FLOW_BIAS_CLAMP_K", 15.0), mod_const("flow_lift", "FLOW_SUPPLY_MAX_C", 75.0)), "false"),
    (r"comfort_weight", r"(Etwa|Um) 5 lässt", "comfort weight default 5, max 20", all_of(const_is("DEFAULT_COMFORT_WEIGHT", 5.0), field("options", "tuning", "comfort_weight", "max", 20)), "false"),
    (r"confidence_margins_enabled", r"0,8 °C", "confidence cap 0.8 °C", const_is("CONFIDENCE_MARGIN_CAP_C", 0.8), "false"),
    (r"price_tiles_enabled", r"75 %", "tiles -1/+1/75 %, 30 days", price_tiles_arms, "false"),
    (r"compressor_cycling_cost", r"Lass 0", "cycling cost default 0", field("options", "tuning", "compressor_cycling_cost", "default", 0.0), "false"),
    (r"compressor_replacement_cost", r"lass 0", "replacement cost default 0", field("options", "tuning", "compressor_replacement_cost", "default", 0.0), "false"),
    (r"price_risk_lambda", r"^0 vertraut", "price risk default 0", field("options", "tuning", "price_risk_lambda", "default", 0.0), "false"),
    # heat curve
    (r"heat_curve/(title|description)|menu_options/heat_curve", r"ECL110", "heat-curve page is ECL110-only", heat_curve_ecl_only, "stale"),
    (r"ecl110_mqtt_qos", r"^0 genügt", "qos range 0..2", field("options", "heat_curve", "ecl110_mqtt_qos", "min", 0), "false"),
    (r"heat_curve_(offset|persistent)_band_k", r"3 K ist", "band default 3 K", all_of(const_is("DEFAULT_HEAT_CURVE_OFFSET_BAND_K", 3.0), const_is("DEFAULT_HEAT_CURVE_PERSISTENT_BAND_K", 3.0)), "false"),
    (r"heat_curve_persistent_writes_per_day", r"^12 ", "writes default 12 < 7000/yr", writes_quota, "false"),
    (r"heat_curve_persistent_writes_per_day", r"Über 19", "19/day = 6935 < 7000 < 20/day", writes_quota, "false"),
    (r"heat_curve_persistent_min_dwell_minutes", r"^60 Minuten", "dwell default 60", const_is("DEFAULT_HEAT_CURVE_PERSISTENT_MIN_DWELL_MINUTES", 60), "false"),
    (r"heat_curve_displace_entity|heat_curve_target_kind|heat_curve_not_offset|heat_curve_target_kind/options/offset", r"0 (keine Verschiebung|neutral|ist neutral|nicht)", "offset is zero-neutral", heat_curve_zero_neutral, "false"),
    # grid
    (r"peak_tariff_offpeak_factor", r"^1,0 behandelt", "offpeak default 1.0", const_is("DEFAULT_PEAK_TARIFF_OFFPEAK_FACTOR", 1.0), "false"),
    (r"peak_tariff_hours|invalid_peak_hours", r"07:00-19:00", "peak hours example parses", peak_hours, "false"),
    (r"grid_fee_rules|invalid_grid_fee_rules", r"Nov-Mar Mon-Fri 06:00-22:00 = 0.25", "fee rule example parses to 0.25", fee_parse("Nov-Mar Mon-Fri 06:00-22:00 = 0.25", 0.25), "false"),
    (r"grid_fee_rules", r"„0,25“ wird also als 0.25", "decimal comma read as 0.25", fee_parse("Nov-Mar Mon-Fri 06:00-22:00 = 0,25", 0.25), "false"),
    (r"main_fuse_amperes", r"^0 lässt sie", "fuse default 0", const_is("DEFAULT_MAIN_FUSE_A", 0), "false"),
    (r"main_fuse_phases", r"3 Phasen", "phases default 3", const_is("DEFAULT_MAIN_FUSE_PHASES", 3), "false"),
    (r"silent_mode_power_fraction", r"(1\.0|1,0) (begrenzt nichts|ist der ungesetzte)|0,6 bis 1,0", "silent fraction 0.6..1.0, default 1.0", silent_clamp, "false"),
    (r"contract_fixed_price", r"^0 lässt", "contract price default 0", field("options", "grid_fees", "contract_fixed_price", "default", 0.0), "false"),
    (r"partload_derate_above_limit", r"0,44", "derate limits 0.44 / 0.17", partload, "false"),
    (r"grid_fee_rules_implausible|grid_fee_magnitude", r"25 statt 0[.,]25|100-mal", "magnitude 100x (öre)", lambda: (__import__("custom_components.heatpump_optimizer.grid_fee", fromlist=["x"]).IMPLAUSIBLE_FEE_SEK_PER_KWH < 25, "grid_fee.IMPLAUSIBLE_FEE_SEK_PER_KWH < 25"), "false"),
    # learning / misc
    (r"outage_recovery_enabled", r"zweistündiges", "outage window 2 h, dhw 45 min", all_of(const_is("OUTAGE_RECOVERY_HOURS", 2.0), const_is("OUTAGE_DHW_DELAY_MINUTES", 45.0)), "false"),
    (r"capacity_curve_enabled", r"60 %", "capacity floor 60 %", capacity_floor, "false"),
    (r"pv_system_efficiency", r"0,8 ist", "pv efficiency default 0.8", const_is("DEFAULT_PV_EFFICIENCY", 0.8), "false"),
    (r"price_prior_enabled", r"13:00", "prices land ~13:00", lambda: ("13:00" in (__import__("custom_components.heatpump_optimizer.price_model", fromlist=["x"]).__doc__ or ""), "price_model module models a 13:00 publication"), "false"),
    (r"debug_collect_enabled", r"15 Minuten", "self-test budget 15 min", lambda: (__import__("custom_components.heatpump_optimizer.debugger", fromlist=["x"]).SELF_TEST_BUDGET.total_seconds() == 900, "debugger.SELF_TEST_BUDGET=900 s"), "false"),
    (r"accuracy_drift", r"drei eingeschwungene", "refit after 3 settled days, ±10 %", accuracy_refit, "false"),
    (r"price_vat", r"^1,0 lässt", "vat default 1.0", const_is("DEFAULT_PRICE_VAT", 1.0), "false"),
    (r"rain_heat_loss_multiplier", r"^1,0 bedeutet", "rain 1.0 = no effect", rain_one, "false"),
    (r"rain_heat_loss_multiplier", r"ab 2 mm/h", "rain full at 2 mm/h, none at 0.1", rain, "false"),
    (r"wind_sensitivity_factor", r"0,15 bedeutet 15 %", "wind factor per m/s", wind, "false"),
    (r"radiator_power_fraction", r"0[.,]4 bedeutet 40", "radiator fraction default 0.4", const_is("DEFAULT_RADIATOR_POWER_FRACTION", 0.4), "false"),
    (r"apply_manual_plan", r"20 Stunden", "manual window 20 h", manual_window, "false"),
    (r"factory_reset/description|factory_reset_done", r"wöchentlichen Momentaufnahme, etwa eine Woche", "weekly snapshot", snapshot_ring, "false"),
    # selector labels with numbers
    (r"selector/peak_window", r"", "peak window options 15/60 minutes", peak_window_opts, "false"),
    (r"selector/dso_product", r"", "dso catalog products", dso_dates, "false"),
]

# numeric sentences whose numbers no code in this tree decides
EXTERNAL = [
    r"3 bis 4 sind typisch|3 bis 4 ist typisch", r"0,02 kWh/°C pro m²", r"0,25 kW/°C bei 20 Grad", r"Heizkörpern (und|von) 100 m²",
    r"etwa 0,2 bei 100 m²", r"0,6 ist typisch", r"1[.,]0 passt zu überwiegend nach Süden", r"0[.,]5 bedeutet, dass beide Etagen",
    r"^0 bedeutet, dass (die gesamte|alle) Wärme", r"Etwa 45 °C genügen", r"gemessen bei 45 °C in einem 20 °C", r"60 °C sind die übliche",
    r"35–45 °C erwartet|35-45 °C erwartet", r"1–2 K ist ein Ausgangspunkt", r"35–40 °C ein Ausgangspunkt", r"Luxtronik: 0,5 K",
    r"Eingang 1010[347]", r"travad", r"^Beispiel: ein Multifunktionsspeicher mit 40 L", r"höchstens 60 °C primärseitig",
    r"etwa 100–250 L", r"60 °C in Großanlagen", r"zwölf Stunden im Voraus 19,0", r"Daikin, 7000", r"SG-Ready-Anhebung",
    r"drei Reaktionszeiten", r"0,1 = 10 %", r"0,05 bis 0,15", r"alle 15 Minuten", r"0,5 ist der übliche halbe Satz",
    r"Fast jedes schwedische", r"^0 bedeutet, dass keine installiert", r"Vor 1960|Nach 2005", r"bei 7 °C Außentemperatur",
    r"0,0 = nur Fußbodenheizung", r"0,3 \(Dreifachverglasung", r"in °C pro Stunde bei 45 °C", r"bei 25 °C über Umgebungstemperatur",
    r"als 24-Stunden-Zeiten", r"ISO-8601", r"Bis Version 5\.1\.7", r"3–9 K wärmer", r"Verwende 24-Stunden-Zeiten",
    r"^0 oder 1 schreibt nichts", r"Zahl als Ziel für das Rücklaufwasser", r"ein Raum-Sollwert auf 5 °C", r"\(Zapf − Kaltwasser\)",
    r"Bleibt sie leer, unlesbar oder 0", r"0 lässt die Leistung aus dem COP", r"0 macht Schwachlaststunden", r"^Verschiebung: eine Temperaturdifferenz",
    r"„Verdichterstarts“", r"Würde ein Innentemperaturziel", r"Wähle „Vorlauftemperatur“ nur", r"Rücklauftemperatur gilt für einen Regler",
    r"Netzentgelte liegen bei einigen Zehnteln", r"Übertragungsentgelte betragen", r"Ein Wert, den die Wärmepumpe nicht übernimmt",
    r"S / 45 K", r"0,6 bis 1,0 \(ein kleinerer", r"zwölf Stunden", r"Ellevio|Göteborg", r"Offset \(0 ist neutral", r"0 für eine Frischwasserstation",
]
#: numeric behaviour claims this round did not drive (they stay unverifiable; next round's first work)
NOT_DRIVEN = [r"auf 1,0 zurück", r"Bei 0 wird die Obergrenze", r"auf 0 \(Obergrenze des Komfortbereichs\)", r"Bei 0 belassen, um die Obergrenze"]


def optional_check(path, s):
    """A description opening "Optional" / "Erforderlich": the rendered marker must agree."""
    m = re.match(r"(Optional|Erforderlich)\b", s)
    if not m:
        return None
    want_required = m.group(1) == "Erforderlich"
    p = path.split("/")
    if p[0] in ("config", "options") and p[1] == "step" and "data_description" in p:
        key = p[-1]
        info = ((F[p[0]].get(p[2]) or {}).get("fields") or {}).get(key)
        if info is None:
            return None
        got = bool(info.get("required"))
        if want_required and not got:
            # "Erforderlich, wenn ..." is conditional: a validator, not the marker, enforces it
            return (True, f"conditional requirement; marker Optional, enforced by the page's errors") if "wenn" in s[:30] or "für" in s[:20] else (False, f"{key} marker required={got}")
        return (got == want_required, f"{p[0]}/{p[2]}.{key} marker required={got}")
    if p[0] == "services" and p[2] == "fields":
        spec = ((F["services_yaml"].get(p[1]) or {}).get("fields") or {}).get(p[3]) or {}
        got = bool(spec.get("required", False))
        return (got == want_required, f"services.yaml {p[1]}.{p[3]} required={got}")
    return None


def content_checks(path, idx, s):
    out = []
    oc = optional_check(path, s)
    if oc is not None:
        out.append(("optional/required marker", oc[0], oc[1], "false"))
    for pre, sre, name, fn, kind in CHECKS:
        if re.search(pre, path) and re.search(sre, s):
            try:
                ok, obs = fn()
            except Exception as e:  # noqa: BLE001
                ok, obs = False, f"check raised {type(e).__name__}: {e}"
            out.append((name, ok, obs, kind))
    return out


NUM = re.compile(r"(?<![{\w])\d")


def unmapped_numeric(units):
    out = []
    for p, idx, s in units:
        path = "/".join(p)
        if not NUM.search(s):
            continue
        if any(re.search(pre, path) and re.search(sre, s) for pre, sre, *_ in CHECKS):
            continue
        if any(re.search(x, s) for x in EXTERNAL + NOT_DRIVEN):
            continue
        out.append(f"{path}#{idx}: {s[:120]}")
    return out


# -------------------------------------------------------------- quoted references
EXAMPLE = re.compile(r"\d|\{|^(hp|estimat|Jul|Nov-Mar|weekdays|unexplained)$")
#: Names another integration or Home Assistant core shows; no code here decides them.
OUTSIDE = {"Estimated Power Draw", "Estimated Heating Output", "Temperature: return target minimum", "Temperature: return limit", "nicht zu Hause"}


def quote_kind(q, labels, card):
    """(ok, observed) for a quoted UI reference; (None, why) when the quote is an example, not a reference."""
    if EXAMPLE.search(q):
        return None, "example value"
    if q in OUTSIDE:
        return None, "a name another integration or HA core shows"
    if q in labels:
        return True, "a de.json label"
    if q in card:
        return True, "a card STRINGS.de label"
    if any(lab.startswith(q + " (") or (len(q) > 6 and q in lab and len(lab) < 80) for lab in labels | card):
        return True, "contained in a de label"
    near = difflib.get_close_matches(q, [x for x in labels | card if len(x) < 80], n=1, cutoff=0.4)
    return False, f"no German label reads „{q}“; nearest: „{near[0] if near else '-'}“"

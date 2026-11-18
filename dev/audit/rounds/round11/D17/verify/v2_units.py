"""D17 verifier V2: independent unit-level measurements, one RESULT per finding.

Run from the export root:
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D17/verify/v2_units.py
Each block calls the production symbol directly (no finder rig) under its own metric.
"""
import os, sys, json, subprocess, re
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import numpy as np
from datetime import datetime, timezone
from heatpump_optimizer import const, thermal_model as tm, power_guard as pg, silent_mode as sm, snapshots, dhw_schedule as ds
from heatpump_optimizer import config_flow as cf


def R(k, v):
    print(f"RESULT {k}={v}", flush=True)


def safe(name, fn):
    try:
        fn()
    except Exception as e:  # noqa
        import traceback; traceback.print_exc()
        R(name + "_ERROR", repr(e))


# ---- D17-s1-01
def s1_01():
    strings = json.load(open("custom_components/heatpump_optimizer/strings.json"))
    flat, sect = set(), set()
    for step, body in strings["options"]["step"].items():
        for k in (body.get("data") or {}):
            flat.add(f"{step}.{k}")
        for sec in (body.get("sections") or {}).values():
            for k in (sec.get("data") or {}):
                sect.add(f"{step}.{k}")
    out = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d17-features"],
                         capture_output=True, text=True).stdout
    printed = set()
    for line in out.splitlines():
        m = re.search(r"option\s+(\w+)\.(\w+)", line)
        if m:
            printed.add(f"{m.group(1)}.{m.group(2)}")
    R("s1_01_declared", len(flat | sect)); R("s1_01_sectioned", len(sect))
    R("s1_01_sectioned_not_printed", len(sect - printed))
    R("s1_01_flat_not_printed", len((flat - sect) - printed))
    R("s1_01_weekend_holiday_printed", sum(1 for p in printed if "weekend" in p or "holiday" in p))


# ---- D17-s1-02
def s1_02():
    C = const
    src_of = {C.CONF_COMFORT_TEMP_DAY_WEEKEND: C.CONF_COMFORT_TEMP_DAY, C.CONF_HOLIDAY_COMFORT_DAY: C.CONF_COMFORT_TEMP_DAY,
              C.CONF_COMFORT_TEMP_NIGHT_WEEKEND: C.CONF_COMFORT_TEMP_NIGHT, C.CONF_HOLIDAY_COMFORT_NIGHT: C.CONF_COMFORT_TEMP_NIGHT,
              C.CONF_DAY_START_HOUR_WEEKEND: C.CONF_DAY_START_HOUR, C.CONF_HOLIDAY_DAY_START_HOUR: C.CONF_DAY_START_HOUR,
              C.CONF_DAY_END_HOUR_WEEKEND: C.CONF_DAY_END_HOUR, C.CONF_HOLIDAY_DAY_END_HOUR: C.CONF_DAY_END_HOUR}
    A = {C.CONF_COMFORT_TEMP_DAY: 22.5, C.CONF_COMFORT_TEMP_NIGHT: 19.0, C.CONF_DAY_START_HOUR: 7, C.CONF_DAY_END_HOUR: 22}
    B = {C.CONF_COMFORT_TEMP_DAY: 21.0, C.CONF_COMFORT_TEMP_NIGHT: 18.0, C.CONF_DAY_START_HOUR: 6, C.CONF_DAY_END_HOUR: 21}
    rows = [r for r in cf._OPTION_FIELDS if isinstance(r.default, cf._Computed) and r.key in src_of]
    lost = null = 0
    for row in rows:
        s = src_of[row.key]
        for submit, arm in ((B, "x"), (A, "null")):
            current = {s: A[s]}
            cleaned = cf._omit_unstored_computed({s: submit[s], row.key: A[s]}, current, None)
            stored = {**current, **cleaned}
            if stored.get(row.key, stored[s]) != A[s]:
                if arm == "x":
                    lost += 1
                else:
                    null += 1
    R("s1_02_rows", len(rows)); R("s1_02_kept_value_lost", lost); R("s1_02_null_lost", null)


def traj_delta(base_cfg, key, a, b):
    outs = []
    for val in (a, b):
        p = tm.ThermalParameters.from_config({**base_cfg, key: val})
        m = tm.ThermalModel(p)
        st = tm.ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=-5.0,
                             upper_floor_temperature=21.0, lower_floor_temperature=21.0)
        n = 96
        pw = np.where(np.arange(n) % 8 < 3, 3.0, 0.0)
        res = m.simulate_trajectory(st, pw, tm.WeatherSeries(outdoor_temps=np.full(n, -5.0)))
        outs.append((p.two_zone_enabled, np.concatenate([np.asarray(r, float).ravel() for r in res if r is not None])))
    return outs[0][0], float(np.nanmax(np.abs(outs[0][1] - outs[1][1])))


def s1_03_s3_02():
    for mode in ("on", "off", None):
        cfg = {} if mode is None else {const.CONF_TWO_ZONE_MODE: mode}
        tz, d = traj_delta(cfg, const.CONF_HOUSE_THERMAL_MASS, 10.0, 40.0)
        R(f"s1_03_mass_10_40_maxdeltaK[{mode}|two_zone={tz}]", round(d, 6))
        tz, d = traj_delta(cfg, const.CONF_HOUSE_THERMAL_MASS, 10.0, 3.0)
        R(f"s3_02_mass_10_3_maxdeltaK[{mode}|two_zone={tz}]", round(d, 6))
        tz, d = traj_delta(cfg, const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT, 0.15, 0.35)
        R(f"s3_02_hlc_015_035_maxdeltaK[{mode}|two_zone={tz}]", round(d, 6))
    row = [r for r in cf._OPTION_FIELDS if r.key == const.CONF_HOUSE_THERMAL_MASS][0]
    R("s1_03_house_mass_row_when", getattr(row, "when", None))


def s1_04():
    for mode in ("on_off", "modulating", "auto"):
        p = tm.ThermalParameters.from_config({const.CONF_COMPRESSOR_MODULATION: mode})
        R(f"s1_04_declared[{mode}]", tm.declared_modulation({const.CONF_COMPRESSOR_MODULATION: mode}))
        R(f"s1_04_params_on_off[{mode}]", getattr(p, "on_off", "n/a"))


def s1_05():
    wrong = 0; err = []
    for P in (0.8, 1.2, 1.8, 3.0, 9.0):
        for m in range(1, 60):
            proj = pg.project_window_mean(P, float(m), P, 60.0)
            err.append(proj - P)
            if (proj > 1.5) != (P > 1.5):
                wrong += 1
    R("s1_05_minutes_wrong_side_no_hysteresis", wrong)
    R("s1_05_projection_err_range_kW", f"{min(err):.3f}..{max(err):.3f}")
    R("s1_05_proj_m30_P1.2", pg.project_window_mean(1.2, 30.0, 1.2, 60.0))
    R("s1_05_proj_m59_P1.2", round(pg.project_window_mean(1.2, 59.0, 1.2, 60.0), 3))


def s2_01():
    for cfg in ({}, {const.CONF_TWO_ZONE_MODE: "auto"}, {const.CONF_TWO_ZONE_MODE: "off"},
                {const.CONF_TWO_ZONE_MODE: "on"}, {const.CONF_TWO_ZONE_MODE: "garbage"}):
        R(f"s2_01_two_zone[{cfg}]", tm.ThermalParameters.from_config(cfg).two_zone_enabled)


def s2_03():
    for valve in (None, "smart_write"):
        for tz in ("on", "off"):
            cfg = {const.CONF_WOOD_FURNACE_ENABLED: True, const.CONF_WOOD_TANK_TOP_ENTITY: "sensor.wood_top",
                   const.CONF_WOOD_TANK_VOLUME: 500, const.CONF_TWO_ZONE_MODE: tz}
            if valve:
                cfg[const.CONF_MIXING_VALVE_MODE] = valve
            p = tm.ThermalParameters.from_config(cfg)
            R(f"s2_03_layout[valve={valve},tz={tz}]", f"{p.topology_layout}|two_tank={p.two_tank_modelled}|probe={p.wood_tank_configured}")
    R("s2_03_quick_setup_mentions_valve", "mixing_valve" in open("custom_components/heatpump_optimizer/quick_setup.py").read())


def s2_04():
    start = datetime(2026, 1, 12, 0, 0, tzinfo=timezone.utc)
    for cfg in ({const.CONF_SILENT_MODE_WINDOWS: "06:00-10:00"},
                {const.CONF_SILENT_MODE_WINDOWS: "06:00-10:00", const.CONF_SILENT_MODE_FRACTION: 0.6}):
        c = sm.compose(None, cfg, start, 96, 0.25, 5.0)
        R(f"s2_04_capped_steps[fraction={cfg.get(const.CONF_SILENT_MODE_FRACTION)}]", 0 if c is None else int(np.sum(c < 5.0)))
    R("s2_04_default_fraction", const.DEFAULT_SILENT_MODE_FRACTION)


def s2_05():
    for choice in ("menu", "close"):
        saved = {const.CONF_AFTER_SAVE: choice, const.CONF_SILENT_MODE_WINDOWS: "22:00-06:00"}
        kept = cf._omit_unstored_defaults(cf._omit_unstored_computed(saved, {}, None), {})
        R(f"s2_05_after_save_kept[{choice}]", const.CONF_AFTER_SAVE in kept)


def s3_03():
    ring = snapshots.SnapshotRing()
    ring.snapshots = [{"taken_at": "2026-11-10T00:00:00+00:00", "healthy": True,
                       "accuracy": {"temperature_bias": None}}]
    R("s3_03_none_bias_qualifies", ring.best_restore() is not None)
    ring.snapshots = [{"taken_at": "2026-11-10T00:00:00+00:00", "healthy": True,
                       "accuracy": {"temperature_bias": 5.0}}]
    R("s3_03_null_outofband_qualifies", ring.best_restore() is not None)


def s3_51():
    spec = "weekdays 06:00-08:30, weekend 08:00-09:30"
    flat = ds.parse_windows(spec); weekly = ds.parse_weekly_windows(spec)
    p = tm.ThermalParameters.from_config({const.CONF_DHW_WINDOWS: spec, const.CONF_DHW_ENABLED: True})
    union = p.dhw_demand_windows
    diff = 0
    for d in range(7):
        day = ds.windows_for_day(weekly, d, flat)
        for h in range(48):
            hr = h / 2 + 0.25
            if ds.hour_in_windows(hr, union) != ds.hour_in_windows(hr, day):
                diff += 1
    R("s3_51_union", union); R("s3_51_params_dhw_windows", getattr(p, "dhw_windows", None))
    R("s3_51_cells_wrong_midpoint", diff)


for name, fn in (("s1_01", s1_01), ("s1_02", s1_02), ("s1_03", s1_03_s3_02), ("s1_04", s1_04), ("s1_05", s1_05),
                 ("s2_01", s2_01), ("s2_03", s2_03), ("s2_04", s2_04), ("s2_05", s2_05), ("s3_03", s3_03), ("s3_51", s3_51)):
    safe(name, fn)

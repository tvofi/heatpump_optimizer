#!/usr/bin/env python3
"""D7.M8 (round 11, seat D7-s3): the agreement test over rules written twice.

Metric (one line): per family of implementations of one rule, the number of shared probes on
which the implementations do not return the same answer (`disagreements`), each
implementation called as production code, none re-implemented here.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m8_agree.py            # every family
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m8_agree.py --only temperature_roundtrip
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m8_agree.py --perturb  # each family's fix, in memory
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m8_agree.py --seams    # the seam rules, as code

Instrumented symbols: named per family in FAMILIES (`module:symbol`).
Count key: the value the production function returns for the probe; nothing is keyed on a
label of this harness. Perturbation (`--perturb`): per family, the one-line production edit
that makes the copies one rule, applied with an attribute swap; `disagreements` must fall to 0.
Counts only. Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, Darwin arm64, Python 3.14.7.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import ast
import glob
import math
import sys
import time
import types
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.getcwd())
PKG = "custom_components.heatpump_optimizer"
PKG_DIR = os.path.join("custom_components", "heatpump_optimizer")


def mod(name):
    import importlib
    return importlib.import_module(PKG + "." + name)


def same(a, b, tol=1e-9):
    if isinstance(a, float) and isinstance(b, float):
        if math.isnan(a) and math.isnan(b):
            return True
        return abs(a - b) <= tol * max(1.0, abs(a), abs(b))
    return a == b


# ---------------------------------------------------------------- families

def fam_temperature_roundtrip(perturb):
    """inputs.py:normalize_temperature_c and inputs.py:temperature_from_c are one conversion
    written forwards and backwards over const.TEMPERATURE_UNIT_TO_C."""
    inputs = mod("inputs")
    orig = inputs.temperature_from_c
    if perturb:
        def fixed(value_c, unit):
            spec = inputs.TEMPERATURE_UNIT_TO_C.get(str(unit).strip())
            if spec is None:
                return value_c
            offset, factor = spec
            return value_c / factor - offset
        inputs.temperature_from_c = fixed
    try:
        rows = []
        for unit in sorted(inputs.TEMPERATURE_UNIT_TO_C):
            for c in (-20.0, 0.0, 21.5, 55.0, 100.0):
                back = inputs.normalize_temperature_c(inputs.temperature_from_c(c, unit), unit)
                rows.append(((unit, c), same(back, c, 1e-9), "wrote %r read back %r" % (
                    inputs.temperature_from_c(c, unit), back)))
        return rows
    finally:
        inputs.temperature_from_c = orig


def fam_dhw_store_tap(perturb):
    """thermal_model.py:DhwStore.store_temp_for_tap and .tap_temp_for_store are inverses."""
    tm = mod("thermal_model")
    rows = []
    for combi in (False, True):
        for eff in (0.5, 0.75, 1.0):
            st = tm.DhwStore(capacity_kwh_per_c=0.3, ua_kw_per_c=0.002, volume_l=300.0, charge_max_temp=60.0,
                             rating_max_temp=70.0, effectiveness=eff, inlet_c=8.0, combi=combi)
            for tap in (30.0, 45.0, 55.0, 65.0):
                back = st.tap_temp_for_store(st.store_temp_for_tap(tap))
                rows.append(((combi, eff, tap), same(back, tap), "back %r" % back))
    return rows


class _Plan(types.SimpleNamespace):
    pass


def fam_step_covering_now(perturb):
    """`the plan step covering now`: coordinator.py:_covering_index, pump_arbiter.py:_step_index,
    pump_arbiter.py:_planned_room, early_cutoff.py:_planned_room. The agreed answer past the
    plan's last step is `no step` (the first two; R10 N-no-expiry)."""
    coord = mod("coordinator")
    arb = mod("pump_arbiter")
    cut = mod("early_cutoff")
    step = timedelta(minutes=arb.PLAN_STEP_MINUTES)
    t0 = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)
    stamps = [t0 + i * step for i in range(8)]
    plan = _Plan(timestamps=stamps, optimal_setpoints=[20.0 + i for i in range(8)],
                 room_temp_trajectory=[19.0 + 0.1 * i for i in range(9)])
    saved = (arb._planned_room, cut._planned_room)
    if perturb:
        def arb_fixed(result, now, attr="optimal_setpoints"):
            i = arb._step_index(result, now)
            points = list(getattr(result, attr, None) or [])
            return points[i] if i is not None and i < len(points) else None

        def cut_fixed(plan_, now):
            i = arb._step_index(plan_, now)
            traj = list(getattr(plan_, "room_temp_trajectory", None) or [])
            return [float(traj[i + 1])] if i is not None and i < len(traj) - 1 else []
        arb._planned_room, cut._planned_room = arb_fixed, cut_fixed
    try:
        rows = []
        probes = [("before", t0 - step), ("first", t0), ("mid", t0 + 3.5 * step),
                  ("last", stamps[-1] + step / 2), ("end_edge", stamps[-1] + step),
                  ("one_step_past", stamps[-1] + 2 * step), ("three_hours_past", stamps[-1] + timedelta(hours=3)),
                  ("a_day_past", stamps[-1] + timedelta(days=1))]
        for name, now in probes:
            a = coord._covering_index(stamps, now, step)
            b = arb._step_index(plan, now)
            c = arb._planned_room(plan, now)
            d = cut._planned_room(plan, now)
            covers = [a is not None, b is not None, c is not None, bool(d)]
            rows.append((name, len(set(covers)) == 1,
                         "_covering_index=%r _step_index=%r arbiter._planned_room=%r early_cutoff._planned_room=%r" % (a, b, c, d)))
        return rows
    finally:
        arb._planned_room, cut._planned_room = saved


def _novalue_literals():
    """The seam rule as code: every tuple/set/frozenset literal of the package that holds both
    "unknown" and "unavailable"."""
    out = []
    for f in sorted(glob.glob(os.path.join(PKG_DIR, "*.py"))):
        for n in ast.walk(ast.parse(open(f, encoding="utf-8").read())):
            if isinstance(n, (ast.Tuple, ast.Set, ast.List)):
                try:
                    vals = [ast.literal_eval(e) for e in n.elts]
                except Exception:
                    continue
                if "unknown" in vals and "unavailable" in vals and all(v is None or isinstance(v, str) for v in vals):
                    if not ({"true", "false"} & set(vals)):
                        out.append(("%s:%d" % (os.path.basename(f), n.lineno), set(vals)))
    return out


def fam_no_value_state(perturb):
    """`a state that holds no value`: every literal the seam rule finds, compared member by member."""
    lits = _novalue_literals()
    if perturb:
        # a static comparison of production literals: its perturbation is the union every
        # site would hold if they read one constant. Reported, never counted in a finding.
        union = set().union(*(v for _s, v in lits))
        lits = [(s, set(union)) for s, _v in lits]
    rows = []
    for probe in ("unknown", "unavailable", "none", "", None):
        answers = {site: (probe in vals) for site, vals in lits}
        rows.append((repr(probe), len(set(answers.values())) == 1,
                     "no-value at: " + ",".join(s for s, a in answers.items() if a) +
                     " | a value at: " + ",".join(s for s, a in answers.items() if not a)))
    return rows


def fam_naive_instant(perturb):
    """`which zone a naive instant is in`: drift.py:_as_utc, coordinator.py:_utc_age_seconds
    (dt_util.as_utc), open_meteo.py:_ensure_utc, manual_plan.py:_instant."""
    drift, coord, om, mp = mod("drift"), mod("coordinator"), mod("open_meteo"), mod("manual_plan")
    from homeassistant.util import dt as dt_util
    from zoneinfo import ZoneInfo
    saved_zone = getattr(dt_util, "DEFAULT_TIME_ZONE", None)
    saved_tz = os.environ.get("TZ")
    saved_fn = om._ensure_utc
    rows = []
    try:
        if perturb:
            om._ensure_utc = drift._as_utc  # one reading of a naive instant: drift's
        if hasattr(dt_util, "set_default_time_zone"):
            dt_util.set_default_time_zone(ZoneInfo("Europe/Stockholm"))
        else:
            dt_util.DEFAULT_TIME_ZONE = ZoneInfo("Europe/Stockholm")
        os.environ["TZ"] = "Asia/Tokyo"
        time.tzset()
        aware = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
        for name, naive in (("winter_noon", datetime(2026, 1, 10, 12, 0)), ("summer_noon", datetime(2026, 7, 10, 12, 0))):
            ref = aware.replace(year=naive.year, month=naive.month)
            a = drift.utc_elapsed_seconds(naive, ref)
            b = coord._utc_age_seconds(naive, ref)
            c = (om._ensure_utc(naive) - ref).total_seconds()
            d = mp._instant(naive) - ref.timestamp()
            vals = [a, b, c, d]
            rows.append((name, len({round(v) for v in vals}) == 1,
                         "seconds from the same aware noon: drift=%r coordinator=%r open_meteo=%r manual_plan=%r" % tuple(vals)))
        # null control: an aware instant has one reading everywhere
        a = drift.utc_elapsed_seconds(aware, aware)
        b = coord._utc_age_seconds(aware, aware)
        c = (om._ensure_utc(aware) - aware).total_seconds()
        d = mp._instant(aware) - aware.timestamp()
        rows.append(("aware_null", len({a, b, c, d}) == 1, "aware: %r %r %r %r" % (a, b, c, d)))
    finally:
        om._ensure_utc = saved_fn
        if saved_zone is not None:
            if hasattr(dt_util, "set_default_time_zone"):
                dt_util.set_default_time_zone(saved_zone)
            else:
                dt_util.DEFAULT_TIME_ZONE = saved_zone
        if saved_tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = saved_tz
        time.tzset()
    return rows


def fam_stored_number(perturb):
    """duty_switch.py:_stored_number and store.py:_number: `a stored value is a finite number in range`."""
    ds, store = mod("duty_switch"), mod("store")
    dom = store.Domain("real", 0.0, math.inf)
    rows = []
    for v in (0, 1, 2.5, -1, -0.0, True, False, float("nan"), float("inf"), "1", None, 1e308, [1]):
        a, b = ds._stored_number(v), store._number(v, dom)
        rows.append((repr(v), a == b, "duty_switch=%r store=%r" % (a, b)))
    return rows


def fam_finite_number(perturb):
    """`a finite number or nothing`: const.py:finite_float, entity.py:payload_number,
    sensor.py:_as_float, replay_doc.py:numeric."""
    import numpy as np
    const, entity, sensor, rd = mod("const"), mod("entity"), mod("sensor"), mod("replay_doc")
    rows = []
    probes = [1, 1.5, -2.0, True, None, "1.5", "abc", "", float("nan"), float("inf"), np.float64(2.0),
              np.float64("nan"), np.int64(3), "nan", "inf", " 7 ", "1e400"]
    saved = (entity.payload_number, sensor.payload_number, rd.numeric)
    if perturb:
        def one(value, types=(int, float)):
            return const.finite_float(value.item() if isinstance(value, np.generic) else value)
        entity.payload_number = sensor.payload_number = one
        rd.numeric = lambda state: const.finite_float(state) is not None
    try:
        for v in probes:
            a = const.finite_float(v.item() if isinstance(v, np.generic) else v) is not None
            b = entity.payload_number(v) is not None
            c = sensor._as_float(v) is not None
            d = bool(rd.numeric(v)) if not isinstance(v, np.generic) else None
            answers = [a, b, c] + ([d] if d is not None else [])
            rows.append((repr(v), len(set(answers)) == 1,
                         "finite_float=%r payload_number=%r _as_float=%r replay_doc.numeric=%r" % (a, b, c, d)))
        return rows
    finally:
        entity.payload_number, sensor.payload_number, rd.numeric = saved


def fam_soc(perturb):
    """battery.py:StorageComponent.soc and battery.py:VirtualBattery.soc: one state-of-charge rule."""
    bat = mod("battery")
    rows = []
    src = open(os.path.join(PKG_DIR, "battery.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    bodies = {}
    for c in tree.body:
        if isinstance(c, ast.ClassDef):
            for n in c.body:
                if isinstance(n, ast.FunctionDef) and n.name == "soc":
                    body = [b for b in n.body if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant))]
                    bodies[c.name] = body
    fns = {}
    for cname, body in bodies.items():
        fn = getattr(bat, cname).__dict__["soc"]
        fns[cname] = fn.fget if isinstance(fn, property) else fn
    for usable, stored in ((10.0, 5.0), (10.0, 12.0), (0.0, 1.0), (10.0, -2.0), (1e-12, 1.0)):
        o = types.SimpleNamespace(usable_capacity_kwh=usable, stored_kwh=stored)
        vals = {c: f(o) for c, f in fns.items()}
        rows.append(((usable, stored), len({round(v, 12) for v in vals.values()}) == 1, repr(vals)))
    return rows


def fam_water_heat(perturb):
    """`the heat that warms a litre of water by one kelvin`: thermal_model.py:ThermalParameters
    .dhw_tank_thermal_mass (const.WATER_SPECIFIC_HEAT), flow_meter.py's kW (const.WATER_CP_KJ_PER_KG_K
    x WATER_KG_PER_L) and sensor.py:_gap_probe_terms (its own literal)."""
    tm, const, sensor, fm, inputs = mod("thermal_model"), mod("const"), mod("sensor"), mod("flow_meter"), mod("inputs")
    saved_cp = const.WATER_CP_KJ_PER_KG_K
    saved_terms = sensor._gap_probe_terms
    try:
        if perturb:
            # one constant: the flow meter's and the advisor's read thermal_model's
            const.WATER_CP_KJ_PER_KG_K = const.WATER_SPECIFIC_HEAT * 3600.0 / const.WATER_KG_PER_L
            import inspect
            import textwrap
            src = textwrap.dedent(inspect.getsource(saved_terms))
            assert "(4.187 / 3600.0)" in src
            ns = dict(vars(sensor))
            ns["_D7S3_CP"] = const.WATER_SPECIFIC_HEAT
            exec(src.replace("(4.187 / 3600.0)", "_D7S3_CP"), ns)
            sensor._gap_probe_terms = ns["_gap_probe_terms"]
        p = tm.ThermalParameters()
        vol = float(p.dhw_tank_volume)
        a = p.dhw_tank_thermal_mass / vol                                 # kWh per litre per K
        kg_s = inputs.normalize_flow_kg_s(1.0, "L/s")                      # one litre a second
        b = fm.thermal_output_kw(kg_s, 1.0, 0.0) / 3600.0                  # kW for 1 K, as kWh per litre
        terms = sensor._gap_probe_terms({}, [1.0], [1.0], 1.0)
        band = float(const.DEFAULT_DHW_SETPOINT) - float(const.DEFAULT_DHW_MIN_TEMP)
        v = mod("entry_config").EntryConfig.from_mapping({}).dhw_tank_volume
        c = terms["dhw_extra_kwh"] / (v * band * 30.0)
        vals = [a, b, c]
        spread = (max(vals) - min(vals)) / min(vals)
        return [("kWh per litre per K", spread < 1e-9,
                 "thermal_model=%.7f flow_meter=%.7f sensor._gap_probe_terms=%.7f spread=%.4f%%" % (a, b, c, 100 * spread))]
    finally:
        const.WATER_CP_KJ_PER_KG_K = saved_cp
        sensor._gap_probe_terms = saved_terms


def fam_buffer_prior_in_bounds(perturb):
    """const.py:default_buffer_cooling_rate and const.py:buffer_cooling_rate_bounds derive one
    rate from one geometry: the prior lies inside its own clamp at every volume."""
    const = mod("const")
    rows = []
    for vol in (0.0, 20.0, 35.0, 100.0, 300.0, 504.0, 1000.0, 3000.0):
        lo, hi = const.buffer_cooling_rate_bounds(vol)
        d = const.default_buffer_cooling_rate(vol)
        rows.append((vol, lo - 1e-12 <= d <= hi + 1e-12, "prior %.5f in [%.5f, %.5f]" % (d, lo, hi)))
    return rows


def fam_effective(perturb):
    """comfort_band.py:effective and config_flow.py:_effective: the value a save would leave."""
    cb, cf = mod("comfort_band"), mod("config_flow")
    rows = []
    for cand, cur, key, default in (({"k": 1}, {"k": 2}, "k", 3), ({}, {"k": 2}, "k", 3), ({}, {}, "k", 3),
                                    ({"k": "4.5"}, {}, "k", 3)):
        a, b = cb.effective(cand, cur, key, default), cf._effective(cand, cur, key, default)
        rows.append(((cand, cur), a == b, "%r %r" % (a, b)))
    return rows


def fam_ua_from_rate(perturb):
    """thermal_model.py:ThermalParameters.wood_tank_heat_loss_coefficient and
    .dhw_tank_heat_loss_coefficient: UA = rate x C / reference delta, written per tank."""
    tm, const = mod("thermal_model"), mod("const")
    rows = []
    for vol in (150.0, 300.0, 600.0):
        p = tm.ThermalParameters(dhw_tank_volume=vol, wood_tank_volume=vol)
        ua_d = p.dhw_tank_heat_loss_coefficient
        ua_w = p.wood_tank_heat_loss_coefficient
        rd = ua_d * const.DHW_COOLING_REFERENCE_DELTA / p.dhw_tank_thermal_mass
        rw = ua_w * const.DHW_COOLING_REFERENCE_DELTA / p.wood_tank_thermal_mass
        rows.append((vol, same(rd, float(p.dhw_cooling_rate), 1e-9) and same(rw, const.default_buffer_cooling_rate(vol), 1e-9),
                     "dhw rate back %.5f (configured %.5f); wood rate back %.5f (prior %.5f)" % (
                         rd, p.dhw_cooling_rate, rw, const.default_buffer_cooling_rate(vol))))
    return rows


def fam_window_mean(perturb):
    """power_guard.py:project_window_mean against tariff.py's realised window mean: the
    projection of a constant draw is that draw at every point of the window (the docstring's own
    two limits: the current draw at the start, the realised average at the end)."""
    pg = mod("power_guard")
    orig = pg.project_window_mean
    if perturb:
        def fixed(mean_so_far_kw, elapsed_minutes, current_kw, window_minutes):
            window_minutes = max(float(window_minutes), 1e-6)
            elapsed = min(max(float(elapsed_minutes), 0.0), window_minutes)
            if mean_so_far_kw is None:
                elapsed = 0.0
            mean = float(mean_so_far_kw) if mean_so_far_kw is not None else 0.0
            return (mean * elapsed + float(current_kw) * (window_minutes - elapsed)) / window_minutes
        pg.project_window_mean = fixed
    try:
        rows = []
        for elapsed in (0.0, 5.0, 15.0, 30.0, 45.0, 55.0, 60.0):
            got = pg.project_window_mean(4.0, elapsed, 4.0, 60.0)
            rows.append(("constant 4 kW at minute %g" % elapsed, same(got, 4.0), "projected %.4f kW" % got))
        got = pg.project_window_mean(None, 0.0, 4.0, 60.0)
        rows.append(("no samples yet", same(got, 4.0), "projected %.4f kW" % got))
        return rows
    finally:
        pg.project_window_mean = orig



# ------------------------------------------------------------ scalar/batch twins (family E)

def _bits(a, b):
    import numpy as np
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return a.shape == b.shape and bool(np.array_equal(a, b, equal_nan=True))


def fam_twin_wood_share(perturb):
    """thermal_model.py:wood_share and thermal_model.py:_wood_share_vec, element by element."""
    import numpy as np
    tm = mod("thermal_model")
    rows = []
    for flow_set in (30.0, 38.0, 45.0):
        wood = np.array([20.0, 30.0, 36.0, 40.0, 44.0, 47.0, 52.0, 60.0, 75.0, 90.0])
        for hp in (25.0, 35.0, 45.0, 55.0):
            for floor in (22.0, 28.0):
                vec = tm._wood_share_vec(wood, np.full_like(wood, hp), flow_set, np.full_like(wood, floor))
                sca = np.array([tm.wood_share(float(w), hp, flow_set, floor) for w in wood])
                rows.append(((flow_set, hp, floor), _bits(vec, sca), "max |diff| %.3g" % float(np.max(np.abs(vec - sca)))))
    return rows


def fam_twin_topk(perturb):
    """tariff.py:_smooth_topk_sum / _plateau_aware_topk_sum and their `_batch` twins, row by row."""
    import numpy as np
    tariff = mod("tariff")
    saved = tariff._exact_topk_sum
    if perturb:
        tariff._exact_topk_sum = _fixed_exact_topk
    try:
        return _twin_topk_rows(tariff)
    finally:
        tariff._exact_topk_sum = saved


def _twin_topk_rows(tariff):
    import numpy as np
    rng = np.random.default_rng(7)
    rows = []
    mats = {"random": rng.uniform(0.0, 6.0, size=(6, 24)),
            "plateau": np.minimum(rng.uniform(0.0, 6.0, size=(6, 24)), 3.0),
            "zeros": np.zeros((3, 24)),
            "one_spike": np.eye(4, 24) * 5.0}
    for name, x in mats.items():
        for k in (1, 2, 3):
            b = tariff._smooth_topk_sum_batch(x, k, tariff._PEAK_SMOOTH_TAU)
            sc = np.array([tariff._smooth_topk_sum(r, k, tariff._PEAK_SMOOTH_TAU) for r in x])
            rows.append((("smooth", name, k), _bits(b, sc), "max |diff| %.3g" % float(np.max(np.abs(b - sc)))))
            b = tariff._plateau_aware_topk_sum_batch(x, k)
            sc = np.array([tariff._plateau_aware_topk_sum(r, k) for r in x])
            rows.append((("plateau_aware", name, k), _bits(b, sc), "max |diff| %.3g" % float(np.max(np.abs(b - sc)))))
    return rows


def fam_twin_day_peaks(perturb):
    """tariff.py:_day_peaks (under the solver's top-k rule) and tariff.py:_day_peaks_batch."""
    import numpy as np
    tariff = mod("tariff")
    rng = np.random.default_rng(11)
    rows = []
    for name, w in (("two_days", 48), ("three_days", 72)):
        x = rng.uniform(0.0, 5.0, size=(5, w))
        x[1] = np.minimum(x[1], 2.0)
        days = np.repeat(np.arange(w // 24), 24).astype(np.int64) + 739000
        for labels in (days, None):
            b = tariff._day_peaks_batch(x, labels, 60)
            sc = np.array([tariff._day_peaks(r, labels, 60, tariff._plateau_aware_topk_sum) for r in x])
            rows.append(((name, "labelled" if labels is not None else "no_labels"), _bits(b, sc),
                         "shapes %s %s" % (np.shape(b), np.shape(sc))))
    return rows


def fam_twin_peak_cost(perturb):
    """tariff.py:peak_cost_smooth and tariff.py:peak_cost_batch on one PeakBilling."""
    import numpy as np
    tariff = mod("tariff")
    saved = tariff._exact_topk_sum
    if perturb:
        tariff._exact_topk_sum = _fixed_exact_topk
    try:
        return _twin_peak_cost_rows(tariff)
    finally:
        tariff._exact_topk_sum = saved


def _twin_peak_cost_rows(tariff):
    import numpy as np
    rng = np.random.default_rng(3)
    rows = []
    n = 96
    for name, kw in (("plain", {}), ("distinct_off", {"distinct_days": False}),
                     ("offset", {"offset_steps": 2}),
                     ("days", {"window_days": np.repeat(np.arange(2), 12).astype(np.int64) + 739000})):
        bill = tariff.PeakBilling(threshold_kw=2.0, price_per_kw=50.0, window_minutes=60, dt_hours=0.25, **kw)
        total = rng.uniform(0.0, 6.0, size=(5, n))
        base = rng.uniform(0.2, 1.0, size=n)
        b = tariff.peak_cost_batch(total, base, bill)
        sc = np.array([tariff.peak_cost_smooth(r, base, bill) for r in total])
        rows.append((name, _bits(b, sc), "max |diff| %.3g" % float(np.max(np.abs(np.asarray(b) - sc)))))
    return rows


def fam_twin_switch_weight(perturb):
    """duty_legs.py:switch_weight and duty_legs.py:switch_weights_batch, row by row."""
    import numpy as np
    dl = mod("duty_legs")
    rng = np.random.default_rng(5)
    rows = []
    for name, stop in (("both", (0.3, 0.6)), ("to_dhw_only", (0.4, 0.0)), ("none", (0.0, 0.0))):
        space = rng.choice([0.0, 0.0, 1.5, 3.0, 5.0], size=(6, 32))
        dhw = rng.choice([0.0, 0.0, 0.0, 2.0, 3.0], size=32)
        b = dl.switch_weights_batch(space, dhw, stop, 6.0)
        sc = np.array([dl.switch_weight(r, dhw, stop, 6.0) for r in space])
        rows.append((name, _bits(b, sc), "max |diff| %.3g" % float(np.max(np.abs(np.asarray(b) - sc)))))
    return rows


def _suite_modules():
    """tests/profiles.py and the package under the name the suite imports it by
    (`heatpump_optimizer`, off custom_components/), so a record profiles builds is the class
    the optimizer under test reads."""
    for extra in (os.path.join(os.getcwd(), "tests"), os.path.join(os.getcwd(), "custom_components")):
        if extra not in sys.path:
            sys.path.insert(0, extra)
    import importlib
    import profiles
    return (profiles, importlib.import_module("heatpump_optimizer.thermal_model"),
            importlib.import_module("heatpump_optimizer.optimizer"),
            importlib.import_module("heatpump_optimizer.tariff"))


def _fixed_exact_topk(excess, k):
    import numpy as np
    return float(np.sum(np.sort(excess)[-k:]))


def _models():
    profiles, tm, _o, _t = _suite_modules()
    out = []
    import importlib
    mv = importlib.import_module("heatpump_optimizer.mixing_valve")
    valve_modes = [m for m in mv.MODES if m != mv.MODE_NONE]
    variants = [("single_zone", False, {}), ("two_zone", True, {}),
                ("single_zone_big_buffer", False, {"buffer_tank_volume": 500.0}),
                ("two_zone_big_buffer", True, {"buffer_tank_volume": 500.0}),
                ("single_zone_flow_carnot", False, {"cop_flow_carnot": True}),
                ("two_zone_flow_curve", True, {"flow_curve_cop": True}),
                ("two_zone_wood", True, {"wood_tank_configured": True, "wood_tank_volume": 600.0, "buffer_tank_volume": 500.0}),
                ("two_zone_wood_coil", True, {"wood_tank_configured": True, "wood_tank_volume": 600.0,
                                              "buffer_tank_volume": 500.0, "dhw_wood_coil_enabled": True})]
    for mode in valve_modes:
        variants.append(("two_zone_valve_%s" % mode, True, {"mixing_valve_mode": mode, "buffer_tank_volume": 500.0}))
        variants.append(("single_zone_valve_%s" % mode, False, {"mixing_valve_mode": mode, "buffer_tank_volume": 500.0}))
    for name, two_zone, over in variants:
        p = tm.ThermalParameters.from_config(profiles.house(two_zone=two_zone))
        for key, value in over.items():
            setattr(p, key, value)
        out.append((name, tm.ThermalModel(p)))
    return profiles, tm, out


def fam_twin_trajectory(perturb):
    """thermal_model.py:ThermalModel.simulate_trajectory and .simulate_trajectory_batch: every
    row of the batch is the scalar path's trajectory, to the bit (the batch docstring's contract)."""
    import importlib
    for extra in (os.path.join(os.getcwd(), "tests"), os.path.join(os.getcwd(), "custom_components")):
        if extra not in sys.path:
            sys.path.insert(0, extra)
    mv = importlib.import_module("heatpump_optimizer.mixing_valve")
    saved = mv.emitter_delivery
    if perturb:
        def clamped(*, mix_temp, zone_temp, ua):
            return max(0.0, ua * (mix_temp - zone_temp))   # the docstring's "never negative"
        mv.emitter_delivery = clamped
    try:
        return _twin_trajectory_rows()
    finally:
        mv.emitter_delivery = saved


def _twin_trajectory_rows():
    import numpy as np
    from datetime import datetime
    profiles, tm, models = _models()
    rng = np.random.default_rng(1)
    rows = []
    keys = ("room", "slab", "upper", "lower", "buffer")
    for mname, model in models:
        p_max = float(model.params.max_electrical_power)
        for wname in ("winter_cold", "shoulder", "summer_warm"):
            ot, wi, ra, so = profiles.weather(wname, datetime(2026, 1, 15))
            n = min(96, len(ot))
            ws = tm.WeatherSeries(outdoor_temps=ot[:n], wind_speeds=wi[:n], precipitation=ra[:n], solar_radiation=so[:n])
            st = tm.ThermalState(room_temperature=20.5, slab_temperature=23.0, outdoor_temperature=float(ot[0]),
                                 upper_floor_temperature=20.5, lower_floor_temperature=21.5, buffer_tank_temperature=38.0,
                                 wood_tank_temperature=62.0 if model.params.wood_tank_configured else None)
            mat = np.vstack([np.zeros(n), np.full(n, p_max), rng.uniform(0.0, p_max, size=n),
                             np.where(rng.uniform(size=n) < 0.5, 0.0, p_max * rng.uniform(size=n))])
            try:
                batch = model.simulate_trajectory_batch(st, mat, ws, dt_hours=0.25)
                worst, ok, where = 0.0, True, ""
                for i in range(mat.shape[0]):
                    scal = model.simulate_trajectory(st, mat[i], ws, dt_hours=0.25)
                    pairs = [(key, batch[key][i], scal[j]) for j, key in enumerate(keys)]
                    pairs.append(("refused", batch["refused"][i], scal[5]))
                    if scal[6] is not None and batch.get("wood") is not None:
                        pairs.append(("wood", batch["wood"][i], scal[6]))
                    for key, a, b in pairs:
                        a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
                        if not _bits(a, b):
                            ok = False
                            d = float(np.max(np.abs(a - b))) if a.shape == b.shape else float("inf")
                            if d >= worst:
                                worst, where = d, "%s, schedule %d" % (key, i)
                rows.append(((mname, wname), ok, "max |diff| %.3g %s" % (worst, where)))
            except Exception as err:
                rows.append(((mname, wname), False, "%s: %s" % (type(err).__name__, str(err)[:140])))
    return rows


class _Captured(Exception):
    pass


def fam_twin_objective(perturb):
    """optimizer.py: the solve's scalar `objective` and its `objective_batch` twin, captured from a
    real optimize() at HeatPumpOptimizer._solve_space: every row of the batch is the scalar
    objective of that plan, to the bit."""
    import numpy as np
    from datetime import datetime
    profiles, tm, opt_mod, tariff = _suite_modules()
    saved_exact = tariff._exact_topk_sum
    if perturb:
        tariff._exact_topk_sum = _fixed_exact_topk
    try:
        return _twin_objective_rows(profiles, tm, opt_mod)
    finally:
        tariff._exact_topk_sum = saved_exact


def _twin_objective_rows(profiles, tm, opt_mod):
    import numpy as np
    from datetime import datetime
    rows = []
    cases = [("single_zone_winter", False, "winter_typical", "winter_cold", {}),
             ("two_zone_winter", True, "winter_typical", "winter_cold", {}),
             ("single_zone_extreme", False, "winter_extreme", "winter_cold", {}),
             ("two_zone_shoulder", True, "shoulder", "shoulder", {}),
             ("single_zone_negative", False, "summer_negative", "summer_warm", {}),
             # the capacity tariff: its default (distinct days) and the per-window rule
             ("tariff_distinct_days", False, "winter_typical", "winter_cold",
              {"peak_price_per_kw": 20.0, "peak_threshold_kw": 1.0}),
             ("tariff_per_window", False, "winter_typical", "winter_cold",
              {"peak_price_per_kw": 20.0, "peak_threshold_kw": 1.0, "peak_distinct_days": False}),
             ("tariff_per_window_two_zone", True, "winter_typical", "winter_cold",
              {"peak_price_per_kw": 20.0, "peak_threshold_kw": 1.0, "peak_distinct_days": False})]
    for name, two_zone, price_p, weather_p, tariff_cfg in cases:
        start = datetime(2026, 1, 15)
        cfg = profiles.house(two_zone=two_zone)
        params = tm.ThermalParameters.from_config(cfg)
        model = tm.ThermalModel(params)
        opt_cfg = opt_mod.OptimizationConfig(
            horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0)
        for key, value in tariff_cfg.items():
            setattr(opt_cfg, key, value)
        opt = opt_mod.HeatPumpOptimizer(model, opt_cfg)
        pr = profiles.prices(price_p, start)
        ot, wi, ra, so = profiles.weather(weather_p, start)
        st = tm.ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(ot[0]),
                             upper_floor_temperature=21.0, lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
        got = {}
        orig = opt_mod.HeatPumpOptimizer._solve_space

        def capture(self, dhw_plan, warm_start, h, p_max, n_steps, dt, prices, init_base, objective, objective_batch):
            headroom, scope = opt_mod._space_scope(self, h, init_base, dhw_plan=dhw_plan, p_max=p_max,
                                                   objective=objective, objective_batch=objective_batch)
            got.update(obj=scope[1], objb=scope[2], dhw=dhw_plan, headroom=headroom, n=n_steps)
            raise _Captured()

        opt_mod.HeatPumpOptimizer._solve_space = capture
        try:
            try:
                opt.optimize(inputs=profiles.solve_inputs(initial_state=st, prices=pr, outdoor_temps=ot, wind_speeds=wi,
                                                          precipitation=ra, solar_radiation=so, start_time=start))
            except _Captured:
                pass
            except Exception as err:
                if not got:
                    rows.append((name, False, "the solve did not reach _solve_space: %s: %s" % (type(err).__name__, str(err)[:80])))
                    continue
        finally:
            opt_mod.HeatPumpOptimizer._solve_space = orig
        if not got:
            rows.append((name, False, "the solve did not reach _solve_space (no capture)"))
            continue
        rng = np.random.default_rng(2)
        n = got["n"]
        head = np.asarray(got["headroom"], dtype=float)
        mat = np.vstack([np.zeros(n), head, head * 0.5, head * rng.uniform(size=n),
                         np.where(rng.uniform(size=n) < 0.5, 0.0, head)])
        batch = np.asarray(got["objb"](mat, got["dhw"]), dtype=float)
        scal = np.array([float(got["obj"](mat[i], got["dhw"])) for i in range(mat.shape[0])])
        rel = float(np.max(np.abs(batch - scal) / np.maximum(1.0, np.abs(scal))))
        rows.append((name, _bits(batch, scal), "5 plans: max relative diff %.3g (scalar %s)" % (
            rel, np.array2string(scal, precision=4, max_line_width=200))))
    return rows


# ------------------------------------------------------------ inverse pairs (family F)

def fam_parse_format(perturb):
    """dhw_schedule.py: the parsers and the formatters of one spec grammar are inverses:
    _parse_day_selector/_format_day_selector, _parse_time/format_clock,
    parse_windows/format_windows, parse_weekly_windows/format_weekly_windows."""
    import itertools
    ds = mod("dhw_schedule")
    rows = []
    for r in range(1, 8):
        for days in itertools.combinations(range(7), r):
            token = ds._format_day_selector(list(days))
            back = ds._parse_day_selector(token)
            rows.append((("day_selector", days), back == list(days), "formatted %r parsed back %r" % (token, back)))
    for hour in (0.0, 0.25, 6.0, 6.5, 12.75, 17.0, 22.5, 23.75, 24.0):
        text = ds.format_clock(hour)
        try:
            back = ds._parse_time(text)
        except Exception as err:
            back = "%s: %s" % (type(err).__name__, err)
        rows.append((("clock", hour), back == hour, "formatted %r parsed back %r" % (text, back)))
    for spec in ("06:00-08:30, 17:00-22:00", "22:00-06:00", "00:00-24:00", "05:15-05:45", "6-8,17-22", ""):
        try:
            w1 = ds.parse_windows(spec)
            text = ds.format_windows(w1)
            w2 = ds.parse_windows(text)
            rows.append((("windows", spec), w1 == w2, "parsed %r formatted %r parsed back %r" % (w1, text, w2)))
        except Exception as err:
            rows.append((("windows", spec), False, "%s: %s" % (type(err).__name__, err)))
    for spec in ("weekdays 06:00-08:00; weekend 08:00-10:00", "Mo-We 06:00-07:00; Sa,Su 09:00-11:00",
                 "daily 17:00-22:00", "Fr-Mo 20:00-23:00"):
        try:
            w1 = ds.parse_weekly_windows(spec)
            if w1 is None:  # the plain every-day form: parse_windows' grammar, by design
                rows.append((("weekly", spec), ds.parse_windows(ds.format_windows(ds.parse_windows(
                    spec.split(None, 1)[-1]))) == ds.parse_windows(spec.split(None, 1)[-1]), "every-day form"))
                continue
            text = ds.format_weekly_windows(w1)
            w2 = ds.parse_weekly_windows(text)
            rows.append((("weekly", spec), w1 == w2, "formatted %r" % (text,)))
        except Exception as err:
            rows.append((("weekly", spec), False, "%s: %s" % (type(err).__name__, str(err)[:120])))
    return rows


def _dict_classes():
    """The seam rule as code: every package class that defines both as_dict and from_dict."""
    out = []
    for f in sorted(glob.glob(os.path.join(PKG_DIR, "*.py"))):
        for n in ast.parse(open(f, encoding="utf-8").read()).body:
            if isinstance(n, ast.ClassDef):
                names = {m.name for m in n.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))}
                if {"as_dict", "from_dict"} <= names:
                    out.append((os.path.basename(f)[:-3], n.name))
    return out


def _bump(obj, depth=0):
    """Give every plain numeric attribute a distinct non-default value, in place."""
    import dataclasses
    seed = [0.0]
    try:
        items = list(vars(obj).items())
    except TypeError:
        return
    for name, value in items:
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            seed[0] += 1.0
            try:
                setattr(obj, name, value + int(seed[0]))
            except Exception:
                pass
        elif isinstance(value, float) and math.isfinite(value):
            seed[0] += 1.0
            try:
                setattr(obj, name, value * 1.01 + 0.01 * seed[0])
            except Exception:
                pass


def fam_as_from_dict(perturb):
    """`a record's writer and its reader`: for every class with both as_dict and from_dict,
    from_dict(as_dict(x)).as_dict() == as_dict(x) on a default instance; on one whose numeric
    attributes were moved off their defaults the reader may refuse an out-of-domain value once,
    and what it admitted must then survive a second round unchanged."""
    import json
    rows = []
    for modname, cls_name in _dict_classes():
        try:
            cls = getattr(mod(modname), cls_name)
            base = cls()
        except Exception as err:
            rows.append(((modname, cls_name), True, "SKIP not default-constructible: %s" % type(err).__name__))
            continue
        for variant in ("default", "moved"):
            try:
                obj = cls()
                if variant == "moved":
                    _bump(obj)
                d1 = obj.as_dict()

                def read(doc):
                    doc = json.loads(json.dumps(doc, default=str))
                    try:
                        return cls.from_dict(doc)
                    except TypeError:
                        return cls.from_dict(doc, doc.get("configured_weight", 1.0))  # ComfortLearner's second argument

                back = read(d1)
                if back is not None and variant == "moved":
                    d1 = back.as_dict()   # what the reader admitted
                    back = read(d1)
                if back is None:
                    rows.append(((modname, cls_name, variant), False, "from_dict returned None for its own as_dict"))
                    continue
                d2 = back.as_dict()
                j1, j2 = json.dumps(d1, sort_keys=True, default=str), json.dumps(d2, sort_keys=True, default=str)
                if j1 == j2:
                    rows.append(((modname, cls_name, variant), True, "%d keys" % len(d1)))
                else:
                    diff = sorted(k for k in set(d1) | set(d2) if json.dumps(d1.get(k), default=str) != json.dumps(d2.get(k), default=str))
                    rows.append(((modname, cls_name, variant), False, "keys that do not survive: " + ", ".join(
                        "%s %r -> %r" % (k, d1.get(k), d2.get(k)) for k in diff[:4])[:260]))
            except Exception as err:
                rows.append(((modname, cls_name, variant), False, "%s: %s" % (type(err).__name__, str(err)[:140])))
    return rows


FAMILIES = [
    ("temperature_roundtrip", fam_temperature_roundtrip, "inputs:temperature_from_c",
     "grep -n 'TEMPERATURE_UNIT_TO_C' custom_components/heatpump_optimizer/*.py"),
    ("dhw_store_tap", fam_dhw_store_tap, "thermal_model:DhwStore.store_temp_for_tap",
     "grep -n 'def store_temp_for_tap\\|def tap_temp_for_store' custom_components/heatpump_optimizer/*.py"),
    ("step_covering_now", fam_step_covering_now, "early_cutoff:_planned_room",
     "grep -n 'bisect_right(' custom_components/heatpump_optimizer/*.py"),
    ("no_value_state", fam_no_value_state, "inputs:_INVALID_STATES",
     "python3 dev/audit/rounds/round11/D7/s3/m8_agree.py --seams"),
    ("naive_instant", fam_naive_instant, "drift:_as_utc",
     "grep -n 'tzinfo is None\\|as_utc(\\|astimezone(' custom_components/heatpump_optimizer/*.py"),
    ("stored_number", fam_stored_number, "duty_switch:_stored_number",
     "python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --show A035"),
    ("finite_number", fam_finite_number, "const:finite_float",
     "grep -n 'def finite_float\\|def payload_number\\|def _as_float\\|def numeric' custom_components/heatpump_optimizer/*.py"),
    ("soc", fam_soc, "battery:StorageComponent.soc",
     "grep -n 'def soc' custom_components/heatpump_optimizer/*.py"),
    ("water_heat", fam_water_heat, "sensor:_gap_probe_terms",
     "python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --show C003"),
    ("buffer_prior_in_bounds", fam_buffer_prior_in_bounds, "const:default_buffer_cooling_rate",
     "python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --show A025"),
    ("effective", fam_effective, "config_flow:_effective",
     "grep -n 'def _\\?effective' custom_components/heatpump_optimizer/*.py"),
    ("ua_from_rate", fam_ua_from_rate, "thermal_model:ThermalParameters.wood_tank_heat_loss_coefficient",
     "python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --show A054"),
    ("window_mean", fam_window_mean, "power_guard:project_window_mean",
     "grep -n 'def project_window_mean\\|project_window_mean(' custom_components/heatpump_optimizer/*.py"),
    ("twin_wood_share", fam_twin_wood_share, "thermal_model:_wood_share_vec", "python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --list | grep '^E'"),
    ("twin_topk", fam_twin_topk, "tariff:_plateau_aware_topk_sum_batch", "python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --list | grep '^E'"),
    ("twin_day_peaks", fam_twin_day_peaks, "tariff:_day_peaks_batch", "python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --list | grep '^E'"),
    ("twin_peak_cost", fam_twin_peak_cost, "tariff:peak_cost_batch", "python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --list | grep '^E'"),
    ("twin_switch_weight", fam_twin_switch_weight, "duty_legs:switch_weights_batch", "python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --list | grep '^E'"),
    ("twin_trajectory", fam_twin_trajectory, "thermal_model:ThermalModel.simulate_trajectory_batch", "python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --list | grep '^E'"),
    ("twin_objective", fam_twin_objective, "optimizer:HeatPumpOptimizer._solve_space", "python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --list | grep '^E'"),
    ("parse_format", fam_parse_format, "dhw_schedule:_format_day_selector", "python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --list | grep '^F'"),
    ("as_from_dict", fam_as_from_dict, "accuracy:AccuracyTracker.from_dict", "python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --list | grep '^F'"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--seams", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    if a.seams:
        for site, vals in _novalue_literals():
            print(site, sorted(vals, key=repr))
        for name, _fn, sym, seam in FAMILIES:
            print("%s\t%s\t%s" % (name, sym, seam))
        return 0
    total = 0
    for name, fn, sym, seam in FAMILIES:
        if a.only and name != a.only:
            continue
        try:
            rows = fn(a.perturb)
        except Exception as err:  # a family that cannot be driven is reported, not hidden
            print("ERROR %s %s: %s" % (name, type(err).__name__, err))
            print("RESULT %s_disagreements=-1 probes" % name)
            continue
        bad = [r for r in rows if not r[1]]
        total += len(bad)
        if not a.quiet:
            for probe, ok, detail in rows:
                print("%s %s %r %s" % ("AGREE   " if ok else "DISAGREE", name, probe, detail))
        print("RESULT %s_probes=%d probes" % (name, len(rows)))
        print("RESULT %s_disagreements=%d probes" % (name, len(bad)))
    print("RESULT families=%d families" % len(FAMILIES))
    print("RESULT disagreements_total=%d probes" % total)
    print("RESULT thread_factor=%.3f ratio" % (time.process_time() / max(time.thread_time(), 1e-9)))
    print("RESULT load1=%.2f load" % os.getloadavg()[0])
    try:
        import resource
        print("RESULT swapins=%d count" % resource.getrusage(resource.RUSAGE_SELF).ru_nswap)
    except Exception:
        print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    sys.exit(main())

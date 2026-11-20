#!/usr/bin/env python3
"""N-staleness enumerator (round 11, SW2): every limit applied to a source that
reports only on change, flagged where it is shorter than that source's
legitimate quiet interval.

Since #2683 (R10 barrier) the reader picks INPUT_ON_CHANGE_MAX_AGE_MINUTES for a
source it has never seen re-report (inputs.age_limit_for / source_polls), so the
on-change table -- not INPUT_MAX_AGE_MINUTES, which round 10's enumerator read --
is the limit a quiet push source meets.  Seams: every key of
const.INPUT_ON_CHANGE_MAX_AGE_MINUTES, plus every module-level *_MAX_AGE_MINUTES
constant in the package (AST) that is not the quiet-store anchor.  FLAG when
limit < QUIET[name] (minutes a source pushed on change legitimately holds; inf =
indefinitely: a flag 'off' all day, 0 W idle).  QUIET is round 10's table
(dev/audit/rounds/round10/D14/sweep-N-staleness/enumerate.py) extended with the
keys the package has gained since; a key without a QUIET entry is flagged
'unknown' so a new source cannot pass unread.

Run:  PYTHONPATH=tests/hastub python3 enumerate.py [--controls]
"""
import ast
import math
import os
import pathlib
import sys

INF = math.inf
QUIET = {
    "CONF_POWER_ENTITY": INF, "CONF_HEAT_PUMP_MODE_ENTITY": INF,
    "CONF_ENERGY_ENTITY": INF, "CONF_HEAT_ENERGY_ENTITY": INF,
    "CONF_HOUSE_POWER_ENTITY": INF, "CONF_THERMAL_POWER_ENTITY": INF,
    "CONF_PV_PRODUCTION_ENTITY": INF, "CONF_SOLAR_RADIATION_ENTITY": INF,
    "CONF_INDOOR_TEMP_ENTITY": 360.0, "CONF_DHW_TEMP_ENTITY": 360.0,
    "CONF_FLOOR_RETURN_TEMP_ENTITY": 360.0, "CONF_LOWER_FLOOR_TEMP_ENTITY": 360.0,
    "CONF_BUFFER_TANK_TEMP_ENTITY": 360.0, "CONF_OUTDOOR_TEMP_ENTITY": 60.0,
    "CONF_INDOOR_HUMIDITY_ENTITY": 240.0,
    "CONF_VALVE_OUTLET_TEMP_ENTITY": INF, "CONF_WOOD_TANK_TOP_ENTITY": INF,
    "CONF_WOOD_TANK_BOTTOM_ENTITY": INF, "CONF_EXTERNAL_HEAT_ENTITY": INF,
    "CONF_HEAT_PUMP_FAULT_ENTITY": INF, "CONF_HEAT_PUMP_DEFROST_ENTITY": INF,
    "CONF_HEAT_PUMP_ONLINE_ENTITY": INF, "CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY": INF,
    "CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY": INF,
    "CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY": INF,
    "CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY": 120.0,
    "CONF_HEAT_PUMP_RETURN_TEMP_ENTITY": 120.0, "CONF_FLOW_METER_ENTITY": INF,
    "DHW_INLET_MAX_AGE_MINUTES": 720.0,
    "MODE_LAST_GOOD_MAX_AGE_MINUTES": INF,
    "OPEN_METEO_OBSERVED_MAX_AGE_MINUTES": None,  # an HTTP payload, not an entity
}


def table_seams(on_change, names):
    """on_change: {key value: limit}; names: {key value: CONF_* name}."""
    return [("const.py", names.get(k, str(k)), float(v)) for k, v in on_change.items()]


def constant_seams(pkg):
    out = []
    for f in sorted(pathlib.Path(pkg).glob("*.py")):
        for st in ast.parse(f.read_text()).body:
            tgt = st.targets[0] if isinstance(st, ast.Assign) and len(st.targets) == 1 else \
                st.target if isinstance(st, ast.AnnAssign) else None
            if not isinstance(tgt, ast.Name) or not tgt.id.endswith("_MAX_AGE_MINUTES"):
                continue
            if tgt.id in ("QUIET_STORE_MAX_AGE_MINUTES", "INPUT_MAX_AGE_MINUTES",
                          "INPUT_ON_CHANGE_MAX_AGE_MINUTES"):  # the tables, read by key above
                continue
            try:
                v = float(eval(compile(ast.Expression(st.value), "<c>", "eval"), {}))
            except Exception:  # noqa: BLE001 -- a non-literal limit is reported unknown
                v = None
            out.append((f.name, tgt.id, v))
    return out


def judge(seams):
    rows = []
    for fname, sym, lim in seams:
        q = QUIET.get(sym, "unknown")
        if q is None:
            flag = False
        elif q == "unknown" or lim is None:
            flag = True
        else:
            flag = lim < q
        rows.append((fname, sym, lim, q, flag))
    return rows


def real():
    from heatpump_optimizer import const
    names = {getattr(const, n): n for n in dir(const) if n.startswith("CONF_") and n.endswith("_ENTITY")}
    pkg = pathlib.Path(const.__file__).parent
    return table_seams(const.INPUT_ON_CHANGE_MAX_AGE_MINUTES, names) + constant_seams(pkg), names, const


def controls():
    seams, names, const = real()
    flagged = {s for (_f, s, _l, _q, fl) in judge(seams) if fl}
    six = {"CONF_HEAT_PUMP_FAULT_ENTITY", "CONF_HEAT_PUMP_DEFROST_ENTITY", "CONF_HEAT_PUMP_ONLINE_ENTITY",
           "CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY", "CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY",
           "CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY"}
    pos = six <= flagged
    print(f"positive: D14-s2-01's six pump flags flagged={len(six & flagged)}/6")
    clean = {"indoor": 360.0, "outdoor": 180.0, "power": INF}
    cn = {"indoor": "CONF_INDOOR_TEMP_ENTITY", "outdoor": "CONF_OUTDOOR_TEMP_ENTITY", "power": "CONF_POWER_ENTITY"}
    null = sum(r[4] for r in judge(table_seams(clean, cn)))
    print(f"null: clean fixture table flagged={null}")
    clean["power"] = 30.0  # the one-line re-introduction (#2683's pre-barrier power row)
    pert = sum(r[4] for r in judge(table_seams(clean, cn)))
    print(f"perturbation: one-line re-introduction flagged={pert}")
    ok = pos and null == 0 and pert == 1
    print("controls", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--controls" in sys.argv:
        sys.exit(controls())
    seams, _n, _c = real()
    rows = judge(seams)
    for fname, sym, lim, q, fl in rows:
        print(f"{'FLAG' if fl else 'ok  '} {fname} {sym} limit={lim} quiet={q}")
    print(f"RESULT seams={len(rows)} flagged={sum(r[4] for r in rows)}")

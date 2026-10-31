#!/usr/bin/env python3
"""N-staleness enumerator: every staleness limit in the package, flagged where it
is shorter than the legitimate quiet interval of a report-on-change source.

SEAM RULE (from D14-s3-02's seam_rules): a seam is a finite age limit applied to
a Home Assistant entity read -- every key of const.INPUT_MAX_AGE_MINUTES (dict
literal plus later subscript assigns) and every module-level *_MAX_AGE_MINUTES
constant in any package module. A seam is FLAGGED when limit < QUIET[name], the
legitimate quiet interval of that source pushed on change (minutes; inf = the
value can hold indefinitely, e.g. 0 W while idle). Static (AST), no imports, so
it runs on any tree, fixture or pre-fix commit.
COMMAND: python3 dev/audit/rounds/round10/D14/sweep-N-staleness/enumerate.py [--root PKGDIR] [--json]
CONTROLS: --controls runs positive (re-finds CONF_POWER_ENTITY and
CONF_HEAT_PUMP_MODE_ENTITY at HEAD; CONF_INDOOR_TEMP_ENTITY at the R9 pre-fix
limit 60), null (a clean fixture package -> 0 flagged), perturbation (one
appended line `INPUT_MAX_AGE_MINUTES[CONF_HOUSE_POWER_ENTITY] = 3.0` -> +1).
"""
import ast, json, math, shutil, sys, tempfile
from pathlib import Path

INF = math.inf
# Legitimate quiet interval of the source when it reports only on change.
# Sources: pump_signals.py module doc (MQTT push leaves pump entities untouched
# for hours), const.py QUIET_STORE rationale (360 min for slow stores).
QUIET = {
    "CONF_POWER_ENTITY": INF, "CONF_HEAT_PUMP_MODE_ENTITY": INF,
    "CONF_ENERGY_ENTITY": INF, "CONF_HOUSE_POWER_ENTITY": 5.0,
    "CONF_PV_PRODUCTION_ENTITY": INF, "CONF_SOLAR_RADIATION_ENTITY": INF,
    "CONF_INDOOR_TEMP_ENTITY": 360.0, "CONF_DHW_TEMP_ENTITY": 360.0,
    "CONF_FLOOR_RETURN_TEMP_ENTITY": 360.0, "CONF_LOWER_FLOOR_TEMP_ENTITY": 360.0,
    "CONF_BUFFER_TANK_TEMP_ENTITY": 360.0, "CONF_OUTDOOR_TEMP_ENTITY": 60.0,
    "CONF_VALVE_OUTLET_TEMP_ENTITY": INF, "CONF_WOOD_TANK_TOP_ENTITY": INF,
    "CONF_WOOD_TANK_BOTTOM_ENTITY": INF, "CONF_EXTERNAL_HEAT_ENTITY": INF,
    "CONF_HEAT_PUMP_FAULT_ENTITY": INF, "CONF_HEAT_PUMP_DEFROST_ENTITY": INF,
    "CONF_HEAT_PUMP_ONLINE_ENTITY": INF, "CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY": INF,
    "CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY": INF,
    "CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY": INF,
    "CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY": 120.0,
    "CONF_HEAT_PUMP_RETURN_TEMP_ENTITY": 120.0, "CONF_FLOW_METER_ENTITY": INF,
    "HUMIDITY_MAX_AGE_MINUTES": 240.0, "DHW_INLET_MAX_AGE_MINUTES": 720.0,
    "MODE_LAST_GOOD_MAX_AGE_MINUTES": INF,
    "OPEN_METEO_OBSERVED_MAX_AGE_MINUTES": None,  # HTTP payload, not an entity
}


def _num(node, names):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.Name) and node.id in names:
        return names[node.id]
    if isinstance(node, ast.BinOp):
        a, b = _num(node.left, names), _num(node.right, names)
        if a is not None and b is not None:
            return {ast.Mult: a * b, ast.Add: a + b}.get(type(node.op))
    return None


def scan(pkg):
    seams = []
    for f in sorted(Path(pkg).glob("*.py")):
        tree = ast.parse(f.read_text())
        names = {}
        for st in tree.body:
            tgt = val = None
            if isinstance(st, ast.Assign) and len(st.targets) == 1:
                tgt, val = st.targets[0], st.value
            elif isinstance(st, ast.AnnAssign) and st.value is not None:
                tgt, val = st.target, st.value
            if tgt is None:
                continue
            if isinstance(tgt, ast.Name):
                v = _num(val, names)
                if v is not None:
                    names[tgt.id] = v
                    if tgt.id.endswith("_MAX_AGE_MINUTES") and tgt.id != "QUIET_STORE_MAX_AGE_MINUTES":
                        seams.append((f.name, tgt.id, v, st.lineno))
                if tgt.id == "INPUT_MAX_AGE_MINUTES" and isinstance(val, ast.Dict):
                    for k, v in zip(val.keys, val.values):
                        if isinstance(k, ast.Name):
                            seams.append((f.name, k.id, _num(v, names), k.lineno))
            elif (isinstance(tgt, ast.Subscript) and isinstance(tgt.value, ast.Name)
                  and tgt.value.id == "INPUT_MAX_AGE_MINUTES"
                  and isinstance(tgt.slice, ast.Name)):
                key = tgt.slice.id
                seams = [s for s in seams if not (s[0] == f.name and s[1] == key)]
                seams.append((f.name, key, _num(val, names), st.lineno))
    out = []
    for fname, sym, lim, line in seams:
        q = QUIET.get(sym, "unknown")
        flagged = (q not in (None, "unknown") and lim is not None and lim < q)
        out.append({"file": fname, "symbol": sym, "line": line, "limit_min": lim,
                    "quiet_min": None if q is None else (q if q != INF else "inf"),
                    "flagged": bool(flagged) or q == "unknown"})
    return out


def flagged(pkg):
    return {s["symbol"] for s in scan(pkg) if s["flagged"]}


def controls(pkg):
    ok = True
    head = flagged(pkg)
    pos = {"CONF_POWER_ENTITY", "CONF_HEAT_PUMP_MODE_ENTITY"} <= head
    print(f"positive HEAD re-finds D14-s3-02 power+mode: {pos}")
    with tempfile.TemporaryDirectory() as t:
        c = Path(t) / "const.py"
        c.write_text((Path(pkg) / "const.py").read_text()
                     + "\nINPUT_MAX_AGE_MINUTES[CONF_INDOOR_TEMP_ENTITY] = 60.0\n")
        r9 = "CONF_INDOOR_TEMP_ENTITY" in flagged(t)
        print(f"positive R9 D1-s5-51 (indoor limit 60, pre-fix value) re-found: {r9}")
        c.write_text("QUIET_STORE_MAX_AGE_MINUTES = 360.0\nINPUT_MAX_AGE_MINUTES = {\n"
                     "    CONF_INDOOR_TEMP_ENTITY: QUIET_STORE_MAX_AGE_MINUTES,\n"
                     "    CONF_OUTDOOR_TEMP_ENTITY: 180.0,\n"
                     "    CONF_HOUSE_POWER_ENTITY: 30.0,\n}\n")
        null = len(flagged(t))
        print(f"null clean fixture flagged={null} (expect 0)")
        c.write_text(c.read_text() + "INPUT_MAX_AGE_MINUTES[CONF_HOUSE_POWER_ENTITY] = 3.0\n")
        pert = len(flagged(t))
        print(f"perturbation one-line re-introduction flagged={pert} (expect 1)")
    ok = pos and r9 and null == 0 and pert == 1
    print(f"RESULT controls_ok={ok}")
    return ok


def main():
    a = sys.argv[1:]
    pkg = a[a.index("--root") + 1] if "--root" in a else "custom_components/heatpump_optimizer"
    if "--controls" in a:
        return 0 if controls(pkg) else 1
    s = scan(pkg)
    if "--json" in a:
        print(json.dumps(s, indent=1)); return 0
    for x in s:
        print(f"{'FLAG' if x['flagged'] else 'ok  '} {x['file']}:{x['line']} {x['symbol']} "
              f"limit={x['limit_min']} quiet={x['quiet_min']}")
    print(f"RESULT seams={len(s)} flagged={sum(x['flagged'] for x in s)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

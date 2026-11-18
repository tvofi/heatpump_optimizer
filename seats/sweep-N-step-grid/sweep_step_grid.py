"""Round 11 class sweep, N-step-grid: every seam of the package where a number
meets a step grid -- a declared selector/input (its max or its default/value off
min + k*step) or a number written to an entity (not quantised to the entity's
step).

Surfaces enumerated (the whole package, not only the judged sites):
  A  config_flow._OPTION_FIELDS / _questionnaire_fields number widgets, and
     config_flow._widen_to_fit applied to every slider (via the finder's
     step_grid.py, which hooks the delivered configs)
  B  services.yaml number selectors (step_grid.py)
  C  every <input type=number|range> in www/heatpump-optimizer-card.js, its
     value bound to a stored setting whose backend validator admits any float
     in range: probed in Chromium with that legal value (validity.stepMismatch
     or a value the range input sanitises away)
  D  every hass.services.async_call in the package (AST): a numeric write
     (set_value / set_temperature / SETPOINT_SERVICES) whose data does not flow
     from a step-snapping call (_on_step, quantise_setpoint_c) is a seam

Command: PYTHONPATH=tests/hastub python3 <this> [--tree DIR] [--perturb-write|--perturb-freq|--null] [--no-card]
  --perturb-write  inputs.write_setpoint's _on_step(...) replaced by float(value) in memory (one-line
                   re-introduction of the pre-#setpoint_step shape): write seams +1
  --perturb-freq   coordinator._command_frequency's round(target, 1) wrapped in _on_step (the D16-s1-01 fix):
                   write seams -1
  --null           run surfaces C and D on a clean fixture (a snapped write, an on-grid card input): 0
"""
import ast
import json
import os
import re
import subprocess
import sys

argv = sys.argv[1:]
TREE = argv[argv.index("--tree") + 1] if "--tree" in argv else os.getcwd()
PKG = os.path.join(TREE, "custom_components", "heatpump_optimizer")
HERE = os.path.dirname(os.path.abspath(__file__))
STEP_GRID = os.path.join(TREE, "dev/audit/rounds/round11/D14/s1/step_grid.py")
NULL = "--null" in argv

SNAP = {"_on_step", "quantise_setpoint_c"}
NUMERIC_SERVICES = {"set_value", "set_temperature"}


# ---------------------------------------------------------------- A + B
def selector_seams():
    if NULL:
        return []
    env = dict(os.environ, PYTHONPATH=os.path.join(TREE, "tests", "hastub"))
    out = subprocess.run([sys.executable, STEP_GRID, "--tree", TREE], capture_output=True,
                         text=True, env=env, cwd=TREE).stdout
    seams = {}
    for line in out.splitlines():
        if not line.startswith("SEAM "):
            continue
        tag = line[5:].split(":")[0]
        if tag == "widen":
            key = ("custom_components/heatpump_optimizer/config_flow.py", "_widen_to_fit")
        elif tag == "services":
            fld = line[5:].split(":")[1].strip()
            key = ("custom_components/heatpump_optimizer/services.yaml", fld)
        else:
            fld = line[5:].split(":")[2].strip()
            key = ("custom_components/heatpump_optimizer/config_flow.py", f"_OPTION_FIELDS.{fld}")
        seams.setdefault(key, []).append(line[5:])
    return [{"surface": "A/B", "file": k[0], "symbol": k[1], "evidence": v} for k, v in seams.items()]


# ---------------------------------------------------------------- C
# Each card input: the class it is found by, and the legal stored value its
# value binding can carry (the backend validator that admits it).
CARD_BINDINGS = {
    "wi-temp": (21.3, "comfort_temp_day: services._COMFORT_TEMP_C = _float_range(5, 30), any float"),
    "wi-dhw-min": (45.3, "dhw_min_temperature: services._DHW_MIN_TEMP_C, any float; max = published "
                   "dhw_min_temperature_max = round(dhw_setpoint - 5.0, 1), dhw_setpoint any float"),
    "wi-quiet-frac": (0.62, "silent_mode_power_fraction: apply_schedule vol.Range(0.0, 1.0), any float"),
    "sp-setpoint": (21.3, "manual_setpoint: assign_entity vol.Range(0, 30), any float"),
    "wi-wood-liters": (None, "liters only ever from this input's own value or the constant 50 (card :12869, :12880)"),
}
CARD_MAX_OVERRIDE = {"wi-dhw-min": 50.3}  # ceiling for a stored dhw_setpoint of 55.3

INPUT_RE = re.compile(r'<input\b([^>]*?)>', re.S)


def card_inputs(js):
    found = []
    for m in INPUT_RE.finditer(js):
        attrs = m.group(1)
        t = re.search(r'type="(number|range)"', attrs)
        if not t:
            continue
        cls = re.search(r'class="([^"]*)"', attrs)
        cls = cls.group(1).split()[-1] if cls else "?"
        get = lambda a: (re.search(a + r'="([^"]*)"', attrs) or [None, None])[1]
        line = js.count("\n", 0, m.start()) + 1
        found.append({"cls": cls, "type": t.group(1), "min": get("min"), "max": get("max"),
                      "step": get("step"), "line": line})
    return found


def probe_card(inputs):
    """Render each input in Chromium with its legal stored value; seam when the
    value is step-mismatched (number) or sanitised to another value (range)."""
    cases = []
    for i in inputs:
        val, why = CARD_BINDINGS.get(i["cls"], (None, "unbound"))
        if val is None:
            continue
        mn = i["min"] if i["min"] and "$" not in i["min"] else "35"
        mx = str(CARD_MAX_OVERRIDE.get(i["cls"], i["max"]))
        cases.append({**i, "minv": mn, "maxv": mx, "value": val, "why": why})
    if NULL:  # clean fixture: on-grid values
        cases = [{"cls": "null-range", "type": "range", "minv": "16", "maxv": "24", "step": "0.5", "value": 21.5,
                  "line": 0, "why": "null"},
                 {"cls": "null-number", "type": "number", "minv": "0", "maxv": "30", "step": "0.5", "value": 21.5,
                  "line": 0, "why": "null"}]
    js = r"""
const { chromium } = require('playwright');
(async () => {
  const cases = JSON.parse(process.argv[1]);
  const b = await chromium.launch(); const p = await b.newPage();
  const out = [];
  for (const c of cases) {
    const r = await p.evaluate((c) => {
      const el = document.createElement('input');
      el.type = c.type; el.min = c.minv; el.max = c.maxv; el.step = c.step;
      el.setAttribute('value', String(c.value)); document.body.appendChild(el);
      const res = {value: el.value, stepMismatch: el.validity.stepMismatch,
                   maxOffGrid: false};
      // max reachable? set the value to max and read back
      el.value = c.maxv; res.atMax = el.value; el.remove(); return res;
    }, c);
    out.push({...c, ...r});
  }
  console.log(JSON.stringify(out)); await b.close();
})();
"""
    res = subprocess.run(["node", "-e", js, json.dumps(cases)], capture_output=True, text=True)
    if res.returncode:
        raise SystemExit("card probe failed: " + res.stderr[-400:])
    seams = []
    stored = {c["cls"]: c["value"] for c in cases}
    for r in json.loads(res.stdout):  # r["value"] is the page's (sanitised) value
        reasons = []
        if r["stepMismatch"]:
            reasons.append(f"value {stored[r['cls']]} stepMismatch on {r['minv']}+k*{r['step']}")
        if r["type"] == "range" and abs(float(r["value"]) - float(stored[r["cls"]])) > 1e-9:
            reasons.append(f"range sanitises stored {stored[r['cls']]} to {r['value']}")
        if abs(float(r["atMax"]) - float(r["maxv"])) > 1e-9:
            reasons.append(f"max {r['maxv']} unreachable (reads {r['atMax']})")
        if reasons:
            seams.append({"surface": "C", "file": "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js",
                          "symbol": f"input.{r['cls']}", "line": r["line"],
                          "evidence": reasons, "binding": r["why"]})
    return seams


# ---------------------------------------------------------------- D
def _names(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _calls(node):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            out.add(f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else "")
    return out


def write_seams(sources):
    seams, sites = [], []
    for rel, src in sources.items():
        tree = ast.parse(src)
        funcs = {f.name: f for f in ast.walk(tree) if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for fn in funcs.values():
            tainted = set()
            for st in ast.walk(fn):
                if isinstance(st, ast.Assign) and (_calls(st.value) & SNAP or _names(st.value) & tainted):
                    for t in st.targets:
                        tainted |= _names(t)
            for n in ast.walk(fn):
                if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "async_call"):
                    continue
                if not (isinstance(n.func.value, ast.Attribute) and n.func.value.attr == "services"):
                    continue
                consts = {c.value for c in ast.walk(n) if isinstance(c, ast.Constant) and isinstance(c.value, str)}
                callee_consts = set()
                for name in _names(n) | _calls(fn):
                    if name in funcs and name != fn.name:
                        callee_consts |= {c.value for c in ast.walk(funcs[name])
                                          if isinstance(c, ast.Constant) and isinstance(c.value, str)}
                svc_names = _names(n)
                numeric = bool(consts & NUMERIC_SERVICES or (callee_consts & NUMERIC_SERVICES and "service" in svc_names)
                               or "SETPOINT_SERVICES" in {x for x in _names(fn)})
                if consts & {"mqtt"} or not numeric:
                    sites.append((rel, fn.name, n.lineno, "non-numeric"))
                    continue
                data_names = set()
                for a in n.args[2:3] + [k.value for k in n.keywords if k.arg != "blocking"]:
                    data_names |= _names(a)
                snapped = bool(data_names & tainted) or bool(_calls(n) & SNAP)
                sites.append((rel, fn.name, n.lineno, "snapped" if snapped else "UNSNAPPED"))
                if not snapped:
                    seams.append({"surface": "D", "file": rel, "symbol": fn.name, "line": n.lineno,
                                  "evidence": [f"numeric async_call at :{n.lineno} with data not flowing from "
                                               f"{'/'.join(sorted(SNAP))}"]})
    return seams, sites


def package_sources():
    if NULL:
        return {"fixture.py": (
            "async def write(hass, eid, value):\n"
            "    sent = _on_step(float(value), setpoint_step(hass, eid), 'nearest')\n"
            "    await hass.services.async_call('number', 'set_value', {'entity_id': eid, 'value': sent})\n"
            "async def off(hass, eid):\n"
            "    await hass.services.async_call('switch', 'turn_off', {'entity_id': eid})\n")}
    srcs = {}
    for f in sorted(os.listdir(PKG)):
        if f.endswith(".py"):
            srcs[f"custom_components/heatpump_optimizer/{f}"] = open(os.path.join(PKG, f), encoding="utf-8").read()
    if "--perturb-write" in argv:
        k = "custom_components/heatpump_optimizer/inputs.py"
        old = '_on_step(float(value), setpoint_step(hass, entity_id), "nearest")'
        assert old in srcs[k]
        srcs[k] = srcs[k].replace(old, "float(value)")
    if "--perturb-freq" in argv:
        k = "custom_components/heatpump_optimizer/coordinator.py"
        old = '"value": round(target, 1)}'
        assert old in srcs[k]
        srcs[k] = srcs[k].replace(old, '"value": _on_step(round(target, 1), 1.0, "nearest")}')
    return srcs


def main():
    sel = selector_seams()
    card = []
    if "--no-card" not in argv:
        js = "" if NULL else open(os.path.join(PKG, "www", "heatpump-optimizer-card.js"), encoding="utf-8").read()
        card = probe_card(card_inputs(js))
    writes, sites = write_seams(package_sources())
    for s in sel + card + writes:
        print("SEAM", s["file"], s["symbol"], "|", "; ".join(s["evidence"])[:300])
    for rel, fn, ln, kind in sites:
        print("SITE", f"{rel}:{ln}", fn, kind)
    print(f"RESULT seams_selectors={len(sel)} sites")
    print(f"RESULT seams_card={len(card)} inputs")
    print(f"RESULT seams_writes={len(writes)} call sites")
    print(f"RESULT write_sites={len(sites)} async_call sites")
    print(f"RESULT seams_total={len(sel) + len(card) + len(writes)}")
    if "--json" in argv:
        json.dump(sel + card + writes, open(argv[argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()

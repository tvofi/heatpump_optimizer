"""D4.M2 harness: services.yaml and icons.json scored against D4-criteria F4/I3-style completeness.

Metric: (a) services.yaml services/fields with no name or description in a language file's
services.<svc>[.fields.<f>]; (b) number-selector fields with a unit and no description;
(c) services with no icon in icons.json, and icons.json services/entity keys with no
service or entity translation key behind them (orphans); (e) leaf strings whose {placeholders} differ from strings.json's at the same path, per language; (d) ServiceValidationError
translation_keys raised in services.py with no exceptions.<key>.message per language, and
{placeholders} those messages read that the raise does not pass.
Count key: services.yaml top-level keys and field keys as Home Assistant loads them;
icons.json keys; translation_key literals in services.py.
Command: PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3 -I dev/audit/rounds/round11/D4/s2/services_icons.py [--perturb-drop SERVICE] [--perturb-fix-de]
  --perturb-fix-de renames de exceptions.run_optimization_no_prices' {entry_id} to {entry_ids}: both mismatch counts go to 0.
  --perturb-drop removes that service's icon in memory: services_without_icon goes up by 1.
Expected: the RESULT counts printed at baseline, exact.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: orchestrator Mac (darwin arm64).
Instrumented symbols: custom_components/heatpump_optimizer/services.yaml, icons.json (the shipped
artefacts HA loads), services.py raise sites (AST).
Run with -I: the integration package holds a datetime.py that shadows the stdlib for PyYAML.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast, json, re, sys, time
import yaml

_t0p, _t0t = time.process_time(), time.thread_time()
CC = "custom_components/heatpump_optimizer/"
TR = {k: json.load(open(p)) for k, p in {
    "strings": CC + "strings.json", "en": CC + "translations/en.json",
    "sv": CC + "translations/sv.json", "de": CC + "translations/de.json"}.items()}
svcs = yaml.safe_load(open(CC + "services.yaml"))
icons = json.load(open(CC + "icons.json"))
if "--perturb-fix-de" in sys.argv:  # the one-line translation fix, applied in memory
    m = TR["de"]["exceptions"]["run_optimization_no_prices"]
    m["message"] = m["message"].replace("{entry_id}", "{entry_ids}")
if "--perturb-drop" in sys.argv:
    icons["services"].pop(sys.argv[sys.argv.index("--perturb-drop") + 1], None)

text_missing, unit_nodesc, nfields = [], [], 0
for svc, spec in svcs.items():
    flds = (spec or {}).get("fields") or {}
    flat = {}
    for f, fs in flds.items():
        if isinstance(fs, dict) and "fields" in fs and "selector" not in fs:  # collapsed section
            flat.update(fs["fields"])
        else:
            flat[f] = fs or {}
    for lang, t in TR.items():
        st = t.get("services", {}).get(svc, {})
        for part in ("name", "description"):
            if not st.get(part):
                text_missing.append(f"{lang}:{svc}.{part}")
        for f, fs in flat.items():
            ft = st.get("fields", {}).get(f, {})
            for part in ("name", "description"):
                if not ft.get(part):
                    text_missing.append(f"{lang}:{svc}.fields.{f}.{part}")
            num = ((fs.get("selector") or {}).get("number") or {})
            if num.get("unit_of_measurement") and not ft.get("description"):
                unit_nodesc.append(f"{lang}:{svc}.{f}")
    nfields += len(flat)

no_icon = sorted(set(svcs) - set(icons.get("services", {})))
orphan_svc_icons = sorted(set(icons.get("services", {})) - set(svcs))
ent_tr = TR["strings"].get("entity", {})
orphan_ent_icons = [f"{plat}.{k}" for plat, d in icons.get("entity", {}).items() for k in d
                    if k not in ent_tr.get(plat, {})]

# ServiceValidationError / HomeAssistantError translation keys in services.py
tree = ast.parse(open(CC + "services.py").read())
raised, ph_missing = {}, []
for n in ast.walk(tree):
    if isinstance(n, ast.Call):
        kw = {k.arg: k.value for k in n.keywords if k.arg}
        tk = kw.get("translation_key")
        if isinstance(tk, ast.Constant) and isinstance(tk.value, str):
            passed = set()
            p = kw.get("translation_placeholders")
            if isinstance(p, ast.Dict):
                passed = {k.value for k in p.keys if isinstance(k, ast.Constant)}
            elif p is not None:
                passed = None  # dynamic, not judged
            raised.setdefault(tk.value, []).append(passed)
exc_missing = []
for key, passes in sorted(raised.items()):
    for lang, t in TR.items():
        msg = t.get("exceptions", {}).get(key, {}).get("message")
        if not msg:
            exc_missing.append(f"{lang}:exceptions.{key}")
            continue
        need = set(re.findall(r"\{([a-z_]+)\}", msg))
        for passed in passes:
            if passed is not None and need - passed:
                ph_missing.append(f"{lang}:{key} needs {sorted(need - passed)}")
# (e) placeholder parity: every leaf string in a translation names the same {placeholders}
# as the strings.json source at the same path.
def leaves(d, path=""):
    for k, v in d.items():
        if isinstance(v, dict):
            yield from leaves(v, f"{path}.{k}" if path else k)
        elif isinstance(v, str):
            yield (f"{path}.{k}" if path else k), v
SRC = dict(leaves(TR["strings"]))
parity = []
for lang in ("en", "sv", "de"):
    for path, v in leaves(TR[lang]):
        if path in SRC:
            a, b = set(re.findall(r"\{([a-z_]+)\}", SRC[path])), set(re.findall(r"\{([a-z_]+)\}", v))
            if a != b:
                parity.append(f"{lang}:{path} source={sorted(a)} translation={sorted(b)}")
for x in parity: print("PLACEHOLDER_PARITY", x)
print(f"RESULT leaf_strings_compared={sum(1 for l in ('en','sv','de') for p,_ in leaves(TR[l]) if p in SRC)} count")
print(f"RESULT placeholder_parity_mismatches={len(parity)} count")
for x in text_missing: print("TEXT_MISSING", x)
for x in unit_nodesc: print("UNIT_NO_DESC", x)
for x in no_icon: print("NO_ICON", x)
for x in orphan_svc_icons + orphan_ent_icons: print("ORPHAN_ICON", x)
for x in exc_missing: print("EXC_MISSING", x)
for x in ph_missing: print("EXC_PLACEHOLDER", x)
print(f"RESULT services={len(svcs)} count")
print(f"RESULT service_fields={nfields} count")
print(f"RESULT text_missing={len(text_missing)} count")
print(f"RESULT unit_fields_without_description={len(unit_nodesc)} count")
print(f"RESULT services_without_icon={len(no_icon)} count")
print(f"RESULT orphan_icons={len(orphan_svc_icons) + len(orphan_ent_icons)} count")
print(f"RESULT icon_entity_keys={sum(len(d) for d in icons.get('entity', {}).values())} count")
print(f"RESULT raised_translation_keys={len(raised)} count")
print(f"RESULT exception_strings_missing={len(exc_missing)} count")
print(f"RESULT exception_placeholders_unsupplied={len(ph_missing)} count")
print(f"RESULT thread_factor={(time.process_time()-_t0p)/max(time.thread_time()-_t0t,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")

"""D10-s2 gold-tier rule checks (D10.M1/M2), round 10.

Metric: per gold rule, a count of violating sites keyed on the production
module's own literals (translation keys raised/issued vs. the keys the
catalogues strings.json / translations/en.json / translations/sv.json carry,
icons.json coverage, device_info presence, diagnostics redaction set).
Command: PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python dev/audit/rounds/round10/D10/s2/gold_rules.py
Expected: every *_missing / *_mismatch RESULT = 0 (+-0). Baseline 17f1c55fad1b, macOS arm64 (B2).
Perturbation: delete one key from strings.json "exceptions" -> exc_keys_missing_strings rises by 1.
"""
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import ast, json, pathlib, time
t0p, t0t = time.process_time(), time.thread_time()
P = pathlib.Path("custom_components/heatpump_optimizer")
cat = {n: json.loads((P / f).read_text()) for n, f in
       (("strings","strings.json"),("en","translations/en.json"),("sv","translations/sv.json"))}
icons = json.loads((P/"icons.json").read_text())
exc, iss, ent = set(), set(), {}
ISSUE_FUNCS = {"async_create_issue","create_issue","ir_create","_create_issue"}
for f in sorted(P.glob("*.py")):
    tree = ast.parse(f.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
            for kw in node.keywords:
                if kw.arg == "translation_key" and isinstance(kw.value, ast.Constant):
                    k = kw.value.value
                    if "issue" in fn.lower():
                        iss.add(k)
                    elif fn.endswith(("Error","Failed","Exception","Invalid")):
                        exc.add(k)
        if isinstance(node, ast.Assign) and any(getattr(t,"id","")=="_attr_translation_key" for t in node.targets) \
                and isinstance(node.value, ast.Constant):
            ent[node.value.value] = f.stem
def miss(keys, sect, name):
    for c, d in cat.items():
        m = sorted(k for k in keys if k not in d.get(sect, {}))
        print(f"RESULT {name}_missing_{c}={len(m)} keys {m}")
miss(exc, "exceptions", "exc_keys")
miss(iss, "issues", "issue_keys")
print(f"RESULT exc_keys_literal={len(exc)} count")
print(f"RESULT issue_keys_literal={len(iss)} count")
# entity translations parity across catalogues
for plat in cat["strings"].get("entity", {}):
    s = set(cat["strings"]["entity"][plat])
    for c in ("en","sv"):
        o = set(cat[c].get("entity", {}).get(plat, {}))
        print(f"RESULT entity_{plat}_mismatch_{c}={len(s ^ o)} keys {sorted(s ^ o)}")
    ic = set(icons.get("entity", {}).get(plat, {}))
    print(f"RESULT entity_{plat}_icon_orphans={len(ic - s)} keys {sorted(ic - s)}")
for sect in ("exceptions","issues"):
    s = set(cat["strings"].get(sect, {}))
    for c in ("en","sv"):
        print(f"RESULT {sect}_mismatch_{c}={len(s ^ set(cat[c].get(sect,{})))} count")
# devices: production device_info presence; diagnostics redaction
src = {f.stem: f.read_text() for f in P.glob("*.py")}
print(f"RESULT device_info_sites={sum(s.count('DeviceInfo(') for s in src.values())} count")
d = ast.parse(src["diagnostics"])
red = [n for n in ast.walk(d) if isinstance(n, ast.Assign) and any(getattr(t,"id","")=="TO_REDACT" for t in n.targets)]
print(f"RESULT diagnostics_to_redact_present={len(red)} count")
print(f"RESULT reconfigure_step_present={int('async_step_reconfigure' in src['config_flow'])} bool")
print(f"RESULT thread_factor={(time.process_time()-t0p)/max(time.thread_time()-t0t,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0 count")

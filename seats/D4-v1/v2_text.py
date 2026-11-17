#!/usr/bin/env python3
"""V2 (D4-v1) independent static measures for D4-s2-01, D4-s2-02, D4-s2-51, D4-s3-06, D4-s3-07.
Run from the planted export root: python3 v2_text.py
s2-01: async_show_form/_device_prefill_form sites in config_flow.py: per step_id, whether the
  placeholder expression names _WINDOW_PLACEHOLDERS or min_window_minutes; per translation file,
  error keys whose text reads {min_window_minutes}.
s2-02: every leaf of translations/<lang>.json against strings.json: differing {placeholder} sets.
s2-51: files under the component referencing the literal {tibber_info}.
s3-06: en/sv config+options step titles with >=1 capitalised non-first word that is not all-caps
  and not in a proper-name list.
s3-07: straight "..." spans vs „...“ spans in de.json values; '<digit> C' (no °) in blueprints.
"""
import ast, json, re, glob
C = "custom_components/heatpump_optimizer/"
src = open(C + "config_flow.py").read(); tree = ast.parse(src)
print("== s2-01")
for n in ast.walk(tree):
    if isinstance(n, ast.Call) and getattr(n.func, "attr", "") in ("async_show_form", "_device_prefill_form"):
        kw = {k.arg: ast.get_source_segment(src, k.value) for k in n.keywords}
        sid = kw.get("step_id") or "(helper call)"
        ph = kw.get("description_placeholders") or kw.get("placeholders") or ""
        if "prefill" in sid or "dhw" in sid or "hot_water" in sid or "silent" in sid:
            print(f"L{n.lineno} {n.func.attr} step={sid} window_ph={'WINDOW' in ph or 'min_window' in ph} ph={ph[:80]}")
for f in [C + "strings.json"] + sorted(glob.glob(C + "translations/*.json")):
    d = json.load(open(f))
    for sect in ("config", "options"):
        for k, v in d.get(sect, {}).get("error", {}).items():
            if "{min_window_minutes}" in v: print(f"{f.split('/')[-1]} {sect}.error.{k}")
print("== s2-02")
def leaves(d, p=""):
    if isinstance(d, dict):
        for k, v in d.items(): yield from leaves(v, f"{p}.{k}" if p else k)
    elif isinstance(d, str): yield p, d
ref = dict(leaves(json.load(open(C + "strings.json"))))
ph = lambda s: set(re.findall(r"\{(\w+)\}", s))
n = mm = 0
for f in sorted(glob.glob(C + "translations/*.json")):
    for k, v in leaves(json.load(open(f))):
        if k in ref:
            n += 1
            if ph(v) != ph(ref[k]): mm += 1; print("MISMATCH", f.split('/')[-1], k, sorted(ph(v)), "vs", sorted(ph(ref[k])))
print(f"RESULT v2_leaves_compared={n} mismatches={mm}")
print("== s2-51")
refs = [f for f in glob.glob(C + "**/*.json", recursive=True) if "{tibber_info}" in open(f).read()]
print(f"RESULT tibber_info_text_refs={len(refs)} passed_in_code={src.count(chr(34)+'tibber_info'+chr(34))}")
print("== s3-06")
PROPER = {"Heat", "Pump", "Optimizer", "Tibber", "Nord", "Pool", "Home", "Assistant", "Modbus", "ECL", "SG", "Ready", "COP", "DHW", "PV", "Solcast", "Forecast.Solar", "Open-Meteo", "Danfoss", "Värmepumpsoptimering", "Optimizer-alternativ"}
for lang in ("en", "sv"):
    d = json.load(open(C + f"translations/{lang}.json")); tot = tc = 0
    for sect in ("config", "options"):
        for sid, st in d.get(sect, {}).get("step", {}).items():
            t = st.get("title")
            if not t: continue
            tot += 1
            ws = re.findall(r"[^\s&/()\-–]+", t)[1:]
            caps = [w for w in ws if w[:1].isupper() and not w.isupper() and w not in PROPER]
            if caps: tc += 1; print(f"{lang} {sect}.{sid}: {t!r} caps={caps}")
    print(f"RESULT {lang}_titles={tot} title_case={tc}")
print("== s3-07")
de = "\n".join(v for _, v in leaves(json.load(open(C + "translations/de.json"))))
st = re.findall(r'"[^"\n]{1,80}"', de); ty = re.findall(r"„[^“\n]{1,80}“", de)
print(f"RESULT de_json_straight={len(st)} de_json_typographic={len(ty)} sample={st[:3]}")
for f in glob.glob("blueprints/**/*.yaml", recursive=True):
    for m in re.finditer(r"\b\d+(\.\d+)?\s?C\b", open(f).read()): print("BARE_C", f, m.group(0))

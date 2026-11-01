import json, re, sys
pats = {"en": re.compile(r"worked before|\bbefore\.", re.I),
        "sv": re.compile(r"tidigare|fungerade tidigare|som förut", re.I)}
def leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from leaves(v, f"{p}.{k}" if p else k)
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from leaves(v, f"{p}[{i}]")
    elif isinstance(o, str): yield p, o
root = sys.argv[1]
for f, lang in (("strings.json","en"),("translations/en.json","en"),("translations/sv.json","sv")):
    d = json.load(open(f"{root}/custom_components/heatpump_optimizer/{f}"))
    n = 0
    for p, s in leaves(d):
        for m in pats[lang].finditer(s):
            n += 1; print(f"HIT {f} {p}: ...{s[max(0,m.start()-60):m.end()+30]}...")
    print(f"RESULT {f} hits={n}")

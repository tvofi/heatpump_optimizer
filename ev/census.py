import json, re, sys, collections
root = sys.argv[1]
pat = {"en": re.compile(r"as before|previously|formerly|no longer|used to|anymore|any more|until now|earlier", re.I),
       "sv": re.compile(r"tidigare|förut|numera|inte längre|dessförinnan|innan|brukade|hittills", re.I)}
def leaves(d, p=""):
    if isinstance(d, dict):
        for k, v in d.items(): yield from leaves(v, f"{p}.{k}" if p else k)
    elif isinstance(d, str): yield p, d
for f, code in (("strings.json","en"),("translations/en.json","en"),("translations/sv.json","sv")):
    data = json.load(open(f"{root}/custom_components/heatpump_optimizer/{f}"))
    c = collections.Counter(); rows = []
    for k, s in leaves(data):
        for m in pat[code].finditer(s):
            c[m.group(0).lower()] += 1
            i = m.start(); rows.append(f"  {k}: ...{s[max(0,i-50):i+60]}...")
    print(f"RESULT {sys.argv[2]} {f}: {sum(c.values())} hits {dict(c)}")
    if len(sys.argv) > 3: print("\n".join(rows))

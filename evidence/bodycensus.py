import json, re, sys, collections
root=sys.argv[1]
en=re.compile(r"used to|as before|no longer|previously|until now|formerly|anymore|any more", re.I)
sv=re.compile(r"som tidigare|tidigare var|brukade|inte längre|hittills|förut|var resten", re.I)
def leaves(d):
    if isinstance(d,dict):
        for v in d.values(): yield from leaves(v)
    elif isinstance(d,str): yield d
c=collections.Counter()
for f,p in (("strings.json",en),("translations/en.json",en),("translations/sv.json",sv)):
    for s in leaves(json.load(open(f"{root}/custom_components/heatpump_optimizer/{f}"))):
        for m in p.finditer(s): c[m.group(0)]+=1
print(f"RESULT {sys.argv[2]} body-pattern census (case-sensitive): {sum(c.values())} {dict(c)}")

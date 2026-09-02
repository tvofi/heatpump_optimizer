"""Summarise tools/audit/round2/D4/results.json (written by card_geometry.mjs).

    python tools/audit/round2/D4/summarise.py [state-or-arm substring ...]

Not a harness: a reader for the judge, no RESULT lines of its own.
"""
import json
import sys
from collections import Counter, defaultdict

r = json.load(open("tools/audit/round2/D4/results.json"))
filt = sys.argv[1:]
by_el = defaultdict(Counter)
worst = defaultdict(list)
for arm in r["arms"]:
    for name, st in arm["states"].items():
        tag = f"{arm['name']}/{name}"
        for c in st["contrast"]:
            by_el["contrast"][c["el"]] += 1
            worst["contrast"].append((c["ratio"], tag, c["el"], c["text"], c["fontPx"]))
        for o in st["overlaps"]:
            by_el["overlap"][f"{o['a'].split(' ')[0]}~{o['b'].split(' ')[0]}"] += 1
            worst["overlap"].append((-min(o["w"], o["h"]), tag, o["a"], o["b"]))
        for o in st["overflow"]:
            by_el["overflow"][f"{o['el']}@{o['where']}"] += 1
            worst["overflow"].append((-o["spill"], tag, o["el"], o["text"], o["where"]))
        for s in st["small"]:
            by_el["small" + ("44" if arm["coarse"] else "24")][s["el"]] += 1
            worst["small" + ("44" if arm["coarse"] else "24")].append((min(s["w"], s["h"]), tag, s["el"], s["aria"][:40]))
        for u in st["tabUnreached"]:
            by_el["unreached"][u.split("#")[0]] += 1
        if st["errors"]:
            by_el["errors"][tag] += len(st["errors"])
        if st["chart"]:
            worst["chartfont"].append((st["chart"]["fontPx"], tag, st["chart"]["w"], st["chart"]["laneH"]))
        if st["minFont"] is not None:
            worst["minfont"].append((st["minFont"], tag))
for k, c in by_el.items():
    print(f"== {k}: {sum(c.values())}")
    for el, n in c.most_common(14):
        print(f"   {n:4d}  {el}")
for k in ("contrast", "overlap", "overflow", "small24", "small44", "chartfont", "minfont"):
    rows = sorted(worst[k])[:10]
    print(f"== worst {k}")
    for row in rows:
        print("   ", row)
if filt:
    for arm in r["arms"]:
        for name, st in arm["states"].items():
            tag = f"{arm['name']}/{name}"
            if not any(f in tag for f in filt):
                continue
            print(f"===== {tag} host={st['hostW']} chart={st['chart']} minFont={st['minFont']}")
            for key in ("overlaps", "overflow", "contrast", "small", "tabUnreached", "errors", "tabSeq"):
                v = st[key]
                print(f"  {key} {len(v)}")
                for x in v[:12]:
                    print("    ", json.dumps(x, ensure_ascii=False)[:200])

# --- finer cuts -------------------------------------------------------------
pairs = Counter()
nosp = Counter()
cmin = defaultdict(lambda: [9.9, None])
s44 = defaultdict(lambda: [999, None])
geom = {}
for arm in r["arms"]:
    for name, st in arm["states"].items():
        tag = f"{arm['name']}/{name}"
        for o in st["overlaps"]:
            pairs[f"{o['a']} ~ {o['b']}"] += 1
        for s in st["small"]:
            if arm["coarse"]:
                side = min(s["w"], s["h"])
                if side < s44[s["el"]][0]:
                    s44[s["el"]] = [side, tag]
            elif s["crowded"]:
                nosp[s["el"]] += 1
        for c in st["contrast"]:
            k = f"{c['el']} ({arm['scheme']})"
            if c["ratio"] < cmin[k][0]:
                cmin[k] = [c["ratio"], f"{tag} '{c['text']}' {c['fontPx']}px {c['fg']} on {c['bg']}"]
        if st["chart"] and name in ("plan_inline", "expanded_plan", "coarse_pointer"):
            geom[tag] = (st["hostW"], st.get("dialogW"), st["chart"]["w"], st["chart"]["h"], st["chart"]["fontPx"], st["chart"]["laneH"])
print("== overlap pairs (text a ~ text b): occurrences")
for k, n in pairs.most_common(12):
    print(f"   {n:4d}  {k}")
print("== small24 with no spacing exception, by element")
for k, n in nosp.most_common(14):
    print(f"   {n:4d}  {k}")
print("== contrast: worst ratio per element and scheme")
for k, (ratio, where) in sorted(cmin.items(), key=lambda kv: kv[1][0]):
    print(f"   {ratio:5.2f}  {k:34s} {where}")
print("== coarse arm: smallest side per element")
for k, (side, where) in sorted(s44.items(), key=lambda kv: kv[1][0]):
    print(f"   {side:6.1f}  {k:28s} {where}")
print("== chart geometry (host, dialog, chart w x h, axis font px, lane px)")
for k, v in sorted(geom.items()):
    print(f"   {k:44s} {v}")

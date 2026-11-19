"""D4.M1 summary (round 11, seat D4-s1): groups m1_browser.mjs's renders.jsonl by
check and element, so each defect is counted once per element with the cells it shows in.

    python3 dev/audit/rounds/round11/D4/s1/m1_summarize.py <renders.jsonl> [--check KEY] [--detail N]

Prints one line per (check, element-key) with the number of renders and the
distinct states / languages / viewports / themes / motion / pointer arms it shows in.
"""
import json, re, sys, collections

path = sys.argv[1]
only = sys.argv[sys.argv.index("--check") + 1] if "--check" in sys.argv else None
detail = int(sys.argv[sys.argv.index("--detail") + 1]) if "--detail" in sys.argv else 0
recs = [json.loads(l) for l in open(path)]
items = {(r["state"], r["lang"]) for r in recs}
print(f"renders {len(recs)}  items {len(items)}  threw {sum(1 for r in recs if r.get('threw'))}  missed {sum(len(r['missed']) for r in recs)}")
def key(check, s):
    s = re.sub(r'"[^"]*"', '"…"', s)
    s = re.sub(r"\d+(\.\d+)?(px|:1)?", "#", s)
    return s
groups = collections.defaultdict(list)
for r in recs:
    for check in ["contrast", "overflow", "overlap", "small", "strictSmall", "popups", "options", "errors", "tabUnreached", "noIndicator", "invisibleFocus", "inkFail"]:
        for x in r.get(check) or []:
            groups[(check, key(check, x))].append((r, x))
    for h in r.get("hoverShift") or []:
        groups[("hoverShift", h["target"] + " src " + ",".join(h["src"]))].append((r, f'{h["v"]}'))
    if r.get("threw"):
        groups[("threw", r["threw"][:80])].append((r, r["threw"]))
    for m in r.get("missed") or []:
        groups[("missed", m)].append((r, m))
for (check, k), xs in sorted(groups.items(), key=lambda kv: (kv[0][0], -len(kv[1]))):
    if only and check != only:
        continue
    rs = [r for r, _ in xs]
    ax = lambda f: ",".join(sorted({str(r[f]) for r in rs}))
    print(f"{check:14s} n={len(xs):5d} renders={len({r['tag'] for r in rs}):5d} states={len({r['state'] for r in rs})} [{ax('state')[:160]}] lang=[{ax('lang')}] vp=[{ax('vp')}] theme=[{ax('theme')}] motion=[{ax('motion')}] ptr=[{ax('pointer')}] :: {k[:150]}")
    for r, x in xs[:detail]:
        print("      ", r["tag"], x[:200])

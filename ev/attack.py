import sys, copy, random, datetime as dt
sys.path.insert(0, 'tools/audit/seat')
import plan_phases as p
f = p.fixture()
def run(name, mut):
    d = copy.deepcopy(f); mut(d)
    v = p.violations(d)
    try:
        p.section(d, v, "f.json", (dt.datetime(2026,1,1), dt.datetime(2026,1,8))); r = "drawn"
    except Exception as e:
        r = f"CRASH {type(e).__name__}: {e}"
    print(f"RESULT case={name} violations={len(v)} section={r}" + (f" first={v[0]!r}" if v else ""))
run("null-control", lambda d: None)
run("prev-entry-int", lambda d: d["phases"][0].update(entry=5))
run("prev-item-name-int", lambda d: d["phases"][1]["items"][1].update(name=7) if len(d["phases"][1].get("items") or [])>1 else [ph for ph in d["phases"] if ph.get("items")][0]["items"][0].update(name=7))
run("prev-basis-int", lambda d: [ph for ph in d["phases"] if ph.get("forecast")][0]["forecast"].update(basis=3))
run("prev-note-int", lambda d: d.update(note=1))
run("started-after-finished", lambda d: [ph for ph in d["phases"] if ph.get("finished")][0].update(started="2026-12-31T00:00:00Z"))
run("start_from-after-start_to", lambda d: [ph for ph in d["phases"] if ph.get("forecast")][0]["forecast"].update(start_from="2026-12-31T00:00:00Z"))
run("round-true", lambda d: d.update(round=True))
# random 2-3 node fuzz
paths = list(p._nodes(f))[1:]
junk = list(p._JUNK) + [None, "x"*3, {"name": 1}, [[1]], -1, 10**30, float("nan"), "2026-13-45T00:00:00Z"]
rnd = random.Random(3622); crashes = 0; n = 0
for _ in range(20000):
    d = copy.deepcopy(f); ok = True
    for pth in rnd.sample(paths, rnd.choice([2,3])):
        at = d
        try:
            for k in pth[:-1]: at = at[k]
            at[pth[-1]] = rnd.choice(junk)
        except Exception: ok = False
    if not ok: continue
    n += 1
    try:
        v = p.violations(d)
        if not v:
            p.section(d, v, "f.json", (dt.datetime(2026,1,1), dt.datetime(2026,1,8))); p.section(d, v, "f.json")
        else:
            p.section(d, v, "f.json")
    except Exception as e:
        crashes += 1
        if crashes <= 5: print("CRASH", pth, type(e).__name__, e)
print(f"RESULT fuzz=multi-node runs={n} crashes={crashes}")

import sys; sys.argv=["x"]
exec(open("/root/h/sim.py").read().split("def g(w)")[0])
import statistics
def prices(win):
    needs, work, probed_ = {}, {}, {}
    for r in win:
        wk = cr._walk(r)
        if wk is None: continue
        for j in wk:
            needs.setdefault(j["name"], set())
            if j["pred"] is not None: needs[j["name"]].add(wk[j["pred"]]["name"])
            if j["priced"]:
                work.setdefault(j["name"], []).append(j["work"])
                if j["reference_work"] is not None: probed_.setdefault(j["name"], []).append(j["reference_work"])
    return {n: round(cr.job_price(s, probed_.get(n))) for n, s in work.items()}, needs
a, na = prices([probed(r, 40) for r in runs[:16]])
w = [probed(r, 40, extra={"tests / closures": 300}) if i < 8 else probed(r, 40) for i, r in enumerate(runs[:16])]
b, nb = prices(w)
for n in sorted(set(a) | set(b)):
    if a.get(n) != b.get(n): print("PRICE", n, a.get(n), "->", b.get(n))
for n in sorted(set(na) | set(nb)):
    if na.get(n) != nb.get(n): print("NEEDS", n, sorted(na.get(n, ())), "->", sorted(nb.get(n, ())))
print("closures needs", sorted(na["tests / closures"]))

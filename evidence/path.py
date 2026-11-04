import sys
exec(open("/root/h/sim.py").read().split("def g(w)")[0])
exec(open("/root/h/dbg.py").read().split("a, na =")[0].split("import statistics")[1])
def crit(win, label):
    pr, nd = prices(win)
    memo = {}
    def pe(n, seen=()):
        if n not in memo:
            best = max(((pe(m, (*seen, n)), m) for m in nd.get(n, ()) if m not in (*seen, n)), default=((0.0, []), None))
            memo[n] = (pr.get(n, 0) + best[0][0], best[0][1] + [n])
        return memo[n]
    tops = sorted((pe(n) for n in nd if n.startswith("tests /")), reverse=True)[:4]
    print(label)
    for v, p in tops: print(f"   {v/60:.3f}  " + " -> ".join(f"{n}[{pr.get(n,0)}]" for n in p))
crit(runs[:16], "UNPROBED newest window (merge push)")
crit([probed(r, 40) for r in runs[:16]], "PROBED (40 s) newest window")

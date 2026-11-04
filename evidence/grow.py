"""Reviewer's own growth/null harness: tests / fast (3.14) probed at
PROBE1 * its run's host factor (median over its >=20 s scripts of seconds /
that script's 60-run median, from fast_scripts.json), other lanes unprobed.
Growth: +300 s wall on fast (3.14) in the newest k runs, scaled by the run's
factor (work on a slow host takes longer), probe unchanged."""
import json, statistics as st, sys
exec(open("/root/h/sim.py").read().split("def g(w)")[0])
HEAVY.clear(); HEAVY["tests / fast (3.14)"] = "3.14"
fs = json.load(open("/root/rev/dev/audit/harnesses/r10_hotfix_ci_critpath_4/fast_scripts.json"))
vals = {}
for rid, sc in fs.items():
    for k, v in sc.items(): vals.setdefault(k, []).append(v)
med = {k: st.median(v) for k, v in vals.items() if st.median(v) >= 20}
fac = {int(rid): st.median([sc[k] / med[k] for k in med if sc.get(k)]) for rid, sc in fs.items()}
PROBE1 = 31.0  # factor-1 host's probe under the fixer's bridge (17.5 / 0.565)
def pw(r, extra=0, slow=1.0):
    f = fac[r["id"]] * slow
    return probed(r, PROBE1 * f / slow, wall_scale=slow, extra={"tests / fast (3.14)": extra * f} if extra else None)
win = runs[:16]
g0 = cr.window_work_minutes([pw(r) for r in win])
print("E fast(3.14) probed by its own host factor, newest window:", g0)
print("E slow fleet 1.9x:", cr.window_work_minutes([pw(r, slow=1.9) for r in win]))
for k in (1, 4, 8, 9, 12, 16):
    gk = cr.window_work_minutes([pw(r, 300 if i < k else 0) for i, r in enumerate(win)])
    print(f"E +300 s work on fast (3.14) in newest {k}: {round(gk - g0, 3)} (all of it {round(300*17.5/31/60, 3)})")
# the older window that contains the fast draw, and the one after it aged out
idx = [r["id"] for r in runs].index(41491607650)
for s0 in (idx - 15, idx - 16):
    print(f"E window starting {runs[s0]['id']}: unprobed {cr.window_work_minutes(runs[s0:s0+16])}, probed {cr.window_work_minutes([pw(r) for r in runs[s0:s0+16]])}")

"""Reviewer's own harness (not the fixer's): grade the window the first
post-merge push inherits -- the newest 15 real push runs of runs.json plus
one synthetic probed merge run cloned from the newest run, each heavy job
given a probe step of PROBE_S seconds -- under the head's tests/ci_ratchet.py.
Also: null control (slow fleet / added work) on that same window."""
import copy, json, sys, datetime as dt
sys.path.insert(0, "/root/rev/tests")
import ci_ratchet as cr
runs = json.load(open("/root/rev/dev/audit/harnesses/r10_hotfix_ci_critpath_4/runs.json"))
runs = runs["workflow_runs"]
runs.sort(key=lambda r: r["created_at"], reverse=True)
HEAVY = {"tests / fast (3.14)": "3.14", "tests / arch-instrument": "3.14",
         "tests / coverage": "3.13", "tests / closures": "3.13"}
P = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
F = lambda t: t.strftime("%Y-%m-%dT%H:%M:%SZ")
def _desc(r, name):
    wk = cr._walk(r); ran = sorted([j for j in r["jobs"] if j.get("completed_at")],
                                   key=lambda j: (P(j["created_at"]), P(j["completed_at"])))
    names = [w["name"] for w in wk]; out = set()
    for i, w in enumerate(wk):
        k = w["pred"]
        while k is not None:
            if names[k] == name: out.add(i); break
            k = wk[k]["pred"]
    return {id(ran[i]) for i in out}
def _shift(r, after, delta, only=None):
    def mv(o):
        for k in ("created_at", "started_at", "completed_at"):
            if o.get(k) and P(o[k]) >= after:
                o[k] = F(P(o[k]) + dt.timedelta(seconds=delta))
    for j in r["jobs"]:
        if id(j) in only:  # descendants by the run's own walk only
            for st in j.get("steps") or []: mv(st)
            mv(j)
def probed(r, probe_s, wall_scale=1.0, extra=None, rid=None):
    r = copy.deepcopy(r); r["id"] = rid or r["id"]
    for name in HEAVY:
        js = [j for j in r["jobs"] if j["name"] == name and j.get("completed_at")]
        if not js: continue
        j = js[0]; s0 = P(j["started_at"]); end = P(j["completed_at"])
        w = (end - s0).total_seconds()
        delta = round(w * (wall_scale - 1) + (extra or {}).get(name, 0))
        if delta:
            _shift(r, end, delta, _desc(r, name))
            j["completed_at"] = F(end + dt.timedelta(seconds=delta))
        j["steps"] = [{"name": f"{cr.PROBE_STEP} (python {HEAVY[name]})", "conclusion": "success",
                       "started_at": F(s0), "completed_at": F(s0 + dt.timedelta(seconds=round(probe_s * wall_scale)))}]
    return r
def g(w): return cr.window_work_minutes(w)
base = runs[:16]
print("A newest window at head, unprobed (merge push grades this):", g(base))
for ps in (31, 35, 38, 40, 44):
    m = probed(runs[0], ps, rid=1)
    print(f"B first post-merge push: 15 real + merge run probed at {ps} s:", g([m] + runs[:15]))
# null controls on a fully probed window (each real run given a probe that scales with its own fast lane? no: constant host, then slow fleet)
win = [probed(r, 40) for r in runs[:16]]
g0 = g(win)
print("C fully probed window, probe 40 s:", g0)
print("C slow fleet 1.9x (walls and probes):", g([probed(r, 40, 1.9) for r in runs[:16]]))
for k in (4, 8, 9, 12, 16):
    w = [probed(r, 40, extra={"tests / closures": 300}) if i < k else probed(r, 40) for i, r in enumerate(runs[:16])]
    print(f"C +300 s on closures in newest {k}:", round(g(w) - g0, 3))
for lane in ("tests / fast (3.14)",):
    for k in (4, 8, 9, 12, 16):
        w = [probed(r, 40, extra={lane: 300}) if i < k else probed(r, 40) for i, r in enumerate(runs[:16])]
        print(f"D +300 s on {lane} in newest {k}: {round(g(w) - g0, 3)} (all of it: {round(300*17.5/40/60,3)})")
# the fast lane probed by its own per-run host factor instead of a constant probe (no host spread in reference)

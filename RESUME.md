# #3045 fix round 4: the body-only repair of the round-3 block (verdict/3045 ebc4a779f)

Head unmoved at 9ef51b8215dd7216950f177386fb2f5a8f010a47. The measurement scripts the body cites are below. Run each from a checkout root as `python3 -I <script> runs60.json`, where runs60.json is the output of `ci_ratchet.py --gather-runs --window 60`.

## critjob.py (sha1 9fa09d25fab72040a9fadbd979c24b6df5bcfb45)
```python
import sys, json, copy, statistics, datetime as dt, collections
sys.path.insert(0, "tests"); import ci_ratchet as c
runs = json.load(open(sys.argv[1]))["workflow_runs"]
def shift(j, mins):
    e = c._at(j["completed_at"]) - dt.timedelta(minutes=mins)
    j["completed_at"] = e.isoformat().replace("+00:00", "Z")
base = []; crit = collections.Counter(); per = []
for r in runs:
    m = c.run_minutes(r)
    if m is None: continue
    base.append(m)
    names = []
    for i, j in enumerate(r["jobs"]):
        if not j.get("completed_at"): continue
        r2 = copy.deepcopy(r); shift(r2["jobs"][i], 0.5)
        if c.run_minutes(r2) < m - 0.2: names.append(j["name"])
    crit[" > ".join(names) or "?"] += 1
    per.append((r["head_sha"][:9], m, names))
print("n", len(base), "median", statistics.median(base))
for k, v in crit.most_common(): print(f"{v:3d}  {k}")
# median of sliding 8
ms=[statistics.median(base[i:i+8]) for i in range(len(base)-7)]
print("8-run median range", min(ms), max(ms), "newest8", ms[0])
```

## sim.py (sha1 aed8cb5177ff3c48f7c276426c037fc35f51dc1d)
```python
import sys, json, copy, statistics as st, datetime as dt
sys.path.insert(0, "tests"); import ci_ratchet as c
runs = json.load(open(sys.argv[1]))["workflow_runs"]
def sim(cut_s, job="tests / ci-ratchet"):
    out=[]
    for r in runs:
        r2=copy.deepcopy(r)
        for j in r2["jobs"]:
            if j["name"]==job and j.get("completed_at") and j.get("started_at"):
                w=(c._at(j["completed_at"])-c._at(j["started_at"])).total_seconds()
                cut=min(cut_s, max(0.0, w-5))
                j["completed_at"]=(c._at(j["completed_at"])-dt.timedelta(seconds=cut)).isoformat().replace("+00:00","Z")
        m=c.run_minutes(r2)
        if m is not None: out.append(m)
    ms=[st.median(out[i:i+8]) for i in range(len(out)-7)]
    return st.median(out), min(ms), max(ms), max(abs(x-st.median(out)) for x in ms)
for cut in (0, 10, 28, 36):
    med, lo, hi, dev = sim(cut)
    print(f"ci-ratchet -{cut:2d}s: median {med:.3f}  8-run medians {lo:.3f}..{hi:.3f}  max|dev| {dev:.3f}  headroom {34.267-med:+.3f}")
```

## Outputs, 2026-11-01
```
ci-ratchet - 0s: median 33.867  8-run medians 32.916..34.575  max|dev| 0.951  headroom +0.400
ci-ratchet -10s: median 33.700  8-run medians 32.833..34.409  max|dev| 0.867  headroom +0.567
ci-ratchet -28s: median 33.416  8-run medians 32.683..34.108  max|dev| 0.733  headroom +0.851
ci-ratchet -36s: median 33.341  8-run medians 32.617..33.975  max|dev| 0.725  headroom +0.926
```

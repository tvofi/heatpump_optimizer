"""Per-head CI measurements from the saved API responses.
Usage: python3 -I measure.py <ev dir>
Inputs: raw/runs_<sha>.json, raw/jobs_<run>.json, raw/checks_<sha>.json (fetch.sh, fetch2.sh),
merged_heads.txt, open_prs.json, main_last12.txt, raw/branchruns_<pr>.json."""
import sys, json, pathlib, statistics as st, collections, datetime as dt
EV = pathlib.Path(sys.argv[1]); RAW = EV/"raw"
def T(s): return dt.datetime.fromisoformat(s.replace("Z","+00:00")) if s else None
def load(p):
    try: return json.loads(p.read_text())
    except Exception: return None
def runs(sha): return (load(RAW/f"runs_{sha}.json") or {}).get("workflow_runs", [])
def jobs(rid): return (load(RAW/f"jobs_{rid}.json") or {}).get("jobs", [])
def checks(sha): return (load(RAW/f"checks_{sha}.json") or {}).get("check_runs", [])
def q(xs, p):
    xs = sorted(xs); return xs[min(len(xs)-1, int(round(p*(len(xs)-1))))] if xs else None
CODE = {"pull_request", "workflow_dispatch"}
API_JOBS = {"validate-hacs","arch-score","env-matrix","nightly-status","pr-contract",
            "budget-raise-gate","rerun-stale-contract","rerun-stale-verdict","closures","ci-ratchet"}
merged = [l.split() for l in (EV/"merged_heads.txt").read_text().splitlines()]
print("# A. Per merged-PR final head (pull_request-event runs at that head, all attempts)")
print("pr\tclass\twf_runs\tby_event\tjobs_listed\tjobs_exec\tjobs_skipped\tapi_jobs_exec\tcheck_runs\twave_wall_s\tlast_job\ttests_wall_s")
agg = collections.defaultdict(list); jobstats = collections.defaultdict(list); queue = collections.defaultdict(list)
for pr, sha, br in merged:
    cls = "record" if "record/" in br else "fix"
    rs = [r for r in runs(sha) if r["event"] != "workflow_run" and r["head_branch"] != "main"]
    ev = collections.Counter(r["event"] for r in rs)
    js = [(r, j) for r in rs for j in jobs(r["id"])]
    ex = [(r, j) for r, j in js if j["conclusion"] not in ("skipped", None)]
    sk = [(r, j) for r, j in js if j["conclusion"] == "skipped"]
    api = [j for r, j in ex if j["name"] in API_JOBS]
    code = [r for r in rs if r["event"] in CODE]
    wall = last = tw = None
    if code:
        t0 = min(T(r["created_at"]) for r in code)
        wave = [r for r in code if (T(r["created_at"]) - t0).total_seconds() < 300]
        wj = [(r, j) for r in wave for j in jobs(r["id"]) if j["run_attempt"] == 1 and j["completed_at"] and j["conclusion"] != "skipped"]
        if wj:
            r_, jl = max(wj, key=lambda x: T(x[1]["completed_at"]))
            wall = round((T(jl["completed_at"]) - t0).total_seconds()); last = f'{r_["name"]}/{jl["name"]}'
            for r, j in wj:
                if j["started_at"] and j["completed_at"]:
                    jobstats[f'{r["name"]}/{j["name"]}'].append((T(j["completed_at"]) - T(j["started_at"])).total_seconds())
                    queue[f'{r["name"]}/{j["name"]}'].append((T(j["started_at"]) - T(r["created_at"])).total_seconds())
            tr = [(r, j) for r, j in wj if r["name"] == "Tests"]
            if tr: tw = round((max(T(j["completed_at"]) for r, j in tr) - min(T(r["created_at"]) for r, j in tr)).total_seconds())
    row = dict(wf=len(rs), jl=len(js), je=len(ex), jsk=len(sk), api=len(api), cr=len(checks(sha)), wall=wall, tw=tw)
    for k, v in row.items():
        if v is not None: agg[(cls, k)].append(v)
    print(f"{pr}\t{cls}\t{len(rs)}\t{dict(ev)}\t{len(js)}\t{len(ex)}\t{len(sk)}\t{len(api)}\t{len(checks(sha))}\t{wall}\t{last}\t{tw}")
print("\n# A-summary: median (min-max) per class")
for (cls, k), v in sorted(agg.items()):
    print(f"{cls}\t{k}\tmedian={st.median(v)}\tmin={min(v)}\tmax={max(v)}\tn={len(v)}")
print("\n# B. Job duration / queue on the code wave, attempt 1 (fix+record heads), median and max seconds")
for k in sorted(jobstats, key=lambda k: -st.median(jobstats[k])):
    v = jobstats[k]; qv = queue[k]
    print(f"{k:55s} n={len(v):2d} dur_med={st.median(v):7.0f} dur_max={max(v):7.0f} queue_med={st.median(qv):5.0f} queue_max={max(qv):5.0f}")
print("\n# C. CI cycles per fix PR: distinct heads with a pull_request Tests run, Tests runs, attempts>1")
for pr, sha, br in merged:
    if "record/" in br: continue
    br_ = load(RAW/f"branchruns_{pr}.json") or []
    pr_runs = [r for r in br_ if r["event"] == "pull_request"]
    heads = {r["head_sha"] for r in pr_runs}
    print(f"{pr}\theads={len(heads)}\ttests_pr_runs={len(pr_runs)}\tdispatch_runs={sum(r['event']=='workflow_dispatch' for r in br_)}\treruns(attempt>1)={sum(r['run_attempt']>1 for r in br_)}")
print("\n# D. workflow_run-event runs (the two re-run workflows), all fetched heads, by UTC hour")
seen = {}
for p in RAW.glob("runs_*.json"):
    for r in (load(p) or {}).get("workflow_runs", []):
        if r["event"] == "workflow_run": seen[r["id"]] = r
byh = collections.Counter((r["created_at"][:13], r["name"]) for r in seen.values())
for (h, n), c in sorted(byh.items()): print(f"{h}Z\t{n}\t{c}")
ex = collections.Counter((r["name"], r["conclusion"]) for r in seen.values())
print("totals:", dict(ex))
print("\n# E. main push runs per main commit (push event at the merge sha)")
for l in (EV/"main_last12.txt").read_text().splitlines()[:10]:
    sha = l.split()[0]
    rs = [r for r in runs(sha) if r["event"] == "push"]
    t = [r for r in rs if r["name"] == "Tests"]
    tw = None
    if t:
        jj = [j for j in jobs(t[0]["id"]) if j["completed_at"] and j["run_attempt"] == 1]
        if jj: tw = round((max(T(j["completed_at"]) for j in jj) - T(t[0]["created_at"])).total_seconds())
    print(f"{sha[:10]}\tpush_runs={len(rs)}\t{sorted(r['name'] for r in rs)}\ttests_push_wall={tw}\tconclusion={t[0]['conclusion'] if t else None}")

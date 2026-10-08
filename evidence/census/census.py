import json, subprocess, time, re, os
fails=0
R="repos/tvofi/heatpump_optimizer"
def api(p):
    time.sleep(1.1)
    r=subprocess.run(["gh","api","--allow-escape-sequences",p],capture_output=True,text=True)
    if r.returncode:
        global fails; fails+=1; print(f"API FAIL {p}: {r.stderr.strip()[:120]}"); return None
    return r.stdout
runs=json.loads(api(f"{R}/actions/workflows/tests.yml/runs?per_page=100&created=>=2026-10-07"))["workflow_runs"]
sel=[r for r in runs if r["event"]=="pull_request" and "2026-10-08T06:40:00Z"<=r["created_at"]<="2026-10-08T12:01:59Z"]
print(f"runs in window: {len(sel)} (of {len(runs)} listed)")
rows=[]
for r in sel:
    jobs=json.loads(api(f"{R}/actions/runs/{r['id']}/jobs?per_page=100"))["jobs"]
    pins=[j for j in jobs if j["name"].startswith("mutation-pins")]
    af=[j for j in jobs if j["name"]=="mutation-autofix" and j["conclusion"] not in ("skipped",None)]
    if not af or not pins: continue
    log=api(f"{R}/actions/jobs/{af[0]['id']}/logs") or ""
    m=re.search(r"Z shards merged: (\S+)",log); a=re.search(r"Z AUTOFIX: (\S+)",log)
    rows.append((r["id"],r["head_sha"][:8],len(pins),af[0]["id"],m.group(1) if m else None,a.group(1) if a else None))
    print("ROW",*rows[-1])
print(f"RESULT census: {len(rows)} runs reached autofix after a pin job; single-shard={sum(1 for x in rows if x[2]==1)} single-shard-skip-no-measurement={sum(1 for x in rows if x[2]==1 and x[4]=='skip-no-measurement')} multi={sum(1 for x in rows if x[2]>1)} multi-skip-no-measurement={sum(1 for x in rows if x[2]>1 and x[4]=='skip-no-measurement')} api_failures={fails}")

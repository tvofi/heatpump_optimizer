#!/usr/bin/env python3
"""Reviewer's own re-read of the fast (3.14) offsets via the public REST API (curl),
independent of the fixer's gh-based harness. Prints the same fields, then a
permutation null: every 3-subset of the before set as an `after` set."""
import json, subprocess, sys, statistics, itertools
from datetime import datetime
def get(p):
    return json.loads(subprocess.run(["curl","-sS",f"https://api.github.com/repos/tvofi/heatpump_optimizer/{p}"],capture_output=True,text=True,check=True).stdout)
t=lambda s: datetime.fromisoformat(s.replace("Z","+00:00"))
def m(rid):
    r=get(f"actions/runs/{rid}"); js=get(f"actions/runs/{rid}/jobs?per_page=100")["jobs"]
    f=[j for j in js if j["name"]=="fast (3.14)"][0]; c=t(r["created_at"])
    q=(t(f["started_at"])-c).total_seconds()/60; d=(t(f["completed_at"])-t(f["started_at"])).total_seconds()/60
    wall=(t(r["updated_at"])-c).total_seconds()/60
    print(f"{rid} {r['event']} {r['head_sha'][:9]} attempt={r['run_attempt']} job_attempt={f['run_attempt']} queue={q:.2f} dur={d:.2f} offset={q+d:.2f} run_wall={wall:.2f}")
    return q+d,d
B="39310145738 39309509899 39309055147 39307877535 39302900612 39301525639 39299026662 39298637824 39293926561".split()
A="39333417268 39337586935 39337584363".split()
bo=[m(x) for x in B]; ao=[m(x) for x in A]
mb=statistics.median(o for o,_ in bo); ma=statistics.median(o for o,_ in ao)
print(f"RESULT before_median_offset={mb:.2f} after_median_offset={ma:.2f} saved_offset={mb-ma:.2f}")
print(f"RESULT before_median_dur={statistics.median(d for _,d in bo):.2f} after_median_dur={statistics.median(d for _,d in ao):.2f}")
subs=[mb-statistics.median(s) for s in itertools.combinations([o for o,_ in bo],3)]
print(f"RESULT permutation_null 3-subsets_of_before={len(subs)} passing_bar5={sum(s>=5 for s in subs)} max_saved={max(subs):.2f}")
allv=[o for o,_ in bo]+[o for o,_ in ao]; obs=ma
cnt=sum(1 for s in itertools.combinations(range(12),3) if statistics.median(allv[i] for i in s)<=obs)
print(f"RESULT exact_perm_p(median of 3 of 12 pooled <= {obs:.2f}) = {cnt}/220 = {cnt/220:.3f}")

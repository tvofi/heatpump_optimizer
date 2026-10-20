#!/usr/bin/env python3
"""Reviewer's own offset reader (round 3): fast (3.14) completed_at minus the run's created_at,
via `gh api`, independent of the fixer's harness."""
import json, subprocess, sys, statistics
from datetime import datetime
def get(p): return json.loads(subprocess.run(["gh","api",f"repos/tvofi/heatpump_optimizer/{p}"],capture_output=True,text=True,check=True).stdout)
t=lambda s: datetime.fromisoformat(s.replace("Z","+00:00"))
def m(rid):
    r=get(f"actions/runs/{rid}"); js=get(f"actions/runs/{rid}/jobs?per_page=100&filter=latest")["jobs"]
    f=[j for j in js if j["name"]=="fast (3.14)"][0]; c=t(r["created_at"])
    q=(t(f["started_at"])-c).total_seconds()/60; d=(t(f["completed_at"])-t(f["started_at"])).total_seconds()/60
    print(f"{rid} {r['event']} {r['head_sha'][:9]} fast={f['conclusion']} queue={q:.2f} dur={d:.2f} offset={q+d:.2f}", flush=True)
    return q+d, d
B="39310145738 39309509899 39309055147 39307877535 39302900612 39301525639 39299026662 39298637824 39293926561".split()
bo=[m(x) for x in B]; h=m(sys.argv[1])
mb=statistics.median(o for o,_ in bo); md=statistics.median(d for _,d in bo)
print(f"RESULT before_median_offset={mb:.2f} head_offset={h[0]:.2f} saved_offset={mb-h[0]:.2f} | before_median_dur={md:.2f} head_dur={h[1]:.2f} saved_dur={md-h[1]:.2f} | bar=5.0")

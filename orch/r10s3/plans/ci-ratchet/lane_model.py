"""Counterfactual fast-lane end if arch_score.py + arch_score_head.py move from lane_units to lane_golden.
Reads each fast job log's run.sh progress lines ([HH:MM:SS] start/ok <cmd> (Ns)) and the jobs API file."""
import json, re, sys, glob
from datetime import datetime as D
p = lambda s: D.fromisoformat(s.replace("Z", "+00:00"))
ev = sys.argv[1]
GOLDEN = ("tests/env_drift.py --all",)
E2E = ("tests/validate.py", "tests/edge.py", "tests/backtest.py", "tests/boost_drift_replay.py", "tests/optimality.py",
       "tests/plan_view.py", "tests/frontend.py", "tests/card.mjs", "tests/setup_qa_render.mjs", "tests/card_drift.mjs")
ARCH = ("tests/arch_score.py", "tests/arch_score_head.py")
rows = []
for f in sorted(glob.glob(f"{ev}/fastlog-*.log")):
    rid = f.split("fastlog-")[1][:-4]
    js = json.load(open(f"{ev}/jobs-{rid}.json"))["jobs"]
    t0 = min(p(j["created_at"]) for j in js)
    tend = max(p(j["completed_at"]) for j in js if j.get("completed_at"))
    fast = next(j for j in js if j["name"].startswith("fast (3.14)"))
    clos = next((j for j in js if j["name"] == "closures" and j.get("completed_at")), None)
    oks, first = {}, None
    for l in open(f):
        m = re.search(r"(\d{4}-\d\d-\d\dT[\d:.]+)Z\s+\[[\d:]+\] (start|ok|FAIL)\s+(\S+) (\S+)(.*?)(?: \((\d+)s\))?$", l)
        if not m: continue
        ts = p(m.group(1)[:26] + "+00:00") if False else D.fromisoformat(m.group(1)[:19] + "+00:00")
        if first is None: first = ts
        cmd = m.group(4) + m.group(5)
        if m.group(2) != "start" and m.group(6):
            oks[cmd.strip()] = ((ts - first).total_seconds(), int(m.group(6)))
    def lane_end(names):
        return max(v[0] for k, v in oks.items() if any(k.startswith(n) for n in names))
    stress = next(v for k, v in oks.items() if k.startswith("tests/stress.py"))
    arch = sum(v[1] for k, v in oks.items() if k.startswith(ARCH))
    golden, e2e = lane_end(GOLDEN), lane_end(E2E)
    lanes_end = stress[0] - stress[1]
    units = lanes_end  # the units lane is what ended last before stress (checked below)
    assert units >= max(golden, e2e) - 5, (rid, units, golden, e2e)
    units_new, golden_new = units - arch, golden + arch
    # core-time bound: single-core work of all three lanes plus arch's pool (4 workers, measured idle)
    work = (units - arch) + golden + e2e + 4 * arch
    lanes_new = max(units_new, golden_new, e2e, work / 4)
    saved = (lanes_end - lanes_new) / 60
    fast_end = (p(fast["completed_at"]) - t0).total_seconds() / 60
    clos_end = (p(clos["completed_at"]) - t0).total_seconds() / 60 if clos else 0
    wall = (tend - t0).total_seconds() / 60
    tail = wall - max(fast_end, clos_end)  # ci-ratchet and whatever follows the last of the two
    wall_new = max(fast_end - saved, clos_end) + tail
    rows.append((rid, js[0]["head_sha"][:8], wall, wall_new, fast_end, fast_end - saved, clos_end, arch))
print("run sha wall wall_new fast_end fast_end_new closures_end arch_s")
for r in rows:
    print(r[0], r[1], *(f"{x:.1f}" for x in r[2:7]), r[7])

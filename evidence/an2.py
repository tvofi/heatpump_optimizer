import json,sys,statistics
sys.path.insert(0,"tests"); import ci_ratchet as c
runs=sorted(json.load(open(sys.argv[1]))["workflow_runs"],key=lambda r:r["created_at"],reverse=True)
W=16
def med(sp):
    m=[x for x in map(c.run_minutes,sp) if x is not None]; return statistics.median(m) if m else None
for i in range(len(runs)-W+1):
    sp=runs[i:i+W]
    print(i, sp[0]["head_sha"][:9], c.window_work_minutes(sp), med(sp[:8]))
# job conclusions in cancelled runs
heavy=["tests / closures","tests / fast (3.14)","tests / arch-instrument","tests / coverage","tests / ci-ratchet","prelude"]
print("--- per job work (s) and conclusion, newest 28")
for r in runs[:28]:
    w={j["name"]:j for j in c._walk(r) or []}
    cj={j["name"]:j.get("conclusion") for j in r["jobs"]}
    print(r["head_sha"][:9], r["conclusion"][:4], " ".join(f'{h.split("/ ")[-1][:6]}={int(w[h]["work"]) if h in w else "-"}{"" if cj.get(h)=="success" else "!"+str(cj.get(h))[:4]}' for h in heavy))

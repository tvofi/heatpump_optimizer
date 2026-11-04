import json,sys,statistics,copy
sys.path.insert(0,"tests"); import ci_ratchet as c
runs=sorted(json.load(open(sys.argv[1]))["workflow_runs"],key=lambda r:r["created_at"],reverse=True)
for r in runs:
    rm=c.run_minutes(r) if r.get("status")=="completed" else None
    ch=c.run_chain(r) if rm else None
    print(r["id"],r["head_sha"][:9],r["created_at"],r["status"],r.get("conclusion"),rm, "->".join(x.replace("tests / ","") for x in (ch or [])[-3:]))

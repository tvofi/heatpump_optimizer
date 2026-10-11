import json, re, sys
from pathlib import Path
S = Path("/Users/timmalmstrom/hpo-seats/r9rev-2131")
dirs = {k: S / f"rec-{k}" for k in ("serial1", "serial2", "lanes")}
scratch = re.compile(r"/(?:var/folders|tmp|private/tmp)/\S+")
def norm(p):
    d = json.loads(p.read_text())
    d.pop("seconds", None)
    if isinstance(d.get("spawned"), list):
        d["spawned"] = [scratch.subn("<SCR>", json.dumps(x))[0] if not isinstance(x, str) else scratch.sub("<SCR>", x) for x in d["spawned"]]
    return d
scripts = ["wood_advisor.py", "doc_claims.py", "plan_view.py", "layout.py", "structure.py"]
for sc in scripts:
    base = norm(dirs["serial1"] / f"{sc}.json")
    for other in ("serial2", "lanes"):
        o = norm(dirs[other] / f"{sc}.json")
        if base == o:
            print(f"{sc}: serial1 == {other} (normalized)")
        else:
            keys = {k for k in set(base) | set(o) if base.get(k) != o.get(k)}
            print(f"{sc}: serial1 != {other} DIFF fields: {sorted(keys)}")
            for k in sorted(keys):
                print(f"   {k}: {json.dumps(base.get(k))[:200]}  VS  {json.dumps(o.get(k))[:200]}")

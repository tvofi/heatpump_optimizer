"""What the umbrella deletes, counted in origin/main's tree.

    python3 -I measure/simplify.py REPO_CHECKOUT > measure/simplify.txt

Counts: the held-run approval steps (by step name), the dispatch sites, the
cancel-superseded jobs, the top-level concurrency blocks, and the two rerun files.
"""
import sys, yaml
from pathlib import Path
wf = Path(sys.argv[1]) / ".github/workflows"
appr = disp = cs = cc = 0; lines = 0
for f in sorted(wf.glob("*.yml")):
    text = f.read_text(); d = yaml.safe_load(text)
    if d.get("concurrency"): cc += 1
    for jid, j in (d.get("jobs") or {}).items():
        if jid == "cancel-superseded": cs += 1; print(f"cancel-superseded job: {f.name}")
        for s in j.get("steps") or []:
            n = s.get("name", "")
            if n.startswith("Approve the runs"):
                appr += 1; L = len((s.get("run") or "").splitlines()); lines += L
                print(f"approval step: {f.name}:{jid} ({L} run lines)")
            if "gh workflow run" in (s.get("run") or ""): disp += 1; print(f"dispatch step: {f.name}:{jid}: {n}")
print(f"approval steps {appr} ({lines} run lines); dispatch steps {disp}; cancel-superseded jobs {cs}; workflows with top-level concurrency {cc}")
for r in ("pr-contract-rerun.yml", "budget-raise-gate-rerun.yml"):
    print(f"{r}: {len((wf / r).read_text().splitlines())} lines")
print(f"workflow files {len(list(wf.glob('*.yml')))}")

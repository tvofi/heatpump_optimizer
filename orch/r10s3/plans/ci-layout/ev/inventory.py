"""Static inventory of .github/workflows/*.yml at a tree.
Usage: python3 -I inventory.py <worktree>
Prints per workflow: name, triggers, job count; per job: whether its steps contain a
GitHub REST call site (gh api|gh pr|gh run|gh workflow|gh issue|gh release|curl api.github.com|
actions/github-script|hacs/action|codeql-action) and how many call sites."""
import sys, re, pathlib, yaml
root = pathlib.Path(sys.argv[1])
PAT = re.compile(r"\bgh (api|pr|run|workflow|issue|release|search)\b|api\.github\.com|actions/github-script|hacs/action|codeql-action/(analyze|init)")
tot_jobs = tot_api = 0
for f in sorted((root/".github/workflows").glob("*.yml")):
    y = yaml.safe_load(f.read_text())
    on = y.get(True, y.get("on"))
    trig = sorted(on.keys()) if isinstance(on, dict) else on
    jobs = y.get("jobs", {})
    print(f"## {f.name}  name={y.get('name')!r}  jobs={len(jobs)}  on={trig}")
    for jid, j in jobs.items():
        txt = yaml.safe_dump(j.get("steps", [])) + str(j.get("uses",""))
        n = len(PAT.findall(txt))
        tot_jobs += 1; tot_api += bool(n)
        m = j.get("strategy", {}).get("matrix")
        print(f"  {jid:28s} api_sites={n:3d} matrix={'y' if m else '-'} if={str(j.get('if',''))[:90]!r}")
print(f"TOTAL jobs={tot_jobs} jobs_with_api_sites={tot_api}")

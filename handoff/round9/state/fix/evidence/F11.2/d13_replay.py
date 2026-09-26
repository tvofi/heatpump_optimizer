"""D13-s1-03 companion (fixer.md step 3): the follower's own decision, replayed.

For every first-parent PR merge on origin/main since SINCE, at the merged head
(the merge's second parent): list the head's workflow runs (REST, read-only),
and for each run of a watched workflow that concluded `failure`, call the
production `contract_rerun.stale_contract` with the contract runs that existed
when that red finished (created_at <= its updated_at). RESULT stale_heads = heads
where at least one red would re-run the contract (the ordering gap, each a
contract that listed the reds before one of them existed); null control
clean_heads_rerun = re-runs the decision asks for at heads with no red (must be 0).
Needs GITHUB_TOKEN. Run from the repository root at the head that carries
.claude/workflows/contract_rerun.py.
"""
import json, os, subprocess, sys, importlib.util
SINCE = sys.argv[1] if len(sys.argv) > 1 else "2026-09-24T00:00:00Z"
spec = importlib.util.spec_from_file_location("crr", ".claude/workflows/contract_rerun.py")
crr = importlib.util.module_from_spec(spec); spec.loader.exec_module(crr)
WATCH = {".github/workflows/" + f for f in ("tests.yml", "governance.yml", "hassfest.yml", "validate.yml", "codeql.yml", "budget-raise-gate.yml")}
tok = os.environ["GITHUB_TOKEN"]
def get(path):
    out = subprocess.run(["curl", "-sS", "-H", f"Authorization: Bearer {tok}", "-H", "Accept: application/vnd.github+json",
                          "https://api.github.com/repos/tvofi/heatpump_optimizer/" + path], capture_output=True, text=True, check=True).stdout
    return json.loads(out)
log = subprocess.run(["git", "log", "--first-parent", "--merges", f"--since={SINCE}", "--format=%P|%s", "origin/main"],
                     capture_output=True, text=True, check=True).stdout.splitlines()
heads = stale = reds_seen = clean_rerun = no_contract = 0
rows = []
for line in log:
    parents, subj = line.split("|", 1)
    if not subj.startswith("Merge pull request #"):
        continue
    head = parents.split()[1]
    runs = get(f"actions/runs?head_sha={head}&per_page=100").get("workflow_runs", [])
    contract = [r for r in runs if r.get("path") == crr.CONTRACT_WORKFLOW]
    if not contract:
        no_contract += 1
        continue
    heads += 1
    reds = [r for r in runs if r.get("path") in WATCH and r.get("conclusion") == "failure"]
    hit = []
    for red in reds:
        before = [c for c in contract if str(c.get("created_at")) <= str(red.get("updated_at"))]
        # the contract's newest attempt at that moment started when it was created or re-run;
        # a later attempt's run_started_at is after the red, so use created_at for runs whose
        # attempt started after the red finished
        view = [dict(c, run_started_at=c["run_started_at"] if str(c["run_started_at"]) <= str(red["updated_at"]) else c["created_at"],
                     status="completed") for c in before]
        a, rid, why = crr.stale_contract(red, view)
        if a == "rerun":
            hit.append(f"{red['path'].split('/')[-1]}#{red['id']}")
    for ok in [r for r in runs if r.get("path") in WATCH and r.get("conclusion") == "success"][:1]:
        if crr.stale_contract(ok, contract)[0] == "rerun":
            clean_rerun += 1
    reds_seen += bool(reds)
    stale += bool(hit)
    rows.append(f"# {subj.split()[3]} head {head[:8]}: reds={len(reds)} rerun_on={hit}")
print("\n".join(rows))
print(f"RESULT merged_heads_with_contract={heads} count")
print(f"RESULT heads_with_a_red={reds_seen} count")
print(f"RESULT stale_heads={stale} count")
print(f"RESULT clean_heads_rerun={clean_rerun} count")
print(f"RESULT heads_without_contract_run={no_contract} count")

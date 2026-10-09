#!/bin/bash
# Step 11 for PR #2075: the head's own check-runs (latest per name), the range's,
# and the 17 required contexts of ruleset 23698884. Read-only GitHub reads.
set -uo pipefail
EV=/Users/timmalmstrom/hpo-seats/review-2075/evidence
REPO=tvofi/heatpump_optimizer
HEAD=094f2c0d2696b4bd04cd485b9e7fc3f144620053
BASE=b2b6acd64cde652676a568e93c05f021571ebe5e
PY3="$HOME/.local/state/hpo/venv-ci/bin/python3"

echo "=== head commit identity (is the head bot-pushed?) ==="
git -C /private/tmp/r9-main show -s --format='  author    %an <%ae>%n  committer %cn <%ce>%n  subject   %s%n  parents   %P' "$HEAD"

echo
echo "=== commits in the branch's own range (merge-base..head) ==="
git -C /private/tmp/r9-main log --format='  %h %an %s' "$BASE..$HEAD"

echo
echo "=== check-runs at the HEAD, latest per name ==="
gh api --paginate "repos/$REPO/commits/$HEAD/check-runs?per_page=100" \
  > "$EV/checkruns-head.json" 2>"$EV/checkruns-head.err"; echo "  api rc=$?"
"$PY3" -I - "$EV/checkruns-head.json" <<'PY'
import json, sys
raw = open(sys.argv[1]).read()
dec = json.JSONDecoder(); i = 0; docs = []
while True:
    while i < len(raw) and raw[i].isspace(): i += 1
    if i >= len(raw): break
    v, i = dec.raw_decode(raw, i); docs.append(v)
runs = []
for d in docs: runs.extend(d.get("check_runs", []))
latest = {}
for r in runs:
    k = r["name"]
    if k not in latest or r["id"] > latest[k]["id"]: latest[k] = r
print(f"  total check-run records: {len(runs)}; distinct names: {len(latest)}")
if not runs:
    print("  NONE -- the head carries no check-run at all")
for name in sorted(latest):
    r = latest[name]
    print(f"    {name:38s} status={r['status']:12s} conclusion={str(r['conclusion']):12s} id={r['id']}")
PY

echo
echo "=== combined commit statuses at the HEAD (some contexts are statuses) ==="
gh api "repos/$REPO/commits/$HEAD/status" > "$EV/status-head.json" 2>&1; echo "  api rc=$?"
"$PY3" -I -c '
import json,sys
d=json.load(open(sys.argv[1]))
print("  state:", d.get("state"), " total_status:", d.get("total_status"))
for s in d.get("statuses", []): print(f"    {s[\"context\"]:38s} {s[\"state\"]}")
' "$EV/status-head.json"

echo
echo "=== the PR's own statusCheckRollup ==="
gh api "repos/$REPO/pulls/2075" --jq '.mergeStateStatus, .draft, .head.sha' 2>&1 | sed 's/^/  /'
gh api graphql -f query='query{repository(owner:"tvofi",name:"heatpump_optimizer"){pullRequest(number:2075){mergeStateStatus commits(last:1){nodes{commit{statusCheckRollup{state contexts{__typename name context status conclusion state}}}}}}}}' \
  > "$EV/rollup.json" 2>&1; echo "  graphql rc=$?"
"$PY3" -I -c '
import json,sys
d=json.load(open(sys.argv[1]))
pr=d["data"]["repository"]["pullRequest"]
print("  mergeStateStatus:", pr["mergeStateStatus"])
for n in pr["commits"]["nodes"]:
    rc=n["commit"]["statusCheckRollup"]
    if rc is None: print("  statusCheckRollup: None -- the head carries NO check"); continue
    print("  rollup state:", rc.get("state"))
    for c in rc.get("contexts",[]):
        nm=c.get("name") or c.get("context")
        st=c.get("status") or c.get("state")
        print(f"    {nm:40s} {str(st):14s} conclusion={c.get(\"conclusion\")}")
' "$EV/rollup.json"

echo
echo "=== required contexts of ruleset 23698884 ==="
gh api "repos/$REPO/rulesets/23698884" > "$EV/ruleset.json" 2>&1; echo "  api rc=$?"
"$PY3" -I -c '
import json,sys
d=json.load(open(sys.argv[1]))
print("  name:", d.get("name"), " enforcement:", d.get("enforcement"), " target:", d.get("target"))
for r in d.get("rules",[]):
    if r.get("type")=="required_status_checks":
        ctx=[c["context"] for c in r["parameters"]["required_status_checks"]]
        print(f"  RESULT required contexts = {len(ctx)}")
        for c in ctx: print("    -", c)
' "$EV/ruleset.json"

#!/bin/bash
# merge-when-green.sh <pr> <head> <body>: wait until every REQUIRED check (ruleset 23698884) at <head>
# is complete with none failed, then merge at that head. Non-required reds do not block (answer them separately).
pr=$1 h=$2 body=$3 R=tvofi/heatpump_optimizer
REQ=$(gh api repos/$R/rulesets/23698884 -q '[.rules[]|select(.type=="required_status_checks")|.parameters.required_status_checks[].context]')
for i in $(seq 1 120); do
  st=$(gh api "repos/$R/commits/$h/check-runs?per_page=100" | python3 -c '
import json,sys
req=set(json.loads(sys.argv[1])); runs=[x for x in json.load(sys.stdin)["check_runs"] if x["name"] in req]
seen={x["name"] for x in runs}
pend=sum(1 for x in runs if x["status"]!="completed")+len(req-seen)
fail=sum(1 for x in runs if x["conclusion"] in ("failure","cancelled","timed_out"))
print(pend, fail)' "$REQ")
  pend=${st% *} fail=${st#* }
  echo "$(date -u +%T) required pend=$pend fail=$fail"
  if [ "$pend" = 0 ] && [ "$fail" = 0 ]; then
    gh pr ready $pr -R $R >/dev/null 2>&1
    gh pr merge $pr -R $R --merge --match-head-commit $h --body "$body"
    gh pr view $pr -R $R --json state,mergeCommit -q '.state+" "+.mergeCommit.oid'; exit 0
  fi
  sleep 120
done; echo TIMEOUT

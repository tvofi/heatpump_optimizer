#!/bin/bash
# mkrev.sh <pr> <head40> <nonce>: writes rev/<pr>.txt and rev/<pr>.json (full ccr) for a cloud reviewer, handing it the dispatch record.
set -euo pipefail
d=$(dirname "$0")/rev
[[ $2 =~ ^[0-9a-f]{40}$ ]] || { echo "head must be 40-hex" >&2; exit 2; }
rec=$(awk -v p="$1" -v h="$2" -v n="$3" '$1==p && $2==h && $4==n' ~/.zcode/bus/dispatched | tail -1)
[ -n "$rec" ] || { echo "no dispatch record for $1 $2 $3" >&2; exit 2; }
python3 - "$1" "$2" "$3" "$rec" "$d" <<'P'
import json,sys
pr,head,nonce,rec,d=sys.argv[1:]; nonce8=nonce[:8]
t=f"""CLOUD REVIEWER seat for PR #{pr} of tvofi/heatpump_optimizer, at head {head}. Bus nonce: {nonce}. Never send push notifications.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout.
Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them exactly; this round's reviewer measures with the finder's harness. Earlier rounds' verdicts are the PR's `Fix review:` comments: say which round this is. Fetch the PR head with `git fetch origin {head}`; the PR body is in the PR. Verify each claim adversarially: mutate the fix and check the tests fail, and check every figure in the body at this head. Check that it merges with origin/main (`git merge-tree --write-tree`) and read CI on this head from the check-runs API.
Output: write verdict.md, whose first line is exactly `Fix review: <merge|blocked> {head}` for merge, or `Fix review: blocked {head} <class>: <reason>` (no brackets) for blocked, then a blank line, then `bus-nonce: {nonce}`. Put the evidence in an `ev/` directory beside it, including `ev/HEAD` holding the 40-hex head you measured, under /tmp/seat/rev{pr}/. Do NOT run bus.sh: the dispatch record lives on the orchestrator's machine, and the orchestrator publishes the verdict there. Return it on a probe ref, and push nothing else: `cd /tmp/seat/rev{pr} && rm -rf pr && git init -q pr && cp -r verdict.md ev pr/ && git -C pr add -A && git -C pr -c user.name=hpo-seat -c user.email=hpo-seat@users.noreply.github.com commit -qm "verdict {pr} {head}" && git -C /home/user/heatpump_optimizer fetch -q /tmp/seat/rev{pr}/pr HEAD && git -C /home/user/heatpump_optimizer push -q origin FETCH_HEAD:refs/heads/probe/rev-{pr}-{nonce8}`. That ref is the return signal. Do not post comments, approve or merge.
Never write to any branch except that probe ref. Never work around a hook or a refusal; report it in the verdict instead.
"""
open(f"{d}/{pr}.txt","w").write(t)
json.dump({"job_config":{"ccr":{"environment_id":"env_01WRxrDVGyUChFCGzSXYJnaj","session_context":{"allowed_tools":["preset:default","Bash","Glob","Grep","Read","Write","BashOutput","KillBash","Monitor"],"model":"claude-opus-5-5","sources":[{"git_repository":{"url":"https://github.com/tvofi/heatpump_optimizer"}}]},"events":[{"data":{"type":"user","message":{"role":"user","content":t}}}]}}},open(f"{d}/{pr}.json","w"))
print(f"{d}/{pr}.json")
P

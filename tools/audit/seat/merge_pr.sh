#!/bin/bash
# merge_pr.sh <pr> <sha> <evidence-dir> <owner|app> [--mandate <comment-id>] [--ready] [issues-to-verify...]
# merge_pr.sh --self-test
#
# owner mode approves code-owned paths as tvofi's account under the mandate
# comment <comment-id> on a record issue (#201 or its continuation), read live at this run by budget_raise_gate.py's
# own reading (`_mandate`, `mandate_state` judged now, its scope the gate's
# MANDATE_COVERS_CODE_OWNED). No --mandate, or one not in force now, refuses before anything is
# posted: the script never defaults to a mandate, because a stale one is a
# forged grant (until R10-TRAIN-RAISE-HOLD it hard-coded one that had expired). A budget RAISE is still the gate's to refuse: this
# approval says nothing of the raise justification `budget-raise-gate` reads.
# A draft pull request refuses before anything is posted, unless --ready says
# to mark it ready first.
# owner mode never posts on a pull request whose head is a fork's (decision
# 0017): this approval is given after, and on the basis of, the verdict, which
# on such a head the contributor's reviewer wrote. Whether a head is
# cross-repository is tools/pr/outside.py's answer over the pulls API object,
# asked before the mandate is read; unanswered is a refusal. app mode on such a
# head merges only where outside.py's whole contract (`check`) admits this head.
set -uo pipefail
R=tvofi/heatpump_optimizer
# The self-test grades this script's own tree; a merge runs from the main checkout.
if [ "${1:-}" = --self-test ]; then [ -n "${PR_BOUND:-}" ] || { . "$(dirname -- "$0")/pr_args.sh"; pr_bounded merge_pr bash "$0" --self-test; }  # pr_args.sh's self-test bound
  cd "$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel)" || exit 1
else cd "$(git -C "$(dirname -- "$0")" rev-parse --path-format=absolute --git-common-dir)/.." || exit 1; fi
SELF=$PWD/tools/audit/seat/merge_pr.sh
OUTSIDE=$PWD/tools/pr/outside.py  # never from the environment; the self-test asks this tree's own copy

# Whose head <pr> is, by outside.py's own reading: prints `OURS` (rc 0), or
# `CROSS-REPOSITORY: <why>` or `REFUSE: <why>` (rc 1). No second definition here.
head_is_ours() { # <repo> <pr>
  python3 -I - "$1" "$2" "$OUTSIDE" <<'P'
import importlib.util, json, subprocess, sys
repo, pr, path = sys.argv[1:4]
r = subprocess.run(["gh", "api", f"repos/{repo}/pulls/{pr}"], capture_output=True, text=True)
try:
    pull = json.loads(r.stdout) if r.returncode == 0 else None
except ValueError:
    pull = None
if not isinstance(pull, dict) or not isinstance(pull.get("head"), dict):
    print(f"REFUSE: #{pr} could not be read from the pulls API; an unread head is never taken for ours")
    sys.exit(1)
try:
    spec = importlib.util.spec_from_file_location("outside", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    facts = mod.pull_facts(repo, int(pr), pull)
    cross = mod.cross_repository(facts, repo)  # outside.py's one definition, never re-typed here
except Exception as e:  # fail closed: outside.py's answer, or none
    print(f"REFUSE: {path} could not say whether #{pr}'s head is cross-repository ({str(e).splitlines()[0][:160] if str(e) else type(e).__name__})")
    sys.exit(1)
if cross:
    print(f"CROSS-REPOSITORY: #{pr}'s head is {str(facts['head_repo'] or 'a deleted fork')[:80]}'s; owner mode posts nothing there, "
          "class O is outside.py's approve subcommand from our own read (decision 0017)")
    sys.exit(1)
print("OURS")
P
}

# outside.py runs from origin/main's blob or not at all, as the train's does
# (`Train.outside_is_mains`): `outside_is_mains outside` compares outside.py alone,
# before whose head is read; `outside_is_mains contract` every file of the train's
# OUTSIDE_MAIN_COPIES, before the contract. Prints `REFUSE: <why>` and returns 1.
outside_is_mains() { # <outside|contract>
  local rel want have rels
  if [ "$1" = outside ]; then rels=tools/pr/outside.py
  else rels=$(python3 -I - "$PWD/tools/audit/seat/merge_train.py" <<'P'
import importlib.util, sys
s = importlib.util.spec_from_file_location("merge_train", sys.argv[1]); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
print("\n".join(m.OUTSIDE_MAIN_COPIES))
P
) || { echo "REFUSE: the train's OUTSIDE_MAIN_COPIES could not be read"; return 1; }; fi
  git fetch -q origin main 2>/dev/null || { echo "REFUSE: origin/main could not be fetched for the outside contract"; return 1; }
  for rel in $rels; do
    want=$(git rev-parse -q --verify "origin/main:$rel" 2>/dev/null); have=$(git hash-object -- "$rel" 2>/dev/null)
    [[ "$want" =~ ^[0-9a-f]{40}$ ]] && [ "$want" = "$have" ] || {
      echo "REFUSE: $rel in this checkout is not origin/main's copy (main ${want:0:12}, here ${have:0:12}): the outside contract is main's or it is not run; run from a checkout at main"; return 1; }
  done
}

# outside.py's whole contract for the cross-repository <pr>, at origin/main:
# prints `ADMITTED: <why>` (rc 0) only when it admits <pr> at <sha>, else
# `CONTRACT REFUSES ...` or `REFUSE: <why>` (rc 1). No second contract here.
outside_contract() { # <repo> <pr> <sha>
  python3 -I - "$1" "$2" "$3" "$OUTSIDE" <<'P'
import importlib.util, sys
repo, pr, sha, path = sys.argv[1:5]
try:
    spec = importlib.util.spec_from_file_location("outside", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rc, lines = mod.check(repo, int(pr), "origin/main")
except Exception as e:  # fail closed: an unread contract admits nothing
    print(f"REFUSE: {path}'s contract for #{pr} could not be read ({str(e).splitlines()[0][:160] if str(e) else type(e).__name__})")
    sys.exit(1)
why = "; ".join(str(ln) for ln in lines)
if rc == 0 and any(str(ln).startswith("OUTSIDE: ") and f" at {sha}: " in str(ln) for ln in lines):
    print("ADMITTED: " + why[:400])
    sys.exit(0)
if rc == 0:
    why = f"it admitted a head other than {sha[:12]}: {why}"
print(f"CONTRACT REFUSES #{pr} at {sha[:12]}: {why[:400]} (decision 0017)")
sys.exit(1)
P
}

# The mandate in force now, by the gate's own reading: prints `IN FORCE: <why>`
# (rc 0) or `REFUSE: <why>` (rc 1). The gate file is the tree's own.
mandate_in_force() { # <repo> <comment-id>
  python3 -I - "$1" "$2" "$PWD/tools/policy" <<'P'
import datetime, sys
repo, cid, gate = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sys.path.insert(0, gate)
import budget_raise_gate as g
try:
    comment, thread = g._mandate(repo, cid)
except Exception as e:  # fail closed: an unread mandate grants nothing
    print(f"REFUSE: mandate {cid} could not be read ({str(e).splitlines()[0][:160] if str(e) else type(e).__name__})")
    sys.exit(1)
now = datetime.datetime.now(datetime.timezone.utc)
ok, why = g.mandate_state(cid, comment, thread, now, now.strftime("%Y-%m-%dT%H:%M:%SZ"), "merge",
                          g.MANDATE_COVERS_CODE_OWNED, "an owner approval of code-owned paths")
print(("IN FORCE: " if ok else "REFUSE: ") + why)
sys.exit(0 if ok else 1)
P
}

# The approval body: declared an agent's and citing the mandate by id, the two
# things budget_raise_gate's `approval` reads (AGENT_DECLARED, MANDATE_CITE).
owner_body() { # <sha> <comment-id> <in-force why>
  printf 'Agent approval (the orchestrator, not tvofi in person) of code-owned paths at head %s after the "Fix review: merge" verdict, under mandate %s: %s.\n' "$1" "$2" "$3"
}

# Every refusal that must come before a post: argv, draft, mandate. Prints the
# refusal and returns 1, or returns 0; READY_OWED=1 when --ready must mark it.
gates() { # <pr> <mode> <mandate-id> <ready 0|1> <sha>
  READY_OWED=0
  case "$2" in owner|app) ;; *) echo "USAGE: mode '$2' is neither owner nor app"; return 1 ;; esac
  d=$(gh pr view "$1" --repo $R --json isDraft --jq .isDraft) || { echo "REFUSE: #$1's draft state could not be read"; return 1; }
  if [ "$d" = true ]; then
    [ "$4" = 1 ] || { echo "DRAFT: #$1 is a draft; pass --ready to mark it ready, or ready it first"; return 1; }
    READY_OWED=1
  fi
  if [ "$2" = owner ] && ! [[ "$3" =~ ^[0-9]{6,}$ ]]; then
    echo "MANDATE REQUIRED: owner mode needs --mandate <comment-id> naming the mandate in force on a record issue (got '$3')"; return 1
  fi
  HEAD_WHY=$(outside_is_mains outside) || { echo "OUTSIDE $HEAD_WHY"; return 1; }
  if ! HEAD_WHY=$(head_is_ours $R "$1"); then
    # Only app mode merges a fork head, and only where the contract admits this head.
    { [ "$2" = app ] && [[ "$HEAD_WHY" == CROSS-REPOSITORY:* ]]; } || { echo "OUTSIDE $HEAD_WHY"; return 1; }
    CONTRACT_WHY=$(outside_is_mains contract) || { echo "OUTSIDE $CONTRACT_WHY"; return 1; }
    CONTRACT_WHY=$(outside_contract $R "$1" "$5") || { echo "OUTSIDE $CONTRACT_WHY"; return 1; }
  fi
  [ "$2" = owner ] || return 0
  MANDATE_WHY=$(mandate_in_force $R "$3") || { echo "MANDATE $MANDATE_WHY"; return 1; }
  MANDATE_WHY=${MANDATE_WHY#IN FORCE: }
}

# P96 (a): app_comment.sh refuses a merge verdict off the live head, so a verdict
# for another head cannot post here. The reviewed head is the verdict's own
# `Fix review: merge <sha40>` line; the route for a carried head is the train,
# which runs `app_approve.sh --carry` at admission and at the head.
carried_head() { # <pr> <head> <verdict file>: prints CARRIED HEAD and returns 1 when they differ
  local v
  v=$(grep -m1 -oE 'Fix review: merge [0-9a-f]{40}' "$3" 2>/dev/null | grep -oE '[0-9a-f]{40}$')
  { [ -z "$v" ] || [ "$v" = "$2" ]; } && return 0  # mut:carried
  echo "CARRIED HEAD: #$1's verdict reviewed $v but the head is $2; route: a one-entry queue [{\"pr\": $1, \"verdict\": \"$v\"}] to \`merge_train.py run\` (the train runs app_approve.sh --carry at admission and at the head), not merge_pr.sh"
  return 1
}

# K15 (b): a check-run left queued or in progress over a completed workflow
# run blocks the merge as BLOCKED forever (#2559: 8 attempts); the train's
# classifier re-runs each such run once, logged with its run id, and re-reads.
unstale_head() { # <sha>
  python3 -I "$PWD/tools/audit/seat/merge_train.py" unstale --repo "$R" "$1"
}

self_test() {
  local T pass=0 fail=0 out
  T=$(mktemp -d) || return 1
  # A fake gh: the draft read answers $FAKE_DRAFT; the mandate read answers
  # $FAKE_MANDATE (a JSON file) or a 404; every call is logged.
  cat > "$T/gh" <<'G'
#!/bin/bash
echo "$*" >> "$FAKE_LOG"
case "$*" in
  *isDraft*) echo "${FAKE_DRAFT:-false}" ;;
  *issues/comments/*) [ -n "${FAKE_MANDATE:-}" ] && cat "$FAKE_MANDATE" || { echo "gh: Not Found (HTTP 404)" >&2; exit 1; } ;;
  *issues/[0-9]*/comments*) echo "[[]]" ;;
  *pulls/[0-9]*) [ -n "${FAKE_PULL:-}" ] && cat "$FAKE_PULL" || { echo "gh: HTTP 502" >&2; exit 1; } ;;
  *check-runs*) cat "$FAKE_RUNS" ;;
  */rerun*) cp "$FAKE_RUNS_AFTER" "$FAKE_RUNS" ;;
  *actions/runs/*) echo "$FAKE_RUN_STATUS" ;;
  *) echo "fake gh: unexpected $*" >&2; exit 1 ;;
esac
G
  chmod +x "$T/gh"
  # A fake git answering the main-copy comparison alone: origin/main's blob of every path is f*40,
  # and this checkout's copy of $FAKE_STALE is another; every other git call is the real git's.
  export REAL_GIT; REAL_GIT=$(command -v git)
  cat > "$T/git" <<'G'
#!/bin/bash
case "$*" in
  "fetch -q origin main") echo "git $*" >> "${FAKE_LOG:-/dev/null}"; exit 0 ;;
  "rev-parse -q --verify origin/main:"*) printf 'f%.0s' {1..40}; echo; exit 0 ;;
  "hash-object -- "*) [ "$3" = "${FAKE_STALE:-}" ] && { printf '0%.0s' {1..40}; echo; } || { printf 'f%.0s' {1..40}; echo; }; exit 0 ;;
esac
exec "$REAL_GIT" "$@"
G
  chmod +x "$T/git"
  # outside.py is part 1's (decision 0017), and the real one is asked: its `pull_facts` reads the pulls object.
  printf '{"number": 7, "head": {"ref": "fix/x", "repo": {"full_name": "%s"}}}' "$R" > "$T/ours.json"
  printf '{"number": 7, "head": {"ref": "fix/x", "repo": {"full_name": "contributor/heatpump_optimizer"}}}' > "$T/theirs.json"
  export FAKE_PULL=$T/ours.json
  mk() { # <from-min> <until-min> [scope] -> a mandate comment, minutes from now
    python3 -I - "$1" "$2" "${3:-all}" <<'P'
import datetime, json, sys
now = datetime.datetime.now(datetime.timezone.utc)
iso = lambda m: (now + datetime.timedelta(minutes=int(m))).strftime("%Y-%m-%dT%H:%M:%SZ")
c = iso(sys.argv[1])
print(json.dumps({"id": 4100000001, "user": {"login": "tvofi", "id": 70032254, "type": "User"},
                  "created_at": c, "updated_at": c,
                  "issue_url": "https://api.github.com/repos/tvofi/heatpump_optimizer/issues/201",
                  "body": f"MANDATE: agents may approve as tvofi, scope {sys.argv[3]}, from {c} until {iso(sys.argv[2])}"}))
P
  }
  mk -60 60 > "$T/live.json"; mk -120 -10 > "$T/expired.json"; S7=$(printf 'c%.0s' {1..40})
  mk -60 60 code-owned > "$T/code-owned.json"; mk -60 60 budget-raise > "$T/raise.json"
  ck() { # <name> <want rc> <want substring> <draft> <mandate file> -- gates args...
    local name=$1 want=$2 sub=$3 draft=$4 mf=$5 rc; shift 6
    : > "$T/log"
    out=$(PATH="$T:$PATH" FAKE_LOG="$T/log" FAKE_DRAFT=$draft FAKE_MANDATE=$mf gates "$@" "$S7" 2>&1); rc=$?
    if [ "$rc" = "$want" ] && [[ "$out" == *"$sub"* ]]; then pass=$((pass + 1)); echo "  ok   $name"
    else fail=$((fail + 1)); echo "  FAIL $name (rc=$rc: $out)"; fi
  }
  ck "app mode on a ready pull request passes the gates (null control)" 0 "" false "" -- 7 app "" 0
  ck "owner mode with no --mandate refuses, never a default" 1 "MANDATE REQUIRED" false "$T/live.json" -- 7 owner "" 0
  ck "owner mode with a non-id --mandate refuses" 1 "MANDATE REQUIRED" false "$T/live.json" -- 7 owner "yesterday" 0
  ck "owner mode under a mandate in force now passes" 0 "" false "$T/live.json" -- 7 owner 4100000001 0
  ck "owner mode under a code-owned mandate in force now passes" 0 "" false "$T/code-owned.json" -- 7 owner 4100000001 0
  ck "owner mode under a budget-raise mandate refuses: the gate's MANDATE_COVERS_CODE_OWNED excludes it" 1 "does not cover" false "$T/raise.json" -- 7 owner 4100000001 0
  ck "owner mode under an expired mandate refuses with the gate's why" 1 "expired" false "$T/expired.json" -- 7 owner 4100000001 0
  ck "owner mode under a mandate that does not exist refuses" 1 "not a comment that exists" false "" -- 7 owner 4100000001 0
  FAKE_PULL=$T/theirs.json ck "owner mode on a cross-repository head refuses, naming the fork (decision 0017)" 1 "OUTSIDE CROSS-REPOSITORY: #7's head is contributor/heatpump_optimizer's" false "$T/live.json" -- 7 owner 4100000001 0
  if grep -q 'pulls/7' "$T/log" && ! grep -q 'issues/comments\|pr review' "$T/log"; then pass=$((pass + 1)); echo "  ok   ... having read the pull request and neither the mandate nor a post"
  else fail=$((fail + 1)); echo "  FAIL ... having read the pull request and neither the mandate nor a post ($(tr '\n' ';' < "$T/log"))"; fi
  sed 's/"number": 7/"number": 8/' "$T/ours.json" > "$T/other.json"
  FAKE_PULL=$T/other.json ck "owner mode refuses a pulls object of another pull request: the real outside.py's pull_facts reads it" 1 "is not #7" false "$T/live.json" -- 7 owner 4100000001 0
  FAKE_PULL= ck "owner mode on a pull request that cannot be read refuses: an unread head is never ours" 1 "OUTSIDE REFUSE: #7 could not be read" false "$T/live.json" -- 7 owner 4100000001 0
  OUTSIDE=$T/absent.py ck "owner mode with no outside.py to ask refuses, fail closed" 1 "OUTSIDE REFUSE: $T/absent.py could not say" false "$T/live.json" -- 7 owner 4100000001 0
  # App mode asks outside.py's whole contract on a cross-repository head (r11-outside-contributor-cycle-p3
  # carry 7): a stub keeps the real pull_facts and cross_repository and answers `check` from FAKE_CHECK
  # (a head it admits, or a REFUSE line), logging each call.
  cat > "$T/outside_stub.py" <<'O'
import importlib.util, os
_s = importlib.util.spec_from_file_location("real_outside", os.environ["REAL_OUTSIDE"])
_m = importlib.util.module_from_spec(_s); _s.loader.exec_module(_m)
pull_facts, cross_repository = _m.pull_facts, _m.cross_repository
def check(repo, pr, ref, **kw):
    open(os.environ["FAKE_LOG"], "a").write(f"check {repo} {pr} {ref}\n")
    at = os.environ.get("FAKE_CHECK", "")
    if at.startswith("REFUSE"):
        return 1, [at]
    return 0, [f"OUTSIDE: #{pr} by contributor (id 1) at {at}: 1 class-F and 0 class-O path(s), none refused"]
O
  export REAL_OUTSIDE=$OUTSIDE
  OUTSIDE=$T/outside_stub.py FAKE_PULL=$T/theirs.json FAKE_CHECK="REFUSE: class R: tools/x.py is a path an outside pull request does not change" \
    ck "app mode on a cross-repository head the outside contract refuses refuses with outside.py's reason (decision 0017)" 1 "OUTSIDE CONTRACT REFUSES #7 at cccccccccccc: REFUSE: class R: tools/x.py" false "" -- 7 app "" 0
  if grep -qx 'check tvofi/heatpump_optimizer 7 origin/main' "$T/log"; then pass=$((pass + 1)); echo "  ok   ... having asked the contract at origin/main"
  else fail=$((fail + 1)); echo "  FAIL ... having asked the contract at origin/main ($(tr '\n' ';' < "$T/log"))"; fi
  OUTSIDE=$T/outside_stub.py FAKE_PULL=$T/theirs.json FAKE_CHECK=$(printf 'b%.0s' {1..40}) \
    ck "app mode on a cross-repository head the contract admits at ANOTHER head refuses, naming both" 1 "it admitted a head other than cccccccccccc" false "" -- 7 app "" 0
  OUTSIDE=$T/outside_stub.py FAKE_PULL=$T/theirs.json FAKE_CHECK=$S7 \
    ck "app mode on a cross-repository head the contract admits at this head passes the gates" 0 "" false "" -- 7 app "" 0
  OUTSIDE=$T/outside_stub.py FAKE_PULL=$T/ours.json FAKE_CHECK="REFUSE: never asked" \
    ck "null control: app mode on a head of ours passes and never asks the contract" 0 "" false "" -- 7 app "" 0
  if grep -q 'pulls/7' "$T/log" && ! grep -q '^check ' "$T/log"; then pass=$((pass + 1)); echo "  ok   ... having read the pull request and asked no contract"
  else fail=$((fail + 1)); echo "  FAIL ... having read the pull request and asked no contract ($(tr '\n' ';' < "$T/log"))"; fi
  FAKE_PULL= ck "app mode on a pull request that cannot be read refuses: an unread head is never ours" 1 "OUTSIDE REFUSE: #7 could not be read" false "" -- 7 app "" 0
  # outside.py runs from origin/main's blob or not at all, as the train's (`Train.outside_is_mains`,
  # whose OUTSIDE_MAIN_COPIES this script reads): before whose-head is read, and the whole list
  # before the contract.
  for m in app owner; do
    FAKE_STALE=tools/pr/outside.py ck "$m mode with a checkout whose outside.py is not origin/main's refuses before executing it, on a head of ours" 1 "OUTSIDE REFUSE: tools/pr/outside.py in this checkout is not origin/main's copy" false "$T/live.json" -- 7 $m 4100000001 0
    if ! grep -q 'pulls/7' "$T/log"; then pass=$((pass + 1)); echo "  ok   ... having read no pull request"
    else fail=$((fail + 1)); echo "  FAIL ... having read no pull request ($(tr '\n' ';' < "$T/log"))"; fi
  done
  OUTSIDE=$T/outside_stub.py FAKE_PULL=$T/theirs.json FAKE_CHECK=$S7 FAKE_STALE=tools/policy/policy_lint.mjs \
    ck "app mode on a fork head refuses when a file the contract reads is not origin/main's, though the contract would admit" 1 "OUTSIDE REFUSE: tools/policy/policy_lint.mjs in this checkout is not origin/main's copy" false "" -- 7 app "" 0
  if ! grep -q '^check ' "$T/log"; then pass=$((pass + 1)); echo "  ok   ... having asked no contract"
  else fail=$((fail + 1)); echo "  FAIL ... having asked no contract ($(tr '\n' ';' < "$T/log"))"; fi
  FAKE_STALE=tools/policy/policy_lint.mjs ck "null control: a head of ours is read whatever the contract's other files say (only outside.py is compared before the read)" 0 "" false "" -- 7 app "" 0
  # The stub stands in for exactly the real module's calls: each name this script makes, bound with
  # the arguments it passes, on the real outside.py (a renamed entry point fails here, not on a merge).
  if python3 -I - "$REAL_OUTSIDE" <<'P'
import importlib.util, inspect, sys
s = importlib.util.spec_from_file_location("outside", sys.argv[1]); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
inspect.signature(m.pull_facts).bind("o/r", 7, {}); inspect.signature(m.cross_repository).bind({}, "o/r")
inspect.signature(m.check).bind("o/r", 7, "origin/main")
P
  then pass=$((pass + 1)); echo "  ok   the real outside.py takes every call head_is_ours and outside_contract make, as they make it"
  else fail=$((fail + 1)); echo "  FAIL the real outside.py takes every call head_is_ours and outside_contract make, as they make it"; fi
  ck "a draft refuses without --ready, naming the flag" 1 "DRAFT: #7 is a draft; pass --ready" true "" -- 7 app "" 0
  ck "a draft with --ready passes the gates" 0 "" true "" -- 7 app "" 1
  PATH="$T:$PATH" FAKE_LOG="$T/log" FAKE_DRAFT=true gates 7 app "" 1 "$S7" >/dev/null
  if [ "$READY_OWED" = 1 ]; then pass=$((pass + 1)); echo "  ok   ... and owes the ready mark"
  else fail=$((fail + 1)); echo "  FAIL ... and owes the ready mark"; fi
  PATH="$T:$PATH" FAKE_LOG="$T/log" FAKE_DRAFT=false gates 7 app "" 1 "$S7" >/dev/null
  if [ "$READY_OWED" = 0 ]; then pass=$((pass + 1)); echo "  ok   a ready pull request with --ready owes no ready mark"
  else fail=$((fail + 1)); echo "  FAIL a ready pull request with --ready owes no ready mark"; fi
  stale='{"name":"budget-raise-gate","status":"in_progress","conclusion":null,"started_at":"1","id":7,"details_url":"https://github.com/o/r/actions/runs/119308796140/job/5"}'
  printf '%s\n' "$stale" | sed 's/"in_progress","conclusion":null,"started_at":"1"/"completed","conclusion":"success","started_at":"2"/' > "$T/after.json"
  for st in completed in_progress; do
    printf '%s\n' "$stale" > "$T/runs.json"; : > "$T/log"
    out=$(PATH="$T:$PATH" FAKE_LOG="$T/log" FAKE_RUNS="$T/runs.json" FAKE_RUNS_AFTER="$T/after.json" FAKE_RUN_STATUS=$st unstale_head "$(printf 'a%.0s' {1..40})" 2>&1); rc=$?
    n=$(grep -c '/actions/runs/119308796140/rerun' "$T/log")
    if [ "$st" = completed ] && [ "$rc" = 0 ] && [ "$n" = 1 ] && [[ "$out" == *"STALE budget-raise-gate"*119308796140* ]]; then
      pass=$((pass + 1)); echo "  ok   a stale check-run over a completed run is re-run once and logged with its run id"
    elif [ "$st" = in_progress ] && [ "$rc" = 0 ] && [ "$n" = 0 ]; then
      pass=$((pass + 1)); echo "  ok   a check-run whose run is still in progress is not re-run (null control)"
    else fail=$((fail + 1)); echo "  FAIL unstale_head with its run $st (rc=$rc, re-runs=$n: $out)"; fi
  done
  b=$(owner_body "$(printf 'a%.0s' {1..40})" 4100000001 "in force (scope all)")
  if python3 -I - "$PWD/tools/policy" "$b" <<'P'
import sys; sys.path.insert(0, sys.argv[1]); import budget_raise_gate as g
b = sys.argv[2]
sys.exit(0 if g.AGENT_DECLARED.search(b) and {a or c for a, c in g.MANDATE_CITE.findall(b)} == {"4100000001"} else 1)
P
  then pass=$((pass + 1)); echo "  ok   the owner body declares an agent and cites exactly the mandate given"
  else fail=$((fail + 1)); echo "  FAIL the owner body declares an agent and cites exactly the mandate given"; fi
  if grep -q "2026-09-2[45]" "$SELF"; then fail=$((fail + 1)); echo "  FAIL no mandate date is written into this script"
  else pass=$((pass + 1)); echo "  ok   no mandate date is written into this script"; fi
  # The merge call after the gates (#2444's fourth unpinned line). A scratch
  # clone, a fake gh answering the whole flow, the stub programs the script
  # prefers under tools/audit/, and a `sleep` that does not sleep. The null
  # control must record exactly `pr merge <N> --merge --match-head-commit <S>`;
  # a merge line replaced by `exit 0` records none, which reddens this step.
  local mo mm msha
  . "$(cd "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)/tests/throwaway_git.sh" && throwaway_git_env
  mo=$T/mo; mm=$T/mm; msha=$(printf 'd%.0s' {1..40})
  mkdir -p "$T/ev" "$T/bin2" "$T/state2"
  printf '# verdict\n' > "$T/ev/VERDICT.md"
  throwaway_git_init "$mo" -q -b main && printf 'a\n' > "$mo/a" \
    && git -C "$mo" add a && git -C "$mo" commit -q -m base \
    && throwaway_git_clone -q "$mo" "$mm"
  mkdir -p "$mm/tools/audit/seat"
  cp "$SELF" "$mm/tools/audit/seat/merge_pr.sh"
  # The real classifier, not a stub: unstale_head runs it against the fake
  # gh's empty check-run list, so the flow crosses the K15 (b) re-run as a no-op.
  # It imports gh_read.py from its own directory (R10-FLY-GH-READ-RETRY), so the
  # module travels with it: without it every flow stopped at STALE on an ImportError.
  cp "${SELF%/*}/merge_train.py" "${SELF%/*}/gh_read.py" "${SELF%/*}/proof_watch.py" "$mm/tools/audit/seat/"
  for p in app_approve.sh preflight.sh worktree_gc.sh; do
    printf '#!/bin/bash\nexit 0\n' > "$mm/tools/audit/$p"; chmod +x "$mm/tools/audit/$p"
  done
  # app_comment.sh leaves a mark when it is asked to post; postmerge.py is a stub
  # recording its argv, printing OWED and failing when FAKE_PM_RC says so.
  mkdir -p "$mm/tools/pr"
  cp "$T/outside_stub.py" "$mm/tools/pr/outside.py"  # the real pull_facts and cross_repository; `check` is FAKE_CHECK's
  # the approver identity posted_verdict reads (proof_watch.verdict_allowlist)
  printf 'VERDICT_AUTHORS="app[bot]"\nVERDICT_AUTHOR_ID=55\n' > "$mm/tools/pr/app_approve.sh"
  printf '#!/bin/bash\necho posted >> "$HPO_STATE_DIR/posted"\n' > "$mm/tools/pr/app_comment.sh"
  chmod +x "$mm/tools/pr/app_comment.sh"
  cat > "$mm/tools/audit/seat/postmerge.py" <<'PM'
import os, sys
open(os.environ["HPO_STATE_DIR"] + "/postmerge.argv", "a").write(" ".join(sys.argv[1:]) + "\n")
rc = int(os.environ.get("FAKE_PM_RC", "0"))
if rc: print("OWED record: refused")
sys.exit(rc)
PM
  printf 'import sys\nprint(sys.argv[2] if len(sys.argv) > 2 else "")\n' \
    > "$mm/tools/audit/seat/ref_privacy.py"
  printf '#!/bin/bash\nexit 0\n' > "$T/bin2/sleep"; chmod +x "$T/bin2/sleep"; cp "$T/git" "$T/bin2/git"
  cat > "$T/bin2/gh" <<'G'
#!/bin/bash
echo "$*" >> "$FAKE_LOG2"
case "$*" in
  *issues/42/comments*) cat "$FAKE_COMMENTS" 2>/dev/null ;;
  "api repos/tvofi/heatpump_optimizer/pulls/42") printf '{"number": 42, "head": {"ref": "fix/x", "repo": {"full_name": "%s"}}}' "${FAKE_HEAD_REPO:-tvofi/heatpump_optimizer}" ;;
  *headRefOid*) echo "$FAKE_SHA" ;;
  *isDraft*) echo false ;;
  *mergeStateStatus*) if [ -f "$FAKE_BLOCKED" ]; then rm -f "$FAKE_BLOCKED"; echo BLOCKED; else echo CLEAN; fi ;;
  *mergeCommit*) echo deadbeef ;;
  *title*) echo "a title" ;;
  *length*) echo 0 ;;
  *group_by*) echo "${FAKE_RED:-}" ;;
  *check-runs*) echo "" ;;
  "pr merge "*) [ "$FAKE_MERGE_FAIL" = 1 ] && exit 1; exit 0 ;;
  *) echo "fake gh: unexpected $*" >&2; exit 1 ;;
esac
G
  chmod +x "$T/bin2/gh"
  flow() { # <merge fails 0|1> [verdict sha]: the whole script, offline
    : > "$T/gh2.log"; rm -f "$T/state2/posted" "$T/state2/postmerge.argv"
    if [ -n "${2:-}" ]; then printf '# Fix review: merge %s\n' "$2" > "$T/ev/VERDICT.md"
    else printf '# verdict\n' > "$T/ev/VERDICT.md"; fi
    HPO_STATE_DIR=$T/state2 PATH="$T/bin2:$PATH" FAKE_LOG2=$T/gh2.log FAKE_SHA=$msha \
      FAKE_LOG=$T/check.log FAKE_BLOCKED=$T/blocked FAKE_COMMENTS=$T/comments FAKE_MERGE_FAIL=$1 FAKE_PM_RC=${FAKE_PM_RC:-0} bash "$mm/tools/audit/seat/merge_pr.sh" 42 "$msha" "$T/ev" app \
      > "$T/flow.out" 2>&1
    echo $? > "$T/flow.rc"
  }
  flow 0
  [ "$(cat "$T/flow.rc")" = 0 ] \
    && grep -qxF "pr merge 42 --merge --match-head-commit $msha" "$T/gh2.log"
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   null control: the merge records the reviewed head"
  else fail=$((fail + 1)); echo "  FAIL null control: the merge records the reviewed head ($(tail -1 "$T/flow.out"))"; fi
  FAKE_HEAD_REPO=contributor/heatpump_optimizer FAKE_CHECK="REFUSE: the base is x:y, not tvofi/heatpump_optimizer:main" flow 0
  [ "$(cat "$T/flow.rc")" != 0 ] && grep -q '^OUTSIDE CONTRACT REFUSES #42' "$T/flow.out" \
    && [ ! -f "$T/state2/posted" ] && ! grep -q '^pr merge' "$T/gh2.log"
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   app mode end to end: a fork head the contract refuses posts nothing and merges nothing"
  else fail=$((fail + 1)); echo "  FAIL app mode end to end: a fork head the contract refuses posts nothing and merges nothing ($(tail -1 "$T/flow.out"))"; fi
  FAKE_HEAD_REPO=contributor/heatpump_optimizer FAKE_CHECK=$msha flow 0
  [ "$(cat "$T/flow.rc")" = 0 ] && grep -qxF "pr merge 42 --merge --match-head-commit $msha" "$T/gh2.log"
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   null control: a fork head the contract admits at the head merges"
  else fail=$((fail + 1)); echo "  FAIL null control: a fork head the contract admits at the head merges ($(tail -1 "$T/flow.out"))"; fi
  flow 1
  [ "$(cat "$T/flow.rc")" != 0 ]
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   a refused merge fails the script (the line's own exit)"
  else fail=$((fail + 1)); echo "  FAIL a refused merge fails the script"; fi
  flow 0 "$msha"
  [ "$(cat "$T/flow.rc")" = 0 ] && [ -f "$T/state2/posted" ] && ! grep -q CARRIED "$T/flow.out"
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   null control: a verdict for the head posts as today"
  else fail=$((fail + 1)); echo "  FAIL null control: a verdict for the head posts as today"; fi
  # MERGE-PR-NO-REPOST: the bus already posted the verdict for this head (verdict/42's tip,
  # the newest `Fix review:` comment by the approver App): nothing is posted again.
  git -C "$mo" branch verdict/42 main
  vtip=$(git -C "$mo" rev-parse verdict/42)
  vcomment() { # <tip named in the comment>
    python3 -I -c 'import json,sys; print(json.dumps({"id": 777000111, "user": {"login": "app[bot]", "id": 55}, "created_at": "2026-11-01T00:00:00Z", "body": "Fix review: merge %s\n\nbus: verdict/42 at %s," % (sys.argv[1], sys.argv[2])}))' "$msha" "$1" > "$T/comments"
  }
  vcomment "$vtip"
  flow 0 "$msha"
  [ "$(cat "$T/flow.rc")" = 0 ] && [ ! -f "$T/state2/posted" ] && grep -qxF "ALREADY POSTED: comment 777000111" "$T/flow.out" \
    && grep -qxF "pr merge 42 --merge --match-head-commit $msha" "$T/gh2.log"
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   a verdict the bus already posted for the head is not posted again, and the merge goes on"
  else fail=$((fail + 1)); echo "  FAIL a verdict the bus already posted for the head is not posted again, and the merge goes on ($(tail -1 "$T/flow.out"))"; fi
  vcomment "$(printf 'f%.0s' {1..40})"
  flow 0 "$msha"
  [ "$(cat "$T/flow.rc")" = 0 ] && [ -f "$T/state2/posted" ] && ! grep -q 'ALREADY POSTED' "$T/flow.out"
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   null control: a posted verdict that is not verdict/42's tip posts as today"
  else fail=$((fail + 1)); echo "  FAIL null control: a posted verdict that is not verdict/42's tip posts as today"; fi
  rm -f "$T/comments"; git -C "$mo" branch -q -D verdict/42
  flow 0 "$(printf 'e%.0s' {1..40})"
  [ "$(cat "$T/flow.rc")" != 0 ] && grep -q "^CARRIED HEAD: #42's verdict reviewed e.*merge_train.py" "$T/flow.out" \
    && [ ! -f "$T/state2/posted" ] && ! grep -q '^pr merge' "$T/gh2.log"
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   a verdict for another head refuses CARRIED HEAD, naming the train, and posts nothing"
  else fail=$((fail + 1)); echo "  FAIL a verdict for another head refuses CARRIED HEAD and posts nothing ($(tail -1 "$T/flow.out"))"; fi
  flow 0
  [ "$(cat "$T/state2/postmerge.argv")" = "42 --repo $R --state-dir $T/state2" ]
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   the merge runs postmerge.py once, for the merged pull request"
  else fail=$((fail + 1)); echo "  FAIL the merge runs postmerge.py for the merged pull request ($(cat "$T/state2/postmerge.argv" 2>&1))"; fi
  FAKE_PM_RC=1 flow 0
  [ "$(cat "$T/flow.rc")" != 0 ] && grep -qxF "OWED record: refused" "$T/flow.out" \
    && [ "$(grep -n '^merged ' "$T/flow.out" | cut -d: -f1)" -lt "$(grep -n '^OWED' "$T/flow.out" | cut -d: -f1)" ]
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   an owed post-merge step prints OWED after the merge line and fails the script"
  else fail=$((fail + 1)); echo "  FAIL an owed post-merge step prints OWED after the merge line and fails the script"; fi
  # P436: a required red the train's classify reads WAIT is waited out, not "RED"; the gate
  # that is still red (RED rc 1) refuses; no red at all never asks classify. The stub answers
  # WAIT (rc 3) twice, then the rc in FAKE_CLS_END.
  printf '#!/bin/bash\nn=$(cat "$T_CLS" 2>/dev/null || echo 0); echo $((n+1)) > "$T_CLS"\n[ "$n" -lt 2 ] && { echo "WAIT x"; exit 3; }\n[ "$FAKE_CLS_END" = 3 ] && { echo "WAIT x"; exit 3; }\n[ "$FAKE_CLS_END" = 0 ] && { echo "GREEN x"; exit 0; }\necho "RED x"; exit 1\n' > "$T/cls.sh"
  clsflow() { # <end rc: 0 green|1 red> <red name or empty>
    rm -f "$T/cls.n"; [ -n "$2" ] && : > "$T/blocked"
    T_CLS=$T/cls.n FAKE_CLS_END=$1 FAKE_RED=$2 HPO_MERGE_CLASSIFY="bash $T/cls.sh" flow 0
  }
  clsflow 0 gate
  [ "$(cat "$T/flow.rc")" = 0 ] && [ "$(cat "$T/cls.n")" = 3 ] && grep -q '^pr merge 42' "$T/gh2.log"
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   a gate red that classify reads WAIT, then GREEN, is waited out and merges"
  else fail=$((fail + 1)); echo "  FAIL a gate red that classify reads WAIT, then GREEN, is waited out and merges ($(tail -1 "$T/flow.out"))"; fi
  clsflow 1 gate
  [ "$(cat "$T/flow.rc")" != 0 ] && grep -q '^RED: gate' "$T/flow.out" && ! grep -q '^pr merge' "$T/gh2.log"
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   null control: a gate red classify reads RED refuses RED and does not merge"
  else fail=$((fail + 1)); echo "  FAIL null control: a gate red classify reads RED refuses RED and does not merge"; fi
  HPO_MERGE_CLASSIFY_POLLS=4 clsflow 3 gate
  [ "$(cat "$T/flow.rc")" = 3 ] && [ "$(cat "$T/cls.n")" = 4 ] && grep -q '^WAIT-EXHAUSTED' "$T/flow.out" \
    && ! grep -q '^RED' "$T/flow.out" && ! grep -q '^pr merge' "$T/gh2.log"
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   a classify that still reads WAIT after the last poll exits 3 WAIT-EXHAUSTED, never RED, and does not merge"
  else fail=$((fail + 1)); echo "  FAIL a classify that still reads WAIT after the last poll exits 3 WAIT-EXHAUSTED, never RED, and does not merge ($(tail -1 "$T/flow.out"))"; fi
  clsflow 1 ""
  [ "$(cat "$T/flow.rc")" = 0 ] && [ ! -f "$T/cls.n" ]
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   null control: no red at the head never asks classify"
  else fail=$((fail + 1)); echo "  FAIL null control: no red at the head never asks classify"; fi
  rm -rf "$T"
  echo "merge_pr self-test: $((pass + fail)) checks, $fail failed"
  [ "$fail" = 0 ]
}
[ "${1:-}" = --self-test ] && { self_test; exit $?; }

PR=$1; S=$2; E=$3; MODE=$4; shift 4
MID=""; READY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --mandate) MID=${2:-}; shift 2 || shift ;;
    --ready) READY=1; shift ;;
    *) break ;;
  esac
done
# For a queue of verdicted PRs, merge_train.py does the same with recarry and the carry check.
D=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/merge_pr; mkdir -p "$D/v"
live=$(gh pr view $PR --json headRefOid --jq .headRefOid); [ "$live" = "$S" ] || { echo "HEAD MOVED: $live"; exit 1; }
gates "$PR" "$MODE" "$MID" "$READY" "$S" || exit 1
[ "$READY_OWED" = 1 ] && { gh pr ready $PR --repo $R >/dev/null || { echo "READY REFUSED for #$PR"; exit 1; }; }
carried_head "$PR" "$S" "$E/VERDICT.md" || exit 1
sed '1s/^# //' "$E/VERDICT.md" > $D/v/verdict-$PR.md; grep -q "$E" $D/v/verdict-$PR.md || printf '\nEvidence: %s/\n' "$(python3 -I tools/audit/seat/ref_privacy.py path "$E")" >> $D/v/verdict-$PR.md
# MERGE-PR-NO-REPOST: a verdict the bus already posted for this head is not posted again -- a
# second comment, left behind by a try that then fails, is no longer verdict/<pr>'s tip text
# and the train's add check refuses the PR. The read is that check's own (`posted-verdict`).
read -r pv_tag pv_head pv_id <<<"$(python3 -I tools/audit/seat/merge_train.py posted-verdict $PR --repo $R 2>/dev/null)"
if [ "$pv_tag" = VERDICT ] && [ "$pv_head" = "$S" ]; then echo "ALREADY POSTED: comment $pv_id"  # mut:repost
else
if test -f tools/audit/app_comment.sh; then bash tools/audit/app_comment.sh $R $PR $D/v/verdict-$PR.md 2>&1; else bash tools/pr/app_comment.sh $R $PR $D/v/verdict-$PR.md 2>&1; fi| tail -1; [ "${PIPESTATUS[0]}" = 0 ] || exit 1
fi
if [ "$MODE" = owner ]; then
  owner_body "$S" "$MID" "$MANDATE_WHY" > $D/approve-$PR.md
  gh pr review $PR --approve --body-file $D/approve-$PR.md || exit 1
else
  if test -f tools/audit/app_approve.sh; then bash tools/audit/app_approve.sh $R $PR $S 2>&1; else bash tools/pr/app_approve.sh $R $PR $S 2>&1; fi| tail -1
fi
sleep 45
unstale_head "$S" || { echo "STALE: a re-run did not clear #$PR's head"; exit 1; }
for i in $(seq 1 60); do n=$(gh api "repos/$R/commits/$S/check-runs?per_page=100" --jq '[.check_runs[] | select(.status!="completed")] | length'); [ "$n" = 0 ] && break; sleep 60; done
red=$(gh api "repos/$R/commits/$S/check-runs?per_page=100" --jq '[.check_runs | group_by(.name)[] | sort_by(.started_at) | last | select(.conclusion=="failure" or .conclusion=="cancelled" or .conclusion=="timed_out") | .name] | join(",")')
if [ -n "$red" ]; then
  # mergeStateStatus already encodes the ruleset's REQUIRED contexts: UNSTABLE/CLEAN =
  # only optional checks fail or are pending (e.g. the non-required CodeQL umbrella on
  # frozen evidence alerts, #1769). Exit only when GitHub itself says BLOCKED/BEHIND/UNKNOWN.
  mss=$(gh pr view $PR --json mergeStateStatus --jq .mergeStateStatus)
  case "$mss" in
    UNSTABLE|CLEAN|HAS_HOOKS) echo "OPTIONAL-RED, proceeding (mergeState=$mss): $red" ;;
    *) # A deferral red is provisional (P436): merge_train.py classify, the one reader of
       # whether a required red is red, answers WAIT while a run it names is unfinished.
       for i in $(seq 1 ${HPO_MERGE_CLASSIFY_POLLS:-20}); do
         cls=$(${HPO_MERGE_CLASSIFY:-python3 -I tools/audit/seat/merge_train.py} classify "$S" --repo $R --pr $PR 2>&1); crc=$?
         [ "$crc" = 3 ] || break
         echo "WAIT: $cls"; sleep 60
       done
       # classify still WAIT after the last poll: the red is provisional, not final. A distinct
       # line and exit 3 (the train's WAIT), never RED, so a caller retries rather than reads a refusal.
       [ "$crc" = 3 ] && { echo "WAIT-EXHAUSTED: classify still reads WAIT after ${HPO_MERGE_CLASSIFY_POLLS:-20} polls; the red is a deferral not yet decided: $red"; exit 3; }
       [ "$crc" = 0 ] || { echo "RED: $red"; exit 1; }
       echo "DEFERRAL RED CLEARED (classify GREEN): $red" ;;
  esac
fi
sleep 10
for j in 1 2 3 4 5 6; do st=$(gh pr view $PR --json mergeStateStatus --jq .mergeStateStatus); [ "$st" != UNKNOWN ] && break; sleep 20; done; echo "state $st"
[ "$st" = CLEAN ] || [ "$st" = HAS_HOOKS ] || [ "$st" = UNSTABLE ] || { echo "not clean"; exit 1; }
gh pr view $PR --json title --jq .title | if test -f tools/audit/preflight.sh; then bash tools/audit/preflight.sh "$@" 2>&1; else bash tools/pr/preflight.sh "$@" 2>&1; fi| tail -1
gh pr merge $PR --merge --match-head-commit $S || exit 1  # mut:merge
sleep 8; echo "merged $(gh pr view $PR --json mergeCommit --jq .mergeCommit.oid)"
for n in "$@"; do echo "issue $n $(gh issue view $n --json state --jq .state)"; done
bash tools/audit/worktree_gc.sh $R 2>&1 | tail -1; git pull -q --ff-only origin main
# The post-merge bookkeeping (standing-merge.md; the record-issue line, the roster stage, the state docs, main's
# suite state): a failure is printed OWED and never undoes the merge, but fails the script.
python3 -I tools/audit/seat/postmerge.py "$PR" --repo $R --state-dir "${HPO_STATE_DIR:-$HOME/.local/state/hpo}"  # mut:postmerge

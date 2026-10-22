#!/bin/bash
# merge_pr.sh <pr> <sha> <evidence-dir> <owner|app> [--mandate <comment-id>] [--ready] [issues-to-verify...]
# merge_pr.sh --self-test
#
# owner mode approves code-owned paths as tvofi's account under the mandate
# comment <comment-id> on #201, read live at this run by budget_raise_gate.py's
# own reading (`_mandate`, `mandate_state` judged now, its scope the gate's
# MANDATE_COVERS_CODE_OWNED). No --mandate, or one not in force now, refuses before anything is
# posted: the script never defaults to a mandate, because a stale one is a
# forged grant (until R10-TRAIN-RAISE-HOLD it hard-coded one that had expired). A budget RAISE is still the gate's to refuse: this
# approval says nothing of the raise justification `budget-raise-gate` reads.
# A draft pull request refuses before anything is posted, unless --ready says
# to mark it ready first.
set -uo pipefail
R=tvofi/heatpump_optimizer
# The self-test grades this script's own tree; a merge runs from the main checkout.
if [ "${1:-}" = --self-test ]; then cd "$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel)" || exit 1
else cd "$(git -C "$(dirname -- "$0")" rev-parse --path-format=absolute --git-common-dir)/.." || exit 1; fi
SELF=$PWD/tools/audit/seat/merge_pr.sh

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
gates() { # <pr> <mode> <mandate-id> <ready 0|1>
  READY_OWED=0
  case "$2" in owner|app) ;; *) echo "USAGE: mode '$2' is neither owner nor app"; return 1 ;; esac
  d=$(gh pr view "$1" --repo $R --json isDraft --jq .isDraft) || { echo "REFUSE: #$1's draft state could not be read"; return 1; }
  if [ "$d" = true ]; then
    [ "$4" = 1 ] || { echo "DRAFT: #$1 is a draft; pass --ready to mark it ready, or ready it first"; return 1; }
    READY_OWED=1
  fi
  [ "$2" = owner ] || return 0
  [[ "$3" =~ ^[0-9]{6,}$ ]] || { echo "MANDATE REQUIRED: owner mode needs --mandate <comment-id> naming the mandate in force on #201 (got '$3')"; return 1; }
  MANDATE_WHY=$(mandate_in_force $R "$3") || { echo "MANDATE $MANDATE_WHY"; return 1; }
  MANDATE_WHY=${MANDATE_WHY#IN FORCE: }
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
  *issues/201/comments*) echo "[[]]" ;;
  *) echo "fake gh: unexpected $*" >&2; exit 1 ;;
esac
G
  chmod +x "$T/gh"
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
  mk -60 60 > "$T/live.json"; mk -120 -10 > "$T/expired.json"
  mk -60 60 code-owned > "$T/code-owned.json"; mk -60 60 budget-raise > "$T/raise.json"
  ck() { # <name> <want rc> <want substring> <draft> <mandate file> -- gates args...
    local name=$1 want=$2 sub=$3 draft=$4 mf=$5 rc; shift 6
    : > "$T/log"
    out=$(PATH="$T:$PATH" FAKE_LOG="$T/log" FAKE_DRAFT=$draft FAKE_MANDATE=$mf gates "$@" 2>&1); rc=$?
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
  ck "a draft refuses without --ready, naming the flag" 1 "DRAFT: #7 is a draft; pass --ready" true "" -- 7 app "" 0
  ck "a draft with --ready passes the gates" 0 "" true "" -- 7 app "" 1
  PATH="$T:$PATH" FAKE_LOG="$T/log" FAKE_DRAFT=true gates 7 app "" 1 >/dev/null
  if [ "$READY_OWED" = 1 ]; then pass=$((pass + 1)); echo "  ok   ... and owes the ready mark"
  else fail=$((fail + 1)); echo "  FAIL ... and owes the ready mark"; fi
  PATH="$T:$PATH" FAKE_LOG="$T/log" FAKE_DRAFT=false gates 7 app "" 1 >/dev/null
  if [ "$READY_OWED" = 0 ]; then pass=$((pass + 1)); echo "  ok   a ready pull request with --ready owes no ready mark"
  else fail=$((fail + 1)); echo "  FAIL a ready pull request with --ready owes no ready mark"; fi
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
  for p in app_comment.sh app_approve.sh preflight.sh worktree_gc.sh; do
    printf '#!/bin/bash\nexit 0\n' > "$mm/tools/audit/$p"; chmod +x "$mm/tools/audit/$p"
  done
  printf 'import sys\nprint(sys.argv[2] if len(sys.argv) > 2 else "")\n' \
    > "$mm/tools/audit/seat/ref_privacy.py"
  printf '#!/bin/bash\nexit 0\n' > "$T/bin2/sleep"; chmod +x "$T/bin2/sleep"
  cat > "$T/bin2/gh" <<'G'
#!/bin/bash
echo "$*" >> "$FAKE_LOG2"
case "$*" in
  *headRefOid*) echo "$FAKE_SHA" ;;
  *isDraft*) echo false ;;
  *mergeStateStatus*) echo CLEAN ;;
  *mergeCommit*) echo deadbeef ;;
  *title*) echo "a title" ;;
  *length*) echo 0 ;;
  *check-runs*) echo "" ;;
  "pr merge "*) [ "$FAKE_MERGE_FAIL" = 1 ] && exit 1; exit 0 ;;
  *) echo "fake gh: unexpected $*" >&2; exit 1 ;;
esac
G
  chmod +x "$T/bin2/gh"
  flow() { # <merge fails 0|1>: the whole script, offline
    : > "$T/gh2.log"
    HPO_STATE_DIR=$T/state2 PATH="$T/bin2:$PATH" FAKE_LOG2=$T/gh2.log FAKE_SHA=$msha \
      FAKE_MERGE_FAIL=$1 bash "$mm/tools/audit/seat/merge_pr.sh" 42 "$msha" "$T/ev" app \
      > "$T/flow.out" 2>&1
    echo $? > "$T/flow.rc"
  }
  flow 0
  [ "$(cat "$T/flow.rc")" = 0 ] \
    && grep -qxF "pr merge 42 --merge --match-head-commit $msha" "$T/gh2.log"
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   null control: the merge records the reviewed head"
  else fail=$((fail + 1)); echo "  FAIL null control: the merge records the reviewed head ($(tail -1 "$T/flow.out"))"; fi
  flow 1
  [ "$(cat "$T/flow.rc")" != 0 ]
  if [ $? = 0 ]; then pass=$((pass + 1)); echo "  ok   a refused merge fails the script (the line's own exit)"
  else fail=$((fail + 1)); echo "  FAIL a refused merge fails the script"; fi
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
gates "$PR" "$MODE" "$MID" "$READY" || exit 1
[ "$READY_OWED" = 1 ] && { gh pr ready $PR --repo $R >/dev/null || { echo "READY REFUSED for #$PR"; exit 1; }; }
sed '1s/^# //' "$E/VERDICT.md" > $D/v/verdict-$PR.md; grep -q "$E" $D/v/verdict-$PR.md || printf '\nEvidence: %s/\n' "$(python3 -I tools/audit/seat/ref_privacy.py path "$E")" >> $D/v/verdict-$PR.md
if test -f tools/audit/app_comment.sh; then bash tools/audit/app_comment.sh $R $PR $D/v/verdict-$PR.md 2>&1; else bash tools/pr/app_comment.sh $R $PR $D/v/verdict-$PR.md 2>&1; fi| tail -1; [ "${PIPESTATUS[0]}" = 0 ] || exit 1
if [ "$MODE" = owner ]; then
  owner_body "$S" "$MID" "$MANDATE_WHY" > $D/approve-$PR.md
  gh pr review $PR --approve --body-file $D/approve-$PR.md || exit 1
else
  if test -f tools/audit/app_approve.sh; then bash tools/audit/app_approve.sh $R $PR $S 2>&1; else bash tools/pr/app_approve.sh $R $PR $S 2>&1; fi| tail -1
fi
sleep 45
for i in $(seq 1 60); do n=$(gh api "repos/$R/commits/$S/check-runs?per_page=100" --jq '[.check_runs[] | select(.status!="completed")] | length'); [ "$n" = 0 ] && break; sleep 60; done
red=$(gh api "repos/$R/commits/$S/check-runs?per_page=100" --jq '[.check_runs | group_by(.name)[] | sort_by(.started_at) | last | select(.conclusion=="failure" or .conclusion=="cancelled" or .conclusion=="timed_out") | .name] | join(",")')
if [ -n "$red" ]; then
  # mergeStateStatus already encodes the ruleset's REQUIRED contexts: UNSTABLE/CLEAN =
  # only optional checks fail or are pending (e.g. the non-required CodeQL umbrella on
  # frozen evidence alerts, #1769). Exit only when GitHub itself says BLOCKED/BEHIND/UNKNOWN.
  mss=$(gh pr view $PR --json mergeStateStatus --jq .mergeStateStatus)
  case "$mss" in
    UNSTABLE|CLEAN|HAS_HOOKS) echo "OPTIONAL-RED, proceeding (mergeState=$mss): $red" ;;
    *) echo "RED: $red"; exit 1 ;;
  esac
fi
sleep 10
for j in 1 2 3 4 5 6; do st=$(gh pr view $PR --json mergeStateStatus --jq .mergeStateStatus); [ "$st" != UNKNOWN ] && break; sleep 20; done; echo "state $st"
[ "$st" = CLEAN ] || [ "$st" = HAS_HOOKS ] || { echo "not clean"; exit 1; }
gh pr view $PR --json title --jq .title | if test -f tools/audit/preflight.sh; then bash tools/audit/preflight.sh "$@" 2>&1; else bash tools/pr/preflight.sh "$@" 2>&1; fi| tail -1
gh pr merge $PR --merge --match-head-commit $S || exit 1  # mut:merge
sleep 8; echo "merged $(gh pr view $PR --json mergeCommit --jq .mergeCommit.oid)"
for n in "$@"; do echo "issue $n $(gh issue view $n --json state --jq .state)"; done
bash tools/audit/worktree_gc.sh $R 2>&1 | tail -1; git pull -q --ff-only origin main

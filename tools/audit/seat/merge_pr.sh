#!/bin/bash
# merge_pr.sh <pr> <sha> <evidence-dir> <owner|app> [--mandate <comment-id>] [issues-to-verify...]
# merge_pr.sh --self-test
# For a queue of verdicted PRs, merge_train.py does the same with recarry and the carry check.
# `owner` approves code-owned paths as tvofi only under the mandate comment
# <comment-id> on #201, read live by budget_raise_gate.py's own reader (`_mandate`,
# `mandate_state`) and in force now for MANDATE_COVERS_CODE_OWNED: no date, scope
# or mandate text lives here. Every refusal runs before the first GitHub write.
set -uo pipefail
R=tvofi/heatpump_optimizer

# The mandate's line when <comment-id> is in force now for a code-owned approval;
# else the gate's own reason and a non-zero exit. Run from the repository root.
mandate_in_force() {
  python3 -I - tools/policy/budget_raise_gate.py "$R" "$1" <<'PY'
import datetime, importlib.util, sys
spec = importlib.util.spec_from_file_location("budget_raise_gate", sys.argv[1])
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
cid, now = int(sys.argv[3]), datetime.datetime.now(datetime.timezone.utc)
try:
    comment, thread = g._mandate(sys.argv[2], cid)
except Exception as e:  # fail closed: an unread mandate grants nothing
    sys.exit(f"mandate {cid} could not be read ({str(e)[:160]})")
ok, why = g.mandate_state(cid, comment, thread, now, now.strftime("%Y-%m-%dT%H:%M:%SZ"), "approval",
                          g.MANDATE_COVERS_CODE_OWNED, "an approval of code-owned paths")
print(why)
sys.exit(0 if ok else 1)
PY
}

self_test() {
  # A throwaway repository holding this script, the real gate (and the move map
  # it imports) and ref_privacy.py,
  # a logging app_comment.sh and a `gh` on PATH that serves fixture mandates and
  # logs every call; `pr review` fails so an arm that reaches the approval stops
  # there instead of waiting on CI.
  local st here n=0 bad=0 rc out
  here=$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel) || return 1
  st=$(mktemp -d) || return 1
  mkdir -p "$st/repo/tools/audit/seat" "$st/repo/tools/policy" "$st/repo/tools/pr" "$st/bin" "$st/ev"
  cp "$0" "$st/repo/tools/audit/seat/merge_pr.sh"
  cp "$here/tools/audit/seat/ref_privacy.py" "$st/repo/tools/audit/seat/"
  mkdir -p "$st/repo/tests"; cp "$here/tests/layout.py" "$here/tests/layout.json" "$st/repo/tests/"  # the gate imports the move map
  cp "$here/tools/policy/budget_raise_gate.py" "$st/repo/tools/policy/"
  printf '#!/bin/bash\necho "WRITE comment $*" >> "$ST/log"\n' > "$st/repo/tools/pr/app_comment.sh"
  git -C "$st/repo" init -q
  cat > "$st/bin/gh" <<'GH'
#!/bin/bash
echo "gh $*" >> "$ST/log"
case "$*" in
  "pr view "*" --json headRefOid --jq .headRefOid") echo "$ST_LIVE" ;;
  "api repos/"*"/issues/comments/"*) test -f "$ST/comment.json" || { echo "gh: Not Found (HTTP 404)" >&2; exit 1; }; cat "$ST/comment.json" ;;
  "api --paginate --slurp repos/"*"/issues/201/comments"*) echo '[[]]' ;;
  "pr review "*) echo "WRITE review" >> "$ST/log"; cp "${@: -1}" "$ST/approve.md"; exit 1 ;;
  *) exit 1 ;;
esac
GH
  chmod +x "$st/bin/gh"
  local H=0123456789abcdef0123456789abcdef01234567 MID=4100000001
  printf '# Fix review: merge %s\n' $H > "$st/ev/VERDICT.md"
  # fixture <scope> <from-min> <until-min>: the mandate comment, built from the
  # gate's own pinned owner and tracking issue
  fixture() {
    python3 -I - "$st/repo" "$1" "$2" "$3" > "$st/comment.json" <<'PY'
import datetime, importlib.util, json, pathlib, sys
root = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("g", root / "tools/policy/budget_raise_gate.py"); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
now = datetime.datetime.now(datetime.timezone.utc)
iso = lambda m: (now + datetime.timedelta(minutes=int(m))).strftime("%Y-%m-%dT%H:%M:%SZ")
print(json.dumps({"id": 4100000001, "created_at": iso(sys.argv[3]), "updated_at": iso(sys.argv[3]),
                  "user": {"login": g.OWNER_LOGIN, "id": g.OWNER_ID, "type": g.OWNER_TYPE},
                  "issue_url": f"https://api.github.com/repos/{g.DEFAULT_REPO}/issues/{g.MANDATE_ISSUE}",
                  "body": f"MANDATE: agents may approve as {g.OWNER_LOGIN}, scope {sys.argv[2]}, "
                          f"from {iso(sys.argv[3])} until {iso(sys.argv[4])}"}))
PY
  }
  # run <live head> <args after the evidence dir...>: rc and output, a fresh log
  run() {
    local live=$1; shift
    : > "$st/log"; rm -f "$st/approve.md"
    out=$(cd "$st" && ST=$st ST_LIVE=$live PATH="$st/bin:$PATH" HPO_STATE_DIR="$st/state" \
          bash "$st/repo/tools/audit/seat/merge_pr.sh" 7 $H "$st/ev" "$@" 2>&1); rc=$?
  }
  check() { n=$((n + 1)); if eval "$2"; then echo "ok   $1"; else bad=$((bad + 1)); echo "FAIL $1 (rc=$rc: $(tail -1 <<<"$out"))"; fi; }
  wrote() { grep -q '^WRITE' "$st/log"; }

  fixture all -120 -1; run $H owner --mandate $MID
  check "an expired mandate refuses" '[ $rc != 0 ] && grep -q "expired" <<<"$out"'
  check "an expired mandate refuses before any GitHub write" '! wrote'
  fixture all -120 60; run $H owner --mandate $MID
  check "null: a mandate in force reaches the approval" 'grep -q "^WRITE review" "$st/log"'
  check "null: the approval cites the mandate by id and quotes its live window" \
    'grep -q "under mandate $MID (scope all, from " "$st/approve.md" && ! grep -q 2026-09-25 "$st/approve.md"'
  check "null: the mandate is read before the verdict comment is written" \
    '[ "$(grep -n "issues/comments/$MID" "$st/log" | head -1 | cut -d: -f1)" -lt "$(grep -n "^WRITE comment" "$st/log" | cut -d: -f1)" ]'
  run $H owner
  check "owner with no --mandate refuses on code-owned paths" '[ $rc != 0 ] && grep -q -- "--mandate" <<<"$out"'
  check "owner with no --mandate refuses before any GitHub write" '! wrote'
  fixture budget-raise -120 60; run $H owner --mandate $MID
  check "a mandate whose scope does not cover code-owned paths refuses" '[ $rc != 0 ] && grep -q "does not cover" <<<"$out" && ! wrote'
  fixture code-owned -120 60; run $H owner --mandate $MID
  check "null: scope code-owned in force reaches the approval" 'grep -q "^WRITE review" "$st/log"'
  rm -f "$st/comment.json"; run $H owner --mandate $MID
  check "a mandate comment that does not exist refuses before any write" '[ $rc != 0 ] && grep -q "not a comment that exists" <<<"$out" && ! wrote'
  fixture all -120 60; run 89abcdef0123456789abcdef0123456789abcdef owner --mandate $MID
  check "a moved head refuses before any write" '[ $rc != 0 ] && grep -q "HEAD MOVED" <<<"$out" && ! wrote'
  rm -rf "$st"
  echo "merge_pr self-test: $n checks, $bad failed"
  [ $bad = 0 ]
}
[ "${1:-}" = --self-test ] && { self_test; exit; }

[ $# -ge 4 ] || { echo "usage: merge_pr.sh <pr> <sha> <evidence-dir> <owner|app> [--mandate <comment-id>] [issues...]"; exit 2; }
PR=$1; S=$2; E=$3; MODE=$4; shift 4; MID=
[ "${1:-}" = --mandate ] && { MID=${2:-}; shift 2 || shift; }
D=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/merge_pr; mkdir -p "$D/v"
cd "$(git -C "$(dirname -- "$0")" rev-parse --path-format=absolute --git-common-dir)/.." || exit 1
# Refusals: nothing below them writes to GitHub until every one has passed.
case "$MODE" in owner|app) ;; *) echo "MODE '$MODE' is neither owner nor app"; exit 2 ;; esac
test -s "$E/VERDICT.md" || { echo "NO VERDICT: $E/VERDICT.md"; exit 1; }
live=$(gh pr view $PR --json headRefOid --jq .headRefOid); [ "$live" = "$S" ] || { echo "HEAD MOVED: $live"; exit 1; }
if [ "$MODE" = owner ]; then
  [[ "$MID" =~ ^[0-9]{6,}$ ]] || { echo "NO MANDATE: owner mode approves code-owned paths only under --mandate <#201 comment id>"; exit 1; }
  mline=$(mandate_in_force "$MID") || { echo "MANDATE NOT IN FORCE: $mline"; exit 1; }
  at=$(date -u +%Y-%m-%dT%H:%MZ)
fi
sed '1s/^# //' "$E/VERDICT.md" > $D/v/verdict-$PR.md; grep -q "$E" $D/v/verdict-$PR.md || printf '\nEvidence: %s/\n' "$(python3 -I tools/audit/seat/ref_privacy.py path "$E")" >> $D/v/verdict-$PR.md
if test -f tools/audit/app_comment.sh; then bash tools/audit/app_comment.sh $R $PR $D/v/verdict-$PR.md 2>&1; else bash tools/pr/app_comment.sh $R $PR $D/v/verdict-$PR.md 2>&1; fi| tail -1; [ "${PIPESTATUS[0]}" = 0 ] || exit 1
if [ "$MODE" = owner ]; then
  cat > $D/approve-$PR.md <<EOT
Owner approval (code-owned paths) at head $S after the "Fix review: merge" verdict, given by the orchestrator under $mline, read in force on #201 at $at.
EOT
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
[ "$(gh pr view $PR --json isDraft --jq .isDraft)" = true ] && gh pr ready $PR >/dev/null
sleep 10
for j in 1 2 3 4 5 6; do st=$(gh pr view $PR --json mergeStateStatus --jq .mergeStateStatus); [ "$st" != UNKNOWN ] && break; sleep 20; done; echo "state $st"
[ "$st" = CLEAN ] || [ "$st" = HAS_HOOKS ] || { echo "not clean"; exit 1; }
gh pr view $PR --json title --jq .title | if test -f tools/audit/preflight.sh; then bash tools/audit/preflight.sh "$@" 2>&1; else bash tools/pr/preflight.sh "$@" 2>&1; fi| tail -1
gh pr merge $PR --merge --match-head-commit $S || exit 1
sleep 8; echo "merged $(gh pr view $PR --json mergeCommit --jq .mergeCommit.oid)"
for n in "$@"; do echo "issue $n $(gh issue view $n --json state --jq .state)"; done
bash tools/audit/worktree_gc.sh $R 2>&1 | tail -1; git pull -q --ff-only origin main

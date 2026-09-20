#!/bin/bash
{ set +x; } 2>/dev/null # before anything: keep the argv-tracing habit even though this tool holds no secret
# Approve the workflow runs GitHub is holding `action_required` on a branch.
#
#   tools/audit/approve_held_runs.sh [--dry-run] <owner/repo> [branch]
#   tools/audit/approve_held_runs.sh --self-test
#
# WHY THIS EXISTS. Since the seats hand their branches to the orchestrator,
# who pushes as the `hpo-author` App (tools/audit/app_push.sh), the
# `pull_request` workflows of that push are created by the pusher -- and a
# workflow run created from GITHUB_TOKEN side a push lands held: GitHub marks
# it `action_required` and waits for a maintainer's approval before it runs.
# Measured tonight on PR #1276: run 35500365827 (`Tests`) sat action_required
# beside green workflow_dispatch equivalents of the same workflows, and its
# held check shadowed the dispatched one in the merge box. This tool lists
# exactly those held runs on one branch and approves each through
# POST /actions/runs/<id>/approve, then reads the branch back.
#
# IT REFUSES, AND APPROVES NOTHING, UNLESS ALL OF THESE HOLD:
#   - the repo argument is owner/repo shaped, and an explicit branch argument
#     is a plain ref name (both checked before any subprocess runs);
#   - `gh` is on PATH and authenticated (`gh auth status` fails closed);
#   - with no branch argument, the checked-out branch of the current git
#     directory has exactly the open pull request this tool reads: its head
#     ref becomes the branch, so a local checkout name is normalised to the
#     pull request's own head ref. No open pull request refuses;
#   - the held-run listing answers with JSON a parser can read -- a failed
#     call or prose refuses before anything is approved (push.sh's
#     "no answer, no push", one action over).
#
# WHAT IT DOES AFTER THOSE PASS: lists the branch's workflow runs with
# status/conclusion action_required, re-verifying each run's own status in
# the parsed listing (the query filters; the read verifies -- a run the
# server returns in another state is reported and skipped, never approved);
# POSTs /actions/runs/<id>/approve for each held run; then re-lists and
# reports approved / still-held / failed with run ids and URLs. Approval is
# not synchronous on GitHub's side, so a run still reading action_required
# on the re-list is reported still-held and re-running the tool is the
# retry; the exit code is 0 only when every targeted run approved.
#
# THE SECRETS, AND THEIR ABSENCE. This tool mints and holds no credential:
# every call rides `gh` as whatever GH_TOKEN the caller set, so a token
# never sits on this script's argv, in its files, or in its output, and
# there is nothing to revoke or clean up on exit.
#
# --dry-run lists what would be approved and touches nothing.
set -uo pipefail

die() { printf 'approve_held_runs: REFUSE: %s\n' "$*" >&2; exit 1; }

# One JSON object per page from `gh api --paginate`, flattened to the runs:
# each page of the runs listing is {"total_count": N, "workflow_runs": [...]}
# rather than a bare list, so the pages are joined on that key. Lines out:
# `HELD <id> <url>` for a run its own JSON holds in action_required, and
# `SKIP <id> <url> status=<s> conclusion=<c>` for one it does not.
RUNS_PY='import sys, json
raw = sys.stdin.read(); dec = json.JSONDecoder(); i = 0; runs = []
while True:
    while i < len(raw) and raw[i].isspace(): i += 1
    if i >= len(raw): break
    v, i = dec.raw_decode(raw, i)
    if isinstance(v, dict): runs.extend(v.get("workflow_runs") or [])
    elif isinstance(v, list): runs.extend(v)
for r in runs:
    st = (r.get("status") or "-"); cc = (r.get("conclusion") or "-")
    if st == "action_required" or cc == "action_required":
        print("HELD %s %s" % (r.get("id"), r.get("html_url")))
    else:
        print("SKIP %s %s status=%s conclusion=%s" % (r.get("id"), r.get("html_url"), st, cc))'

# <repo> <branch, percent-encoded for the query string> -> RUNS_PY lines.
# A failed gh call or an unparseable answer both fail the pipeline, which is
# the refusal: the caller never sees a listing that was not read.
list_runs() {
  gh api --paginate "repos/$1/actions/runs?branch=$2&status=action_required&per_page=100" 2>/dev/null \
    | python3 -c "$RUNS_PY"
}

approve_held() {
  local dry=0
  [ "${1:-}" = "--dry-run" ] && { dry=1; shift; }
  { [ $# -ge 1 ] && [ $# -le 2 ]; } || die "usage: approve_held_runs.sh [--dry-run] <owner/repo> [branch]"
  local repo=$1 branch=${2:-}
  [[ $repo =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die "repo '$repo' is not owner/repo"
  if [ -n "$branch" ]; then
    [[ $branch =~ ^[A-Za-z0-9._][A-Za-z0-9._/-]*$ ]] || die "branch name '$branch' is not a plain ref name"
  fi
  command -v gh >/dev/null 2>&1 || die "no gh on PATH, so no call can be authenticated and NOTHING was approved"
  gh auth status >/dev/null 2>&1 || die "gh is not authenticated (gh auth status); NOTHING was approved"

  if [ -z "$branch" ]; then
    # The default is the OPEN pull request's head branch, read via gh: the
    # checked-out branch names it, and the pull request's own head ref -- not
    # the local name -- is what the runs listing is keyed on.
    local cur owner headq listing
    cur=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) \
      || die "no branch given and this directory is no git checkout, so there is no current pull request to read"
    owner=${repo%/*}
    headq=$(printf '%s:%s' "$owner" "$cur" | sed 's|:|%3A|g; s|/|%2F|g')
    listing=$(gh api "repos/$repo/pulls?head=$headq&state=open" 2>/dev/null) \
      || die "could not ask whether a pull request is open for the checked-out branch '$cur' on $repo; NOTHING was approved"
    branch=$(printf '%s' "$listing" | python3 -c '
import sys, json
try:
    d = json.loads(sys.stdin.read() or "null")
except ValueError:
    d = None
print((d[0]["head"].get("ref") or "") if isinstance(d, list) and d and isinstance(d[0].get("head"), dict) else "")')
    [ -n "$branch" ] \
      || die "no open pull request on $repo for the checked-out branch '$cur', so no head branch to list held runs for; pass the branch explicitly"
  fi

  # The branch rides a query string, so the characters that reshape one are
  # encoded; % first, or the encodings would double-encode themselves.
  local bq; bq=$(printf '%s' "$branch" | sed 's|%|%25|g; s|/|%2F|g; s|&|%26|g; s|#|%23|g')
  local nl=$'\n' lines held="" skipped="" line
  lines=$(list_runs "$repo" "$bq") \
    || die "could not list action_required runs on '$branch' (or the answer was not JSON); NOTHING was approved"
  while IFS= read -r line; do
    case "$line" in
      HELD\ *) held="${held:+$held$nl}${line#HELD }" ;;
      SKIP\ *) skipped="${skipped:+$skipped$nl}${line#SKIP }" ;;
    esac
  done <<<"$lines"

  if [ -z "$held" ]; then
    printf 'approve_held_runs: no action_required runs on %s:%s; nothing to approve\n' "$repo" "$branch"
    if [ -n "$skipped" ]; then
      printf 'approve_held_runs: %s run(s) listed in another state and skipped:\n' "$(printf '%s' "$skipped" | grep -c .)"
      while IFS= read -r line; do printf '  skip   %s\n' "$line"; done <<<"$skipped"
    fi
    exit 0
  fi

  printf 'approve_held_runs: %s action_required run(s) on %s:%s:\n' "$(printf '%s' "$held" | grep -c .)" "$repo" "$branch"
  while IFS= read -r line; do printf '  held   %s\n' "$line"; done <<<"$held"
  if [ -n "$skipped" ]; then
    while IFS= read -r line; do printf '  skip   %s (not action_required; not approved)\n' "$line"; done <<<"$skipped"
  fi

  if [ "$dry" = 1 ]; then
    printf 'approve_held_runs: DRY-RUN: would POST /actions/runs/<id>/approve for the run(s) above; approved nothing\n'
    exit 0
  fi

  # Approve each held run; a refused POST fails that run alone, and the rest
  # are still tried -- one wedged run must not hold its siblings' checks.
  local e id url failed=""
  while IFS= read -r e; do
    [ -n "$e" ] || continue
    id=${e%% *}; url=${e#* }
    if gh api -X POST "repos/$repo/actions/runs/$id/approve" >/dev/null 2>&1; then
      printf 'approve_held_runs: approve POSTed for run %s (%s)\n' "$id" "$url"
    else
      failed="${failed:+$failed$nl}$e"
      printf 'approve_held_runs: FAILED to approve run %s (%s)\n' "$id" "$url" >&2
    fi
  done <<<"$held"

  # Read the branch back and classify: a targeted run is approved only when
  # its POST returned AND the re-list no longer holds it; still-held means
  # approve posted but the run reads action_required again (retry, or another
  # approver is needed); failed means its POST was refused.
  local re still="" approved=""
  re=$(list_runs "$repo" "$bq") \
    || die "the re-list after approving failed; read the runs on $repo:$branch by hand before merging -- the URLs are above"
  while IFS= read -r line; do
    case "$line" in
      HELD\ *) still="${still:+$still$nl}${line#HELD }" ;;
    esac
  done <<<"$re"
  while IFS= read -r e; do
    [ -n "$e" ] || continue
    id=${e%% *}
    if printf '%s\n' "$failed" | grep -qx "$e"; then : # reported as failed below
    elif printf '%s\n' "$still" | grep -qx "$e"; then : # reported as still-held below
    else approved="${approved:+$approved$nl}$e"; fi
  done <<<"$held"

  printf 'approve_held_runs: report on %s:%s -- targeted %s, approved %s, still-held %s, failed %s\n' \
    "$repo" "$branch" \
    "$(printf '%s\n' "$held" | grep -c .)" \
    "$([ -n "$approved" ] && printf '%s\n' "$approved" | grep -c . || echo 0)" \
    "$([ -n "$still" ] && printf '%s\n' "$still" | grep -c . || echo 0)" \
    "$([ -n "$failed" ] && printf '%s\n' "$failed" | grep -c . || echo 0)"
  while IFS= read -r e; do [ -n "$e" ] && printf '  still-held %s\n' "$e"; done <<<"$still"
  while IFS= read -r e; do [ -n "$e" ] && printf '  failed     %s\n' "$e"; done <<<"$failed"

  [ -z "$still$failed" ]
}

if [ "${1:-}" != "--self-test" ]; then
  approve_held "$@"
  exit $?
fi

# ---------------------------------------------------------------------------
# --self-test: `gh`, `git` and `curl` are stubs on PATH; no network, no token.
# The curl stub is a tripwire: this tool must make every call through gh, so
# any curl line in a log is a failure, not a stubbed success. Every refusal
# is paired with the healthy run it must NOT refuse.
SELF="$(cd "$(dirname -- "$0")" && pwd)/$(basename -- "$0")"
W=$(mktemp -d) || exit 2
trap 'rm -rf "$W"' EXIT
mkdir -p "$W/bin"
FAILS=0; N=0
st() { N=$((N + 1)); if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3 (got '$1', want '$2')"; FAILS=$((FAILS + 1)); fi; }
BR=fix/stub-x                                  # a slash: the branch must be encoded
BQ=fix%2Fstub-x                                # its query-string form
LISTQ="api --paginate repos/o/r/actions/runs?branch=$BQ&status=action_required&per_page=100"

cat > "$W/bin/gh" <<'STUB'
#!/bin/bash
printf 'gh %s\n' "$*" >> "$STUB/log"
case "$*" in
  "auth status") [ -f "$STUB/noauth" ] && { echo "gh: You are not logged into any GitHub hosts." >&2; exit 1; }; exit 0 ;;
  "api repos/o/r/pulls?head=o%3Afix%2Fstub-x&state=open")
    [ -f "$STUB/nopr" ] && { printf '[]'; exit 0; }
    printf '[{"number": 7, "head": {"ref": "fix/stub-x"}}]' ;;
  "$LISTQ_STUB")
    n=$(grep -c "^gh api -X POST repos/o/r/actions/runs/[0-9]*/approve$" "$STUB/log")
    if [ "$n" -gt 0 ] && [ -f "$STUB/runs-after.json" ]; then cat "$STUB/runs-after.json"; else cat "$STUB/runs.json"; fi ;;
  "api -X POST repos/o/r/actions/runs/222/approve")
    [ -f "$STUB/refuse-222" ] && { echo "gh: 403 Resource not accessible by integration" >&2; exit 1; }; exit 0 ;;
  "api -X POST repos/o/r/actions/runs/"*"/approve") exit 0 ;;
  *) echo "gh-stub: unexpected call: $*" >&2; exit 9 ;;
esac
STUB
LISTQ_STUB="$LISTQ" export LISTQ_STUB
cat > "$W/bin/git" <<'STUB'
#!/bin/bash
printf 'git %s\n' "$*" >> "$STUB/log"
case "$*" in
  "rev-parse --abbrev-ref HEAD") printf 'fix/stub-x\n' ;;
  *) exit 9 ;;
esac
STUB
cat > "$W/bin/curl" <<'STUB'
#!/bin/bash
printf 'curl %s\n' "$*" >> "$STUB/log"
exit 9   # tripwire: every real call rides gh, so curl is never legitimate here
STUB
chmod +x "$W/bin/gh" "$W/bin/git" "$W/bin/curl"

# The fixtures: 111 and 222 are held, 333 succeeded -- the success-state run
# is the null control for "approve only what its own JSON holds". A page is
# an object with a workflow_runs array, the shape the real endpoint returns.
run_json() { # id status conclusion [id status conclusion...] -> one listing page
  python3 -c 'import sys, json
a = sys.argv[1:]
runs = []
for i in range(0, len(a) - len(a) % 3, 3):
    rid, st, cc = a[i:i + 3]
    runs.append({"id": int(rid), "status": st, "conclusion": None if cc == "null" else cc,
                 "html_url": "https://example.test/runs/%s" % rid})
print(json.dumps({"total_count": len(runs), "workflow_runs": runs}))' "$@"
}
mkcase() { local d="$W/$1"; mkdir -p "$d/tmp"; : > "$d/log"; }
run() { # name args... -> rc; out/err captured in the case dir
  local d="$W/$1"; shift
  ( export STUB="$d" PATH="$W/bin:$PATH" TMPDIR="$d/tmp"
    bash "$SELF" "$@" > "$d/out" 2> "$d/err" )
}
calls() { grep -c "^$2" "$W/$1/log"; }
firstline() { grep -n "$2" "$W/$1/log" | head -1 | cut -d: -f1; }

# The happy path, on the DEFAULT branch: the checked-out branch resolves to
# the open pull request's head ref, both held runs are approved, the re-list
# holds nothing, and the success-state run is skipped untouched.
mkcase ok
run_json 111 action_required null 222 action_required null 333 success success > "$W/ok/runs.json"
printf '{"total_count": 0, "workflow_runs": []}\n' > "$W/ok/runs-after.json"
run ok o/r; st $? 0 "an open pull request's held runs at its head ref are approved (branch defaulted via gh)"
st "$(grep -c "branch=$BQ" "$W/ok/log")" 2 "the branch reached both listings percent-encoded"
st "$(grep -c "branch=$BR" "$W/ok/log")" 0 "and never raw: a slash in a branch name would reshape the query"
l1=$(firstline ok "^gh $LISTQ$"); a1=$(firstline ok '^gh api -X POST repos/o/r/actions/runs/111/approve$')
a2=$(firstline ok '^gh api -X POST repos/o/r/actions/runs/222/approve$')
l2=$(grep -n "^gh $LISTQ$" "$W/ok/log" | sed -n 2p | cut -d: -f1)
if [ -n "$l1" ] && [ -n "$a1" ] && [ -n "$a2" ] && [ -n "$l2" ] \
   && [ "$l1" -lt "$a1" ] && [ "$a1" -lt "$a2" ] && [ "$a2" -lt "$l2" ]; then ORD=ordered; else ORD="list=$l1 appr111=$a1 appr222=$a2 relist=$l2"; fi
st "$ORD" ordered "the loop is list, approve each held run, then re-list"
st "$(calls ok 'gh api -X POST repos/o/r/actions/runs/111/approve')" 1 "exactly one approve POST for run 111"
st "$(calls ok 'gh api -X POST repos/o/r/actions/runs/222/approve')" 1 "and exactly one for run 222"
st "$(calls ok 'gh api -X POST repos/o/r/actions/runs/333/approve')" 0 "and NONE for run 333 (null control: a success-state run is not approved)"
st "$(grep -c 'skip   333 https://example.test/runs/333 status=success' "$W/ok/out")" 1 "the success-state run is reported skipped, with its own status"
st "$(grep -c 'report on o/r:fix/stub-x -- targeted 2, approved 2, still-held 0, failed 0' "$W/ok/out")" 1 "the report counts every category"
st "$(grep -c 'approve POSTed for run 111 (https://example.test/runs/111)' "$W/ok/out")" 1 "and each approved run is named with its id and URL"
st "$(grep -c 'approve POSTed for run 222 (https://example.test/runs/222)' "$W/ok/out")" 1 "both of them"
st "$(calls ok 'curl')" 0 "no raw curl call: every request rides gh, so no credential can reach this script's argv"
st "$(grep -c -e 'ghs_' -e 'Bearer ' -e 'Authorization' "$W/ok/log")" 0 "and no credential text on any stubbed command line"

# A run whose approve POSTed but which still reads action_required on the
# re-list: reported still-held, exit non-zero -- the merge box is not clear.
mkcase stillheld
run_json 111 action_required null 222 action_required null > "$W/stillheld/runs.json"
run_json 111 action_required null > "$W/stillheld/runs-after.json"
run stillheld o/r "$BR"; st $? 1 "a run still held on the re-list fails the tool"
st "$(grep -c 'report on o/r:fix/stub-x -- targeted 2, approved 1, still-held 1, failed 0' "$W/stillheld/out")" 1 "counted as still-held, not approved"
st "$(grep -c 'still-held 111 https://example.test/runs/111' "$W/stillheld/out")" 1 "named with its id and URL"
st "$(grep -c 'report on o/r:fix/stub-x -- targeted 2, approved 1' "$W/stillheld/out")" 1 "while its sibling, no longer held, is approved"

# A refused POST fails that run alone; the sibling is still approved.
mkcase approvfail
run_json 111 action_required null 222 action_required null > "$W/approvfail/runs.json"
printf '{"total_count": 0, "workflow_runs": []}\n' > "$W/approvfail/runs-after.json"
: > "$W/approvfail/refuse-222"
run approvfail o/r "$BR"; st $? 1 "a refused approve POST fails the tool"
st "$(grep -c 'FAILED to approve run 222 (https://example.test/runs/222)' "$W/approvfail/err")" 1 "naming the failed run and its URL"
st "$(grep -c 'failed     222 https://example.test/runs/222' "$W/approvfail/out")" 1 "reported under failed"
st "$(grep -c 'report on o/r:fix/stub-x -- targeted 2, approved 1, still-held 0, failed 1' "$W/approvfail/out")" 1 "with the rest of the report honest"

# Refusals, each approving nothing.
mkcase noauth; : > "$W/noauth/noauth"
run noauth o/r "$BR"; st $? 1 "REFUSE: gh is unauthenticated"
st "$(grep -c 'gh is not authenticated' "$W/noauth/err")" 1 "saying so"
st "$(calls noauth 'gh api -X POST')" 0 "and approving nothing"
st "$(calls noauth 'gh auth status')" 1 "having asked gh before anything else"

mkcase badrepo
run badrepo not-a-repo; st $? 1 "REFUSE: a repo argument without owner/repo shape"
st "$(wc -l < "$W/badrepo/log" | tr -d ' ')" 0 "before any gh, git or curl call"
mkcase badbranch
run badbranch o/r 'bad branch'; st $? 1 "REFUSE: a branch argument that is not a plain ref name"
st "$(wc -l < "$W/badbranch/log" | tr -d ' ')" 0 "before any gh, git or curl call"
mkcase usage
run usage; st $? 1 "REFUSE: no arguments at all is a usage error"
st "$(grep -c 'usage: approve_held_runs.sh' "$W/usage/err")" 1 "with the usage line"

mkcase nopr; : > "$W/nopr/nopr"
run nopr o/r; st $? 1 "REFUSE: no open pull request on the checked-out branch"
st "$(grep -c 'no open pull request on o/r' "$W/nopr/err")" 1 "naming the repo and the checkout's branch"
st "$(calls nopr 'gh api -X POST')" 0 "and approving nothing"

mkcase none
printf '{"total_count": 0, "workflow_runs": []}\n' > "$W/none/runs.json"
run none o/r "$BR"; st $? 0 "a branch with nothing held succeeds approving nothing"
st "$(grep -c '^approve_held_runs: no action_required runs on o/r:fix/stub-x; nothing to approve$' "$W/none/out")" 1 "saying there was nothing to do"

# --dry-run: lists, approves nothing.
mkcase dry
run_json 111 action_required null 333 success success > "$W/dry/runs.json"
run dry --dry-run o/r "$BR"; st $? 0 "--dry-run lists the held run and succeeds"
st "$(calls dry 'gh api -X POST')" 0 "and POSTs no approve at all"
st "$(grep -c "^gh $LISTQ$" "$W/dry/log")" 1 "having listed exactly once"
st "$(grep -c 'held   111 https://example.test/runs/111' "$W/dry/out")" 1 "naming the run it would approve"
st "$(grep -c '^approve_held_runs: DRY-RUN: would POST' "$W/dry/out")" 1 "and saying it approved nothing"

echo "approve_held_runs self-test: $N checks, $FAILS failed"
[ "$FAILS" -eq 0 ]

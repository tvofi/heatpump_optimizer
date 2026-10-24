#!/bin/bash
# failure_logs.sh <pr-number> [out-dir]: why the newest red at this PR's live
# head is red, read from the failing jobs' logs — the chain every round-9
# session hand-rolled a dozen times.
#
#   latest failing check-runs at the head -> each one's details_url ->
#   the workflow job it backs -> the job's log -> the error lines.
#
# Writes per-check log files and a HEAD.txt under <out-dir>
# (default ${HPO_STATE_DIR:-$HOME/.local/state/hpo}/failure-logs/<pr>, the
# documented state root — an instrument's evidence does not live under /tmp,
# the 2026-10-03 cleanup ruling tmp_paths.py encodes) and prints one line per
# failing check: name, check-run id, job id (or NO-JOB), log path (or NO-LOG),
# then the grepped error lines. Needs `gh` and `jq`.
#
#   bash failure_logs.sh 2188
#   bash failure_logs.sh --self-test
#
# WHAT IT READS, AND WHAT IT REFUSES TO GUESS:
#   * check-runs are grouped by name, latest `started_at` wins — a red run
#     behind a newer green one of the same name is not the failure to read
#     (`gh pr checks` hides a red-then-green; the API is the authority);
#   * a check-run whose details_url is not an Actions job URL (a ruleset or
#     an App check) prints NO-JOB: there is no log to read, and inventing one
#     is the fabricated-evidence class;
#   * a log GitHub no longer serves prints NO-LOG, exits 1, and is counted,
#     never read as a status — the closing count is over the logs it could
#     read and says how many it could not;
#   * error lines are the job's own markers: `##[error]`, `ERROR:`, `FAILED`,
#     `Process completed with exit code`; if none match, the log's last 3
#     lines, prefixed `tail:` — a grep written from one failure's shape finds
#     nothing in the next one's, and a silent zero is worse than a tail.
#
# Paced for the shared API quota (owner, 2026-10-07): one call a second
# (FAILURE_LOGS_PACE overrides, whole seconds). Scope: exactly the head the PR
# names when this run started; every log file's name carries the job id, so a
# re-run at a new head never presents an old head's log as this one's.
set -uo pipefail
R=${FAILURE_LOGS_REPO:-tvofi/heatpump_optimizer}
PACE=${FAILURE_LOGS_PACE:-1}
api() { sleep "$PACE"; gh api "$@"; }

self_test() {
  passed=0; failed=0
  ck() { local name=$1; shift
         if "$@" >/dev/null 2>&1; then passed=$((passed + 1)); printf '  ok   %s\n' "$name"
         else failed=$((failed + 1)); printf '  FAIL %s\n' "$name"; fi; }
  TMP=$(mktemp -d) || exit 1
  trap 'rm -rf "$TMP"' EXIT
  mkdir -p "$TMP/bin" "$TMP/out"
  FIX=$TMP/fix; mkdir -p "$FIX"; export FIX   # the fake gh child reads it
  HEAD=903283a394560d6cb516481debdde2dcf47c6ade
  printf '%s\n' "$HEAD" > "$FIX/head"
  # Four check-runs, two of them the same name: the newest run of `closures`
  # is the failure; the 08:00 green must not be read. delivery-status is a
  # non-Actions check (NO-JOB). mutation's log fetch fails (NO-LOG).
  cat > "$FIX/cr.json" <<'EOF'
{"total_count":4,"check_runs":[
 {"name":"closures","status":"completed","conclusion":"failure",
  "started_at":"2026-10-14T09:00:00Z","id":111,
  "details_url":"https://github.com/o/r/actions/runs/700/job/900"},
 {"name":"closures","status":"completed","conclusion":"success",
  "started_at":"2026-10-14T08:00:00Z","id":112,
  "details_url":"https://github.com/o/r/actions/runs/701/job/901"},
 {"name":"delivery-status","status":"completed","conclusion":"failure",
  "started_at":"2026-10-14T09:00:00Z","id":113,
  "details_url":"https://github.com/o/r/check-runs/113"},
 {"name":"mutation","status":"completed","conclusion":"timed_out",
  "started_at":"2026-10-14T09:00:00Z","id":114,
  "details_url":"https://github.com/o/r/actions/runs/702/job/902"}
]}
EOF
  printf '##[error]Process completed with exit code 1.\nsome noise line\n' > "$FIX/log-900"
  printf 'green-run log: must never be read\n' > "$FIX/log-901"
  # The 902 job's log fetch fails like an expired log: the NO-LOG arm is
  # graded on a real shape, not a fixture of the report text.
  cat > "$TMP/bin/gh" <<'FAKE'
#!/bin/bash
prev=""; prog=""
for x in "$@"; do [ "$prev" = "--jq" ] && prog="$x"; prev="$x"; done
a="$*"
case "$a" in
  *"pr view"*)  cat "$FIX/head" ;;
  *"/check-runs"*) jq -r "$prog" "$FIX/cr.json" 2>/dev/null || cat "$FIX/cr.json" ;;
  *"/jobs/900/logs"*) cat "$FIX/log-900" ;;
  *"/jobs/902/logs"*) exit 1 ;;
  *) exit 0 ;;
esac
FAKE
  chmod +x "$TMP/bin/gh"
  PATH="$TMP/bin:$PATH" FAILURE_LOGS_PACE=0 bash "$0" 2188 "$TMP/out" \
    > "$TMP/stdout.tsv" 2>&1
  rc=$?
  ck "partial read reports itself (exit 1, one log unread)" [ "$rc" = 1 ]
  newest_ok=1
  [ -f "$TMP/out/closures-900.log" ] || newest_ok=0
  [ -f "$TMP/out/closures-901.log" ] && newest_ok=0
  grep -q 'must never be read' "$TMP/out"/*.log 2>/dev/null && newest_ok=0
  ck "red-then-green grouped to the newest: job 900 read, 901 never fetched" \
    [ "$newest_ok" = 1 ]
  ck "non-Actions check prints NO-JOB" grep -q 'NO-JOB' "$TMP/stdout.tsv"
  ck "unreadable log prints NO-LOG" grep -q 'NO-LOG' "$TMP/stdout.tsv"
  ck "error lines from the real log land in the report" \
    grep -q '##\[error\]Process completed' "$TMP/stdout.tsv"
  ck "count is over readable logs beside the unread one" \
    grep -q 'logs read: 1 of 2' "$TMP/stdout.tsv"
  ck "report names the head it read at" grep -q "$HEAD" "$TMP/stdout.tsv"
  printf 'passed=%d failed=%d\n' "$passed" "$failed"
  [ "$failed" = 0 ]
}

[ "${1:-}" = "--self-test" ] && { self_test; exit $?; }

PR=${1:?usage: failure_logs.sh <pr-number> [out-dir]}
OUT=${2:-${FAILURE_LOGS_STATE:-${HPO_STATE_DIR:-$HOME/.local/state/hpo}/failure-logs}/$PR}
HEAD=$(gh pr view "$PR" --repo "$R" --json headRefOid --jq .headRefOid 2>/dev/null) || exit 2
[ -n "$HEAD" ] || { echo "REFUSE: no live head for #$PR"; exit 2; }
mkdir -p "$OUT"
echo -e "pr\t$PR\nhead\t$HEAD" > "$OUT/HEAD.txt"
echo "head $HEAD"

# Latest per name, completed-failure only, newest started_at wins.
api "repos/$R/commits/$HEAD/check-runs?per_page=100" --jq '
  [.check_runs[] | select(.status == "completed")
   | select((.conclusion // "") != "" and
            (.conclusion == "failure" or .conclusion == "timed_out" or
             .conclusion == "startup_failure"))]
  | group_by(.name) | map(sort_by(.started_at) | last) |
  .[] | [.name, (.conclusion // ""), .id, (.details_url // "")] | @tsv' \
  > "$OUT/failing.tsv" || { echo "REFUSE: check-runs read failed"; exit 2; }

read_total=0; job_total=0; nojob=0
while IFS=$'\t' read -r name concl crid url; do
  [ -n "$name" ] || continue
  jid=""; case $url in
    */actions/runs/*/job/*) jid=${url##*/job/} ;;
  esac
  if [ -z "$jid" ]; then
    nojob=$((nojob + 1))
    printf '%s\t%s\t%s\tNO-JOB\t(no Actions job behind this check)\n' \
      "$name" "$crid" "$concl"
    continue
  fi
  job_total=$((job_total + 1))
  safe=$(printf '%s' "$name" | tr -c 'A-Za-z0-9._-' '-')
  f="$OUT/$safe-$jid.log"
  if [ ! -s "$f" ]; then
    api --allow-escape-sequences "repos/$R/actions/jobs/$jid/logs" > "$f" 2>/dev/null \
      || { rm -f "$f"; printf '%s\t%s\t%s\tNO-LOG\tjob %s (log not served)\n' \
             "$name" "$crid" "$concl" "$jid"; continue; }
  fi
  read_total=$((read_total + 1))
  lines=$(grep -nE '##\[error\]|^ERROR:|^FAILED|Process completed with exit code' "$f" \
          | head -20)
  [ -n "$lines" ] || lines=$(tail -3 "$f" | sed 's/^/tail: /')
  printf '%s\t%s\t%s\t%s\n' "$name" "$crid" "$jid" "$f"
  printf '%s\n' "$lines" | sed 's/^/    /'
done < "$OUT/failing.tsv"
echo "failing checks: $job_total (+$nojob without a job to read); " \
     "logs read: $read_total of $job_total (head $HEAD)"
[ "$read_total" = "$job_total" ] || exit 1   # a log GitHub would not serve:
exit 0                                       # the caller must know it is
                                             # reading a partial report.

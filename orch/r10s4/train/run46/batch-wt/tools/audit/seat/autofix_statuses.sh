#!/bin/bash
# autofix_statuses.sh <out-dir> [pages]: what the two repairing autofix jobs
# actually answered, re-derived from their job logs (R9-CI-1).
#
# For the newest <pages> x 100 pull_request runs of tests.yml (default 3), it
# lists every mutation-autofix and closures-autofix job that ran, reads the
# `AUTOFIX: <status>` line from each job's log, and, for a closures-autofix
# skip, names the failure heading the same run's `closures` job printed
# (UNDER-SCOPED, INERT READS UNDER-APPROXIMATED, PHANTOM, NOT A FILE). It
# prints the status counts, then the API failures beside them: a log GitHub
# no longer serves (they expire) is counted, never read as a status, so a
# count is over the logs it could read and says how many it could not.
#
# Paced for the shared API quota (owner, 2026-10-07): one call a second at
# most, and each run's job list is fetched once and cached under jobs/.
# Writes <out-dir>/runs.tsv, jobs.tsv, status.tsv, jobs/ and logs/. Needs `gh`.
set -uo pipefail
OUT=${1:?usage: autofix_statuses.sh <out-dir> [pages]}
PAGES=${2:-3}
R=tvofi/heatpump_optimizer
api() { sleep 1; gh api "$@"; }
mkdir -p "$OUT/logs" "$OUT/jobs"
cd "$OUT" || exit 2
: > runs.tsv
rf=0
# Not `seq 1 "$PAGES"`: BSD seq counts DOWN from 1 when PAGES is 0.
case $PAGES in ''|*[!0-9]*) echo "pages must be a whole number" >&2; exit 2 ;; esac
for ((p = 1; p <= PAGES; p++)); do
  api -X GET "repos/$R/actions/workflows/tests.yml/runs" -f event=pull_request \
    -f per_page=100 -f page="$p" \
    --jq '.workflow_runs[] | [.id, .head_branch, .head_sha[0:10]] | @tsv' >> runs.tsv \
    || rf=$((rf + 1))
done
jf=0
: > jobs.tsv
while IFS=$'\t' read -r run br sha; do
  j=jobs/$run.json
  [ -s "$j" ] || api "repos/$R/actions/runs/$run/jobs?per_page=100" > "$j" \
    || { jf=$((jf + 1)); rm -f "$j"; continue; }
  out=$(jq -r '.jobs[]
      | select(.name == "mutation-autofix" or .name == "closures-autofix")
      | select(.conclusion != "skipped" and .conclusion != null)
      | [.id, .name, .conclusion] | @tsv' "$j")
  [ -n "$out" ] && printf '%s\n' "$out" \
    | awk -v r="$run" -v b="$br" -v s="$sha" -F'\t' '{print r"\t"b"\t"s"\t"$0}' >> jobs.tsv
done < runs.tsv
lf=0
: > status.tsv
while IFS=$'\t' read -r run br sha jid name concl; do
  f=logs/$jid.log
  [ -s "$f" ] || api --allow-escape-sequences "repos/$R/actions/jobs/$jid/logs" > "$f" 2>/dev/null \
    || { lf=$((lf + 1)); rm -f "$f"; continue; }
  st=$(grep -m1 -oE 'AUTOFIX: [a-z-]+' "$f" | cut -d' ' -f2)
  why=-
  if [ "$name" = closures-autofix ] && [ "${st:-}" != changed ]; then
    cj=$(jq -r '.jobs[] | select(.name == "closures") | .id' "jobs/$run.json")
    c=logs/closures-$cj.log
    if [ -n "$cj" ] && { [ -s "$c" ] || api --allow-escape-sequences \
        "repos/$R/actions/jobs/$cj/logs" > "$c" 2>/dev/null; }; then
      why=$(grep -oE '(UNDER-SCOPED|INERT READS UNDER-APPROXIMATED|PHANTOM|NOT A FILE):' "$c" \
        | sort -u | tr -d ':' | paste -sd, -)
    else
      lf=$((lf + 1)); rm -f "$c"; why=log-unavailable
    fi
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$run" "$br" "$sha" "$jid" "$name" \
    "$concl" "${st:-<none>}" "${why:--}" >> status.tsv
done < jobs.tsv
echo "runs listed: $(wc -l < runs.tsv | tr -d ' ') (page failures: $rf)"
echo "autofix jobs that ran: $(wc -l < jobs.tsv | tr -d ' ') (job-list failures: $jf)"
echo "statuses read: $(wc -l < status.tsv | tr -d ' ') (log failures: $lf)"
cut -f5,7,8 status.tsv | sort | uniq -c | sort -rn

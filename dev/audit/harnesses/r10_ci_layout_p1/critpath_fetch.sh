#!/bin/sh
# Read-only GETs for critpath.py: RAW gets the two newest pages of completed
# pull_request runs of tests.yml, each run's latest jobs, and CASES one line per
# run whose four lanes concluded: run id, closure-scope job id, and the CASE
# word of that job's log ("CASE: SCOPED -- ..." / "CASE: FULL -- ...").
#   sh dev/audit/harnesses/r10_ci_layout_p1/critpath_fetch.sh RAW CASES
# A seat whose proxy refuses the log host reads the same line through any
# other log reader; the CASES format is the contract.
set -u
D=$1; C=$2; R=repos/tvofi/heatpump_optimizer
mkdir -p "$D"; : > "$C"
for p in 1 2; do
  gh api "$R/actions/workflows/tests.yml/runs?event=pull_request&status=completed&per_page=100&page=$p" \
    > "$D/tests_runs_pull_request_p$p.json" || exit 2
done
python3 -I - "$D" <<'PY' > "$D/ids.txt"
import json, sys
from pathlib import Path
for f in sorted(Path(sys.argv[1]).glob("tests_runs_pull_request_p*.json")):
    for r in json.loads(f.read_text())["workflow_runs"]:
        print(r["id"])
PY
while read -r id; do
  gh api "$R/actions/runs/$id/jobs?filter=latest&per_page=100" > "$D/tests_jobs_$id.json" || continue
  jid=$(python3 -I - "$D/tests_jobs_$id.json" <<'PY'
import json, sys
J = {j["name"]: j for j in json.load(open(sys.argv[1]))["jobs"]}
need = ("closure-scope", "coverage", "closures", "fast (3.14)")
ok = all(n in J and J[n]["conclusion"] in ("success", "failure") for n in need)
print(J["closure-scope"]["id"] if ok else "")
PY
)
  [ -n "$jid" ] || continue
  case_word=$(gh api "$R/actions/jobs/$jid/logs" 2>/dev/null | grep -o -E 'CASE: [A-Z]+' | head -1 | cut -d' ' -f2)
  printf '%s\t%s\t%s\n' "$id" "$jid" "${case_word:-UNKNOWN}" >> "$C"
done < "$D/ids.txt"

"""Same-head duplicate code runs: a dispatch AND a pull_request run of one workflow.

    python3 -I measure/dupes.py measure/raw > measure/dupes.txt

raw/runsat_<sha>.json (fetch2.sh). For each head and each code workflow (Tests,
CodeQL, Hassfest, Validate, Governance), counts runs by event and conclusion; a head
with both a workflow_dispatch and a pull_request run that executed (not skipped,
not action_required) ran that workflow's code twice for one tree. Runner time is
not in the run object; the Tests figure is priced from phase 1's medians.
"""
import json, sys
from collections import defaultdict
from pathlib import Path
CODE = ("Tests", "CodeQL", "Hassfest", "Validate", "Governance")
raw = Path(sys.argv[1]); dup = defaultdict(int); heads = 0; held = 0
for f in sorted(raw.glob("runsat_*.json")):
    heads += 1
    by = defaultdict(lambda: defaultdict(list))
    for r in json.loads(f.read_text())["workflow_runs"]:
        by[r["name"]][r["event"]].append(r["conclusion"] or r["status"])
        held += (r["conclusion"] == "action_required")
    line = []
    for w in CODE:
        e = by.get(w, {})
        if e.get("workflow_dispatch") and [c for c in e.get("pull_request", []) if c not in ("skipped", "action_required")]:
            dup[w] += 1; line.append(f"{w} pr={e['pull_request']} dispatch={e['workflow_dispatch']}")
    if line: print(f"{f.stem[7:17]}: " + "; ".join(line))
print(f"\nheads {heads}; heads where a workflow's code ran twice (dispatch + pull_request): {dict(dup)}; action_required runs seen: {held}")

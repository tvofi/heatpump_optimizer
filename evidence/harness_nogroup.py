# Harness (reviewer-built): postmerge for a merged PR resolving to no roster group, sync rc 0.
import sys, tempfile
from pathlib import Path
seat = Path(sys.argv[1]) / "tools/audit/seat"
sys.path.insert(0, str(seat))
import postmerge as pm, record_beat as rb
rc_sync = int(sys.argv[2]) if len(sys.argv) > 2 else 0
rb.facts = lambda pr, repo, run=None: {"sha": "a"*40, "branch": "chore/x", "issues": [], "body": ""}
rb.record = lambda *a, **k: None
calls = []
def run(argv):
    calls.append(argv)
    if any("roster_sync.py" in x for x in argv): return rc_sync, "synced"
    if any("merge_train.py" in x for x in argv): return 0, "GREEN"
    return 0, ""
out = []
with tempfile.TemporaryDirectory() as td:
    code = pm.postmerge(9, "o/r", Path(td), False, False, run, out.append, {"groups": [{"group": "R10-X", "carry": []}]})
print("rc", code); print("\n".join(out))
print("ledger-open", any("ledger.py" in " ".join(c) and "open" in c for c in calls))

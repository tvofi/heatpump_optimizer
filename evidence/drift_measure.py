"""Reviewer's own drift measurement (rev-3806-r4): run selftest_scope.drift
from the checked-out tree (cwd) over each table given, against a CI
selftest-closures artifact used as the measured read set.
usage: python3 -I drift_measure.py <artifact.json> <label=table.json>..."""
import json, sys
from pathlib import Path
root = Path.cwd()
sys.path.insert(0, str(root / "tools/ci"))
import selftest_scope as s
art = s.parse_table(Path(sys.argv[1]).read_text())
steps = s.workflow_steps(root)
print(f"tree gated steps: {len(s.gated_ids(steps))}; artifact steps: {len(art['steps'])}")
for spec in sys.argv[2:]:
    label, tp = spec.split("=", 1)
    table = s.load_table(Path(tp))
    r, notes = s.drift(table, art["steps"], steps)
    print(f"{label}: {len(r)} refusal(s), {len(notes)} note(s)")
    for x in r:
        print("   ", x[:400])

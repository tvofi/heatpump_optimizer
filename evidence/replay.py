import json, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve(); art = json.loads(Path(sys.argv[2]).read_text())
sys.path.insert(0, str(root / "tools/ci"))
import selftest_scope as s
steps = s.workflow_steps(root)
table = s.load_table(root / s.TABLE) if len(sys.argv) < 4 else s.load_table(Path(sys.argv[3]))
refuse, notes = s.drift(table, art["steps"], steps)
for l in refuse: print("  " + l)
print(f"replay: {len(s.gated_ids(steps))} gated step(s), {len(refuse)} refusal(s), {len(notes)} note(s)")

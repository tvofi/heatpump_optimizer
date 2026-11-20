import json, sys
sys.path.insert(0, "tools/ci")
from pathlib import Path
import selftest_scope as s
art = json.load(open(sys.argv[1]))
steps = s.workflow_steps(Path("."))
for label, tpath in (("head", "tools/ci/selftest_closures.json"),("main","../main_table.json")):
    table = s.load_table(Path(tpath))
    r, _ = s.drift(table, art["steps"], steps)
    print(label, len(r), "refusal(s)")
    for x in r: print("  ", x[:300])

import json, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve(); out = Path(sys.argv[2])
sys.path.insert(0, str(root / "tools/ci"))
import selftest_scope as s
table = s.load_table(root / s.TABLE)
for a in sys.argv[3:]:
    table = {"steps": s.union_entries(table, json.loads(Path(a).read_text())["steps"])}
s.write_table(out, table["steps"], root)

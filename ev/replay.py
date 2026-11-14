import json,sys
from pathlib import Path
root=Path(sys.argv[1]); sys.path.insert(0,str(root/"tools/ci"))
import selftest_scope as s
table=json.load(open(sys.argv[2])); art=json.load(open(sys.argv[3]))
steps=s.workflow_steps(root)
r,n=s.drift(table,art["steps"],steps)
for l in r: print("  ",l)
for l in n: print("   note:",l)
print(f"RESULT replay root={sys.argv[4]} table={sys.argv[5]}: {len(s.gated_ids(steps))} gated, {len(r)} refusal(s), {len(n)} note(s)")

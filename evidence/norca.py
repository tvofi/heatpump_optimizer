# Owing groups (escape or hotfix) at the reader ref whose `rca` list is empty: caused_by can never be admitted for them.
import sys, json
sys.path.insert(0, "tools/audit/seat")
import roster_lib, loop_ledger
ros, _ = loop_ledger.load_ref(".", roster_lib.reader_ref(".", None))
for n, p, ro in ros:
    gs = list(roster_lib.groups_of(ro).values())
    owe = [g for g in gs if "caused_by" in loop_ledger.owed(g)]
    no = [g["group"] for g in owe if not g.get("rca")]
    print(f"round {n}: groups owing caused_by {len(owe)}, of which with no rca record {len(no)}: {no[:6]}")
print("-- escapes only (injected's owing set)")
for n, p, ro in ros:
    esc = [g for g in roster_lib.groups_of(ro).values() if loop_ledger.is_escape(g)]
    print(f"round {n}: escapes {len(esc)}, with no rca record {sum(not g.get('rca') for g in esc)}")

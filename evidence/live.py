import sys, json, copy
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import roster_edit as R
for label, p in (("origin/main", sys.argv[2]), ("handoff/audit-r10-roster", sys.argv[3])):
    raw = open(p, encoding="utf-8").read()
    ro = json.loads(raw)
    gs = ro["groups"]
    ne = sum(1 for g in gs if g.get("carry")); em = sum(1 for g in gs if "carry" in g and g["carry"] == []); kl = [g["group"] for g in gs if "carry" not in g]
    print(f"RESULT live={label} groups={len(gs)} nonempty={ne} empty={em} keyless={len(kl)} {kl} dump_roundtrip={R.dump(ro)==raw}")
    refused = changed = 0
    for g in gs:
        r2 = copy.deepcopy(ro)
        spec = ",".join(g.get("after") or []) or "-"
        try:
            R.op_set_after(r2, g["group"], spec)
            if R.dump(r2) != raw: changed += 1
        except R.Refuse as e:
            refused += 1; print("  refused", g["group"], e)
    print(f"RESULT live={label} set-after-own-edges refused={refused} byte_changes={changed}")
    diff = []
    for g in gs:
        r2 = copy.deepcopy(ro)
        R.op_append_carry(r2, g["group"], "probe round-trip xyzzy")
        R.op_drop_carry(r2, g["group"], match="probe round-trip xyzzy")
        if R.dump(r2) != raw: diff.append(g["group"])
    print(f"RESULT live={label} append+drop byte_changes={len(diff)} {diff}")
    # cycle probe on a real edge
    for g in gs:
        if g.get("after"):
            a = g["after"][0]; r2 = copy.deepcopy(ro)
            try: R.op_set_after(r2, a, g["group"]); print("  NOT refused cycle", a, g["group"])
            except R.Refuse as e: print(f"RESULT live={label} cycle-probe refused: {e}")
            break

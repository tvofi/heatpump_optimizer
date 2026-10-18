import sys, json, glob, copy
sys.path.insert(0,"tools/audit/seat"); sys.path.insert(0,"tests")
import roster_edit as R
for f in sorted(glob.glob("dev/programme/rosters/wave-r*-groups.json")):
    raw=open(f,encoding="utf-8").read(); base=json.loads(raw)
    print(f"RESULT {f}: dump(load) byte-identical={R.dump(base)==raw}")
    for fld in ("issues","fixes"):
        same=diff=0; ex=[]
        for g in base["groups"]:
            r=copy.deepcopy(base)
            R.op_wire_issue(r,g["group"],"999999",fld); R.op_unwire_issue(r,g["group"],"999999",fld)
            if R.dump(r)==raw: same+=1
            else:
                diff+=1; ex.append((g["group"], g.get(fld)))
        print(f"RESULT {f} wire+unwire --field {fld}: identical={same} changed={diff} examples={ex[:3]}")

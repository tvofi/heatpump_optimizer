import json, subprocess, sys, collections
def load(ref):
    return json.loads(subprocess.check_output(["git","show",f"{ref}:dev/programme/rosters/wave-r10-groups.json"]))
a, b = load(sys.argv[1]), load(sys.argv[2])
ga = {g["group"]: g for g in a["groups"]}; gb = {g["group"]: g for g in b["groups"]}
added = sorted(set(gb)-set(ga)); removed = sorted(set(ga)-set(gb))
changed = sorted(k for k in ga if k in gb and ga[k] != gb[k])
print("COUNTS", len(ga), len(gb), len(added), len(removed), len(changed))
st = collections.Counter(); moves=[]
for k in sorted(set(ga)&set(gb)):
    sa = (ga[k].get("resume") or {}).get("stage"); sb = (gb[k].get("resume") or {}).get("stage")
    if sa != sb: st[sb]+=1; moves.append((k,sa,sb,gb[k].get("resume")))
print("STAGE_CHANGES", len(moves), dict(st))
print("KEYS", sorted({kk for g in gb.values() for kk in g}))
json.dump({"added":added,"removed":removed,"changed":changed,"moves":moves}, open(sys.argv[3],"w"), indent=1, default=str)

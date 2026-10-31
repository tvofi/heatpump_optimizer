import json,sys
a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2]))
ga={g['group']:g for g in a['groups']}; gb={g['group']:g for g in b['groups']}
print("groups", len(ga), len(gb))
add=sorted(set(gb)-set(ga)); rem=sorted(set(ga)-set(gb))
print("added", len(add), add)
print("removed", len(rem), rem)
changed=[]
for k in sorted(set(ga)&set(gb)):
    if ga[k]!=gb[k]:
        keys=sorted(set(ga[k])|set(gb[k]))
        moved=[x for x in keys if ga[k].get(x)!=gb[k].get(x)]
        changed.append((k,moved))
print("changed", len(changed))
for k,m in changed: print("  ",k,"("+", ".join(m)+")")

import json,re
d=json.load(open("/root/ev/roster_diff.json"))
for k,a,b,r in d["moves"]:
    if b not in ("done","absorbed"): continue
    note=(r.get("note") or "")+" "+(r.get("next_step") or "")
    pr=re.findall(r"(?:#|PR-)(\d{3,5})",note); grp=[g for g in re.findall(r"R10-[A-Z0-9-]+[A-Z0-9]",note) if g!=k]
    print("PR " if pr else ("GRP" if grp else "NONE"), b, k, "prs="+",".join(pr), "grps="+",".join(grp), "| note:", (r.get("note") or "")[:160])

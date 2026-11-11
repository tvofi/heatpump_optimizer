"""Reviewer's probe: for each live group over PART_CARRIES pending, does a part-k topic
(<topic>-p<k>, k>1) equal another roster group's own topic (its dispatch ref and branch)?"""
import sys, json, subprocess
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import roster_lib, cloud_dispatch as cd
ref = sys.argv[2]
path = roster_lib.roster_path(".", ref, None)
roster = json.loads(subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True, check=True).stdout)
legacy = roster_lib.read_legacy(".", path)
topics = {cd._topic_of(g): g.get("group") for g in roster.get("groups", [])}
for g in roster.get("groups", []):
    if (g.get("resume") or {}).get("stage") in roster_lib.CARRY_CLOSED:
        continue
    pend = roster_lib.pending_carries(g, legacy)
    if len(pend) <= cd.PART_CARRIES:
        continue
    k = len(cd.part_split(pend).split(", "))
    for p in range(2, k + 1):
        t = f"{cd._topic_of(g)}-p{p}"
        if t in topics:
            o = next(x for x in roster["groups"] if x.get("group") == topics[t])
            print(f"COLLISION {g.get('group')} --part {p}: topic {t} = topic of {topics[t]} "
                  f"(stage {(o.get('resume') or {}).get('stage')}); ref {cd.dispatch_ref('fixer', t, '')}; "
                  f"group_for_branch(fix/{t}) -> {roster_lib.group_for_branch(roster, 'fix/' + t)}")

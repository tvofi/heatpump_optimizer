"""Reviewer's probe (not the finder's): live groups over PART_CARRIES pending, their split,
and whether roster_lib.group_for_branch maps each part-k topic back to the group."""
import sys
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import roster_lib, cloud_dispatch as cd
import json, subprocess
ref = sys.argv[2] if len(sys.argv) > 2 else roster_lib.reader_ref(".", None)
path = roster_lib.roster_path(".", ref, None)
roster = json.loads(subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True, check=True).stdout)
legacy = roster_lib.read_legacy(".", path)
print("roster", ref, path)
n = 0
for g in roster.get("groups", []):
    if (g.get("resume") or {}).get("stage") in roster_lib.CARRY_CLOSED:
        continue
    pend = roster_lib.pending_carries(g, legacy)
    if len(pend) <= cd.PART_CARRIES:
        continue
    n += 1
    topic = cd._topic_of(g)
    split = cd.part_split(pend)
    k = len(split.split(", "))
    maps = {p: roster_lib.group_for_branch(roster, f"fix/{topic}-p{p}") for p in range(2, k + 1)}
    bad = {p: m for p, m in maps.items() if m != g.get("group")}
    print(f"{g.get('group')} pending={len(pend)} topic={topic} split={split} part-branch-maps-wrong={bad or 'none'}")
print("live groups over five pending:", n)

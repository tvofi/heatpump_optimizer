"""Reviewer's probe, round 2 (extends round-1 ev/collide.py, the finder's harness): for every
live group over PART_CARRIES pending and each part k in 2..n, call dispatch_group itself at the
roster ref with publish_seat captured (nothing pushed), and independently ask group_for_branch
which group fix/<topic> and handoff/<topic> credit. Prints one RESULT line per part."""
import sys, json, subprocess, os
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import roster_lib, cloud_dispatch as cd
ref = sys.argv[2]
published = []
cd.publish_seat = lambda repo_dir, r, role, head, **a: published.append((r, a["topic"])) or {}
cd.design_approved = lambda *a: True
path = roster_lib.roster_path(".", ref, None)
roster = json.loads(subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True, check=True).stdout)
legacy = roster_lib.read_legacy(".", path)
env = {"HPO_CLOUD_ENV_ID": "env_0000000000000000000000000"}
for g in roster.get("groups", []):
    if (g.get("resume") or {}).get("stage") in roster_lib.CARRY_CLOSED:
        continue
    pend = roster_lib.pending_carries(g, legacy)
    if len(pend) <= cd.PART_CARRIES:
        continue
    k = len(cd.part_split(pend).split(", "))
    for p in range(1, k + 1):
        t = cd._topic_of(g) + (f"-p{p}" if p > 1 else "")
        credit = {b: roster_lib.group_for_branch(roster, f"{b}/{t}") for b in ("fix", "handoff")}
        alias = sorted({c for c in credit.values() if c != g.get("group")} - {None})
        n0 = len(published)
        try:
            out = "published " + cd.dispatch_group("fixer", g["group"], "", repo_dir=".", roster_ref=ref, head="0"*40,
                                                    environ=env, design_exempt="probe", part=p)
        except cd.Refusal as e:
            out = "refused: " + str(e)
        except Exception as e:
            out = f"error {type(e).__name__}: {e}"
        bad = (alias and out.startswith("published")) or (not alias and out.startswith("refused") and "is the topic of" in out)
        print(f"RESULT group={g['group']} part={p} topic={t} alias={','.join(alias) or '-'} -> {out[:160]} verdict={'BAD' if bad else 'ok'}")

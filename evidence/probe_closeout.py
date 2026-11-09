import sys; sys.path.insert(0, sys.argv[1]+"/tools/audit/seat")
import closeout
def gr(n, st, **kw): return {"group": n, "resume": {"stage": st}, **kw}
for st in ("refused","refuted","deferred"):
    r = gr("R", st); r["resume"]["host"] = "H"
    print(f"RESULT closeout blocker {st}+open-host:", closeout.roster_blockers({"groups":[r, gr("H","in-progress"), gr(closeout.SELF_GROUP,"not-started")]}))

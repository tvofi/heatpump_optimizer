import sys; sys.path.insert(0, "tools/ci"); import prelude as P
t = P.title("code", "7", "main", "abc")
def run(fast_names):
    jobs = {"prelude": ("completed","success"), "gate": ("completed","success")}
    for u in sorted(P.workset("code","7") & set(P.UNITS)):
        for n in P.UNITS[u]:
            if (u, n) == ("tests", "fast (3.14)"):
                for f in fast_names: jobs[f"tests / {f}"] = ("completed","success")
            else:
                jobs[f"{u} / {n}"] = ("completed","success")
    return {"id": 1, "title": t, "status": "in_progress", "attempt": 1, "jobs": jobs}
print("null, unsharded completed run judging():", P.judging(run(["fast (3.14)"])))
print("sharded completed run judging():", P.judging(run([f"fast (3.14, {k}/3)" for k in (1,2,3)])))

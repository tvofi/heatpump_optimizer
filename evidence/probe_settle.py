import sys; sys.path.insert(0, sys.argv[1])
import sweep_selftest as T
def pinned(*rs, v=9, files=("tools/ci/gate.py",)):
    for r in rs: r.setdefault("event","pull_request")
    w=T.World(list(rs), v); w.base_files=list(files); return w
# settle: the #3261 pair, plus a dispatched fresh judge created after both stale gates concluded
w=pinned(T.run(1,"1",started="5",units=["6"]), T.run(2,"1",started="5",units=["6"]), T.run(5,"7",g="success",started="8"), v=2)
w.runs[5]["event"]="workflow_dispatch"
rc,out=w.sweep()
print("settle+fresh judge present: posts=",w.posts); print(out)
# poll path: a stale red gate still running when the sweep starts, finishing red; a dispatched judge created later
w=pinned(T.run(1,"1",status="in_progress",gstatus="in_progress",started="2"), T.v_run())
w.runs[1]["event"]="pull_request"
w.runs[5]=dict(T.run(5,"9",g="success",started="9"),event="workflow_dispatch")
w.script={1:T.finish(1,"failure")}
rc,out=w.sweep()
print("poll+fresh judge present: posts=",w.posts); print(out)

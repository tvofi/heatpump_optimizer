import sys
tree=sys.argv[1]; sys.path.insert(0, tree+"/tools/ci")
import prelude as p
T=p.title("code","7","main","H")
def J(name,st,c=None): return {"name":name,"status":st,"conclusion":c,"id":1}
units=[J("prelude","completed","success")]+[J(n,"completed","success") for n in sorted(set(p.workset("code","7"))) if n in p.UNITS]
# expand: use the names judging() expects via the self-test helper if present
states={
 "pending(queued, no jobs)": ("queued",[]),
 "running(units in progress)": ("in_progress",[J("prelude","completed","success"),J("tests / fast (3.14)","in_progress")]),
 "running(pr-contract started)": ("in_progress",[J("prelude","completed","success"),J("tests / fast (3.14)","in_progress"),J("pr-contract / pr-contract","in_progress")]),
 "concluded(completed)": ("completed",[J("prelude","completed","success"),J("gate","completed","success")]),
}
for label,(st,jobs) in states.items():
    def get(path,params=None):
        if path.endswith("/runs"): return 200,{},{"workflow_runs":[{"id":40,"status":st,"display_title":T}]}
        return 200,{},{"jobs":jobs,"total_count":len(jobs)}
    ctx={"repo":"o/r","head":"H","run_id":50}
    print(f"{tree.rsplit('/',1)[-1]} {label}: defer_to -> {p.defer_to(ctx,'7',get)}; body kinds deferred: {getattr(p,'BODY_KINDS',('edit',))}")

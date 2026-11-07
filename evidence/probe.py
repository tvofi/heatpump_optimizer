import sys; sys.path.insert(0, sys.argv[1]); import sweep
H="h"*40
def ts(s): return f"2026-11-07T12:{s//60:02d}:{s%60:02d}Z"
def mk(with3):
    runs={1:dict(id=1,status="completed",created_at=ts(0),run_attempt=1,path=sweep.CI_PATH,head_sha=H,pull_requests=[{"number":7}],
           jobs=[dict(name="prelude",id=11,status="completed",conclusion="success",started_at=ts(1),completed_at=ts(5)),
                 dict(name="gate",id=10,status="completed",conclusion="failure",started_at=ts(10),completed_at=ts(11))]),
          2:dict(id=2,status="completed",created_at=ts(2),run_attempt=1,path=sweep.CI_PATH,head_sha=H,pull_requests=[{"number":7}],
           jobs=[dict(name="tests / fast",id=21,status="completed",conclusion="success",started_at=ts(3),completed_at=ts(30)),
                 dict(name="gate",id=20,status="completed",conclusion="success",started_at=ts(31),completed_at=ts(40))])}
    if with3:
        runs[3]=dict(id=3,status="completed",conclusion="startup_failure",created_at=ts(35),run_attempt=1,path=sweep.CI_PATH,head_sha=H,pull_requests=[{"number":7}],jobs=[])
    return runs
for with3 in (False, True):
    runs=mk(with3); posts=[]; outs=[]
    def get(path, params=None):
        if path.endswith("/pulls/7"): return 200,{},{"head":{"sha":H}}
        if path.endswith("/actions/runs"): return 200,{},{"workflow_runs":list(runs.values())}
        i=int(path.split("/runs/")[1].split("/")[0]); r=runs[i]
        return 200,{},({"jobs":r["jobs"]} if path.endswith("/jobs") else r)
    clk=[0.0]
    sweep.main(["--run","2","--repo","o/r"],get,lambda p,b=None:(posts.append(p),(201,{},{}))[1],outs.append,lambda s:clk.__setitem__(0,clk[0]+s),lambda:clk[0])
    print(f"third run completed with no jobs={with3}: posts={posts} out={outs[-1]!r}")

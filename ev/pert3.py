exec(open('$HOME/pert2.py').read().split('def g(rs)')[0])
def g(rs): return c.window_work_minutes(rs[:16])
def work(r,job):
    for j in r["jobs"]:
        if j["name"]==job and j.get("completed_at") and j.get("started_at"):
            P=lambda t:datetime.fromisoformat(t.replace("Z","+00:00")); return (P(j["completed_at"])-P(j["started_at"])).total_seconds()
SLOW={"tests / closures":2200,"tests / fast (3.14)":1850,"tests / arch-instrument":1800}
print("base",g(runs))
# realistic slow-host window: newest k runs, each fast draw of the lane made slow (x1.9), slow draws left
for job,th in SLOW.items():
    out=[]
    for k in [8,12,15,16]:
        rs=[grow(r,job,0,mult=1.9) if i<k and (work(r,job) or 1e9)<th*0.8 else r for i,r in enumerate(runs)]
        out.append(f"k={k}:{g(rs)}")
    print("all-slow",job," ".join(out))
# one outlier: newest run's lane at 3.2x its fastest window value (e.g. a retried/failing job)
for job in SLOW:
    m=min(work(r,job) for r in runs[:16] if work(r,job) and work(r,job)>300)
    w0=work(runs[0],job)
    rs=[grow(runs[0],job,3.2*m-w0)]+runs[1:]
    print("one outlier 3.2x fastest",job,g(rs))

exec(open('$HOME/pert3.py').read().split('print("base"')[0])
import statistics
def oldmed(rs):
    m=[x for x in map(c.run_minutes,rs[:8]) if x is not None]; return round(statistics.median(m),3)
print("old median-8 base",oldmed(runs))
for job in ["tests / closures","tests / fast (3.14)"]:
    print("old +300",job," ".join(f"k={k}:{oldmed([grow(r,job,300) if i<k else r for i,r in enumerate(runs)])}" for k in [1,2,4,5,8]))
# variant: floor from median, success-only
orig=c.window_work_minutes
def variant(rs):
    chains,work=[],{}
    for r in rs:
        w=c._walk(r)
        if w is None: continue
        chains.append(c.run_chain(r))
        concl={j["name"]:j.get("conclusion") for j in r["jobs"]}
        for j in w:
            if not j["skipped"] and concl.get(j["name"])=="success": work.setdefault(j["name"],[]).append(j["work"])
    price={n:min(x for x in s if x>=statistics.median(s)/3) for n,s in work.items()}
    return round(max(sum(price.get(n,0) for n in ch) for ch in chains)/60,3)
print("variant base",variant(runs[:16]))
for job in SLOW:
    m=min(work(r,job) for r in runs[:16] if work(r,job) and work(r,job)>300); w0=work(runs[0],job)
    print("variant one outlier 3.2x",job,variant([grow(runs[0],job,3.2*m-w0)]+runs[1:16]))
print("variant +300 closures all16",variant([grow(r,"tests / closures",300) for r in runs[:16]]))

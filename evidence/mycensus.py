import json,glob,collections
runs={}
for p in glob.glob('runs/*.json'):
    for r in json.load(open(p))['workflow_runs']: runs[r['id']]=r
R=list(runs.values())
print("events",collections.Counter((r['event'],r['conclusion']) for r in R))
by=collections.defaultdict(list)
for r in R:
    if r['event']=='pull_request': by[r['head_sha']].append(r)
canc=[r for r in R if r['event']=='pull_request' and r['conclusion']=='cancelled']
same=[r for r in canc if len(by[r['head_sha']])>1]
print("cancelled pr runs",len(canc),"with any same-sha pr sibling",len(same))
print("actors of cancelled",collections.Counter(r['triggering_actor']['login'] for r in canc))
# sibling count distribution and whether cancelled was the lower id
pos=collections.Counter()
gap=[]
for r in same:
    sibs=[s for s in by[r['head_sha']] if s['id']!=r['id']]
    pos['cancelled_is_older_id' if r['id']<min(s['id'] for s in sibs) else 'cancelled_not_oldest']+=1
    from datetime import datetime
    t=lambda x:datetime.fromisoformat(x['created_at'].replace('Z','+00:00'))
    gap.append(min(abs((t(s)-t(r)).total_seconds()) for s in sibs))
print(pos); gap.sort(); print("min gap s: max",gap[-1] if gap else None,"median",gap[len(gap)//2] if gap else None)
# live-head question: is any head SHA left with only cancelled pr runs + no success?
only=[sha for sha,l in by.items() if all(x['conclusion']=='cancelled' for x in l)]
print("shas with only cancelled pr runs",len(only))
rv=[r for r in R if r['event']!='pull_request' and r['conclusion']=='cancelled']
print("non-pr cancelled",len(rv))

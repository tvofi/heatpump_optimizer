import sys, copy
sys.argv=['x']; sys.path.insert(0,'dev/audit/harnesses/r10_hotfix_ci_critpath_3')
import replay as R, json
from tests import ci_ratchet as cr
runs=sorted(json.loads((R.HERE/'runs.json').read_text())['workflow_runs'],key=lambda r:r['created_at'],reverse=True)
W=16; new=cr.window_work_minutes; base=new(runs[:W]); print('base',base,'retired',R.retired(runs[:W]))
for lane in R.LANES:
    fastest=min(x for x in (R.work_s(r,lane) for r in runs[:W]) if x)
    row=[]
    for k in (1,2,4,6,7,8,9):
        w=[R.with_work(r,lane,lambda _x:3.2*fastest) for r in runs[:k]]+runs[k:W]
        row.append(f"k={k} {round(new(w)-base,3):+}")
    w=[R.with_work(runs[0],lane,lambda _x:10*fastest)]+runs[1:W]
    print(lane,'3.2x newest k:',' '.join(row),'| 10x one:',round(new(w)-base,3))
def setc(r,lane,c,frac):
    r=copy.deepcopy(r)
    for j in r['jobs']:
        if j['name']==lane and j.get('completed_at'):
            j['conclusion']=c
    return R.with_work(r,lane,lambda x:x*frac) if frac!=1 else r
for lane in R.LANES+('prelude',):
    for c,fr in (('failure',0.4),('failure',0.9),('cancelled',0.45)):
        w=[setc(runs[0],lane,c,fr)]+runs[1:W]
        print(f"{lane} newest {c} at {fr}: {round((new(w) or 0)-base,3):+}")
# all fastest runs of a lane failed: 
print('--- isolate: conclusion only (no work change), and chain under the 0.4 plant')
for lane in R.LANES:
    w=[setc(runs[0],lane,'failure',1)]+runs[1:W]
    print(f"{lane} newest failure, work unchanged: new {round(new(w)-base,3):+} retired {round(R.retired(w)-R.retired(runs[:W]),3):+}")
r0=setc(runs[0],'tests / fast (3.14)','failure',0.4)
print('chain fast-failed-0.4:',cr.run_chain(r0),'retired delta',round(R.retired([r0]+runs[1:W])-R.retired(runs[:W]),3))
# ci-ratchet success after merge
def ok(r):
    r=copy.deepcopy(r)
    for j in r['jobs']:
        if j['name']=='tests / ci-ratchet' and j['conclusion']=='failure': j['conclusion']='success'
    return r
P1=ok(runs[0])
print('2nd push after merge, window [P1(ci-ratchet success)]+runs[:15]:',new([P1]+runs[:15]),'budget+band',21.983+1.3)
print('all 16 with ci-ratchet success:',new([ok(r) for r in runs[:16]]))
cw=[ (cr._at(j['completed_at'])-cr._at(j['started_at'])).total_seconds() for r in runs for j in r['jobs'] if j['name']=='tests / ci-ratchet' and j['conclusion'] in('success','failure')]
print('ci-ratchet work s min/max over 40:',min(cw),max(cw))

"""Reviewer's own harness (fix review of #3201): price windows mixing the branch's
probed fleet runs (fleet.json) into main's push history (runs.json) with the
tree's own tests/ci_ratchet.window_work_minutes, jobs cut to the names main's
push runs carry (a pull_request run's extra jobs, e.g. codeql, are not on push)."""
import json,sys
sys.path.insert(0,'/root/wt')
from tests import ci_ratchet as cr
H='/root/wt/dev/audit/harnesses/r10_hotfix_ci_critpath_4/'
rr=json.load(open(H+'runs.json'))['workflow_runs']
fl=json.load(open(H+'fleet.json'))['workflow_runs']
pushnames={j['name'] for r in rr[:16] for j in r['jobs']}
def P(r):
    r=dict(r); r.pop('event',None); r['conclusion']='success'
    r['jobs']=[j for j in r['jobs'] if j['name'] in pushnames]; return r
budget=21.983+1.3
print('push job names', len(pushnames))
print('RESULT main newest16 =', cr.window_work_minutes(rr[:16]), 'limit', round(budget,3))
for k,f in enumerate(fl):
    print(f'RESULT probed {f["id"]}({f["event"]}) + main15 =', cr.window_work_minutes([P(f)]+rr[:15]))
print('RESULT 3 probed + main13 =', cr.window_work_minutes([P(f) for f in fl]+rr[:13]))
for k in (1,2):
    print(f'RESULT 16 copies of probed {fl[k]["id"]} =', cr.window_work_minutes([P(fl[k])]*16))
print('RESULT the 3 probed runs, 16-run window by repetition =', cr.window_work_minutes([P(f) for f in fl]*5+[P(fl[1])]))

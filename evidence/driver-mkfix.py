import json, subprocess, sys
sh=lambda *a: subprocess.check_output(a, text=True).strip()
rp='dev/programme/rosters/wave-r11-groups.json'
r=json.load(open(rp)); gs=r['groups']
o=json.load(open('dev/audit/yardstick/round10/OBJECTIVE.json'))
terms=json.load(open('dev/audit/config/objective.json'))['terms']
head=sh('git','rev-parse','HEAD')
rank1={'R11-OUTSIDE-HONEST-DHW-RUNS','R10-DRAW-MAP-EVIDENCE'}
groups={}
for g in gs:
    n=g['group']
    groups[n]={'rank':1,'cards':['E11-FIX']} if n in rank1 else {'rank':2,'examined_by':'D7 pass'}
edges=[{'from':'R11-OUTSIDE-HONEST-DHW-RUNS','to':t,'adr':'ADR-F1'} for t in ('R11-OUTSIDE-HONEST-STARTS-RUNS','R11-OUTSIDE-HONEST-STARTS-RUNS-P2')]
edges+=[{'from':'R10-DRAW-MAP-EVIDENCE','to':t,'adr':'ADR-F1'} for t in ('R10-COP-LEARNER-DRAW-FLOOR','R11-OUTSIDE-SELF-SETTING-PUMP')]
plan={'round':11,'groups':[{'group':g['group']} for g in gs],
 'moves':[{'group':g['group'],'adr':'ADR-F1','metrics':{},'dS':0} for g in gs],
 'objective':{'baseline':{'record':'dev/audit/yardstick/round10/OBJECTIVE.json','tree':head},
  'pin':{'roster_path':rp,'roster_blob':sh('git','hash-object',rp),'start':'2026-11-17T08:00:00Z','durations_blob':sh('git','rev-parse','HEAD:tools/plan/durations.json')},
  'terms':{t:({'direction':'hold','basis':'fixture'} if 'value' in o['terms'][t] else {'direction':'undecided','builder':'fixture'}) for t in terms},
  'groups':groups,'edges':edges}}
import os; os.makedirs('dev/audit/rounds/round11/PLAN',exist_ok=True)
json.dump(plan,open('dev/audit/rounds/round11/PLAN/PLAN.json','w'),indent=1)

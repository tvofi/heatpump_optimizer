import sys; sys.path.insert(0,'tests'); import json, ci_ratchet as c
b=json.load(open('tests/ci_budgets.json')); nb={k:v for k,v in b.items() if k!='critical_path_minutes_band'}
base={k:v for k,v in b.items() if k not in ('recorded_at','reason','critical_path_minutes_band')}
for lbl,d in [('34.467',{'critical_path_minutes':34.467}),('35.567',{'critical_path_minutes':35.567}),('35.568',{'critical_path_minutes':35.568}),('35.777',{'critical_path_minutes':35.777}),('spp55',{'script_runs_per_push':55}),('arch1',{'archscore.unused_boundary_imports':1})]:
    d2={**base,**d}
    print('RESULT',lbl,'head grew=',c.compare(b,d2)[1],'noband grew=',c.compare(nb,d2)[1])
print('RESULT budget_problems(head)=',c.budget_problems(b))

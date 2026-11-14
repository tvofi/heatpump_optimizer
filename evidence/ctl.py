import sys,json
sys.path[:0]=['tests','tests/hastub']
import replay as R
bad=0
for n,ok,d in R.controls():
    if 'cycle_cost' in n or not ok:
        print(('PASS ' if ok else 'FAIL ')+n+' :: '+d[:300])
    bad+= not ok
syn='synthetic-dhw-only.json'
b,k,f=R.derive_cost_classes(R.cost_draws(),syn)
print('derived class budgets', k)
print('derived == COST_CLASS_BUDGETS[syn]:', k==R.COST_CLASS_BUDGETS[syn])
print('bands derived == COST_RUNNER_CLASSES:', b==R.COST_RUNNER_CLASSES.get(syn, R.COST_RUNNER_CLASSES) if isinstance(R.COST_RUNNER_CLASSES,dict) else b)
print('RESULT failing controls', bad)

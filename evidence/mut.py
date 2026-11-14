import sys
sys.path[:0]=['tests','tests/hastub']
import replay as R
want=('control:cycle_cost:class_rule','control:cycle_cost:level_shift','control:cycle_cost:draws')
for n,ok,d in R.controls():
    if n in want: print(('PASS ' if ok else 'FAIL ')+n+' :: '+d[:160])

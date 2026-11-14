import sys,math
sys.path[:0]=['tests','tests/hastub']
import replay as R
syn='synthetic-dhw-only.json'
raw=R.cost_draws(cuts=())
b,k,f=R.derive_cost_classes(raw,syn)
print('no-cut derived class budgets (null):',k)
print('no-cut free budgets:',f)
cls=dict(R.cost_class_jobs(raw,syn))
cut='2026-11-08T17:14:34Z'
cr=R.cost_draw_created()
for c in ('ref40','ref47'):
    pre=[a['clean']['cpu_ratio'] for j,_,a in cls[c] if cr[j]<cut]
    post=[(j,a['clean']['cpu_ratio']) for j,_,a in cls[c] if cr[j]>=cut]
    mid=math.sqrt(min(pre)*max(pre)); print(c,'pre n',len(pre),'min',min(pre),'max',max(pre),'post',post,'factor',round(post[0][1]/mid,4))
f40=1.7266/math.sqrt(2.7594*2.8809); f47=1.5508/math.sqrt(2.2558*2.4762); g=math.sqrt(f40*f47)
print('f40 %.4f f47 %.4f geo %.4f dist %.3f%% %.3f%%'%(f40,f47,g,100*(g/f40-1),100*(1-g/f47)))
print('head derived (with cut):',R.derive_cost_classes(R.cost_draws(),syn)[1:])
print('COST_BUDGETS syn:',R.COST_BUDGETS.get(syn))

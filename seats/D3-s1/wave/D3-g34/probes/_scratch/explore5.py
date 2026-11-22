exec(open('/tmp/claude-0/sp/explore2.py').read().split('# b8d5: gaps')[0])
ALT=[S,T,R,S,T,R,S,T,R,S,T,R,S,T,R,S]
def exact_series(k, p, qs, outs, T0=20.0):
    # T_{i+1} = T_i - k*(T_i - Tout_i) + p*q_i, dt = 1 h, phases alternating (no in-phase triple -> sigma2 = 0)
    T=[T0]
    for q,o in zip(qs,outs): T.append(T[-1] - k*(T[-1]-o) + p*q)
    n=len(T)
    return L.samples(T, list(outs)+[0.0], list(qs)+[0.0], ALT[:n], list(range(n)))
outs=[0.0,4.0,-2.0,8.0,2.0,-4.0,6.0,0.0,10.0]
# d742: power constant (collinear with intercept) -> 4-col gram exactly singular -> 2-col fallback rank 2
smp=exact_series(0.5,0.25,[4.0]*9,outs)
for k in ('d742_2114','1066_2114'): show(k,'q-const exact',smp)
# 1066: power proportional to x = Tout - T  (collinear col0/col1) -> fallback rank 1
T=[20.0]; outs_hot=[]; qs=[]
for o in [24.0,28.0,26.0,32.0,30.0,27.0,34.0,29.0,31.0]:
    x=o-T[-1]; outs_hot.append(o); qs.append(2.0*x); T.append(T[-1]+0.25*x)
smp=L.samples(T,outs_hot+[0.0],qs+[0.0],ALT[:len(T)],list(range(len(T))))
for k in ('d742_2114','1066_2114'): show(k,'q ∝ x',smp)
smp0=exact_series(0.5,0.25,[0.0]*9,outs)
for k in ('d742_2114','1066_2114'): show(k,'q zero',smp0)
for k in ('d742_2114','1066_2114'): show(k,'plant null',L.plant())
# 0722 negative ua plant
for k in ('0722_2126','3e78_2126','87c3_2126'):
    show(k,'neg-ua plant',L.plant(ua=-0.1,t_room=20.0))
    show(k,'plant null',L.plant())
# tie search for 3e78/87c3 via exact fallback series
import itertools
hits={'3e78_2126':0,'87c3_2126':0}
rng=np.random.default_rng(1)
for trial in range(3000):
    o=[float(x) for x in rng.integers(-8,12,9)]
    smp=exact_series(1e-6,0.25,[4.0]*9,o) if trial%2==0 else exact_series(0.5,1e-6,[4.0]*9,o)
    for k in hits:
        b=L.call(L.SI.identify,smp); m=L.call(M[k],smp)
        if repr(b)!=repr(m) and hits[k]<2:
            hits[k]+=1; print(k,'TIE hit trial',trial,o, L.short(b),'|',L.short(m))
print(hits)

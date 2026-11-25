exec(open('/tmp/claude-0/sp/explore2.py').read().split('# b8d5: gaps')[0])
# 8437 search
rng=np.random.default_rng(0)
for s in range(60):
    kw=dict(ua=float(rng.uniform(0.05,0.5)),cap=float(rng.uniform(1,20)),gains=float(rng.uniform(0,1)),noise=float(rng.choice([0,0.01,0.03,0.06,0.1,0.2])),dt_h=float(rng.choice([0.25,0.5,1.0])),drift=float(rng.choice([0,0.05,-0.05])),seed=s, q=(float(rng.uniform(0,4)),float(rng.uniform(2,8)),0.0))
    smp=L.plant(**kw)
    b=L.call(L.SI.identify,smp); m=L.call(M['8437_2010'],smp)
    if repr(b)!=repr(m): print('8437 hit', kw, L.short(b), '|', L.short(m))
# 44bb tie construction
u=0.125; a_,b_,c_=20.0,21.0,22.0
temps=[a_,a_+u,a_,b_,b_+2*u,b_,c_,c_+2*u,c_,21.5]
ph=[S,S,S,T,T,T,R,R,R,S]
devs=[1,-1,0.25,-0.25,0.25,-0.25,0,0,0]
outs=[t+20+d for t,d in zip(temps[:9],devs)]+[0.0]
pw=[2,2,2,5,5,5,0,0,0,2]
smp=L.samples(temps,outs,pw,ph,list(range(10)))
for k in ('44bb_2038','b97b_2038','6b6a_2068'): show(k,'tie-design',smp)
# null: tie broken by one ulp-ish: devs slightly different
outs2=list(outs); outs2[0]+=0.0625
smp2=L.samples(temps,outs2,pw,ph,list(range(10)))
for k in ('44bb_2038',): show(k,'tie-broken',smp2)
# sigma2 == 0 designs for b97b/6b6a: no triples (alternating phases), constant x (spread 0)
ph_alt=[S,T,S,T,R,S,R,T,R,S]
smp3=L.samples(temps,outs,pw,ph_alt,list(range(10)))
outs_c=[t-0.0 for t in temps]  # delta 0 -> x spread 0
smp4=L.samples(temps,[t+5 for t in temps],pw,ph_alt,list(range(10)))
for k in ('b97b_2038','6b6a_2068'):
    show(k,'no-triples',smp3); show(k,'no-triples const-x',smp4)
    show(k,'noise-free plant 3triples', L.plant(hours=(0.75,0.75,0.75),noise=0.0)[:9])
    show(k,'plant', L.plant())
# d2 exactly zero with triples: linear temps
lin=[20+0.25*i for i in range(10)]
smp5=L.samples(lin,[l-20 for l in lin],pw,ph,list(range(10)))
for k in ('b97b_2038','6b6a_2068'): show(k,'linear temps (k_hat curvature)',smp5)

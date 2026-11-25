exec(open('/tmp/claude-0/sp/explore2.py').read().split('# b8d5: gaps')[0])
p=L.plant(noise=0.0)
def dup(p, idx, dt, bump=0.05):
    q=list(p); s=q[idx]
    q.insert(idx+1, sysid.SysIdSample(when=s.when+dt, room_temp=s.room_temp+bump, outdoor_temp=s.outdoor_temp, power_kw=s.power_kw, phase=s.phase))
    return q
print([s.phase[:2] for s in p])
for k in ('20f7_2018','50da_2018'):
  for idx in (6,10,15):
    show(k,f'dup0@{idx}', dup(p,idx,timedelta(0)))
    show(k,f'tie3600us@{idx}', dup(p,idx,timedelta(microseconds=3600)))
    show(k,f'3601us@{idx}', dup(p,idx,timedelta(microseconds=3601)))
for noise in (0.0,0.01,0.02,0.05):
  for seed in range(3):
    pp=L.plant(hours=(0.75,0.75,0.75),dt_h=0.25,noise=noise,seed=seed)[:9]
    show('4eeb_2032',f'3triples n={noise} s={seed}',pp)
pp=L.plant(hours=(1.0,1.0,0.75),dt_h=0.25,noise=0.02,seed=0)[:12]
show('4eeb_2032','4triples null',pp)

import _sysid_lib as L, numpy as np
from datetime import timedelta
from custom_components.heatpump_optimizer import sysid
exec(open('/tmp/claude-0/sp/explore.py').read().split('# random battery')[0])
S,T,R = sysid.PHASE_SETTLING, sysid.PHASE_STEP, sysid.PHASE_RELAX
def show(k, name, smp, cfg=None):
    b=L.call(L.SI.identify,smp,cfg); m=L.call(M[k],smp,cfg)
    print(k, name, int(repr(b)!=repr(m)), '|', L.short(b), '|', L.short(m))
# b8d5: gaps
hrs=[0,0.5,1,4,4.5,8,8.5]; n=len(hrs)
smp=L.samples([20,20.2,20.3,20.1,20.4,19.9,20.0],[0]*n,[3,3,6,6,0,0,0],[S,S,T,T,R,R,R],hrs)
show('b8d5_1942','4rows',smp)
hrs=[0,3,6,9,12,15]; smp=L.samples([20,20.5,21,20.8,20.4,20.2],[0]*6,[3,6,6,0,0,0],[S,T,T,R,R,R],hrs)
show('b8d5_1942','0rows',smp)
hrs=[0,0.5,1,1.5,2,6,6.5]; smp=L.samples([20,20.2,20.5,20.7,20.6,20.0,19.9],[0]*7,[3,6,6,6,0,0,0],[S,T,T,T,R,R,R],hrs)
show('b8d5_1942','4rows-b',smp)
# 756f
base=L.plant()
for tm in (0.05, 0.0, 0.1, 10.0):
    show('756f_1974', f'tm={tm}', base, sysid.SysIdConfig(thermal_mass_prior=tm))
show('756f_1974','tm=0.05 noisy', L.plant(noise=0.03,seed=4), sysid.SysIdConfig(thermal_mass_prior=0.05))
# 20f7/50da duplicate & tie timestamps
p=L.plant(noise=0.0)
def dup(p, idx, dt):
    q=list(p); s=q[idx]
    q.insert(idx+1, sysid.SysIdSample(when=s.when+dt, room_temp=s.room_temp+0.05, outdoor_temp=s.outdoor_temp, power_kw=s.power_kw, phase=s.phase))
    return q
for k in ('20f7_2018','50da_2018'):
    show(k,'dup0', dup(p,3,timedelta(0)))
    show(k,'tie3600us', dup(p,3,timedelta(microseconds=3600)))
    show(k,'3601us', dup(p,3,timedelta(microseconds=3601)))
    show(k,'neg', dup(p,3,timedelta(seconds=-60)))
# 4eeb: exactly 3 triples
ph=[S,S,S,T,T,T,R,R,R,S]
for noise in (0.0,0.02,0.05):
    pp=L.plant(hours=(0.75,0.75,0.75),dt_h=0.25,noise=noise,seed=7)
    pp=pp[:10]; pp=[sysid.SysIdSample(s.when,s.room_temp,s.outdoor_temp,s.power_kw,f) for s,f in zip(pp,ph)]
    show('4eeb_2032',f'3triples n={noise}',pp)

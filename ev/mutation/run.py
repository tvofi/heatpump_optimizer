import subprocess,os,sys
W='/root/wt-mut/';O=W+'custom_components/heatpump_optimizer/optimizer.py';P=W+'custom_components/heatpump_optimizer/plan_slots.py'
M="# --- R11-SEAM-solver: the start set brackets"
env=dict(os.environ,PYTHONPATH='tests/hastub')
def run(i):
    r=subprocess.run(['python3','tools/audit/seat/features_block.py','--prelude',"exec(open('/root/mut/prelude.py').read())",M],cwd=W,env=env,capture_output=True,text=True)
    open(f'/root/mut/{i}.txt','w').write(r.stdout+r.stderr+f'\nrc={r.returncode}\n')
def ed(f,a,b,cnt=1):
    s=open(f).read(); assert s.count(a)==cnt,(a,s.count(a)); open(f,'w').write(s.replace(a,b))
def settle():
    s=open(O).read(); i=s.index('def _settle_horizon'); j=s.index('\n    def ',i+10)
    seg=s[i:j]; assert seg.count('h.money_prices')==3,seg.count('h.money_prices')
    open(O,'w').write(s[:i]+seg.replace('h.money_prices','h.prices')+s[j:])
def m3():
    s=open(O).read(); a='            starts.append(_lower_bound_start(bounds))\n'; assert s.count(a)==1; open(O,'w').write(s.replace(a,''))
def m4():
    s=open(O).read(); a='    starts.append(_lower_bound_start(bounds))\n    return starts'; assert s.count(a)==1; open(O,'w').write(s.replace(a,'    return starts'))
ML=[('M1',lambda:ed(P,'max(dict.fromkeys(codes), key=codes.count)','max(set(codes), key=codes.count)')),
('M2',lambda:ed(O,'return self.prices if self.raw_prices is None else self.raw_prices','return self.prices')),
('M3',m3),('M4',m4),
('M5',lambda:ed(O,'    if covered > 0.0:','    if False:')),
('M6',lambda:ed(O,'[np.asarray(result.x, dtype=float), _lower_bound_start(bounds)], None, 200,','[np.asarray(result.x, dtype=float)], None, 200,')),
('M7',lambda:ed(O,'self._energy_cost_fn(h.money_prices, dt),','self._energy_cost_fn(h.prices, dt),')),
('M8',settle),
('M9',lambda:ed(O,'prices=h.money_prices.tolist(),','prices=h.prices.tolist(),')),
('M10',lambda:ed(O,'                raw_prices=raw_prices,\n',''))]
run('M0')
for i,f in ML:
    f()
    d=subprocess.run(['git','diff','--stat'],cwd=W,capture_output=True,text=True).stdout
    print(i,'diff:',d.strip().splitlines()[-1] if d.strip() else 'EMPTY',flush=True)
    run(i)
    subprocess.run(['git','checkout','--','.'],cwd=W)
    assert subprocess.run(['git','status','--porcelain'],cwd=W,capture_output=True,text=True).stdout==''

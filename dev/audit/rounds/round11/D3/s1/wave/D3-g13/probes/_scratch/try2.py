exec(open('/tmp/claude-0/-home-user-heatpump-optimizer/25370d85-7c12-5d31-9bdf-080232e3fc11/scratchpad/preamble.py').read().replace('ROOT = repo_root(__file__)','ROOT = Path.cwd()'))
exec(open('/tmp/claude-0/-home-user-heatpump-optimizer/25370d85-7c12-5d31-9bdf-080232e3fc11/scratchpad/dhw_common.py').read())
F = DhwPlanner._apply_dhw_min_run
def M(o,n): return mutated(dhw_planner, F, o, n)
W1="weak = np.where((plan > 1e-6) & (plan < min_run_power))[0]"
m597=M(W1,"weak = np.where((plan > 1e-6) & (plan <= min_run_power))[0]")
mdf4=M(W1,"weak = np.where((plan >= 1e-6) & (plan < min_run_power))[0]")
m722=M("unchanged: np.ndarray = np.clip(plan, 0.0, p_dhw_max)", "unchanged: np.ndarray = (plan)")
m49d=M("run_power = min(min_run_power, p_dhw_max)", "run_power = (min_run_power)")
z=np.zeros(24)
p=z.copy(); p[5]=MIN_RUN; p[10]=0.2
for kw in (dict(initial=35.0,ceiling=55.0), dict(initial=50.0,ceiling=50.0)):
  print('597 eq',run(p,**kw)[[5,10]], run(p,m597,**kw)[[5,10]])
  q=z.copy(); q[5]=2.0
  print('597 pmax<min', run(q,p_max=1.0,min_run=2.0,**kw)[5], run(q,m597,p_max=1.0,min_run=2.0,**kw)[5])
  q=z.copy(); q[5]=1e-6
  print('df4', run(q,**kw)[5], run(q,mdf4,**kw)[5])
  q=z.copy(); q[5]=3.5; q[6]=-0.5
  print('722', run(q,**kw)[[5,6]], run(q,m722,**kw)[[5,6]])
  q=z.copy(); q[5]=0.3; q[15]=0.3
  print('49d', run(q,p_max=1.0,min_run=2.0,**kw)[[5,15]], run(q,m49d,p_max=1.0,min_run=2.0,**kw)[[5,15]])

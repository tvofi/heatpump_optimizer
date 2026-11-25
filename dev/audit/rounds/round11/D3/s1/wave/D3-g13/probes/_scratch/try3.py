exec(open('/tmp/claude-0/-home-user-heatpump-optimizer/25370d85-7c12-5d31-9bdf-080232e3fc11/scratchpad/preamble.py').read().replace('ROOT = repo_root(__file__)','ROOT = Path.cwd()'))
exec(open('/tmp/claude-0/-home-user-heatpump-optimizer/25370d85-7c12-5d31-9bdf-080232e3fc11/scratchpad/dhw_common.py').read())
print(joint_cases())
F = DhwPlanner._apply_dhw_min_run
m49d=mutated(dhw_planner,F,"run_power = min(min_run_power, p_dhw_max)", "run_power = (min_run_power)")
m597=mutated(dhw_planner,F,"weak = np.where((plan > 1e-6) & (plan < min_run_power))[0]","weak = np.where((plan > 1e-6) & (plan <= min_run_power))[0]")
for nm,fn in (('49d',m49d),('597',m597)):
  mv=0;tot=0
  for seed in range(12):
    for initial, ceiling, draw in ((50.0, 50.0, 1.8), (35.0, 55.0, 0.0), (45.0, 60.0, 3.0), (55.0, 55.0, 0.5)):
      for n,nw in ((24,3),(96,24),(48,10)):
        plan,kw=fixture(n,nw,seed,initial,ceiling,draw)
        plan=np.where(plan>0.55, 1.2, plan)  # strong slots at exactly min_run=1.2 > p_max=1.0
        b=run(plan,p_max=1.0,min_run=1.2,**kw); m=run(plan,fn,p_max=1.0,min_run=1.2,**kw); tot+=1
        mv+= not np.array_equal(b,m)
  print(nm,mv,tot)

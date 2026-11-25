import json,sys
cl=json.load(open(sys.argv[1]))["closures"];P="custom_components/heatpump_optimizer/"
prod={f for fs in cl.values() for f in fs if f.startswith(P)}
for a,b in [("tests/boost_drift_replay.py","tests/config_flow_steps.py"),("tests/config_flow_steps.py","tests/plan_view.py"),("tests/env_drift.py","tests/manual_plan.py"),("tests/golden.py","tests/manual_plan.py")]:
  A=set(cl.get(a,[]))&prod;B=set(cl.get(b,[]))&prod
  print(f"  {a[6:]}/{b[6:]} {len(A&B)}/{len(A|B)}={len(A&B)/len(A|B):.4f}" if A and B else f"  {a}/{b} n/a")

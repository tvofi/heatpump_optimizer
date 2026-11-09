import sys, json, datetime as dt
sys.path.insert(0, sys.argv[1]); import replan as R
caps = dict(R.DEFAULT_CAPS, slots=6, seats=8, coordinator_cap=1)
d = {"sizes_hours": {"S": 2.0, "M": 4.0, "L": 6.0, "XL": 8.0},"live_remaining_fraction": 0.7,"batch_window_minutes": 20,"stamp_lead_minutes": 60,"closure_lead_minutes": 120,
 "ci": {"fast (3.14)": {"median_minutes": 50.0},"closures": {"median_minutes": 22.0},"Analyze (python)": {"median_minutes": 27.0, "cancelled_rate": 0.04}},"provenance": {}}
d.update(first_round_hours=dict(d["sizes_hours"]), review_rounds={k:1.0 for k in d["sizes_hours"]}, round_hours=0.0, carry_part_hours=1.0, carries_per_part=1.0)
F=["custom_components/heatpump_optimizer/coordinator.py"]
def fx(n,size="S",after=(),files=None): return {"group":n,"size":size,"lane":"Core model","kind":"defect","after":list(after),"resume":{"stage":"not-started"},**({"files":files} if files else {})}
ros={"groups":[fx("D","S"),fx("CP1","XL",["D"],F),fx("CP2","XL",["CP1"]),fx("X3","L",files=F)]}
p=R.build_plan(ros,d,caps,dt.datetime(2026,1,5),"v1.0.0",round_n=2)
print("RESULT overlap fixture:", {n:(g["start"],g["finish"],g.get("exempt_coordinator")) for n,g in p["groups"].items()})
print("RESULT check_plan:", R.check_plan(p))

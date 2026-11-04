import sys; sys.path.insert(0,'tests'); import replay as r
s='synthetic-dhw-only.json'
# (job, ref_ms, metric, clean, doubled) from CI cost lines
rows=[("125461180429",23.83,"cpu_ratio",2.5671,5.2086),("125461180429",23.83,"loop_cpu_ratio",0.1282,0.2603),
("125160076828",30.32,"cpu_ratio",2.81,5.701),("125240101580",30.93,"cpu_ratio",2.7543,5.5315),
("125097530406",45.65,"cpu_ratio",2.3246,4.6473),("125316010511",46.36,"cpu_ratio",2.4235,4.7775),
("125530195186-head",46.56,"cpu_ratio",2.3273,4.6962),("125530195186-head",46.56,"loop_cpu_ratio",0.0923,0.1913),
("124414072168",52.76,"cpu_ratio",1.4563,2.8848),("124725704090",53.27,"cpu_ratio",1.451,2.841),("125036077984",52.43,"cpu_ratio",1.4926,2.9251),
("125000687320-refused",28.01,"cpu_ratio",1.8924,3.8922),("123225871060-refused",34.35,"cpu_ratio",1.8747,None)]
for j,x,k,c,d in rows:
    b,ref=r.class_budget(s,x)
    cl=ref[:1] or r.cost_offenders({k:c},b) or "WITHIN"
    dl=None if d is None else (ref[:1] or r.cost_offenders({k:d},b))
    print("RESULT",j,x,k,"clean",c,"->",cl,"| doubled",d,"->",dl)
print("RESULT memory-doubled ref24", r.cost_offenders({"peak_kib":3860.7}, r.class_budget(s,24.31)[0]))
print("RESULT owner ref24", r.cost_offenders({"cpu_ratio":269.8155}, r.class_budget("owner-2026-10-30-away.json",24.06)[0]) or "WITHIN")
for x in (float('nan'),0.0,-1.0,float('inf'),22.63,25.54,28.71,32.70,42.98,49.52,49.55,56.79):
    print("RESULT probe",x, r.class_budget(s,x)[1][:1] or "ADMITTED")

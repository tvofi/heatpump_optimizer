import sys, yaml, voluptuous as vol
sys.path.insert(0, "custom_components")
from heatpump_optimizer import services as S
cat = yaml.safe_load(open("custom_components/heatpump_optimizer/services.yaml"))
schemas = {n[len("SERVICE_SCHEMA_"):].lower(): getattr(S, n) for n in dir(S) if n.startswith("SERVICE_SCHEMA_")}; schemas["set_thermal_parameters"] = S.SERVICE_SCHEMA_SET_THERMAL_PARAMS
def fields(sch):
    while not hasattr(sch, "schema") or not isinstance(sch.schema, dict):
        sch = next(v for v in sch.validators if isinstance(v, (vol.Schema, dict, vol.All)))
        if isinstance(sch, dict): sch = vol.Schema(sch)
    return {str(getattr(k, "schema", k)): v for k, v in sch.schema.items()}
opn = 0
for svc, body in cat.items():
    sch = schemas.get(svc)
    if sch is None:
        print("NO-SCHEMA", svc); continue
    fs = fields(sch)
    for f, spec in ((body or {}).get("fields") or {}).items():
        num = ((spec or {}).get("selector") or {}).get("number")
        if num is None: continue
        lo, hi, st = num.get("min"), num.get("max"), num.get("step", 1)
        if st == "any": st = 1
        for p in (lo - st, hi + st):
            try:
                vol.Schema(fs[f])(p); print(f"OPEN {svc}.{f} accepts {p} (selector {lo}..{hi})"); opn += 1
            except vol.Invalid: pass
            except KeyError: print("NOFIELD", svc, f)
print("open probes:", opn)

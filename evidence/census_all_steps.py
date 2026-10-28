"""Reviewer-built census (not the finder's): every config-flow step that renders a
form with no input; each field whose key has an _OPTION_FIELDS row must carry
that row's widget object."""
import asyncio, sys, os
sys.path.insert(0, "tests"); sys.path.insert(0, os.getcwd())
import types
T = types.ModuleType('cfs'); T.__file__='tests/config_flow_steps.py'
_src=open('tests/config_flow_steps.py').read().replace('sys.exit(asyncio.run(main()))','')
exec(compile(_src,'tests/config_flow_steps.py','exec'), T.__dict__)
cf = T.config_flow
import voluptuous as vol
def _leaves(schema):
    for m, v in schema.schema.items():
        inner = getattr(v, 'schema', None)
        if isinstance(inner, vol.Schema): yield from _leaves(inner)
        else: yield m, v

async def main():
    flow = cf.HeatPumpOptimizerConfigFlow(); flow.hass = T.FakeHass()
    flow._reauth_entry = None
    steps = sorted(n[len("async_step_"):] for n in dir(flow) if n.startswith("async_step_"))
    total = bad = 0; badl = []; unrendered = []
    for s in steps:
        try:
            r = await getattr(flow, f"async_step_{s}")()
        except Exception as e:
            unrendered.append(f"{s}:{type(e).__name__}"); continue
        sch = r.get("data_schema") if isinstance(r, dict) else None
        if sch is None: unrendered.append(f"{s}:{r.get('type') if isinstance(r,dict) else r}"); continue
        for m, w in _leaves(sch):
            rows = [x for x in cf._OPTION_FIELDS if x.key == str(m)]
            if not rows: continue
            total += 1
            if not any(w is x.widget for x in rows): bad += 1; badl.append(f"{s}:{m}")
    print("steps", steps); print("unrendered", unrendered)
    print(f"RESULT all_steps_registry_fields={total} count"); print(f"RESULT all_steps_spelled_twice={bad} count {badl}")
asyncio.run(main())

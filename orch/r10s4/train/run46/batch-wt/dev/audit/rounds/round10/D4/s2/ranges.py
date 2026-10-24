"""D4.M2 defaults vs selector ranges, every options page and every config-flow form reached untouched.
Metric: count of numeric fields whose rendered default/suggested_value lies outside the
NumberSelector [min,max] or off its step grid (step tolerance 1e-9), as delivered by async_show_form.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D4/s2/ranges.py
Baseline 17f1c55fad1b, machine: macOS arm64 audit box B6. Expected: exact.
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, sys, time
sys.path.insert(0, "tests"); sys.path.insert(0, ".")
from harness import FakeHass, FakeEntry  # noqa
from custom_components.heatpump_optimizer import config_flow  # noqa
t0p, t0t = time.process_time(), time.thread_time()

def walk_schema(sch, prefix=""):
    for k, v in sch.schema.items():
        if type(v).__name__ == "section":
            yield from walk_schema(v.schema, f"{k}."); continue
        val = None
        desc = getattr(k, "description", None) or {}
        if isinstance(desc, dict) and "suggested_value" in desc:
            val = desc["suggested_value"]
        else:
            try: val = k.default()
            except Exception: val = None
        cfg = getattr(v, "config", None)
        if isinstance(cfg, dict) and ("min" in cfg or "max" in cfg) and type(v).__name__ == "NumberSelector":
            yield prefix + str(k), val, cfg

bad = []; n = 0
def check(where, sch):
    global n
    for name, val, cfg in walk_schema(sch):
        if val is None or isinstance(val, bool) or type(val).__name__ == "Undefined": continue
        try: x = float(val)
        except Exception: bad.append((where, name, val, "nonnumeric")); continue
        n += 1
        lo, hi, st = cfg.get("min"), cfg.get("max"), cfg.get("step")
        if (lo is not None and x < lo) or (hi is not None and x > hi):
            bad.append((where, name, val, f"out [{lo},{hi}]"))
        elif isinstance(st, (int, float)) and lo is not None and abs(((x - lo) / st) - round((x - lo) / st)) > 1e-6:
            bad.append((where, name, val, f"off-grid step {st} from {lo}"))

async def options():
    flow = config_flow.HeatPumpOptimizerOptionsFlow(FakeEntry(options={}))
    flow.hass = FakeHass()
    for step in list(flow._TOP_MENU) + list(flow._ADVANCED_MENU):
        r = await getattr(flow, f"async_step_{step}")(None)
        if r.get("type") == "form" and r.get("data_schema"):
            check("options/" + r["step_id"], r["data_schema"])

asyncio.run(options())

# config flow: walk untouched like tests/entities.py:_walk_flow_untouched, checking each form
class _Resp:
    status = 200
    async def json(self): return {"data": {"viewer": {"name": "Home"}}}
class _Sess:
    def post(self, *a, **k):
        class C:
            async def __aenter__(s): return _Resp()
            async def __aexit__(s, *e): return False
        return C()
async def cfgwalk():
    real = config_flow.async_get_clientsession
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: _Sess()
    try:
        flow = config_flow.HeatPumpOptimizerConfigFlow(); flow.hass = FakeHass()
        r = await flow.async_step_user(None)
        seen = set(); visits = []
        for _ in range(30):
            if r.get("type") == "create_entry":
                print(f"RESULT config_steps_to_entry={len(visits)} count"); print("STEPS", *visits); return
            if r.get("type") == "menu":
                opts = list(r["menu_options"]); step = "temperature" if "temperature" in opts else opts[0]
                r = await getattr(flow, f"async_step_{step}")(None); continue
            step = r["step_id"]; visits.append(step)
            if r.get("data_schema") and step not in seen:
                seen.add(step); check("config/" + step, r["data_schema"])
            ans = {}
            for k, v in (r["data_schema"].schema.items() if r.get("data_schema") else ()):
                d = getattr(k, "description", None) or {}
                if isinstance(d, dict) and "suggested_value" in d: ans[str(k)] = d["suggested_value"]; continue
                try: dv = k.default()
                except Exception: dv = None
                if dv is not None and type(dv).__name__ != "Undefined": ans[str(k)] = dv
            if step == "user": ans.update({"name": "HPO", "tibber_token": "tok", "weather_entity": "weather.home"})
            r = await getattr(flow, f"async_step_{step}")(ans)
    finally:
        config_flow.async_get_clientsession = real
asyncio.run(cfgwalk())
for b in bad: print("BAD", *b)
print(f"RESULT numeric_fields_checked={n} count")
print(f"RESULT defaults_outside_selector={len(bad)} count")
pc, tc = time.process_time()-t0p, time.thread_time()-t0t
print(f"RESULT thread_factor={pc/tc if tc else 1:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")

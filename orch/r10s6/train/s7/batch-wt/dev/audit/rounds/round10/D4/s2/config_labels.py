"""D4.M2 config-flow (install) form label/help coverage.
Metric: fields (sections recursed) on each config-flow form reached by the untouched install walk
whose key lacks a label or data_description under config.step.<id> in strings/en/sv.
Count key: field key delivered by async_show_form's data_schema.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D4/s2/config_labels.py
Baseline 17f1c55fad1b, machine: macOS arm64 audit box B6. Expected: exact.
Perturbation: delete one key from strings.json config.step.user.data -> missing_label_strings up by 1.
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, json, sys, time
from pathlib import Path
sys.path.insert(0, "tests"); sys.path.insert(0, ".")
from harness import FakeHass  # noqa
from custom_components.heatpump_optimizer import config_flow  # noqa
ROOT = Path("custom_components/heatpump_optimizer")
LANGS = {n: json.loads(p.read_text()) for n, p in (("strings", ROOT/"strings.json"), ("en", ROOT/"translations/en.json"), ("sv", ROOT/"translations/sv.json"))}
t0p, t0t = time.process_time(), time.thread_time()
forms = {}
class _Resp:
    status = 200
    async def json(self): return {"data": {"viewer": {"name": "Home"}}}
class _Sess:
    def post(self, *a, **k):
        class C:
            async def __aenter__(s): return _Resp()
            async def __aexit__(s, *e): return False
        return C()
def fields(sch):
    for k, v in sch.schema.items():
        if type(v).__name__ == "section":
            yield ("section", str(k))
            for kk in v.schema.schema: yield (str(k), str(kk))
        else: yield (None, str(k))
async def walk(first_menu_pick):
    real = config_flow.async_get_clientsession
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: _Sess()
    try:
        flow = config_flow.HeatPumpOptimizerConfigFlow(); flow.hass = FakeHass()
        r = await flow.async_step_user(None)
        for _ in range(30):
            if r.get("type") in ("create_entry", "abort"): return
            if r.get("type") == "menu":
                opts = list(r["menu_options"]); step = first_menu_pick(opts)
                r = await getattr(flow, f"async_step_{step}")(None); continue
            step = r["step_id"]
            if r.get("data_schema"): forms.setdefault(step, list(fields(r["data_schema"])))
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
asyncio.run(walk(lambda o: "temperature" if "temperature" in o else o[0]))
asyncio.run(walk(lambda o: o[-1]))
asyncio.run(walk(lambda o: o[min(1, len(o)-1)]))
miss = {l: [0, 0] for l in LANGS}
for step, fl in forms.items():
    print("FORM", step, len([f for f in fl if f[0] != "section"]))
    for lang, d in LANGS.items():
        st = d["config"]["step"].get(step, {})
        for sec, f in fl:
            if sec == "section":
                if "name" not in st.get("sections", {}).get(f, {}): miss[lang][0] += 1; print("MISSING", lang, step, f, "section")
                continue
            blk = st if sec is None else st.get("sections", {}).get(sec, {})
            if f not in blk.get("data", {}): miss[lang][0] += 1; print("MISSING", lang, step, f, "label")
            if f not in blk.get("data_description", {}): miss[lang][1] += 1; print("MISSING", lang, step, f, "help")
print(f"RESULT config_forms={len(forms)} count")
for l, (a, b) in miss.items():
    print(f"RESULT missing_label_{l}={a} count"); print(f"RESULT missing_help_{l}={b} count")
pc, tc = time.process_time()-t0p, time.thread_time()-t0t
print(f"RESULT thread_factor={pc/tc if tc else 1:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")

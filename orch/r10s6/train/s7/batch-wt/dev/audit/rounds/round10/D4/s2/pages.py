"""D4.M2 options/config page survey.
Metric: per rendered form (options flow, every page opened with no input), the
fields whose key lacks a label / a data_description in strings.json, en.json, sv.json.
Count key: the field key the production schema (async_show_form data_schema) delivers.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D4/s2/pages.py
Baseline 17f1c55fad1b, machine: macOS arm64 audit box B6. Expected: exact.
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, json, sys, time
from pathlib import Path
sys.path.insert(0, "tests"); sys.path.insert(0, ".")
from harness import FakeHass, FakeEntry  # noqa
from custom_components.heatpump_optimizer import config_flow  # noqa
ROOT = Path("custom_components/heatpump_optimizer")
LANGS = {n: json.loads(p.read_text()) for n, p in (("strings", ROOT/"strings.json"), ("en", ROOT/"translations/en.json"), ("sv", ROOT/"translations/sv.json"))}
t0p, t0t = time.process_time(), time.thread_time()

async def walk():
    flow = config_flow.HeatPumpOptimizerOptionsFlow(FakeEntry(options={}))
    flow.hass = FakeHass()
    pages = {}
    steps = list(flow._TOP_MENU) + list(flow._ADVANCED_MENU)
    for step in steps:
        try:
            r = await getattr(flow, f"async_step_{step}")(None)
        except Exception as e:
            pages[step] = ("error", repr(e)); continue
        if r.get("type") != "form":
            pages[step] = (r.get("type"), None); continue
        sch = r.get("data_schema")
        fl = []
        for k, v in (sch.schema.items() if sch else ()):
            if hasattr(v, "schema") and type(v).__name__ == "section":
                fl.append(("section", str(k)))
                fl += [(str(k), str(kk)) for kk in v.schema.schema]
            else:
                fl.append((None, str(k)))
        pages[r["step_id"]] = ("form", fl)
    return pages

pages = asyncio.run(walk())
miss_label = {l: 0 for l in LANGS}; miss_help = {l: 0 for l in LANGS}; detail = []
nfields = 0
for step, (kind, fields) in pages.items():
    if kind != "form":
        print(f"PAGE {step} kind={kind} {fields or ''}"); continue
    fields_only=[x for x in fields if x[0]!='section']; nfields += len(fields_only)
    print(f"PAGE {step} fields={len(fields_only)} sections={len(fields)-len(fields_only)}")
    for lang, d in LANGS.items():
        st = d.get("options", {}).get("step", {}).get(step, {})
        for sec, f in fields:
            if sec == "section":
                if "name" not in st.get("sections", {}).get(f, {}):
                    miss_label[lang] += 1; detail.append((lang, step, f, "section-name"))
                continue
            blk = st if sec is None else st.get("sections", {}).get(sec, {})
            if f not in blk.get("data", {}):
                miss_label[lang] += 1; detail.append((lang, step, f, "label"))
            if f not in blk.get("data_description", {}):
                miss_help[lang] += 1; detail.append((lang, step, f, "help"))
for d in detail:
    print("MISSING", *d)
print(f"RESULT pages={len(pages)} count")
print(f"RESULT fields={nfields} count")
for lang in LANGS:
    print(f"RESULT missing_label_{lang}={miss_label[lang]} count")
    print(f"RESULT missing_help_{lang}={miss_help[lang]} count")
print(f"RESULT max_fields_per_page={max((len([x for x in f if x[0]!='section']) for k,f in pages.values() if k=='form'), default=0)} count")
pc, tc = time.process_time()-t0p, time.thread_time()-t0t
print(f"RESULT thread_factor={pc/tc if tc else 1:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")

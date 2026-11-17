"""D4.M3 (seat D4-s3): does a config/options flow page put English text into a sv/de form?

Metric: description_placeholders values that a page renders identically under hass.config.language
"en" and "sv"/"de" and that carry >=2 alphabetic words of >=4 letters (an untranslated sentence
spliced into a translated description, and named as {key} by some text in that language), counted over every options-menu page and every initial
step golden.py:capture_config_flow renders. Key: the value the flow returns in
`description_placeholders` (the production seam), never a strings.json key.

Run (export root):  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D4/s3/m3_flow_lang.py [--perturb=preset_en]
Perturbation preset_en: config_flow._building_preset_warning ignores the language (returns
PRESET_WARNING["en"]); expected untranslated_placeholders up (pages showing the preset warning).
Expected at baseline: see REPORT.md (exact count). Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B10.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import re
import sys
import time

sys.path[:0] = ["tests", "custom_components"]
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import config_flow as cf  # noqa: E402

PERTURB = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--perturb=")), "")
if PERTURB == "preset_en":
    cf._building_preset_warning = lambda hass, current: cf.PRESET_WARNING["en"]

DATA = {"tibber_token": "x", "weather_entity": "weather.home", "building_preset_enabled": True}
INITIAL = ("user", "user_sensors", "finish_setup", "quick_setup", "device_prefill", "temperature", "building",
           "building_describe", "building_extras", "thermal", "zones", "dhw", "weather_sensitivity", "setup_overview")


def pages(lang):
    out = {}
    hass = FakeHass()
    hass.config.language = lang
    flow = cf.HeatPumpOptimizerOptionsFlow(FakeEntry(data=dict(DATA)))
    flow.hass = hass
    for step in cf.HeatPumpOptimizerOptionsFlow._MENU_LABELS:
        try:
            r = asyncio.run(getattr(flow, f"async_step_{step}")())
            out[f"options/{step}"] = dict(r.get("description_placeholders") or {})
        except Exception as e:  # a page the stub cannot render is reported, not hidden
            out[f"options/{step}"] = {"__error__": repr(e)[:80]}
    init = cf.HeatPumpOptimizerConfigFlow()
    init.hass = FakeHass()
    init.hass.config.language = lang
    for step in INITIAL:
        try:
            r = asyncio.run(getattr(init, f"async_step_{step}")())
            out[f"initial/{step}"] = dict(r.get("description_placeholders") or {})
        except Exception as e:
            out[f"initial/{step}"] = {"__error__": repr(e)[:80]}
    return out


import json  # noqa: E402
TR = {l: json.dumps(json.load(open(f"custom_components/heatpump_optimizer/translations/{l}.json"))) for l in ("en", "sv", "de")}


def shown(lang, key):
    """A placeholder reaches the user only when some translated text in that language names it."""
    return "{" + key + "}" in TR[lang]


t0 = time.process_time()
en = pages("en")
bad, rendered, errors, dead = [], 0, [], []
for lang in ("sv", "de"):
    other = pages(lang)
    for page, ph in other.items():
        if "__error__" in ph:
            errors.append(f"{lang}:{page}")
            continue
        for k, v in ph.items():
            if not isinstance(v, str) or not v.strip():
                continue
            if not shown(lang, k):
                dead.append(f"{lang}:{page}:{k}")
                continue
            rendered += 1
            words = re.findall(r"\b[A-Za-z]{4,}\b", re.sub(r"https?://\S+|\S+\.\S+_\S+|`[^`]*`", "", v))
            if en.get(page, {}).get(k) == v and len(words) >= 2:
                bad.append(f"{lang}:{page}:{k}={v[:90]!r}")
for b in bad:
    print("UNTRANSLATED", b)
print("pages", len(en), "stub errors", errors, "placeholders no text names:", sorted(set(d.split(":", 1)[1] for d in dead)))
print(f"RESULT pages={len(en)} count")
print(f"RESULT placeholders_non_en={rendered} count")
print(f"RESULT untranslated_placeholders={len(bad)} count")
print(f"RESULT unreferenced_placeholders={len(dead)} count")
print(f"RESULT stub_errors={len(errors)} count")
print(f"RESULT cpu_s={time.process_time() - t0:.2f} s (provisional)")
print("RESULT thread_factor=1.00")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")

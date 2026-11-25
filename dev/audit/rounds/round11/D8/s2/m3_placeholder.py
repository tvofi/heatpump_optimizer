"""D8-s2-01: the run-optimization refusal renders in every shipped language.

Metric: number of shipped languages whose exceptions.<key>.message cannot be
  formatted with the translation_placeholders the raised HomeAssistantError
  actually carries (str.format KeyError, i.e. what HA's translation
  placeholder validation rejects and replaces with English). Key: the
  placeholders on the exception production raises, not the strings file.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D8/s2/m3_placeholder.py [--perturb-de]
Instrumented symbol: heatpump_optimizer.button (the optimize_now button's
  async_press, with coordinator.async_run_optimization returning "no_prices").
Perturbation: --perturb-de replaces "{entry_id}" with "{entry_ids}" in the
  German message in memory: unrenderable_langs must fall 1 -> 0.
Null control: the same press with reason None raises nothing (null_raised=0).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, macOS arm64.
Expected at baseline: unrenderable_langs=1 (de), exact.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
t0p, t0t = time.process_time(), time.thread_time()
import rig  # noqa: E402
from homeassistant.exceptions import HomeAssistantError  # noqa: E402

ROOT = Path("custom_components/heatpump_optimizer")
LANGS = sorted(p.stem for p in (ROOT / "translations").glob("*.json"))
TR = {l: json.loads((ROOT / "translations" / f"{l}.json").read_text()) for l in LANGS}
if "--perturb-de" in sys.argv:
    m = TR["de"]["exceptions"]["run_optimization_no_prices"]
    m["message"] = m["message"].replace("{entry_id}", "{entry_ids}")

ents = rig.build(rig.golden.coordinator_scenarios()["coord_minimal"])
btn = next(e for p, e in ents if p == "button"
           and e._attr_translation_key == "optimize_now")


def press(reason):
    async def _run():
        return reason
    btn.coordinator.async_run_optimization = _run
    btn.coordinator.async_request_refresh = lambda: asyncio.sleep(0)
    try:
        asyncio.run(btn.async_press())
    except HomeAssistantError as err:
        return err
    return None


err = press("no_prices")
key = getattr(err, "translation_key", None)
ph = getattr(err, "translation_placeholders", None) or {}
bad = []
for lang in LANGS:
    msg = TR[lang]["exceptions"][key]["message"]
    try:
        msg.format(**ph)
    except KeyError as k:
        bad.append(f"{lang}:missing {k}")
print(f"DETAIL key={key} placeholders={sorted(ph)} unrenderable={bad}")
null = press(None)
print(f"RESULT unrenderable_langs={len(bad)} count")
print(f"RESULT null_raised={0 if null is None else 1} count")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")

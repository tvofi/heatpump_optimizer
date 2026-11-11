"""V2 probe for D7-arch2-06: what a rejected options form re-renders in a slot the user cleared.

Metric: stale_slots = _STORED entity rows on page `entities` whose re-rendered marker carries the
STORED entity as suggested_value after a submit that cleared them (key absent from user_input),
using the baseline re-render input {**current, **user_input} (config_flow.py async_step_entities)
versus the patch-08 re-render input {**current, **_clear_absent(flat, step, merged)}.
Null control: a submit that leaves every slot as stored (nothing cleared) -> rows_shown_differently 0
(all 9 slots show the stored entity in both arms).
Run (from a tree root): PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/arch-s2/probe_rerender.py
Expected at 554e2ecfa: baseline stale_slots = number of stored entity rows cleared; patched 0.
Machine: shared macOS box; counts only. Imports the working tree's package read-only.
"""
import os, sys
from pathlib import Path
here = Path(__file__).resolve()
root = next(c for c in here.parents if (c / "custom_components/heatpump_optimizer/manifest.json").is_file())
sys.path.insert(0, str(root / "custom_components")); sys.path.insert(0, str(root / "tests"))
from heatpump_optimizer import config_flow as cf
from harness import FakeHass
hass = FakeHass({})
STEP = "entities"
rows = [r for r in cf._page_rows(STEP, {}) if r.default is cf._STORED]
current = {r.key: f"sensor.stored_{i}" for i, r in enumerate(rows)}
def suggested(schema, key):
    for m in schema.schema:
        if getattr(m, "schema", m) == key:
            return (getattr(m, "description", None) or {}).get("suggested_value")
        inner = cf._section_inner(schema.schema[m])
        if inner is not None:
            got = suggested(inner, key)
            if got is not None:
                return got
    return None
def stale(shown, cleared):
    sch = cf._page_schema(STEP, shown, hass)
    return sum(1 for k in cleared if suggested(sch, k) == current[k])
for label, cleared in (("clear_all", [r.key for r in rows]), ("null_nothing_cleared", [])):
    user_input = {k: v for k, v in current.items() if k not in cleared}
    base_shown = {**current, **user_input}
    merged = {**current, **user_input}
    patch_shown = {**current, **cf._clear_absent(user_input, STEP, merged)}
    print(f"RESULT {label}_stored_rows={len(rows)} count")
    print(f"RESULT {label}_baseline_stale_slots={stale(base_shown, cleared)} count")
    print(f"RESULT {label}_patched_stale_slots={stale(patch_shown, cleared)} count")
    allk = [r.key for r in rows]
    print(f"RESULT {label}_rows_shown_differently={stale(base_shown, allk) - stale(patch_shown, allk)} count")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")

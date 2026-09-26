"""D10 verify-v2 for D10-s2-01: are the climate entity's published preset_mode values translatable?

Metric: over the distinct preset_mode values the production property
climate:HeatPumpOptimizerClimate.preset_mode publishes while coordinator.mode is
driven through every const MODE_* value, count values that are neither an
HA-standard climate preset (core climate/const.py PRESET_*: none, eco, away,
boost, comfort, home, sleep, activity -- hard-coded, no HA core in this venv)
nor present under ANY entity.climate.<key>.state_attributes.preset_mode.state
table of the file (looser than binding to the entity's translation_key).
Reported per file: strings.json, translations/en.json, translations/sv.json,
and icons.json (entity.climate.*.state_attributes.preset_mode.state).
Also: values of those that the integration DOES translate for another entity
(entity.sensor.optimization_mode.state) -- words available, not wired.
Count key: the value the production preset_mode property returns.
Perturbation: --perturb economy_eco swaps coordinator mode 'economy' for the
published preset value 'eco' via mock.patch.object on the class attribute
_attr_preset_modes and a property wrapper mapping economy->eco -> count 2 -> 1.
Run: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D10/verify-v2/preset_lookup.py [--perturb economy_eco]
Expected baseline: untranslatable=2 in each of 4 files (+-0); economy_eco: 1.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G2-V2 cloud container, 4 cores, CPython 3.14.0rc2.
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, json, sys, time  # noqa: E402
from pathlib import Path  # noqa: E402
from unittest import mock  # noqa: E402
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import climate, const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
PERTURB = "economy_eco" in sys.argv
STD = {"none", "eco", "away", "boost", "comfort", "home", "sleep", "activity"}
P = Path("custom_components/heatpump_optimizer")
files = {"strings": P / "strings.json", "en": P / "translations/en.json",
         "sv": P / "translations/sv.json", "icons": P / "icons.json"}


def any_climate_preset_keys(d):
    out = set()
    for tk in (d.get("entity", {}).get("climate", {}) or {}).values():
        out |= set(((tk.get("state_attributes", {}) or {}).get("preset_mode", {}) or {}).get("state", {}) or {})
    return out


async def main():
    hass = FakeHass(); hass.states.set("sensor.indoor", FakeState("21.0"))
    entry = FakeEntry(data={const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor"})
    c = HeatPumpOptimizerCoordinator(hass, entry); entry.runtime_data = c
    ps = []
    if PERTURB:
        cls = climate.HeatPumpOptimizerClimate
        orig = cls.preset_mode.fget
        ps = [mock.patch.object(cls, "_attr_preset_modes", ["auto", "comfort", "eco", "boost"]),
              mock.patch.object(cls, "preset_mode", property(lambda self: "eco" if self.coordinator.mode == "economy" else orig(self)))]
    for p in ps: p.start()
    added = []
    await climate.async_setup_entry(hass, entry, lambda es, *a, **k: added.extend(es))
    ent = next(e for e in added if isinstance(e, climate.HeatPumpOptimizerClimate))
    modes = sorted({getattr(const, n) for n in dir(const) if n.startswith("MODE_") and isinstance(getattr(const, n), str) and n.count("_") == 1})
    published = set()
    for m in modes:
        c._mode = m
        v = ent.preset_mode
        print(f"coordinator.mode={m:8s} -> preset_mode={v!r}")
        if v is not None: published.add(v)
    for p in ps: p.stop()
    custom = sorted(published - STD)
    print(f"published={sorted(published)} non_standard={custom} translation_key={getattr(ent, '_attr_translation_key', None)!r}")
    for name, path in files.items():
        keys = any_climate_preset_keys(json.loads(path.read_text()))
        miss = [v for v in custom if v not in keys]
        print(f"RESULT untranslatable_{name}={len(miss)} count ({','.join(miss)})")
    en = json.loads(files["en"].read_text())
    avail = [v for v in custom if v in en.get("entity", {}).get("sensor", {}).get("optimization_mode", {}).get("state", {})]
    print(f"RESULT translated_for_other_entity={len(avail)} count ({','.join(avail)})")
    print(f"MODE {'economy_eco' if PERTURB else 'baseline'}")

t0p, t0t = time.process_time(), time.thread_time()
asyncio.run(main())
dp, dt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp/dt if dt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + next(l.split()[1] for l in open('/proc/vmstat') if l.startswith('pswpin')))
except Exception:
    print("RESULT swapins=unknown")

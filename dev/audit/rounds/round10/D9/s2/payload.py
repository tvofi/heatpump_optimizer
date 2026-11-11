"""D9.M1 payload bytes (round 10, seat D9-s2).

Metric: JSON bytes of coordinator._build_data_dict() and of every
enabled-by-default entity's extra_state_attributes after one solved cycle,
split into attributes the recorder keeps (not in the class's
_unrecorded_attributes) and attributes it drops; per cycle, and per day at the
default 30-min optimization interval (48 cycles/day, an upper bound: the
recorder writes a row only when state or attributes change).
Key: bytes of json.dumps(value, default=str, separators=(",", ":")) per attribute
key, as delivered by the entity's extra_state_attributes property.

Command (repo root):
  PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python \
      dev/audit/rounds/round10/D9/s2/payload.py [--config coord_all_features] [--horizon-hours 48]
Perturbation: --drop-unrecorded-guard
(treats every _unrecorded_attributes as empty) must raise recorded_bytes_per_cycle
from 3476 to 87934. (--horizon-hours does not move it: the horizon is padded.)
Expected (17f1c55fad1b, MacBook arm64, coord_all_features, 48 h): see REPORT.md, tolerance +-2 %.
Counts/bytes are final (contention-immune).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import json
import sys
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

ap = argparse.ArgumentParser()
ap.add_argument("--config", default="coord_all_features")
ap.add_argument("--horizon-hours", type=int, default=48)
ap.add_argument("--cycles", type=int, default=2)
ap.add_argument("--drop-unrecorded-guard", action="store_true")
ap.add_argument("--top", type=int, default=12)
args = ap.parse_args()

t_cpu0, t_thr0 = time.process_time(), time.thread_time()

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
import importlib  # noqa: E402

START = golden.START
H = args.horizon_hours


def nbytes(v):
    return len(json.dumps(v, default=str, separators=(",", ":")))


def registry_default(entity):
    v = getattr(entity, "entity_registry_enabled_default", None)
    if v is None:
        v = getattr(entity, "_attr_entity_registry_enabled_default", True)
    return v is not False


cfg = dict(golden.coordinator_scenarios()[args.config])
dt_util.freeze(START)
hass = FakeHass()
entry = FakeEntry(data=cfg)
coord = HeatPumpOptimizerCoordinator(hass, entry)
coord._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                  "starts_at": (START + timedelta(hours=h)).isoformat(),
                  "level": "NORMAL"} for h in range(H)]
coord._weather_forecast = [{"datetime": (START + timedelta(hours=h)).isoformat(),
                            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
                            "wind_speed": 3.0, "precipitation": 0.0,
                            "humidity": 85.0} for h in range(H)]
coord._solar_radiation_forecast = [max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0))
                                   for h in range(H)]


async def run():
    await coord._update_current_state()
    coord.data = coord._build_data_dict()
    for _ in range(args.cycles - 1):
        await coord._update_current_state()
        await coord.async_run_optimization()
        coord.data = coord._build_data_dict()

asyncio.run(run())
data = coord.data
entry.runtime_data = coord

rows = []  # (entity, key, bytes, recorded)
entities = 0
for name in ("sensor", "binary_sensor", "climate", "switch", "number",
             "select", "button", "datetime", "time"):
    try:
        mod = importlib.import_module(f"heatpump_optimizer.{name}")
    except ImportError:
        continue
    if not hasattr(mod, "async_setup_entry"):
        continue
    added = []

    def add(ents, *_a, **_k):
        for e in ents:
            e.hass = hass
        added.extend(ents)
    try:
        asyncio.run(mod.async_setup_entry(hass, entry, add))
    except Exception as exc:  # noqa: BLE001
        print(f"# platform {name} setup failed: {exc!r}")
        continue
    for ent in added:
        if not registry_default(ent):
            continue
        entities += 1
        unrec = set() if args.drop_unrecorded_guard else set(
            getattr(type(ent), "_unrecorded_attributes", frozenset())
            | getattr(type(ent), "_entity_component_unrecorded_attributes", frozenset()))
        try:
            attrs = ent.extra_state_attributes or {}
        except Exception as exc:  # noqa: BLE001
            print(f"# {type(ent).__name__} attrs raised {exc!r}")
            continue
        for k, v in attrs.items():
            rows.append((type(ent).__name__, k, nbytes(v), k not in unrec))

dt_util.freeze(None)
rec = sum(r[2] for r in rows if r[3])
unr = sum(r[2] for r in rows if not r[3])
print("# largest RECORDED attributes (entity.key bytes):")
for r in sorted((r for r in rows if r[3]), key=lambda r: -r[2])[:args.top]:
    print(f"#   {r[0]}.{r[1]} {r[2]}")
print("# largest UNRECORDED attributes:")
for r in sorted((r for r in rows if not r[3]), key=lambda r: -r[2])[:6]:
    print(f"#   {r[0]}.{r[1]} {r[2]}")
print(f"RESULT data_dict_bytes={nbytes(data)} bytes")
print(f"RESULT data_dict_keys={len(data)} count")
print(f"RESULT entities_enabled_default={entities} count")
print(f"RESULT recorded_bytes_per_cycle={rec} bytes")
print(f"RESULT unrecorded_bytes_per_cycle={unr} bytes")
print(f"RESULT recorded_share={rec / max(1, rec + unr):.4f} ratio")
print(f"RESULT recorded_bytes_per_day_upper={rec * 48} bytes")
tf = (time.process_time() - t_cpu0) / max(1e-9, time.thread_time() - t_thr0)
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=n/a")

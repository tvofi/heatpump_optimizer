#!/usr/bin/env python3
"""D15-s2 harness, D15.M5 (timeline replay, stores seeded): do the seeded
stores' entity ids resolve in the replay half they are replayed against?

Metrics (one line each):
  unresolved_id_leaves: string leaves of the bundle's store documents shaped
      as an entity id (domain.object_id) that name no entity of the replay
      half (neither a ``states`` key nor a value of its entry data/options).
  voided_learners: learners ``HeatPumpOptimizerCoordinator._void_heat_loss_learners``
      voids while ``debug_replay.run_seeded`` sets the coordinator up from the
      seeded stores and runs the window's first cycle.
  learned_samples_lost: house_heat_loss_samples + lower_floor_loss_samples the
      seeded thermal_learning store carries minus what the coordinator holds
      after that first cycle (the learned evidence the replay throws away).
Property: every entity id a seeded store leaf names resolves in the replay
half, so the replayed coordinator starts from the install's learned state.
Rule enumerating the seams: this harness's ``--list`` (each unresolved leaf by
store name and path; the id itself is never printed).
Count key: ``voided_learners`` is keyed on the production void path's calls,
``learned_samples_lost`` on the coordinator's own counters after load; neither
on the store text alone.

Run (from the export root):
    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/rounds/round11/D15/s2/m5_seed_ids.py --bundle B
    ... --list            # the seams: each unresolved leaf (store name, path)
    ... --remap-zones     # perturbation: the zone leaves rewritten to the replay
                          # entry's own ids for the same keys -> voided_learners 0
Null control: the synthetic bundle (tools/replay/dbg_bundle_gen.py --days 1),
whose stores the same replay wrote: unresolved 0, voided 0.
Expected on the owner's 2026-11-16 download at 92d38ecb: unresolved_id_leaves
>= 3, voided_learners=2 (house_heat_loss_scale, lower_floor_loss_ratio);
--remap-zones: voided_learners=0.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: owner's macOS box (B8).
Privacy: prints counts, store names and leaf paths only.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import contextlib  # noqa: E402
import copy  # noqa: E402
import io  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from pathlib import Path  # noqa: E402
from unittest import mock  # noqa: E402

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components",
           ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import debug_ingest  # noqa: E402
import debug_replay  # noqa: E402

ENTITY_ID = re.compile(
    r"^(sensor|binary_sensor|switch|number|select|climate|weather|water_heater|button|"
    r"datetime|input_number|input_boolean|input_select|input_datetime|calendar|person|"
    r"device_tracker|zone|light|fan|valve)\.[a-z0-9_]+$")
ZONE_KEYS = {"indoor_temp_entity": "indoor_temp_entity",
             "lower_floor_temp_entity": "lower_floor_temp_entity"}


def id_leaves(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from id_leaves(v, f"{path}/{k}")
    elif isinstance(node, list):
        for v in node:
            yield from id_leaves(v, f"{path}/#")
    elif isinstance(node, str) and ENTITY_ID.match(node):
        yield path, node


def unresolved(stores: dict, replay_doc: dict) -> list[tuple[str, str, str]]:
    from heatpump_optimizer import store as store_mod
    entry = replay_doc.get("entry") or {}
    known = set(replay_doc.get("states") or {}) | {
        v for v in {**(entry.get("data") or {}), **(entry.get("options") or {})}.values()
        if isinstance(v, str)}
    out = []
    for key, document in stores.items():
        name = store_mod.store_name(key) or "?"
        for path, value in id_leaves(document):
            if value not in known:
                out.append((name, path, value))
    return out


def remap_zones(stores: dict, replay_doc: dict) -> dict:
    entry = replay_doc.get("entry") or {}
    config = {**(entry.get("data") or {}), **(entry.get("options") or {})}
    stores = copy.deepcopy(stores)
    for key, document in stores.items():
        zones = document.get("heat_loss_zone_entities") if key.endswith("_thermal_learning") else None
        if isinstance(zones, dict):
            for zkey, ckey in ZONE_KEYS.items():
                if zkey in zones and config.get(ckey):
                    zones[zkey] = config[ckey]
    return stores


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True, type=Path)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--remap-zones", action="store_true")
    a = ap.parse_args(argv)
    began_cpu, began_thread = time.process_time(), time.thread_time()

    bundle = debug_ingest.load_bundle(a.bundle)
    replay_doc = bundle.get("replay") or {}
    stores = bundle.get("stores") or {}
    if a.remap_zones:
        stores = remap_zones(stores, replay_doc)
    bad = unresolved(stores, replay_doc)
    if a.list:
        for name, path, _value in bad:
            print(f"{name}{path}")
        return 0
    print(f"RESULT unresolved_id_leaves={len(bad)} unit=count")
    print(f"RESULT unresolved_stores={len({n for n, _, _ in bad})} unit=count")

    tl = next((d for k, d in stores.items() if k.endswith("_thermal_learning")), {})
    stored_samples = int(tl.get("house_heat_loss_samples") or 0) + int(
        tl.get("lower_floor_loss_samples") or 0)

    from heatpump_optimizer import coordinator as cm
    voided: list[tuple[str, str]] = []
    seen: dict = {}
    real_void = cm.HeatPumpOptimizerCoordinator._void_heat_loss_learners
    real_tick = cm.HeatPumpOptimizerCoordinator._async_update_data

    def counting_void(self, learners, why):
        voided.extend((learner, why) for learner in learners)
        return real_void(self, learners, why)

    async def keeping_tick(self):
        seen["coord"] = self
        return await real_tick(self)

    start = datetime.fromisoformat(replay_doc["window"]["start"])
    step = timedelta(minutes=15)
    window = debug_replay.trim_replay(replay_doc, start, start + step)
    with mock.patch.object(cm.HeatPumpOptimizerCoordinator, "_void_heat_loss_learners",
                           counting_void), \
            mock.patch.object(cm.HeatPumpOptimizerCoordinator, "_async_update_data",
                              keeping_tick), \
            contextlib.redirect_stderr(io.StringIO()):
        verdict = debug_replay.run_seeded(window, stores or None, 15)
    coord = seen.get("coord")
    held = (int(getattr(coord, "_house_heat_loss_samples", 0) or 0)
            + int(getattr(coord, "_lower_floor_loss_samples", 0) or 0)) if coord else 0
    print(f"RESULT replay_cycles={verdict.get('cycles')} unit=count")
    print(f"RESULT voided_learners={len(voided)} unit=count")
    for learner, why in voided:
        print(f"RESULT voided={learner} why={why!r}")
    print(f"RESULT learned_samples_lost={max(0, stored_samples - held)} unit=count")
    cpu, thr = time.process_time() - began_cpu, time.thread_time() - began_thread
    print(f"RESULT thread_factor={cpu / thr if thr > 0 else float('nan'):.3f} unit=ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} unit=load")
    print("RESULT swapins=n/a unit=count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

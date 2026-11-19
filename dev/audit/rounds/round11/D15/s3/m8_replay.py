#!/usr/bin/env python3
"""D15-s3 M8: a step-7 anomaly reproduced over its window of the bundle's
replay half, through ``tools/replay/debug_replay.py``'s own seeding and
``tests/replay.py:run_fixture``, with counts hooked on production symbols.

Prints derived counts only: no entity id, reading or instant of the bundle
(the window is given and printed as hours after the replay half's start).
A bundle is a user's private data and is never committed.

Arms (all on one run):
  tiles   anomaly ``solve_wall_ms:wall_twice_payload``: what-if solves
          (``HeatPumpOptimizerCoordinator.async_simulate``) per scheduled
          solve (``async_run_optimization``). ``--perturb tiles-off`` sets the
          replayed entry's ``price_tiles_enabled`` False: the count falls to 0.
  dhw     anomaly ``dhw_window_floor``: cycles inside a demand window whose
          published tank reading is under the published window minimum, and
          of those the cycles whose action heats no hot water.
  ids     the seeded stores' entity-id strings that name no entity of the
          masked replay half, the integration's WARNING records that say
          an input is unreadable, and those that reset a learned heat-loss
          learner to the configuration because "its zone sensor changed"
          (``_void_heat_loss_learners``). ``--perturb remap-ids`` rewrites each such
          id to the masked id the replay entry gives the same configuration
          key (the remap the seeding omits): both counts fall.

Command (repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s3/m8_replay.py --bundle B --start-h 18.5 --end-h 23 [--perturb tiles-off|remap-ids]
Expected (owner's bundle, window 18.5-23 h, 18 cycles; exact counts):
    EXPECTED RESULT simulate_per_solve=0.667 (12 of 18: two degree tiles of
      every three turns, the cap tile's turn inside its 6 h clock solves
      nothing); --perturb tiles-off: 0.0
    EXPECTED RESULT dhw_window_cycles=12 dhw_window_below_floor=5
      dhw_window_below_floor_not_heating=0
    EXPECTED RESULT seeded_foreign_entity_ids=4 learner_resets_zone_sensor_changed=2
      unreadable_warnings=1; --perturb remap-ids: 0, 0, 0 (finding D15-s3-03)
    EXPECTED RESULT judge_*=0 in every arm
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64,
CI venv. Counts only; the seconds printed are provisional.
Instrumented symbols: coordinator:HeatPumpOptimizerCoordinator.async_simulate,
    coordinator:HeatPumpOptimizerCoordinator.async_run_optimization,
    coordinator:HeatPumpOptimizerCoordinator._async_update_data,
    debug_replay:seed_stores, debug_replay:trim_replay.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import copy  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from contextlib import redirect_stdout  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from pathlib import Path  # noqa: E402
from unittest import mock  # noqa: E402

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components",
           ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import debug_ingest  # noqa: E402
import debug_replay  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402

ENTITY = re.compile(r"\b(?:sensor|switch|climate|number|select|binary_sensor|water_heater|"
                    r"input_number|input_boolean|weather)\.[a-z0-9_]+\b")


class _Count(logging.Handler):
    def __init__(self) -> None:
        super().__init__(logging.WARNING)
        self.unreadable = 0
        self.resets = 0

    def emit(self, record: logging.LogRecord) -> None:
        msg = record.getMessage()
        if "unreadable" in msg:
            self.unreadable += 1
        if "reset to the configuration" in msg and "zone sensor changed" in msg:
            self.resets += 1


def _real_config(path: Path) -> dict:
    doc = debug_ingest.read_download(path)
    data = doc.get("data") if isinstance(doc.get("data"), dict) else doc
    return data.get("config") if isinstance(data.get("config"), dict) else {}


def foreign_ids(stores: dict, replay_doc: dict) -> set[str]:
    known = set((replay_doc.get("states") or {})) | set(replay_doc.get("inputs") or [])
    found = set(ENTITY.findall(json.dumps(stores)))
    return {e for e in found if e not in known}


def remap(stores: dict, replay_doc: dict, real: dict) -> dict:
    entry = replay_doc.get("entry") or {}
    masked = {**(entry.get("data") or {}), **(entry.get("options") or {})}
    pairs = {v: masked[k] for k, v in real.items()
             if isinstance(v, str) and k in masked and isinstance(masked[k], str) and v != masked[k]}
    text = json.dumps(stores)
    for old, new in sorted(pairs.items(), key=lambda kv: -len(kv[0])):
        text = re.sub(rf"\b{re.escape(old)}\b", new, text)
    return json.loads(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True, type=Path)
    ap.add_argument("--start-h", type=float, required=True)
    ap.add_argument("--end-h", type=float, required=True)
    ap.add_argument("--perturb", choices=["", "tiles-off", "remap-ids"], default="")
    a = ap.parse_args()
    cpu0, thr0, wall0 = time.process_time(), time.thread_time(), time.monotonic()
    bundle = debug_ingest.load_bundle(a.bundle)
    replay_doc = copy.deepcopy(bundle.get("replay") or {})
    stores = copy.deepcopy(bundle.get("stores") or {})
    if not replay_doc:
        print("RESULT replay_half=absent")
        return 1
    w0 = datetime.fromisoformat(replay_doc["window"]["start"])
    start, end = w0 + timedelta(hours=a.start_h), w0 + timedelta(hours=a.end_h)
    doc = debug_replay.trim_replay(replay_doc, start, end)
    if a.perturb == "tiles-off":
        doc["entry"]["options"] = {**(doc["entry"].get("options") or {}), "price_tiles_enabled": False}
        doc["entry"]["data"] = {**(doc["entry"].get("data") or {}), "price_tiles_enabled": False}
    if a.perturb == "remap-ids":
        stores = remap(stores, replay_doc, _real_config(a.bundle))
    print(f"RESULT window_h={a.start_h}-{a.end_h} unit=h")
    print(f"RESULT seeded_foreign_entity_ids={len(foreign_ids(stores, replay_doc))} unit=count")

    calls = {"simulate": 0, "solve": 0, "cycles": 0, "win": 0, "below": 0, "below_no_dhw": 0}
    real_sim = cm.HeatPumpOptimizerCoordinator.async_simulate
    real_run = cm.HeatPumpOptimizerCoordinator.async_run_optimization
    real_tick = cm.HeatPumpOptimizerCoordinator._async_update_data

    async def sim(self, *args, **kw):
        calls["simulate"] += 1
        return await real_sim(self, *args, **kw)

    async def run(self, *args, **kw):
        calls["solve"] += 1
        return await real_run(self, *args, **kw)

    async def tick(self):
        data = await real_tick(self)
        calls["cycles"] += 1
        if data.get("dhw_in_demand_window"):
            calls["win"] += 1
            tank, floor = data.get("dhw_temperature"), data.get("dhw_min_temperature")
            if tank is not None and floor is not None and tank < floor:
                calls["below"] += 1
                act = data.get("current_action") or {}
                if not (act.get("dhw_heating_active") or (act.get("dhw_power") or 0) > 0):
                    calls["below_no_dhw"] += 1
        return data

    counter = _Count()
    logging.getLogger("custom_components.heatpump_optimizer").addHandler(counter)
    logging.getLogger("heatpump_optimizer").addHandler(counter)
    cm.HeatPumpOptimizerCoordinator.async_simulate = sim
    cm.HeatPumpOptimizerCoordinator.async_run_optimization = run
    cm.HeatPumpOptimizerCoordinator._async_update_data = tick
    # The lane's cost instruments (cycle 0 under sys.setprofile, odd cycles
    # under tracemalloc) multiply each solve's time several-fold and feed only
    # its cost figures, which this harness does not read: switched off, so the
    # counts above are the same and the run fits a shared box.
    import tracemalloc
    quiet = [mock.patch.object(sys, "setprofile", lambda *_a: None),
             mock.patch.object(tracemalloc, "start", lambda *_a: None),
             mock.patch.object(tracemalloc, "stop", lambda: None)]
    for q in quiet:
        q.start()
    try:
        with redirect_stdout(io.StringIO()):
            verdict = debug_replay.run_seeded(doc, stores or None, None)
    finally:
        for q in quiet:
            q.stop()
        cm.HeatPumpOptimizerCoordinator.async_simulate = real_sim
        cm.HeatPumpOptimizerCoordinator.async_run_optimization = real_run
        cm.HeatPumpOptimizerCoordinator._async_update_data = real_tick
    counts = verdict.get("counts") or {}
    print(f"RESULT cycles={verdict.get('cycles')} ticks={calls['cycles']} unit=count")
    for name in ("finite", "unit", "no_default", "agreement", "cycle"):
        print(f"RESULT judge_{name}={counts.get(name, 0)} unit=count")
    print(f"RESULT solves={calls['solve']} simulate_calls={calls['simulate']} unit=count")
    print(f"RESULT simulate_per_solve={round(calls['simulate'] / calls['solve'], 3) if calls['solve'] else 0} unit=ratio")
    print(f"RESULT dhw_window_cycles={calls['win']} unit=count")
    print(f"RESULT dhw_window_below_floor={calls['below']} unit=count")
    print(f"RESULT dhw_window_below_floor_not_heating={calls['below_no_dhw']} unit=count")
    print(f"RESULT unreadable_warnings={counter.unreadable} unit=count")
    print(f"RESULT learner_resets_zone_sensor_changed={counter.resets} unit=count")
    print(f"RESULT seconds={round(time.monotonic() - wall0, 1)} provisional=true unit=s")
    cpu, thr = time.process_time() - cpu0, time.thread_time() - thr0
    print(f"RESULT thread_factor={round(cpu / thr, 3) if thr else 1.0}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

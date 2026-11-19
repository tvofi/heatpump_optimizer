#!/usr/bin/env python3
"""D9-s2 retained bytes per config-entry reload: coordinators, entities and bytes still alive after unload.

METRIC: the entry is set up through the integration's own ``async_setup_entry`` (via
``tests/harness.py:ha_setup_entry``) with every platform's entities built by their real
``async_setup_entry``, driven ``--cycles`` real cycles
(``HeatPumpOptimizerCoordinator._async_update_data``), then unloaded through
``async_unload_entry`` (``ha_unload_entry``: on-unload callbacks run, ``runtime_data``
deleted) with the harness dropping every entity, as Home Assistant removes them. After a
full ``gc.collect()``: (a) how many ``HeatPumpOptimizerCoordinator`` instances are still
alive (weakref liveness of each one the harness built), (b) the tracemalloc traced bytes
attributable to production frames, per reload, as a slope over reloads 2..K. A clean
unload leaves 0 coordinators alive per reload, bytes flat. Count key: weakref liveness of
the production coordinator objects; bytes as tracemalloc reports them.

RUN:   HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D9/s2/reload.py \
         [--reloads 8] [--cycles 3] [--fixture synthetic] [--arm baseline|keep_entities]
  --arm keep_entities is the positive control (perturbation the instrument must see): the
  harness keeps the unloaded entities alive, as a platform that failed to remove them
  would; each one references its coordinator, so coordinators_alive must go UP to K.
EXPECTED: baseline coordinators_alive_after_unload=0 (exact); keep_entities = reloads (exact).
BASELINE: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. MACHINE: printed.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import gc
import importlib
import platform
import sys
import time
import tracemalloc
import weakref
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _drive  # noqa: E402

PKG = "custom_components/heatpump_optimizer/"


def prod_bytes() -> int:
    snap = tracemalloc.take_snapshot().filter_traces(
        [tracemalloc.Filter(True, f"*{PKG}*")])
    return sum(s.size for s in snap.statistics("filename"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reloads", type=int, default=8)
    ap.add_argument("--cycles", type=int, default=3)
    ap.add_argument("--fixture", default="synthetic", choices=sorted(_drive.FIXTURES))
    ap.add_argument("--arm", default="baseline", choices=["baseline", "keep_entities"])
    args = ap.parse_args()
    t0 = time.time()

    # The driver supplies hass, the entry, the input replay and the synthetic price and
    # solar fetches; its own coordinator is the first "load", unloaded like every other.
    drv = _drive.Driver(args.fixture)
    import heatpump_optimizer as integration
    from harness import ha_unload_entry
    cm = drv.cm
    hass, entry = drv.hass, drv.entry
    if entry not in hass.config_entries.entries:
        hass.config_entries.entries.append(entry)
    # Class-level copies of the driver's per-instance fetch stubs, so the coordinators
    # async_setup_entry builds fetch nothing from the network either.
    solar_stub, price_stub = drv.coord._fetch_solar_forecast, drv.coord.__dict__.get("_fetch_tibber_prices")

    async def no_solar(self) -> None:
        self._open_meteo = None

    cm.HeatPumpOptimizerCoordinator._fetch_solar_forecast = no_solar
    del solar_stub, price_stub

    # async_setup_entry builds the coordinator INSIDE a running loop, where the driver's
    # asyncio.run(restore_session) cannot run: schedule it on that loop instead (it
    # completes before setup's own awaits return); every other spawn is closed, as
    # FakeHass closes it.
    def create_task(coro, name=None, eager_start=None):
        if getattr(coro, "__name__", "") in _drive.RUN_SPAWNS:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                asyncio.run(coro)
                return None
            return loop.create_task(coro)
        coro.close()
        return None

    hass.async_create_task = create_task
    # The notifier async_setup_entry wires fires bus events; the stub bus has no
    # async_fire, so give it a recorder-less one (not production state).
    if not hasattr(hass.bus, "async_fire"):
        hass.bus.async_fire = lambda *a, **k: None

    refs: list[weakref.ref] = [weakref.ref(drv.coord)]
    kept: list = []
    rows = []
    tracemalloc.start(1)

    def run_cycles(coord) -> None:
        for _ in range(args.cycles):
            t = drv.now()
            drv.dt_util.freeze(t)
            drv._inputs(t)
            try:
                coord.data = asyncio.run(coord._async_update_data())
            except Exception as err:  # noqa: BLE001
                drv.n_errors += 1
                if len(drv.errors) < 5:
                    drv.errors.append(f"{type(err).__name__}: {err}")
            drv.cycles += 1

    run_cycles(drv.coord)
    for k in range(1, args.reloads + 1):
        # unload the current load
        ok = asyncio.run(ha_unload_entry(integration, hass, entry))
        if args.arm == "keep_entities":
            kept.extend(drv.entities)
        drv.entities = []
        drv.coord = None
        hass.services.calls.clear()
        gc.collect(); gc.collect()
        alive = sum(1 for r in refs if r() is not None)
        rows.append({"reload": k, "unload_ok": ok, "alive": alive, "built": len(refs), "bytes": prod_bytes()})
        # set the next load up through the integration's own setup
        t = drv.now()
        drv.dt_util.freeze(t)
        drv._inputs(t)
        asyncio.run(integration.async_setup_entry(hass, entry))
        coord = entry.runtime_data
        refs.append(weakref.ref(coord))
        ents: list = []
        for plat in integration.PLATFORM_LIST:
            mod = importlib.import_module(f"heatpump_optimizer.{str(plat)}")
            asyncio.run(mod.async_setup_entry(hass, entry, ents.extend))
        drv.entities = ents
        drv.coord = coord
        run_cycles(coord)
        del coord, ents
    tracemalloc.stop()
    drv.close()

    print(f"# machine {platform.platform()} py{platform.python_version()}")
    print(f"# fixture={args.fixture} arm={args.arm} reloads={args.reloads} cycles/load={args.cycles} "
          f"cycle_errors={drv.n_errors} {drv.errors[:2]}")
    for r in rows:
        print(f"# reload={r['reload']} unload_ok={r['unload_ok']} coordinators_built={r['built']} "
              f"alive_after_gc={r['alive']} prod_traced_bytes={r['bytes']}")
    # Traced bytes alternate with reload parity (the in-process plan handover the
    # unload parks and the next setup pops), so the slope compares like parity.
    last = rows[-1]
    ref = next(r for r in rows if r["reload"] >= 2 and (last["reload"] - r["reload"]) % 2 == 0) \
        if len(rows) > 2 else rows[0]
    span = max(1, last["reload"] - ref["reload"])
    print(f"RESULT coordinators_alive_after_unload={last['alive']} count (of {last['built']} built)")
    print(f"RESULT prod_bytes_slope_per_reload={(last['bytes'] - ref['bytes']) / span:.0f} B/reload "
          f"(reloads {ref['reload']}..{last['reload']})")
    print(f"RESULT wall_s={time.time() - t0:.0f} s (provisional)")
    print(f"RESULT thread_factor={time.process_time() / max(1e-9, time.thread_time()):.3f}")
    print(f"RESULT load1={_drive.load1()}")
    print(f"RESULT swapins={_drive.swapins()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""D9-s2 retained bytes per on-demand call: diagnostics download and the read-only service actions.

METRIC: after --warm real cycles of the synthetic replay, each entry point is called --calls
times back to back (no cycle between, so nothing else allocates); the production-frame
tracemalloc bytes (frames under custom_components/heatpump_optimizer/) after a full GC are
read after call 2 and after the last call; slope = bytes retained per call. A call that
keeps nothing reads ~0 B/call. Entry points: diagnostics.async_get_config_entry_diagnostics
(the Download diagnostics button), services.handle_simulate_plan (the card's what-if),
services.handle_diagnose_interval, services.handle_debug_collect(action=status), and
config_flow's options flow opened and abandoned (OptionsFlow init step).
Count key: tracemalloc bytes whose allocating frame is production code.
POSITIVE CONTROL (the instrument must see retention): --arm leak appends each diagnostics
result to a list held by the diagnostics module, so its slope must go UP to ~the payload size.
RUN:   HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D9/s2/ondemand.py \
         [--calls 30] [--warm 6] [--arm baseline|leak]
EXPECTED: printed per entry point; a held result reads < 1 % of its own response bytes per call.
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
import json
import platform
import sys
import time
import tracemalloc
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _drive  # noqa: E402

PKG = "custom_components/heatpump_optimizer/"


def prod_bytes() -> int:
    gc.collect(); gc.collect()
    snap = tracemalloc.take_snapshot().filter_traces([tracemalloc.Filter(True, f"*{PKG}*")])
    return sum(s.size for s in snap.statistics("filename"))


class Call:
    def __init__(self, hass, data):
        self.hass, self.data = hass, data
        self.domain, self.service, self.return_response = "heatpump_optimizer", "", True
        self.context = None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--calls", type=int, default=30)
    ap.add_argument("--warm", type=int, default=6)
    ap.add_argument("--arm", default="baseline", choices=["baseline", "leak"])
    args = ap.parse_args()
    t0 = time.time()
    drv = _drive.Driver("synthetic")
    for _ in range(args.warm):
        drv.cycle()
    hass, entry = drv.hass, drv.entry
    from homeassistant.config_entries import ConfigEntryState
    entry.state = ConfigEntryState.LOADED
    if entry not in hass.config_entries.entries:
        hass.config_entries.entries.append(entry)
    from heatpump_optimizer import diagnostics, services, config_flow
    if args.arm == "leak":
        diagnostics._D9_HELD = []
        orig = diagnostics.async_get_config_entry_diagnostics

        async def held(h, e):
            out = await orig(h, e)
            diagnostics._D9_HELD.append(out)
            return out
        diagnostics.async_get_config_entry_diagnostics = held

    async def diag():
        return await diagnostics.async_get_config_entry_diagnostics(hass, entry)

    async def whatif():
        return await services.handle_simulate_plan(hass, Call(hass, {}))

    async def diagnose():
        return await services.handle_diagnose_interval(hass, Call(hass, {}))

    async def debug_status():
        return await services.handle_debug_collect(hass, Call(hass, {"action": "status"}))

    async def options_flow():
        flow = config_flow.HeatPumpOptimizerConfigFlow.async_get_options_flow(entry)
        flow.hass = hass
        try:
            flow.handler = entry.entry_id
        except Exception:  # noqa: BLE001
            pass
        try:
            object.__setattr__(flow, "_config_entry", entry)
        except Exception:  # noqa: BLE001
            pass
        return await flow.async_step_init(None)

    points = {"diagnostics": diag, "simulate_plan": whatif, "diagnose_interval": diagnose,
              "debug_collect_status": debug_status, "options_flow_init": options_flow}
    tracemalloc.start(1)
    rows = {}
    for name, fn in points.items():
        b2 = None
        size = None
        err = None
        for i in range(1, args.calls + 1):
            try:
                out = asyncio.run(fn())
                if size is None:
                    size = len(json.dumps(out, default=str).encode())
            except Exception as e:  # noqa: BLE001
                err = f"{type(e).__name__}: {str(e)[:120]}"
                out = None
            del out
            if i == 2:
                b2 = prod_bytes()
        bn = prod_bytes()
        rows[name] = {"slope": (bn - (b2 or bn)) / max(1, args.calls - 2), "response_bytes": size, "error": err}
    tracemalloc.stop()
    drv.close()
    print(f"# machine {platform.platform()} py{platform.python_version()}")
    print(f"# arm={args.arm} calls={args.calls} warm={args.warm} cycle_errors={drv.n_errors}")
    for name, r in rows.items():
        print(f"RESULT retained_per_call[{name}]={r['slope']:.0f} B/call (response {r['response_bytes']} B; error={r['error']})")
    print(f"RESULT wall_s={time.time() - t0:.0f} s (provisional)")
    print(f"RESULT thread_factor={time.process_time() / max(1e-9, time.thread_time()):.3f}")
    print(f"RESULT load1={_drive.load1()}")
    print(f"RESULT swapins={_drive.swapins()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

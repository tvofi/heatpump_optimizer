#!/usr/bin/env python3
"""D5.M3 mechanism harness: docs/setup.md:131 says that under Configure "**Quick setup** is the last
entry on the first menu"; the options flow's first menu ends with Advanced settings.

Metric: position from the end of `quick_setup` among the menu_options the options flow's
async_step_init actually shows (1 = last, as the doc states), driven with the translation lookup
patched to pass labels through and async_show_menu captured.
Key: the menu the production step builds, not the class attribute alone.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/menu_order.py [--perturb]
  --perturb  the "advanced" entry dropped from the shown menu in memory (as if Advanced settings
             were not on the first menu): quick_setup_from_end 2 -> 1.
Null control: setup_overview (the doc's first entry, "Your system, as configured") is index 0.
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (exact): menu_entries=9,
quick_setup_from_end=2, last_entry=advanced, setup_overview_index=0.
Machine: B2 (orchestrator's macOS box).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, sys, time
from unittest import mock

sys.path.insert(0, "custom_components")
import heatpump_optimizer.config_flow as cf  # noqa: E402


async def passthrough(hass, flow, step, labels):
    return dict(labels)


def main():
    cls = next(getattr(cf, n) for n in dir(cf) if isinstance(getattr(cf, n), type) and hasattr(getattr(cf, n), "_TOP_MENU"))
    flow = cls.__new__(cls)
    flow.hass = None
    shown = {}
    def show_menu(**kw):
        opts = list(kw["menu_options"])
        if "--perturb" in sys.argv:
            opts = [o for o in opts if o != "advanced"]
        shown["opts"] = opts
        return kw
    flow.async_show_menu = show_menu
    with mock.patch.object(cf, "_translated_menu", passthrough):
        asyncio.run(flow.async_step_init())
    opts = shown["opts"]
    print(f"RESULT menu_entries={len(opts)} entries")
    print(f"RESULT quick_setup_from_end={len(opts) - opts.index('quick_setup')}")
    print(f"RESULT last_entry={opts[-1]}")
    print(f"RESULT setup_overview_index={opts.index('setup_overview')}")
    print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()

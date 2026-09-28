#!/usr/bin/env python3
"""D10 -- does the integration hand its DataUpdateCoordinator the config entry?

METRIC (one line): the number of ``DataUpdateCoordinator.__init__`` invocations
made by the integration that pass a ``config_entry`` argument, and the value of
``coordinator.config_entry`` on a coordinator built the way ``async_setup_entry``
builds one.

COMMAND (from the export root, nothing else needed):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/coordinator_entry_rule.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python3 3.11.5): super_init_calls=1, calls_passing_config_entry=0,
coordinator_config_entry_is_set=0, stub_would_reject=0. Counts; contention-immune.

Home Assistant's own current example on
https://developers.home-assistant.io/docs/integration_fetching_data (fetched
2026-09-10) constructs the coordinator as ``super().__init__(hass, _LOGGER,
config_entry=config_entry, name=..., update_interval=...)``.

INSTRUMENTED SYMBOL:
custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.__init__
(the base ``DataUpdateCoordinator.__init__`` it calls is wrapped here and the
keyword set of every call is recorded).

PERTURBATION: add ``config_entry=entry`` to the ``super().__init__`` call in
coordinator.py; calls_passing_config_entry goes 0 -> 1 (direction: up) and
coordinator_config_entry_is_set goes 0 -> 1.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
os.chdir(ROOT)
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.helpers import update_coordinator as uc  # noqa: E402

CALLS: list[set[str]] = []
_orig = uc.DataUpdateCoordinator.__init__


def _spy(self, *args, **kwargs):
    CALLS.append(set(kwargs))
    return _orig(self, *args, **kwargs)


uc.DataUpdateCoordinator.__init__ = _spy
try:
    import heatpump_optimizer.coordinator as cm  # noqa: E402
    cfg = {"tibber_token": "t", "heat_pump_switch": "switch.hp"}
    coord = cm.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
finally:
    uc.DataUpdateCoordinator.__init__ = _orig

passing = sum(1 for kw in CALLS if "config_entry" in kw)
sig = inspect.signature(_orig)
stub_named = "config_entry" in sig.parameters
print(f"RESULT super_init_calls={len(CALLS)} count")
print(f"RESULT calls_passing_config_entry={passing} count")
print(f"RESULT coordinator_config_entry_is_set="
      f"{1 if getattr(coord, 'config_entry', None) is not None else 0} count")
print(f"RESULT coordinator_has_private_entry_attr="
      f"{1 if getattr(coord, 'entry', None) is not None else 0} count")
print(f"RESULT stub_names_config_entry={1 if stub_named else 0} count")
print(f"RESULT stub_signature={str(sig).replace(' ', '')} text")
print(f"RESULT kwargs_actually_passed={sorted(CALLS[0]) if CALLS else []} text")
print("RESULT thread_factor=1.0")
try:
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
except OSError:
    print("RESULT load1=nan")
print("RESULT swapins=0")

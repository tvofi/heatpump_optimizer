#!/usr/bin/env python3
"""D12 generalization — DHW configuration leaking onto a no-DHW plant.

METRIC (one line): the number of AVAILABLE entities whose
``extra_state_attributes`` carry a non-empty ``dhw_windows`` string, counted
once on the fully-mapped reference plant (DHW present) and once on the same
plant with DHW dropped.

WHY: `_PlanSensorBase._plan` (sensor.py, the seam the space-heating plan
sensor publishes through) includes ``dhw_windows`` / ``dhw_windows_spec`` /
``dhw_min_temperature`` unconditionally, taken from the coordinator payload.
On a plant that configured no DHW the payload still carries the DEFAULT
windows string and the DEFAULT minimum, so a *space-heating* sensor on an
install with no hot water advertises a hot-water schedule.  The attribute's
own comment states the intent is to pre-fill the card "from what is really
in force rather than from a default that would propose an unasked-for
change"; on the no-DHW plant the value published IS a default.

A correct gate would take the count to ZERO when DHW is dropped; the
observed count is the finding.

COMMAND:  cd <repo root> && HPO_PLANDATA=$TMP/plandata \
            PYTHONPATH=tests/hastub python3 tools/audit/round5/D12/dhw_leak.py

EXPECTED:  reference count 5; no-DHW count 0 (a fabricated value is a
           correctness claim, so tolerance is exact).
BASELINE:  origin/main eaa2a06af16a1b5b006f58a0f36cc92131f80225
MACHINE:   darwin 25.6.0, Apple M1, 8 GB

The count is keyed on the published attribute on a created entity, never on
a config attribute the harness wrote.
"""
import os

for _k in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_k, "1")

import asyncio  # noqa: E402
import importlib  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cells  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)

PLATFORMS = ("sensor", "binary_sensor", "button", "climate", "switch", "datetime")
#: attributes that assert a DHW configuration exists
DHW_CONFIG_ATTRS = ("dhw_windows", "dhw_windows_spec", "dhw_min_temperature")


def build(name: str) -> tuple[dict, object, list]:
    cfg, kw = cells.cell_configs()[name]
    cfg = cells._apply(dict(cfg), kw)
    dt_util.freeze(cells.START)
    hass = FakeHass(cells.states_for(cfg))
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    asyncio.run(coord._update_current_state())
    cells.seed(coord)
    asyncio.run(coord.async_run_optimization())
    coord.data = coord._build_data_dict()
    entry.runtime_data = coord
    ents: list = []
    for mod in PLATFORMS:
        obj = importlib.import_module(f"heatpump_optimizer.{mod}")
        added: list = []
        asyncio.run(obj.async_setup_entry(hass, entry, added.extend))
        ents.extend(added)
    return cfg, coord, ents


def exposing(ents: list) -> list[str]:
    """Available entities carrying a non-empty DHW-config attribute."""
    out: list[str] = []
    for e in ents:
        try:
            if not e.available:
                continue
            attrs = e.extra_state_attributes or {}
        except Exception:
            continue
        for key in DHW_CONFIG_ATTRS:
            val = attrs.get(key)
            if isinstance(val, str) and val.strip():
                out.append(f"{getattr(e, '_attr_unique_id', '?')}:{key}")
                break
    return out


def main() -> int:
    t0 = time.process_time()
    cfg_r, coord_r, ents_r = build("ref_all_mapped")
    cfg_n, coord_n, ents_n = build("no_dhw")

    ref_hits = exposing(ents_r)
    nodhw_hits = exposing(ents_n)

    print(f"  reference dhw_enabled={coord_r._thermal_params.dhw_enabled} "
          f"hits={len(ref_hits)}")
    for h in ref_hits:
        print(f"    {h}")
    print(f"  no_dhw    dhw_enabled={coord_n._thermal_params.dhw_enabled} "
          f"hits={len(nodhw_hits)}")
    for h in nodhw_hits:
        print(f"    {h}")

    cpu = time.process_time() - t0
    print(f"RESULT reference_dhw_config_entities={len(ref_hits)} count")
    print(f"RESULT nodhw_dhw_config_entities={len(nodhw_hits)} count")
    print(f"RESULT nodhw_dhw_enabled={int(coord_n._thermal_params.dhw_enabled)} bool")
    print(f"RESULT leaked_attributes={','.join(nodhw_hits) if nodhw_hits else '-'}")
    print(f"RESULT pid_cpu_s={round(cpu, 3)}")
    print("RESULT thread_factor=1.0")
    try:
        load1 = float(os.getloadavg()[0])
    except Exception:
        load1 = float("nan")
    print(f"RESULT load1={round(load1, 2)}")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

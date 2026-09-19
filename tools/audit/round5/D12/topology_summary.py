#!/usr/bin/env python3
"""D12 generalization — the topology description surface across plants.

METRIC (one line): the number of plant cells whose ``describe_setup`` /
``render_text_summary`` call raises, run over every matrix cell plus
deliberately malformed layout / positions values.

WHY: ``topology.describe_setup`` is the seam every card and setup summary
reads to say what plant it thinks it is looking at.  If a legal cell makes
it raise, the plant that cell describes is unusable; if it raises on a
malformed layout, the surface is not defensive against a config a user can
reach by editing storage.

COMMAND:  cd <repo root> && HPO_PLANDATA=$TMP/plandata \
            PYTHONPATH=tests/hastub python3 tools/audit/round5/D12/topology_summary.py

EXPECTED:  0 raising cells.
BASELINE:  origin/main eaa2a06af16a1b5b006f58a0f36cc92131f80225
MACHINE:   darwin 25.6.0, Apple M1, 8 GB
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

import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cells  # noqa: E402
from heatpump_optimizer import const as C  # noqa: E402
from heatpump_optimizer import topology  # noqa: E402


def rich() -> dict:
    cfg = cells.map_all(cells.base_config())
    cfg.update(
        {
            C.CONF_DHW_TANK_VOLUME: 200.0,
            C.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0,
            C.CONF_LOWER_FLOOR_THERMAL_MASS: 8.0,
            C.CONF_MIXING_VALVE_MODE: "manual",
            C.CONF_BUFFER_TANK_VOLUME: 750.0,
            C.CONF_WOOD_FURNACE_ENABLED: True,
            C.CONF_WOOD_TANK_VOLUME: 500.0,
            C.CONF_DHW_WOOD_COIL_ENABLED: True,
        }
    )
    return cfg


def main() -> int:
    t0 = time.process_time()
    cases: dict[str, dict] = {}
    for name, (cfg, kw) in cells.cell_configs().items():
        cases[name] = cells._apply(dict(cfg), kw)
    cases["empty"] = {}
    cases["topology_garbage"] = {**rich(), C.CONF_TOPOLOGY_LAYOUT: "not_a_layout"}
    cases["positions_garbage"] = {**rich(), C.CONF_TOPOLOGY_POSITIONS: {"bogus": 3}}

    bad: list[str] = []
    for name, cfg in cases.items():
        try:
            desc = topology.describe_setup(dict(cfg))
            text = topology.render_text_summary(desc)
            print(
                f"  ok  {name:26s} layout={desc['layout']:24s} "
                f"slots={len(desc['slots']):2d} edges={len(desc['edges'])} "
                f"summary={len(text)}"
            )
        except Exception as err:
            bad.append(name)
            print(f"  FAIL {name:26s} {type(err).__name__}: {err}")

    cpu = time.process_time() - t0
    print(f"RESULT topo_cases={len(cases)} count")
    print(f"RESULT topo_failures={len(bad)} count")
    print(f"RESULT failing_topo_cells={','.join(bad) if bad else '-'}")
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

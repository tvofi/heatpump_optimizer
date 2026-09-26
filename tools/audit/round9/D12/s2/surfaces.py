"""D12-s2 (round 9, D12.M3) non-finding sweep over the heat-pump control
surfaces the tree already has: switch-slot domains, ECL110 MQTT absent/present,
compressor-frequency number/sensor/none in observe and control.

Metric (one line): per surface cell, the count of service calls the production
seam issues that (a) target a domain other than the entity's own, or (b) write
through a surface the config did not configure or did not opt into; a cell
FAILS when that count > 0 (the sweep's `failing_surface_cells`).

Count key: ``FakeServices.calls`` issued by ``HeatPumpOptimizerCoordinator``
seams -- ``_apply_action`` (``_on_off_service``), ``async_publish_current_action``
(``_publish_ecl110_topics``), ``_command_frequency`` -- never the config.

Perturbation (--perturb): ``coordinator._on_off_service`` patched in memory to
the pre-#1526 hard-coded ``("switch", ...)``: failing_surface_cells 0 -> 2
(the input_boolean and climate switch-slot cells; UP). This proves the sweep
can see a misroute rather than asserting one.

Run:   PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D12/s2/surfaces.py [--perturb]
Expected (baseline): RESULT failing_surface_cells=0 cells; --perturb: 2 cells
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
Machine: box B7 cloud container, Linux 6.18, 4 vCPU; counts only.
Root rule: run from the repository root; relative tests/ and custom_components/.
"""
import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import asyncio
import sys
import tempfile
import time
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

BASE = {"tibber_token": "x", "weather_entity": "weather.home"}


def _coord(states=None, **cfg):
    from harness import FakeEntry, FakeHass
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    return HeatPumpOptimizerCoordinator(FakeHass(states or {}), FakeEntry(data={**BASE, **cfg}))


def switch_cell(domain):
    eid = f"{domain}.heat_pump"
    c = _coord(heat_pump_switch_entity=eid)

    async def _np(**_k):
        return None

    c.async_publish_current_action = _np
    c._mode = "comfort"
    bad = 0
    for on in (True, False):
        c._current_action = {"heat_pump_on": on, "power": 1.0}
        asyncio.run(c._apply_action())
    for d, svc, data in c.hass.services.calls:
        if (data or {}).get("entity_id") == eid and d != domain:
            bad += 1
    n = sum(1 for _d, _s, data in c.hass.services.calls if (data or {}).get("entity_id") == eid)
    return bad, n


def ecl_cell(configured):
    cfg = {}
    if configured:
        cfg = {"ecl110_displace_set_topic": "ecl110/displace/set", "ecl110_command_topic": "ecl110/cmd"}
    c = _coord(**cfg)
    c._current_action = {"heat_pump_on": True, "displace_value": 2.0}
    asyncio.run(c.async_publish_current_action(reason="d12s2"))
    mqtt = sum(1 for d, _s, _x in c.hass.services.calls if d == "mqtt")
    return (mqtt if not configured else 0), mqtt


def freq_cell(kind, mode):
    from harness import FakeState

    states = {}
    cfg = {"freq_control_mode": mode}
    if kind in ("number", "both"):
        states["number.comp_hz"] = FakeState("40", attributes={"min": 20, "max": 90})
        cfg["compressor_freq_entity"] = "number.comp_hz"
    if kind in ("sensor", "both"):
        states["sensor.comp_hz"] = FakeState("40")
        cfg["compressor_freq_sensor"] = "sensor.comp_hz"
    c = _coord(states, **cfg)
    c._current_action = {"power": 2.0, "heat_pump_on": True}
    # Evidence in every bucket so control has an answer, and no rate limit.
    for hz in range(21, 90, 2):
        for _ in range(6):
            c._freq_map.observe(float(hz), hz * 0.05, 20.0, 90.0)
    c._freq_last_write = None
    asyncio.run(c._command_frequency())
    writes = sum(1 for d, s, _x in c.hass.services.calls if d == "number" and s == "set_value")
    allowed = kind in ("number", "both") and mode == "control"
    bad = writes if not allowed else 0
    return bad, writes, c._freq_mode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    args = ap.parse_args()
    os.environ.setdefault("HPO_PLANDATA", tempfile.mkdtemp(prefix="d12s2_sf_"))
    from heatpump_optimizer import coordinator as co

    patch = (
        mock.patch.object(co, "_on_off_service", lambda eid, on: ("switch", "turn_on" if on else "turn_off"))
        if args.perturb
        else None
    )
    if patch:
        patch.start()
    t0p, t0t = time.process_time(), time.thread_time()
    fails = 0
    cells = 0
    try:
        for dom in ("switch", "input_boolean", "climate"):
            bad, n = switch_cell(dom)
            cells += 1
            fails += bool(bad)
            print(f"CELL switch_slot={dom} misrouted={bad} calls={n}")
        for conf in (False, True):
            bad, n = ecl_cell(conf)
            cells += 1
            fails += bool(bad)
            print(f"CELL ecl110_configured={conf} unconfigured_publishes={bad} mqtt_calls={n}")
        for kind in ("none", "sensor", "number", "both"):
            for mode in ("observe", "control"):
                bad, n, eff = freq_cell(kind, mode)
                cells += 1
                fails += bool(bad)
                print(f"CELL freq_entity={kind} mode={mode} effective={eff} unallowed_writes={bad} writes={n}")
    finally:
        if patch:
            patch.stop()
    print(f"RESULT surface_cells={cells} cells")
    print(f"RESULT failing_surface_cells={fails} cells")
    proc, thr = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    swap = 0
    try:
        with open("/proc/vmstat") as fh:
            for line in fh:
                if line.startswith("pswpin "):
                    swap = int(line.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={swap}")


if __name__ == "__main__":
    main()

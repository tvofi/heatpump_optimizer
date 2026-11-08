#!/usr/bin/env python3
"""Reproduce R10-HOTFIX-COP-UNMEASURED at any checkout: the COP health watch fed by the model.

    python3 -I dev/audit/harnesses/r10_rca_cop_unmeasured.py [--check] <repo root at the SHA to measure>

The root-cause seat's reproduction (dev/audit/rca/R10-RCA-COP-UNMEASURED.md).
It builds the real coordinator against the tests' Home Assistant stub, from the
checkout named on the command line, and drives ``_fold_cop_evidence`` (the COP
fold's tail every cycle and counter span ends in) with three installs:

- ``null``: no heat input, a hot-water interval whose draw equals the plan's ask.
  ``cop_evidence`` then infers the model's own COP, so any band it records is the
  model graded against itself.
- ``tuya``: heat and power both vendor estimates (entity ids carrying
  ``estimated``), whose ratio is the vendor's fitted COP on every interval.
- ``metered``: a thermal power entity and a power entity with plain ids, the
  positive control: the one install whose band should fill.

Each prints what the watch recorded (``_cop_baseline``) and the last measured
COP (``_measured_cop.cop``), then ``RESULT`` with a verdict per install:
``graded`` (the watch took the sample) or ``withheld``. A defective tree prints
``null=graded tuya=graded``; a fixed one ``null=withheld tuya=withheld``.
``metered=graded`` on both is the control that the harness can see a sample.
Without ``--check`` it exits 0: it measures, it does not judge. With
``--check`` it is the detector: exit 1 when the watch took a ``null`` or
``tuya`` sample (the defect), exit 2 when it withheld the ``metered`` one (a
tree that withholds everything would otherwise pass by skipping), exit 3 when
a module loaded from outside the named root, else 0. The verdict follows the
named root whatever the shell's cwd: the harness changes into it first.
"""
from __future__ import annotations

import os
import sys


def main(root: str, check: bool = False) -> int:
    root = os.path.abspath(root)
    # tests/harness.py, at every tree measured, inserts the cwd-relative
    # "tests" and "custom_components" ahead of these, so the import follows
    # the shell's cwd unless the cwd is the root itself.
    os.chdir(root)
    sys.path[:0] = [os.path.join(root, p) for p in ("tests/hastub", "custom_components", "tests")]
    import harness  # noqa: PLC0415
    from harness import FakeEntry, FakeHass, FakeState  # noqa: PLC0415
    from heatpump_optimizer import flow_meter  # noqa: PLC0415
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: PLC0415

    # Refuse rather than measure another tree: every module the verdict
    # rests on must have loaded from the root named on the command line.
    for mod in (harness, flow_meter, sys.modules["heatpump_optimizer.coordinator"]):
        loaded = os.path.realpath(mod.__file__)
        if os.path.commonpath([loaded, os.path.realpath(root)]) != os.path.realpath(root):
            print(f"REFUSED {mod.__name__} loaded from {loaded}, outside {root}")
            return 3

    base_cfg = {
        "tibber_token": "x", "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
        "heat_pump_max_power": 14.0, "heat_pump_min_power": 1.0,
    }
    states = {
        "sensor.indoor": FakeState("21.0", unit="°C"),
        "sensor.outdoor": FakeState("8.0", unit="°C"),
    }

    def coord(**cfg):
        return HeatPumpOptimizerCoordinator(FakeHass(dict(states)), FakeEntry(data=dict(base_cfg, **cfg)))

    def fold(c, heat_kw, dhw, elec=2.0, ask=2.0, outdoor=8.0, tank=48.0):
        c._current_state.outdoor_temperature = outdoor
        m = c._thermal_model
        ref = (m.compute_cop_dhw(outdoor, tank), True, tank) if dhw else (m.compute_cop(outdoor), False, None)
        refusal = c._fold_cop_evidence(ask, elec, heat_kw, ref)
        return refusal, ref[0]

    verdicts = {}

    null = coord(heat_pump_power_entity="sensor.pump_power")
    refusal, model = fold(null, None, True)
    inferred = flow_meter.cop_evidence(model, 2.0, 2.0, None, 1.0)[0]
    print(f"null: model compute_cop_dhw(8, 48) = {model!r}; inferred = {inferred!r}; equal = {inferred == model}")
    print(f"null: refusal {refusal!r}; baseline {dict(null._cop_baseline)}; measured cop {null._measured_cop.cop!r}")
    verdicts["null"] = "graded" if null._cop_baseline else "withheld"

    tuya = coord(heat_pump_power_entity="sensor.pump_estimated_power_draw",
                 heat_pump_thermal_power_entity="sensor.pump_estimated_heating_output")
    for fitted in (3.1, 2.4, 4.05):
        refusal, _ = fold(tuya, fitted * 2.0, False)
    print(f"tuya: refusal {refusal!r}; baseline {dict(tuya._cop_baseline)}; measured cop {tuya._measured_cop.cop!r}")
    verdicts["tuya"] = "graded" if tuya._cop_baseline else "withheld"

    metered = coord(heat_pump_power_entity="sensor.hp_power", heat_pump_thermal_power_entity="sensor.heat_kw")
    refusal, _ = fold(metered, 6.0, False)
    print(f"metered: refusal {refusal!r}; baseline {dict(metered._cop_baseline)}; measured cop {metered._measured_cop.cop!r}")
    verdicts["metered"] = "graded" if metered._cop_baseline else "withheld"

    print("RESULT " + " ".join(f"{k}={v}" for k, v in verdicts.items()))
    if not check:
        return 0
    if verdicts["metered"] != "graded":
        return 2
    return 1 if "graded" in (verdicts["null"], verdicts["tuya"]) else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    want_check = args[:1] == ["--check"]
    args = args[1:] if want_check else args
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(args[0], want_check))

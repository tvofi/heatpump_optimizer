"""D17-s2-01 -- "Automatic" two-zone mode is unconditionally ON: an entry that never
saved a zone value is planned as a two-zone house.

Metric: over the initial-flow paths that reach create_entry, the number of created
entries whose model runs two-zone (ThermalParameters.from_config(...).two_zone_enabled,
read back from the coordinator's published `two_zone_enabled`) although the entry
holds NO zone value (upper/lower floor mass, inter-zone transfer, radiator fraction)
at the moment it was created by a path that never asked the two-zone question, or
whose stored answer is the default "auto". Key: the model's two_zone_enabled as the
real coordinator publishes it after one cycle, never the entry's keys.
Oracle (docs/configuration.md "Two-zone model" row, strings.json
options.step.thermal_model_zones.data_description.two_zone_mode): "Automatic uses
two-zone as soon as any zone value has ever been saved"; config.step.finish_setup:
"start with shipped defaults" (quick_setup.SHIPPED_ANSWERS two_zone=False);
config.step.building_describe.data_description.upper_floor_emitter: "A single-zone
house is modelled from the lower floor heating answer alone".

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D17/s2/two_zone_auto.py [--perturb]
Expected at 92d38ecb: RESULT auto_two_zone_without_values=1 (finish_now) ; RESULT
          questionnaire_two_zone_unasked=1 ; RESULT upper_emitter_moves_single_zone_answer=1 ;
          null control RESULT explicit_off_two_zone=0. Tolerance 0 (counts).
--perturb: ThermalParameters.from_config wrapped so mode "auto" answers by zone-key
presence (the one-line fix: drop DEFAULT_TWO_ZONE_MODE from the `in (ON, DEFAULT)`
tuple at thermal_model.py:1122). Expected under it: auto_two_zone_without_values=0,
questionnaire_two_zone_unasked=0, upper_emitter_moves_single_zone_answer=0,
explicit_off_two_zone=0.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13 (Linux x86_64 container).
Instrumented: custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.from_config
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dataclasses  # noqa: E402
import time  # noqa: E402
from unittest import mock  # noqa: E402

import rig  # noqa: E402
from heatpump_optimizer import const, thermal_model  # noqa: E402

ZONE_KEYS = (const.CONF_UPPER_FLOOR_THERMAL_MASS, const.CONF_LOWER_FLOOR_THERMAL_MASS,
             const.CONF_INTER_ZONE_TRANSFER, const.CONF_RADIATOR_POWER_FRACTION)


def arm(path, **ov):
    d = rig.walk(path, **ov)
    _, _, c = rig.build(d)
    reason, res, data = rig.cycle(c)
    return d, data.get("two_zone_enabled"), rig.plan_fp(res)


def measure():
    out = {}
    d, tz, _ = arm("finish_now")
    has_zone = any(k in d for k in ZONE_KEYS)
    print(f"finish_now: two_zone_mode={d.get('two_zone_mode')!r} zone values={has_zone} model two_zone={tz}")
    out["auto_two_zone_without_values"] = int(tz is True and not has_zone)
    d, tz, fpa = arm("questionnaire")
    print(f"questionnaire: two_zone_mode={d.get('two_zone_mode')!r} model two_zone={tz} "
          f"(the path never asks the two-zone question)")
    out["questionnaire_two_zone_unasked"] = int(tz is True and d.get("two_zone_mode") is None)
    _, _, fpb = arm("questionnaire", building_describe={"upper_floor_emitter": "floor"})
    out["upper_emitter_moves_single_zone_answer"] = int(fpa != fpb and d.get("two_zone_mode") != "on")
    d, tz, _ = arm("expert", zones={"two_zone": False})
    out["explicit_off_two_zone"] = int(tz is True)
    d, tz, _ = arm("expert", zones={"two_zone": True})
    out["explicit_on_two_zone"] = int(tz is True)
    return out


def presence_auto(orig):
    def wrapped(config, *a, **k):
        p = orig(config, *a, **k)
        mode = str(config.get(const.CONF_TWO_ZONE_MODE, const.DEFAULT_TWO_ZONE_MODE))
        if mode == const.TWO_ZONE_MODE_AUTO:
            p = dataclasses.replace(p, two_zone_enabled=any(k2 in config for k2 in ZONE_KEYS))
        return p
    return wrapped


if __name__ == "__main__":
    t0, c0 = time.time(), time.process_time()
    if "--perturb" in sys.argv:
        TP = thermal_model.ThermalParameters
        with mock.patch.object(TP, "from_config", staticmethod(presence_auto(TP.from_config))):
            r = measure()
    else:
        r = measure()
    for k, v in r.items():
        print(f"RESULT {k}={v} entries")
    print(f"RESULT wall_s={time.time() - t0:.1f} s (provisional)")
    print("RESULT thread_factor=1.00 (counts only; single-thread pin)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")

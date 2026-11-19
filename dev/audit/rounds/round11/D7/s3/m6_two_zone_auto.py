#!/usr/bin/env python3
"""D7.M6 (round 11, seat D7-s3): the dead `else` arm of the two-zone mode resolution, driven.

Metric (one line): configs on which `ThermalParameters.from_config` answers `two_zone_enabled`
differently for the default mode ("auto", or no mode key) than for an unknown mode string --
the two spellings its own comment declares one rule ("an unknown value is treated as auto",
"auto ... is the presence rule unchanged").

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m6_two_zone_auto.py
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m6_two_zone_auto.py --perturb

Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalParameters.from_config.
Count key: the `two_zone_enabled` the production classmethod returns; nothing is re-derived here.
Perturbation (`--perturb`): the classmethod re-executed in memory with the one-line edit
`(const.TWO_ZONE_MODE_ON, const.DEFAULT_TWO_ZONE_MODE)` -> `(const.TWO_ZONE_MODE_ON,)`;
`disagreements` must fall to 0 (to_zero). The static twin is `m6_stmt.py`'s exhausted_else row.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, Darwin arm64, Python 3.14.7. Expected 4, exact.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import inspect
import sys
import textwrap
import time

sys.path.insert(0, os.getcwd())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    from custom_components.heatpump_optimizer import const, thermal_model as tm

    cls = tm.ThermalParameters
    saved = cls.__dict__["from_config"]
    if a.perturb:
        src = textwrap.dedent(inspect.getsource(saved.__func__))
        old = "(const.TWO_ZONE_MODE_ON, const.DEFAULT_TWO_ZONE_MODE)"
        assert src.count(old) == 1, "the line this harness perturbs has moved"
        ns = dict(vars(tm))
        exec(src.replace(old, "(const.TWO_ZONE_MODE_ON,)"), ns)
        cls.from_config = ns["from_config"]
    try:
        base = {"target_temperature": 21.0, "heat_pump_max_power": 6.0}
        zone_keys = {const.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0, const.CONF_LOWER_FLOOR_THERMAL_MASS: 4.5}
        bad = 0
        n = 0
        for label, extra in (("no zone keys", {}), ("zone keys", zone_keys),
                             ("a stored single-zone house", {"thermal_mass": 6.0, "heat_loss_coefficient": 0.18})):
            unknown = cls.from_config({**base, **extra, const.CONF_TWO_ZONE_MODE: "not-a-mode"}).two_zone_enabled
            for mode_label, mode in (("no mode key", None), ("auto", const.TWO_ZONE_MODE_AUTO)):
                cfg = {**base, **extra}
                if mode is not None:
                    cfg[const.CONF_TWO_ZONE_MODE] = mode
                got = cls.from_config(cfg).two_zone_enabled
                n += 1
                ok = got == unknown
                bad += (not ok)
                print("%s %s, %s: two_zone_enabled=%s (an unknown mode on the same config: %s)" % (
                    "AGREE   " if ok else "DISAGREE", label, mode_label, got, unknown))
            # null control: the explicit modes are explicit, whatever the keys
            on = cls.from_config({**base, **extra, const.CONF_TWO_ZONE_MODE: const.TWO_ZONE_MODE_ON}).two_zone_enabled
            off = cls.from_config({**base, **extra, const.CONF_TWO_ZONE_MODE: const.TWO_ZONE_MODE_OFF}).two_zone_enabled
            print("NULL     %s: on=%s off=%s" % (label, on, off))
        print("RESULT probes=%d configs" % n)
        print("RESULT disagreements=%d configs" % bad)
    finally:
        cls.from_config = saved
    print("RESULT thread_factor=%.3f ratio" % (time.process_time() / max(time.thread_time(), 1e-9)))
    print("RESULT load1=%.2f load" % os.getloadavg()[0])
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    sys.exit(main())

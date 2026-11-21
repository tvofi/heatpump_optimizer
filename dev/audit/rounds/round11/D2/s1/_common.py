"""Shared plumbing for the D2-s1 round-11 harnesses (not a harness itself).

Every harness pins the BLAS threads BEFORE importing this module (the pin must
precede the numpy import); this module only adds paths, builders and the
RESULT trailer the harness contract asks for.
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

BASELINE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"

_T0_PROC = time.process_time()
_T0_THREAD = time.thread_time()


def result(name: str, value, unit: str = "") -> None:
    print(f"RESULT {name}={value} {unit}".rstrip(), flush=True)


def _swapins() -> int:
    try:
        with open("/proc/vmstat") as fh:
            for line in fh:
                if line.startswith("pswpin "):
                    return int(line.split()[1])
    except OSError:
        pass
    return -1


def trailer() -> None:
    proc = time.process_time() - _T0_PROC
    thr = time.thread_time() - _T0_THREAD
    result("thread_factor", round(proc / thr, 4) if thr > 0 else 1.0)
    result("load1", round(os.getloadavg()[0], 2))
    result("swapins", _swapins())


def house_params(two_zone=False, dhw=False, **overrides):
    """ThermalParameters from tests/profiles.py:house with config overrides."""
    from profiles import house
    from heatpump_optimizer.thermal_model import ThermalParameters
    cfg = house(two_zone=two_zone, dhw=dhw)
    # "off" pins the single-zone model: at this baseline the default "auto"
    # resolves to two-zone regardless of the zone keys (a lead, not an M1 cell).
    cfg.setdefault("two_zone_mode", "on" if two_zone else "off")
    cfg.update(overrides)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    return p

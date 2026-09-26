#!/usr/bin/env python3
"""D3-s1-01 (V3 reach): is _dhw_inlet_c's lower bound reached with a genuine Home Assistant State,
and does mutant C0043 (coordinator.py:1371 `-5.0 <= value` -> `-5.0 < value`) change its output there?

METRIC: reach_delta = number of probe readings on which _dhw_inlet_c, fed a real
  homeassistant.core.State through a real StateMachine-shaped lookup, returns a different
  value with C0043 patched in versus the baseline function. Key: return value repr.
RUN:      PYTHONPATH=custom_components /root/venvha/bin/python tools/audit/round9/D3/verify-v3/D3-s1-01_reach.py [--null]
          (real HA 2026.2.3 venv, NO tests/hastub on the path). --null patches the unmutated source.
EXPECTED: reach_delta=2 (the -5.0 degC and 23 degF readings move: -5.0 -> None); --null -> 0.
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
MACHINE:  box G1-V3 (4 vCPU cloud container, Linux 6.18), CPython of /root/venvha
ROOT:     Path(".") -- run from the repository root.
PERTURBATION: C0043 applied by text substitution of the one line in the function source,
  re-compiled in the production module's namespace, swapped in with mock.patch.object. No file written.
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import typing

# Environment shim, not production: mashumaro (pulled in by homeassistant.helpers) touches
# typing.ByteString, which CPython 3.14 removed; HA 2026.2.3 on 3.14.0rc2 fails to import without it.
if not hasattr(typing, "ByteString"):
    typing.ByteString = bytes  # type: ignore[attr-defined]

import inspect
import sys
import textwrap
import time
from unittest import mock

import homeassistant  # genuine package, not the stub
from homeassistant.const import __version__ as HA_VERSION
from homeassistant.core import State
from homeassistant.util import dt as dt_util

from heatpump_optimizer import coordinator as co

assert "hastub" not in (homeassistant.__file__ or ""), homeassistant.__file__

t0p, t0 = time.process_time(), time.perf_counter()
null = "--null" in sys.argv
src = textwrap.dedent(inspect.getsource(co._dhw_inlet_c))
old = "-5.0 <= value <= 35.0"
assert src.count(old) == 1, "baseline line not found"
mut_src = src if null else src.replace(old, "-5.0 < value <= 35.0")
ns: dict = {}
exec(compile(mut_src, co.__file__, "exec"), co.__dict__, ns)
mutated = ns["_dhw_inlet_c"]


class _States:
    def __init__(self, st): self._st = st
    def get(self, eid): return self._st if eid == self._st.entity_id else None


class _Hass:
    def __init__(self, st): self.states = _States(st)


now = dt_util.utcnow()
readings = [("-5.1", "°C"), ("-5.0", "°C"), ("-4.9", "°C"), ("12.0", "°C"),
            ("35.0", "°C"), ("35.1", "°C"), ("23.0", "°F")]  # 23 degF == -5.0 degC
base_out, mut_out = [], []
for raw, unit in readings:
    st = State("sensor.dhw_inlet", raw, {"unit_of_measurement": unit},
               last_changed=now, last_reported=now, last_updated=now)
    h = _Hass(st)
    base_out.append(repr(co._dhw_inlet_c(h, "sensor.dhw_inlet")))
    with mock.patch.object(co, "_dhw_inlet_c", mutated):
        mut_out.append(repr(co._dhw_inlet_c(h, "sensor.dhw_inlet")))
print("HA_VERSION", HA_VERSION)
print("READINGS", readings)
print("BASE", base_out)
print("MUT ", mut_out)
delta = sum(a != b for a, b in zip(base_out, mut_out))
print(f"RESULT reach_delta={delta} count")
tp, tt = time.process_time() - t0p, time.perf_counter() - t0
print(f"RESULT thread_factor={tp / tt if tt > 1e-9 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except OSError:
    sw = "n/a"
print(f"RESULT swapins={sw}")

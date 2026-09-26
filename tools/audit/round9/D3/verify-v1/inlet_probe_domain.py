#!/usr/bin/env python3
"""D3-s1-01 verifier V1: can any existing test input observe mutant C0043 on _dhw_inlet_c?

METRIC: suite_inputs_differing = number of inlet readings the test suite feeds
  _dhw_inlet_c (enumerated below from tests/features.py ~18850 and ~45236-45305;
  goldens configure no inlet entity, only a static dhw_inlet_temperature) on which the
  mutant (`-5.0 <= value` -> `-5.0 < value`, coordinator.py:1371) returns a different
  value than the baseline. boundary_inputs_differing is the same count over a
  boundary probe set (the perturbation arm: it must be >=1 or the mutant is equivalent).
  suite_numeric_inputs_at_or_below_bound is a static count of numeric inlet
  literals <= -5.0 in the suite probe list (0 means no check can reach the bound).
RUN:      PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/verify-v1/inlet_probe_domain.py [--null]
EXPECTED: suite_inputs_differing=0, boundary_inputs_differing=2 (exact: -5.0 degC and 23 degF); --null -> both 0
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (evidence tree 6f51db2c)
MACHINE:  box G1-V1, 4 vCPU cloud container, Linux 6.18, CPython 3.14.0rc2
PERTURBATION: the mutant is built by an exact one-occurrence string replacement of the
  function's own source and exec'd in the production module's globals, in memory; --null
  re-execs the unmodified source through the same path.
"""
from __future__ import annotations

import os

for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

import inspect
import sys
import textwrap
from datetime import UTC, datetime, timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeHass, FakeState  # noqa: E402

import heatpump_optimizer.coordinator as coord  # noqa: E402

NULL = "--null" in sys.argv
OLD, NEW = "-5.0 <= value <= 35.0", "-5.0 < value <= 35.0"

src = textwrap.dedent(inspect.getsource(coord._dhw_inlet_c))
assert src.count(OLD) == 1, "production line moved"
ns: dict = {}
exec(compile(src if NULL else src.replace(OLD, NEW), coord.__file__, "exec"), coord.__dict__, ns)
mut, base = ns["_dhw_inlet_c"], coord._dhw_inlet_c

now = datetime.now(UTC)
# (value, unit, age) exactly as the suite feeds them
SUITE = [
    ("12.0", None, timedelta(minutes=30)),      # features ~18850 fresh
    ("12.0", None, timedelta(hours=48)),        # features ~18859 frozen
    ("50.0", "°F", timedelta(0)),               # features ~45244
    ("10.0", "°C", timedelta(0)),
    ("10.0", None, timedelta(0)),
    ("10", "°C", timedelta(days=2)),            # features ~45296 stale
    ("40.0", "°C", timedelta(0)),               # implausible high
    ("unknown", "°C", timedelta(0)),
]
BOUNDARY = [("-5.0", "°C", timedelta(0)), ("-4.9", "°C", timedelta(0)),
            ("-5.1", "°C", timedelta(0)), ("35.0", "°C", timedelta(0)),
            ("23.0", "°F", timedelta(0))]   # 23 degF == -5 degC exactly


def run(fn, v, unit, age):
    hass = FakeHass({"sensor.inlet": FakeState(v, unit=unit, last_updated=now - age)})
    try:
        return repr(fn(hass, "sensor.inlet"))
    except Exception as exc:  # noqa: BLE001
        return type(exc).__name__


def diff(cases):
    out = []
    for c in cases:
        b, m = run(base, *c), run(mut, *c)
        print(f"  {c[0]!r:>10} {c[1]!s:>4} base={b} mut={m}")
        out.append(b != m)
    return sum(out)


print("SUITE inputs")
s = diff(SUITE)
print("BOUNDARY inputs")
bd = diff(BOUNDARY)
low = sum(1 for v, _u, _a in SUITE
          if v.replace(".", "", 1).lstrip("-").isdigit() and float(v) <= -5.0)
print(f"RESULT suite_inputs_differing={s} count")
print(f"RESULT boundary_inputs_differing={bd} count")
print(f"RESULT suite_numeric_inputs_at_or_below_bound={low} count")
print("RESULT thread_factor=1.000")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")

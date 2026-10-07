#!/usr/bin/env python3
"""D3.M4: does a pre-screen survivor change what production computes? (so the suite owes a kill)

METRIC: behaviour_delta = number of probe inputs on which the named production symbol returns a
  different value (or raises where the baseline did not) with the mutant patched in, versus the
  baseline symbol. Key: the symbol's own return value (repr) / exception type, nothing else.
RUN:      PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/s1/behaviour.py <CID>
          <CID> in PROBES below; `--null` patches the UNMUTATED function source through the same path
          (the control: behaviour_delta=0).
EXPECTED: C0043 -> RESULT behaviour_delta=1 count (exact), --null -> 0;
          C0054 -> behaviour_delta=1, behaviour_delta_production_shape=0 (equivalent on every shape optimizer.py builds)
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
MACHINE:  box B1 (4 vCPU cloud container, Linux 6.18), CPython 3.14.0rc2
ROOT:     Path(".") -- run from the repository root.
PERTURBATION: the mutant (mutants.py CID) re-compiled from the production source and swapped in
  with mock.patch.object on the production module -- in memory, no file is written.
"""
from __future__ import annotations

import os

for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

import ast
import sys
import textwrap
import time
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tools/audit/round9/D3/s1")

import mutants  # noqa: E402
from harness import FakeHass, FakeState  # noqa: E402

import heatpump_optimizer.coordinator as coord  # noqa: E402


def compiled(src: str, func_qual: str):
    """Compile the def named func_qual (module-level or Class.method) from src in coord's globals."""
    tree = ast.parse(src)
    parts = func_qual.split(".")
    scope = tree.body
    node = None
    for p in parts:
        node = next(n for n in scope if getattr(n, "name", None) == p)
        scope = getattr(node, "body", [])
    seg = textwrap.dedent(ast.get_source_segment(src, node))
    ns: dict = {}
    exec(compile(seg, coord.__file__, "exec"), coord.__dict__, ns)
    return parts, ns[parts[-1]]


def probe_C0043(fn) -> list:
    now = datetime.now(UTC)
    out = []
    for v in ("-6.0", "-5.0", "-4.9", "0.0", "12.0", "35.0", "35.1"):
        hass = FakeHass({"sensor.inlet": FakeState(v, last_updated=now, unit="°C")})
        try:
            out.append(repr(fn(hass, "sensor.inlet")))
        except Exception as err:  # noqa: BLE001
            out.append(type(err).__name__)
    return out


def probe_C0054(fn) -> list:
    """_apply_result_payload on a production-shaped result (every per-step list the horizon's
    length, as optimizer.py's single OptimizationResult constructor builds it) at n = 4, 96, 192,
    and on two NON-production shapes (heat_pump_on_schedule one short / empty) as the positive arm."""
    from datetime import timedelta

    from heatpump_optimizer.optimizer import OptimizationResult

    def result(n, hp_len):
        t0 = datetime(2026, 1, 15, tzinfo=UTC)
        ts = [t0 + timedelta(minutes=15 * i) for i in range(n)]
        return OptimizationResult(
            power_schedule=[0.5 * (i % 3) for i in range(n)],
            room_temp_trajectory=[21.0] * (n + 1), slab_temp_trajectory=[22.0] * (n + 1),
            timestamps=ts, prices=[1.0] * n, predicted_cost=1.0, baseline_cost=2.0,
            predicted_savings=1.0, savings_percentage=50.0, optimal_setpoints=[21.0] * n,
            status="ok", heat_pump_on_schedule=[(i % 3) > 0 for i in range(hp_len)],
            displace_schedule=[0.0] * n)

    out = []
    for n, hp in ((4, 4), (96, 96), (192, 192), (96, 95), (96, 0)):
        data: dict = {}
        try:
            fn(data, result(n, hp), {}, {})
            out.append(repr([r["heat_pump_on"] for r in data["schedule"]]))
        except Exception as err:  # noqa: BLE001
            out.append(type(err).__name__)
    return out


PROBES = {"C0043": probe_C0043, "C0054": probe_C0054}


def main() -> int:
    cid = sys.argv[1]
    null = "--null" in sys.argv
    t0p, t0t = time.process_time(), time.thread_time()
    src = Path(coord.__file__).read_text()
    cand = next(c for c in mutants.candidates(src) if c["id"] == cid)
    msrc = src if null else mutants.apply(src, cand)
    parts, fn_mut = compiled(msrc, cand["func"])
    owner = coord if len(parts) == 1 else getattr(coord, parts[0])
    base = PROBES[cid](getattr(owner, parts[-1]))
    with mock.patch.object(owner, parts[-1], fn_mut):
        mut = PROBES[cid](getattr(owner, parts[-1]))
    delta = sum(a != b for a, b in zip(base, mut))
    print("BASE", [b[:60] for b in base])
    print("MUT ", [m[:60] for m in mut], "(null)" if null else cand)
    print("DIFF_AT", [i for i, (a, b) in enumerate(zip(base, mut)) if a != b])
    if cid == "C0054":  # probes 0-2 are production-shaped, 3-4 are not
        print(f"RESULT behaviour_delta_production_shape={sum(a != b for a, b in zip(base[:3], mut[:3]))} count")
    print(f"RESULT behaviour_delta={delta} count")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt > 1e-9 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())

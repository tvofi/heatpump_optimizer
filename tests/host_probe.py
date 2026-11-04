#!/usr/bin/env python3
"""The runner's speed, measured by fixed work: the unit critical_path_minutes
is priced in (R10-HOTFIX-CI-CRITPATH-4).

    python3 tests/host_probe.py            # the probe (CI: a step of its own)

Hosted runners differ ~2x on the same work (`tests / fast (3.14)` read
1008..2094 s over 60 push runs on one tree), so a job's wall reads which host
it drew. This script does the same pure-Python work on every host and checks
its own checksum, so its duration is the host's speed and nothing else. CI
runs it as a step named PROBE_STEP in each heavy `tests / *` job, after
actions/setup-python, so under the job's own matrix interpreter -- the
`(python X.Y)` the step's name carries, which selects PROBE_REFERENCE_S's
per-interpreter value -- and tests/ci_ratchet.py reads that step's duration
off the jobs API to price the job's work in reference-host seconds
(reference_work).

The work never changes: a change to ROUNDS or to work() changes the unit
every recorded critical_path_minutes is in, so CHECKSUM refuses it on
every CI run and tests/entities.py pins one round of it; a deliberate change
re-derives PROBE_REFERENCE_S on the fleet (tools/audit/seat/probe_bridge.py,
a new fleet.json) and re-records the budget in the same pull request.
"""
from __future__ import annotations

import sys
import time

ROUNDS = 1600
CHECKSUM = 173938904679337691


def work(rounds: int = ROUNDS) -> int:
    """Interpreter-bound work in the test suite's own shape: integer and float
    arithmetic, dict and list churn, string formatting. Deterministic."""
    acc = 0
    for r in range(rounds):
        table: dict[int, float] = {}
        seq: list[int] = []
        x = 0x9E3779B9 + r
        for i in range(60_000):
            x = (x * 1103515245 + 12345) & 0x7FFFFFFF
            k = x % 4093
            table[k] = table.get(k, 0.0) * 0.5 + (x & 0xFFFF) / 65536.0
            if i % 7 == 0:
                seq.append(k)
        seq.sort()
        s = ",".join(f"{v:.3f}" for v in list(table.values())[:400])
        acc = (acc * 1_000_003 + len(s) + sum(seq[::97]) + int(sum(table.values()) * 1000)) % (1 << 61)
    return acc


def main() -> int:
    t0 = time.perf_counter()
    got = work()
    dt = time.perf_counter() - t0
    if got != CHECKSUM:
        print(f"host_probe: checksum {got} is not the recorded {CHECKSUM}: the "
              "probe's work changed, so its duration is no longer the unit "
              "critical_path_minutes is recorded in (refusing)", file=sys.stderr)
        return 1
    print(f"host_probe: {dt:.3f} s for the fixed work (checksum {got})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""D10 log-when-unavailable (Silver) — how many ERROR records N failed polls emit.

METRIC: count of logging records at ERROR level emitted by
custom_components.heatpump_optimizer.coordinator over N=10 consecutive failed
price fetches, followed by one successful fetch, driven through the real
coordinator instance rather than read off the source.

RUN (from the export root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D10/log_when_unavailable.py

EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697):
    RESULT error_records_over_10_failures=1   (tolerance 0)
    RESULT debug_records_over_10_failures=9   (tolerance 0)
    RESULT info_records_on_recovery=1         (tolerance 0)
    RESULT error_records_after_recovery_and_10_more=1  (tolerance 0)
  The rule requires "log only once in total to avoid spamming the logs", and
  one log when the service comes back. 10 ERRORs would be a violation; 1 is
  the rule.
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, Python 3.11.5.

INSTRUMENTED SYMBOL:
    heatpump_optimizer.coordinator.HeatPumpOptimizerCoordinator._tibber_fetch_failed
    heatpump_optimizer.coordinator.HeatPumpOptimizerCoordinator._tibber_fetch_recovered
PERTURBATION: delete the `if not self._tibber_outage_cycles:` guard in
    _tibber_fetch_failed (log ERROR unconditionally); error_records rises
    1 -> 10 and debug_records falls 9 -> 0.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import logging  # noqa: E402
import sys  # noqa: E402

# tests/harness.py puts "tests" and "custom_components" on sys.path, which is
# how every script in this suite reaches the package: as `heatpump_optimizer`,
# not `custom_components.heatpump_optimizer` (there is no `custom_components`
# package -- tests/deployment_shape.py is the check that pins that layout).
sys.path.insert(0, os.path.join(os.getcwd(), "tests"))

from harness import FakeHass, FakeEntry  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from homeassistant.helpers.update_coordinator import UpdateFailed  # noqa: E402

HeatPumpOptimizerCoordinator = coord_mod.HeatPumpOptimizerCoordinator


class _Collector(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def _counts(records, since=0):
    out = {"ERROR": 0, "WARNING": 0, "INFO": 0, "DEBUG": 0}
    for r in records[since:]:
        out[r.levelname] = out.get(r.levelname, 0) + 1
    return out


def main() -> int:
    cfg = {"tibber_token": "x", "weather_entity": "weather.home"}
    coord = HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data=cfg))

    log = logging.getLogger(coord_mod.__name__)  # the module's own logger
    handler = _Collector()
    log.addHandler(handler)
    prev_level, prev_prop = log.level, log.propagate
    log.setLevel(logging.DEBUG)
    log.propagate = False
    try:
        for _ in range(10):
            try:
                coord._tibber_fetch_failed("Error fetching Tibber prices: boom")
            except UpdateFailed:
                pass
        outage = _counts(handler.records)
        mark = len(handler.records)

        coord._tibber_fetch_recovered()
        recovery = _counts(handler.records, mark)
        mark = len(handler.records)

        for _ in range(10):
            try:
                coord._tibber_fetch_failed("Error fetching Tibber prices: boom")
            except UpdateFailed:
                pass
        second = _counts(handler.records, mark)
    finally:
        log.removeHandler(handler)
        log.setLevel(prev_level)
        log.propagate = prev_prop

    print(f"RESULT error_records_over_10_failures={outage['ERROR']} records")
    print(f"RESULT debug_records_over_10_failures={outage['DEBUG']} records")
    print(f"RESULT info_records_on_recovery={recovery['INFO']} records")
    print(f"RESULT error_records_after_recovery_and_10_more={second['ERROR']} records")
    print(f"RESULT debug_records_after_recovery_and_10_more={second['DEBUG']} records")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=n/a (record counts, not timings)")
    ok = (outage["ERROR"] == 1 and outage["DEBUG"] == 9
          and recovery["INFO"] == 1 and second["ERROR"] == 1)
    print("VERDICT log-when-unavailable=" + ("done" if ok else "todo"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

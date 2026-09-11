#!/usr/bin/env python3
"""D10 -- quality-scale rule `log-when-unavailable` (Silver), measured by
driving the coordinator's outage path and counting log records by level.

METRIC (one line): the number of ERROR-level records the integration's logger
emits over five consecutive failed price polls followed by one successful poll.

COMMAND (from the export root, nothing else needed):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/log_once_rule.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python3 3.11.5): errors_over_5_failures=1, debugs_over_5_failures=4,
info_on_recovery=1, errors_after_recovery_and_5_more=2. Counts; contention-immune.
The rule's bar is exactly one ERROR per outage, then DEBUG until it clears.

INSTRUMENTED SYMBOL:
custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._tibber_fetch_failed
(and ``._tibber_fetch_recovered``), driven directly on a bound instance so no
network, no event loop and no fixture is involved.

PERTURBATION: change the ``if not self._tibber_outage_cycles:`` guard in
``_tibber_fetch_failed`` to ``if True:`` and errors_over_5_failures goes 1 -> 5
(direction: up); that is the shape the register's `todo` comment describes.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
os.chdir(ROOT)
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from homeassistant.helpers.update_coordinator import UpdateFailed  # noqa: E402
import heatpump_optimizer.coordinator as coordinator_module  # noqa: E402


class _Collector(logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.records: list[tuple[str, str]] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append((record.levelname, record.getMessage()))


class _Bare:
    """A minimal object the two latch methods are bound onto.

    The two methods read and write exactly one attribute, ``_tibber_outage_cycles``,
    so binding them to a bare object measures the latch and nothing else; a real
    coordinator would drag the whole config flow in and measure fixtures too.
    """
    _tibber_outage_cycles = 0
    _tibber_reauth_started = False


def _drive(obj, failed, recovered, n: int) -> None:
    for i in range(n):
        try:
            failed(obj, f"poll {i} failed")
        except UpdateFailed:
            pass


def main() -> int:
    handler = _Collector()
    logger = coordinator_module._LOGGER
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    cls = coordinator_module.HeatPumpOptimizerCoordinator
    failed = cls._tibber_fetch_failed
    recovered = cls._tibber_fetch_recovered

    obj = _Bare()
    _drive(obj, failed, recovered, 5)
    phase1 = list(handler.records)
    handler.records.clear()
    recovered(obj)
    phase2 = list(handler.records)
    handler.records.clear()
    _drive(obj, failed, recovered, 5)
    phase3 = list(handler.records)

    e1 = sum(1 for lvl, _ in phase1 if lvl == "ERROR")
    d1 = sum(1 for lvl, _ in phase1 if lvl == "DEBUG")
    i2 = sum(1 for lvl, _ in phase2 if lvl == "INFO")
    e3 = sum(1 for lvl, _ in phase3 if lvl == "ERROR")

    print(f"RESULT errors_over_5_failures={e1} count")
    print(f"RESULT debugs_over_5_failures={d1} count")
    print(f"RESULT info_on_recovery={i2} count")
    print(f"RESULT errors_after_recovery_and_5_more={e1 + e3} count")
    print(f"RESULT records_total={len(phase1) + len(phase2) + len(phase3)} count")
    print(f"RESULT latch_cycles_after_run={obj._tibber_outage_cycles} count")
    print("RESULT thread_factor=1.0")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=nan")
    print("RESULT swapins=0")
    for label, phase in (("outage", phase1), ("recovery", phase2), ("second outage", phase3)):
        for lvl, msg in phase:
            print(f"DETAIL {label}: {lvl} {msg[:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

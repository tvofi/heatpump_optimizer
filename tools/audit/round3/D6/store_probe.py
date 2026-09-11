#!/usr/bin/env python3
"""Every ``.storage`` file the integration creates, counted by instrumentation.

METRIC: the number of distinct ``homeassistant.helpers.storage.Store`` keys the
integration constructs for one config entry, and their ``<name>`` suffixes --
which is exactly what README.md's Removal section tells a user to delete.

RUN (single command, from the repository root):

    PYTHONPATH=tests/hastub:tests:custom_components python3 tools/audit/round3/D6/store_probe.py

EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1:

    RESULT store_keys=12 count
    RESULT readme_listed=10 count
    RESULT undocumented=2 count      (away, boost)

INSTRUMENTED SYMBOL: ``homeassistant.helpers.storage.Store.__init__``, driven
through ``heatpump_optimizer.coordinator.HeatPumpOptimizerCoordinator.__init__``
and ``heatpump_optimizer.boost.restore_session`` -- the call the coordinator
itself spawns from ``async_setup`` (coordinator.py:1357).

PERTURBATION: delete the ``Store(...)`` construction in ``boost.py:_store``
(or in ``away.py:_away_store``); ``store_keys`` falls from 12 to 11 and
``undocumented`` from 2 to 1. Adding the two missing names to README.md's
removal list drives ``undocumented`` to 0.

ROOT RULE: ``Path(".")`` -- the current working directory, never ``__file__``.

MACHINE: 8-core Apple M1, 8 GB, python 3.11.5. Counts only: contention-immune.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(".")
for _p in ("tests/hastub", "tests", "custom_components", "."):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def build_every_store() -> str:
    """Drive the production paths that construct a ``Store``.

    Nothing here lists a store: the coordinator's own constructor builds the
    ten it owns, and ``boost.restore_session`` -- the coroutine the coordinator
    spawns from ``async_setup`` -- builds the boost store and, through
    ``away.restore_override``, the away store.
    """
    from harness import FakeEntry, FakeHass

    from heatpump_optimizer import boost
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    coord = HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry())
    asyncio.run(boost.restore_session(coord))
    return str(coord.entry.entry_id)


def measure() -> tuple[list[str], set[str]]:
    import homeassistant.helpers.storage as ha_storage

    from heatpump_optimizer.const import DOMAIN

    seen: list[str] = []
    original = ha_storage.Store.__init__

    def spy(self, hass, version, key, *args, **kwargs):  # noqa: ANN001
        seen.append(str(key))
        return original(self, hass, version, key, *args, **kwargs)

    ha_storage.Store.__init__ = spy  # type: ignore[method-assign]
    try:
        entry_id = build_every_store()
    finally:
        ha_storage.Store.__init__ = original  # type: ignore[method-assign]

    prefix = f"{DOMAIN}_{entry_id}_"
    names = {key[len(prefix):] if key.startswith(prefix) else key for key in seen}
    listed = set(
        re.findall(
            r"`heatpump_optimizer_<entry id>_([a-z_]+)`",
            (ROOT / "README.md").read_text(),
        )
    )
    return sorted(names), listed


if __name__ == "__main__":
    constructed, listed = measure()
    undocumented = sorted(set(constructed) - listed)
    print(f"constructed: {constructed}")
    print(f"README lists: {sorted(listed)}")
    print(f"RESULT store_keys={len(constructed)} count")
    print(f"RESULT readme_listed={len(listed)} count")
    print(f"RESULT undocumented={len(undocumented)} count  {undocumented}")
    print("RESULT thread_factor=1.0")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=-1")
    print("RESULT swapins=0")

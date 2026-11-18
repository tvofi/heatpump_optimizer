"""Does an UNPARSEABLE stored legionella ``last_cycle`` read as a fresh install?

Measures ``LegionellaGuard.async_load`` for three stored payloads, each on a
fresh guard with a fake store: ``valid`` (2026-01-10), ``absent`` ({}), and
``garbage`` ("not-a-time", "2026-13-45T99:99:99"). Per arm it reports whether
``last_cycle`` became now, whether the store was written, and how many
WARNING+ records the heatpump_optimizer loggers emitted during the load.

Run (repo root): PYTHONPATH=tests/hastub python3 \
    dev/audit/rounds/round11/D14/N-silent-zero/legionella_unparseable.py [--perturb]

Expected baseline: valid_kept=1; both garbage arms last_cycle==now, saved=1,
warnings=0, so unparseable_read_as_fresh=2.
Perturbation (--perturb): wrap async_load so a non-empty string last_cycle
that stored_instant cannot parse logs a WARNING first; expected
unparseable_read_as_fresh=0.
"""
from __future__ import annotations

import asyncio
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
for p in (ROOT / "tests", ROOT / "tests" / "hastub", ROOT / "custom_components"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import heatpump_optimizer.legionella as lm  # noqa: E402
from harness import FakeHass  # noqa: E402
from heatpump_optimizer.disinfection import DisinfectionSwitch  # noqa: E402
from heatpump_optimizer.legionella import LegionellaGuard  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
from homeassistant.util import dt as dtu  # noqa: E402

NOW = datetime(2026, 1, 20, 12, 0, tzinfo=timezone.utc)
PERTURB = "--perturb" in sys.argv


class FakeStore:
    def __init__(self, data):
        self.data, self.saved = data, []

    async def async_load(self):
        return self.data

    async def async_save(self, data):
        self.saved.append(data)

    async def async_wait_for_read(self):
        return None


class Collect(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.records = []

    def emit(self, record):
        self.records.append(record)


if PERTURB:
    _orig = LegionellaGuard.async_load

    async def _wrapped(self):
        raw = ((await self.store.async_load()) or {}).get("last_cycle")
        if (isinstance(raw, str) and raw
                and lm.stored_instant(raw, dtu.DEFAULT_TIME_ZONE) is None):
            lm._LOGGER.warning("Unparseable legionella last_cycle %r", raw)
        await _orig(self)

    LegionellaGuard.async_load = _wrapped


def make_guard(data):
    params = ThermalParameters()
    guard = LegionellaGuard(
        FakeHass(), "probe", lambda: params, {},
        action=lambda: {},
        disinfect=DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None),
        dhw_blocked=lambda: False,
    )
    guard.store = FakeStore(data)
    return guard


async def run_arm(name, data):
    guard = make_guard(data)
    h = Collect()
    root = logging.getLogger()
    root.addHandler(h)
    try:
        await guard.async_load()
    finally:
        root.removeHandler(h)
    warns = [r for r in h.records if "heatpump_optimizer" in r.name]
    lc = guard.last_cycle
    eq = int(lc == NOW)
    print(f"ARM {name} last_cycle={lc.isoformat() if lc else None} "
          f"equals_now={eq} saved={int(bool(guard.store.saved))} "
          f"warnings={len(warns)}")
    return lc, eq, len(warns)


async def main():
    dtu.freeze(NOW)
    arms = [
        ("valid", {"last_cycle": "2026-01-10T12:00:00+00:00"}),
        ("absent", {}),
        ("garbage", {"last_cycle": "not-a-time"}),
        ("garbage2", {"last_cycle": "2026-13-45T99:99:99"}),
    ]
    res = {}
    for name, data in arms:
        res[name] = await run_arm(name, data)
    fresh = sum(1 for n in ("garbage", "garbage2")
                if res[n][1] == 1 and res[n][2] == 0)
    v = res["valid"][0]
    kept = int(v is not None and v.date().isoformat() == "2026-01-10")
    print(f"RESULT unparseable_read_as_fresh={fresh} count")
    print(f"RESULT valid_kept={kept} count")


asyncio.run(main())

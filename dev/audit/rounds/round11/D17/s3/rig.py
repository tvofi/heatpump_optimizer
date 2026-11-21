"""D17-s3 shared rig: a real entry set up the way Home Assistant sets one up.

Not a harness on its own; the harnesses beside it import it. Run from the
export root with PYTHONPATH=tests/hastub. Builds a real
HeatPumpOptimizerCoordinator through ``__init__.async_setup_entry``
(``tests/harness.py:ha_setup_entry``) on a FakeHass with the readings
``tests/entities.py:_honest_coordinator`` seeds (indoor 21.4, outdoor -3.0,
a 180 l tank) plus an offline entity price feed (``_seed_prices``), so every
service dispatches through its registered schema to its real handler.
A restart is simulated as Home Assistant has one: unload, a new hass holding
the same states, a new entry object with the same id, data and options; the
stub Store's disk is shared across instances (tests/hastub storage.py).
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

import sys
import tempfile
import time

sys.path[:0] = ["tests", "custom_components"]
os.environ.setdefault("HPO_PLANDATA", tempfile.mkdtemp(prefix="d17s3_"))

from datetime import timedelta  # noqa: E402

from harness import (  # noqa: E402
    FakeEntry,
    FakeHass,
    FakeState,
    ha_setup_entry,
    ha_unload_entry,
)

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

DOMAIN = const.DOMAIN

BASE_STATES = {
    "sensor.indoor": ("21.4", {}),
    "sensor.outdoor": ("-3.0", {}),
}


START = None


def freeze(when=None):
    """Pin the stub clock (homeassistant.util.dt.freeze); default a fixed
    winter evening so every run plans the same horizon."""
    from datetime import datetime, timezone

    global START
    START = when or datetime(2026, 1, 14, 17, 0, tzinfo=timezone.utc)
    dt_util.freeze(START)
    return START


def advance(minutes):
    """Move the frozen clock forward."""
    now = dt_util.now()
    dt_util.freeze(now + timedelta(minutes=minutes))
    return dt_util.now()


def price_rows(hours=48, base=0.5, now=None):
    now = (now or dt_util.now()).replace(minute=0, second=0, microsecond=0)
    return [
        {
            "start": (now + timedelta(hours=h)).isoformat(),
            "value": round(base + 0.1 * (h % 4), 3),
        }
        for h in range(hours)
    ]


def seed(hass, base=0.5, hours=48, extra_states=None):
    for eid, (state, attrs) in BASE_STATES.items():
        hass.states.set(eid, FakeState(state, attributes=dict(attrs)))
    hass.states.set(
        "sensor.prices",
        FakeState(str(base), attributes={"raw_today": price_rows(hours, base)}),
    )
    for eid, st in (extra_states or {}).items():
        hass.states.set(eid, st)


def base_config(dhw=True, **extra):
    cfg = {
        "price_source": "entity",
        "price_entity": "sensor.prices",
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    }
    if dhw:
        cfg[const.CONF_DHW_TANK_VOLUME] = 180.0
    cfg.update(extra)
    return cfg


class Install:
    """One entry on one hass; ``restart()`` swaps both for fresh ones."""

    def __init__(self, data=None, options=None, entry_id="d17s3", states=None):
        self.entry_id = entry_id
        self.fired = []
        self.tasks = []
        self.extra_states = states or {}
        self.hass = self._hass()
        seed(self.hass, extra_states=self.extra_states)
        self.entry = FakeEntry(data=data if data is not None else base_config(),
                               options=options, entry_id=entry_id)

    fired: list = []

    def _hass(self):
        """A FakeHass whose bus records fired events (FakeBus has no async_fire)."""
        hass = FakeHass()
        fired = self.fired

        def async_fire(event_type, data=None, *a, **k):
            fired.append((event_type, dict(data or {})))

        hass.bus.async_fire = async_fire
        # FakeHass.async_create_task closes the coroutine; Home Assistant runs
        # it. The startup store reads (mode, away, manual plan ...) and the
        # refresh an action requests ride on it, so run them for real.
        tasks = self.tasks

        def async_create_task(coro, *a, **k):
            import asyncio

            task = asyncio.get_running_loop().create_task(coro)
            tasks.append(task)
            return task

        hass.async_create_task = async_create_task
        hass.async_create_background_task = lambda coro, *a, **k: async_create_task(coro)
        return hass

    async def settle(self, rounds=20):
        """Await every task production spawned, and any they spawn in turn."""
        import asyncio

        for _ in range(rounds):
            pending = [t for t in self.tasks if not t.done()]
            if not pending:
                await asyncio.sleep(0)
                if not [t for t in self.tasks if not t.done()]:
                    break
                continue
            await asyncio.gather(*pending, return_exceptions=True)

    async def setup(self, settle=True):
        ok = await ha_setup_entry(integration, self.hass, self.entry)
        assert ok, "setup failed"
        if settle:
            await self.settle()
        return self.coord

    @property
    def coord(self):
        return self.entry.runtime_data

    async def cycle(self):
        """One coordinator update cycle with a solve (what the interval runs)."""
        await self.coord.async_refresh()
        return self.coord.data

    async def call(self, service, data=None, settle=True):
        out = await self.hass.services.async_call(DOMAIN, service, data or {})
        if settle:
            await self.settle()
        return out

    async def restart(self):
        """Unload, then a fresh hass and entry object carrying the same config."""
        await self.settle()
        await ha_unload_entry(integration, self.hass, self.entry)
        await self.settle()
        old_states = self.hass.states
        data, options = dict(self.entry.data), dict(self.entry.options)
        self.hass = self._hass()
        seed(self.hass, extra_states=self.extra_states)
        # carry any state a test set on the old hass
        try:
            for eid, st in getattr(old_states, "_states", {}).items():
                self.hass.states.set(eid, st)
        except Exception:  # noqa: BLE001
            pass
        self.entry = FakeEntry(data=data, options=options, entry_id=self.entry_id)
        await self.setup()
        return self.coord

    async def reload(self):
        """What the entry's update listener does after an options write:
        unload, then set the entry up again on the same hass (the in-process
        plan handover in hass.data survives, as it does in Home Assistant)."""
        await self.settle()
        await ha_unload_entry(integration, self.hass, self.entry)
        await self.settle()
        data, options = dict(self.entry.data), dict(self.entry.options)
        self.entry = FakeEntry(data=data, options=options, entry_id=self.entry_id)
        if self.entry not in self.hass.config_entries.entries:
            self.hass.config_entries.entries[:] = [
                e for e in self.hass.config_entries.entries if e.entry_id != self.entry_id
            ] + [self.entry]
        await self.setup()
        return self.coord

    def entities(self):
        """Every entity the six platforms add for this entry, by entity_id."""
        import asyncio  # noqa: F401
        from heatpump_optimizer import (
            binary_sensor,
            button,
            climate,
            datetime as hpo_datetime,
            sensor,
            switch,
        )

        added = []

        def add(ents, *_a, **_k):
            for e in ents:
                e.hass = self.hass
            added.extend(ents)

        return added, add, (sensor, binary_sensor, button, climate, switch, hpo_datetime)

    async def all_entities(self):
        added, add, mods = self.entities()
        for m in mods:
            await m.async_setup_entry(self.hass, self.entry, add)
        return {e.entity_id: e for e in added}


def footer(t0_cpu, t0_thread):
    """The contract's closing RESULT lines."""
    proc = time.process_time() - t0_cpu
    thr = time.thread_time() - t0_thread
    print(f"RESULT thread_factor={proc / thr if thr > 0 else 1.0:.3f}")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=-1")
    swap = -1
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                swap = int(line.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={swap}")

"""Shared driver for D9-s2's harnesses (retained.py, payload.py); not a harness itself.

Drives the REAL coordinator cycle ``HeatPumpOptimizerCoordinator._async_update_data``
N times on an advancing frozen clock, with every entity of the six platforms
built by its real ``async_setup_entry``, the way ``tests/replay.py:run_fixture``
does (its ``InProcessWorker`` substitutes the child interpreter; FakeHass runs
executor jobs inline -- fine for bytes, never for GIL timing).

Inputs: a fixture's entry config (``owner`` = tests/replay/owner-2026-10-30-away.json,
the richest real configuration in the tree; ``synthetic`` = synthetic-dhw-only.json)
with ``optimization_interval`` forced to the options flow's minimum, 10 min. Each
recorded input is replayed from its row at the clock wrapped into the fixture
window, re-stamped to the cycle instant, numeric temperatures riding a daily
sine so the learners see a moving house. Prices and the weather forecast are
synthesised deterministically (24 h sine plus a day-indexed ripple).
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import importlib
import json
import math
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

FIXTURES = {
    "owner": ROOT / "tests" / "replay" / "owner-2026-10-30-away.json",
    "synthetic": ROOT / "tests" / "replay" / "synthetic-dhw-only.json",
}
INTERVAL_MIN = 10  # config_flow.py: _number(10, 120, ...) for optimization_interval
CYCLES_PER_DAY = 24 * 60 // INTERVAL_MIN  # 144
CYCLES_PER_YEAR = 365 * CYCLES_PER_DAY  # 52,560 -- D9-criteria B4

RUN_SPAWNS = frozenset({
    "restore_session", "async_load_profile", "async_load_draws", "async_load",
    "_async_load_thermal_learning", "_async_load_price_model", "_async_load_accuracy",
    "_async_load_energy_totals", "_async_load_ledger", "_async_load_snapshots",
    "_async_setup_peak_guard", "_async_setup_defrost_watch", "_async_load_manual_plan",
})

TEMP_DAILY_AMPL = {"sensor.outdoor_temp": 4.0}
DEFAULT_TEMP_AMPL = 0.6


def _ts(raw):
    return datetime.fromisoformat(raw) if raw else None


def _price(t_utc: datetime) -> float:
    h = t_utc.hour + t_utc.minute / 60.0
    day = t_utc.toordinal()
    return round(1.0 + 0.6 * math.sin(2 * math.pi * (h - 6) / 24.0)
                 + 0.1 * ((day * 7 + t_utc.hour) % 5) / 5.0, 4)


class Driver:
    def __init__(self, fixture: str = "owner", overrides: dict | None = None, worker: str = "child",
                 step_minutes: int | None = None):
        import replay as rp  # tests/replay.py: guarded __main__
        from homeassistant.util import dt as dt_util
        from harness import FakeEntry, FakeHass, FakeState
        import heatpump_optimizer as integration
        from heatpump_optimizer import const
        from heatpump_optimizer import coordinator as cm

        self.rp, self.dt_util, self.FakeState, self.cm = rp, dt_util, FakeState, cm
        fx = json.loads(FIXTURES[fixture].read_text())
        self.fx = fx
        self.rec = rp.Recording(fx["states"])
        data = dict(fx["entry"]["data"])
        options = dict(fx["entry"]["options"])
        options[const.CONF_OPTIMIZATION_INTERVAL] = INTERVAL_MIN
        options.update(overrides or {})
        self.config = {**data, **options}
        self.w_start = _ts(fx["window"]["start"])
        self.w_end = _ts(fx["window"]["end"])
        self.window = self.w_end - self.w_start
        self.t0 = dt_util.as_utc(self.w_start)
        # step_minutes > INTERVAL_MIN is the time-warp arm: the configured interval stays
        # 10 min, the clock jumps further between cycles so month-keyed state ages.
        self.step = timedelta(minutes=step_minutes or INTERVAL_MIN)

        # worker="child": production's own _ensure_worker child interpreter, so the solver's
        # transient allocations live where they live in production, not in this process.
        # worker="inprocess": tests/replay.py's InProcessWorker (solver CPU on this clock).
        if worker == "inprocess":
            w = rp.InProcessWorker()
            cm._ensure_worker = lambda: w

        class QuietHass(FakeHass):
            def async_create_task(self, coro, name=None, eager_start=None):
                # restore_session and the coordinator's deferred store loads
                # (coordinator.py __init__: the ``for load in (...)`` spawns) run now,
                # as they complete in production before the first cycles: a load left
                # unrun keeps e.g. wear.StartCounter.queued alive (its restore never
                # comes), which reads as retained growth production does not have.
                # Every other spawn is closed exactly as FakeHass does.
                if getattr(coro, "__name__", "") in RUN_SPAWNS:
                    asyncio.run(coro)
                    return None
                return super().async_create_task(coro)

        hass = QuietHass()
        self.hass = hass
        weather_id = self.config.get(const.CONF_WEATHER_ENTITY)

        async def forecasts(call):
            now = dt_util.as_utc(dt_util.now())
            out = []
            for h in range(48):
                t = now + timedelta(hours=h)
                hh = t.hour + t.minute / 60.0
                out.append({"datetime": t.isoformat(),
                            "temperature": round(2.0 + 4.0 * math.sin(2 * math.pi * (hh - 9) / 24.0), 2),
                            "wind_speed": 3.0, "precipitation": 0.0, "condition": "cloudy"})
            return {weather_id: {"forecast": out}}

        if weather_id:
            hass.services.async_register("weather", "get_forecasts", forecasts)

        entry = FakeEntry(data=data, options=options)
        self.entry = entry
        coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
        entry.runtime_data = coord

        async def no_solar_fetch() -> None:
            coord._open_meteo = None

        coord._fetch_solar_forecast = no_solar_fetch
        if not cm._entity_price_source(self.config):
            async def synth_prices() -> None:
                now = dt_util.now()
                day0 = now.replace(hour=0, minute=0, second=0, microsecond=0)
                span = 2 if now.hour >= 13 else 1
                rows, t = [], dt_util.as_utc(day0)
                while t < day0 + timedelta(days=span):
                    rows.append({"total": _price(t), "starts_at": dt_util.as_local(t).isoformat(),
                                 "level": "NORMAL"})
                    t += timedelta(minutes=15)
                coord._prices = rows

            coord._fetch_tibber_prices = synth_prices
        self.coord = coord
        entities: list = []
        for platform in integration.PLATFORM_LIST:
            module = importlib.import_module(f"heatpump_optimizer.{str(platform)}")
            asyncio.run(module.async_setup_entry(hass, entry, entities.extend))
        self.entities = entities
        self.price_entity = self.config.get(const.CONF_PRICE_ENTITY) or "sensor.price"
        self.n_errors = 0
        self.cycles = 0
        self.errors: list[str] = []

    def _inputs(self, t: datetime) -> None:
        dt_util = self.dt_util
        wrapped = self.w_start + (t - self.t0) % self.window
        hh = t.hour + t.minute / 60.0
        for entity_id in self.fx["inputs"]:
            if entity_id == self.price_entity:
                # Nord Pool shape (price_model.prices_from_entity_attributes): local today
                # and, from 13:00, tomorrow, hourly, synthesised by _price.
                state = str(_price(t))
                loc = dt_util.as_local(t)
                day0 = loc.replace(hour=0, minute=0, second=0, microsecond=0)
                attrs = {"unit_of_measurement": "SEK/kWh", "currency": "SEK"}
                for key, off in (("raw_today", 0), ("raw_tomorrow", 1)):
                    if off and loc.hour < 13:
                        attrs[key] = []
                        continue
                    rows = []
                    for h in range(24):
                        st = dt_util.as_local(dt_util.as_utc(day0) + timedelta(days=off, hours=h))
                        rows.append({"start": st.isoformat(), "end": (st + timedelta(hours=1)).isoformat(),
                                     "value": _price(dt_util.as_utc(st))})
                    attrs[key] = rows
            else:
                row = self.rec.at(entity_id, wrapped)
                if row is None:
                    continue
                _u, state, attrs, _r = row
                if (attrs or {}).get("device_class") == "temperature":
                    try:
                        v = float(state)
                        amp = TEMP_DAILY_AMPL.get(entity_id, DEFAULT_TEMP_AMPL)
                        state = f"{v + amp * math.sin(2 * math.pi * (hh - 9) / 24.0):.2f}"
                    except ValueError:
                        pass
            self.hass.states.set(entity_id, self.FakeState(
                state, last_updated=t - timedelta(minutes=1), last_reported=t, attributes=attrs))

    def now(self) -> datetime:
        return self.t0 + self.step * self.cycles

    def cycle(self) -> dict:
        t = self.now()
        self.dt_util.freeze(t)
        # FakeServices.calls is the test double's own log of every service call; it is
        # not production state and would read as retained growth.
        self.hass.services.calls.clear()
        self._inputs(t)
        try:
            data = asyncio.run(self.coord._async_update_data())
            self.coord.data = data
            self.coord.last_update_success = True
        except Exception as err:  # noqa: BLE001
            self.n_errors += 1
            if len(self.errors) < 5:
                self.errors.append(f"{t.isoformat()}: {type(err).__name__}: {err}")
            self.coord.last_update_success = False
            data = self.coord.data or {}
        self.cycles += 1
        return data

    def sweep(self) -> list[dict]:
        errs: list[str] = []
        out = self.rp.sweep(self.entities, (self.coord.data or {}).get("current_action") or {},
                            errs, self.now())
        self.n_errors += len(errs)
        self.errors.extend(errs[: max(0, 5 - len(self.errors))])
        return out

    def close(self) -> None:
        self.dt_util.freeze(None)
        proc = getattr(self.cm, "_PROCESS_WORKER", None)
        if proc is not None and hasattr(proc, "stdin"):
            try:
                proc.stdin.close()
                proc.wait(timeout=30)
            except Exception:  # noqa: BLE001
                proc.kill()


def load1() -> float:
    try:
        return float(Path("/proc/loadavg").read_text().split()[0])
    except OSError:
        return float(os.getloadavg()[0])


def swapins() -> int:
    try:
        for line in Path("/proc/vmstat").read_text().splitlines():
            if line.startswith("pswpin "):
                return int(line.split()[1])
    except OSError:
        pass
    return 0

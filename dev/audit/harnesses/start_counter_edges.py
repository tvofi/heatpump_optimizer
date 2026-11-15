"""R10-START-COUNTER-EDGES harness: what the compressor start counter counts on
the sampled path (the base) and on the running-signal edge path (the head),
on the same synthetic meter traces through the production coordinator.

Part D of Bankaifan's outside pull request 3420. No finder harness exists
(an outside report); these arms are the build's own. Each arm replays meter
state changes (one reading a minute, delivered only when the value changes)
and a refresh every default optimization interval. On a tree with the
sampled path a refresh is ``_update_current_state`` then
``_observe_compressor_start``, which is what ``_record_accuracy`` runs once
per refresh; on a tree with ``running_signal`` the coordinator's own
listener, confirm timer and per-refresh re-read count.

  control     a meter-only trace whose every on and off phase spans at least
              two refresh periods: starts counted (three on phases)
  perturbed   the same trace with one 5-minute stop and restart inside one
              refresh period: starts counted
  restored    one start before the ledger load lands, over a stored lifetime
              of 7: the lifetime after the load
  s7_60s      an element cut-in with the compressor off on a meter averaging
              over 60 s, at 6 offsets inside the window: false starts (offset
              0 fills its window, so its first report is already over)
  s7_30s      the same on a 30 s averaging meter, 6 offsets: false starts
  s7r_60s     s7_60s with a refresh every period, one landing between the
              partial's confirmation and over, the element running three
              periods and cutting out through a partial: false starts
  s7r_30s     the same on a 30 s averaging meter: false starts
  s7r_real    the null control of the two s7r rows: the same rig and
              refreshes with a real compressor start at each of the 6 offsets
              of a 60 s window: starts counted (6, one each)

Synthetic inputs only. Run from a worktree root, the base's or the head's:
  PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/start_counter_edges.py

EXPECTED RESULT control=3
EXPECTED RESULT perturbed=4
EXPECTED RESULT restored=8
EXPECTED RESULT s7_60s=0
EXPECTED RESULT s7_30s=0
EXPECTED RESULT s7r_60s=0
EXPECTED RESULT s7r_30s=0
EXPECTED RESULT s7r_real=6

The expected values are the head's, the refresh-held start (owner ruling D1);
the base without it reads s7_60s, s7_30s, s7r_60s and s7r_30s 5 and the rest
the same.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace as NS

from harness import FakeEntry, FakeHass, FakeState
from homeassistant.util import dt as dt_util
from heatpump_optimizer.const import DEFAULT_OPTIMIZATION_INTERVAL
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer.thermal_model import on_threshold_kw

try:
    from heatpump_optimizer import running_signal  # noqa: F401
    EDGES = True
except ImportError:
    EDGES = False

T0 = datetime(2026, 2, 3, 6, 0, tzinfo=timezone.utc)
PERIOD_S = 60 * DEFAULT_OPTIMIZATION_INTERVAL
BASE = {"tibber_token": "x", "weather_entity": "weather.home", "heat_pump_power_entity": "sensor.kw"}


class Rig:
    """One coordinator over the fake bus; fires due timers once, in order."""

    def __init__(self):
        dt_util.freeze(T0)
        self.c = HeatPumpOptimizerCoordinator(FakeHass({"sensor.kw": FakeState("0.0", unit="kW")}),
                                              FakeEntry(data=dict(BASE)))
        self.now, self.armed = T0, {}
        self._seen()

    def _seen(self):
        for entry in getattr(self.c.hass, "timers", []):
            self.armed.setdefault(id(entry), (self.now, entry))

    def at(self, when):
        while True:
            live = getattr(self.c.hass, "timers", [])
            due = sorted(((t + timedelta(seconds=e[0]), k, e) for k, (t, e) in self.armed.items()
                          if e in live and t + timedelta(seconds=e[0]) <= when), key=lambda d: d[0])
            if not due:
                break
            fire_at, key, entry = due[0]
            self.now = max(self.now, fire_at)
            dt_util.freeze(self.now)
            live.remove(entry)
            del self.armed[key]
            entry[1](self.now)
            self._seen()
        self.now = when
        dt_util.freeze(when)

    def set(self, kw, when):
        self.at(when)
        value = f"{kw:.2f}"
        old = self.c.hass.states.get("sensor.kw")
        self.c.hass.states.set("sensor.kw", FakeState(value, unit="kW"))
        if old is not None and old.state == value:
            return
        for ids, action in list(getattr(self.c.hass, "state_listeners", [])):
            if "sensor.kw" in ids:
                action(NS(data={"new_state": self.c.hass.states.get("sensor.kw")}))
        self._seen()

    def refresh(self, when):
        self.at(when)
        asyncio.run(self.c._update_current_state())
        if not EDGES:
            self.c._observe_compressor_start(when)
        self._seen()

    def load(self, payload):
        async def _load(_p=payload):
            return _p
        self.c._ledger_store.async_load = _load
        asyncio.run(self.c._async_load_ledger())


def replay(readings, refreshes=True, rig=None, load=True):
    """``readings``: [(second, kW)]; a refresh every period. Returns the rig."""
    rig = rig or Rig()
    if load:
        rig.load(None)
    refresh_at = PERIOD_S
    for second, kw in readings:
        while refreshes and second >= refresh_at:
            rig.refresh(T0 + timedelta(seconds=refresh_at))
            refresh_at += PERIOD_S
        rig.set(kw, T0 + timedelta(seconds=second))
    rig.at(T0 + timedelta(seconds=readings[-1][0] + 60))
    return rig


PHASES = [(90, 0.0), (120, 2.0), (90, 0.0), (150, 2.0), (120, 0.0), (90, 2.0), (60, 0.0)]


def trace(perturb=None):
    out, t = [], 0
    for minutes, kw in PHASES:
        for s in range(t, t + minutes * 60, 60):
            off = perturb is not None and perturb[0] * 60 <= s < (perturb[0] + perturb[1]) * 60
            out.append((s, 0.0 if off else kw))
        t += minutes * 60
    return out


def restored():
    rig = Rig()
    rig.set(2.0, T0 + timedelta(minutes=1))
    rig.set(2.0, T0 + timedelta(minutes=2))
    for k in (1, 2):  # two refreshes see the draw before the store is read
        rig.refresh(T0 + timedelta(minutes=2, seconds=k))
    rig.load({"ledger": {"months": {}}, "starts": {"lifetime": 7, "months": {}, "running": False}})
    return rig.c._start_counter.lifetime


def s7(window_s):
    """An element cut-in, compressor off, on a meter reporting its window's average.

    The element draws 1.15 x nameplate + 1 kW from offset ``u`` inside a
    window, so the first report is a partial average; the next is the full
    level. A start is false here: the compressor never ran.
    """
    false = 0
    for u in [window_s * k / 6 for k in range(6)]:
        rig = Rig()
        rig.load(None)
        rig.c._current_action = {**rig.c._current_action, "power": 2.0, "dhw_power": 0.0}
        params = rig.c._ctx._thermal_params
        level = float(params.max_electrical_power) * 1.15 + 1.0
        partial = level * (window_s - u) / window_s
        assert partial >= on_threshold_kw(params)
        rig.set(partial, T0 + timedelta(seconds=600))
        rig.set(level, T0 + timedelta(seconds=600 + window_s))
        rig.at(T0 + timedelta(seconds=900))
        false += rig.c._start_counter.lifetime
    return false


def s7r(window_s, real=False):
    """``s7`` with the refreshes: one every period from the first, the element
    running three periods and cutting out through a partial; ``real`` replaces
    the element by a compressor start at 2 kW at the same instants."""
    counted = 0
    for u in [window_s * k / 6 for k in range(6)]:
        rig = Rig()
        rig.load(None)
        rig.c._current_action = {**rig.c._current_action, "power": 2.0, "dhw_power": 0.0}
        level = 2.0 if real else float(rig.c._ctx._thermal_params.max_electrical_power) * 1.15 + 1.0
        partial = level * (window_s - u) / window_s
        rise = T0 + timedelta(seconds=PERIOD_S - 45)
        rig.set(partial, rise)
        rig.refresh(T0 + timedelta(seconds=PERIOD_S))
        rig.set(level, rise + timedelta(seconds=window_s))
        for k in (2, 3, 4):
            rig.refresh(T0 + timedelta(seconds=k * PERIOD_S))
        cut = T0 + timedelta(seconds=4 * PERIOD_S + 60)
        if not real:
            rig.set(level * u / window_s, cut)
            rig.set(0.0, cut + timedelta(seconds=window_s))
        for k in (5, 6, 7):
            rig.refresh(T0 + timedelta(seconds=k * PERIOD_S))
        counted += rig.c._start_counter.lifetime
    return counted


print(f"tree: {'edge path (running_signal)' if EDGES else 'sampled path'}")
print(f"RESULT control={replay(trace()).c._start_counter.lifetime}")
print(f"RESULT perturbed={replay(trace(perturb=(90 + 40, 5))).c._start_counter.lifetime}")
print(f"RESULT restored={restored()}")
print(f"RESULT s7_60s={s7(60)}")
print(f"RESULT s7_30s={s7(30)}")
print(f"RESULT s7r_60s={s7r(60)}")
print(f"RESULT s7r_30s={s7r(30)}")
print(f"RESULT s7r_real={s7r(60, real=True)}")
dt_util.freeze(None)

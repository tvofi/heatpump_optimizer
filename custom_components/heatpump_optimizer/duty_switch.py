"""Duty-switch restart learning: does a duty switch stop a running compressor?

Design: ``docs/design/2026-11-10-duty-switch-restart-learning/design.md``. On some
pumps a switch from hot water to heating while the compressor runs stops it:
the controller judges the heating request on a return the hot-water leg has
just heated. Whether it does is learned per install and per direction.

**Observe.** An episode opens at the arbiter's mode write that changes the
served single duty while the compressor runs (:func:`duty_opened`), when the
source leg heated the circuit (the return :data:`HEATED_MARGIN_K` over the
target's set-point, or without a return sensor a leg of :data:`T_SRC`), the
target duty has demand by the plan's own reading and the plan keeps it on
for :data:`W_STOP`. It closes stopped when the running signal drops inside
:data:`W_STOP`, kept when it still runs then, and void when anything else
could explain a stop: another mode write or a person's change (the record
``pump_arbiter.hold`` drops), the supply switch, a non-plan or non-control
mode, a boost, a disinfection hold, defrost, a fault, an electric heater, or
an unavailable running signal. A stop's off time runs to the next start and
is censored when the arbiter wrote, or the supply switch read off, in between.

**The running signal** is the frequency sensor above zero, else the meter at
``thermal_model.on_threshold_kw``, read by its own listener: not one of the
arbiter's entities, which run a full pass on every change. The listener only
notes a change of the running state; the arbiter's next pass confirms it once
it held :data:`RUNNING_DEBOUNCE` (:func:`_on_running`), keeping the
listener's time. A compressor found running when it arms counts as one that
started then.

**Estimate and use.** Per direction ``p`` is the share of stops over
exponentially decayed counts (half-life :data:`HALF_LIFE_DAYS`), ``t_off`` the
median of the retained uncensored off times (:func:`learned`). Only with at
least :data:`N_MIN` decayed episodes over two local days and ``p`` at or above
:data:`P_ON` is a direction costly, and only a costly direction changes
anything: a both step is served space first where only hot water -> heating is
costly, and a second share entering a costly direction needs that direction's
off time on top of ``SPLIT_MIN_MINUTES`` or the first duty keeps the whole
step (:func:`duty_split`). ``pump_arbiter`` calls the three hooks directly. Below that the split is exactly the arbiter's own.
The episodes persist in their own store; the estimate is in the diagnostics.
"""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from . import boost, pump_mode
from .const import (
    CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY,
    CONF_HEAT_PUMP_DEFROST_ENTITY,
    CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY,
    CONF_HEAT_PUMP_FAULT_ENTITY,
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
    DOMAIN,
    MODE_AUTO,
    MODE_ECONOMY,
    PUMP_DUTY_MODES,
    finite_float,
)
from .drift import stored_instant, utc_elapsed_seconds
from .entry_config import EntryConfig
from .inputs import InputReader, state_power_kw
from .store import QuarantiningStore, load_mapping
from .thermal_model import on_threshold_kw

if TYPE_CHECKING:  # pump_arbiter imports this module
    from .pump_arbiter import ArbiterInputs, ArbiterState, PumpCommand

_LOGGER = logging.getLogger(__name__)

#: The learned directions: the single duty switched from, then to.
DIRECTIONS = ("dhw_space", "space_dhw")
W_STOP = timedelta(minutes=3)
HALF_LIFE_DAYS = 14.0
N_MIN = 5.0
P_ON = 0.5
HEATED_MARGIN_K = 2.0
T_SRC = timedelta(minutes=1)
RUNNING_DEBOUNCE = timedelta(seconds=30)
EPISODES_MAX = 200
_EPISODES_STORE_VERSION = 1
_DIRECTION = {(pump_mode.MODE_DHW, pump_mode.MODE_HEAT): "dhw_space",
              (pump_mode.MODE_HEAT, pump_mode.MODE_DHW): "space_dhw"}
_VOID_FLAGS = (CONF_HEAT_PUMP_DEFROST_ENTITY, CONF_HEAT_PUMP_FAULT_ENTITY,
               CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY, CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY)


@dataclass
class DutySwitchState:
    """Per arbiter record: the running signal, the open episode, the closed ones."""

    #: The confirmed running state and since when; a change not yet confirmed.
    running: tuple[bool, datetime] | None = None
    edge: tuple[bool | None, datetime] | None = None
    unsub: Any = None
    loaded: bool = False
    episode: dict[str, Any] | None = None
    episodes: list[dict[str, Any]] = field(default_factory=list)
    #: The both step's latched split: (step start, first, second, extra minutes).
    order: tuple[datetime, str, str, float] | None = None


def state(held: ArbiterState) -> DutySwitchState:
    held.duty = held.duty or DutySwitchState()
    return held.duty


@dataclass(frozen=True)
class Learned:
    """One direction's estimate; ``costly`` gates every use."""

    p: float
    n: float
    t_off_min: float | None
    costly: bool


def learned(ds: DutySwitchState, direction: str, now: datetime) -> Learned:
    """``p``, the decayed ``n`` and the median uncensored off time for ``direction``."""
    rows = [e for e in ds.episodes if e["dir"] == direction]
    weights = [0.5 ** (max(0.0, utc_elapsed_seconds(now, e["at"])) / (HALF_LIFE_DAYS * 86400.0)) for e in rows]
    n = sum(weights)
    p = sum(w for w, e in zip(weights, rows) if e["stopped"]) / n if n else 0.0
    offs = sorted(e["off_min"] for e in rows if e["stopped"] and e["off_min"] is not None)
    t_off = (offs[(len(offs) - 1) // 2] + offs[len(offs) // 2]) / 2.0 if offs else None
    days = {dt_util.as_local(e["at"]).date() for e in rows}
    return Learned(p, n, t_off, n >= N_MIN and len(days) >= 2 and p >= P_ON)


def duty_split(held: ArbiterState, start: datetime, now: datetime) -> tuple[str, str, float]:
    """(first duty, second duty, minutes the second share needs on top of
    ``SPLIT_MIN_MINUTES``) of the both step at ``start``; latched per step, so
    neither the tick nor a mid-step re-solve flips it."""
    ds = state(held)
    if ds.order is None or ds.order[0] != start:
        est = {d: learned(ds, d, now) for d in DIRECTIONS}
        space_first = est["dhw_space"].costly and not est["space_dhw"].costly
        first, second = ("space", "dhw") if space_first else ("dhw", "space")
        into = est[f"{first}_{second}"]
        ds.order = (start, first, second, (into.t_off_min or 0.0) if into.costly else 0.0)
    return ds.order[1], ds.order[2], ds.order[3]


def _reading(state_: Any, freq: bool, threshold_kw: float) -> bool | None:
    if freq:
        raw = finite_float(getattr(state_, "state", None))
        return None if raw is None else raw > 0.0
    kw = state_power_kw(state_, "clamp")
    return None if kw is None else kw >= threshold_kw


def _arm(ds: DutySwitchState, held: ArbiterState, inp: ArbiterInputs, now: datetime) -> None:
    """Arm the running signal's listener with the arbiter's own, once per arming."""
    if ds.unsub is not None and ds.unsub in held.unsubs:
        return
    cfg = EntryConfig.from_mapping(inp.config)
    entity = cfg.compressor_freq_sensor or cfg.heat_pump_power_entity
    ds.unsub = None
    if not entity or not held.unsubs:
        return
    freq, threshold = bool(cfg.compressor_freq_sensor), on_threshold_kw(inp.thermal.params)
    first = _reading(inp.hass.states.get(entity), freq, threshold)
    ds.running, ds.edge = (None if first is None else (first, now)), None

    @callback
    def _changed(event: Any) -> None:
        reading = _reading(event.data.get("new_state"), freq, threshold)
        if reading == (ds.running[0] if ds.running else None):
            ds.edge = None
        elif ds.edge is None or ds.edge[0] != reading:
            ds.edge = (reading, dt_util.now())

    ds.unsub = async_track_state_change_event(inp.hass, [entity], _changed)
    held.unsubs.append(ds.unsub)


def _on_running(ds: DutySwitchState, now: datetime) -> None:
    """Confirm a running-state change that held :data:`RUNNING_DEBOUNCE`; feed the episode."""
    edge = ds.edge
    if edge is None or utc_elapsed_seconds(now, edge[1]) < RUNNING_DEBOUNCE.total_seconds():
        return
    ds.edge, ds.running = None, None if edge[0] is None else (edge[0], edge[1])
    ep = ds.episode
    if ep is None:
        return
    if edge[0] is None:
        ds.episode = None  # an unavailable running signal voids the episode
    elif not edge[0] and "stop" not in ep and utc_elapsed_seconds(edge[1], ep["at"]) <= W_STOP.total_seconds():
        ep["stop"] = edge[1]
    elif edge[0] and "stop" in ep:
        _close(ds, ep, True, utc_elapsed_seconds(edge[1], ep["stop"]) / 60.0)


def _close(ds: DutySwitchState, ep: dict[str, Any], stopped: bool, off_min: float | None) -> None:
    ds.episode = None
    ds.episodes = [*ds.episodes, {"at": ep["at"], "dir": ep["dir"], "stopped": stopped,
                                  "off_min": off_min}][-EPISODES_MAX:]


def _reader(inp: ArbiterInputs) -> InputReader:
    cfg = EntryConfig.from_mapping(inp.config)
    return InputReader(inp.hass, dict(inp.config or {}), enabled=cfg.staleness_watchdog_enabled,
                       scale=cfg.staleness_max_age_scale)


def _supply_off(inp: ArbiterInputs) -> bool:
    return getattr(inp.hass.states.get(EntryConfig.from_mapping(inp.config).heat_pump_switch_entity or ""),
                   "state", None) == "off"


def _void(coord: Any, held: ArbiterState, inp: ArbiterInputs, ep: dict[str, Any], now: datetime) -> bool:
    """Whether anything but the switch could explain a stop since ``ep`` opened."""
    mode = held.written.get("mode")
    return bool(
        inp.mode not in (MODE_AUTO, MODE_ECONOMY)
        or EntryConfig.from_mapping(inp.config).pump_duty_mode != PUMP_DUTY_MODES[2]
        or inp.disinfecting or _supply_off(inp) or state(held).running is None
        # A person's change drops the record (``pump_arbiter.hold``), as another write moves it.
        or mode is None or mode[1] != ep["at"]
        or any(boost.held_for(coord).active(c, now) for c in (boost.CHANNEL_SPACE, boost.CHANNEL_DHW))
        or any(r.ok and r.flag for r in map(_reader(inp).read_bool, _VOID_FLAGS))
    )


def _demand(inp: ArbiterInputs, duty: str, now: datetime) -> bool:
    """The target duty has demand by the plan's own reading."""
    if duty == "space":
        room = getattr(inp.state, "room_temperature", None)
        i = _index(inp.plan, now)
        planned = list(getattr(inp.plan, "optimal_setpoints", None) or [])
        return room is not None and i is not None and i < len(planned) and float(room) < float(planned[i])
    tank = getattr(inp.state, "dhw_temperature", None)
    return tank is not None and float(tank) < float(inp.params.dhw_setpoint)


def _index(plan: Any, now: datetime) -> int | None:
    stamps = list(getattr(plan, "timestamps", None) or [])
    i = sum(1 for t in stamps if t <= now) - 1
    return i if i >= 0 else None


def _heated(inp: ArbiterInputs, setpoint: float | None, since: datetime, now: datetime) -> bool:
    inlet = _reader(inp).read(CONF_HEAT_PUMP_RETURN_TEMP_ENTITY)
    if not inlet.ok:
        return utc_elapsed_seconds(now, since) >= T_SRC.total_seconds()
    return setpoint is not None and inlet.value - setpoint >= HEATED_MARGIN_K


def duty_opened(coord: Any, held: ArbiterState, inp: ArbiterInputs, command: PumpCommand,
                before: tuple[Any, datetime] | None, now: datetime, step_duty: Any) -> None:
    """The arbiter's mode-write hook; ``step_duty`` is the arbiter's own. A
    learner fault never aborts the arbiter's pass."""
    try:
        _opened(coord, held, inp, command, before, now, step_duty)
    except Exception as err:  # noqa: BLE001 - the learner is advisory
        _LOGGER.debug("Duty-switch learner skipped an episode: %s", err)


def _opened(coord: Any, held: ArbiterState, inp: ArbiterInputs, command: PumpCommand,
            before: tuple[Any, datetime] | None, now: datetime, step_duty: Any) -> None:
    """Open an episode at a mode write that changed the served single duty while running."""
    after, ds = held.written.get("mode"), state(held)
    direction = _DIRECTION.get((before[0], after[0])) if before and after and after[1] == now else None
    if direction is None or not (ds.running and ds.running[0]) or inp.plan is None:
        return
    target = direction.split("_")[1]
    setpoint = command.space_setpoint if target == "space" else command.dhw_setpoint
    planned = all(step_duty(inp.plan, t) in (target, "both") for t in (now, now + W_STOP))
    ep = {"at": now, "dir": direction}
    if (_heated(inp, setpoint, before[1], now) and planned and _demand(inp, target, now)
            and not _void(coord, held, inp, ep, now)):
        ds.episode = ep


async def duty_follow(coord: Any, held: ArbiterState, inp: ArbiterInputs, now: datetime) -> None:
    """The arbiter's per-pass hook: a learner fault never aborts its pass."""
    try:
        await _follow(coord, held, inp, now)
    except Exception as err:  # noqa: BLE001 - the learner is advisory
        _LOGGER.debug("Duty-switch learner skipped a pass: %s", err)


async def _follow(coord: Any, held: ArbiterState, inp: ArbiterInputs, now: datetime) -> None:
    """Each arbiter pass: load once, arm the listener, confirm an edge, close episodes."""
    ds = state(held)
    if not ds.loaded:
        ds.loaded = True
        await _load(coord, held)
    _arm(ds, held, inp, now)
    count = len(ds.episodes)
    _on_running(ds, now)
    _classify(coord, held, ds, inp, now)
    if len(ds.episodes) != count:
        await _persist(coord, held)


def _classify(coord: Any, held: ArbiterState, ds: DutySwitchState, inp: ArbiterInputs, now: datetime) -> None:
    """A stop is void-checked once; a kept episode closes at :data:`W_STOP`; an
    off time the arbiter or the supply switch wrote into is censored."""
    ep = ds.episode
    if ep is None:
        return
    if "stop" not in ep:
        if ds.edge is None and utc_elapsed_seconds(now, ep["at"]) >= W_STOP.total_seconds():
            if _void(coord, held, inp, ep, now):
                ds.episode = None
            else:
                _close(ds, ep, False, None)
        return
    if not ep.get("checked"):
        ep["checked"] = True
        if _void(coord, held, inp, ep, now):
            ds.episode = None
            return
    if any(at > ep["stop"] for _v, at in held.written.values()) or _supply_off(inp):
        _close(ds, ep, True, None)


def _store(coord: Any) -> QuarantiningStore[dict[str, Any]]:
    return QuarantiningStore(coord.hass, _EPISODES_STORE_VERSION, f"{DOMAIN}_{coord.entry.entry_id}_duty_switch",
                             naive_zone=dt_util.DEFAULT_TIME_ZONE)


async def _persist(coord: Any, held: ArbiterState) -> None:
    ds = state(held)
    try:
        await _store(coord).async_save({"episodes": [{**e, "at": e["at"].isoformat()} for e in ds.episodes]})
    except Exception:  # noqa: BLE001 - the next closed episode saves again
        return


async def _load(coord: Any, held: ArbiterState) -> None:
    ds = state(held)
    raw = await load_mapping(_store(coord), "the duty-switch record")
    rows = (raw or {}).get("episodes")
    for row in rows if isinstance(rows, list) else ():
        at = stored_instant(row.get("at"), dt_util.DEFAULT_TIME_ZONE) if isinstance(row, dict) else None
        if at is not None and row.get("dir") in DIRECTIONS:
            off = finite_float(row.get("off_min"))
            ds.episodes.append({"at": at, "dir": row["dir"], "stopped": row.get("stopped") is True,
                                "off_min": off if off is not None and off >= 0.0 else None})


def diagnostics_view(held: ArbiterState) -> dict[str, Any]:
    """Each direction's ``p``, decayed ``n``, ``t_off`` and whether it is in use."""
    ds = state(held)
    return {d: asdict(learned(ds, d, dt_util.now())) for d in DIRECTIONS}

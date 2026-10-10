"""Documented events for what an owner wants to be told about (R9-UX-4, #1795).

The coordinator already publishes every signal an owner would want a message
for. This module listens to each update, reads the typed ``Payload`` and fires
one Home Assistant event per occurrence, so an automation (the shipped
``notifications`` blueprint, or the owner's own) picks the target, the events
and the quiet hours. There is no option field and no coordinator line: the
module subscribes with ``async_add_listener`` where the entry stores its
coordinator.

An occurrence is a rising edge. Each detector names the occurrences present in
a payload, each with a key; the event fires when the key differs from the one
last sent, and a detector that sees its signal gone forgets the key so the next
occurrence fires. A payload that does not carry a detector's signal at all
leaves its state alone, so a light payload neither fires nor re-arms. What was
sent is written to a store after each change and read back at setup, so a
restart does not announce a standing condition again. A receipt already held
when the store is first created is adopted silently: an upgrade must not
announce last month's receipt as news.
"""
from __future__ import annotations

import logging
from collections.abc import Callable, Coroutine
from typing import Any, NamedTuple

from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .payload import Payload
from .store import QuarantiningStore

_LOGGER = logging.getLogger(__name__)

NOTIFIER_STORE_VERSION = 1
EVENT_MONTHLY_RECEIPT = f"{DOMAIN}_monthly_receipt"
EVENT_COMFORT_AT_RISK = f"{DOMAIN}_comfort_at_risk"
EVENT_INPUT_STALE = f"{DOMAIN}_input_stale"
EVENT_PLAN_STALE = f"{DOMAIN}_plan_stale"
EVENT_MANUAL_PLAN_RELEASED = f"{DOMAIN}_manual_plan_released"

#: The data each event carries, in the order ``docs/automations.md`` lists it.
#: What an event fires is exactly these keys, filled from its occurrence.
EVENT_DATA: dict[str, tuple[str, ...]] = {
    EVENT_MONTHLY_RECEIPT: (
        "entry_id", "month", "total_sek", "saving_sek", "saving_pct", "currency",
    ),
    EVENT_COMFORT_AT_RISK: (
        "entry_id", "predicted_min_c", "at", "floor_c",
        "peak_guard_suppressing", "cause",
    ),
    EVENT_INPUT_STALE: ("entry_id", "input", "age_minutes", "max_age_minutes"),
    EVENT_PLAN_STALE: ("entry_id", "age_minutes"),
    EVENT_MANUAL_PLAN_RELEASED: (
        "entry_id", "channel", "steps", "reason", "expires_at",
    ),
}


class Occurrence(NamedTuple):
    """One thing worth an event: its type, the key naming this occurrence, its data."""

    event: str
    key: str
    data: dict[str, Any]


#: Occurrences by id, or ``None`` when the payload does not carry the signal.
Detected = dict[str, Occurrence] | None


def _monthly_receipt(data: Payload) -> Detected:
    insight = data.get("insight")
    if insight is None:
        return None
    report = insight.get("monthly_report")
    if not report or not isinstance(month := report.get("month"), str):
        return None
    saving = next(
        (m for m in data.get("savings_months", []) if m.get("month") == month), None
    )
    return {"receipt": Occurrence(EVENT_MONTHLY_RECEIPT, month, {
        "month": month,
        "total_sek": report.get("total_sek"),
        "saving_sek": saving.get("savings_sek") if saving else None,
        "saving_pct": saving.get("savings_pct") if saving else None,
        "currency": data.get("currency"),
    })}


def _comfort_cause(data: Payload, when: Any) -> str | None:
    """The coldest step's published reason, when the plan carries one."""
    plan = data.get("space_plan")
    if not isinstance(plan, dict):
        return None
    for step in plan.get("forecast") or []:
        if isinstance(step, dict) and step.get("t") == when:
            reason = step.get("reason")
            return reason if isinstance(reason, str) and reason else None
    return None


def _comfort(data: Payload) -> Detected:
    floor = data.get("min_temperature")
    steps = data.get("schedule")
    if floor is None or steps is None:
        return None
    cold = [
        (float(t), step.get("time")) for step in steps
        if isinstance(t := step.get("room_temp"), (int, float))
    ]
    if not cold:
        return {}
    low, when = min(cold, key=lambda step: step[0])
    if low >= floor:
        return {}
    return {"comfort": Occurrence(EVENT_COMFORT_AT_RISK, "at_risk", {
        "predicted_min_c": round(low, 1),
        "at": when,
        "floor_c": floor,
        "peak_guard_suppressing": bool(data.get("peak_guard_suppressing")),
        "cause": _comfort_cause(data, when),
    })}


def _inputs(data: Payload) -> Detected:
    problems = data.get("input_problems")
    if problems is None:
        return None
    return {
        f"input_stale:{p.get('input')}": Occurrence(EVENT_INPUT_STALE, "stale", {
            "input": p.get("input"),
            "age_minutes": p.get("age_minutes"),
            "max_age_minutes": p.get("max_age_minutes"),
        })
        for p in problems if p.get("problem") == "stale"
    }


def _plan(data: Payload) -> Detected:
    stale = data.get("plan_stale")
    if stale is None:
        return None
    if not stale:
        return {}
    return {"plan_stale": Occurrence(EVENT_PLAN_STALE, "stale", {
        "age_minutes": data.get("plan_age_minutes"),
    })}


def _manual(data: Payload) -> Detected:
    plan = data.get("manual_plan")
    found: dict[str, Occurrence] = {}
    if plan is None:
        return found
    for channel, rows in (
        ("space", plan.get("released_space")), ("dhw", plan.get("released_dhw")),
    ):
        steps = [r["step"] for r in rows or [] if isinstance(r.get("step"), int)]
        if steps:
            expires = plan.get("expires_at")
            found[f"manual_plan:{channel}"] = Occurrence(
                EVENT_MANUAL_PLAN_RELEASED, str(expires), {
                    "channel": channel,
                    "steps": steps,
                    "reason": rows[0].get("reason") if rows else None,
                    "expires_at": expires,
                })
    return found


#: Each detector with the id prefix its occurrences carry.
_DETECTORS: tuple[tuple[str, Callable[[Payload], Detected]], ...] = (
    ("receipt", _monthly_receipt),
    ("comfort", _comfort),
    ("input_stale", _inputs),
    ("plan_stale", _plan),
    ("manual_plan", _manual),
)


class Notifier:
    """Fires the events, remembering what it has sent."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        spawn: Callable[[Coroutine[Any, Any, None]], object],
    ) -> None:
        self._hass = hass
        self._entry_id = entry_id
        self._spawn = spawn
        self._store: QuarantiningStore[dict[str, Any]] = QuarantiningStore(
            hass, NOTIFIER_STORE_VERSION, f"{DOMAIN}_{entry_id}_notifier",
            # A manual plan's expiry is the owner's instant, ahead of the clock
            # by design, and it is this store's key: bounding it would rewrite
            # the key and announce the same override again after a restart.
            lead=None,
        )
        self._sent: dict[str, str] = {}
        self._baseline = True

    async def async_load(self) -> None:
        try:
            raw = await self._store.async_load()
        except Exception as err:  # noqa: BLE001 - a bad store only costs a repeat
            _LOGGER.debug("Could not load notifier state: %s", err)
            return
        sent = raw.get("sent") if raw else None
        if isinstance(sent, dict):
            self._sent = {
                k: v for k, v in sent.items()
                if isinstance(k, str) and isinstance(v, str)
            }
            self._baseline = False

    async def _async_save(self) -> None:
        try:
            await self._store.async_save({"sent": dict(self._sent)})
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not persist notifier state: %s", err)

    def handle(self, data: Payload) -> None:
        """Fire what is new in ``data`` and forget what has cleared."""
        # The first payload that carries the receipt signal is the baseline.
        adopt = self._baseline and "insight" in data
        changed = adopt
        self._baseline = self._baseline and not adopt
        for prefix, detect in _DETECTORS:
            seen = detect(data)
            if seen is None:
                continue
            for oid, occurrence in seen.items():
                if self._sent.get(oid) == occurrence.key:
                    continue
                self._sent[oid] = occurrence.key
                changed = True
                if not (adopt and prefix == "receipt"):
                    fields = {"entry_id": self._entry_id, **occurrence.data}
                    self._hass.bus.async_fire(
                        occurrence.event,
                        {k: fields.get(k) for k in EVENT_DATA[occurrence.event]},
                    )
            for oid in [o for o in self._sent if o.startswith(prefix) and o not in seen]:
                del self._sent[oid]
                changed = True
        if changed:
            self._spawn(self._async_save())


async def async_setup_notifier(
    hass: HomeAssistant, entry: Any, coordinator: Any
) -> None:
    """Start the entry's notifier and drop it with the entry."""
    notifier = Notifier(
        hass,
        entry.entry_id,
        lambda coro: entry.async_create_background_task(
            hass, coro, name="heatpump_optimizer_notifier_save"
        ),
    )
    await notifier.async_load()

    def _on_update() -> None:
        if coordinator.data is not None:
            notifier.handle(coordinator.data)

    entry.async_on_unload(coordinator.async_add_listener(_on_update))

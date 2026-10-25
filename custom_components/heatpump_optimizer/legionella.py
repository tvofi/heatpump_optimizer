"""The anti-legionella guard: when the cycle runs, and what it refuses.

Extracted from ``HeatPumpOptimizerCoordinator`` by W5-G10 (#193's follow-on).
The guard owns the cycle's own state -- when disinfection last completed, what
a commanded cycle reached, how long the tank has held temperature, and the
three repair notices it raises -- and holds none of the coordinator. It reads
two shared objects it never writes, ``ThermalParameters`` and the effective
configuration, and observes one coordinator fact through a callable rather
than reaching for it: the action currently planned, which tells the cycle
whether the plan commanded it.

Every method body is the coordinator's, moved verbatim under the substitution
table the pull request publishes; the residual diff per method is the proof.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Callable

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from .store import QuarantiningStore
from homeassistant.util import dt as dt_util

from .accuracy import utc_elapsed_seconds
from .const import (
    DEFAULT_DHW_LEGIONELLA_TEMP,
    DEFAULT_DHW_SETPOINT,
    DHW_LEGIONELLA_BOOST_MAX_HOURS,
    DHW_LEGIONELLA_HOLD_MINUTES,
    DOMAIN,
)
from .drift import stored_instant
from .disinfection import DisinfectionSwitch
from .entry_config import EntryConfig
from .payload import REASON_LEGIONELLA, CurrentAction
from .issues import clear_issue, create_issue, set_issue
from .thermal_model import ThermalParameters

_LOGGER = logging.getLogger(__name__)

LEGIONELLA_STORE_VERSION = 1

#: How soon a cycle that fell short is tried again, when a tank probe can tell
#: the next try apart. Spacing it by the whole interval let one cut-off boost
#: push the next try a week out, so a pump that never finished went weeks with
#: one 15-minute attempt each (D15 lead L8: 66 days without a completion). A
#: day keeps it off every plan while staying inside one 24 h horizon.
DHW_LEGIONELLA_RETRY_HOURS = 24.0


def days_since_confirmed(
    last_cycle: datetime | None, now: datetime, interval_days: float, *, watched: bool
) -> int | None:
    """Whole days since the last confirmed cycle once past the interval, else None."""
    if not watched or last_cycle is None:
        return None
    age_h = utc_elapsed_seconds(now, last_cycle) / 3600.0
    return int(age_h // 24.0) if age_h > interval_days * 24.0 else None


class LegionellaGuard:
    """The disinfection cycle's state, its ceilings and its repair notices."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        params: Callable[[], ThermalParameters],
        config: dict[str, Any],
        *,
        action: Callable[[], CurrentAction],
        disinfect: DisinfectionSwitch,
        dhw_blocked: Callable[[], bool],
    ) -> None:
        self.hass = hass
        #: Reads the coordinator's published parameters, never holds a snapshot.
        self._params = params
        self._config = config
        #: The action the plan currently commands, observed and never held.
        self._action = action
        #: #1067: the pump's own disinfection switch, driven by the boost's
        #: edges in control mode and only read in observe mode.
        self.disinfect = disinfect
        disinfect.persist = self.async_save
        #: Whether the pump's mode blocks hot water, read live on THIS cycle.
        #: The last solve's reading (``check_mode_block``) lags a mode change
        #: until the next solve, and the ON edge must not.
        self._dhw_blocked = dhw_blocked
        #: Whether the switch's write-failure repair is currently raised.
        self.write_failed_notice: bool = False
        #: Set when the bound closed a boost the plan still commands; the
        #: switch is not turned back on until the plan stops commanding it.
        self.switch_latched: bool = False
        #: The (owned switches, latch) pair as last written to the store.
        self._switch_saved: tuple[tuple[str, ...], bool] = ((), False)
        self.last_cycle: datetime | None = None
        self.store: QuarantiningStore[dict[str, Any]] = QuarantiningStore(
            hass,
            LEGIONELLA_STORE_VERSION,
            f"{DOMAIN}_{entry_id}_dhw_legionella",
            naive_zone=dt_util.DEFAULT_TIME_ZONE,  # async_load's zone
        )
        # #24: minutes the tank has HELD the disinfection temperature.
        self.hold_minutes: float = 0.0
        self.hold_last: datetime | None = None
        # v5.1.10: the cycle the PLAN commanded, followed independently of
        # whether the tank was ever seen at temperature. Without this the
        # only way the timer could ever reset was an observation at
        # ``legionella_temp - 1``, so a pump that cannot get there -- or a
        # tank with no probe at all -- left the countdown running for ever.
        self.boost_active: bool = False
        self.boost_peak: float | None = None
        self.boost_started: datetime | None = None
        #: When a commanded cycle last FINISHED SHORT of the disinfection
        #: temperature, and how far it got. This is not success and is never
        #: reported as such; it exists so the retry is spaced by ``hours_since``
        #: instead of landing on the first step of every single plan.
        self.attempt: datetime | None = None
        self.attempt_peak: float | None = None
        #: The (disinfection temp, charge limit, interval) the ceiling notice
        #: was last raised for, so it is only rewritten when the pair changes.
        self.ceiling_notice: tuple[float, float, float] | None = None
        #: Signature of the "disinfection is blocked by the pump's mode"
        #: notice currently raised, or None when none is. Coarsened to whole
        #: overdue days so a worsening situation updates the text without
        #: re-raising the issue every cycle.
        self.mode_block_notice: int | None = None
        #: Whole days since the last confirmed cycle while the overdue notice
        #: stands, or None when none is.
        self.overdue_notice: int | None = None

    async def async_load(self) -> None:
        """Load the timestamp of the last completed anti-legionella cycle.

        A fresh install has no record. It is initialised to "now" rather than
        "never" so a brand-new setup does not immediately blast the tank to the
        legionella temperature.
        """
        try:
            stored = await self.store.async_load()
            raw = (stored or {}).get("last_cycle")
            parsed = stored_instant(raw, dt_util.DEFAULT_TIME_ZONE)
            # A cycle that ran but fell short is remembered separately, so a
            # restart cannot turn a failed attempt back into an overdue timer
            # that pins a boost on every plan.
            attempt_raw = (stored or {}).get("last_attempt")
            attempt = stored_instant(attempt_raw, dt_util.DEFAULT_TIME_ZONE)
            self._load_switch_record(stored or {})
            if attempt is not None:
                self.attempt = attempt
                peak = (stored or {}).get("last_attempt_peak")
                if isinstance(peak, (int, float)):
                    self.attempt_peak = float(peak)
            if parsed is not None:
                self.last_cycle = parsed
                return
        except Exception as err:
            _LOGGER.debug("Could not load DHW legionella timestamp: %s", err)

        self.last_cycle = dt_util.now()
        await self.async_save()

    def _load_switch_record(self, stored: dict[str, Any]) -> None:
        """The switches a previous run turned on and never saw off, and
        whether the boost bound's latch was holding them off."""
        owned = stored.get("disinfection_owned")
        if isinstance(owned, list):
            self.disinfect.owned = [o for o in owned if isinstance(o, str) and o]
        self.switch_latched = stored.get("disinfection_latched") is True
        self._switch_saved = (tuple(self.disinfect.owned), self.switch_latched)

    async def async_save(self) -> None:
        """Persist the timestamp of the last completed anti-legionella cycle."""
        if self.last_cycle is None:
            return
        payload: dict[str, Any] = {
            "last_cycle": self.last_cycle.isoformat()
        }
        if self.disinfect.owned:
            payload["disinfection_owned"] = list(self.disinfect.owned)
        if self.switch_latched:
            payload["disinfection_latched"] = True
        self._switch_saved = (tuple(self.disinfect.owned), self.switch_latched)
        if self.attempt is not None:
            payload["last_attempt"] = self.attempt.isoformat()
            if self.attempt_peak is not None:
                payload["last_attempt_peak"] = round(
                    float(self.attempt_peak), 2
                )
        try:
            await self.store.async_save(payload)
        except Exception as err:
            _LOGGER.debug("Could not persist DHW legionella timestamp: %s", err)

    async def async_track(self, dhw_temp: float) -> None:
        """Reset the anti-legionella timer whenever the tank actually gets hot.

        Any reason for the tank reaching the disinfection temperature counts —
        a planned cycle, a manual boost, a wood coil or an immersion heater.

        With free disinfection (#24) switched on, the credit is
        hold-verified: the tank must spend ``DHW_LEGIONELLA_HOLD_MINUTES``
        at temperature, integrated across observations, before the
        completion timestamp is written — exactly the timestamp a planned
        cycle writes. A momentary blip at 60 °C kills nothing and credits
        nothing. With the flag off the historical instant-credit rule is
        untouched.
        """
        # #2674: the store's startup read would land on top of a cycle
        # credited before it, and the credit would be lost.
        await self.store.async_wait_for_read()
        target = float(self._params().dhw_legionella_temp)
        now = dt_util.now()

        if EntryConfig.from_mapping(self._config).dhw_free_disinfection_enabled:
            if dhw_temp >= target - 0.5:
                previous_obs = self.hold_last
                # Accumulate only hot-to-hot gaps: an interval that STARTED
                # cold proves nothing about the water in between. Capped so
                # a long observation gap cannot claim more than was
                # plausibly held.
                if previous_obs is not None:
                    gap_min = utc_elapsed_seconds(now, previous_obs) / 60.0
                    self.hold_minutes += min(gap_min, 90.0)
                self.hold_last = now
                if self.hold_minutes < DHW_LEGIONELLA_HOLD_MINUTES:
                    return
            else:
                # Not at temperature: the accumulation chain breaks, and a
                # clear fall below the band starts the hold over.
                self.hold_last = None
                if dhw_temp < target - 1.5:
                    self.hold_minutes = 0.0
                return
        elif dhw_temp < target - 1.0:
            return

        previous = self.last_cycle
        if previous is not None and utc_elapsed_seconds(now, previous) < 3600:
            return
        self.hold_minutes = 0.0
        self.last_cycle = now
        # A real cycle clears any record of one that fell short, and takes the
        # "cannot reach temperature" notice down with it.
        self.attempt = None
        self.attempt_peak = None
        self.clear_unreachable_issue()
        self.clear_unverified_issue()
        self.check_overdue()
        _LOGGER.info(
            "DHW anti-legionella cycle observed at %.1f°C, timer reset", dhw_temp
        )
        await self.async_save()

    async def async_track_cycle(
        self, dhw_temp: float | None
    ) -> None:
        """Follow the disinfection boost the PLAN commanded, to its end.

        The observer above credits only a tank seen at temperature, so a pump
        that cannot get there, or a tank with no probe, would leave the cycle
        overdue and pinned on every plan. The commanded boost is followed to
        its end instead, and judged: an attempt, never a completion, spaced by
        ``hours_since``. The end is bounded by
        ``DHW_LEGIONELLA_BOOST_MAX_HOURS``, because a cycle the tank cannot
        finish is re-commanded on every solve and its window never closes.
        Success is the observer's credit during the boost, never this peak:
        the observer's rule differs with the free-disinfection flag.
        """
        params = self._params()
        if not params.dhw_legionella_enabled:
            self.boost_active = False
            self.boost_peak = None
            self.boost_started = None
            await self._drive_switch(False)
            return

        now = dt_util.now()
        commanded = (
            str(self._action().get("dhw_reason") or "") == REASON_LEGIONELLA
        )
        self.switch_latched = self.switch_latched and commanded
        if commanded:
            if not self.boost_active:
                self.boost_active = True
                self.boost_started = now
            if dhw_temp is not None:
                self.boost_peak = max(
                    self.boost_peak
                    if self.boost_peak is not None
                    else float(dhw_temp),
                    float(dhw_temp),
                )
            started = self.boost_started
            expired = (
                started is not None
                and utc_elapsed_seconds(now, started)
                >= DHW_LEGIONELLA_BOOST_MAX_HOURS * 3600.0
            )
            if not expired:
                await self._drive_switch(True)
                return
            # Still commanded after half a day. A cycle the tank cannot
            # finish is re-commanded on every solve, so waiting for the boost
            # to end is waiting for something that never happens: the window
            # is closed here instead and judged on what it managed, which is
            # what lets the retry be spaced and the user be told.
            _LOGGER.warning(
                "DHW anti-legionella boost has been commanded for %.0f h "
                "without completing; recording what it achieved",
                DHW_LEGIONELLA_BOOST_MAX_HOURS,
            )
            self.switch_latched = True
        elif not self.boost_active:
            # Idle: an owned switch that still reads on is turned off here,
            # which is also what retries an OFF the close failed to land.
            await self._drive_switch(False)
            return

        # The boost window closed — either the plan moved on, or it outlasted
        # the bound above. Decide what it achieved.
        await self._drive_switch(False)
        started = self.boost_started
        self.boost_active = False
        self.boost_started = None
        peak = self.boost_peak
        self.boost_peak = None
        target = float(params.dhw_legionella_temp)

        # Did the observer credit a completed cycle while this boost ran? That
        # is the only evidence of success there is, and it is the same test on
        # both sides of the free-disinfection flag. Reading the peak instead
        # (`peak >= target - 1.0`) disagreed with the observer's own rule
        # (`target - 0.5`, held for DHW_LEGIONELLA_HOLD_MINUTES): a cycle
        # peaking in [59.0, 59.5) was neither credited nor recorded, no notice
        # was raised, and `hours_since` stayed pinned at its overdue value
        # while the cycle was re-commanded on every single solve.
        credited = (
            self.last_cycle is not None
            and started is not None
            and utc_elapsed_seconds(self.last_cycle, started) >= 0
        )
        if credited:
            return
        pending = self._pending_attempt()
        if pending is not None and (
            utc_elapsed_seconds(now, pending) < self._retry_hours() * 3600.0
        ):
            # Reopened inside its retry (the cycle step flaps between steps 0
            # and 1): the same attempt, or a re-stamp per solve never expires.
            if peak is not None:
                self.attempt_peak = max(peak, self.attempt_peak or peak)
            return

        if not self._has_probe():
            # No way to verify, ever. What is recorded is an ATTEMPT, not a
            # completion: nothing observed the tank, and this integration
            # publishes a plan — the actuation may be an external automation
            # that never ran. An attempt already drives `hours_since` from
            # 192 h to 0 exactly as a completion would, because
            # `hours_since` counts attempts too, so claiming
            # success bought no scheduling benefit at all and cost the ability
            # to say the cycle is unverified. It is said instead.
            self.hold_minutes = 0.0
            self.attempt = now
            self.attempt_peak = None
            _LOGGER.warning(
                "DHW anti-legionella cycle commanded but cannot be verified: "
                "no tank temperature sensor is configured, so nothing confirms "
                "the tank reached %.0f °C",
                target,
            )
            self.raise_unverified_issue(target)
            await self.async_save()
            return

        if peak is None:
            # A probe exists but said nothing for the whole boost. Nothing was
            # observed, so nothing is claimed — but the retry is still spaced
            # by ``DHW_LEGIONELLA_RETRY_HOURS``, not repeated on every solve.
            self.attempt = now
            self.attempt_peak = None
            _LOGGER.warning(
                "DHW anti-legionella cycle ran with no usable tank reading; "
                "it cannot be confirmed and will be retried within a day"
            )
            await self.async_save()
            return

        self.attempt = now
        self.attempt_peak = float(peak)
        if peak >= target - 1.0:
            # It got to temperature but the completion was never credited —
            # under the free-disinfection flag that means the hold was not
            # observed for long enough. The retry is spaced by ``hours_since``,
            # and no "cannot reach temperature" notice is raised, because the
            # tank plainly can.
            _LOGGER.warning(
                "DHW anti-legionella cycle reached %.1f °C but the completion "
                "could not be confirmed; it will be retried within a day",
                peak,
            )
        else:
            # Commanded, run, and the tank topped out below the disinfection
            # temperature. This is the achievable maximum for this pump and
            # this tank, so repeating the same boost cannot do better.
            _LOGGER.warning(
                "DHW anti-legionella cycle reached only %.1f °C against a "
                "%.0f °C target; the tank is not being disinfected",
                peak,
                target,
            )
            self.raise_unreachable_issue(float(peak), target)
        await self.async_save()

    async def _drive_switch(self, on: bool) -> None:
        """Put the pump's disinfection switch in the boost's state.

        ON goes to the configured switch only in control mode, while the
        boost wants it and the bound's close is not latched: the command that
        outlasted the bound is still the plan's until the next solve, and it
        re-opens the boost window on the very next cycle. Every switch this
        integration owns and is not keeping on is released against its real
        state (``DisinfectionSwitch.release``), whatever the mode says now,
        so a closed boost, disabled disinfection, and an options change to
        observe, to another switch or to none all end with it off -- and an
        older record never blocks the configured switch. The record and the
        latch are persisted whenever they change. A write that raised raises
        a repair, and the next write that lands takes it down; a record
        dropped as unreadable raises its own.
        """
        switch = self.disinfect
        now = dt_util.now()
        if on and not self.switch_latched and switch.controlling:
            await switch.turn_on(dhw_blocked=self._dhw_blocked())
            await switch.release(now, keep=switch.entity_id)
        else:
            switch.memo = None
            await switch.release(now)
        if (tuple(switch.owned), self.switch_latched) != self._switch_saved:
            await self.async_save()
        lost, switch.lost = switch.lost, []
        for entity_id in lost:
            create_issue(
                self.hass,
                DOMAIN,
                f"dhw_disinfection_switch_lost_{entity_id}",
                is_fixable=False,
                # Persistent: the record is gone, so nothing would raise it
                # again after a restart, and the switch may still be on.
                is_persistent=True,
                severity=ir.IssueSeverity.WARNING,
                translation_key="dhw_disinfection_switch_lost",
                translation_placeholders={"entity_id": entity_id},
            )
        if switch.failed == self.write_failed_notice:
            return
        self.write_failed_notice = switch.failed
        # Not persistent: the write is retried every cycle, and the notice
        # goes with the first one that lands.
        set_issue(
            self.hass,
            "dhw_disinfection_write_failed",
            switch.failed,
            placeholders={"entity_id": str(switch.failed_entity)},
        )

    async def async_release_switch(self) -> None:
        """On unload: turn off every switch this integration owns, unread.

        No further cycle will reconcile them, and a switch left on keeps the
        tank heating for as long as the integration stays unloaded. A record
        is dropped once its OFF has landed, so a program the user starts by
        hand while the integration is unloaded is not switched off at the
        next setup; a record whose OFF failed is kept for that setup.
        """
        await self.disinfect.release_blind()

    async def async_observe(self, dhw_temp: float | None, reader: Any) -> float | None:
        """One cycle: the observer on a reading, the cycle follower regardless; ``hours_since``."""
        if dhw_temp is not None:
            await self.async_track(dhw_temp)
        self.disinfect.observe(reader)
        await self.async_track_cycle(dhw_temp)
        self.check_ceiling()
        self.check_overdue()
        return self.hours_since()

    def _has_probe(self) -> bool:
        """Whether a tank sensor is configured to verify a cycle at all."""
        return bool(EntryConfig.from_mapping(self._config).dhw_temp_entity)

    def check_ceiling(self) -> None:
        """Say so when disinfection takes the tank above the charge limit.

        A warning, not a block. Since v5.1.10 the charge limit really is the
        highest temperature the plan charges to, and the disinfection
        temperature applies only during a cycle — so a 52/60 pair is a valid
        configuration with a consequence: once an interval the tank goes 8 °C
        above the limit. Judged from the parameters actually in force, which
        is what makes it cover the ``set_thermal_parameters`` service as well
        as the two config-flow pages; the flow's own validator warns at save
        time, but a service call never touches a form.
        """
        params = self._params()
        legionella = float(params.dhw_legionella_temp)
        setpoint = float(params.dhw_setpoint)
        # The stock pair says nothing. `dhw_enabled=True` alone gives 55/60,
        # both straight from DEFAULT_*, so raising a WARNING-severity,
        # non-fixable Repairs card on it put a permanent card on every fresh
        # install — one whose own text reads "That is allowed and nothing is
        # wrong", which is not what a Repairs card is for. Nothing about the
        # stock pair is a surprise the user needs telling; a pair they edited
        # to differ still is. The config flow logs the same fact at save time
        # for anyone who does set it up that way.
        stock = (
            legionella == float(DEFAULT_DHW_LEGIONELLA_TEMP)
            and setpoint == float(DEFAULT_DHW_SETPOINT)
        )
        active = (
            bool(params.dhw_enabled and params.dhw_legionella_enabled)
            and legionella > setpoint
            and not stock
        )
        signature = (
            (
                round(legionella, 1),
                round(setpoint, 1),
                round(float(params.dhw_legionella_interval_days), 1),
            )
            if active
            else None
        )
        if signature == self.ceiling_notice:
            return
        self.ceiling_notice = signature
        legionella, setpoint, interval = signature or (0.0, 0.0, 0.0)
        # Not persistent: it is derived from configuration, so it is
        # re-raised on the next cycle for as long as the pair stands.
        set_issue(
            self.hass,
            "dhw_legionella_above_setpoint",
            signature is not None,
            placeholders={
                "legionella_temp": f"{legionella:.0f}",
                "setpoint": f"{setpoint:.0f}",
                "interval_days": f"{interval:.0f}",
            },
        )

    def raise_unreachable_issue(
        self, peak: float, target: float
    ) -> None:
        """Tell the user the disinfection cycle is not reaching temperature.

        Silent failure is the worst outcome available here: the user believes
        the tank is being disinfected weekly and it is not. Persistent, because
        the fact survives a restart in the store.
        """
        set_issue(
            self.hass,
            "dhw_legionella_unreachable",
            True,
            persistent=True,
            placeholders={"reached": f"{peak:.1f}", "target": f"{target:.0f}"},
        )

    def clear_unreachable_issue(self) -> None:
        """Take the notice down once a cycle actually reaches temperature."""
        clear_issue(self.hass, "dhw_legionella_unreachable")

    def raise_unverified_issue(self, target: float) -> None:
        """Say that the cycle was commanded but nothing confirmed it ran.

        This integration publishes a plan; whether the pump obeyed it is
        something only a tank temperature can answer. Without one, a
        commanded cycle is a request, not a disinfection — and telling the
        user their water is being disinfected weekly when nothing checked is
        the one failure mode worth a notice all by itself. Persistent,
        because the fact survives a restart.
        """
        set_issue(
            self.hass,
            "dhw_legionella_unverified",
            True,
            persistent=True,
            placeholders={"target": f"{target:.0f}"},
        )

    def clear_unverified_issue(self) -> None:
        """Take it down once a cycle is actually observed at temperature."""
        clear_issue(self.hass, "dhw_legionella_unverified")

    def hours_since(self) -> float | None:
        """The countdown's age in hours, which the planner places the cycle by.

        Hours since the last completed cycle, except after a newer cycle that
        RAN but fell short. That is not success and nothing pretends it was,
        but it bounds the retry rate: an overdue age used to pin a 60 °C
        requirement on the first step of every plan, re-commanded every
        quarter of an hour and never once completed. So the age after an
        attempt leaves the cycle due again ``DHW_LEGIONELLA_RETRY_HOURS``
        later, never later than the completion itself makes it. With no tank
        probe a retry learns nothing a later one would not, and the attempt
        spaces the next by the whole interval, as a completion would.
        """
        last = self.last_cycle
        attempt = self._pending_attempt()
        # #1299: UTC instants — a shared ZoneInfo subtracts as wall clocks.
        now = dt_util.now()
        since = None if last is None else utc_elapsed_seconds(now, last) / 3600.0
        if attempt is not None:
            interval_h = max(0.0, float(self._params.dhw_legionella_interval_days) * 24.0)
            age = interval_h - self._retry_hours() + utc_elapsed_seconds(now, attempt) / 3600.0
            since = age if since is None else min(since, age)
        if since is None:
            return None
        return max(0.0, since)

    def _pending_attempt(self) -> datetime | None:
        """The attempt newer than the last completion, which the retry serves."""
        attempt, last = self.attempt, self.last_cycle
        if attempt is None or (last is not None and utc_elapsed_seconds(attempt, last) <= 0):
            return None
        return attempt

    def _retry_hours(self) -> float:
        """How long after an attempt the cycle is due again (``hours_since``)."""
        interval_h = max(0.0, float(self._params.dhw_legionella_interval_days) * 24.0)
        return min(interval_h, DHW_LEGIONELLA_RETRY_HOURS) if self._has_probe() else interval_h

    def due_in_hours(self) -> float | None:
        """Hours left before the next anti-legionella cycle is required."""
        params = self._params()
        if not params.dhw_legionella_enabled:
            return None
        since = self.hours_since()
        if since is None:
            return None
        return float(round(params.dhw_legionella_interval_days * 24.0 - since, 1))

    def check_overdue(self) -> None:
        """Say so while no cycle has been confirmed for longer than the interval.

        The attempt notices each speak for one way a cycle can fall short,
        and a cycle cut off before it got hot, or one with a silent probe,
        raises none of them: the countdown restarted on each attempt and the
        tank went weeks undisinfected without a word (D15 lead L8). This one
        reads the last confirmed completion alone, whatever the attempts did.
        With no tank probe ``dhw_legionella_unverified`` is that notice.
        """
        params = self._params
        days = days_since_confirmed(
            self.last_cycle,
            dt_util.now(),
            float(params.dhw_legionella_interval_days),
            watched=bool(params.dhw_enabled and params.dhw_legionella_enabled)
            and self._has_probe(),
        )
        if days == self.overdue_notice:
            return
        self.overdue_notice = days
        set_issue(
            self.hass,
            "dhw_legionella_overdue",
            days is not None,
            placeholders={
                "days": f"{days}",
                "interval_days": f"{float(params.dhw_legionella_interval_days):.0f}",
            },
        )

    def check_mode_block(self, dhw_blocked: bool) -> None:
        """Say so when a mode block is holding disinfection past its deadline.

        A hot-water channel the pump's mode has blocked is hard-zeroed for
        the whole horizon, so the anti-legionella cycle simply never gets
        placed: ``dhw_legionella_due_in_hours`` goes negative in an attribute
        and nothing else happens. A pump left in a heating-only mode for a
        fortnight therefore stops disinfecting the tank silently, which is
        the same failure ``dhw_legionella_unreachable`` exists to prevent,
        arriving by a different route — the cycle is not falling short of
        temperature, it is not being scheduled at all.

        Only ever a notice: the mode block is never released, here or
        anywhere else. Putting hot water back into the plan would promise
        water the hardware refuses to heat.
        """
        params = self._params()
        due = self.due_in_hours()
        overdue_days: int | None = None
        if (
            dhw_blocked
            and bool(params.dhw_enabled)
            and bool(params.dhw_legionella_enabled)
            and due is not None
            and due < 0.0
        ):
            overdue_days = max(1, int(-due // 24.0) + 1)
        if overdue_days == self.mode_block_notice:
            return
        self.mode_block_notice = overdue_days
        if overdue_days is not None:
            _LOGGER.warning(
                "The anti-legionella cycle has been due for %d day(s) but the "
                "heat pump's mode makes no hot water, so it cannot be planned",
                overdue_days,
            )
        # Not persistent: it is derived from the live mode reading, so it is
        # re-raised on the next cycle for as long as the mode stands.
        set_issue(
            self.hass,
            "dhw_legionella_mode_blocked",
            overdue_days is not None,
            placeholders={
                "overdue_days": f"{overdue_days}",
                "interval_days": f"{float(params.dhw_legionella_interval_days):.0f}",
            },
        )

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
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_DHW_FREE_DISINFECTION_ENABLED,
    CONF_DHW_TEMP_ENTITY,
    DEFAULT_DHW_FREE_DISINFECTION_ENABLED,
    DEFAULT_DHW_LEGIONELLA_TEMP,
    DEFAULT_DHW_SETPOINT,
    DHW_LEGIONELLA_BOOST_MAX_HOURS,
    DHW_LEGIONELLA_HOLD_MINUTES,
    DOMAIN,
)
from .dhw_learning import DHW_PROFILE_STORE_VERSION
from .optimizer import REASON_LEGIONELLA
from .setpoint_check import create_issue
from .thermal_model import ThermalParameters

_LOGGER = logging.getLogger(__name__)


class LegionellaGuard:
    """The disinfection cycle's state, its ceilings and its repair notices."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        params: ThermalParameters,
        config: dict[str, Any],
        *,
        action: Callable[[], dict[str, Any]],
    ) -> None:
        self.hass = hass
        self._params = params
        self._config = config
        #: The action the plan currently commands, observed and never held.
        self._action = action
        self.last_cycle: datetime | None = None
        self.store: Store[dict[str, Any]] = Store(
            hass,
            DHW_PROFILE_STORE_VERSION,
            f"{DOMAIN}_{entry_id}_dhw_legionella",
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
        #: reported as such; it exists so the retry happens once per
        #: interval instead of on the first step of every single plan.
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

    async def async_load(self) -> None:
        """Load the timestamp of the last completed anti-legionella cycle.

        A fresh install has no record. It is initialised to "now" rather than
        "never" so a brand-new setup does not immediately blast the tank to the
        legionella temperature.
        """
        try:
            stored = await self.store.async_load()
            raw = (stored or {}).get("last_cycle")
            parsed = dt_util.parse_datetime(raw) if isinstance(raw, str) else None
            # A cycle that ran but fell short is remembered separately, so a
            # restart cannot turn a failed attempt back into an overdue timer
            # that pins a boost on every plan.
            attempt_raw = (stored or {}).get("last_attempt")
            attempt = (
                dt_util.parse_datetime(attempt_raw)
                if isinstance(attempt_raw, str)
                else None
            )
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

    async def async_save(self) -> None:
        """Persist the timestamp of the last completed anti-legionella cycle."""
        if self.last_cycle is None:
            return
        payload: dict[str, Any] = {
            "last_cycle": self.last_cycle.isoformat()
        }
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
        target = float(self._params.dhw_legionella_temp)
        now = dt_util.now()

        if bool(
            self._config.get(
                CONF_DHW_FREE_DISINFECTION_ENABLED,
                DEFAULT_DHW_FREE_DISINFECTION_ENABLED,
            )
        ):
            if dhw_temp >= target - 0.5:
                previous_obs = self.hold_last
                # Accumulate only hot-to-hot gaps: an interval that STARTED
                # cold proves nothing about the water in between. Capped so
                # a long observation gap cannot claim more than was
                # plausibly held.
                if previous_obs is not None:
                    gap_min = (now - previous_obs).total_seconds() / 60.0
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
        if previous is not None and (now - previous).total_seconds() < 3600:
            return
        self.hold_minutes = 0.0
        self.last_cycle = now
        # A real cycle clears any record of one that fell short, and takes the
        # "cannot reach temperature" notice down with it.
        self.attempt = None
        self.attempt_peak = None
        self.clear_unreachable_issue()
        self.clear_unverified_issue()
        _LOGGER.info(
            "DHW anti-legionella cycle observed at %.1f°C, timer reset", dhw_temp
        )
        await self.async_save()

    async def async_track_cycle(
        self, dhw_temp: float | None
    ) -> None:
        """Follow the disinfection boost the PLAN commanded, to its end.

        The observer above resets the timer only on seeing the tank at
        ``legionella_temp - 1``. That is the only reset path there is, and it
        has two holes:

        * a pump that cannot physically get the tank to 60 °C never triggers
          it, so ``hours_since`` runs past the interval and never comes back;
        * with no tank probe configured it cannot run at all, while the
          countdown keeps advancing on the clock.

        Either way the cycle is permanently overdue — and an overdue cycle
        used to pin a 60 °C requirement on the first step of every plan, for
        ever, while never actually disinfecting anything. Both the scheduling
        half and the user-facing half of that are fixed here: the boost the
        plan commanded is followed to its end, and what happened is recorded
        honestly.

        "Its end" has to be bounded, because a cycle the tank cannot finish
        is re-commanded on every solve and its boost window never closes on
        its own. After ``DHW_LEGIONELLA_BOOST_MAX_HOURS`` the window is
        closed here and judged on what it managed — otherwise a pump heating
        towards a temperature it will never reach would do so indefinitely,
        and nothing would ever be recorded or reported.

        Success is never inferred from the peak this saw. The observer above
        owns that decision, and its rule differs with the free-disinfection
        flag; asking "did the observer credit a cycle while this boost ran?"
        is the same question on both sides of it. Reading the peak instead
        left a cycle topping out in the half-degree between the two rules
        neither credited nor recorded, with the countdown pinned at its
        overdue value for ever.
        """
        params = self._params
        if not params.dhw_legionella_enabled:
            self.boost_active = False
            self.boost_peak = None
            self.boost_started = None
            return

        now = dt_util.now()
        commanded = (
            str(self._action().get("dhw_reason") or "") == REASON_LEGIONELLA
        )
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
                and (now - started).total_seconds()
                >= DHW_LEGIONELLA_BOOST_MAX_HOURS * 3600.0
            )
            if not expired:
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
        elif not self.boost_active:
            return

        # The boost window closed — either the plan moved on, or it outlasted
        # the bound above. Decide what it achieved.
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
            and self.last_cycle >= started
        )
        if credited:
            return

        has_probe = bool(self._config.get(CONF_DHW_TEMP_ENTITY))
        if not has_probe:
            # No way to verify, ever. What is recorded is an ATTEMPT, not a
            # completion: nothing observed the tank, and this integration
            # publishes a plan — the actuation may be an external automation
            # that never ran. An attempt already drives `hours_since` from
            # 192 h to 0 exactly as a completion would, because
            # `_dhw_hours_since_legionella` counts attempts too, so claiming
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
            # by the interval rather than repeated on every solve.
            self.attempt = now
            self.attempt_peak = None
            _LOGGER.warning(
                "DHW anti-legionella cycle ran with no usable tank reading; "
                "it cannot be confirmed and will be retried next interval"
            )
            await self.async_save()
            return

        self.attempt = now
        self.attempt_peak = float(peak)
        if peak >= target - 1.0:
            # It got to temperature but the completion was never credited —
            # under the free-disinfection flag that means the hold was not
            # observed for long enough. The retry is spaced by the interval,
            # and no "cannot reach temperature" notice is raised, because the
            # tank plainly can.
            _LOGGER.warning(
                "DHW anti-legionella cycle reached %.1f °C but the completion "
                "could not be confirmed; it will be retried next interval",
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
        params = self._params
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
        if signature is None:
            try:
                ir.async_delete_issue(
                    self.hass, DOMAIN, "dhw_legionella_above_setpoint"
                )
            except Exception as err:  # noqa: BLE001 - clearing is best-effort
                _LOGGER.debug("Could not clear legionella ceiling notice: %s", err)
            return
        legionella, setpoint, interval = signature
        create_issue(
            self.hass,
            DOMAIN,
            "dhw_legionella_above_setpoint",
            is_fixable=False,
            # Not persistent: it is derived from configuration, so it is
            # re-raised on the next cycle for as long as the pair stands.
            severity=ir.IssueSeverity.WARNING,
            translation_key="dhw_legionella_above_setpoint",
            translation_placeholders={
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
        create_issue(
            self.hass,
            DOMAIN,
            "dhw_legionella_unreachable",
            is_fixable=False,
            is_persistent=True,
            severity=ir.IssueSeverity.WARNING,
            translation_key="dhw_legionella_unreachable",
            translation_placeholders={
                "reached": f"{peak:.1f}",
                "target": f"{target:.0f}",
            },
        )

    def clear_unreachable_issue(self) -> None:
        """Take the notice down once a cycle actually reaches temperature."""
        try:
            ir.async_delete_issue(self.hass, DOMAIN, "dhw_legionella_unreachable")
        except Exception as err:  # noqa: BLE001 - clearing is best-effort
            _LOGGER.debug("Could not clear legionella issue: %s", err)

    def raise_unverified_issue(self, target: float) -> None:
        """Say that the cycle was commanded but nothing confirmed it ran.

        This integration publishes a plan; whether the pump obeyed it is
        something only a tank temperature can answer. Without one, a
        commanded cycle is a request, not a disinfection — and telling the
        user their water is being disinfected weekly when nothing checked is
        the one failure mode worth a notice all by itself. Persistent,
        because the fact survives a restart.
        """
        create_issue(
            self.hass,
            DOMAIN,
            "dhw_legionella_unverified",
            is_fixable=False,
            is_persistent=True,
            severity=ir.IssueSeverity.WARNING,
            translation_key="dhw_legionella_unverified",
            translation_placeholders={"target": f"{target:.0f}"},
        )

    def clear_unverified_issue(self) -> None:
        """Take it down once a cycle is actually observed at temperature."""
        try:
            ir.async_delete_issue(self.hass, DOMAIN, "dhw_legionella_unverified")
        except Exception as err:  # noqa: BLE001 - clearing is best-effort
            _LOGGER.debug("Could not clear legionella notice: %s", err)

    def hours_since(self) -> float | None:
        """Hours since the last anti-legionella cycle, or None if unknown.

        A cycle that RAN but fell short counts here too. It is not success —
        nothing pretends it was — but it does bound the retry rate. Without
        it, a pump that cannot reach the disinfection temperature leaves the
        timer permanently overdue, and an overdue timer used to pin a 60 °C
        requirement on the first step of every plan for ever: the boost was
        re-commanded every quarter of an hour and never once completed.
        """
        last = self.last_cycle
        attempt = self.attempt
        if attempt is not None and (last is None or attempt > last):
            last = attempt
        if last is None:
            return None
        delta = (dt_util.now() - last).total_seconds() / 3600.0
        return max(0.0, delta)

    def due_in_hours(self) -> float | None:
        """Hours left before the next anti-legionella cycle is required."""
        params = self._params
        if not params.dhw_legionella_enabled:
            return None
        since = self.hours_since()
        if since is None:
            return None
        return float(round(params.dhw_legionella_interval_days * 24.0 - since, 1))

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
        params = self._params
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
        if overdue_days is None:
            try:
                ir.async_delete_issue(
                    self.hass, DOMAIN, "dhw_legionella_mode_blocked"
                )
            except Exception as err:  # noqa: BLE001 - clearing is best-effort
                _LOGGER.debug(
                    "Could not clear legionella mode-block notice: %s", err
                )
            return
        _LOGGER.warning(
            "The anti-legionella cycle has been due for %d day(s) but the "
            "heat pump's mode makes no hot water, so it cannot be planned",
            overdue_days,
        )
        create_issue(
            self.hass,
            DOMAIN,
            "dhw_legionella_mode_blocked",
            is_fixable=False,
            # Not persistent: it is derived from the live mode reading, so it
            # is re-raised on the next cycle for as long as the mode stands.
            severity=ir.IssueSeverity.WARNING,
            translation_key="dhw_legionella_mode_blocked",
            translation_placeholders={
                "overdue_days": f"{overdue_days:d}",
                "interval_days": f"{float(params.dhw_legionella_interval_days):.0f}",
            },
        )

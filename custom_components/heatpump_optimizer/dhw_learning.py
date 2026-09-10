"""The hot-water usage profile and draw learner.

The first subsystem carved out of ``HeatPumpOptimizerCoordinator`` (W5-G9,
2026-09-10). It owns the learned hourly draw profile, the weekday/weekend
day-type profiles (#18), the per-window draw statistics (#32) and the tank's
standby cooling rate, together with the two Home Assistant stores that persist
them. The coordinator constructs one, hands it the shared ``ThermalParameters``
it learns into, and three narrow callables for the state it must observe; the
learner never holds the coordinator.

Bodies moved verbatim from the coordinator; the only edits are the substitution
of the coordinator's private names for this class's public ones, the three
observed values that arrive through callables instead of ``self``, and the
freeze reason that is returned to the caller instead of written onto it.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

import numpy as np

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_DHW_TEMP_ENTITY,
    DHW_COOLING_RATE_MAX,
    DHW_COOLING_RATE_MIN,
    DHW_COOLING_REFERENCE_DELTA,
    DHW_DAYTYPE_BLEND_K,
    DOMAIN,
)
from .dhw_draws import DrawStats, labels_for, window_label as draw_window_label
from .thermal_model import DHW_AMBIENT_TEMP, ThermalParameters

_LOGGER = logging.getLogger(__name__)

DHW_PROFILE_STORE_VERSION = 1
DHW_PROFILE_EWMA_ALPHA = 0.12
DHW_PROFILE_MIN_INTENSITY = 0.2
DHW_PROFILE_MAX_INTENSITY = 3.5

# Learning rates for the tank cooling model. Every observation is an upper
# bound on the true standby loss — an unnoticed draw can only make the tank
# look leakier than it is, never tighter. So the estimate follows the lower
# envelope of what is observed: it drops quickly towards a quieter reading and
# only creeps upward, which keeps a single shower from convincing the model
# that the tank is badly insulated.
DHW_COOLING_ALPHA_DOWN = 0.25
DHW_COOLING_ALPHA_UP = 0.02
# Sample intervals outside this range are useless: too short and sensor
# quantisation dominates, too long and the tank was almost certainly used.
DHW_COOLING_MIN_SAMPLE_HOURS = 0.25
DHW_COOLING_MAX_SAMPLE_HOURS = 6.0
# The tank has to be meaningfully warmer than its surroundings for the decay
# to carry any information about the loss coefficient.
DHW_COOLING_MIN_DELTA = 5.0


class DhwProfileLearner:
    """Usage profile, day-type profiles, draw statistics and cooling rate.

    ``params`` is the coordinator's live ``ThermalParameters``: the learner
    writes the pattern and the cooling rate into it exactly where the
    coordinator's methods did, so the solver reads what was learned without
    a second copy. ``frozen`` answers why learning should be skipped this
    interval, ``heating_active`` whether the plan is heating the tank now, and
    ``external_heat_active`` whether a wood burn is driving the tank — the
    three coordinator facts the learner observes and never owns.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        params: ThermalParameters,
        *,
        frozen: Callable[[str], str | None],
        heating_active: Callable[[], bool],
        external_heat_active: Callable[[], bool],
    ) -> None:
        self._params = params
        self._frozen = frozen
        self._heating_active = heating_active
        self._external_heat_active = external_heat_active
        self.last_temp_sample: float | None = None
        self.last_sample_time: datetime | None = None
        self.hourly_profile: list[float] = (
            params.dhw_hourly_draw_pattern.copy()
        )
        # Self-learned standby cooling of the tank, in °C/h at the reference
        # condition (45 °C tank, 20 °C ambient). Seeded from the configured
        # default until enough quiet decay has been observed.
        self.cooling_rate: float = float(params.dhw_cooling_rate)
        self.cooling_samples: int = 0
        self.heating_since_sample: bool = False
        self.profile_store: Store = Store(
            hass,
            DHW_PROFILE_STORE_VERSION,
            f"{DOMAIN}_{entry_id}_dhw_profile",
        )

        # --- Hot water, v4.0.0 T3 -----------------------------------------
        # #18: day-type profiles learned BESIDE the pooled one, blended
        # toward pooled by their own evidence. A store that has only ever
        # seen the pooled profile loads with zero day-type samples, which
        # blends to exactly the pooled answer.
        self.profile_weekday: list[float] = self.hourly_profile.copy()
        self.profile_weekend: list[float] = self.hourly_profile.copy()
        #: Distinct DAYS with draw evidence per day type — the blend's
        #: trust must measure days lived, not sensor ticks survived.
        self.daytype_samples: list[int] = [0, 0]  # [weekday, weekend]
        self.daytype_last_day: list[str] = ["", ""]
        # #32/#20: per-window draw-occurrence statistics, own store.
        self.draw_stats = DrawStats()
        self.draws_store: Store = Store(
            hass,
            DHW_PROFILE_STORE_VERSION,
            f"{DOMAIN}_{entry_id}_dhw_draws",
        )
        self.draws_dirty: bool = False

    def normalize_profile(self, profile: list[float]) -> list[float]:
        """Normalize and clamp DHW hourly profile (average ~= 1.0)."""
        default = self._params.dhw_hourly_draw_pattern.copy()
        if len(profile) != 24:
            return default
        try:
            cleaned = [float(np.clip(v, DHW_PROFILE_MIN_INTENSITY, DHW_PROFILE_MAX_INTENSITY)) for v in profile]
            avg = float(np.mean(cleaned))
        except (TypeError, ValueError):
            return default
        if avg <= 0:
            return default
        return [float(np.clip(v / avg, DHW_PROFILE_MIN_INTENSITY, DHW_PROFILE_MAX_INTENSITY)) for v in cleaned]

    async def async_load_profile(self) -> None:
        """Load the persisted DHW usage profile and tank cooling rate."""
        try:
            stored = dict(await self.profile_store.async_load() or {})
        except Exception as err:
            _LOGGER.debug("Could not load learned DHW profile: %s", err)
            return

        profile = stored.get("hourly_profile")
        if isinstance(profile, list) and len(profile) == 24:
            self.hourly_profile = self.normalize_profile(profile)
            self._params.dhw_hourly_draw_pattern = (
                self.hourly_profile.copy()
            )
            _LOGGER.info("Loaded learned DHW usage profile from storage")

        # #18: day-type profiles are additive keys. A pooled-only store —
        # every store written before T3 — leaves both arrays at the pooled
        # profile with zero samples, and the blend below then answers
        # exactly the pooled pattern.
        for attr, key, count_idx in (
            ("profile_weekday", "profile_weekday", 0),
            ("profile_weekend", "profile_weekend", 1),
        ):
            arr = stored.get(key)
            if isinstance(arr, list) and len(arr) == 24:
                setattr(self, attr, self.normalize_profile(arr))
            else:
                setattr(self, attr, self.hourly_profile.copy())
            try:
                self.daytype_samples[count_idx] = max(
                    0, int(stored.get(f"{key}_samples", 0))
                )
            except (TypeError, ValueError, OverflowError):
                self.daytype_samples[count_idx] = 0

        rate = stored.get("cooling_rate")
        if rate is None:
            return
        try:
            self.apply_cooling_rate(float(rate))
            self.cooling_samples = int(stored.get("cooling_samples", 0))
        except (TypeError, ValueError, OverflowError) as err:
            _LOGGER.debug("Could not load learned DHW cooling rate: %s", err)
            return
        _LOGGER.info(
            "Loaded learned DHW tank cooling rate %.2f °C/h (%d samples)",
            self.cooling_rate,
            self.cooling_samples,
        )

    def apply_cooling_rate(self, rate: float) -> None:
        """Clamp a cooling rate to a plausible range and push it to the model."""
        self.cooling_rate = float(
            np.clip(rate, DHW_COOLING_RATE_MIN, DHW_COOLING_RATE_MAX)
        )
        self._params.dhw_cooling_rate = self.cooling_rate

    async def async_set_cooling_rate(self, rate: float) -> None:
        """An explicit value replaces the learned one and resets the sample
        count, so the learner treats it as the new starting point."""
        self.apply_cooling_rate(rate)
        self.cooling_samples = 0
        await self.async_save_profile()

    def payload(self) -> dict[str, Any]:
        """The DHW profile store's exact save shape.

        One producer for both the store and the weekly snapshot (#42),
        same contract as ``_thermal_learning_payload``: a second
        hand-built copy is how formats drift.
        """
        return {
            "hourly_profile": self.hourly_profile,
            "cooling_rate": self.cooling_rate,
            "cooling_samples": self.cooling_samples,
            # #18: additive — old loaders ignore these keys.
            "profile_weekday": self.profile_weekday,
            "profile_weekend": self.profile_weekend,
            "profile_weekday_samples": self.daytype_samples[0],
            "profile_weekend_samples": self.daytype_samples[1],
        }

    def apply_payload(self, profile: dict[str, Any]) -> None:
        """Restore the profile half of a learner snapshot (#42 rollback)."""
        hourly = profile.get("hourly_profile")
        if isinstance(hourly, list) and len(hourly) == 24:
            self.hourly_profile = self.normalize_profile(hourly)
            self._params.dhw_hourly_draw_pattern = (
                self.hourly_profile.copy()
            )
        # The day-type profiles restore alongside the pooled one, or a
        # rollback would blend a rolled-back pool with un-rolled-back
        # day shapes — half of one week, half of another.
        for attr, key, count_idx in (
            ("profile_weekday", "profile_weekday", 0),
            ("profile_weekend", "profile_weekend", 1),
        ):
            arr = profile.get(key)
            if isinstance(arr, list) and len(arr) == 24:
                setattr(self, attr, self.normalize_profile(arr))
                try:
                    self.daytype_samples[count_idx] = max(
                        0, int(profile.get(f"{key}_samples", 0))
                    )
                except (TypeError, ValueError):
                    self.daytype_samples[count_idx] = 0
        rate = profile.get("cooling_rate")
        if rate is not None:
            try:
                self.apply_cooling_rate(float(rate))
            except (TypeError, ValueError):
                pass

    def apply_draws(self, draws: dict[str, Any]) -> None:
        """Restore the draw-statistics half of a learner snapshot."""
        self.draw_stats = DrawStats.from_dict(draws)

    async def async_save_profile(self) -> None:
        """Persist learned DHW profile to Home Assistant storage."""
        try:
            await self.profile_store.async_save(
                {
                    **self.payload(),
                    "updated_at": dt_util.now().isoformat(),
                }
            )
        except Exception as err:
            _LOGGER.debug("Could not persist DHW profile: %s", err)

    async def async_load_draws(self) -> None:
        """Load the per-window draw statistics (#32)."""
        try:
            stored = await self.draws_store.async_load()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not load DHW draw statistics: %s", err)
            return
        if isinstance(stored, dict):
            self.draw_stats = DrawStats.from_dict(stored)

    async def async_save_draws(self) -> None:
        try:
            await self.draws_store.async_save(self.draw_stats.as_dict())
            self.draws_dirty = False
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not persist DHW draw statistics: %s", err)

    def pattern_for(self, weekend: bool) -> list[float]:
        """The #18 blended pattern for one day type, volume-preserving.

        ``w = n/(n+K)`` leans on the pooled profile until the day type has
        real evidence of its own; the result is re-normalised so each day
        type still budgets the same daily volume — the profile decides
        *when*, never *how much*.
        """
        idx = 1 if weekend else 0
        daytype = (
            self.profile_weekend if weekend else self.profile_weekday
        )
        n = float(self.daytype_samples[idx])
        w = n / (n + DHW_DAYTYPE_BLEND_K) if n > 0 else 0.0
        if w <= 0.0:
            return self.hourly_profile.copy()
        blended = [
            (1.0 - w) * pooled + w * day
            for pooled, day in zip(self.hourly_profile, daytype)
        ]
        return self.normalize_profile(blended)

    async def async_learn_dynamics(self, dhw_temp: float) -> str | None:
        """Learn the tank's usage profile and its standby cooling rate.

        Both models are fed by the same observation — how far the tank
        temperature moved since the previous sample — so they are derived
        together from a single consistent measurement. Returns the freeze
        reason when learning was skipped for one, so the caller can record
        it; ``None`` otherwise.
        """
        now = dt_util.now()
        heating = bool(self._heating_active())

        previous_temp = self.last_temp_sample
        previous_time = self.last_sample_time
        heated_during_interval = self.heating_since_sample or heating

        self.last_temp_sample = dhw_temp
        self.last_sample_time = now
        self.heating_since_sample = heating

        frozen = self._frozen(CONF_DHW_TEMP_ENTITY)
        if frozen:
            return frozen

        if previous_temp is None or previous_time is None:
            return None

        dt_h = (now - previous_time).total_seconds() / 3600.0
        if dt_h <= 0.02 or dt_h > DHW_COOLING_MAX_SAMPLE_HOURS:
            return None

        temp_drop = previous_temp - dhw_temp

        if not heated_during_interval:
            await self.async_learn_cooling(previous_temp, dhw_temp, dt_h)
        await self.async_learn_usage(
            previous_temp,
            temp_drop,
            dt_h,
            now.hour,
            heated_during_interval,
            weekend=now.weekday() >= 5,
        )
        await self.async_fold_draw_stats(now, previous_temp, temp_drop, dt_h)
        return None

    async def async_fold_draw_stats(
        self, now: datetime, previous_temp: float, temp_drop: float, dt_h: float
    ) -> None:
        """Fold one interval's beyond-standby draw energy into #32's stats.

        External heat is the one contamination the freeze guard upstream
        does not cover: a wood burn drives the tank temperature and every
        drop-based attribution with it, so those intervals are skipped
        outright. Heated intervals ARE folded — heating makes the drop
        smaller, so the attributed energy is a lower bound of the true
        draw, which can only make the learned heavy-day target
        conservative relative to reality, never inflated.
        """
        if self._external_heat_active():
            return
        params = self._params
        if not params.dhw_enabled:
            return
        standby_rate = (
            self.cooling_rate
            * max(0.0, previous_temp - DHW_AMBIENT_TEMP)
            / DHW_COOLING_REFERENCE_DELTA
        )
        intensity = max(0.0, temp_drop / dt_h - standby_rate)  # °C/h beyond standby
        energy_kwh = (
            intensity * dt_h * max(params.dhw_tank_thermal_mass, 0.05)
        )
        windows = params.dhw_demand_windows
        label = draw_window_label(
            now.hour + now.minute / 60.0, windows
        )
        self.draw_stats.prune(labels_for(windows))
        before = {k: len(v) for k, v in self.draw_stats.reservoirs.items()}
        self.draw_stats.fold(now, label, energy_kwh)
        after = {k: len(v) for k, v in self.draw_stats.reservoirs.items()}
        # Persist when an occurrence closes, and also whenever real energy
        # was folded into the OPEN occurrence — as_dict carries it, and
        # saving only at close time meant a restart mid-shower silently
        # dropped everything since the last close, dragging the p90 down.
        # Zero-energy ticks (most of the day) still cause no churn.
        if before != after or energy_kwh > 1e-4:
            await self.async_save_draws()

    async def async_learn_cooling(
        self, previous_temp: float, dhw_temp: float, dt_h: float
    ) -> None:
        """Refine the tank cooling model from an interval with no heating.

        Standby decay follows ``C·dT/dt = -UA·(T - T_ambient)``, so a pair of
        temperatures bracketing an idle interval pins down the time constant:

            UA/C = -ln((T_end - T_amb) / (T_start - T_amb)) / Δt

        Scaled to the reference condition that gives a cooling rate in °C/h
        directly comparable to the configured default.

        Any hot water drawn during the interval inflates the estimate, which is
        why the result is folded in as a lower envelope rather than a plain
        average — see the alpha constants.
        """
        if dt_h < DHW_COOLING_MIN_SAMPLE_HOURS:
            return
        # A rise means the tank was heated or refilled from a hotter source;
        # either way it says nothing about standby loss.
        if dhw_temp > previous_temp:
            return

        start_delta = previous_temp - DHW_AMBIENT_TEMP
        end_delta = dhw_temp - DHW_AMBIENT_TEMP
        if start_delta < DHW_COOLING_MIN_DELTA or end_delta < DHW_COOLING_MIN_DELTA:
            return

        time_constant = -np.log(end_delta / start_delta) / dt_h  # 1/h
        observed = float(time_constant * DHW_COOLING_REFERENCE_DELTA)
        if not np.isfinite(observed):
            return
        if observed < DHW_COOLING_RATE_MIN or observed > DHW_COOLING_RATE_MAX:
            return

        alpha = (
            DHW_COOLING_ALPHA_DOWN
            if observed < self.cooling_rate
            else DHW_COOLING_ALPHA_UP
        )
        self.apply_cooling_rate(
            (1.0 - alpha) * self.cooling_rate + alpha * observed
        )
        self.cooling_samples += 1

        _LOGGER.debug(
            "Learned DHW cooling: %.2f°C→%.2f°C over %.2fh gives %.2f °C/h, "
            "model now %.2f °C/h (%d samples)",
            previous_temp,
            dhw_temp,
            dt_h,
            observed,
            self.cooling_rate,
            self.cooling_samples,
        )
        await self.async_save_profile()

    async def async_learn_usage(
        self,
        previous_temp: float,
        temp_drop: float,
        dt_h: float,
        hour: int,
        heated: bool,
        weekend: bool = False,
    ) -> None:
        """Learn hourly DHW usage profile from observed temperature drops."""
        # Learn only while DHW is not actively heated, and only from the part
        # of the drop that standby loss cannot explain. The tank cools all the
        # time — roughly 0.4 °C/h for a 55 °C tank at the default rate — and
        # attributing that to usage taught a phantom draw into every idle
        # hour, washing the real morning/evening pattern towards flat.
        if temp_drop < 0.15 or heated:
            return

        standby_rate = (
            self.cooling_rate
            * max(0.0, previous_temp - DHW_AMBIENT_TEMP)
            / DHW_COOLING_REFERENCE_DELTA
        )
        draw_intensity = temp_drop / dt_h - standby_rate
        if draw_intensity <= 0.05:
            return

        profile = self.hourly_profile.copy()
        profile[hour] = (
            (1.0 - DHW_PROFILE_EWMA_ALPHA) * profile[hour]
            + DHW_PROFILE_EWMA_ALPHA * draw_intensity
        )
        self.hourly_profile = self.normalize_profile(profile)
        self._params.dhw_hourly_draw_pattern = self.hourly_profile.copy()

        # #18: the same observation also teaches this day type's own
        # profile. Both are normalised independently, so each day type
        # preserves the daily volume on its own — the invariant the ready
        # targets stand on.
        idx = 1 if weekend else 0
        daytype = (
            self.profile_weekend if weekend else self.profile_weekday
        ).copy()
        daytype[hour] = (
            (1.0 - DHW_PROFILE_EWMA_ALPHA) * daytype[hour]
            + DHW_PROFILE_EWMA_ALPHA * draw_intensity
        )
        normalized = self.normalize_profile(daytype)
        if weekend:
            self.profile_weekend = normalized
        else:
            self.profile_weekday = normalized
        # Trust counts distinct days, not ticks: at a five-minute sample
        # cadence a tick counter would reach half-trust inside one
        # Saturday morning.
        day = dt_util.now().date().isoformat()
        if self.daytype_last_day[idx] != day:
            self.daytype_last_day[idx] = day
            self.daytype_samples[idx] += 1

        _LOGGER.debug(
            "Learned DHW usage hour=%d drop=%.2f°C dt=%.2fh intensity=%.2f",
            hour,
            temp_drop,
            dt_h,
            draw_intensity,
        )
        await self.async_save_profile()

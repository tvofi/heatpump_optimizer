"""Solar irradiance from Open-Meteo.

Most Home Assistant weather integrations publish temperature, wind and rain but
not irradiance, which left the thermal model planning with zero solar gain. On a
clear winter day in a glazed house that is a large, systematically one-sided
error: the optimizer buys heat it did not need.

Open-Meteo serves global horizontal irradiance for any coordinate, free and
without an API key, from two endpoints that this module uses for different jobs:

* ``/v1/forecast`` is the only one that looks *forward*, so it supplies the
  planning horizon. Where available it is queried at 15 minute resolution,
  which lines up exactly with the optimizer's step grid.
* The satellite archive is *observed* rather than modelled and is current to
  within about ten minutes, so it supplies "what is the sun doing right now".
  That value feeds the house heat loss learner, where using a modelled number
  would fold forecast error into the learned parameter.

The satellite endpoint has no forecast route, so it cannot replace the first;
the forecast endpoint is modelled, so it should not replace the second.

Timestamp convention
--------------------
Open-Meteo labels each radiation sample with the **end** of its averaging
interval: the value at 04:00 is the mean irradiance over 03:00-04:00. This was
verified against sunrise and sunset rather than assumed, at 60.06N on 2026-08-21
(sunrise 03:20, sunset 18:29 UTC): the first non-zero hourly sample is 04:00 and
the last is 19:00. Under a start-of-interval reading the 03:00 sample would have
had to be non-zero and the 19:00 sample zero, and both were the other way round.

Getting this backwards would shift every solar gain by a full interval, which
around sunrise and sunset is the difference between full sun and darkness.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    OPEN_METEO_FORECAST_URL,
    OPEN_METEO_MIN_REFRESH_MINUTES,
    OPEN_METEO_OBSERVED_MAX_AGE_MINUTES,
    OPEN_METEO_SATELLITE_MODEL,
    OPEN_METEO_SATELLITE_URL,
    OPEN_METEO_TIMEOUT_SECONDS,
)

_LOGGER = logging.getLogger(__name__)

# Global horizontal irradiance. The thermal model's ``solar_radiation`` is
# documented as GHI and its window gain multiplies by an orientation factor, so
# direct-beam radiation would be the wrong input: it excludes the diffuse
# component, which on an overcast day is essentially all of the light there is.
_VARIABLE = "shortwave_radiation"
# T4b: the defrost derate's second dimension (#21) and the rain/snow split
# (#30) ride the same forecast request. Hourly is enough for both — frost
# and precipitation type do not turn on quarter-hour timescales.
_VARIABLE_HUMIDITY = "relative_humidity_2m"
_VARIABLE_SNOWFALL = "snowfall"

# Physical ceiling used to reject nonsense rather than feed it to the model.
# The solar constant is ~1361 W/m^2; surface GHI cannot exceed it, and values
# above ~1200 only occur with cloud-edge focusing.
_MAX_PLAUSIBLE_GHI = 1400.0


def _ensure_utc(value: datetime) -> datetime:
    """Normalise a caller-supplied instant to UTC.

    Home Assistant's ``dt_util.now()`` normally returns an aware local
    datetime, but it yields a naive one when no timezone is configured. Naive
    values are interpreted as system local time, which is what that function
    means by them; the alternative, comparing a naive and an aware datetime,
    raises TypeError inside the coordinator's update loop and takes the whole
    optimization down over a timezone detail.
    """
    # astimezone() interprets a naive datetime as system local time, which is
    # exactly what dt_util.now() means by one, and is a no-op relabelling for
    # an aware one.
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class IrradianceSeries:
    """A uniformly spaced irradiance series in W/m^2.

    ``times`` are timezone-aware UTC and mark the END of each sample's
    averaging interval, so sample ``i`` describes ``(t_i - resolution, t_i]``.
    """

    times: tuple[datetime, ...]
    values: tuple[float, ...]
    resolution: timedelta

    def __bool__(self) -> bool:
        return bool(self.times)

    @property
    def start(self) -> datetime | None:
        """First instant covered by the series."""
        return self.times[0] - self.resolution if self.times else None

    @property
    def end(self) -> datetime | None:
        """Last instant covered by the series."""
        return self.times[-1] if self.times else None

    def mean_over(self, start: datetime, end: datetime) -> float | None:
        """Mean irradiance over ``[start, end)``, or None if not covered.

        Averaging by overlap rather than picking the nearest sample means the
        caller's step length does not have to match the API's resolution: an
        hourly series answers a 15 minute question, and a 10 minute series
        answers an hourly one, both without special cases.
        """
        if not self.times:
            return None
        start = _ensure_utc(start)
        end = _ensure_utc(end)
        if end <= start:
            return None

        total_weight = 0.0
        total = 0.0
        for t, v in zip(self.times, self.values):
            sample_start = t - self.resolution
            overlap = min(end, t) - max(start, sample_start)
            seconds = overlap.total_seconds()
            if seconds <= 0:
                continue
            total += v * seconds
            total_weight += seconds

        if total_weight <= 0:
            return None
        # Require the request to be mostly covered. A step that overlaps the
        # series by a few seconds at its edge would otherwise return a value
        # derived from almost none of the requested window.
        requested = (end - start).total_seconds()
        if total_weight < 0.5 * requested:
            return None
        return total / total_weight

    def latest_before(self, when: datetime, max_age: timedelta) -> float | None:
        """Most recent sample at or before ``when``, if fresh enough."""
        when = _ensure_utc(when)
        best: tuple[datetime, float] | None = None
        for t, v in zip(self.times, self.values):
            if t <= when and (best is None or t > best[0]):
                best = (t, v)
        if best is None:
            return None
        if when - best[0] > max_age:
            return None
        return best[1]


_EMPTY = IrradianceSeries(times=(), values=(), resolution=timedelta(hours=1))


def _parse_block(
    block: dict, variable: str, max_value: float = _MAX_PLAUSIBLE_GHI
) -> IrradianceSeries:
    """Build a series from one Open-Meteo time block, skipping null samples.

    Open-Meteo pads the tail of a block with nulls when a model has not
    produced that far ahead, and the satellite archive has gaps where no image
    was usable. Both must be dropped rather than coerced to zero, which would
    read as "no sun" instead of "no data". ``max_value`` is the variable's own
    plausibility ceiling — the GHI limit means nothing to a humidity series.
    """
    times_raw = block.get("time") or []
    values_raw = block.get(variable) or []

    times: list[datetime] = []
    values: list[float] = []
    for raw_t, raw_v in zip(times_raw, values_raw):
        if raw_v is None:
            continue
        try:
            value = float(raw_v)
        except (TypeError, ValueError):
            continue
        if value < 0.0 or value > max_value:
            continue
        try:
            # timezone=UTC is requested, so the naive ISO stamps are UTC.
            parsed = datetime.fromisoformat(str(raw_t))
        except ValueError:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        times.append(parsed.astimezone(timezone.utc))
        values.append(value)

    if len(times) < 2:
        return _EMPTY

    order = sorted(range(len(times)), key=lambda i: times[i])
    times = [times[i] for i in order]
    values = [values[i] for i in order]

    # Infer the sample interval from the data. Taking the smallest positive gap
    # rather than the first keeps a single missing sample from doubling the
    # inferred resolution and smearing every value across twice its true span.
    gaps = [
        (times[i + 1] - times[i]).total_seconds()
        for i in range(len(times) - 1)
        if (times[i + 1] - times[i]).total_seconds() > 0
    ]
    if not gaps:
        return _EMPTY
    resolution = timedelta(seconds=min(gaps))

    return IrradianceSeries(
        times=tuple(times), values=tuple(values), resolution=resolution
    )


class OpenMeteoSolar:
    """Fetches and caches irradiance for one coordinate."""

    def __init__(
        self, hass: HomeAssistant, latitude: float, longitude: float
    ) -> None:
        self._hass = hass
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self._forecast: IrradianceSeries = _EMPTY
        self._observed: IrradianceSeries = _EMPTY
        # T4b side series from the same forecast payload: relative humidity
        # in % (#21) and snowfall in cm per interval (#30). The series class
        # is a generic timestamped sequence despite its name.
        self._humidity: IrradianceSeries = _EMPTY
        self._snowfall: IrradianceSeries = _EMPTY
        self._last_success: datetime | None = None
        self._last_attempt: datetime | None = None
        self._failures = 0

    # ---- state ----------------------------------------------------------

    @property
    def forecast(self) -> IrradianceSeries:
        return self._forecast

    @property
    def observed(self) -> IrradianceSeries:
        return self._observed

    @property
    def available(self) -> bool:
        return bool(self._forecast) or bool(self._observed)

    @property
    def last_success(self) -> datetime | None:
        return self._last_success

    def matches(self, latitude: float, longitude: float) -> bool:
        """True when this client already covers the given coordinate."""
        return (
            abs(self.latitude - float(latitude)) < 1e-6
            and abs(self.longitude - float(longitude)) < 1e-6
        )

    # ---- reads ----------------------------------------------------------

    def irradiance_for(self, start: datetime, duration: timedelta) -> float | None:
        """Mean irradiance over one optimizer step.

        Observed satellite data wins where it exists, because for steps that
        have already partly happened it is measurement rather than prediction.
        """
        end = start + duration
        observed = self._observed.mean_over(start, end)
        if observed is not None:
            return observed
        return self._forecast.mean_over(start, end)

    def humidity_for(self, start: datetime, duration: timedelta) -> float | None:
        """Mean forecast relative humidity (%) over one optimizer step (#21)."""
        return self._humidity.mean_over(start, start + duration)

    def snowfall_for(self, start: datetime, duration: timedelta) -> float | None:
        """Mean forecast snowfall rate (cm/h) over one optimizer step (#30)."""
        return self._snowfall.mean_over(start, start + duration)

    def current_irradiance(self, now: datetime) -> float | None:
        """Best estimate of irradiance right now.

        Prefers the newest satellite observation, which trails real time by
        roughly ten minutes, and falls back to the forecast when the archive is
        stale or unreachable.
        """
        observed = self._observed.latest_before(
            now, timedelta(minutes=OPEN_METEO_OBSERVED_MAX_AGE_MINUTES)
        )
        if observed is not None:
            return observed
        return self._forecast.mean_over(now - timedelta(minutes=15), now)

    # ---- fetching -------------------------------------------------------

    def _should_refresh(self, now: datetime, force: bool) -> bool:
        if force or self._last_attempt is None:
            return True
        age = now - self._last_attempt
        return age >= timedelta(minutes=OPEN_METEO_MIN_REFRESH_MINUTES)

    async def async_refresh(self, now: datetime, force: bool = False) -> bool:
        """Refresh both series. Returns True when usable data is held.

        Never raises: a weather API being down must not stop the optimizer, so
        a failed refresh keeps the previous series and the caller carries on
        with slightly stale sun.
        """
        if not self._should_refresh(now, force):
            return self.available

        self._last_attempt = now
        session = async_get_clientsession(self._hass)

        forecast = await self._fetch_forecast(session)
        if forecast:
            self._forecast = forecast

        observed = await self._fetch_observed(session)
        if observed:
            self._observed = observed

        if forecast or observed:
            self._last_success = now
            if self._failures:
                _LOGGER.info(
                    "Open-Meteo solar irradiance recovered after %d failure(s)",
                    self._failures,
                )
            self._failures = 0
        else:
            self._failures += 1
            # Log loudly once, then stay quiet: a multi-hour outage should not
            # fill the log with one warning per coordinator cycle.
            if self._failures == 1:
                # No coordinates in the message: four decimals of
                # geolocation is identifying, and diagnostics() already
                # publishes rounded ones where they are wanted.
                _LOGGER.warning(
                    "Could not fetch solar irradiance from Open-Meteo; "
                    "continuing with cached data"
                )
            else:
                _LOGGER.debug(
                    "Open-Meteo solar fetch still failing (%d consecutive)",
                    self._failures,
                )

        return self.available

    async def _get_json(
        self, session: aiohttp.ClientSession, url: str, params: dict
    ) -> dict | None:
        try:
            async with session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=OPEN_METEO_TIMEOUT_SECONDS),
            ) as resp:
                if resp.status != 200:
                    _LOGGER.debug(
                        "Open-Meteo %s returned HTTP %s", url, resp.status
                    )
                    return None
                # The API answers errors with 400 + JSON, but content type has
                # been seen to vary, so do not let aiohttp police it.
                data = await resp.json(content_type=None)
        except Exception as err:  # noqa: BLE001 - never break the update cycle
            _LOGGER.debug("Open-Meteo request to %s failed: %s", url, err)
            return None

        if not isinstance(data, dict) or data.get("error"):
            _LOGGER.debug(
                "Open-Meteo %s reported an error: %s",
                url,
                data.get("reason") if isinstance(data, dict) else data,
            )
            return None
        return data

    async def _fetch_forecast(
        self, session: aiohttp.ClientSession
    ) -> IrradianceSeries:
        """Forward horizon, at 15 minute resolution where the model offers it."""
        data = await self._get_json(
            session,
            OPEN_METEO_FORECAST_URL,
            {
                "latitude": f"{self.latitude:.6f}",
                "longitude": f"{self.longitude:.6f}",
                "minutely_15": _VARIABLE,
                "hourly": ",".join(
                    (_VARIABLE, _VARIABLE_HUMIDITY, _VARIABLE_SNOWFALL)
                ),
                # UTC keeps parsing unambiguous and immune to DST transitions,
                # which is exactly the kind of edge a heating plan spans.
                "timezone": "UTC",
                # Two days covers the longest supported optimization horizon
                # with room for the run to start late in the day.
                "forecast_days": "3",
            },
        )
        if data is None:
            return _EMPTY

        # The side series (#21 #30) parse from the same hourly block; a
        # missing variable leaves the previous series in place, exactly
        # like a failed irradiance fetch.
        hourly_block = data.get("hourly") or {}
        humidity = _parse_block(hourly_block, _VARIABLE_HUMIDITY, max_value=100.0)
        if humidity:
            self._humidity = humidity
        # 50 cm in one hour is beyond any recorded snowfall rate.
        snowfall = _parse_block(hourly_block, _VARIABLE_SNOWFALL, max_value=50.0)
        if snowfall:
            self._snowfall = snowfall

        fine = _parse_block(data.get("minutely_15") or {}, _VARIABLE)
        coarse = _parse_block(hourly_block, _VARIABLE)

        # 15 minute data is only published for some regions and models. Prefer
        # it when present, but only if it actually spans a useful horizon;
        # otherwise the hourly block is the more complete answer.
        if fine and coarse and fine.end and coarse.end:
            if fine.end >= coarse.end - timedelta(hours=6):
                return fine
            return coarse
        return fine or coarse

    async def _fetch_observed(
        self, session: aiohttp.ClientSession
    ) -> IrradianceSeries:
        """Recent observed irradiance from the geostationary satellite archive."""
        data = await self._get_json(
            session,
            OPEN_METEO_SATELLITE_URL,
            {
                "latitude": f"{self.latitude:.6f}",
                "longitude": f"{self.longitude:.6f}",
                "hourly": _VARIABLE,
                "models": OPEN_METEO_SATELLITE_MODEL,
                "timezone": "UTC",
                # Native resolution is ~10 minutes; resampling to hours here
                # would throw away the freshness that makes this worth calling.
                "temporal_resolution": "native",
            },
        )
        if data is None:
            return _EMPTY
        return _parse_block(data.get("hourly") or {}, _VARIABLE)

    def diagnostics(self) -> dict:
        """Small summary for sensor attributes and troubleshooting."""
        return {
            "latitude": round(self.latitude, 5),
            "longitude": round(self.longitude, 5),
            "forecast_points": len(self._forecast.times),
            "forecast_resolution_minutes": int(
                self._forecast.resolution.total_seconds() // 60
            )
            if self._forecast
            else None,
            "forecast_until": self._forecast.end.isoformat()
            if self._forecast.end
            else None,
            "observed_points": len(self._observed.times),
            "observed_until": self._observed.end.isoformat()
            if self._observed.end
            else None,
            "humidity_points": len(self._humidity.times),
            "snowfall_points": len(self._snowfall.times),
            "last_success": self._last_success.isoformat()
            if self._last_success
            else None,
            "consecutive_failures": self._failures,
        }

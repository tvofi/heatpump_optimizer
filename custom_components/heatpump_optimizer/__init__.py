"""Heat Pump Cost Optimizer integration for Home Assistant.

This integration optimizes heat pump operation to minimize electricity costs
using Model Predictive Control (MPC). It integrates with Tibber for electricity
prices and Home Assistant weather entities for temperature forecasts.

The optimization accounts for:
- Thermal mass of slab floor heating (slow response)
- Weather-dependent heat loss
- COP variation with outdoor temperature
- Pre-heating before expensive periods
- Temperature setback during expensive periods
"""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.loader import async_get_integration
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONFIG_ENTRY_VERSION,
    CONF_COMFORT_TEMP_DAY,
    CONF_DAY_END_HOUR,
    CONF_DAY_START_HOUR,
    CONF_DHW_MIN_TEMP,
    CONF_DHW_SETPOINT,
    CONF_DHW_WINDOWS,
    MANUAL_PLAN_WINDOW_HOURS,
    DEFAULT_DAY_END_HOUR,
    DEFAULT_DAY_START_HOUR,
    DEFAULT_DHW_SETPOINT,
    DHW_MIN_TEMP_SETPOINT_MARGIN,
    SERVICE_APPLY_SCHEDULE,
    SERVICE_ASSIGN_ENTITY,
    SERVICE_APPLY_MANUAL_PLAN,
    SERVICE_CLEAR_MANUAL_PLAN,
    SERVICE_RUN_OPTIMIZATION,
    SERVICE_SET_MODE,
    SERVICE_SET_THERMAL_PARAMS,
    SERVICE_SIMULATE_PLAN,
    MODE_AUTO,
    MODE_COMFORT,
    MODE_ECONOMY,
    OPERATION_MODES,
    MODE_OFF,
    MODE_BOOST,
)
from .coordinator import HeatPumpOptimizerCoordinator
from .dhw_schedule import DHWWindowError, format_windows, parse_windows
from .frontend import async_register_frontend
from . import topology
from .manual_plan import ManualPlanError, build_override

_LOGGER = logging.getLogger(__name__)

PLATFORM_LIST = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.SWITCH,
]

SERVICE_SCHEMA_RUN_OPTIMIZATION = vol.Schema({})

# What-if simulator (item 21). Every field is optional: the card sends only the
# one the user is dragging, and anything absent keeps its configured value.
SERVICE_SCHEMA_SIMULATE_PLAN = vol.Schema(
    {
        vol.Optional("target_temp"): vol.Coerce(float),
        vol.Optional("min_temp"): vol.Coerce(float),
        vol.Optional("max_temp"): vol.Coerce(float),
        vol.Optional("comfort_temp_day"): vol.Coerce(float),
        vol.Optional("comfort_temp_night"): vol.Coerce(float),
        vol.Optional("comfort_weight"): vol.Coerce(float),
        # The heating schedule: which hours get the day comfort temperature.
        vol.Optional("day_start_hour"): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=23)
        ),
        vol.Optional("day_end_hour"): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=24)
        ),
        vol.Optional("dhw_setpoint"): vol.Coerce(float),
        vol.Optional("dhw_min_temperature"): vol.Coerce(float),
        # An empty string is meaningful here: it simulates having no demand
        # windows at all, so it must survive the "drop empty values" filter in
        # the handler below.
        vol.Optional("dhw_windows"): cv.string,
    }
)

SERVICE_SCHEMA_SET_MODE = vol.Schema(
    {
        vol.Required("mode"): vol.In(
            list(OPERATION_MODES)
        ),
    }
)

# Assign one optional sensor from the card's setup diagram (item 32).
#
# One of two services that write to the config entry, and deliberately the
# narrower: one key, one entity, both checked against the same slot table the
# diagram is drawn from. ``entity_id`` may be an empty string, which clears
# the slot -- unassigning has to be possible from the same place assigning is,
# or the diagram becomes a one-way door.
SERVICE_SCHEMA_ASSIGN_ENTITY = vol.Schema(
    {
        vol.Required("key"): vol.In(sorted(topology.ASSIGNABLE_KEYS)),
        vol.Required("entity_id"): cv.string,
        vol.Optional("entry_id"): cv.string,
    }
)

# Persist a schedule the user arrived at in the what-if simulator.
#
# Deliberately narrow: it accepts the fields the card can edit and nothing
# else. Ranges are enforced here rather than in the handler so a bad call is
# rejected before it can touch stored configuration.
SERVICE_SCHEMA_APPLY_SCHEDULE = vol.Schema(
    {
        vol.Optional("day_start_hour"): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=23)
        ),
        vol.Optional("day_end_hour"): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=24)
        ),
        # An empty string is meaningful: it means "no guaranteed hot water
        # windows at all", so it must not be filtered out as a blank.
        vol.Optional("dhw_windows"): cv.string,
        vol.Optional("comfort_temp_day"): vol.All(
            vol.Coerce(float), vol.Range(min=5, max=30)
        ),
        # The coarse range matches the options flow; the real ceiling depends
        # on the entry's own ``dhw_setpoint`` and so is checked per entry in
        # the handler, where that setpoint is in hand.
        vol.Optional("dhw_min_temperature"): vol.All(
            vol.Coerce(float), vol.Range(min=35, max=55)
        ),
        # Restrict the write to one config entry. Omitted means every entry,
        # which matches how simulate_plan behaves and is what the card wants
        # on a single-heat-pump install.
        vol.Optional("entry_id"): cv.string,
    }
)

# A slot is one contiguous run the user pinned; the deep validation (parseable
# datetimes, end > start, no overlap) lives in ``manual_plan`` so it stays
# unit-testable, and the schema only guarantees the coarse shape. ``vol.Any``
# with ``None`` keeps the "omitted / null means automatic" distinction the
# handler relies on — an explicit empty list still arrives as ``[]``.
_MANUAL_SLOT_LIST = vol.Any(None, [dict])

SERVICE_SCHEMA_APPLY_MANUAL_PLAN = vol.Schema(
    {
        vol.Optional("dhw_slots"): _MANUAL_SLOT_LIST,
        vol.Optional("space_slots"): _MANUAL_SLOT_LIST,
        vol.Optional("expires_at"): cv.string,
        vol.Optional("entry_id"): cv.string,
    }
)

SERVICE_SCHEMA_CLEAR_MANUAL_PLAN = vol.Schema(
    {
        vol.Optional("entry_id"): cv.string,
    }
)

# Ranges guard the physics, not just the UI: services.yaml selectors only
# constrain the Developer Tools form, and an automation calling with a zero
# thermal mass or a power fraction above 1 would otherwise flow straight into
# the model as a division by zero or a heat flow with the wrong sign.
def _positive(upper: float) -> vol.All:
    return vol.All(vol.Coerce(float), vol.Range(min=0.01, max=upper))


SERVICE_SCHEMA_SET_THERMAL_PARAMS = vol.Schema(
    {
        vol.Optional("house_thermal_mass"): _positive(200),
        vol.Optional("house_heat_loss_coefficient"): _positive(10),
        vol.Optional("slab_thermal_mass"): _positive(200),
        vol.Optional("slab_heat_transfer"): _positive(50),
        vol.Optional("heat_pump_cop_nominal"): vol.All(
            vol.Coerce(float), vol.Range(min=1.0, max=8.0)
        ),
        vol.Optional("upper_floor_thermal_mass"): _positive(200),
        vol.Optional("lower_floor_thermal_mass"): _positive(200),
        vol.Optional("inter_zone_heat_transfer"): _positive(50),
        vol.Optional("radiator_power_fraction"): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        vol.Optional("window_area"): _positive(500),
        vol.Optional("solar_heat_gain_coefficient"): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        # DHW parameters
        vol.Optional("dhw_tank_volume"): _positive(2000),
        vol.Optional("dhw_setpoint"): vol.All(
            vol.Coerce(float), vol.Range(min=30, max=75)
        ),
        vol.Optional("dhw_min_temperature"): vol.All(
            vol.Coerce(float), vol.Range(min=10, max=70)
        ),
        vol.Optional("dhw_daily_consumption"): _positive(2000),
        vol.Optional("dhw_cooling_rate"): _positive(5),
        vol.Optional("buffer_cooling_rate"): _positive(50),
        vol.Optional("dhw_schedule_enabled"): cv.boolean,
        vol.Optional("dhw_windows"): cv.string,
        vol.Optional("dhw_idle_min_temperature"): vol.All(
            vol.Coerce(float), vol.Range(min=5, max=60)
        ),
        vol.Optional("dhw_legionella_enabled"): cv.boolean,
        vol.Optional("dhw_legionella_temperature"): vol.All(
            vol.Coerce(float), vol.Range(min=55, max=75)
        ),
        vol.Optional("dhw_legionella_interval_days"): _positive(60),
        # Weather sensitivity parameters
        vol.Optional("wind_sensitivity_factor"): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        vol.Optional("rain_heat_loss_multiplier"): vol.All(
            vol.Coerce(float), vol.Range(min=1.0, max=2.0)
        ),
        # ECL110 dynamics and displace limits. The coordinator has handled the
        # two limit keys since the mirrors were added, but the schema never
        # admitted them, so the handling was unreachable from the service.
        vol.Optional("ecl110_pid_time_constant_hours"): _positive(24),
        vol.Optional("ecl110_displace_min"): vol.All(
            vol.Coerce(float), vol.Range(min=-30, max=0)
        ),
        vol.Optional("ecl110_displace_max"): vol.All(
            vol.Coerce(float), vol.Range(min=0, max=30)
        ),
    }
)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate a config entry created by an older version of the integration.

    Every option the integration reads is looked up with a default, so older
    entries only need their version stamped forward. Without this handler Home
    Assistant refuses to load entries created before the current
    ``ConfigFlow.VERSION`` and the integration appears broken after an upgrade.
    """
    if entry.version > CONFIG_ENTRY_VERSION:
        # Downgrade: the entry was written by a newer release than this one.
        _LOGGER.error(
            "Config entry version %s is newer than the supported version %s; "
            "downgrade is not supported",
            entry.version,
            CONFIG_ENTRY_VERSION,
        )
        return False

    if entry.version < CONFIG_ENTRY_VERSION:
        _LOGGER.info(
            "Migrating Heat Pump Optimizer config entry from version %s to %s",
            entry.version,
            CONFIG_ENTRY_VERSION,
        )
        hass.config_entries.async_update_entry(entry, version=CONFIG_ENTRY_VERSION)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Heat Pump Optimizer from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = HeatPumpOptimizerCoordinator(hass, entry)
    try:
        integration = await async_get_integration(hass, DOMAIN)
        coordinator.integration_version = str(integration.version)
    except Exception:  # noqa: BLE001 - version is cosmetic, never block setup
        _LOGGER.debug("Could not resolve integration version", exc_info=True)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Serve and register the Lovelace dashboard card (idempotent; runs once).
    await async_register_frontend(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORM_LIST)

    # Register services
    async def handle_run_optimization(call: ServiceCall) -> None:
        """Handle the run_optimization service call."""
        _LOGGER.info("Manual optimization triggered via service call")
        for entry_id, coord in hass.data[DOMAIN].items():
            if isinstance(coord, HeatPumpOptimizerCoordinator):
                await coord.async_run_optimization()

    async def handle_set_mode(call: ServiceCall) -> None:
        """Handle the set_mode service call."""
        mode = call.data["mode"]
        _LOGGER.info("Setting optimizer mode to: %s", mode)
        for entry_id, coord in hass.data[DOMAIN].items():
            if isinstance(coord, HeatPumpOptimizerCoordinator):
                await coord.async_set_mode(mode)

    async def handle_set_thermal_params(call: ServiceCall) -> None:
        """Handle the set_thermal_parameters service call."""
        params = dict(call.data)

        # Same deadband rule apply_schedule enforces, checked against the
        # *effective* pair per coordinator before anything is written — the
        # schema cannot express a cross-field rule, and a minimum at or above
        # the setpoint is the one configuration the solver silently cannot
        # satisfy.
        wanted_min = params.get("dhw_min_temperature")
        wanted_set = params.get("dhw_setpoint")
        if wanted_min is not None or wanted_set is not None:
            for coord in hass.data[DOMAIN].values():
                if not isinstance(coord, HeatPumpOptimizerCoordinator):
                    continue
                setpoint = (
                    wanted_set
                    if wanted_set is not None
                    else coord._thermal_params.dhw_setpoint
                )
                minimum = (
                    wanted_min
                    if wanted_min is not None
                    else coord._thermal_params.dhw_min_temp
                )
                ceiling = float(setpoint) - DHW_MIN_TEMP_SETPOINT_MARGIN
                if float(minimum) > ceiling:
                    raise ServiceValidationError(
                        f"A hot water minimum of {float(minimum):g} °C leaves "
                        f"no deadband below the {float(setpoint):g} °C "
                        f"setpoint; it must be at most {ceiling:g} °C"
                    )

        _LOGGER.info("Updating thermal parameters: %s", params)
        for entry_id, coord in hass.data[DOMAIN].items():
            if isinstance(coord, HeatPumpOptimizerCoordinator):
                await coord.async_update_thermal_params(params)

    async def handle_simulate_plan(call: ServiceCall) -> dict[str, Any]:
        """Price a hypothetical comfort choice without disturbing operation.

        Backs the dashboard card's what-if simulator. Returns a response rather
        than firing an event so the card can await the answer directly, and the
        coordinator rate-limits the underlying solve so that dragging a slider
        cannot trigger one solve per pixel.
        """
        # ``None`` means "not supplied"; an empty string is a real value that
        # simulates removing the hot water demand windows entirely.
        overrides = {k: v for k, v in call.data.items() if v is not None}
        results: dict[str, Any] = {}
        for entry_id, coord in hass.data[DOMAIN].items():
            if isinstance(coord, HeatPumpOptimizerCoordinator):
                results[entry_id] = await coord.async_simulate(overrides)
        return {"results": results}

    async def handle_assign_entity(call: ServiceCall) -> dict[str, Any]:
        """Assign or clear one optional sensor from the setup diagram.

        Item 32's click-to-assign. It writes the same options the config flow
        writes, through the same reload, so an assignment made on the card and
        one made in the options pages are indistinguishable afterwards.

        Two checks the schema cannot make. The entity must exist -- a config
        flow's picker can only offer real entities, and this service is
        callable directly, so without this a typo would be stored and the
        model would plan against a sensor that never reports. And its domain
        must be one the slot accepts: assigning a switch to a temperature slot
        is the mistake a clickable diagram makes easy, and it produces a model
        quietly planning against nonsense rather than an error.
        """
        key = call.data["key"]
        raw = str(call.data["entity_id"]).strip()
        target_entry = call.data.get("entry_id")

        if raw:
            if hass.states.get(raw) is None:
                raise ServiceValidationError(
                    f"Entity {raw} does not exist"
                )
            domains = topology.ASSIGNABLE_KEYS[key]
            domain = raw.split(".", 1)[0]
            if domain not in domains:
                raise ServiceValidationError(
                    f"{raw} is a {domain} entity; {key} accepts "
                    f"{', '.join(domains)}"
                )

        targets = [
            entry
            for entry in hass.config_entries.async_entries(DOMAIN)
            if (target_entry is None or entry.entry_id == target_entry)
            and entry.entry_id in hass.data.get(DOMAIN, {})
        ]
        if not targets:
            raise ServiceValidationError(
                "No loaded Heat Pump Optimizer config entry matched this call"
            )

        # ``None`` rather than "" for a cleared slot: that is what the options
        # flow stores, and what every reader treats as absent.
        value = raw or None
        for entry in targets:
            options = {**dict(entry.options), key: value}
            hass.config_entries.async_update_entry(entry, options=options)

        _LOGGER.info(
            "Assigned %s = %s on %d entry(ies)", key, value, len(targets)
        )
        return {"key": key, "entity_id": value}

    async def handle_apply_schedule(call: ServiceCall) -> dict[str, Any]:
        """Persist a schedule the user built in the what-if simulator.

        The simulator deliberately runs against a copy of the configuration, so
        nothing it does survives. This is the deliberate second step: it writes
        the same fields into the config entry's options, where they become the
        schedule the optimizer actually plans against.

        Writing options triggers ``async_update_options``, which reloads the
        entry — so the next plan is computed from the new schedule without the
        user restarting anything.
        """
        data = dict(call.data)
        target_entry = data.pop("entry_id", None)

        updates: dict[str, Any] = {}
        for key in (
            CONF_DAY_START_HOUR,
            CONF_DAY_END_HOUR,
            CONF_COMFORT_TEMP_DAY,
            CONF_DHW_MIN_TEMP,
        ):
            if data.get(key) is not None:
                updates[key] = data[key]

        # Validate and normalise the windows before storing them. A malformed
        # spec written to options would fail on every subsequent load, turning
        # a mistyped time into a broken integration; parsing here converts that
        # into a rejected service call instead. Round-tripping through the
        # parser also canonicalises the format, so what is stored is what the
        # optimizer will read back.
        if data.get(CONF_DHW_WINDOWS) is not None:
            raw = data[CONF_DHW_WINDOWS]
            try:
                updates[CONF_DHW_WINDOWS] = format_windows(parse_windows(raw))
            except DHWWindowError as err:
                raise ServiceValidationError(
                    f"Invalid hot water windows {raw!r}: {err}"
                ) from err

        if not updates:
            return {"updated": {}, "reason": "nothing to apply"}

        targets = [
            entry
            for entry in hass.config_entries.async_entries(DOMAIN)
            if (target_entry is None or entry.entry_id == target_entry)
            and entry.entry_id in hass.data.get(DOMAIN, {})
        ]
        if not targets:
            raise ServiceValidationError(
                "No loaded Heat Pump Optimizer config entry matched this call"
            )

        # A day window that never opens would leave the house on the night
        # temperature around the clock, silently — get_comfort_temp only
        # returns the day value for start <= hour < end. The call may update
        # one bound and collide with the other bound already stored, so the
        # check runs per entry against the *effective* pair, not just the
        # call's own values.
        if CONF_DAY_START_HOUR in updates or CONF_DAY_END_HOUR in updates:
            for entry in targets:
                stored = {**entry.data, **entry.options}
                start = updates.get(
                    CONF_DAY_START_HOUR,
                    stored.get(CONF_DAY_START_HOUR, DEFAULT_DAY_START_HOUR),
                )
                end = updates.get(
                    CONF_DAY_END_HOUR,
                    stored.get(CONF_DAY_END_HOUR, DEFAULT_DAY_END_HOUR),
                )
                if int(start) >= int(end):
                    raise ServiceValidationError(
                        f"The heating day would start at {int(start)}:00 and "
                        f"end at {int(end)}:00, leaving no comfort period "
                        "at all"
                    )

        # The hot water minimum has to clear a deadband below the setpoint, and
        # the setpoint is per entry, so this cannot live in the schema. Check
        # every target before writing to any of them: a call that fails halfway
        # would leave two heat pumps on different schedules with no indication
        # of which ones took.
        #
        # The solver treats the tank limits as *soft* penalties, so an
        # impossible minimum is not rejected downstream -- the plan would simply
        # sit in permanent slight violation, which is close to undiagnosable
        # from the outside. Hence a hard failure here.
        if CONF_DHW_MIN_TEMP in updates:
            wanted = float(updates[CONF_DHW_MIN_TEMP])
            for entry in targets:
                setpoint = float(
                    entry.options.get(
                        CONF_DHW_SETPOINT,
                        entry.data.get(CONF_DHW_SETPOINT, DEFAULT_DHW_SETPOINT),
                    )
                )
                ceiling = setpoint - DHW_MIN_TEMP_SETPOINT_MARGIN
                if wanted > ceiling:
                    raise ServiceValidationError(
                        f"A hot water minimum of {wanted:g} °C leaves no "
                        f"deadband below the {setpoint:g} °C setpoint; it must "
                        f"be at most {ceiling:g} °C"
                    )

        updated: dict[str, Any] = {}
        for entry in targets:
            options = {**dict(entry.options), **updates}
            hass.config_entries.async_update_entry(entry, options=options)
            updated[entry.entry_id] = dict(updates)

        _LOGGER.info("Applied schedule to %d entry(ies): %s", len(updated), updates)
        return {"updated": updated}

    def _manual_targets(target_entry: str | None):
        """Loaded coordinators the manual-plan services should act on."""
        for entry in hass.config_entries.async_entries(DOMAIN):
            if target_entry is not None and entry.entry_id != target_entry:
                continue
            coord = hass.data.get(DOMAIN, {}).get(entry.entry_id)
            if coord is not None:
                yield entry.entry_id, coord

    async def handle_apply_manual_plan(call: ServiceCall) -> dict[str, Any]:
        """Pin *when* space heating and hot water run for the rest of the day.

        Unlike apply_schedule, which only shifts the envelope the optimizer
        keeps re-deciding inside, this fixes the actual run slots until
        ``expires_at`` (20 hours from now by default). The pins are validated
        in full *before* any coordinator is touched, so a rejected call leaves an
        existing override completely untouched. Safety still wins: the optimizer
        releases a forced-off slot if the house or tank would breach a hard
        floor — see the coordinator and optimizer for how.
        """
        data = dict(call.data)
        target_entry = data.pop("entry_id", None)
        now = dt_util.now()

        raw_expires = data.get("expires_at")
        if raw_expires is None:
            # Measured from this moment, not from the end of the day. A midnight
            # expiry shrank as the day wore on -- an override applied at 22:00
            # lasted two hours -- and the card's edit ceiling had to track it,
            # or slots showed as pinned past the point `channel_pins` frees them.
            expires_at = now + timedelta(hours=MANUAL_PLAN_WINDOW_HOURS)
        else:
            expires_at = dt_util.parse_datetime(raw_expires)
            if expires_at is None:
                raise ServiceValidationError(
                    f"Invalid expires_at {raw_expires!r}: not an ISO 8601 datetime"
                )

        # Validate once, up front. build_override raises for a past expiry, an
        # unparseable slot, an end at or before its start, or overlapping slots.
        try:
            override = build_override(
                dhw_slots=data.get("dhw_slots"),
                space_slots=data.get("space_slots"),
                expires_at=expires_at,
                now=now,
            )
        except ManualPlanError as err:
            raise ServiceValidationError(str(err)) from err

        applied: dict[str, Any] = {}
        first = True
        for entry_id, coord in _manual_targets(target_entry):
            # Reuse the already-validated override for the first (usually only)
            # entry; give any further entries their own copy so the transient
            # safety-release annotations of one never bleed into another.
            this_override = override if first else build_override(
                dhw_slots=data.get("dhw_slots"),
                space_slots=data.get("space_slots"),
                expires_at=expires_at,
                now=now,
            )
            first = False
            applied[entry_id] = await coord.async_apply_manual_plan(this_override)

        if not applied:
            raise ServiceValidationError(
                "No loaded Heat Pump Optimizer config entry matched this call"
            )

        _LOGGER.info("Applied manual plan to %d entry(ies)", len(applied))
        return {"applied": applied}

    async def handle_clear_manual_plan(call: ServiceCall) -> dict[str, Any]:
        """Remove any manual override so planning reverts to fully automatic."""
        target_entry = dict(call.data).get("entry_id")
        cleared: list[str] = []
        for entry_id, coord in _manual_targets(target_entry):
            await coord.async_clear_manual_plan()
            cleared.append(entry_id)
        return {"cleared": cleared}

    hass.services.async_register(
        DOMAIN,
        SERVICE_RUN_OPTIMIZATION,
        handle_run_optimization,
        schema=SERVICE_SCHEMA_RUN_OPTIMIZATION,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_MODE,
        handle_set_mode,
        schema=SERVICE_SCHEMA_SET_MODE,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_THERMAL_PARAMS,
        handle_set_thermal_params,
        schema=SERVICE_SCHEMA_SET_THERMAL_PARAMS,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SIMULATE_PLAN,
        handle_simulate_plan,
        schema=SERVICE_SCHEMA_SIMULATE_PLAN,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_APPLY_SCHEDULE,
        handle_apply_schedule,
        schema=SERVICE_SCHEMA_APPLY_SCHEDULE,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_ASSIGN_ENTITY,
        handle_assign_entity,
        schema=SERVICE_SCHEMA_ASSIGN_ENTITY,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_APPLY_MANUAL_PLAN,
        handle_apply_manual_plan,
        schema=SERVICE_SCHEMA_APPLY_MANUAL_PLAN,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CLEAR_MANUAL_PLAN,
        handle_clear_manual_plan,
        schema=SERVICE_SCHEMA_CLEAR_MANUAL_PLAN,
        supports_response=SupportsResponse.OPTIONAL,
    )

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORM_LIST)

    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

    # Remove services if no more entries. One list, so registration and
    # removal cannot drift apart again — apply_schedule was registered but
    # never removed, leaving a dead service behind after the last entry.
    if not hass.data[DOMAIN]:
        for service in (
            SERVICE_RUN_OPTIMIZATION,
            SERVICE_SET_MODE,
            SERVICE_SET_THERMAL_PARAMS,
            SERVICE_SIMULATE_PLAN,
            SERVICE_APPLY_SCHEDULE,
            SERVICE_ASSIGN_ENTITY,
            SERVICE_APPLY_MANUAL_PLAN,
            SERVICE_CLEAR_MANUAL_PLAN,
        ):
            hass.services.async_remove(DOMAIN, service)

    return unload_ok

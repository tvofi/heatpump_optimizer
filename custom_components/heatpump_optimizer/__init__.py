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

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
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
    DEFAULT_DHW_SETPOINT,
    DHW_MIN_TEMP_SETPOINT_MARGIN,
    CONF_TOPOLOGY_LAYOUT,
    CONF_TOPOLOGY_POSITIONS,
    SERVICE_APPLY_SCHEDULE,
    SERVICE_APPLY_TOPOLOGY,
    SERVICE_ASSIGN_ENTITY,
    SERVICE_APPLY_MANUAL_PLAN,
    SERVICE_CLEAR_MANUAL_PLAN,
    SERVICE_DIAGNOSE_INTERVAL,
    SERVICE_RESTORE_SNAPSHOT,
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
    topology_layout_valid,
)
from . import comfort_band
from . import mixing_valve
from .coordinator import HeatPumpOptimizerConfigEntry, HeatPumpOptimizerCoordinator
from .thermal_model import ThermalParameters
from .dhw_schedule import (
    DHWWindowError,
    format_weekly_windows,
    format_windows,
    parse_weekly_windows,
    parse_windows,
)
from .frontend import async_register_frontend
from . import topology
from .manual_plan import ManualPlanError, build_override

_LOGGER = logging.getLogger(__name__)

# Configured through the UI only (``config_flow: true``): YAML under this
# domain is refused with a repair issue rather than silently ignored.
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORM_LIST = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.SWITCH,
]
# Diagnostics is deliberately NOT here. Home Assistant has no
# ``Platform.DIAGNOSTICS``: the diagnostics component discovers
# ``diagnostics.py`` by name when the user asks for a download, and this list
# is only for platforms that set entities up. Naming it here raised
# ``AttributeError: type object 'Platform' has no attribute 'DIAGNOSTICS'``
# at import time, which failed the whole integration's setup (v6.3.1-v6.3.2).


# hass.data key of the one object that legitimately outlives an entry's
# runtime data: the last published plan, carried across ONE reload. Written
# by ``async_unload_entry`` -- after which Home Assistant discards the entry's
# ``runtime_data`` -- and popped by the ``async_setup_entry`` that follows.
# Never persisted. Everything else an entry needs while it is loaded lives on
# ``entry.runtime_data`` (runtime-data, Bronze).
_PLAN_HANDOVER_KEY = f"{DOMAIN}_plan_handover"


def _plan_handovers(hass: HomeAssistant) -> dict[str, Any]:
    """The reload handovers by entry id, created on first use."""
    return hass.data.setdefault(_PLAN_HANDOVER_KEY, {})

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

# Store the layout the card's editor snapped to (v3.16.0). The schema only
# admits selectable catalog keys — an unmodelled layout (slab_shunt) is
# impossible by construction, not by handler vigilance. Positions are
# cosmetic box coordinates, {place: [x, y]}; free-form edges are never
# accepted anywhere, which is the whole design.
SERVICE_SCHEMA_APPLY_TOPOLOGY = vol.Schema(
    {
        vol.Required("layout"): vol.In(
            sorted(k for k, v in topology.LAYOUTS.items() if v.selectable)
        ),
        vol.Optional("positions"): vol.Schema(
            {
                vol.In(sorted(topology.PLACE_LABELS)): vol.All(
                    [vol.Coerce(float)], vol.Length(min=2, max=2)
                ),
            }
        ),
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

# Same shape, own name: reusing the clear-manual-plan constant for the
# snapshot restore read as if the two services were related.
SERVICE_SCHEMA_RESTORE_SNAPSHOT = vol.Schema(
    {
        vol.Optional("entry_id"): cv.string,
    }
)

SERVICE_SCHEMA_DIAGNOSE_INTERVAL = vol.Schema(
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


# Unique-id suffixes of entities removed by later releases, per platform.
# v5.0.0: the "Solar Radiation (Optimizer)" sensor was merged into "Solar
# Irradiance" — both published the same coordinator value, and the irradiance
# sensor is the one the dashboard card, the docs and the tests point at.
RETIRED_ENTITIES: tuple[tuple[str, str], ...] = (
    ("sensor", "solar_radiation"),
)


def _async_remove_retired_entities(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Drop registry entries for entities this release no longer creates.

    Without this the retired unique_ids linger as permanently-unavailable
    "restored" entities on the device. The survivor of a merge keeps its own
    unique_id, entity_id and recorded history untouched; only the retired
    duplicate's registry entry is removed.
    """
    registry = er.async_get(hass)
    retired = {
        (domain, f"{entry.entry_id}_{suffix}") for domain, suffix in RETIRED_ENTITIES
    }
    for reg_entry in list(er.async_entries_for_config_entry(registry, entry.entry_id)):
        if (reg_entry.domain, reg_entry.unique_id) in retired:
            _LOGGER.info(
                "Removing retired entity %s (unique_id %s)",
                reg_entry.entity_id,
                reg_entry.unique_id,
            )
            registry.async_remove(reg_entry.entity_id)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Register the domain's services, once, before any entry (action-setup).

    Home Assistant calls this when the integration loads, whether or not a
    config entry exists yet, so the eleven services are known -- and an
    automation naming one validates -- while every entry is unloaded. The
    handlers resolve the entry or entries they act on when a call arrives
    (``_loaded_entries``) and refuse a call that finds none loaded. Nothing
    is registered per entry and nothing is removed at unload: the services
    belong to the domain for the life of the process.
    """
    _async_register_services(hass)
    return True


def _loaded_entries(
    hass: HomeAssistant, target_entry: str | None = None
) -> list[HeatPumpOptimizerConfigEntry]:
    """The entries a service call acts on, resolved when the call arrives.

    With an ``entry_id``: that entry, which must exist under this domain and
    be loaded. Without one: every loaded entry, and at least one -- the
    services exist even when no entry does, so an empty answer is refused
    rather than acted on silently. ``LOADED`` is the state Home Assistant
    gives an entry once ``async_setup_entry`` has returned True and takes
    away again at unload, so ``runtime_data`` is there on every entry this
    returns.
    """
    if target_entry is not None:
        entry = hass.config_entries.async_get_entry(target_entry)
        if entry is None or entry.domain != DOMAIN:
            raise ServiceValidationError(
                f"No Heat Pump Optimizer config entry has the id "
                f"{target_entry!r}",
                translation_domain=DOMAIN,
                translation_key="config_entry_not_found",
                translation_placeholders={"entry_id": str(target_entry)},
            )
        if entry.state is not ConfigEntryState.LOADED:
            raise ServiceValidationError(
                f"Heat Pump Optimizer config entry {target_entry!r} "
                f"is not loaded",
                translation_domain=DOMAIN,
                translation_key="config_entry_not_loaded",
                translation_placeholders={"entry_id": str(target_entry)},
            )
        return [entry]
    loaded = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.state is ConfigEntryState.LOADED
    ]
    if not loaded:
        raise ServiceValidationError(
            "No loaded Heat Pump Optimizer config entry matched this call",
            translation_domain=DOMAIN,
            translation_key="no_loaded_config_entry",
        )
    return loaded


def _loaded_coordinators(
    hass: HomeAssistant, target_entry: str | None = None
) -> list[tuple[str, HeatPumpOptimizerCoordinator]]:
    """``_loaded_entries`` as (entry id, coordinator) pairs."""
    return [
        (entry.entry_id, entry.runtime_data)
        for entry in _loaded_entries(hass, target_entry)
    ]


async def async_setup_entry(
    hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry
) -> bool:
    """Set up Heat Pump Optimizer from a config entry."""
    # Clean up entities retired by this release before the platforms register
    # their current rosters. Idempotent and cheap, so it runs on every setup
    # rather than only inside a config-entry version bump — registry state is
    # not versioned by the config entry.
    _async_remove_retired_entities(hass, entry)

    coordinator = HeatPumpOptimizerCoordinator(hass, entry)
    try:
        integration = await async_get_integration(hass, DOMAIN)
        coordinator.integration_version = str(integration.version)
    except Exception:  # noqa: BLE001 - version is cosmetic, never block setup
        _LOGGER.debug("Could not resolve integration version", exc_info=True)

    # If this setup is the second half of an in-process reload, the unload
    # handler stashed the previous plan. Always pop — a stale payload must
    # never outlive the one reload it was made for — and hand it to the
    # coordinator so the first refresh can republish it instantly.
    handover = _plan_handovers(hass).pop(entry.entry_id, None)
    if handover is not None:
        coordinator._reload_handover = handover

    # The first refresh must not run the full MPC solve: it executes inside
    # ``async_setup_entry``, and on modest hardware the sensor reads, the
    # network fetches and a Python-heavy cold solve add up to minutes during
    # which the whole instance is unresponsive (the solve holds the GIL even
    # from the executor thread). The flag is set here and ONLY here; the
    # coordinator consumes it on the next refresh, so every later cycle —
    # and every existing test path — solves exactly as before.
    coordinator._skip_solve_once = True
    await coordinator.async_config_entry_first_refresh()

    # The coordinator is the entry's runtime data (runtime-data, Bronze):
    # every platform reads it from here, the options listener compares a
    # save against the config it was built from, and Home Assistant drops it
    # with the entry at unload. Assigned once the first refresh has
    # succeeded, so a ``ConfigEntryNotReady`` leaves nothing half-built behind.
    entry.runtime_data = coordinator

    # Serve and register the Lovelace dashboard card (idempotent; runs once).
    await async_register_frontend(hass, coordinator.integration_version)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORM_LIST)

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    # The real first solve, deferred out of setup (see the skip-solve flag
    # above). Platforms are set up by now, so entities exist and publish the
    # light payload — the handover plan after a reload, live sensor readings
    # on a fresh start — while the cold solve runs here in the background and
    # replaces it within the first update cycle.
    if hasattr(entry, "async_create_background_task"):
        entry.async_create_background_task(
            hass,
            coordinator.async_request_refresh(),
            name="heatpump_optimizer_first_solve",
        )
    else:
        task = hass.async_create_task(coordinator.async_request_refresh())
        if task is not None and hasattr(task, "cancel"):
            entry.async_on_unload(task.cancel)

    return True


def _async_register_services(hass: HomeAssistant) -> None:
    """The service handlers, registered by ``async_setup``.

    They close over ``hass`` and nothing else: which entries a call acts on
    is decided when the call arrives, from the entries Home Assistant holds
    and their state, never from anything captured at setup.
    """

    async def handle_run_optimization(call: ServiceCall) -> None:
        """Handle the run_optimization service call."""
        _LOGGER.info("Manual optimization triggered via service call")
        for _entry_id, coord in _loaded_coordinators(hass):
            await coord.async_run_optimization()

    async def handle_set_mode(call: ServiceCall) -> None:
        """Handle the set_mode service call."""
        mode = call.data["mode"]
        _LOGGER.info("Setting optimizer mode to: %s", mode)
        for _entry_id, coord in _loaded_coordinators(hass):
            await coord.async_set_mode(mode)

    async def handle_set_thermal_params(call: ServiceCall) -> None:
        """Handle the set_thermal_parameters service call."""
        params = dict(call.data)
        targets = _loaded_coordinators(hass)

        # Same deadband rule apply_schedule enforces, checked against the
        # *effective* pair per coordinator before anything is written — the
        # schema cannot express a cross-field rule, and a minimum at or above
        # the setpoint is the one configuration the solver silently cannot
        # satisfy.
        wanted_min = params.get("dhw_min_temperature")
        wanted_set = params.get("dhw_setpoint")
        if wanted_min is not None or wanted_set is not None:
            for _entry_id, coord in targets:
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
                        f"A hot water minimum of {float(minimum):g} °C "
                        f"leaves no deadband below the {float(setpoint):g} °C "
                        f"setpoint; it must be at most {ceiling:g} °C",
                        translation_domain=DOMAIN,
                        translation_key="set_thermal_params_dhw_min_no_deadband",
                        translation_placeholders={
                            "minimum": f"{float(minimum):g}",
                            "setpoint": f"{float(setpoint):g}",
                            "ceiling": f"{ceiling:g}",
                        },
                    )

        _LOGGER.info("Updating thermal parameters: %s", params)
        for _entry_id, coord in targets:
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
        for entry_id, coord in _loaded_coordinators(hass):
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
                    f"Entity {raw} does not exist",
                    translation_domain=DOMAIN,
                    translation_key="assign_entity_missing",
                    translation_placeholders={"entity_id": raw},
                )
            domains = topology.ASSIGNABLE_KEYS[key]
            domain = raw.split(".", 1)[0]
            if domain not in domains:
                raise ServiceValidationError(
                    f"{raw} is a {domain} entity; {key} accepts "
                    f"{', '.join(domains)}",
                    translation_domain=DOMAIN,
                    translation_key="assign_entity_wrong_domain",
                    translation_placeholders={
                        "entity_id": raw,
                        "domain": domain,
                        "key": key,
                        "domains": ", ".join(domains),
                    },
                )

        targets = _loaded_entries(hass, target_entry)

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

    async def handle_apply_topology(call: ServiceCall) -> dict[str, Any]:
        """Store the layout the card's editor snapped to (v3.16.0).

        Mirrors assign_entity's discipline: server-side validation, an
        options write, the ordinary reload. The schema already restricts
        the key to selectable catalog entries; what it cannot know is
        whether THIS configuration can honor it — a two-tank layout needs
        a wood probe, a valved layout needs a valve — so that is checked
        per entry here, and the rejection names the requirement so the
        editor can show it verbatim.
        """
        key = call.data["layout"]
        positions = call.data.get("positions")
        target_entry = call.data.get("entry_id")

        targets = _loaded_entries(hass, target_entry)

        for entry in targets:
            merged = {**entry.data, **entry.options}
            p = ThermalParameters.from_config(merged)
            if not topology_layout_valid(
                key,
                two_zone=p.two_zone_enabled,
                throttling=mixing_valve.is_throttling(p.mixing_valve_mode),
                wood_probe=p.wood_tank_configured,
            ):
                raise ServiceValidationError(
                    f"This system cannot use the "
                    f"'{topology.LAYOUTS[key].label}' layout: it needs "
                    f"{topology.LAYOUTS[key].requirement}",
                    translation_domain=DOMAIN,
                    translation_key="apply_topology_unsupported",
                    translation_placeholders={
                        "layout": topology.LAYOUTS[key].label,
                        "requirement": topology.LAYOUTS[key].requirement,
                    },
                )

        for entry in targets:
            options = {**dict(entry.options), CONF_TOPOLOGY_LAYOUT: key}
            if positions is not None:
                options[CONF_TOPOLOGY_POSITIONS] = {
                    place: [float(x), float(y)]
                    for place, (x, y) in positions.items()
                }
            hass.config_entries.async_update_entry(entry, options=options)

        _LOGGER.info(
            "Topology layout %s stored on %d entry(ies)", key, len(targets)
        )
        return {"layout": key}

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
                # Weekly specs (#3) normalise through their own round trip;
                # the flat formatter would silently drop the day selectors
                # and turn "weekdays 06-07, weekend 08-09" into "06-07,
                # 08-09" every day -- a behaviour change wearing a
                # canonicalisation costume.
                weekly = parse_weekly_windows(raw)
                updates[CONF_DHW_WINDOWS] = (
                    format_weekly_windows(weekly)
                    if weekly is not None
                    else format_windows(parse_windows(raw))
                )
            except DHWWindowError as err:
                raise ServiceValidationError(
                    f"Invalid hot water windows {raw!r}: {err}",
                    translation_domain=DOMAIN,
                    translation_key="apply_schedule_invalid_dhw_windows",
                    translation_placeholders={
                        "windows": str(raw),
                        "error": str(err),
                    },
                ) from err

        if not updates:
            return {"updated": {}, "reason": "nothing to apply"}

        targets = _loaded_entries(hass, target_entry)

        # The comfort band's cross-field rules, the same ones the config flow
        # runs. This service writes `comfort_temp_day` and the day window
        # straight into the entry options, and the only thing standing between
        # a call and stored configuration was the schema's 5-30 range: a
        # daytime temperature below the stored night one, or a day window that
        # never opens, went in unremarked and left the plan in a contradiction
        # nothing downstream reports.
        #
        # Only violations this call INTRODUCES may refuse it. Judging the
        # merged result outright would make the service fail on a
        # contradiction already sitting in the entry's options and untouched
        # by the call -- and one is genuinely out there, because until v5.1.7
        # the thermostat slider ran to `max_temp + 1` and wrote it unchecked,
        # so a single tap on its top notch stored `target 24` against a
        # `max 23` ceiling. A nightly `dhw_windows` automation would then have
        # started throwing at 03:00 about a ceiling it never mentioned. The
        # stored contradiction is real and worth telling the user about, but
        # a repair issue is where that belongs (`_audit_comfort_band` in the
        # coordinator), not an unrelated service call's exception.
        #
        # The call may still update one half of a pair and collide with the
        # stored other half, so both sides are evaluated against the
        # *effective* values, not the call's own.
        for entry in targets:
            stored = {**entry.data, **entry.options}
            already = {
                (v.field, v.code) for v in comfort_band.violations({}, stored)
            }
            introduced = [
                v
                for v in comfort_band.violations(updates, stored)
                if (v.field, v.code) not in already
            ]
            if introduced:
                raise ServiceValidationError(
                    comfort_band.describe(introduced),
                    translation_domain=DOMAIN,
                    translation_key="apply_schedule_comfort_band_violation",
                    translation_placeholders={
                        "violations": comfort_band.describe(introduced)
                    },
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
                        f"deadband below the {setpoint:g} °C setpoint; it "
                        f"must be at most {ceiling:g} °C",
                        translation_domain=DOMAIN,
                        translation_key="apply_schedule_dhw_min_no_deadband",
                        translation_placeholders={
                            "minimum": f"{wanted:g}",
                            "setpoint": f"{setpoint:g}",
                            "ceiling": f"{ceiling:g}",
                        },
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
        return _loaded_coordinators(hass, target_entry)

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
                    f"Invalid expires_at {raw_expires!r}: "
                    f"not an ISO 8601 datetime",
                    translation_domain=DOMAIN,
                    translation_key="manual_plan_invalid_expires_at",
                    translation_placeholders={"expires_at": str(raw_expires)},
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
            raise ServiceValidationError(
                str(err),
                translation_domain=DOMAIN,
                translation_key="manual_plan_invalid_slots",
                translation_placeholders={"error": str(err)},
            ) from err

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

    async def handle_restore_snapshot(call: ServiceCall) -> dict[str, Any]:
        """Roll the learners back to the newest trustworthy snapshot (#42)."""
        target_entry = dict(call.data).get("entry_id")
        restored: list[str] = []
        for entry_id, coord in _manual_targets(target_entry):
            if await coord.async_restore_learned_snapshot():
                restored.append(entry_id)
        return {"restored": restored}

    async def handle_diagnose_interval(call: ServiceCall) -> dict[str, Any]:
        """Attribute the last settled interval's residual (T6 #52)."""
        target_entry = dict(call.data).get("entry_id")
        reports: dict[str, Any] = {}
        for entry_id, coord in _manual_targets(target_entry):
            reports[entry_id] = await hass.async_add_executor_job(
                coord.diagnose_last_interval
            )
            await coord.async_request_refresh()
        return {"diagnosis": reports}

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
        SERVICE_APPLY_TOPOLOGY,
        handle_apply_topology,
        schema=SERVICE_SCHEMA_APPLY_TOPOLOGY,
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
    hass.services.async_register(
        DOMAIN,
        SERVICE_RESTORE_SNAPSHOT,
        handle_restore_snapshot,
        schema=SERVICE_SCHEMA_RESTORE_SNAPSHOT,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_DIAGNOSE_INTERVAL,
        handle_diagnose_interval,
        schema=SERVICE_SCHEMA_DIAGNOSE_INTERVAL,
        supports_response=SupportsResponse.OPTIONAL,
    )


async def async_update_options(
    hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry
) -> None:
    """Handle options update.

    Reload only when the save actually changed something. The options flow
    persists every page it leaves — ``_save`` merges the page's fields into
    the options dict — so backing out of an untouched form still fires this
    listener. Reloading on those no-op saves tore the whole integration down
    for nothing, which is exactly the freeze the skip-solve flag exists to
    soften; here it is avoided entirely.

    The comparison is against the config the loaded coordinator was built
    from: after a reload the new coordinator carries the new config, so the
    same save repeated is a no-op again. With no coordinator on the entry
    there is nothing to compare against, and the reload goes ahead.
    """
    new_config = {**entry.data, **entry.options}
    coordinator = getattr(entry, "runtime_data", None)
    if coordinator is not None and coordinator.effective_config == new_config:
        _LOGGER.debug(
            "Options saved without changes for %s; skipping reload",
            entry.entry_id,
        )
        return
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry
) -> bool:
    """Unload a config entry.

    The services are the domain's, not this entry's (``async_setup``), so
    nothing is removed here; a call arriving while no entry is loaded is
    refused by the handler itself.
    """
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORM_LIST)

    if unload_ok:
        coordinator = entry.runtime_data
        # Keep the last published payload for the setup that follows a
        # reload: it republishes the previous plan instantly instead of
        # holding Home Assistant hostage to a cold solve. In-process only —
        # never written to disk — and setup always pops it. It cannot ride
        # on the entry: Home Assistant deletes ``runtime_data`` right after
        # this returns.
        if coordinator.data is not None:
            _plan_handovers(hass)[entry.entry_id] = coordinator.data
        await coordinator.async_shutdown()

    return unload_ok

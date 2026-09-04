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

import importlib
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.loader import async_get_integration

from .const import DOMAIN, CONFIG_ENTRY_VERSION

if TYPE_CHECKING:
    from .coordinator import HeatPumpOptimizerConfigEntry

# Importing this package must not execute the coordinator's module graph.
# ``coordinator`` and ``services`` reach 40 of the integration's modules
# between them, and a plain ``from .coordinator import ...`` here put every
# one of them inside the MEASURED closure of anything that imports the
# package -- including ``tests/stress.py``, whose only production entry
# points are the solver and the models under it. That made a change to the
# coordinator, the frontend or the narrative select a forty-minute stress
# run the change could not affect. Home Assistant reaches everything below
# through ``async_setup``/``async_setup_entry``, which run long after import.
_LAZY_ATTRS = {
    "HeatPumpOptimizerConfigEntry": "coordinator",
    "HeatPumpOptimizerCoordinator": "coordinator",
    # The four service schemas the test suite pokes through the package root
    # (the facade rule): they are defined in -- and re-exported from --
    # services.py, along with everything else the eleven services are made of.
    "SERVICE_SCHEMA_APPLY_MANUAL_PLAN": "services",
    "SERVICE_SCHEMA_APPLY_SCHEDULE": "services",
    "SERVICE_SCHEMA_CLEAR_MANUAL_PLAN": "services",
    "SERVICE_SCHEMA_SIMULATE_PLAN": "services",
}


def _lazy(module: str):
    """A sibling module, imported on first use. See ``_LAZY_ATTRS``."""
    return importlib.import_module(f".{module}", __package__)


def __getattr__(name: str) -> Any:
    """Resolve a re-export from the package root (PEP 562)."""
    module = _LAZY_ATTRS.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(_lazy(module), name)
    globals()[name] = value
    return value


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


async def async_setup_entry(
    hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry
) -> bool:
    """Set up Heat Pump Optimizer from a config entry."""
    # Clean up entities retired by this release before the platforms register
    # their current rosters. Idempotent and cheap, so it runs on every setup
    # rather than only inside a config-entry version bump — registry state is
    # not versioned by the config entry.
    _async_remove_retired_entities(hass, entry)

    coordinator = _lazy("coordinator").HeatPumpOptimizerCoordinator(hass, entry)
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
    await _lazy("frontend").async_register_frontend(
        hass, coordinator.integration_version
    )

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
    """Register the domain's services (the handlers live in ``services``).

    Thin seam since #222: schemas, the twelve handlers and the eleven
    ``hass.services.async_register`` calls are ``services.py``'s; this only
    forwards, so ``async_setup`` keeps one registration path and nothing is
    captured per entry.
    """
    _lazy("services").async_register_services(hass)


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

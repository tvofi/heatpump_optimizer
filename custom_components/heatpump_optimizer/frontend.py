"""Frontend registration for the Heat Pump Optimizer Lovelace card.

This module serves the custom card's JavaScript from a static path and, when
Lovelace is running in storage mode, registers the resource automatically so
users do not have to add it by hand.

Both steps are defensive: the static-path helper prefers the modern
``async_register_static_paths`` API but falls back to the deprecated
synchronous call on older Home Assistant releases, and the resource
registration is wrapped in a broad ``try/except`` because Lovelace internals
are not a stable public API and must never break integration setup.
"""
from __future__ import annotations

import logging
import os

from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Public URL under which the card JS is served.
URL_BASE = "/heatpump_optimizer_static"
CARD_FILENAME = "heatpump-optimizer-card.js"

_FLAG = f"{DOMAIN}_frontend_registered"


def _www_dir() -> str:
    """Return the absolute path to the bundled ``www`` directory."""
    return os.path.join(os.path.dirname(__file__), "www")


def _card_version(hass: HomeAssistant) -> str:
    """Best-effort integration version string for cache-busting."""
    try:
        data = hass.data.get(DOMAIN)
        if isinstance(data, dict):
            for value in data.values():
                version = getattr(value, "integration_version", None)
                if version:
                    return str(version)
    except Exception:  # noqa: BLE001
        pass
    return "0"


async def _register_static_path(hass: HomeAssistant, www_dir: str) -> None:
    """Register the static path, preferring the modern async API."""
    try:
        from homeassistant.components.http import StaticPathConfig

        await hass.http.async_register_static_paths(
            [StaticPathConfig(URL_BASE, www_dir, True)]
        )
        return
    except (ImportError, AttributeError):
        # Older Home Assistant: fall back to the deprecated sync call.
        try:
            hass.http.register_static_path(URL_BASE, www_dir, True)
        except Exception:  # noqa: BLE001
            _LOGGER.warning(
                "Could not register static path %s for the Heat Pump "
                "Optimizer card",
                URL_BASE,
                exc_info=True,
            )
    except Exception:  # noqa: BLE001
        _LOGGER.warning(
            "Unexpected error registering static path %s", URL_BASE, exc_info=True
        )


async def _register_lovelace_resource(hass: HomeAssistant, url: str) -> None:
    """Register the card as a Lovelace module resource in storage mode."""
    try:
        lovelace = hass.data.get("lovelace")
        if lovelace is None:
            _LOGGER.debug("Lovelace not initialised yet; skipping resource")
            return

        # Support both the object-style and dict-style `lovelace` data that
        # different Home Assistant versions expose.
        mode = getattr(lovelace, "mode", None)
        resources = getattr(lovelace, "resources", None)
        if resources is None and isinstance(lovelace, dict):
            mode = lovelace.get("mode", mode)
            resources = lovelace.get("resources")

        if resources is None:
            _LOGGER.info(
                "Lovelace resources unavailable; add %s manually as a "
                "dashboard resource (type: module)",
                url,
            )
            return

        if mode == "yaml":
            _LOGGER.info(
                "Lovelace is in YAML mode. Add the Heat Pump Optimizer card "
                "resource manually:\n"
                "  resources:\n"
                "    - url: %s\n"
                "      type: module",
                url,
            )
            return

        if hasattr(resources, "loaded") and not resources.loaded:
            await resources.async_load()
            resources.loaded = True

        # Skip if a resource with the same base URL already exists. If it does
        # but the cache-busting query differs, update it in place: leaving the
        # stale ?v= means browsers keep serving the previously cached card
        # after an upgrade, which looks exactly like the new version not
        # working.
        base = url.split("?")[0]
        existing = []
        if hasattr(resources, "async_items"):
            existing = resources.async_items() or []
        elif hasattr(resources, "data"):
            existing = resources.data or []
        for item in existing:
            item_url = item.get("url") if isinstance(item, dict) else None
            if not item_url or item_url.split("?")[0] != base:
                continue
            if item_url == url:
                _LOGGER.debug("Card resource already registered: %s", item_url)
                return
            item_id = item.get("id")
            if item_id is None or not hasattr(resources, "async_update_item"):
                _LOGGER.debug(
                    "Card resource %s is stale but cannot be updated", item_url
                )
                return
            await resources.async_update_item(
                item_id, {"res_type": "module", "url": url}
            )
            _LOGGER.info(
                "Updated Heat Pump Optimizer card resource %s -> %s",
                item_url,
                url,
            )
            return

        await resources.async_create_item({"res_type": "module", "url": url})
        _LOGGER.info("Registered Heat Pump Optimizer card resource: %s", url)
    except Exception:  # noqa: BLE001 - never break setup over Lovelace internals
        _LOGGER.warning(
            "Could not auto-register the Heat Pump Optimizer Lovelace "
            "resource; add %s manually (type: module)",
            url,
            exc_info=True,
        )


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Serve and register the Lovelace card. Idempotent across config entries."""
    if hass.data.get(_FLAG):
        return
    hass.data[_FLAG] = True

    www_dir = await hass.async_add_executor_job(_www_dir)
    await _register_static_path(hass, www_dir)

    version = _card_version(hass)
    url = f"{URL_BASE}/{CARD_FILENAME}?v={version}"
    await _register_lovelace_resource(hass, url)

"""The repair-notice writer: the one place a notice is raised or cleared.

A leaf (it imports only ``const``), so a module that raises a notice -- the
store boundary, the legionella guard, the notifier, the pump-duty arbiter --
does not inherit what the set-point consistency check imports to do its own
work (the quiet windows and, through them, the solver).
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN

# Manifest ``documentation`` — the URL every repair notice links to (#558 F2).
DOCUMENTATION_URL = "https://github.com/tvofi/heatpump_optimizer"

_LOGGER = logging.getLogger(__name__)


def create_issue(hass: Any, domain: str, issue_id: str, **kwargs: Any) -> None:
    """Raise a repair notice, defaulting the documentation link (#558 F2)."""
    kwargs.setdefault("learn_more_url", DOCUMENTATION_URL)
    ir.async_create_issue(hass, domain, issue_id, **kwargs)


def set_issue(
    hass: Any,
    issue_id: str,
    raise_it: bool,
    *,
    fixable: bool = False,
    persistent: bool = False,
    placeholders: dict[str, str] | None = None,
    data: dict[str, Any] | None = None,
) -> None:
    """Raise or clear one repair: the writer every pure finding feeds.

    Its ``translation_key`` is its ``issue_id``, its severity a warning;
    called each cycle, since creating an existing issue updates it and
    deleting an absent one does nothing.
    """
    if not raise_it:
        clear_issue(hass, issue_id)
        return
    kwargs: dict[str, Any] = {
        "is_fixable": fixable,
        "severity": ir.IssueSeverity.WARNING,
        "translation_key": issue_id,
        "translation_placeholders": placeholders or {},
    }
    if persistent:
        kwargs["is_persistent"] = True
    if data is not None:
        kwargs["data"] = data
    create_issue(hass, DOMAIN, issue_id, **kwargs)


def clear_issue(hass: Any, issue_id: str) -> None:
    """Clear one repair, best-effort: a failed clear is logged, never raised."""
    try:
        ir.async_delete_issue(hass, DOMAIN, issue_id)
    except Exception as err:  # noqa: BLE001 - clearing is best-effort
        _LOGGER.debug("Could not clear %s: %s", issue_id, err)


def note_price_outage(
    hass: Any, reason: str, cycles: int, exc_info: bool, covering: list[float] | bool
) -> bool:
    """Log one failed price fetch, raise its repair, and say whether planning goes on.

    ``covering``: the last published prices still covering now (falsy when none
    do, or for a refused token). While they do, planning goes on and the failure
    is a warning plus the ``price_feed_stale`` repair; otherwise the update fails
    and it is an error. ``cycles`` counts this one: only an outage's first cycle
    logs above DEBUG (D10-09).
    """
    bridged = bool(covering)
    if cycles > 1:
        _LOGGER.debug("Tibber still failing (%s)", reason)
    elif bridged:
        _LOGGER.warning("%s; planning on the last published prices", reason)
    else:
        _LOGGER.error("%s", reason, exc_info=exc_info)
    if bridged:  # once raised it stays through the failed update; recovery clears it
        set_issue(hass, "price_feed_stale", True, placeholders={"error": reason})
    return bridged

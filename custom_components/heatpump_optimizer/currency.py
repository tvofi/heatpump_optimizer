"""The one place the display currency is decided.

Every monetary unit in the integration used to be the literal string "SEK",
hard-coded per sensor — eight copies of an assumption about where the user
lives. Home Assistant already knows the instance's currency; the fallback
stays SEK because that is what every existing install has always shown, and
a unit that changes under an unconfigured instance would break long-term
statistics for the people the hard-coding happened to fit.
"""
from __future__ import annotations

FALLBACK_CURRENCY = "SEK"


def resolve_currency(hass) -> str:
    """The instance's configured currency, or the historical SEK fallback."""
    return getattr(getattr(hass, "config", None), "currency", None) or (
        FALLBACK_CURRENCY
    )

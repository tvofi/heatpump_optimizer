"""The one place the display currency is decided.

Every monetary unit in the integration used to be the literal string "SEK",
hard-coded per sensor — eight copies of an assumption about where the user
lives. Home Assistant already knows the instance's currency; the fallback
stays SEK because that is what every existing install has always shown, and
a unit that changes under an unconfigured instance would break long-term
statistics for the people the hard-coding happened to fit.

The instance currency is a label, though, and the numbers are denominated
by the price feed (#1657): a EUR feed on a SEK instance published EUR
figures under SEK units. So a published money unit is the feed's own code
where the feed declares one (:func:`declared_currency`), and the instance's
only where it does not: :func:`figure_currency` is that precedence.
"""
from __future__ import annotations

import re
from typing import Any

from homeassistant.core import HomeAssistant

FALLBACK_CURRENCY = "SEK"

#: A symbol that names exactly one currency. "kr" and "$" name several.
_SYMBOL_CODES = {"€": "EUR", "£": "GBP", "zł": "PLN"}

#: Whole units of a currency worth about one SEK, rounded up (#1657,
#: D12-s3-81). A money bound written for SEK-sized numbers — a fee limit, a
#: widget maximum — is multiplied by this so a real HUF, ISK, JPY or KRW
#: figure is enterable. Order of magnitude only: an absent code is 1, which
#: leaves every currency near or above the krona exactly as it was.
_UNITS_PER_SEK = {
    "ARS": 200, "CLP": 100, "COP": 500, "CZK": 5, "HUF": 50,
    "IDR": 2000, "INR": 10, "ISK": 20, "JPY": 20, "KRW": 200,
    "KZT": 100, "NGN": 200, "PHP": 10, "PKR": 50, "RSD": 20,
    "RUB": 10, "THB": 5, "TWD": 5, "UAH": 5, "VND": 5000,
}


def resolve_currency(hass: HomeAssistant) -> str:
    """The instance's configured currency, or the historical SEK fallback."""
    return getattr(getattr(hass, "config", None), "currency", None) or (
        FALLBACK_CURRENCY
    )


def declared_currency(unit: Any, attributes: Any = None) -> str | None:
    """The ISO code a price feed declares for its numbers, or ``None``.

    The money half of ``<money>/<energy>`` when it is an ISO code or an
    unambiguous symbol, else the feed's ``currency`` attribute (a minor unit
    such as öre names no single currency). ``None`` when the feed says
    nothing a code can be read from.
    """
    money = str(unit or "").partition("/")[0].strip()
    code = _SYMBOL_CODES.get(money)
    if code is None and re.fullmatch("[A-Z]{3}", money):  # not "ÖRE"
        code = money
    attr = (attributes or {}).get("currency") if isinstance(attributes, dict) else None
    if code is None and isinstance(attr, str) and re.fullmatch("[A-Za-z]{3}", attr):
        code = attr.upper()
    return code


def feed_currency(hass: Any, feed: str | None) -> str | None:
    """The code the price entity ``feed`` declares from its live state, or ``None``.

    ``None`` too when there is no feed (Tibber) or it is not in ``hass.states``.
    """
    state = hass.states.get(feed) if feed else None
    attrs = getattr(state, "attributes", None) or {}
    return declared_currency(attrs.get("unit_of_measurement"), attrs)


def figure_currency(hass: Any, feed: str | None, adopted: str | None = None) -> str:
    """The currency every money figure is published and entered in (#1657).

    The feed's declared code first, since its numbers denominate every
    figure; else ``adopted``, the code already in use (an unavailable feed
    does not flip the unit); else the instance's (``resolve_currency``).
    The one precedence for the sensors, the options dialog's labels and its
    fee bound (D14-s1-03).
    """
    return feed_currency(hass, feed) or adopted or resolve_currency(hass)


def money_scale(currency: Any) -> int:
    """How many of ``currency``'s whole units a SEK-sized bound spans."""
    return _UNITS_PER_SEK.get(str(currency or "").upper(), 1)

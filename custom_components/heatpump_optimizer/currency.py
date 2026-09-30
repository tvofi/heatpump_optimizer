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
only where it does not.
"""
from __future__ import annotations

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
    "ARS": 200.0, "CLP": 100.0, "COP": 500.0, "CZK": 5.0, "HUF": 50.0,
    "IDR": 2000.0, "INR": 10.0, "ISK": 20.0, "JPY": 20.0, "KRW": 200.0,
    "KZT": 100.0, "NGN": 200.0, "PHP": 10.0, "PKR": 50.0, "RSD": 20.0,
    "RUB": 10.0, "THB": 5.0, "TWD": 5.0, "UAH": 5.0, "VND": 5000.0,
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
    if code is None and len(money) == 3 and money.isalpha() and money.isupper():
        code = money
    attr = (attributes or {}).get("currency") if isinstance(attributes, dict) else None
    if code is None and isinstance(attr, str) and len(attr) == 3 and attr.isalpha():
        code = attr.upper()
    return code


def money_scale(currency: Any) -> float:
    """How many of ``currency``'s whole units a SEK-sized bound spans."""
    return _UNITS_PER_SEK.get(str(currency or "").upper(), 1.0)

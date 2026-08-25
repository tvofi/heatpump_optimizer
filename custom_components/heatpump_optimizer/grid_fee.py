"""Time-of-use grid transfer fees, layered onto the spot price (item #1).

Swedish DSOs increasingly price the grid by time, not only by peak kW:
höglast energy fees (roughly +25 öre/kWh weekday 06–22, November–March at
several DSOs), and per-hour dynamic fees are on the way. The spot price the
integration plans against — Tibber's ``total`` — includes tax and VAT but
**not** the DSO transfer fee, so a fee layer here is additive, never
double-counted.

Rules are configured as comma- or newline-separated lines of the form::

    Nov-Mar Mon-Fri 06:00-22:00 = 0.25
    Jul = 0.10

Each part before the ``=`` is optional and narrows when the rate applies:
a month or month range (wrapping allowed, ``Nov-Mar``), a weekday or weekday
range (``Mon-Fri``), and a time-of-day range in the same ``HH:MM-HH:MM``
grammar as the DHW demand windows (wrapping allowed). A rule with no
qualifiers applies always. **Overlapping rules add**: real tariffs are often
a base transfer fee plus a high-load surcharge, and addition composes those
without asking the user to pre-merge them.

Kept free of Home Assistant imports so it can be unit-tested directly, like
``dhw_schedule`` and ``tariff``. The live-entity mode is therefore expressed
as a value the caller reads from Home Assistant and passes in; this module
only decides what it means.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

from .dhw_schedule import DHWWindowError, Window, hour_in_windows, parse_windows

_LOGGER = logging.getLogger(__name__)

#: ``grid_fee_mode`` values. "none" is the sentinel default: every vector is
#: zeros and an untouched install is byte-for-byte what it was.
MODE_NONE = "none"
MODE_RULES = "rules"
MODE_ENTITY = "entity"
MODES = (MODE_NONE, MODE_RULES, MODE_ENTITY)

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    # Swedish spellings that differ from the English three-letter forms —
    # a Swedish integration that rejected "maj" would be embarrassing.
    "maj": 5, "okt": 10,
}
_DAYS = {
    "mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6,
    # Swedish
    "mån": 0, "man": 0, "tis": 1, "ons": 2, "tor": 3, "fre": 4,
    "lör": 5, "lor": 5, "sön": 6, "son": 6,
}


class GridFeeError(ValueError):
    """Raised when a grid-fee specification cannot be parsed."""


def parse_month_range(token: str) -> frozenset[int]:
    """``"Nov-Mar"`` or ``"Jul"`` as the set of month numbers it covers."""
    token = token.strip().lower()
    if "-" in token:
        start_token, _, end_token = token.partition("-")
        start = _MONTHS.get(start_token.strip())
        end = _MONTHS.get(end_token.strip())
        if start is None or end is None:
            raise GridFeeError(f"Unknown month in '{token}'")
        if start <= end:
            return frozenset(range(start, end + 1))
        # Wrapping: Nov-Mar is Nov, Dec, Jan, Feb, Mar.
        return frozenset(list(range(start, 13)) + list(range(1, end + 1)))
    month = _MONTHS.get(token)
    if month is None:
        raise GridFeeError(f"Unknown month '{token}'")
    return frozenset({month})


def parse_day_range(token: str) -> frozenset[int]:
    """``"Mon-Fri"`` or ``"Sat"`` as the set of ``datetime.weekday()`` values."""
    token = token.strip().lower()
    if "-" in token:
        start_token, _, end_token = token.partition("-")
        start = _DAYS.get(start_token.strip())
        end = _DAYS.get(end_token.strip())
        if start is None or end is None:
            raise GridFeeError(f"Unknown weekday in '{token}'")
        if start <= end:
            return frozenset(range(start, end + 1))
        return frozenset(list(range(start, 7)) + list(range(0, end + 1)))
    day = _DAYS.get(token)
    if day is None:
        raise GridFeeError(f"Unknown weekday '{token}'")
    return frozenset({day})


@dataclass(frozen=True)
class FeeRule:
    """One parsed rule: a rate and the times it applies to."""

    rate: float
    #: None means "any month"; likewise for days and hours.
    months: frozenset[int] | None = None
    days: frozenset[int] | None = None
    hours: tuple[Window, ...] | None = None

    def applies(self, when: datetime) -> bool:
        if self.months is not None and when.month not in self.months:
            return False
        if self.days is not None and when.weekday() not in self.days:
            return False
        if self.hours is not None:
            hour = when.hour + when.minute / 60.0
            if not hour_in_windows(hour, list(self.hours)):
                return False
        return True


def _parse_rule(line: str) -> FeeRule:
    body, sep, rate_token = line.rpartition("=")
    if not sep:
        raise GridFeeError(f"Rule '{line}' has no '= rate' part")
    try:
        rate = float(rate_token.strip().replace(",", "."))
    except ValueError as err:
        raise GridFeeError(f"Bad rate in '{line}'") from err
    if not np.isfinite(rate):
        raise GridFeeError(f"Bad rate in '{line}'")

    months: frozenset[int] | None = None
    days: frozenset[int] | None = None
    hours: tuple[Window, ...] | None = None
    for token in body.split():
        token = token.strip()
        if not token:
            continue
        if ":" in token or token.replace("-", "").isdigit():
            # A time range in the DHW window grammar.
            if hours is not None:
                raise GridFeeError(f"Two time ranges in '{line}'")
            try:
                hours = tuple(parse_windows(token))
            except DHWWindowError as err:
                raise GridFeeError(str(err)) from err
            continue
        head = token.partition("-")[0].strip().lower()
        if head in _MONTHS:
            if months is not None:
                raise GridFeeError(f"Two month ranges in '{line}'")
            months = parse_month_range(token)
        elif head in _DAYS:
            if days is not None:
                raise GridFeeError(f"Two weekday ranges in '{line}'")
            days = parse_day_range(token)
        else:
            raise GridFeeError(f"Unrecognised token '{token}' in '{line}'")
    return FeeRule(rate=rate, months=months, days=days, hours=hours)


def parse_rules(spec: str | None) -> list[FeeRule]:
    """Parse a whole rule specification. Empty input is an empty list."""
    if not spec:
        return []
    raw = str(spec).replace(";", ",").replace("\n", ",")
    rules = []
    for line in raw.split(","):
        line = line.strip()
        if line:
            rules.append(_parse_rule(line))
    return rules


def is_valid_spec(spec: str) -> bool:
    """Whether a rule specification parses, for the config flow to check."""
    try:
        parse_rules(spec)
    except GridFeeError:
        return False
    return True


@dataclass
class GridFeeSchedule:
    """The configured fee layer, evaluated per instant or per step grid."""

    mode: str = MODE_NONE
    #: A flat SEK/kWh component added in every step, in rules and entity mode.
    fixed: float = 0.0
    rules: list[FeeRule] = field(default_factory=list)

    @classmethod
    def from_config(cls, config: dict) -> "GridFeeSchedule":
        """Build from the config entry; a broken spec degrades to no rules.

        Degrading is deliberate: the config flow validates on the way in, so
        a parse failure here means a hand-edited store, and pricing the plan
        with zero fees is better than refusing to plan at all.
        """
        from . import const

        mode = str(config.get(const.CONF_GRID_FEE_MODE, const.DEFAULT_GRID_FEE_MODE))
        if mode not in MODES:
            mode = MODE_NONE
        fixed = 0.0
        rules: list[FeeRule] = []
        if mode != MODE_NONE:
            try:
                fixed = float(
                    config.get(const.CONF_GRID_FEE_FIXED, const.DEFAULT_GRID_FEE_FIXED)
                )
            except (TypeError, ValueError):
                fixed = 0.0
            if not np.isfinite(fixed):
                fixed = 0.0
        if mode == MODE_RULES:
            try:
                rules = parse_rules(config.get(const.CONF_GRID_FEE_RULES, ""))
            except GridFeeError as err:
                _LOGGER.warning(
                    "Invalid grid fee rules (%s); pricing with no ToU fees", err
                )
                rules = []
        return cls(mode=mode, fixed=fixed, rules=rules)

    @property
    def active(self) -> bool:
        """Whether the layer can produce a non-zero fee at all."""
        if self.mode == MODE_RULES:
            return bool(self.rules) or self.fixed != 0.0
        if self.mode == MODE_ENTITY:
            return True
        return False

    def current_fee(self, when: datetime, entity_value: float | None = None) -> float:
        """SEK/kWh fee at one instant."""
        if self.mode == MODE_ENTITY:
            value = entity_value if entity_value is not None else 0.0
            if not np.isfinite(value):
                value = 0.0
            return self.fixed + float(value)
        if self.mode == MODE_RULES:
            return self.fixed + sum(
                rule.rate for rule in self.rules if rule.applies(when)
            )
        return 0.0

    def fee_vector(
        self,
        step_starts: list[datetime],
        entity_value: float | None = None,
    ) -> np.ndarray:
        """SEK/kWh per step of a grid.

        In entity mode the current value is held flat across the horizon:
        an entity reports now, not tomorrow, and holding flat is honest
        about knowing nothing better.
        """
        n = len(step_starts)
        if self.mode == MODE_NONE or n == 0:
            return np.zeros(n, dtype=float)
        if self.mode == MODE_ENTITY:
            return np.full(n, self.current_fee(step_starts[0], entity_value))
        return np.asarray(
            [self.current_fee(when) for when in step_starts], dtype=float
        )

"""The shared entity base for Heat Pump Cost Optimizer (common-modules, Bronze).

Each platform file used to declare its own ``CoordinatorEntity`` base class,
and the five of them re-declared the same two members -- the
``_attr_has_entity_name`` flag and the ``device_info`` property that lands
every entity on the coordinator's device. Those live here once now (issue
#298); each platform's base classes build on ``HeatPumpOptimizerEntity``
instead of re-declaring them. Everything that differs per platform (the
unique-id key, the pinned ``entity_id``, the translation key) stays in the
platform file that owns it. The plain-and-finite publication scrub lives here
too, so it covers all six platforms rather than the sensor platform alone
(#1541).
"""
from __future__ import annotations

import math
from typing import Any, Callable

import numpy as np

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity


def _finite(value: Any) -> Any:
    """Plain, finite Python for everything an entity publishes, recursively.

    ``inf`` and ``nan`` are not JSON. orjson -- the serializer Home Assistant
    uses for the websocket and the recorder -- writes them as ``null``, so the
    frontend and the database already see "unknown" while a Jinja template
    reading the same attribute in-process sees Python's ``inf`` and compares
    ``> 100`` as true. One published number, two different meanings depending
    on who reads it.

    The values are not accidents. ``PeakTracker.threshold_kw`` returns ``inf``
    on purpose, as a sentinel meaning "the capacity term has no reference yet,
    do not let it distort the plan" -- which is a decision variable, and
    ``None`` ("unknown") is what it means once it becomes a published
    attribute. It is +inf on the 1st of every month, for every install with a
    capacity tariff.

    Applied at the publication boundary rather than at the two sites that
    produce it today, because the interesting case is the one nobody
    predicted: the next attribute that divides by a zero sample count is
    covered without anyone remembering to ask. It was a sensor-only scrub
    until #1541 found climate, switch and binary-sensor attributes publishing
    the raw value; the entity base installs it on every platform now.

    The same boundary plains numpy (#173). The optimizer hands the
    coordinator numpy scalars -- the solar-gain trajectory is one
    ``numpy.float64`` per step -- and the coordinator converts the fields
    it remembers to (``predictive_info`` goes through ``_plain_types``) and
    forgets the rest (``schedule`` did not). Converting here, once, covers
    every entity, and the order matters: ``np.float64`` *subclasses*
    ``float``, so it has to be unwrapped before the finite test or it walks
    through that test unchanged.
    """
    if isinstance(value, np.ndarray):
        return _finite(value.tolist())
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: _finite(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_finite(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_finite(item) for item in value)
    return value


class HeatPumpOptimizerEntity(CoordinatorEntity):
    """What every Heat Pump Optimizer entity has in common.

    Display names come from the translation files (``strings.json`` /
    ``translations/*.json``) via ``translation_key``, so the UI follows the
    Home Assistant language while ``unique_id`` — and therefore history and
    statistics — never moves.
    """

    _attr_has_entity_name = True

    #: The properties Home Assistant reads to build a state write, on every
    #: platform this integration has. Every number it publishes leaves through
    #: one of them, which is why the plain-and-finite scrub is installed here
    #: rather than repeated per entity -- and why an entity added next year
    #: gets it without anyone remembering to ask for it.
    _PUBLISHED = (
        "native_value",
        "extra_state_attributes",
        "current_temperature",
        "target_temperature",
    )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Wrap every subclass's published properties in the finite scrub."""
        super().__init_subclass__(**kwargs)
        for name in HeatPumpOptimizerEntity._PUBLISHED:
            prop = cls.__dict__.get(name)
            if not isinstance(prop, property) or prop.fget is None:
                continue
            if getattr(prop.fget, "_finite_scrubbed", False):
                continue

            def scrubbed(
                self: HeatPumpOptimizerEntity,
                _fget: Callable[[Any], Any] = prop.fget,
            ) -> Any:
                return _finite(_fget(self))

            scrubbed.__name__ = name
            scrubbed.__doc__ = prop.fget.__doc__
            setattr(scrubbed, "_finite_scrubbed", True)
            setattr(cls, name, property(scrubbed, prop.fset, prop.fdel))

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        info: DeviceInfo = self.coordinator.device_info
        return info

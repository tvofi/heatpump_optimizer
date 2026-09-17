"""Option values read from a heat pump's own Home Assistant device (#1067).

``modbus_prefill`` reads a GCHV package's register sensors by entity-id
prefix. A pump that is integrated rather than polled over Modbus has no such
prefix: its entities belong to a *device* in Home Assistant's registries, and
the user knows the device by name, not by the slug its entity ids happen to
carry. This module is the other end of :func:`modbus_prefill.snapshot`'s
resolver input -- it turns one device's entity-registry records into the same
``role -> Resolved`` map ``modbus_prefill.candidates`` returns, so
:func:`modbus_prefill.infer` reads a device and a Modbus package identically.

Two rules are the contract, and ``tests/features.py`` pins each:

* **A source table proves its device.** Dispatch is by the integration that
  owns the entities (``platform``). A table applies only when the records
  carry a key set that source's own definitions make unique to the model the
  table was derived from; an integration with no table registered resolves
  nothing. Guessing is W1067-G7b-3's fallback, which is not in this module.
* **Scale travels with the role.** The same setting arrives in different
  units from different sources. The GCHV package's register 404 holds tenths
  of a degree; the Tuya integration's DHW set-point number already reads
  degrees. A scale fixed inside ``infer()`` would turn a 50 degree set-point
  into 5.0, so each :class:`~.modbus_prefill.Resolved` carries its own.

Matching keys on the **unique id**, never on the entity id: a unique id is
the integration's own identifier and survives a rename, while an entity id is
the user's and is slugged from a name that changes. Home Assistant scopes a
unique id per platform *and* domain, so the domain is part of the match --
a device named "Heat Night" gives its ``mode`` select the unique id
``heat_night_mode``, which ends in the ``night_mode`` switch's key.

Kept free of Home Assistant imports, like ``modbus_prefill``:
``config_flow.py`` reads the registries and hands this module plain records.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import NamedTuple

from .const import (
    CONF_DHW_TEMP_ENTITY,
    CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY,
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
    CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY,
    CONF_OUTDOOR_TEMP_ENTITY,
)
from .modbus_prefill import Resolved


class EntityRecord(NamedTuple):
    """One entity-registry entry, as plain values.

    The fields W1067-G7b's resolvers read. The last five are unused by the
    source tables here and carried for the fuzzy fallback (G7b-3), which
    matches on type, unit and name.
    """

    platform: str
    unique_id: str
    entity_id: str
    original_name: str | None = None
    translation_key: str | None = None
    device_class: str | None = None
    unit: str | None = None
    state_class: str | None = None

    @property
    def domain(self) -> str:
        """The entity id's domain -- ``sensor`` for ``sensor.hp_t4``."""
        return self.entity_id.split(".", 1)[0]


#: tvofi/tuya_heat_pump at ``fda9bed``: ``(domain, model key) -> (role, scale)``.
#:
#: The keys are the dict keys of ``models/000004k4z6.py``'s per-platform
#: tables, which every platform turns into ``f"{device_name_slug}_{key}"``
#: (``binary_sensor.py:112``, and the same line in ``sensor.py``,
#: ``switch.py``, ``number.py`` and ``select.py``). The key, not the ``code``
#: field: ``fault_description`` carries ``code: fault``.
#:
#: Each role is paired with the register carrying the same meaning in the
#: generated Modbus package, so the two sources agree on what is being read:
#: T4 is register 1, temp_current_f (the tank, dp 26) is 206, temp_current
#: (dp 10, Midea T1) is 4, Tin (dp 101, TW_in) is 3, and DHWSET (dp 104) is
#: register 404 -- **at scale 1.0, where the register is tenths**.
#:
#: ``Tout`` (dp 106) is the plate outlet, not T1, and is deliberately not
#: mapped. The installer parameters the other registers carry (405, 406,
#: 601, 711-714, 518-519, 4109) are not in the Tuya schema at all, so
#: ``infer()``'s absent rule omits them.
_TUYA_HEAT_PUMP: dict[tuple[str, str], tuple[str, float]] = {
    ("sensor", "T4"): (CONF_OUTDOOR_TEMP_ENTITY, 1.0),
    ("sensor", "temp_current_f"): (CONF_DHW_TEMP_ENTITY, 1.0),
    ("sensor", "temp_current"): (CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY, 1.0),
    ("sensor", "Tin"): (CONF_HEAT_PUMP_RETURN_TEMP_ENTITY, 1.0),
    ("switch", "night_mode"): (CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY, 1.0),
    ("number", "DHWSET"): ("r404", 1.0),
}

#: The pairs above that no other model file in that repo defines at
#: ``fda9bed`` (the grep is in the pull-request body). One of them present
#: proves the device is the model the table was derived from; none present
#: means some other Tuya heat pump, which this table may not read.
#: ``temp_current`` is not here: several model files reuse it.
_TUYA_HEAT_PUMP_SIGNATURE = frozenset(
    {("sensor", "T4"), ("sensor", "Tin"), ("switch", "night_mode"), ("number", "DHWSET")}
)

#: ``platform -> (table, signature)``. W1067-G7b-2 registers ``tuya_local``
#: here; a platform absent from it resolves nothing, which is where G7b-3's
#: fuzzy fallback attaches.
_SOURCES: dict[str, tuple[Mapping[tuple[str, str], tuple[str, float]], frozenset]] = {
    "tuya_heat_pump": (_TUYA_HEAT_PUMP, _TUYA_HEAT_PUMP_SIGNATURE),
}


def _matched_keys(
    records: Iterable[EntityRecord],
    table: Mapping[tuple[str, str], tuple[str, float]],
) -> dict[tuple[str, str], str]:
    """``(domain, key) -> entity_id`` for every record a table key names.

    A record matches when its unique id ends in an underscore and the key,
    within the key's own domain. The longest key wins, so ``temp_current_f``
    is not read as ``temp_current``.
    """
    matched: dict[tuple[str, str], str] = {}
    for record in records:
        unique_id = record.unique_id.lower()
        # Keyed by the TABLE's pair, not the record's domain. Keying by the
        # record's domain would encode the domain a second time and quietly
        # neutralise a wrong match: a select whose unique id ends in the
        # night_mode switch's key would land under ("select", "night_mode"),
        # which no table row asks for, so the domain test below would look
        # load-bearing while proving nothing.
        pairs = [
            (domain, key)
            for (domain, key) in table
            if domain == record.domain and unique_id.endswith(f"_{key.lower()}")
        ]
        if pairs:
            matched[max(pairs, key=lambda pair: len(pair[1]))] = record.entity_id
    return matched


def resolve(records: Iterable[EntityRecord]) -> dict[str, Resolved]:
    """One device's records as ``modbus_prefill``'s resolver input.

    Empty when no registered source recognises the device, which the options
    flow reports rather than opening an empty pre-fill form.
    """
    by_platform: dict[str, list[EntityRecord]] = {}
    for record in records:
        by_platform.setdefault(record.platform, []).append(record)
    resolved: dict[str, Resolved] = {}
    for platform, own in by_platform.items():
        source = _SOURCES.get(platform)
        if source is None:
            continue
        table, signature = source
        matched = _matched_keys(own, table)
        if not signature & matched.keys():
            continue
        for pair, (role, scale) in table.items():
            if pair in matched and role not in resolved:
                resolved[role] = Resolved((matched[pair],), scale)
    return resolved

"""Option values read from a heat pump's own Home Assistant device (#1067).

``modbus_prefill`` reads a GCHV package's register sensors by entity-id
prefix. A pump that is integrated rather than polled over Modbus has no such
prefix: its entities belong to a *device* in Home Assistant's registries, and
the user knows the device by name, not by the slug its entity ids happen to
carry. This module is the other end of :func:`modbus_prefill.snapshot`'s
resolver input -- it turns one device's entity-registry records into the same
``role -> ResolvedRole`` map ``modbus_prefill.candidates`` returns, so
:func:`modbus_prefill.infer` reads a device and a Modbus package identically.

Two rules are the contract, and ``tests/features.py`` pins each:

* **A source table proves its device.** Dispatch is by the integration that
  owns the entities (``platform``). A table applies only when the records
  carry a key set that source's own definitions make unique to the model the
  table was derived from; an integration with no table resolves nothing
  here. ``localtuya`` has no table, and that is a decision rather than an
  omission: its records are a device id, a DP number and the user's own
  names, and nothing in them names firmware. DP numbers are not identity --
  dp 105 is the outdoor probe in the config below and a select's option in
  another of the same corpus, and dp 107 is a tank in one source and a wired
  controller in the other -- so a DP-keyed table would be this repository's
  Tuya meanings worn by a device of unknown firmware. What carries those
  devices is ``name_match``, W1067-G7b-3's fallback, which
  :func:`resolve_with_fallback` applies to the roles
  :func:`resolve` left empty.
* **Scale travels with the role.** The same setting arrives in different
  units from different sources. The GCHV package's register 404 holds tenths
  of a degree; the Tuya integration's DHW set-point number already reads
  degrees. A scale fixed inside ``infer()`` would turn a 50 degree set-point
  into 5.0, so each :class:`~.modbus_prefill.ResolvedRole` carries its own.
  The fallback's roles carry 1.0, because a Home Assistant state that has a
  unit already reads in that unit.

``resolve()`` is the source-table half **alone**, and stays that way: it is
the object the merge base's own answer is compared against, so the fallback
is added beside it rather than inside it.

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

from . import name_match
from .const import (
    CONF_DHW_TEMP_ENTITY,
    CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY,
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
    CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY,
    CONF_OUTDOOR_TEMP_ENTITY,
)
from .modbus_prefill import ResolvedRole


class Resolution(NamedTuple):
    """A device's roles, and which source resolved each one.

    ``roles`` is what ``modbus_prefill.snapshot`` reads. ``source`` is the
    page's account of itself, one label per role: a source table's own
    platform, or ``name_match.SOURCE`` where nothing but a name matched. It is
    the plan's "Resolved plus the source name, carried for the disclaimer",
    and it rides here rather than on ``ResolvedRole`` for one reason -- the
    role map is the object the null control compares byte for byte against the
    merge base, and a field added to it would be a difference in every
    fixture. A label nothing displays costs a lookup; a field costs that.
    """

    roles: dict[str, ResolvedRole]
    source: dict[str, str]


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
_TUYA_HEAT_PUMP_SIGNATURE = (
    frozenset({
        ("sensor", "T4"),
        ("sensor", "Tin"),
        ("switch", "night_mode"),
        ("number", "DHWSET"),
    }),
)

#: make-all/tuya-local at ``2026.9.1`` (commit ``4551357``): ``(domain,
#: config id) -> (role, scale)``.
#:
#: There the unique id is the device uid, a hyphen, then the *config id*
#: (``helpers/device_config.py:293-295``), and a config id is the entity type
#: plus the slugified entity name -- ``sensor_outdoor_temperature``
#: (``:323-338``). The two rows are the only roles a *sensor* entity there can
#: prove, in ``devices/fisher_water_heatpump.yaml``: dp 105 is the sensor
#: "Outdoor temperature" and dp 101 the sensor "Inlet temperature" (the plate
#: heat exchanger inlet, register 3's TW_in). Its dp 106 sensor "Outlet
#: temperature" is the plate outlet -- Tout, not the T1 supply -- and is
#: deliberately not mapped. dp 10 and dp 26 are attributes of the config's
#: ``climate`` entity and dp 104 and dp 107 of its ``water_heater``, so no
#: entity slot can take them.
_TUYA_LOCAL: dict[tuple[str, str], tuple[str, float]] = {
    ("sensor", "sensor_outdoor_temperature"): (CONF_OUTDOOR_TEMP_ENTITY, 1.0),
    ("sensor", "sensor_inlet_temperature"): (CONF_HEAT_PUMP_RETURN_TEMP_ENTITY, 1.0),
}

#: Those two keys together are unique to that config among tuya-local's 1746
#: device configs at ``4551357`` (the counts are in the pull-request body):
#: "Outdoor temperature" appears in 13 configs and "Outlet temperature" in 22,
#: and together in that one only. So the proof is the pair, and it is the pair
#: whether or not this table maps it: the sensor the table reads (dp 105) and
#: the one it deliberately does not (dp 106, Tout). The config's third named
#: sensor, "Inlet temperature", is in neither group -- shared with other
#: configs, it proves nothing. Brand is not identity here either: the
#: corpus's other Rotenso config is an air conditioner whose dp 105 and dp 101
#: are a select and a pm25 sensor.
_TUYA_LOCAL_SIGNATURE = (
    frozenset({("sensor", "sensor_outdoor_temperature")}),
    frozenset({("sensor", "sensor_outlet_temperature")}),
)

#: ``platform -> (table, signature, separator)``. A *signature* is a tuple of
#: key groups, and the table applies only when every group has at least one
#: matched key -- which lets a source say what its own definitions prove. The
#: Tuya model above is one group of four keys it alone defines, so any one of
#: them suffices; tuya-local's is the two-key pair above, because neither key
#: alone is unique in that corpus. The separator is how each source joins its
#: own key to the device: tuya-local hyphenates a device uid and a config id,
#: the Tuya integration underscores a device slug and a model key. A platform
#: absent from here resolves nothing, which is where G7b-3's fuzzy fallback
#: attaches.
_SOURCES: dict[
    str,
    tuple[
        Mapping[tuple[str, str], tuple[str, float]],
        tuple[frozenset[tuple[str, str]], ...],
        str,
    ],
] = {
    "tuya_heat_pump": (_TUYA_HEAT_PUMP, _TUYA_HEAT_PUMP_SIGNATURE, "_"),
    "tuya_local": (_TUYA_LOCAL, _TUYA_LOCAL_SIGNATURE, "-"),
}


def _matched_keys(
    records: Iterable[EntityRecord],
    keys: Iterable[tuple[str, str]],
    separator: str,
) -> dict[tuple[str, str], str]:
    """``(domain, key) -> entity_id`` for every record one of ``keys`` names.

    A record matches when its unique id ends in the source's own separator and
    the key, within the key's own domain. The longest key wins, so
    ``temp_current_f`` is not read as ``temp_current``.
    """
    matched: dict[tuple[str, str], str] = {}
    for record in records:
        unique_id = record.unique_id.lower()
        # Keyed by the asked-for pair, not the record's domain. Keying by the
        # record's domain would encode the domain a second time and quietly
        # neutralise a wrong match: a select whose unique id ends in the
        # night_mode switch's key would land under ("select", "night_mode"),
        # which no source asks for, so the domain test below would look
        # load-bearing while proving nothing.
        pairs = [
            (domain, key)
            for (domain, key) in keys
            if domain == record.domain
            and unique_id.endswith(f"{separator}{key.lower()}")
        ]
        if pairs:
            matched[max(pairs, key=lambda pair: len(pair[1]))] = record.entity_id
    return matched


def resolve(records: Iterable[EntityRecord]) -> dict[str, ResolvedRole]:
    """One device's records as ``modbus_prefill``'s resolver input.

    Empty when no registered source recognises the device, which the options
    flow reports rather than opening an empty pre-fill form. This is the
    source-table half alone and its answer never changes: the fallback is
    *added* to it by :func:`resolve_with_fallback`, so a device an earlier
    group resolved resolves identically here.
    """
    by_platform: dict[str, list[EntityRecord]] = {}
    for record in records:
        by_platform.setdefault(record.platform, []).append(record)
    resolved: dict[str, ResolvedRole] = {}
    for platform, own in by_platform.items():
        source = _SOURCES.get(platform)
        if source is None:
            continue
        table, signature, separator = source
        # The signature's keys are looked for as well: a proof key need not be
        # a role this table maps -- tuya-local's proof is the sensor it
        # deliberately does not map.
        matched = _matched_keys(
            own,
            set(table) | {pair for group in signature for pair in group},
            separator,
        )
        if not all(group & matched.keys() for group in signature):
            continue
        for pair, (role, scale) in table.items():
            if pair in matched and role not in resolved:
                resolved[role] = ResolvedRole((matched[pair],), scale)
    return resolved


def _table_sources(
    records: Iterable[EntityRecord], roles: Mapping[str, ResolvedRole]
) -> dict[str, str]:
    """``role -> the platform whose table resolved it``.

    Read off the registered tables rather than carried through ``resolve()``,
    so that function's own answer stays exactly what it was. Platforms are
    sorted, because a device whose records span two tabled integrations is
    resolved deterministically rather than by set order.
    """
    present = sorted({record.platform for record in records if record.platform in _SOURCES})
    return {
        role: platform
        for platform in present
        for _pair, (role, _scale) in _SOURCES[platform][0].items()
        if role in roles
    }


def resolve_with_fallback(records: Iterable[EntityRecord]) -> Resolution:
    """The dispatcher the pre-fill page reads a device through.

    A source table when one is registered for the platform, and then -- for
    the roles that left empty -- W1067-G7b-3's fallback, which matches on the
    entity's type, unit and name and says so on the page. A role the table
    decided is never reopened, and a device no table proves is read by name
    alone, which is what carries a locally-configured or unbranded pump.
    """
    pool = list(records)
    roles = resolve(pool)
    source = _table_sources(pool, roles)
    for match in name_match.matches(pool, taken=roles):
        roles[match.role] = ResolvedRole((match.entity_id,))
        source[match.role] = name_match.SOURCE
    return Resolution(roles, source)


def disclaimer(resolution: Resolution | None = None) -> dict[str, str]:
    """The page's own account of where the suggestions came from.

    Two description placeholders: the roles a *name* filled, each as
    ``role -> entity``, and the sources whose tables filled the rest. An
    em dash where there is nothing to say, the page's existing spelling of
    "nothing read" (``modbus_prefill.notes``). The sentence around them, which
    is what asks the user to check before saving, lives in ``strings.json``.
    """
    roles = {} if resolution is None else resolution.roles
    source = {} if resolution is None else resolution.source
    matched = sorted(
        (role, resolved.entity_ids[0])
        for role, resolved in roles.items()
        if source.get(role) == name_match.SOURCE
    )
    tables = sorted({label for label in source.values() if label != name_match.SOURCE})
    return {
        "name_matched": (
            "; ".join(f"{role} -> {entity_id}" for role, entity_id in matched) or "–"
        ),
        "matched_sources": ", ".join(tables) or "–",
    }

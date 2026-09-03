"""One description of the configured system, shared by every picture of it.

Items 32 and 33. The config flow's setup overview and the card's setup page
both draw the same system — house, zones, tanks, valves, furnace, and every
sensor at its physical place. Two renderers with two ideas of the topology
would diverge the first time a sensor is added, so the description is built
here, once, and both consume it.

Everything is derived from configuration the integration already has — the
backlog is explicit that this needs no new options. The derived facts
(two-zone, DHW, valve mode, whether the tank is a store) come from
``ThermalParameters.from_config`` itself, so a picture can never disagree
with what the model actually believes.

**A slot that is empty is shown empty.** A diagram that silently omits an
unconfigured sensor looks complete, and "looks complete" is worse than no
diagram — the whole point is to reveal what is missing.

Kept free of Home Assistant imports so it can be unit-tested directly, like
`manual_plan`, `mixing_valve` and `external_heat`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import mixing_valve
from .const import (
    CONF_TOPOLOGY_POSITIONS,
    TOPOLOGY_NO_VALVE,
    TOPOLOGY_SINGLE_TANK_VALVE,
    TOPOLOGY_SLAB_SHUNT,
    TOPOLOGY_TWO_TANK_4WAY,
    TOPOLOGY_VALVE_UPPER_DIRECT_SLAB,
    topology_layout_valid,
    CONF_BUFFER_TANK_TEMP_ENTITY,
    CONF_DHW_TEMP_ENTITY,
    CONF_DHW_WOOD_COIL_ENABLED,
    CONF_ENERGY_ENTITY,
    CONF_EXTERNAL_HEAT_ENABLED,
    CONF_EXTERNAL_HEAT_ENTITY,
    CONF_FLOOR_RETURN_TEMP_ENTITY,
    CONF_HEAT_PUMP_DEFROST_ENTITY,
    CONF_HEAT_PUMP_FAULT_ENTITY,
    CONF_HEAT_PUMP_MODE_ENTITY,
    CONF_HEAT_PUMP_ONLINE_ENTITY,
    CONF_HEAT_PUMP_SWITCH_ENTITY,
    CONF_HOUSE_POWER_ENTITY,
    CONF_INDOOR_TEMP_ENTITY,
    CONF_LOWER_FLOOR_TEMP_ENTITY,
    CONF_MIXING_VALVE_TARGET_ENTITY,
    CONF_OUTDOOR_TEMP_ENTITY,
    CONF_POWER_ENTITY,
    CONF_PV_PRODUCTION_ENTITY,
    CONF_SOLAR_RADIATION_ENTITY,
    CONF_VALVE_OUTLET_TEMP_ENTITY,
    CONF_WOOD_TANK_BOTTOM_ENTITY,
    CONF_WOOD_TANK_TOP_ENTITY,
    CONF_WOOD_TANK_VOLUME,
    DEFAULT_WOOD_TANK_VOLUME,
)
from .thermal_model import ThermalParameters

# Every sensor slot the diagram can show: (config key, place, label).
# Places are stable ids both renderers key their drawing off; adding a place
# here without teaching the renderers about it is harmless — unknown places
# land in the "elsewhere" group rather than vanishing.
# The domains each slot accepts, so the card's picker and the assign service
# agree about what may go where. Assigning a switch to a temperature slot is
# the mistake a clickable diagram makes easy, and the one that produces a
# model quietly planning against nonsense rather than an error.
_TEMP = ("sensor", "number", "input_number")
# What the pump reports about itself. A flag may plausibly arrive as a
# binary_sensor, as a switch (some integrations expose writable DPs that way),
# as an input_boolean mirroring one, or as a plain sensor carrying the raw
# code — so all four are accepted and `inputs.parse_bool` reconciles them.
_FLAG = ("binary_sensor", "switch", "input_boolean", "sensor")
_MODE = ("select", "sensor", "input_select")

# What a slot is asking for, where the answer is narrower than the domains it
# accepts. ``sensor`` covers every reading a house produces, so on an install
# with hundreds of them the card's picker ranks a matching device class to the
# top of the list: the probe the slot is for is near the top before a single
# character is typed. RANKING ONLY -- nothing is hidden by it, because plenty
# of working sensors carry no device class at all, and a picker that hid those
# would hide the very probe the user came to assign.
#
# It lives here, in the same row as the domains, rather than in a second table
# inside the card: two descriptions of one slot are two things to keep in step,
# and the card's copy was reachable by no test at all.
_TEMPERATURE = "temperature"
_POWER = "power"
_ENERGY = "energy"
_IRRADIANCE = "irradiance"
_SLOTS: tuple[tuple[str, str, str, tuple[str, ...], str | None], ...] = (
    (CONF_OUTDOOR_TEMP_ENTITY, "outdoor", "Outdoor temperature", _TEMP,
     _TEMPERATURE),
    (CONF_SOLAR_RADIATION_ENTITY, "outdoor", "Solar radiation", _TEMP,
     _IRRADIANCE),
    (CONF_PV_PRODUCTION_ENTITY, "outdoor", "PV production", _TEMP, _POWER),
    (CONF_INDOOR_TEMP_ENTITY, "upper_zone", "Indoor temperature", _TEMP,
     _TEMPERATURE),
    (CONF_LOWER_FLOOR_TEMP_ENTITY, "lower_zone", "Lower floor temperature",
     _TEMP, _TEMPERATURE),
    (CONF_FLOOR_RETURN_TEMP_ENTITY, "floor_loop", "Floor loop return", _TEMP,
     _TEMPERATURE),
    (CONF_HEAT_PUMP_SWITCH_ENTITY, "heat_pump", "Heat pump switch",
     ("switch", "input_boolean", "climate"), None),
    (CONF_POWER_ENTITY, "heat_pump", "Power meter", _TEMP, _POWER),
    (CONF_ENERGY_ENTITY, "heat_pump", "Energy meter", _TEMP, _ENERGY),
    (CONF_HOUSE_POWER_ENTITY, "heat_pump", "Whole-house power", _TEMP, _POWER),
    # v5.3.0: what the pump says about itself. All optional, all read-only,
    # all at the heat pump because that is the device they describe. None of
    # them has a device class worth ranking on: a mode is a select, and the
    # three flags arrive as whichever of four domains the integration chose.
    (CONF_HEAT_PUMP_MODE_ENTITY, "heat_pump", "Operating mode", _MODE, None),
    (CONF_HEAT_PUMP_DEFROST_ENTITY, "heat_pump", "Defrosting", _FLAG, None),
    (CONF_HEAT_PUMP_ONLINE_ENTITY, "heat_pump", "Online status", _FLAG, None),
    (CONF_HEAT_PUMP_FAULT_ENTITY, "heat_pump", "Fault alarm", _FLAG, None),
    (CONF_BUFFER_TANK_TEMP_ENTITY, "buffer_tank", "Buffer tank temperature",
     _TEMP, _TEMPERATURE),
    (CONF_MIXING_VALVE_TARGET_ENTITY, "mixing_valve", "Valve target", _TEMP,
     _TEMPERATURE),
    (CONF_DHW_TEMP_ENTITY, "dhw_tank", "Hot water temperature", _TEMP,
     _TEMPERATURE),
    # A stove sensor is a thermometer on some installs and a contact on
    # others, which is why it accepts four domains; ranking one of them would
    # push the other three down for no reason.
    (CONF_EXTERNAL_HEAT_ENTITY, "wood_tank", "Stove or flue sensor",
     ("sensor", "binary_sensor", "switch", "input_boolean"), None),
    (CONF_WOOD_TANK_TOP_ENTITY, "wood_tank", "Wood tank top", _TEMP,
     _TEMPERATURE),
    (CONF_WOOD_TANK_BOTTOM_ENTITY, "wood_tank", "Wood tank bottom", _TEMP,
     _TEMPERATURE),
    # "wood_valve" is a slot id, not a drawn place: the wood-side blending
    # valve was a box of its own until v4.0.0, when the user's #40 feedback
    # (item 3) had it removed — it modelled nothing, could not be deleted,
    # and drew a device nobody owns. ``describe_setup`` re-homes this slot
    # onto the 4-way valve in the two-tank layout and onto the wood tank
    # everywhere else.
    (CONF_VALVE_OUTLET_TEMP_ENTITY, "wood_valve", "Valve outlet temperature",
     _TEMP, _TEMPERATURE),
)

#: Every config key a diagram may assign, and the domains it accepts. The one
#: source for the card's picker and the ``assign_entity`` service, so what the
#: diagram offers and what the service accepts cannot drift apart.
ASSIGNABLE_KEYS: dict[str, tuple[str, ...]] = {
    key: domains for key, _place, _label, domains, _class in _SLOTS
}

# ---------------------------------------------------------------------------
# The layout catalog (v3.16.0, issue #40)
# ---------------------------------------------------------------------------
#
# The root-cause fix for "the diagram lies about the physics": one catalog
# of named hydronic layouts that the editor validates against, the drawing
# derives its edges FROM, and the model dispatches on
# (`ThermalParameters.topology_layout`). Free-form graphs are never stored:
# the editor snaps a drawn edge set to a catalog key or rejects it with an
# explanation naming the nearest supported layout.


@dataclass(frozen=True)
class Layout:
    """One supported (or known-but-unmodelled) hydronic arrangement."""

    key: str
    label: str
    description: str
    #: What the configuration must have for this key to be storable — the
    #: prose half of `const.topology_layout_valid`, shown when a selection
    #: is rejected.
    requirement: str
    #: False = drawable in explanations, selectable never, because no model
    #: variant exists — promising physics nobody wrote is the exact failure
    #: this catalog ends.
    selectable: bool = True


LAYOUTS: dict[str, Layout] = {
    layout.key: layout
    for layout in (
        Layout(
            TOPOLOGY_NO_VALVE,
            "No mixing valve",
            "Everything the pump makes reaches the emitters; the tank is a "
            "pass-through with a standing loss.",
            "no throttling mixing valve configured",
        ),
        Layout(
            TOPOLOGY_SINGLE_TANK_VALVE,
            "One tank behind a valve",
            "The valve regulates one shared flow to every circuit; wood "
            "heat, if any, is folded into the heat-pump tank.",
            "a throttling mixing valve",
        ),
        Layout(
            TOPOLOGY_TWO_TANK_4WAY,
            "Two tanks, one 4-way valve",
            "A wood tank beside the heat-pump tank; the valve draws "
            "wood-first while usable and feeds both floors in parallel.",
            "a throttling valve, two zones and a wood-tank top probe",
        ),
        Layout(
            TOPOLOGY_VALVE_UPPER_DIRECT_SLAB,
            "Valve on the radiators, slab fed direct",
            "Only the radiator circuit sits behind the valve; the slab "
            "drinks raw tank water.",
            "a throttling valve, two zones, and no wood-tank probe (no "
            "model exists for two tanks with a direct-fed slab)",
        ),
        Layout(
            TOPOLOGY_SLAB_SHUNT,
            "Separate slab shunt",
            "A second shunt on the slab circuit. Recorded as a known "
            "layout; not selectable until physics exists for it.",
            "not selectable: no model variant exists yet",
            selectable=False,
        ),
    )
}

#: Human names for the places edges connect. The ``assign_place`` service
#: validator accepts exactly these keys (the layout editor's rejection
#: explanations live in the card, in its own mirrored copy).
PLACE_LABELS: dict[str, str] = {
    "heat_pump": "Heat pump",
    "buffer_tank": "Buffer tank",
    "mixing_valve": "Mixing valve",
    "upper_zone": "Upper floor",
    "lower_zone": "Lower floor",
    "wood_tank": "Wood tank",
    "dhw_tank": "Hot water tank",
    "slab_shunt": "Slab shunt",
}


def layout_edges(
    key: str,
    *,
    two_zone: bool,
    wood: bool,
    dhw_coil: bool = False,
    dhw: bool = False,
) -> list[tuple[str, str]]:
    """The drawn edge set of a layout under this configuration's flags.

    Place-name pairs, source to sink. The flags matter because the same
    layout draws differently on different houses — a one-zone house has no
    lower-floor edge, a house without a furnace has no wood chain — and
    both the drawing and the editor's matching must agree on the composed
    set, so it is composed here, once.
    """
    edges: list[tuple[str, str]] = [("heat_pump", "buffer_tank")]
    # The single-tank wood chain: the furnace tank's heat folded into the HP
    # tank. Drawn tank-to-tank since v4.0.0 — the wood-side blending valve
    # used to be a box of its own, which modelled nothing, could not be
    # removed, and drew a device nobody owns (#40 feedback, item 3). Only
    # two_tank_4way replaces this chain.
    wood_chain = [("wood_tank", "buffer_tank")]
    if key == TOPOLOGY_NO_VALVE:
        edges.append(("buffer_tank", "upper_zone"))
        if two_zone:
            edges.append(("buffer_tank", "lower_zone"))
        if wood:
            edges.extend(wood_chain)
    elif key == TOPOLOGY_SINGLE_TANK_VALVE:
        edges.extend(
            [("buffer_tank", "mixing_valve"), ("mixing_valve", "upper_zone")]
        )
        if two_zone:
            edges.append(("mixing_valve", "lower_zone"))
        if wood:
            edges.extend(wood_chain)
    elif key == TOPOLOGY_TWO_TANK_4WAY:
        edges.extend(
            [
                ("buffer_tank", "mixing_valve"),
                ("wood_tank", "mixing_valve"),
                ("mixing_valve", "upper_zone"),
                ("mixing_valve", "lower_zone"),
            ]
        )
        if dhw_coil:
            edges.append(("wood_tank", "dhw_tank"))
    elif key == TOPOLOGY_VALVE_UPPER_DIRECT_SLAB:
        edges.extend(
            [
                ("buffer_tank", "mixing_valve"),
                ("mixing_valve", "upper_zone"),
                ("buffer_tank", "lower_zone"),
            ]
        )
        if wood:
            edges.extend(wood_chain)
    elif key == TOPOLOGY_SLAB_SHUNT:
        edges.extend(
            [
                ("buffer_tank", "mixing_valve"),
                ("mixing_valve", "upper_zone"),
                ("buffer_tank", "slab_shunt"),
                ("slab_shunt", "lower_zone"),
            ]
        )
    else:
        raise KeyError(f"unknown layout {key!r}")
    # Electric hot water rides every layout: the heat pump heats the DHW tank
    # whenever hot water is modelled at all. The diagram used to omit this
    # pipe entirely, leaving the tank floating unconnected (#40 feedback,
    # item 2) — with a coil, the only pipe shown was the wood one, which
    # implied the tank had no electric heat source at all.
    if dhw:
        edges.append(("heat_pump", "dhw_tank"))
    return edges


def describe_setup(config: dict[str, Any]) -> dict[str, Any]:
    """The configured system as one structured description.

    Pure over the config dict. The ``slots`` list includes empty slots for
    every place the configured topology has, each entry
    ``{key, label, place, entity}`` with ``entity`` ``None`` when nothing is
    assigned.
    """
    p = ThermalParameters.from_config(config)
    valve = mixing_valve.is_throttling(p.mixing_valve_mode)
    # Whether the wood tank is simulated as its own store, or folded into the
    # heat-pump tank. Read from the model, never re-derived here, so a picture
    # cannot claim physics the model does not run (issue #40).
    two_tank = p.two_tank_modelled
    wood = bool(
        config.get(CONF_EXTERNAL_HEAT_ENABLED)
        or config.get(CONF_WOOD_TANK_TOP_ENTITY)
        or config.get(CONF_WOOD_TANK_BOTTOM_ENTITY)
        or config.get(CONF_VALVE_OUTLET_TEMP_ENTITY)
        or config.get(CONF_EXTERNAL_HEAT_ENTITY)
    )
    present = {
        "outdoor": True,
        "upper_zone": True,
        "heat_pump": True,
        "buffer_tank": True,
        "lower_zone": p.two_zone_enabled,
        "floor_loop": p.two_zone_enabled,
        "dhw_tank": p.dhw_enabled,
        "mixing_valve": valve,
        "wood_tank": wood,
    }
    def placed(place: str) -> str:
        """Where this slot actually lives on the configured topology.

        The "wood valve" stopped being a drawn place in v4.0.0 (#40 feedback,
        item 3): in the two-tank layout the 4-way valve is the one physical
        device the outlet probe sits on, and in the single-tank abstraction
        the probe belongs with the wood tank whose blended output it
        measures — a separate box modelled nothing and could not be removed.
        """
        if place == "wood_valve":
            return "mixing_valve" if two_tank else "wood_tank"
        return place

    slots = [
        {
            "key": key,
            "label": label,
            "place": placed(place),
            "entity": config.get(key) or None,
            # Carried so the card's picker offers only what the service will
            # accept for this slot -- one list, not two that can disagree.
            "domains": list(domains),
            # ...and what the slot is actually asking for within those
            # domains, which the picker ranks by. None where the slot has no
            # narrower answer than its domains already give.
            "device_class": device_class,
        }
        for key, place, label, domains, device_class in _SLOTS
        if present.get(placed(place), True)
    ]
    # The active layout's drawn edges, composed from the catalog — the card
    # draws these rather than hardcoding pipes, so drawing and physics can
    # no longer diverge (v3.16.0). The editor matches edited edge sets
    # against `catalog`, whose entries carry each layout's edges under THIS
    # configuration's flags, plus whether the configuration could store it.
    active_edges = layout_edges(
        p.topology_layout,
        two_zone=p.two_zone_enabled,
        wood=wood,
        dhw_coil=p.dhw_coil_active,
        dhw=p.dhw_enabled,
    )
    catalog = [
        {
            "key": layout.key,
            "label": layout.label,
            "description": layout.description,
            # The prose half of the validity predicate. The card renders it
            # when a drawing matches a layout the configuration cannot store;
            # omitting it was the "needs: undefined" bug (#40 feedback,
            # item 5) — the one message meant to say exactly what is missing
            # said nothing at all.
            "requirement": layout.requirement,
            "selectable": layout.selectable,
            "valid": layout.selectable
            and topology_layout_valid(
                layout.key,
                two_zone=p.two_zone_enabled,
                throttling=valve,
                wood_probe=p.wood_tank_configured,
            ),
            "edges": [list(e) for e in layout_edges(
                layout.key,
                two_zone=p.two_zone_enabled,
                wood=wood,
                dhw_coil=p.dhw_coil_active,
                dhw=p.dhw_enabled,
            )],
        }
        for layout in LAYOUTS.values()
    ]
    positions = config.get(CONF_TOPOLOGY_POSITIONS) or {}
    return {
        "two_zone": p.two_zone_enabled,
        "dhw": p.dhw_enabled,
        "valve_mode": p.mixing_valve_mode,
        # Additive (issue #40): the layout key the model resolved to, and
        # whether it runs the two-tank physics. Both renderers key off these
        # rather than re-deriving "is there a wood tank" for themselves.
        "layout": p.topology_layout,
        "two_tank_modelled": two_tank,
        # Additive (v3.16.0): the drawing and the editor's material.
        "edges": [list(e) for e in active_edges],
        "catalog": catalog,
        "positions": dict(positions) if isinstance(positions, dict) else {},
        # Additive (v3.15.1): the DHW tank refills through a coil in the wood
        # tank. Read from the model's own gate rather than re-derived, so the
        # coil is drawn only when it can actually preheat anything — the
        # option alone, without hot water and a modelled wood tank, changes
        # no physics and must therefore change no picture.
        "dhw_wood_coil": p.dhw_coil_active,
        "buffer": {
            "volume_l": p.buffer_tank_volume,
            "is_store": p.buffer_is_store,
            "max_temp": p.buffer_max_temp,
        },
        "wood": {
            "present": wood,
            "volume_l": float(
                config.get(CONF_WOOD_TANK_VOLUME) or DEFAULT_WOOD_TANK_VOLUME
            ),
        },
        "slots": slots,
    }


def _slot_lines(setup: dict[str, Any], place: str) -> list[str]:
    lines = []
    for slot in setup["slots"]:
        if slot["place"] != place:
            continue
        mark = "*" if slot["entity"] else "-"
        value = slot["entity"] or "not configured"
        lines.append(f"  {mark} {slot['label']}: {value}")
    return lines


def render_text_summary(setup: dict[str, Any]) -> str:
    """The read-only overview for the config flow, as monospaced markdown.

    Item 32's recommended staging: a picture of what is configured so far,
    with the empty slots visible. Home Assistant renders flow descriptions
    as markdown, and a fenced block is the one drawing surface that needs no
    endpoint, no authentication story and no frontend support beyond what
    every install already has.
    """
    valve = mixing_valve.is_throttling(setup["valve_mode"])
    # Absent on descriptions captured before issue #40, and false is the
    # right answer for those: the single-tank abstraction is what they ran.
    two_tank = bool(setup.get("two_tank_modelled"))
    parts: list[str] = []

    house = ["House: two zones" if setup["two_zone"] else "House: one zone"]
    house += _slot_lines(setup, "upper_zone")
    if setup["two_zone"]:
        house += _slot_lines(setup, "lower_zone")
        house += _slot_lines(setup, "floor_loop")
    parts.append("\n".join(house))

    hp = ["Heat pump"]
    hp += _slot_lines(setup, "heat_pump")
    parts.append("\n".join(hp))

    buf = setup["buffer"]
    tank = [
        # With a second modelled store the bare word "buffer" stops
        # identifying which tank is meant, so name it by what fills it.
        ("Heat pump tank" if two_tank else "Buffer tank")
        + f": {buf['volume_l']:.0f} L"
        + (
            f", used as a store up to {buf['max_temp']:.0f} °C"
            if buf["is_store"]
            else (", too small to store" if valve else "")
        )
    ]
    if valve:
        tank.append(f"  * Mixing valve: {setup['valve_mode']}")
        tank += _slot_lines(setup, "mixing_valve")
    else:
        tank.append("  - Mixing valve: none (delivery is not throttled)")
    tank += _slot_lines(setup, "buffer_tank")
    parts.append("\n".join(tank))

    if setup["dhw"]:
        dhw = ["Hot water tank"]
        # Absent on descriptions captured before v3.15.1, and absent is the
        # right rendering for those: no coil, so nothing to say. Placed like
        # the wood tank's caption, immediately under the heading it qualifies.
        if setup.get("dhw_wood_coil"):
            dhw.append("  (refilled through a coil in the wood tank)")
        dhw += _slot_lines(setup, "dhw_tank")
        parts.append("\n".join(dhw))

    if setup["wood"]["present"]:
        # Two tanks or one: the caption is the honest difference. Without the
        # two-tank model the separate tank is drawn but its heat is folded
        # into the heat-pump tank, and the summary must admit that; with it,
        # the tank is a store in its own right and the caption would lie.
        wood = [
            f"Wood furnace tank: {setup['wood']['volume_l']:.0f} L"
            + (", modelled as its own store" if two_tank else "")
        ]
        if not two_tank:
            wood.append("  (modelled as heat into the heat-pump tank)")
        # The valve-outlet probe's slot lives on the wood tank here (or on
        # the 4-way valve in the two-tank layout, rendered above) — there is
        # no separate wood-valve section since v4.0.0.
        wood += _slot_lines(setup, "wood_tank")
        parts.append("\n".join(wood))

    outside = ["Outside"]
    outside += _slot_lines(setup, "outdoor")
    parts.append("\n".join(outside))

    body = "\n\n".join(parts)
    return f"```\n{body}\n```"

"""The plan, told in sentences (T6 #29).

The reason codes (item 16) made each slot explicable one tooltip at a time;
this module tells the whole day at once: group the plan's steps by reason,
total each group's energy and money, and render one line per reason —
"6.2 kWh in the cheapest hours for 8.40 kr", "holding the minimum
temperature cost 2.10 kr", and so on, ordered by spend.

Two contracts hold everything honest:

* The groups are ARITHMETIC over the same schedule the plan sensors
  publish — sums of the very steps, never a re-derivation — so the
  narrative can never disagree with the plan it narrates.
* The text comes from the template tables below, ``str.format`` over named
  placeholders, one table per language with identical keys and identical
  placeholders (asserted by the test suite). Never f-strings: an English
  sentence hard-coded at a call site is a sentence Swedish can never say.

Templates live here as data rather than in the translation JSON because
hassfest validates ``strings.json`` against a fixed schema with no room for
free-form template sections; the parity contract is enforced by tests
instead. Kept free of Home Assistant imports so it can be unit-tested
directly.
"""
from __future__ import annotations

from typing import Any

LANGUAGES = ("en", "sv")

#: One sentence per reason code, per language. Placeholders: {kwh} energy
#: in the group, {sek} its cost, {hours} total duration in hours. Keys and
#: placeholders MUST stay identical across languages — tests enforce it.
TEMPLATES: dict[str, dict[str, str]] = {
    "en": {
        "cheap_price": "{kwh} kWh in the cheapest hours for {sek} kr",
        "comfort_floor": "holding the minimum temperature took {kwh} kWh ({sek} kr)",
        "preheat_weather": "pre-heating {kwh} kWh before colder weather ({sek} kr)",
        "terminal_value": "leaving the house warm past the horizon: {kwh} kWh ({sek} kr)",
        "solar_surplus": "{kwh} kWh covered by solar surplus ({sek} kr)",
        "dhw_window": "hot water needed now: {kwh} kWh ({sek} kr)",
        "dhw_ready": "getting the tank ready for a demand window: {kwh} kWh ({sek} kr)",
        "dhw_preheat": "charging the tank while electricity is cheap: {kwh} kWh ({sek} kr)",
        "legionella": "the anti-legionella cycle takes {kwh} kWh ({sek} kr)",
        "manual_plan": "{kwh} kWh you scheduled yourself ({sek} kr)",
        "idle": "idle for {hours} h",
        "untagged": "{kwh} kWh outside the plan ({sek} kr)",
    },
    "sv": {
        "cheap_price": "{kwh} kWh under de billigaste timmarna för {sek} kr",
        "comfort_floor": "att hålla minimitemperaturen tog {kwh} kWh ({sek} kr)",
        "preheat_weather": "förvärmning med {kwh} kWh inför kallare väder ({sek} kr)",
        "terminal_value": "huset lämnas varmt bortom horisonten: {kwh} kWh ({sek} kr)",
        "solar_surplus": "{kwh} kWh täckta av solöverskott ({sek} kr)",
        "dhw_window": "varmvatten behövs nu: {kwh} kWh ({sek} kr)",
        "dhw_ready": "tanken görs redo inför ett behovsfönster: {kwh} kWh ({sek} kr)",
        "dhw_preheat": "tanken laddas medan elen är billig: {kwh} kWh ({sek} kr)",
        "legionella": "legionellacykeln tar {kwh} kWh ({sek} kr)",
        "manual_plan": "{kwh} kWh som du själv schemalagt ({sek} kr)",
        "idle": "viloläge i {hours} h",
        "untagged": "{kwh} kWh utanför planen ({sek} kr)",
    },
}


def group_by_reason(
    powers: list[float],
    prices: list[float],
    reasons: list[str],
    dt_hours: float,
) -> dict[str, dict[str, float]]:
    """Sum a schedule into per-reason totals: kwh, sek, hours.

    Steps beyond the reasons list (or with a falsy code) group as
    "untagged" — the totals must cover every step, or the narrative's sum
    quietly disagrees with the plan sensor's.
    """
    groups: dict[str, dict[str, float]] = {}
    for i, power in enumerate(powers):
        reason = (
            reasons[i] if reasons and i < len(reasons) and reasons[i] else "untagged"
        )
        entry = groups.setdefault(reason, {"kwh": 0.0, "sek": 0.0, "hours": 0.0})
        p = float(power or 0.0)
        price = float(prices[i]) if i < len(prices) else 0.0
        entry["kwh"] += p * dt_hours
        entry["sek"] += p * price * dt_hours
        entry["hours"] += dt_hours
    return groups


def build(
    space: dict[str, list],
    dhw: dict[str, list],
    dt_hours: float,
) -> list[dict[str, Any]]:
    """The structured narrative: one item per reason, biggest spend first.

    ``space``/``dhw`` each carry ``powers``, ``prices`` and ``reasons`` for
    one channel; the channels merge because the reader's question is "where
    does the money go", not "which circuit spent it" — the reason codes are
    already channel-specific where that distinction matters.
    """
    merged: dict[str, dict[str, float]] = {}
    for channel in (space, dhw):
        groups = group_by_reason(
            channel.get("powers") or [],
            channel.get("prices") or [],
            channel.get("reasons") or [],
            dt_hours,
        )
        for reason, entry in groups.items():
            into = merged.setdefault(
                reason, {"kwh": 0.0, "sek": 0.0, "hours": 0.0}
            )
            for key, value in entry.items():
                into[key] += value
    items = []
    for reason, entry in merged.items():
        # Idle carries no energy by definition; every other zero-energy
        # group is noise (a reason that never actually drew) and a line
        # saying "0.0 kWh for 0.00 kr" teaches the reader nothing.
        if reason != "idle" and entry["kwh"] < 0.05:
            continue
        items.append(
            {
                "reason": reason,
                "kwh": round(entry["kwh"], 2),
                "sek": round(entry["sek"], 2),
                "hours": round(entry["hours"], 2),
            }
        )
    items.sort(key=lambda item: (-item["sek"], -item["kwh"], item["reason"]))
    return items


def render(items: list[dict[str, Any]], language: str) -> list[str]:
    """The narrative lines in one language, unknown reasons skipped.

    Skipped rather than crashed or anglicised: a reason code added by a
    later version must degrade to a missing sentence, not break the sensor
    or leak English into a Swedish narrative.
    """
    table = TEMPLATES.get(language) or TEMPLATES["en"]
    lines = []
    for item in items:
        template = table.get(item["reason"])
        if not template:
            continue
        lines.append(
            template.format(
                kwh=f"{item['kwh']:.1f}",
                sek=f"{item['sek']:.2f}",
                hours=f"{item['hours']:.1f}",
            )
        )
    return lines

"""Diagnostics for the Heat Pump Optimizer config entry (audit D10-12).

``Download diagnostics`` in Home Assistant produces this JSON, and the file
routinely ends up attached to a public issue or forum post.

The rule the Gold-scale item set was "no credential ever leaves the
instance". #509 found that rule narrower than the risk: ``entry.data`` was
emitted verbatim apart from the token, and ``CONF_SOLAR_LOCATION`` is seeded
by ``config_flow._default_location`` from ``hass.config.latitude`` -- so the
usual install, which accepts the pre-filled field, published its home to
building precision. The rule is now **no credential and no personal
location**, enforced with Home Assistant's own ``async_redact_data`` so it
holds at any depth rather than only over the top-level keys of ``entry.data``.

What is kept, and why, because over-redaction makes a diagnostics file
useless for the support it exists for: the entity ids, which say which
sensors the install was reading; the MQTT topics, which are the usual cause
of an ECL110 control fault; and the building and tariff parameters, which are
the thermal model a "my plan is wrong" report is about. None of those is
pre-filled from anything private.

``config`` is the live configuration -- ``entry.options`` laid over
``entry.data``, exactly what the coordinator runs on -- under the same
redaction. It used to be ``entry.data`` alone, so a live install's dump showed
setup-time limits where the running ones had been changed through options.
The setup data stays beside it as ``config_setup``, and
``config_overridden_by_options`` names the keys whose live value is not the
setup one.

R9-UX-7 (#1795) adds what the published payload says about the last cycle:
the last diagnosis, the input states, a plan summary (counts and totals, no
per-step series) and the learning view. Two kinds of entity id are an
exception to "ids are kept": a ``person.*`` id names a member of the
household and a ``calendar.*`` id a family calendar, and the away and
holiday options hold them. They are redacted wherever they appear, inside a
message string too, because an input problem echoes the id it is about.

R10-DIAG-REDACT: a keyed pass removes a value only under its key, and D15's
production triage found redacted credential values elsewhere in the same
payload. So each value the entry's keyed passes remove -- the token, the entry
name, each coordinate at full precision -- is searched for in the whole
payload afterwards and redacted wherever it is: inside a message, as a key,
or as the number under a key the coarsening does not name. A value shorter
than ``replay_doc.LEAK_MIN_CHARS`` is not searched for, as the replay's own
leak check does not, so a two-letter name cannot blank every word holding it.

#2814: the download says when it was taken (``exported_at``), and the plan
summary's ``plan_age_minutes`` is measured at that instant from
``last_optimization``. The published value is the age when the payload was
built, up to one optimisation interval earlier, so a 14-minute-old plan read
0.8 in the owner's bundle.

Its residue: the input watchdog's view is judged at the export -- every age,
including the age its problem messages render, and both verdicts beside them,
``input_health`` and ``stale_inputs``; ``plan_stale`` is judged at the export by
the coordinator's own limit; and the debug manifest states when the stored
self-tests ran.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime
from functools import reduce
from typing import Any

from homeassistant.components.diagnostics import REDACTED, async_redact_data
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from . import accuracy, debugger, draw_range, early_cutoff, pump_arbiter, replay_doc
from .const import CONF_COP_SCALE, CONF_TIBBER_TOKEN, DOMAIN, PRIVATE_ENTITY_ID
from .drift import stored_age_seconds
from .inputs import describe_problem, health_summary
from .thermal_model import probe_install
from .coordinator import (
    CoordinatorDiagnostics,
    HeatPumpOptimizerConfigEntry,
    HeatPumpOptimizerCoordinator,
    plan_stale_limit_minutes,
)
from .payload import LearningView

#: Keys whose values never leave the instance, at any depth: the Tibber
#: credential, and the entry name, which is free text the user typed and
#: which nothing outside the config flow's entry title reads. Redacting
#: ``name`` at any depth is deliberate even though it is a common key --
#: blanking an internal label a future summary adds is a far cheaper failure
#: than publishing a household name, and a privacy control fails safe.
TO_REDACT = {CONF_TIBBER_TOKEN, CONF_NAME}

#: Coordinate keys, wherever they are nested. Coarsened, not redacted.
COORDINATE_KEYS = frozenset({"latitude", "longitude"})

#: Decimal places kept on a coordinate. One place is about 11 km of latitude
#: and 6 km of longitude at the 59 degrees N of a Swedish install -- far
#: coarser than the dwelling #509 was about, and at or below Open-Meteo's own
#: forecast grid, so it cannot change which cell a reader would look up. A
#: fully redacted coordinate would hide the two faults this field actually
#: produces: latitude and longitude swapped, and a location in the wrong
#: country.
COORDINATE_PLACES = 1

#: The input watchdog's published keys (the coordinator's input health view).
INPUT_KEYS = (
    "input_health",
    "stale_inputs",
    "input_problems",
    "problem_inputs",
    "problem_messages",
    "input_ages_minutes",
    "input_ages_at",
    "learners_frozen",
    "learner_freeze_reason",
)


def _without_private_ids(value: Any) -> Any:
    """``value`` with every person and calendar entity id redacted, at any depth."""
    if isinstance(value, str):
        return PRIVATE_ENTITY_ID.sub(REDACTED, value)
    if isinstance(value, Mapping):
        return {key: _without_private_ids(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_without_private_ids(item) for item in value]
    return value


def _private_values(node: Any, under: str | None = None) -> set[str]:
    """The text of every value the keyed passes remove from ``node``: each one
    under a ``TO_REDACT`` key, and each coordinate the coarsening cuts.

    A leaf's text is ``str(leaf)`` whatever its type, as ``_without_values``
    reads it: the keyed pass blanks a value of any type.
    """
    if isinstance(node, Mapping):
        return set().union(*(_private_values(item, key) for key, item in node.items()))
    if isinstance(node, list):
        return set().union(*(_private_values(item, under) for item in node))
    removed = under in TO_REDACT or (under in COORDINATE_KEYS and _coordinate(node) != node)
    text = str(node)
    return {text} if removed and len(text) >= replay_doc.LEAK_MIN_CHARS else set()


def _without_values(value: Any, private: frozenset[str]) -> Any:
    """``value`` with each of ``private`` redacted wherever it appears, at any depth."""
    if isinstance(value, str):
        return reduce(lambda text, secret: text.replace(secret, REDACTED), private, value)
    if isinstance(value, Mapping):
        return {_without_values(key, private): _without_values(item, private)
                for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_without_values(item, private) for item in value]
    # Any other leaf is matched whole, by its text. A flag's, "True", and
    # None's are shorter than any value searched for.
    return REDACTED if str(value) in private else value


def _over_age(problem: Any) -> bool:
    """Whether this problem's re-based age has passed its own published limit.

    A fault code is not a measurement at any age: ``InputReader.read`` sets
    ``implausible`` after the age gate, so it already outranks staleness and
    the export does not relabel it.
    """
    age = problem.get("age_minutes")
    limit = problem.get("max_age_minutes")
    return (
        problem.get("problem") != "implausible"
        and isinstance(age, (int, float))
        and isinstance(limit, (int, float))
        and age > limit
    )


def _aged_problem(problem: Mapping[str, Any], aged: Callable[[Any], Any]) -> dict[str, Any]:
    """One published problem, its age re-based and its staleness re-judged at the export.

    An input the publication called stale stays stale, its age only grows; one
    whose age now passes its own limit joins it.
    """
    entry = {**problem, "age_minutes": aged(problem.get("age_minutes"))}
    return {**entry, "problem": "stale"} if _over_age(entry) else entry


def _inputs_at(data: Mapping[str, Any], now: datetime) -> dict[str, Any]:
    """The input watchdog's keys, each age re-based from ``input_ages_at`` to ``now``.

    With no read instant, or one ahead of ``now``, the ages stay as published.

    An age is half a field. ``problem_messages`` renders a second, and
    ``input_health`` / ``stale_inputs`` are verdicts about a third. Re-basing
    only the numbers let one payload state a 20-minute age in the message and
    a 60-minute age beside it, with an age twice its own ``max_age_minutes``
    still reported healthy (#2873's fix review). So every age-bearing field
    and both verdicts are judged at ``now`` -- the export the rest of this
    module dates its ages at (the module docstring) -- and no third time base
    is invented. Staleness is the one class the export can re-judge, being
    this age against this limit with both published (:func:`_over_age`).
    """
    inputs = {key: data[key] for key in INPUT_KEYS if key in data}
    elapsed = stored_age_seconds(data.get("input_ages_at"), now)
    if elapsed is None:
        return inputs

    def aged(minutes: Any) -> Any:
        return round(minutes + elapsed / 60.0, 1) if isinstance(minutes, (int, float)) else minutes

    if isinstance(ages := inputs.get("input_ages_minutes"), Mapping):
        inputs["input_ages_minutes"] = {key: aged(age) for key, age in ages.items()}
    if isinstance(problems := inputs.get("input_problems"), list):
        entries = [
            _aged_problem(problem, aged) if isinstance(problem, Mapping) else problem
            for problem in problems
        ]
        over_age = {entry.get("input") for entry in entries if _over_age(entry)}
        stale = {key for key in (inputs.get("stale_inputs") or []) if isinstance(key, str)}
        stale.update(over_age)
        missing = {
            entry.get("input") for entry in entries
            if entry.get("entity_id") and entry.get("input") not in stale
            and entry.get("problem") != "stale"
        }
        inputs.update({
            key: value for key, value in (
                ("input_problems", entries),
                ("stale_inputs", sorted(stale)),
                ("problem_messages",
                 [describe_problem(entry) for entry in entries if entry.get("entity_id")]),
                ("input_health", health_summary(stale, missing)),
            ) if key in inputs
        })
    return inputs


def _plan_summary(
    data: Mapping[str, Any], now: datetime, stale_limit: float | None = None
) -> dict[str, Any]:
    """What the current plan is, in counts and totals: no per-step series.

    Its age is measured at ``now``, the export, not copied from the payload,
    and so is ``plan_stale`` wherever the export can date the plan and the
    coordinator's limit is readable; a plan the export cannot date keeps the
    verdict it was published with.
    """
    age = stored_age_seconds(data.get("last_optimization"), now)
    stale = (data.get("plan_stale") if stale_limit is None or age is None
             else age / 60.0 > stale_limit)

    def channel(plan: Any) -> dict[str, Any]:
        plan = plan if isinstance(plan, Mapping) else {}
        return {
            "steps": len(plan.get("forecast") or []),
            "slots": len(plan.get("slots") or []),
            "total_energy_kwh": plan.get("total_energy_kwh"),
            "total_cost": plan.get("total_cost"),
            "active_now": plan.get("active_now"),
        }

    return {
        **{
            key: data.get(key)
            for key in (
                "mode",
                "optimization_status",
                "last_optimization",
                "next_optimization",
                "current_action",
            )
        },
        "plan_stale": stale,
        "plan_age_minutes": round(age / 60.0, 1) if age is not None else None,
        "space": channel(data.get("space_plan")),
        "dhw": channel(data.get("dhw_plan")),
    }


def _published_sections(coord: Any, now: datetime) -> dict[str, Any]:
    """The last cycle as the entities saw it: diagnosis, inputs, plan, learning."""
    data = getattr(coord, "data", None)
    data = data if isinstance(data, Mapping) else {}
    insight = data.get("insight")
    return {
        "last_diagnosis": (
            insight.get("last_diagnosis") if isinstance(insight, Mapping) else None
        ),
        "inputs": _inputs_at(data, now),
        "plan": _plan_summary(
            data, now, plan_stale_limit_minutes(getattr(coord, "effective_config", None))
        ),
        "learning": {key: data[key] for key in LearningView.__annotations__ if key in data},
    }


def _coordinate(value: Any) -> Any:
    """One coordinate, coarsened -- or redacted if it is not a number.

    Free text under a coordinate key can be an address, so only something
    that converts to a float is published.
    """
    try:
        return round(float(value), COORDINATE_PLACES)
    except (TypeError, ValueError):
        return REDACTED


def _coarsen(value: Any) -> Any:
    """``value`` with every coordinate coarsened, at any depth."""
    if isinstance(value, Mapping):
        return {
            key: _coordinate(item) if key in COORDINATE_KEYS else _coarsen(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_coarsen(item) for item in value]
    return value


def config_view(
    data: Mapping[str, Any], options: Mapping[str, Any]
) -> dict[str, Any]:
    """The live config, the setup data under it, and what options changed."""
    return {
        "config": {**data, **options},
        "config_setup": dict(data),
        "config_overridden_by_options": sorted(
            k for k in options if k not in data or options[k] != data[k]
        ),
    }


def _coordinator_snapshot(coord: HeatPumpOptimizerCoordinator) -> dict[str, Any]:
    """The runtime state a bug report actually needs.

    Deliberately small and plain: the learners' own summary() dictionaries,
    the outage latches and the staleness flags -- the things that explain
    WHY a plan looks wrong -- without the 200-key published payload
    (reproducible from the entities) or any trajectory array (large, and
    derivable). The counters and learner summaries arrive through the
    coordinator's published ``diagnostics_state`` view (#1739); a
    coordinator that cannot produce one (a duck-typed harness) reports the
    fields as ``None``, exactly as the per-field ``getattr`` fallbacks did.
    """
    try:
        state: CoordinatorDiagnostics | None = coord.diagnostics_state()
    except Exception:  # noqa: BLE001 -- diagnostics never breaks
        state = None
    snap: dict[str, Any] = {
        "mode": getattr(coord, "mode", None),
        "tibber_outage_cycles": state.tibber_outage_cycles if state else None,
        "tibber_reauth_started": state.tibber_reauth_started if state else None,
        "weather_stale_hours": coord.weather_stale_hours()
        if hasattr(coord, "weather_stale_hours")
        else None,
        "optimization_running": getattr(coord, "optimization_running", None),
        "solve_failures": state.solve_failures if state else None,
        CONF_COP_SCALE: state.cop_scale if state else None,
        "cop_samples": state.cop_samples if state else None,
        "house_heat_loss_scale": state.house_heat_loss_scale if state else None,
        "last_update_success": bool(
            getattr(coord, "last_update_success", False)
        ),
    }
    if state:
        snap.update(state.learner_summaries)
    snap.update({key: _never_breaks(view, coord) for key, view in _VIEWS})
    return snap


def _never_breaks(view: Callable[[Any], Any], coord: Any) -> Any:
    """One module's view, or ``"unavailable"``: diagnostics never breaks."""
    try:
        return view(coord)
    except Exception:  # noqa: BLE001 -- diagnostics never breaks
        return "unavailable"


#: Each module's own ``diagnostics_view``, one ``(key, view)`` row per module.
#: A row reads the coordinator's public views and hands its module values.
_VIEWS: tuple[tuple[str, Callable[[Any], Any]], ...] = (
    ("pump_duty", pump_arbiter.diagnostics_view),
    ("early_cutoff", lambda c: early_cutoff.diagnostics_view(early_cutoff.state_for(c))),
    ("draw_range", lambda c: draw_range.diagnostics_view(
        c.accuracy.draw, c.thermal_params,
        probe_install(c.arbiter_inputs().config))),
    # Why the observed-COP sensor has nothing yet: it is unavailable then, and
    # Home Assistant hides an unavailable entity's attributes.
    ("cop_learner", lambda c: accuracy.diagnostics_view(c.measured_cop, c.thermal_params, c.accuracy.draw)),
)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    now = dt_util.utcnow()
    coord = entry.runtime_data if hasattr(entry, "runtime_data") else None
    snapshot = _coordinator_snapshot(coord) if coord else None
    collector = debugger.collector_for(coord) if coord else None
    # Both passes run over the whole payload rather than over ``entry.data``
    # alone, so a coordinate or a credential that a future coordinator
    # summary starts carrying is covered without a second decision here --
    # the debug bundle's payload snapshots and store documents included. The
    # value pass then finds what they removed under any other key.
    private = frozenset(_private_values([dict(entry.data), dict(entry.options)]))
    redacted: dict[str, Any] = _without_values(async_redact_data(
        _without_private_ids(
            _coarsen(
                {
                    "exported_at": now.isoformat(),
                    "entry": {
                        "version": entry.version,
                        "options_keys": sorted(entry.options.keys()),
                    },
                    **config_view(entry.data, entry.options),
                    "coordinator": snapshot,
                    **_published_sections(coord, now),
                    "domain": DOMAIN,
                    # #1940: capped, so a week too large to inline is its summary.
                    "debug": debugger.capped(
                        await collector.async_bundle(coord, snapshot, entry),
                        f"{DOMAIN}_{entry.entry_id}_debug",
                    ) if collector else None,
                }
            )
        ),
        TO_REDACT,
    ), private)
    return redacted

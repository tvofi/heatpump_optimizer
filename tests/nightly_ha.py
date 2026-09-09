#!/usr/bin/env python3
"""Home Assistant itself, in the container an installation actually runs (#521).

``tests/deployment_shape.py`` (#513) builds the deployment *shape* -- the
production module name and the ``custom_components`` filesystem layout, with no
``tests/`` sibling -- and drives the process worker through it in about a
second. It says in its own docstring what it cannot do: ``homeassistant`` comes
from ``tests/hastub`` there, as it does in every other lane, so no script in
this directory has ever observed real Home Assistant import or setup semantics.
That is the third divergence of #513 and it is what let #511 -- every solve
failing, on every install, permanently -- ship green in v6.3.15.

This lane closes it by running the integration inside the official
``homeassistant/home-assistant`` image: real Home Assistant, real interpreter,
real ``/config/custom_components/heatpump_optimizer`` path, real
``custom_components.*`` qualified name, real config-entry setup. It is nightly
only, because it costs minutes, needs Docker, and is the first lane here that
can go red for a reason outside this repository.

THE ASSERTION THAT MATTERS IS THAT A PLAN CAME OUT. Setup succeeded throughout
#511; it was the solve that failed. A lane asserting only "the integration
loaded" would have been green for the whole of that release, so the checks are
ordered outward from ``plan:*`` rather than inward from "it booted".

Deliberately NOT pytest-homeassistant-custom-component. Its layout puts the
repository root on ``sys.path`` and keeps a ``tests/`` sibling, which is the
branch of ``coordinator._worker_env`` no installation takes -- so #511 may not
reproduce under it at all. It would buy real Home Assistant import semantics
while staying blind to the defect that motivated the work.

WHAT THIS LANE DOES NOT COVER, stated the way ``deployment_shape.py`` states
its own limit:

* **Tibber.** Prices are the one input whose absence stops a solve outright
  (``_fetch_tibber_prices`` raises ``UpdateFailed``), and the real endpoint
  needs a live account. ``api.tibber.com`` is redirected to a local TLS server
  in the container by ``--add-host``, whose certificate is added to the trust
  store the shared aiohttp session uses. Production code is not patched: the
  real URL, the real session and real TLS are exercised; only the counterparty
  is ours. The Tibber *account* path -- reauth, a refused token -- is not
  covered.
* **Actuation.** No heat-pump switch, valve or frequency entity is configured,
  and the two ECL110 MQTT topics are blanked because the container has no
  broker, so ``_apply_action`` and its followers are reached but write
  nowhere. This lane observes that a plan exists, not that it was carried out.
* **Home Assistant's own complaints.** Its loop protection fired twice on this
  integration on this lane's first green run (#525); #540 moved both off the
  loop, so ``KNOWN_BLOCKING`` is empty and ANY report against this package now
  fails ``log:no_new_blocking_call``. ``log:blocking_report_parsed`` catches a
  reword of the half naming the source line. A reword of ``Detected blocking
  call to`` empties the loose anchor; ``log:blocking_positive_control`` is the
  deliberate on-loop ``_lazy`` (#588) that must still match the same regex.
* **The config flow.** The entry is seeded into ``.storage/core.config_entries``
  from the defaults recorded in ``tests/golden/config_flow.json``, so the nine
  setup steps are not driven here. ``tests/entities.py`` and the golden lane own
  the flow itself.

AND MOST OF WHAT A CONTAINER COULD ASSERT, WHICH THE FOUR LIMITS ABOVE DO NOT
SAY (#533). The programme's production-escape analysis derives fourteen
assertions for this lane; the four above are not any of the ten missing ones,
so a reader had to re-derive the gap to find it. Written down instead:

===  ====================================================  ==========  =======
A    what it asserts                                       escapes     state
===  ====================================================  ==========  =======
A1   the entry reaches ``loaded``, both image tags         6           done
A2   a plan was actually produced                          4           done
A3   the published-state sweep, judged by HA's machinery   named set   done
A4   availability conjoins the coordinator (fault-inject)  6           none
A5   the entry round-trips through its own forms           9           done
A6   corrupt-store resilience                              4           none
A7   the log carries none of this integration's failures   5           partial
A8   services register once; no leftover per-entry handlers 3          done
A9   reload without growth                                 3           done (partial)
A10  diagnostics leak no credential and no location        2           #585
A11  a failing service raises, it does not no-op           3           none
A12  an older schema version migrates                      1           none
A13  the currency follows the instance                     1           none
A14  setup does not block the event loop                   1           partial
===  ====================================================  ==========  =======

A3's named set is the §4 A3 row of the production-escape analysis, counted at
this merge base by listing those identifiers (not by carrying a filed total):
E71, E33, E19, E45, E6, E74, E73, E77, E47, E113, E137, E138, E78, E7, E119.
A4 is a different issue and is not implemented here. The counts are
bullet-level, stable in ranking and about +/-15 in absolute terms; the two
largest classes in the record -- solver numbers and card geometry, 68 escapes
between them -- are out of this lane's reach by construction, so this is the
deployment-shape and HA-citizenship lane and not a general safety net.
A4, A6, A11, A12 and A13 have no issue: they are recorded here and unscheduled,
which is a different thing from unnoticed.
A5/A8/A9 (#587): the form count is derived from ``_OPTION_PAGES`` plus the two
menus, and the service catalog from ``services.yaml``, not from the filed 23/11.
A8's "0 remain" is leftover *per-entry* handlers after both entries unload;
the domain catalog stays, because action-setup registers once on ``async_setup``.
A9 stays partial: the ceiling is the first sample, not zero, because a standing
STOP reap and update listener are load-bearing (#540); leaks only visible as
long-horizon growth (debouncer, in-flight refresh, MQTT) are outside it.

    python tests/nightly_ha.py --image homeassistant/home-assistant:2025.2.0

The same file is the driver that runs inside the container (``--inside``); the
container half never sees this repository, only ``/config`` and its own two
mounted files.
"""
from __future__ import annotations

import argparse
import ast
import asyncio
import dataclasses
import importlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Home Assistant loads an integration from ``<config>/custom_components/<domain>``.
CONFIG_DIR_NAME = "custom_components"
PACKAGE_NAME = "heatpump_optimizer"
PACKAGE_REL = f"{CONFIG_DIR_NAME}/{PACKAGE_NAME}"

# Inside the container. ``/opt/hpo`` holds exactly this file and the seed, so
# nothing on the driver's own ``sys.path`` can make the package under test
# resolvable by accident -- the trap `deployment_shape.py` calls out.
IN_CONFIG = "/config"
IN_DRIVER_DIR = "/opt/hpo"
IN_SEED = f"{IN_DRIVER_DIR}/seed.json"
IN_ROSTER = f"{IN_DRIVER_DIR}/nightly_a3_roster.json"
ROSTER_NAME = "nightly_a3_roster.json"
# tests/hastub and tests/ha_contract.py, mounted beside the driver (#536). The
# contract module is run TWICE here -- once with the stub on PYTHONPATH and once
# without -- because this container is the only place in this repository where
# both providers exist at all. Neither run is on the boot path: the stub is
# never put on the interpreter's own sys.path, only into a subprocess env.
IN_CONTRACT = f"{IN_DRIVER_DIR}/ha_contract.py"
IN_HASTUB = f"{IN_DRIVER_DIR}/hastub"
LOG_NAME = "home-assistant.log"

TIBBER_HOST = "api.tibber.com"

MARKER = "<<<nightly-ha-json>>>"

# A3 named identifiers, re-derived at this merge base from the analysis §4
# A3 row by listing them. Do not substitute a carried total.
A3_NAMED_ESCAPES = (
    "E71", "E33", "E19", "E45", "E6", "E74", "E73", "E77", "E47",
    "E113", "E137", "E138", "E78", "E7", "E119",
)

# Demanded by name from tests/entities.py. A4 is a different issue; these
# names must not grow a fault-injection check.
A3_INSIDE = (
    "a3:roster",
    "a3:orjson",
    "a3:finite",
    "a3:device_class_state_class",
    "a3:no_constructor_defaults",
)

# Demanded by name from tests/entities.py. #509 already closed (#535);
# A10 pins the landed privacy rule, it does not re-open a red nightly.
A10_INSIDE = (
    "a10:no_credential",
    "a10:no_precise_location",
)
A10_COORDINATE_KEYS = frozenset({"latitude", "longitude"})
A10_MAX_COORDINATE_DECIMALS = 2

# A5/A8/A9 named identifiers, listed from #587. Do not substitute a carried total.
A5_NAMED_ESCAPES = (
    "E85", "E116", "E117", "E26", "E44", "E42", "E43", "E41", "E31",
)
A8_NAMED_ESCAPES = ("E37", "E99", "E38")
A9_NAMED_ESCAPES = ("E56", "E2", "E105")

# Demanded by name from tests/entities.py. A4 is a different issue.
A5_INSIDE = (
    "a5:pages_ok",
    "a5:byte_unchanged",
    "a5:service_examples",
    "a5:service_bounds",
)
A8_INSIDE = (
    "a8:register_once",
    "a8:deregister",
    "a8:already_configured",
)
A9_INSIDE = (
    "a9:reload_loaded",
    "a9:roster_unchanged",
    "a9:no_growth",
)
# The issue's trial count, not a derived population.
A9_RELOADS = 5
A8_SECOND_ENTRY_ID = "01JHPA9NGHTHACNTNR00000002"

# What the container half must report. The outer half requires this set
# exactly: a driver that dies after two checks, or one whose checks were
# quietly renamed away, fails here instead of looking like a pass. A no-op is
# indistinguishable from a pass unless something demands the checks by name.
INSIDE_CHECKS = (
    "shape:package_at_config_path",
    "shape:no_tests_sibling",
    "shape:inherited_pythonpath_cannot_mask",
    "ha:home_assistant_is_real",
    "ha:core_running",
    "entry:loaded",
    "entities:registered",
    "entities:coordinator_healthy",
    "entities:none_unavailable_by_coordinator",
    "plan:optimization_result",
    "plan:last_optimization_published",
    "plan:current_action_published",
    "plan:setpoints_non_empty",
    "plan:no_solve_repair",
    # #536. The stub half runs here rather than in the gate for one reason: the
    # comparison needs both providers in one process tree, and the gate has
    # only ever had one.
    "contract:real_provider",
    "contract:stub_provider",
    "contract:probes_agree",
    *A3_INSIDE,
    *A10_INSIDE,
    *A5_INSIDE,
    *A8_INSIDE,
    *A9_INSIDE,
)

# Judged by the outer half, over the container's combined output and the log
# file the run left in the bind mount. The worker child inherits the parent's
# stderr (``coordinator._ensure_worker`` passes ``stderr=None``), so its
# traceback lands on the container's stderr and never in home-assistant.log --
# which is why both streams are scanned rather than the log alone.
#
# Demanded by name, exactly as ``INSIDE_CHECKS`` is, and for the same reason
# its comment gives. Until #533 nothing referenced this tuple at all: it was a
# roster the run never consulted, so a check deleted or renamed out here left
# a shorter green run and no other trace. ``run:all_checks_ran`` is the demand
# and names itself in its own roster.
OUTSIDE_CHECKS = (
    "run:driver_reported",
    "run:exit_status",
    "run:all_checks_ran",
    "log:no_module_not_found",
    "log:no_worker_exit",
    "log:no_integration_traceback",
    "log:blocking_report_parsed",
    "log:no_new_blocking_call",
    "log:blocking_pin_not_stale",
    "log:blocking_positive_control",
)

FORBIDDEN = {
    "log:no_module_not_found": "ModuleNotFoundError",
    "log:no_worker_exit": "process worker exited rc=",
}

TRACEBACK_HEAD = "Traceback (most recent call last):"

# The repairs that mean the solve route itself is in trouble. Named rather than
# "the integration raised nothing", because a defaults-only entry with no
# lower-floor sensor and no legionella schedule legitimately raises others, and
# a check that failed on those would become pressure to weaken it later.
# solve_worker_fallback is #515's: with an in-process fallback in place a
# worker that can unpickle nothing still produces a plan, so without this the
# plan checks alone would call a degraded install healthy.
SOLVE_REPAIRS = frozenset({"solve_failures", "solve_worker_fallback"})

# Home Assistant's own loop protection, which no lane using tests/hastub can
# see -- `homeassistant.util.loop` does not exist there. Its report carries a
# stack, so it is picked out by its own rule instead of being counted as an
# exception traceback.
#
# `BLOCKING_CALL` is built FROM `BLOCKING_AT_OURS` rather than beside it, so
# the loose anchor and the strict pin cannot drift apart. The loose one asks
# only whether Home Assistant blamed this package; the strict one also reads
# the source line, which is the half an upstream reword would take away. A
# report the loose regex claims and the strict one cannot parse is that
# reword, and `log:blocking_report_parsed` is where it lands -- because
# without it the pin degrades to always-pass and says nothing (#533).
_BLOCKING_AT = (
    r"Detected blocking call to (\S+) .* at "
    rf"({re.escape(PACKAGE_REL)}/[\w./]+)"
)
BLOCKING_AT_OURS = re.compile(_BLOCKING_AT)
BLOCKING_CALL = re.compile(_BLOCKING_AT + r", line \d+: (.*?) \(offender:")

# A RATCHET, IN BOTH DIRECTIONS, AND BOTH DIRECTIONS FAIL.
#
# `log:no_new_blocking_call` refuses growth: an offender not listed here is a
# new defect. `log:blocking_pin_not_stale` refuses decay: an offender listed
# here that the run did not produce has been FIXED, and a pin outliving its
# defect would pass while pinning nothing. #525's two entries stood here after
# #540 removed both, and the run went green either way -- one check with a
# subset test and a detail line cannot report the second direction, because a
# shrunken pin is a pass and `Checks.check` blanked the detail on a pass.
#
# The two directions are separate checks rather than an equality test for the
# reason the old comment measured: an offender on a conditional path (#525's
# `worker.wait`, reached only while the worker is alive) is legitimately
# absent from some runs. Equality would fail such a run for a second, unrelated
# reason. Two checks name which direction moved, and a pinned entry whose path
# is that conditional does not belong here in the first place.
#
# Empty since #540 (#533): the import went to `async_add_import_executor_job`
# and the reap to `async_add_executor_job`, so ANY report against this package
# now fails the lane -- the strongest form, and the one an empty pin cannot go
# stale in. If #540's fix is incomplete, this lane says so by name.
KNOWN_BLOCKING: frozenset[tuple[str, str, str]] = frozenset()
BLOCKING_REPORT = "Detected blocking call to"
# The probe must not reach the pin. Home Assistant 2025.2.0 de-duplicates at
# ``(integration, filename, lineno)`` (``homeassistant.util.loop``
# ``_PREVIOUSLY_REPORTED``; a repeat is DEBUG). ``import_module`` is wrapped
# ``strict=False`` and is skipped when ``args[0]`` is already in
# ``sys.modules`` (``block_async_io._check_import_call_allowed``). ``_lazy``
# passes a relative name, which is never a ``sys.modules`` key. A begin/end
# window keeps shutdown (#525's second offender) in the pin half; one
# sentinel after the probe would hide it.
BLOCKING_PROBE_BEGIN = "<<<nightly-ha-blocking-probe-begin>>>"
BLOCKING_PROBE_END = "<<<nightly-ha-blocking-probe-end>>>"
BLOCKING_POSITIVE_CONTROL = "log:blocking_positive_control"

# Config-option keys that seed a thermometer. Popped for A3(e)'s second seed.
THERMOMETER_KEYS = (
    "indoor_temp_entity",
    "outdoor_temp_entity",
    "dhw_temp_entity",
    "buffer_tank_temp_entity",
    "floor_return_temp_entity",
    "lower_floor_temp_entity",
    "valve_outlet_temp_entity",
    "wood_tank_top_entity",
    "wood_tank_bottom_entity",
)


# --- shared reporting -------------------------------------------------------


class Checks:
    """A pass/fail record that survives the container boundary as JSON."""

    def __init__(self) -> None:
        self.results: dict[str, list] = {}

    def check(self, name: str, cond: object, detail: str = "") -> bool:
        """Record a check. The detail is kept whether it passed or failed.

        Blanking it on pass is how the stale ``KNOWN_BLOCKING`` pin stayed
        invisible (#533): its detail names the offenders pinned but not seen,
        and a pin that has gone stale *passes*, so the one line that would
        have reported it was exactly the line thrown away. A detail is a
        measurement, not an excuse for a failure -- write it to read in both
        states, because it is only ever printed in one of them by accident.
        """
        ok = bool(cond)
        self.results[name] = [ok, detail]
        print(f"  {'ok  ' if ok else 'FAIL'} {name}" + (f"  [{detail}]" if detail else ""))
        return ok

    def failures(self) -> list[str]:
        return [n for n, (ok, _) in self.results.items() if not ok]


def _collect_entity_ids() -> list[str]:
    """Entity ids ``async_setup_entry`` adds. Host only; container reads the staged copy.

    Same rule as ``tests/entities.py`` ``collect()`` over ``PLATFORM_LIST``.
    Does not import ``entities`` (that file is the suite).
    """
    tests_dir = str(Path(__file__).resolve().parent)
    cc = str(ROOT / "custom_components")
    stub = str(Path(tests_dir) / "hastub")
    for path in (stub, tests_dir, cc):
        if path not in sys.path:
            sys.path.insert(0, path)
    from harness import FakeCoordinator, FakeEntry, FakeHass
    import heatpump_optimizer as integration

    def collect(module):
        added = []

        def add_entities(entities):
            added.extend(entities)

        coordinator = FakeCoordinator({})
        coordinator._month_totals = {"dhw": (41.5, 62.25), "space": (120.0, 180.0)}
        hass = FakeHass()
        entry = FakeEntry()
        entry.runtime_data = coordinator
        asyncio.run(module.async_setup_entry(hass, entry, add_entities))
        return added

    return sorted(
        e.entity_id
        for p in integration.PLATFORM_LIST
        for e in collect(importlib.import_module(f"heatpump_optimizer.{str(p)}"))
        if getattr(e, "entity_id", None)
    )


def load_committed_roster() -> list[str]:
    """Expected entity ids. Container: the staged collect() copy. Host: collect()."""
    staged = Path(IN_ROSTER)
    if staged.is_file():
        data = json.loads(staged.read_text())
        if not isinstance(data, list) or not all(isinstance(x, str) for x in data):
            raise ValueError(f"{ROSTER_NAME} is not a JSON list of strings")
        return data
    return _collect_entity_ids()


def json_bytes_ha(obj: object) -> bytes:
    """Home Assistant's serializer -- the orjson boundary this check exists for."""
    try:
        from homeassistant.helpers.json import json_bytes
    except ImportError as exc:
        raise RuntimeError(
            "homeassistant.helpers.json is absent; A3(b) cannot judge the orjson boundary"
        ) from exc
    return json_bytes(obj)


def _state_dump_obj(state: object) -> object:
    as_dict = getattr(state, "as_dict", None)
    if callable(as_dict):
        return as_dict()
    return {
        "state": getattr(state, "state", None),
        "attributes": dict(getattr(state, "attributes", None) or {}),
    }


def _nonfinite_paths(node: object, path: str, found: list[str]) -> None:
    if isinstance(node, bool):
        return
    if isinstance(node, dict):
        for key, value in node.items():
            _nonfinite_paths(value, f"{path}.{key}", found)
    elif isinstance(node, (list, tuple)):
        for index, value in enumerate(node):
            _nonfinite_paths(value, f"{path}[{index}]", found)
    elif isinstance(node, (int, float)) and not math.isfinite(float(node)):
        found.append(f"{path}={node!r}")


def _close(value: object, default: object) -> bool:
    if default is None or not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    if not isinstance(default, (int, float)) or isinstance(default, bool):
        return False
    return math.isclose(float(value), float(default), rel_tol=0.0, abs_tol=1e-9)


def check_a3_roster(
    checks: Checks,
    registered_ids: list[str],
    expected: list[str] | None = None,
) -> None:
    want = set(expected if expected is not None else load_committed_roster())
    got = set(registered_ids)
    checks.check(
        "a3:roster",
        got == want,
        f"{len(got)} registered, {len(want)} in the committed collect() roster; "
        f"missing={sorted(want - got)}; extra={sorted(got - want)}",
    )


def check_a3_orjson(
    checks: Checks,
    items: list[tuple[str, object]],
    dumps=None,
) -> None:
    serialize = dumps if dumps is not None else json_bytes_ha
    bad = []
    for entity_id, obj in items:
        try:
            serialize(obj)
        except Exception as exc:
            bad.append(f"{entity_id}:{type(exc).__name__}:{exc}")
    checks.check(
        "a3:orjson",
        not bad,
        f"{len(bad)} failed HA json_bytes"
        + (f"; first: {bad[:3]}" if bad else ""),
    )


def check_a3_finite(checks: Checks, items: list[tuple[str, object]]) -> None:
    found: list[str] = []
    for entity_id, obj in items:
        _nonfinite_paths(obj, entity_id, found)
    checks.check(
        "a3:finite",
        not found,
        f"{len(found)} non-finite" + (f"; {found[:6]}" if found else ""),
    )


def check_a3_device_class_state_class(
    checks: Checks,
    pairs: list[tuple[str, object, object]],
    table=None,
) -> None:
    if table is None:
        from homeassistant.components.sensor import DEVICE_CLASS_STATE_CLASSES

        table = DEVICE_CLASS_STATE_CLASSES
    forbidden = []
    for entity_id, device_class, state_class in pairs:
        if not device_class or not state_class:
            continue
        allowed = table.get(device_class)
        if allowed is None:
            allowed = table.get(str(device_class))
        if allowed is None:
            continue
        allowed_s = {str(item) for item in allowed}
        if str(state_class) not in allowed_s:
            forbidden.append(f"{entity_id}:{device_class}+{state_class}")
    checks.check(
        "a3:device_class_state_class",
        not forbidden,
        f"{len(forbidden)} forbidden pair(s)"
        + (f": {forbidden[:6]}" if forbidden else ""),
    )


def _thermal_defaults():
    try:
        from custom_components.heatpump_optimizer.thermal_model import ThermalState
    except ImportError:
        from heatpump_optimizer.thermal_model import ThermalState
    return ThermalState()


def _numeric_constructor_defaults(state) -> list[float]:
    """Finite numeric fields of a ThermalState instance, from the constructor."""
    out: list[float] = []
    for field in dataclasses.fields(type(state)):
        value = getattr(state, field.name)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if not math.isfinite(float(value)):
            continue
        out.append(float(value))
    return out


def check_a3_no_constructor_defaults(
    checks: Checks,
    records: list[dict],
    *,
    defaults=None,
    roster: list[str] | None = None,
) -> None:
    """Available temperature/climate/volume must not be a ThermalState default.

    An empty records list is a sweep that judged nothing, not a pass.
    """
    if not records:
        checks.check(
            "a3:no_constructor_defaults",
            False,
            "empty sweep: no published states were judged",
        )
        return
    state = defaults if defaults is not None else _thermal_defaults()
    numeric_defaults = _numeric_constructor_defaults(state)
    offenders = []
    for rec in records:
        entity_id = rec["entity_id"]
        published = rec.get("state")
        attrs = rec.get("attributes") or {}
        unavailable = published in ("unavailable", "unknown", "none", None)
        device_class = rec.get("device_class") or attrs.get("device_class")
        if str(device_class) == "volume_storage":
            if not unavailable:
                offenders.append(f"{entity_id}:available volume_storage={published!r}")
            continue
        if not unavailable and str(device_class) == "temperature":
            try:
                value = float(published)
            except (TypeError, ValueError):
                value = None
            if value is not None and any(_close(value, d) for d in numeric_defaults):
                offenders.append(f"{entity_id}:temperature={value}")
        if entity_id.startswith("climate.") and not unavailable:
            for key, raw in attrs.items():
                if "temperature" not in str(key).lower():
                    continue
                if any(_close(raw, d) for d in numeric_defaults):
                    offenders.append(f"{entity_id}.{key}={raw!r}")
    checks.check(
        "a3:no_constructor_defaults",
        not offenders,
        f"{len(offenders)} constructor default(s) published as available"
        + (f": {offenders[:8]}" if offenders else ""),
    )


def _json_decimal_places(value: object) -> int | None:
    """Decimal places in the JSON spelling, or None if ``value`` is not a number.

    The #585 rule is about the published token, not float equality: 59.330
    dumped as ``59.33`` is two places.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        dumped = json.dumps(value)
    elif isinstance(value, str):
        try:
            float(value)
        except ValueError:
            return None
        dumped = value if "." in value else json.dumps(float(value))
    else:
        return None
    if "." not in dumped:
        return 0
    return len(dumped.split(".", 1)[1])


def _a10_coordinate_hits(node: object, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            if key in A10_COORDINATE_KEYS:
                places = _json_decimal_places(value)
                if places is not None and places > A10_MAX_COORDINATE_DECIMALS:
                    hits.append(f"{here}={value!r} ({places} dp)")
            hits.extend(_a10_coordinate_hits(value, here))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            hits.extend(_a10_coordinate_hits(value, f"{path}[{i}]"))
    return hits


def check_a10_no_credential(
    checks: Checks, payload: object, tokens: tuple[str, ...] | list[str] = ()
) -> None:
    blob = json.dumps(payload, default=str)
    found = [token for token in tokens if token and token in blob]
    checks.check(
        "a10:no_credential",
        not found,
        (
            "token(s) in payload: " + ", ".join(found[:4])
            if found
            else "no demanded token in payload"
        ),
    )


def check_a10_no_precise_location(checks: Checks, payload: object) -> None:
    hits = _a10_coordinate_hits(payload)
    checks.check(
        "a10:no_precise_location",
        not hits,
        (
            f"{len(hits)} coordinate(s) beyond {A10_MAX_COORDINATE_DECIMALS} dp"
            + (f"; {hits[:4]}" if hits else "")
        ),
    )


def check_a10_payload(
    checks: Checks, payload: object, tokens: tuple[str, ...] | list[str] = ()
) -> None:
    check_a10_no_credential(checks, payload, tokens)
    check_a10_no_precise_location(checks, payload)


async def _async_check_a10_published(checks: Checks, hass, entry) -> None:
    import importlib

    diag = None
    err = ""
    for name in (
        f"{PACKAGE_NAME}.diagnostics",
        f"{CONFIG_DIR_NAME}.{PACKAGE_NAME}.diagnostics",
    ):
        try:
            diag = importlib.import_module(name)
            break
        except ImportError as exc:
            err = f"{name}: {exc}"
            continue
    if diag is None:
        checks.check("a10:no_credential", False, err or "diagnostics module did not import")
        checks.check(
            "a10:no_precise_location", False, err or "diagnostics module did not import"
        )
        return
    payload = await diag.async_get_config_entry_diagnostics(hass, entry)
    data = getattr(entry, "data", {}) or {}
    token = data.get("tibber_token")
    tokens = tuple(t for t in (token, "nightly-ha-local") if t)
    check_a10_payload(checks, payload, tokens)


def _prod_mod(name: str):
    """The installed package, then the host ``heatpump_optimizer`` import."""
    for prefix in (f"{CONFIG_DIR_NAME}.{PACKAGE_NAME}", PACKAGE_NAME):
        try:
            return importlib.import_module(f"{prefix}.{name}")
        except ImportError:
            continue
    raise ImportError(name)


def option_step_ids(pages=None) -> tuple[str, ...]:
    """``init``, ``advanced``, then every ``_OPTION_PAGES`` step. Derived."""
    if pages is None:
        pages = _prod_mod("config_flow")._OPTION_PAGES
    return ("init", "advanced") + tuple(page.step for page in pages)


def load_services_catalog(path: Path | None = None) -> dict:
    import yaml

    if path is None:
        staged = Path(IN_CONFIG) / PACKAGE_REL / "services.yaml"
        path = staged if staged.is_file() else ROOT / PACKAGE_REL / "services.yaml"
    data = yaml.safe_load(path.read_text())
    return data if isinstance(data, dict) else {}


def documented_service_names(catalog: dict | None = None) -> frozenset[str]:
    return frozenset((catalog if catalog is not None else load_services_catalog()))


def service_example_payloads(catalog: dict) -> list[tuple[str, dict]]:
    out: list[tuple[str, dict]] = []
    for name, spec in catalog.items():
        fields = ((spec or {}).get("fields") or {})
        payload = {
            field: fspec["example"]
            for field, fspec in fields.items()
            if isinstance(fspec, dict) and "example" in fspec
        }
        if payload:
            out.append((name, payload))
    return out


def service_bound_payloads(catalog: dict) -> list[tuple[str, dict]]:
    """Each number selector's min and max, on top of that service's examples."""
    examples = {name: payload for name, payload in service_example_payloads(catalog)}
    out: list[tuple[str, dict]] = []
    for name, spec in catalog.items():
        fields = ((spec or {}).get("fields") or {})
        base = dict(examples.get(name) or {})
        for field, fspec in fields.items():
            number = ((fspec or {}).get("selector") or {}).get("number")
            if not isinstance(number, dict):
                continue
            for edge in ("min", "max"):
                if edge in number:
                    out.append((name, {**base, field: number[edge]}))
    return out


def apply_schema(schema, payload) -> tuple[bool, str]:
    if schema is None:
        return True, "no schema"
    try:
        schema(dict(payload))
    except Exception as err:  # noqa: BLE001 - any rejection is the finding
        return False, f"{type(err).__name__}: {err}"
    return True, "accepted"


def _schema_failures(
    schema_by_name: dict, payloads: list[tuple[str, dict]]
) -> list[str]:
    bad: list[str] = []
    for name, payload in payloads:
        if name not in schema_by_name:
            bad.append(f"{name}: not registered")
            continue
        ok, why = apply_schema(schema_by_name[name], payload)
        if not ok:
            bad.append(f"{name}: {why}")
    return bad


def check_a5_service_examples(checks: Checks, schema_by_name: dict, catalog: dict) -> None:
    payloads = service_example_payloads(catalog)
    if not payloads:
        checks.check("a5:service_examples", False, "catalog has no examples")
        return
    bad = _schema_failures(schema_by_name, payloads)
    checks.check(
        "a5:service_examples",
        not bad,
        (
            f"{len(payloads)} example(s) accepted"
            if not bad
            else f"{len(bad)} example(s) rejected: {bad[:4]}"
        ),
    )


def check_a5_service_bounds(checks: Checks, schema_by_name: dict, catalog: dict) -> None:
    payloads = service_bound_payloads(catalog)
    if not payloads:
        checks.check("a5:service_bounds", False, "catalog has no number bounds")
        return
    bad = _schema_failures(schema_by_name, payloads)
    checks.check(
        "a5:service_bounds",
        not bad,
        (
            f"{len(payloads)} bound(s) accepted"
            if not bad
            else f"{len(bad)} bound(s) rejected: {bad[:4]}"
        ),
    )


def stored_effective_bytes(data, options) -> bytes:
    """Effective config, None treated as absent -- so a first save that writes
    ``None`` onto an empty optional slot is not a wipe, and #542's wipe of a
    stored ``external_heat_entity`` still moves the bytes.
    """
    merged = {**dict(data or {}), **dict(options or {})}
    cleaned = {key: value for key, value in merged.items() if value is not None}
    return json.dumps(
        cleaned, sort_keys=True, default=str, separators=(",", ":")
    ).encode()


def check_a5_byte_unchanged(checks: Checks, before: bytes, after: bytes) -> None:
    checks.check(
        "a5:byte_unchanged",
        before == after,
        (
            f"{len(before)}B identical"
            if before == after
            else f"stored bytes moved: before={len(before)}B after={len(after)}B"
        ),
    )


def check_a5_pages(checks: Checks, results: list, expected: tuple[str, ...] | list[str]) -> None:
    """Every walked step saved or returned a menu; none raised; the set is complete."""
    kinds = []
    raised = []
    walked = []
    for row in results:
        step = row.get("step")
        kind = row.get("kind")
        walked.append(step)
        kinds.append(f"{step}:{kind}")
        if kind == "raise" or row.get("raised"):
            raised.append(f"{step}:{row.get('detail') or kind}")
    missing = [step for step in expected if step not in walked]
    extra = [step for step in walked if step not in expected]
    bad_kind = [item for item in kinds if not item.endswith(":save") and not item.endswith(":menu")]
    checks.check(
        "a5:pages_ok",
        bool(results)
        and not raised
        and not missing
        and not extra
        and not bad_kind,
        (
            f"{len(walked)} step(s) save-or-menu"
            if results and not raised and not missing and not extra and not bad_kind
            else (
                f"raised={raised[:3]} missing={missing[:6]} extra={extra[:4]} "
                f"not-save-or-menu={bad_kind[:4]}"
            )
        ),
    )


def option_resubmit(step: str, current: dict) -> dict:
    """Untouched values this page owns. ``setup_overview`` saves nothing."""
    if step == "setup_overview":
        return {}
    cf = _prod_mod("config_flow")
    const = _prod_mod("const")
    out: dict = {}
    for row in cf._page_rows(step, current):
        if row.default is cf._DYNAMIC:
            continue
        value = current.get(row.key)
        if value is not None:
            out[row.key] = value
    out[const.CONF_AFTER_SAVE] = const.AFTER_SAVE_CLOSE
    return out


def check_a8_register_once(
    checks: Checks, registered: list[str] | set[str] | tuple[str, ...], catalog: set[str] | frozenset[str]
) -> None:
    names = set(registered)
    want = set(catalog)
    checks.check(
        "a8:register_once",
        names == want,
        f"{len(names)} registered after two entries; catalog {len(want)}; "
        f"extra={sorted(names - want)}; missing={sorted(want - names)}",
    )


def check_a8_deregister(
    checks: Checks, registered: list[str] | set[str] | tuple[str, ...], catalog: set[str] | frozenset[str]
) -> None:
    """After both entries unload: no leftover per-entry names; catalog remains.

    Literal 0 would refuse action-setup. ``registered == catalog`` is the
    issue's "0 remain" for extras, not a domain teardown this integration
    does not have.
    """
    names = set(registered)
    want = set(catalog)
    checks.check(
        "a8:deregister",
        names == want,
        f"{len(names)} registered after unload; catalog {len(want)}; "
        f"extra={sorted(names - want)}; missing={sorted(want - names)}",
    )


def check_a8_already_configured(checks: Checks, reason: str | None) -> None:
    checks.check(
        "a8:already_configured",
        reason == "already_configured",
        f"duplicate setup aborted as {reason!r}",
    )


def _is_loaded(state) -> bool:
    if state is None:
        return False
    name = getattr(state, "value", None) or getattr(state, "name", None) or state
    return str(name).split(".")[-1].lower() == "loaded"


def check_a9_reload_loaded(checks: Checks, states: list) -> None:
    loaded = [_is_loaded(state) for state in states]
    checks.check(
        "a9:reload_loaded",
        len(states) >= A9_RELOADS and all(loaded),
        f"{sum(loaded)} of {len(states)} reload(s) loaded (need {A9_RELOADS})",
    )


def check_a9_roster_unchanged(
    checks: Checks, before: list[str] | tuple[str, ...], after: list[str] | tuple[str, ...]
) -> None:
    left, right = list(before), list(after)
    checks.check(
        "a9:roster_unchanged",
        left == right,
        (
            f"{len(left)} id(s) unchanged"
            if left == right
            else (
                f"before={len(left)} after={len(right)} "
                f"only_before={sorted(set(left) - set(right))[:4]} "
                f"only_after={sorted(set(right) - set(left))[:4]}"
            )
        ),
    )


def series_grew(series: list[int] | tuple[int, ...]) -> bool:
    """Growth above the first sample. A dip is not growth (#540 shipped ``[1,0,1,1]``)."""
    if not series:
        return True
    return max(series) > series[0]


def check_a9_no_growth(
    checks: Checks,
    tasks: list[int] | tuple[int, ...],
    listeners: list[int] | tuple[int, ...],
    stop: list[int] | tuple[int, ...],
) -> None:
    """Ceiling is the first sample, not zero.

    Zero would re-record whenever HA's own bookkeeping or the standing STOP
    reap (#540) moves. A9 stays partial for leaks only visible as long-horizon
    growth (debouncer, in-flight refresh, MQTT). The #540 neutered series
    ``[1,1,2,3]`` fails; shipped ``[1,0,1,1]`` does not.
    """
    grew = (
        not tasks
        or not listeners
        or not stop
        or series_grew(tasks)
        or series_grew(listeners)
        or series_grew(stop)
    )
    ceiling = (
        f"ceiling tasks={tasks[0] if tasks else None} "
        f"listeners={listeners[0] if listeners else None} "
        f"stop={stop[0] if stop else None}; "
        f"max t/l/s="
        f"{max(tasks) if tasks else None}/"
        f"{max(listeners) if listeners else None}/"
        f"{max(stop) if stop else None}"
    )
    checks.check("a9:no_growth", not grew, ceiling)


def _flow_mapping(result) -> dict:
    if isinstance(result, dict):
        return result
    return {
        "type": getattr(result, "type", None),
        "flow_id": getattr(result, "flow_id", None),
        "reason": getattr(result, "reason", None),
        "step_id": getattr(result, "step_id", None),
    }


def _flow_kind(result) -> str:
    raw = _flow_mapping(result).get("type")
    name = getattr(raw, "value", None) or getattr(raw, "name", None) or raw
    name = str(name).split(".")[-1].lower()
    if name in ("create_entry", "createentry"):
        return "save"
    if name in ("menu", "form", "abort", "raise"):
        return name
    return name


def _flow_id(result) -> str:
    return _flow_mapping(result)["flow_id"]


def _flow_reason(result) -> str | None:
    return _flow_mapping(result).get("reason")


def domain_service_names(hass) -> list[str]:
    services = hass.services.async_services()
    return sorted(services.get(PACKAGE_NAME, {}) or {})


def domain_service_schemas(hass) -> dict:
    services = hass.services.async_services().get(PACKAGE_NAME, {}) or {}
    return {name: getattr(svc, "schema", None) for name, svc in services.items()}


def _bus_listener_count(hass, event: str | None = None) -> int:
    listeners = hass.bus.async_listeners()
    if event is not None:
        value = listeners.get(event, 0)
        return value if isinstance(value, int) else len(value)
    total = 0
    for value in listeners.values():
        total += value if isinstance(value, int) else len(value)
    return total


def _tracked_task_count(hass) -> int:
    loop = getattr(hass, "loop", None)
    try:
        tasks = asyncio.all_tasks(loop) if loop is not None else asyncio.all_tasks()
    except RuntimeError:
        return 0
    return sum(1 for task in tasks if not task.done())


def _owned_roster(hass, entry) -> list[str]:
    from homeassistant.helpers import entity_registry as er

    registry = er.async_get(hass)
    return sorted(
        item.entity_id
        for item in er.async_entries_for_config_entry(registry, entry.entry_id)
    )


def _growth_snapshot(hass) -> tuple[int, int, int]:
    from homeassistant.const import EVENT_HOMEASSISTANT_STOP

    return (
        _tracked_task_count(hass),
        _bus_listener_count(hass),
        _bus_listener_count(hass, EVENT_HOMEASSISTANT_STOP),
    )


async def _async_open_options_step(hass, entry, step: str, advanced: frozenset[str]):
    result = await hass.config_entries.options.async_init(entry.entry_id)
    if step == "init":
        return result
    if step == "advanced" or step in advanced:
        result = await hass.config_entries.options.async_configure(
            _flow_id(result), {"next_step_id": "advanced"}
        )
        if step == "advanced":
            return result
    return await hass.config_entries.options.async_configure(
        _flow_id(result), {"next_step_id": step}
    )


async def _async_check_a5_options(checks: Checks, hass, entry) -> None:
    cf = _prod_mod("config_flow")
    expected = option_step_ids(cf._OPTION_PAGES)
    advanced = frozenset(page.step for page in cf._OPTION_PAGES if page.menu == cf._ADVANCED)
    before = stored_effective_bytes(entry.data, entry.options)
    results = []
    for step in expected:
        try:
            result = await _async_open_options_step(hass, entry, step, advanced)
            kind = _flow_kind(result)
            if step not in ("init", "advanced") and kind == "form":
                current = {**dict(entry.data), **dict(entry.options)}
                result = await hass.config_entries.options.async_configure(
                    _flow_id(result), option_resubmit(step, current)
                )
                kind = _flow_kind(result)
                await hass.async_block_till_done()
                entry = hass.config_entries.async_get_entry(entry.entry_id) or entry
            results.append({"step": step, "kind": kind})
        except Exception as err:  # noqa: BLE001 - a raise is the A5 failure
            results.append(
                {"step": step, "kind": "raise", "raised": True, "detail": type(err).__name__}
            )
    check_a5_pages(checks, results, expected)
    after = stored_effective_bytes(entry.data, entry.options)
    check_a5_byte_unchanged(checks, before, after)


def _fail_a5_services(checks: Checks, detail: str) -> None:
    checks.check("a5:service_examples", False, detail)
    checks.check("a5:service_bounds", False, detail)


async def _async_check_a5_services(checks: Checks, hass) -> None:
    try:
        catalog = load_services_catalog()
        schemas = domain_service_schemas(hass)
    except Exception as err:  # noqa: BLE001
        _fail_a5_services(checks, f"{type(err).__name__}: {err}")
        return
    check_a5_service_examples(checks, schemas, catalog)
    check_a5_service_bounds(checks, schemas, catalog)


async def _async_check_a5(checks: Checks, hass, entry) -> None:
    await _async_check_a5_options(checks, hass, entry)
    await _async_check_a5_services(checks, hass)


async def _async_check_a9(checks: Checks, hass, entry):
    tasks = []
    listeners = []
    stop = []
    states = []
    before = _owned_roster(hass, entry)
    snap = _growth_snapshot(hass)
    tasks.append(snap[0])
    listeners.append(snap[1])
    stop.append(snap[2])
    for _ in range(A9_RELOADS):
        await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
        entry = hass.config_entries.async_get_entry(entry.entry_id)
        states.append(getattr(entry, "state", None) if entry is not None else None)
        snap = _growth_snapshot(hass)
        tasks.append(snap[0])
        listeners.append(snap[1])
        stop.append(snap[2])
    check_a9_reload_loaded(checks, states)
    check_a9_roster_unchanged(checks, before, _owned_roster(hass, entry) if entry else [])
    check_a9_no_growth(checks, tasks, listeners, stop)
    return entry


async def _async_duplicate_user_flow(hass, seed) -> str | None:
    data = seed["data"]
    cf = _prod_mod("config_flow")
    result = await hass.config_entries.flow.async_init(
        PACKAGE_NAME, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        _flow_id(result),
        {
            "name": "Duplicate",
            "tibber_token": data["tibber_token"],
            "weather_entity": data["weather_entity"],
        },
    )
    sensors = {key: data[key] for key in cf._IDENTITY_ENTITY_KEYS if data.get(key)}
    result = await hass.config_entries.flow.async_configure(_flow_id(result), sensors)
    return _flow_reason(result)


async def _async_add_second_entry(hass, seed):
    from homeassistant.config_entries import ConfigEntry

    data = dict(seed["data"])
    options = dict(seed["options"])
    if data.get("indoor_temp_entity"):
        data["indoor_temp_entity"] = (
            data.get("outdoor_temp_entity") or "sensor.ci_indoor_temperature_b"
        )
    else:
        data["indoor_temp_entity"] = "sensor.ci_indoor_temperature"
    unique_id = _prod_mod("config_flow").entry_identity(data)
    kwargs = {
        "version": seed["version"],
        "minor_version": 1,
        "domain": PACKAGE_NAME,
        "title": "Nightly second",
        "data": data,
        "options": options,
        "source": "user",
        "unique_id": unique_id,
        "entry_id": A8_SECOND_ENTRY_ID,
    }
    try:
        extra = ConfigEntry(**kwargs)
    except TypeError:
        extra = ConfigEntry(
            entry_id=kwargs["entry_id"],
            version=kwargs["version"],
            domain=kwargs["domain"],
            title=kwargs["title"],
            data=kwargs["data"],
            source=kwargs["source"],
            unique_id=kwargs["unique_id"],
            options=kwargs["options"],
        )
    adder = getattr(hass.config_entries, "async_add", None) or getattr(
        hass.config_entries, "async_add_entry", None
    )
    if adder is None:
        raise RuntimeError("config_entries has no async_add")
    await adder(extra)
    await hass.async_block_till_done()
    return hass.config_entries.async_get_entry(A8_SECOND_ENTRY_ID)


def _fail_a8(checks: Checks, detail: str) -> None:
    checks.check("a8:register_once", False, detail)
    checks.check("a8:deregister", False, detail)
    checks.check("a8:already_configured", False, detail)


async def _async_check_a8(checks: Checks, hass, seed, entry) -> None:
    catalog = documented_service_names()
    try:
        reason = await _async_duplicate_user_flow(hass, seed)
    except Exception as err:  # noqa: BLE001
        reason = f"{type(err).__name__}: {err}"
    check_a8_already_configured(
        checks, reason if reason == "already_configured" else reason
    )
    try:
        second = await _async_add_second_entry(hass, seed)
        if second is None:
            raise RuntimeError("second entry did not register")
        check_a8_register_once(checks, domain_service_names(hass), catalog)
        first_id = seed["entry_id"]
        await hass.config_entries.async_unload(first_id)
        await hass.config_entries.async_unload(A8_SECOND_ENTRY_ID)
        await hass.async_block_till_done()
        check_a8_deregister(checks, domain_service_names(hass), catalog)
    except Exception as err:  # noqa: BLE001
        if "a8:register_once" not in checks.results:
            checks.check("a8:register_once", False, f"{type(err).__name__}: {err}")
        if "a8:deregister" not in checks.results:
            checks.check("a8:deregister", False, f"{type(err).__name__}: {err}")


def _check_a3_published(checks: Checks, hass, entry, *, constructor_defaults: bool) -> None:
    from homeassistant.helpers import entity_registry as er

    registry = er.async_get(hass)
    owned = list(er.async_entries_for_config_entry(registry, entry.entry_id))
    ids = [item.entity_id for item in owned]
    if constructor_defaults:
        records = []
        for item in owned:
            state = hass.states.get(item.entity_id)
            if state is None:
                continue
            records.append(
                {
                    "entity_id": item.entity_id,
                    "state": state.state,
                    "attributes": dict(state.attributes),
                    "device_class": dict(state.attributes).get("device_class"),
                }
            )
        check_a3_no_constructor_defaults(checks, records)
        return
    check_a3_roster(checks, ids)
    dump_items: list[tuple[str, object]] = []
    pairs: list[tuple[str, object, object]] = []
    missing = []
    for item in owned:
        state = hass.states.get(item.entity_id)
        if state is None:
            if getattr(item, "disabled_by", None) is None:
                missing.append(item.entity_id)
            continue
        obj = _state_dump_obj(state)
        dump_items.append((item.entity_id, obj))
        attrs = dict(state.attributes)
        pairs.append((item.entity_id, attrs.get("device_class"), attrs.get("state_class")))
    if missing:
        dump_items.append(("__enabled_without_state__", {"missing": missing, "k": set(missing)}))
    check_a3_orjson(checks, dump_items)
    check_a3_finite(checks, dump_items)
    check_a3_device_class_state_class(checks, pairs)


# ===========================================================================
# The container half
# ===========================================================================


# Cheap at night, dear morning and evening: a curve with something to optimise
# against, and no randomness anywhere, so two runs of this lane differ only by
# the hour they started at.
DIURNAL_PRICE = (
    0.55, 0.50, 0.48, 0.47, 0.50, 0.70, 1.20, 1.60, 1.45, 1.10, 0.90, 0.80,
    0.75, 0.72, 0.78, 0.95, 1.35, 1.70, 1.50, 1.15, 0.95, 0.80, 0.68, 0.60,
)


def _hourly_prices(now: datetime) -> tuple[list[dict], list[dict]]:
    """A deterministic three-day price curve in the Tibber wire shape.

    Starts two hours behind ``now`` so the horizon the optimizer builds is
    fully inside published data rather than inside the learned extrapolation.
    """
    start = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=2)
    entries = [
        {
            "total": DIURNAL_PRICE[(start + timedelta(hours=i)).hour],
            "startsAt": (start + timedelta(hours=i)).isoformat(),
            "level": "NORMAL",
        }
        for i in range(72)
    ]
    return entries[:24], entries[24:]


def _tibber_body(now: datetime) -> bytes:
    today, tomorrow = _hourly_prices(now)
    return json.dumps(
        {
            "data": {
                "viewer": {
                    "homes": [
                        {
                            "currentSubscription": {
                                "priceInfo": {
                                    "current": today[2],
                                    "today": today,
                                    "tomorrow": tomorrow,
                                }
                            }
                        }
                    ]
                }
            }
        }
    ).encode()


def _self_signed(host: str, workdir: Path) -> tuple[Path, Path]:
    """A certificate for ``host``, trusted by appending it to the CA bundle."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, host)])
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(host)]), False)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), True)
        .sign(key, hashes.SHA256())
    )
    cert_path, key_path = workdir / "price.crt", workdir / "price.key"
    pem = cert.public_bytes(serialization.Encoding.PEM)
    cert_path.write_bytes(pem)
    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        )
    )
    import certifi

    with open(certifi.where(), "ab") as bundle:
        bundle.write(b"\n" + pem)
    return cert_path, key_path


def _serve_prices(workdir: Path) -> None:
    """Answer the real Tibber URL from loopback, over real TLS.

    ``--add-host`` points the hostname here; the certificate above is in the
    bundle ``homeassistant.util.ssl`` hands to the shared aiohttp session. So
    ``TIBBER_API_URL``, the session and the TLS handshake are all the
    production ones, and no module constant is monkeypatched.
    """
    import ssl
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    cert, key = _self_signed(TIBBER_HOST, workdir)

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler's name
            self.rfile.read(int(self.headers.get("Content-Length") or 0))
            body = _tibber_body(datetime.now().astimezone())
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args: object) -> None:
            return

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # PROTOCOL_TLS_SERVER still permits TLS 1.0/1.1, which CodeQL flags high
    # (py/insecure-protocol) and which nothing here needs.
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(cert, key)
    server = ThreadingHTTPServer(("127.0.0.1", 443), Handler)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()


def _write_config_entries(seed: dict) -> None:
    """Seed ``.storage/core.config_entries`` in Home Assistant's own format.

    The storage version is read from the installed ``config_entries`` module
    rather than written down, so this lane neither triggers a migration it did
    not mean to nor claims a version newer than the image's.
    """
    from homeassistant import config_entries as ce

    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "created_at": now,
        "data": seed["data"],
        "disabled_by": None,
        "discovery_keys": {},
        "domain": PACKAGE_NAME,
        "entry_id": seed["entry_id"],
        "minor_version": 1,
        "modified_at": now,
        "options": seed["options"],
        "pref_disable_new_entities": False,
        "pref_disable_polling": False,
        "source": "user",
        "subentries": [],
        "title": seed["title"],
        "unique_id": seed.get("unique_id"),
        "version": seed["version"],
    }
    store = Path(IN_CONFIG) / ".storage"
    store.mkdir(parents=True, exist_ok=True)
    (store / "core.config_entries").write_text(
        json.dumps(
            {
                "version": ce.STORAGE_VERSION,
                "minor_version": ce.STORAGE_VERSION_MINOR,
                "key": "core.config_entries",
                "data": {"entries": [entry]},
            },
            indent=1,
        )
    )


def _check_shape(checks: Checks) -> None:
    """The deployment shape, asserted rather than assumed.

    Every check below turns green if the package happens to be importable from
    somewhere else, so the shape is proved before anything is measured -- and
    in particular the inherited ``PYTHONPATH`` is proved unable to resolve
    ``custom_components`` on its own, because that is precisely what #511's
    ``_worker_env`` has to supply and an image that supplied it for free would
    make this lane pass while proving nothing.
    """
    pkg = Path(IN_CONFIG) / PACKAGE_REL
    checks.check(
        "shape:package_at_config_path",
        (pkg / "__init__.py").is_file() and (pkg / "manifest.json").is_file(),
        f"{pkg} is not an integration",
    )
    checks.check(
        "shape:no_tests_sibling",
        not (Path(IN_CONFIG) / "tests").exists()
        and not (pkg.parent / "tests").exists(),
        "a tests/ sibling puts _worker_env on the branch no install takes",
    )
    inherited = [p for p in (os.environ.get("PYTHONPATH") or "").split(os.pathsep) if p]
    masks = [p for p in inherited if (Path(p) / CONFIG_DIR_NAME).is_dir()]
    checks.check(
        "shape:inherited_pythonpath_cannot_mask",
        not masks,
        f"inherited PYTHONPATH already resolves {CONFIG_DIR_NAME}: {masks}",
    )


def _check_contracts(checks: Checks) -> None:
    """Run tests/ha_contract.py against BOTH providers and compare them (#536).

    The gate runs that file with ``PYTHONPATH=tests/hastub`` and it can only
    ever answer "the stub does what this file says". Here the same file runs
    against the genuine package, which is what makes the saying honest -- a
    contract that misreads upstream fails on ``contract:real_provider``, and a
    transcribed roster that has drifted fails on ``contract:probes_agree``.

    Run before Home Assistant boots: it costs a second, it needs nothing set
    up, and a failure here explains any entity failure that follows.
    """
    work = Path(tempfile.mkdtemp(prefix="ha-contract-"))
    real_env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    runs = {
        "real": (real_env, work / "real.json", ["--contracts-only"]),
        "stub": ({**real_env, "PYTHONPATH": IN_HASTUB}, work / "stub.json", []),
    }
    for provider, (env, out, extra) in runs.items():
        completed = subprocess.run(
            [sys.executable, IN_CONTRACT, "--emit-probes", str(out), *extra],
            capture_output=True,
            text=True,
            env=env,
        )
        for line in completed.stdout.splitlines():
            if line[:6] in ("  ok  ", "  FAIL", "  ..  "):
                print("  " + line)
        checks.check(
            f"contract:{provider}_provider",
            completed.returncode == 0 and out.is_file(),
            f"exit {completed.returncode}; "
            + (completed.stdout + completed.stderr).strip()[-600:],
        )
    compared = subprocess.run(
        [
            sys.executable,
            IN_CONTRACT,
            "--compare",
            str(runs["stub"][1]),
            str(runs["real"][1]),
        ],
        capture_output=True,
        text=True,
        env=real_env,
    )
    print(compared.stdout)
    checks.check(
        "contract:probes_agree",
        compared.returncode == 0,
        f"exit {compared.returncode}; " + (compared.stdout + compared.stderr).strip()[-600:],
    )


async def _boot(seed: dict):
    """Boot Home Assistant the way its own entry point does."""
    import dataclasses

    from homeassistant import bootstrap, runner

    wanted = {
        "config_dir": IN_CONFIG,
        "verbose": False,
        "log_rotate_days": None,
        "log_file": str(Path(IN_CONFIG) / LOG_NAME),
        "log_no_color": True,
        "skip_pip": False,
        "recovery_mode": False,
        "debug": False,
        "open_ui": False,
    }
    names = {f.name for f in dataclasses.fields(runner.RuntimeConfig)}
    config = runner.RuntimeConfig(**{k: v for k, v in wanted.items() if k in names})
    _write_config_entries(seed)
    hass = await bootstrap.async_setup_hass(config)
    if hass is not None:
        await hass.async_start()
        await hass.async_block_till_done()
    return hass


async def _await_plan(coordinator, deadline: float) -> None:
    """Wait for the background first solve ``async_setup_entry`` scheduled.

    ``async_config_entry_first_refresh`` deliberately skips the solve, so a
    plan exists only after the deferred refresh has run. Waited for rather
    than forced, because the scheduling is part of what this lane observes;
    one explicit refresh follows if the deadline passes, so a slow runner
    reports a solve failure rather than a timeout.
    """
    import asyncio
    import time

    while time.monotonic() < deadline:
        if getattr(coordinator, "_optimization_result", None) is not None:
            return
        await asyncio.sleep(1.0)
    await coordinator.async_refresh()


def _check_entry(checks: Checks, hass, seed: dict):
    from homeassistant.config_entries import ConfigEntryState

    entry = hass.config_entries.async_get_entry(seed["entry_id"])
    state = getattr(entry, "state", None)
    checks.check(
        "entry:loaded",
        state is ConfigEntryState.LOADED,
        f"no entry {seed['entry_id']}: the seed did not reach the manager"
        if entry is None
        else f"entry state is {state} (reason: {getattr(entry, 'reason', None)})",
    )
    return entry


def _self_gated(hass, entity_id: str) -> bool:
    """Whether the entity narrows its own availability past the coordinator's.

    Derived from the class, never listed. Roughly a third of this roster
    overrides ``available`` to mean "the install has no lower floor / no
    battery / no hot water", and on a defaults-only entry those are
    unavailable because they are supposed to be; pinning today's set of them
    would rot on the next entity added. What must never happen is an entity
    going unavailable because the COORDINATOR failed, and that is exactly the
    set this leaves behind. An entity whose object cannot be found counts as
    NOT self-gated, so an unresolvable one fails rather than disappears.
    """
    from homeassistant.helpers.entity import Entity
    from homeassistant.helpers.entity_component import DATA_INSTANCES
    from homeassistant.helpers.update_coordinator import CoordinatorEntity

    component = hass.data.get(DATA_INSTANCES, {}).get(entity_id.split(".")[0])
    entity = component.get_entity(entity_id) if component is not None else None
    if entity is None:
        return False
    return type(entity).available not in (CoordinatorEntity.available, Entity.available)


def _check_entities(checks: Checks, hass, entry) -> None:
    from homeassistant.helpers import entity_registry as er

    registry = er.async_get(hass)
    registered = er.async_entries_for_config_entry(registry, entry.entry_id)
    # Six sensors set _attr_entity_registry_enabled_default = False. A disabled
    # registry entry has no state object at all, which is the same shape as an
    # entity that failed to add -- so they are excluded here rather than
    # tolerated below, and an ENABLED entity with no state still fails.
    enabled = [e for e in registered if e.disabled_by is None]
    domains = {e.entity_id.split(".")[0] for e in enabled}
    checks.check(
        "entities:registered",
        len(enabled) > 0 and {"sensor", "binary_sensor", "climate"} <= domains,
        f"{len(enabled)} enabled entities across {sorted(domains)}",
    )
    checks.check(
        "entities:coordinator_healthy",
        bool(entry.runtime_data.last_update_success),
        "last_update_success is False: every entity is unavailable at once",
    )
    unavailable = [
        e.entity_id
        for e in enabled
        if (s := hass.states.get(e.entity_id)) is None or s.state == "unavailable"
    ]
    exposed = [e for e in unavailable if not _self_gated(hass, e)]
    print(
        f"  ..   {len(registered)} registered, {len(registered) - len(enabled)} "
        f"disabled by default, {len(unavailable)} unavailable, "
        f"{len(unavailable) - len(exposed)} of those self-gated"
    )
    for item in sorted(registered, key=lambda e: e.entity_id):
        state = hass.states.get(item.entity_id)
        print(f"       {item.entity_id} = {state.state if state else '<no state>'}")
    checks.check(
        "entities:none_unavailable_by_coordinator",
        not exposed,
        f"{len(exposed)} unavailable without gating themselves: {sorted(exposed)[:10]}",
    )


def _check_plan(checks: Checks, hass, entry) -> None:
    """The point of the lane: a plan came out.

    Read from the payload the entities read (``_build_data_dict``) as well as
    from the result object, because #511 left both empty while setup and every
    entity stayed perfectly healthy.
    """
    from homeassistant.helpers import issue_registry as ir

    coordinator = entry.runtime_data
    data = coordinator.data or {}
    result = getattr(coordinator, "_optimization_result", None)
    checks.check(
        "plan:optimization_result",
        result is not None,
        f"no solve completed; solve_failures={getattr(coordinator, '_solve_failures', '?')}",
    )
    checks.check(
        "plan:last_optimization_published",
        data.get("last_optimization") is not None,
        "the payload's last_optimization is the repair notice's em-dash",
    )
    action = data.get("current_action")
    checks.check(
        "plan:current_action_published",
        isinstance(action, dict) and "mode" in action,
        f"current_action={action!r}",
    )
    setpoints = list(getattr(result, "optimal_setpoints", []) or [])
    checks.check(
        "plan:setpoints_non_empty",
        len(setpoints) > 0,
        f"{len(setpoints)} setpoints in the plan",
    )
    raised = {
        key for (domain, key) in ir.async_get(hass).issues if domain == PACKAGE_NAME
    }
    checks.check(
        "plan:no_solve_repair",
        not (raised & SOLVE_REPAIRS),
        f"solve-route repairs raised: {sorted(raised & SOLVE_REPAIRS)}; "
        f"everything raised: {sorted(raised)}",
    )


async def _inside(seed: dict, budget: float) -> int:
    import time

    checks = Checks()
    _check_shape(checks)
    _check_contracts(checks)
    hass = await _boot(seed)
    checks.check("ha:home_assistant_is_real", hass is not None, "bootstrap returned None")
    if hass is None:
        return _emit(checks)
    import homeassistant.core as ha_core

    checks.check(
        "ha:core_running",
        hass.state is ha_core.CoreState.running,
        f"core state is {hass.state}",
    )
    entry = _check_entry(checks, hass, seed)
    if getattr(entry, "runtime_data", None) is not None:
        await _await_plan(entry.runtime_data, time.monotonic() + budget)
        await hass.async_block_till_done()
        _check_entities(checks, hass, entry)
        _check_a3_published(checks, hass, entry, constructor_defaults=False)
        await _async_check_a10_published(checks, hass, entry)
        _check_plan(checks, hass, entry)
        await _async_check_a5(checks, hass, entry)
        entry = await _async_check_a9(checks, hass, entry)
        await _async_check_a8(checks, hass, seed, entry)
    _write_probe_marker(BLOCKING_PROBE_BEGIN)
    _provoke_lazy_on_loop()
    _flush_logs()
    _write_probe_marker(BLOCKING_PROBE_END)
    await hass.async_stop()
    return _emit(checks)


async def _inside_a3e(seed: dict) -> int:
    """Second seed: default install, no thermometer entities (A3(e))."""
    checks = Checks()
    hass = await _boot(seed)
    if hass is None:
        checks.check(
            "a3:no_constructor_defaults",
            False,
            "default-install bootstrap returned None",
        )
        return _emit(checks)
    entry = hass.config_entries.async_get_entry(seed["entry_id"])
    if getattr(entry, "runtime_data", None) is None:
        checks.check(
            "a3:no_constructor_defaults",
            False,
            f"default-install entry {seed['entry_id']} has no runtime_data",
        )
        await hass.async_stop()
        return _emit(checks)
    await hass.async_block_till_done()
    _check_a3_published(checks, hass, entry, constructor_defaults=True)
    await hass.async_stop()
    return _emit(checks)


def _write_probe_marker(mark: str) -> None:
    """Write the probe window bound to stdout and the HA log file."""
    print(mark, flush=True)
    log = Path(IN_CONFIG) / LOG_NAME
    with log.open("a", encoding="utf-8") as fh:
        fh.write(mark + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def _flush_logs() -> None:
    import logging

    for name in ("", "homeassistant", "homeassistant.util.loop"):
        for handler in logging.getLogger(name).handlers:
            handler.flush()


def _provoke_lazy_on_loop() -> None:
    """The package's own synchronous ``_lazy``, via ``__getattr__`` (#588)."""
    pkg = sys.modules.get("custom_components.heatpump_optimizer")
    if pkg is None:
        try:
            import custom_components.heatpump_optimizer as pkg
        except ImportError:
            print("  ..   blocking probe: package not importable", flush=True)
            return
    try:
        pkg.__dict__.pop("HeatPumpOptimizerCoordinator", None)
        getattr(pkg, "HeatPumpOptimizerCoordinator")
    except Exception as exc:
        print(f"  ..   blocking probe raise: {type(exc).__name__}: {exc}", flush=True)


def _emit(checks: Checks) -> int:
    print(MARKER + json.dumps(checks.results), flush=True)
    return 1 if checks.failures() else 0


def _run_inside(args: argparse.Namespace) -> int:
    import asyncio

    seed = json.loads(Path(IN_SEED).read_text())
    _serve_prices(Path(tempfile.mkdtemp()))
    if args.a3e_only:
        return asyncio.run(_inside_a3e(seed))
    return asyncio.run(_inside(seed, args.plan_budget))


# ===========================================================================
# The runner half
# ===========================================================================


def _fixture_defaults(pages: dict) -> dict:
    """Every field's recorded default, as a value.

    ``tests/golden/config_flow.json`` stores each default as ``repr``; a field
    whose default is ``null`` (the entity selectors, mostly) is left out
    entirely so the integration's own fallback applies rather than a literal
    ``None`` the config flow would never have written.
    """
    out: dict = {}
    for page in pages.values():
        for name, spec in page.items():
            if not isinstance(spec, dict) or "selector" not in spec:
                continue
            if spec.get("default") is None:
                continue
            try:
                out[name] = ast.literal_eval(spec["default"])
            except (ValueError, SyntaxError):
                continue
    return out


def _seed_payload(*, thermometers: bool = True) -> dict:
    """The config entry, from the flow's own recorded defaults.

    Driving the nine setup steps is the expensive part of a real-Home-Assistant
    test and it is already paid for: the golden fixture records every page's
    schema, so "the user accepted every default" is a dictionary comprehension
    rather than a UI script. The entity keys the integration reads are then
    pointed at the template entities ``configuration.yaml`` defines, and the
    Tibber token at the local server -- the two things a defaults-only entry
    cannot supply.

    ``thermometers=False`` is A3(e): the shipping flow's default install, no
    thermometer entities. Do not collapse that seed into the thermometer-seeded boot.
    """
    fixture = json.loads((ROOT / "tests" / "golden" / "config_flow.json").read_text())
    options_pages = {k: v for k, v in fixture.items() if not k.startswith("_")}
    initial_pages = {
        k: v for k, v in fixture["_initial"].items() if "menu" not in v
    }
    const = (ROOT / "custom_components" / PACKAGE_NAME / "const.py").read_text()
    version = re.search(r"CONFIG_ENTRY_VERSION:\s*Final\s*=\s*(\d+)", const)
    if version is None:
        raise SystemExit("const.py no longer declares CONFIG_ENTRY_VERSION")
    # The effective configuration is ``{**entry.data, **entry.options}``
    # (``HeatPumpOptimizerOptionsFlow._current``), so OPTIONS WIN. The first
    # run of this lane put these in ``data`` alone and the fixture's own
    # option default -- ``weather.home``, from the FakeEntry golden.py records
    # against -- silently replaced the weather entity the container defines.
    wiring = {
        "tibber_token": "nightly-ha-local",
        "weather_entity": "weather.ci_weather",
        "heat_pump_power_entity": "sensor.ci_heat_pump_power",
        # No broker here, and the topic defaults are non-empty, so a
        # defaults-only entry publishes on every cycle and logs the failure at
        # ERROR. Blanked rather than tolerated: `_publish_ecl110` returns early
        # on two empty topics, which is the install-without-MQTT case.
        "ecl110_command_topic": "",
        "ecl110_displace_set_topic": "",
    }
    if thermometers:
        wiring.update(
            {
                "indoor_temp_entity": "sensor.ci_indoor_temperature",
                "outdoor_temp_entity": "sensor.ci_outdoor_temperature",
                "dhw_temp_entity": "sensor.ci_dhw_temperature",
            }
        )
    data = _fixture_defaults(initial_pages)
    data.update({"name": "CI"})
    data.update(wiring)
    options = {**_fixture_defaults(options_pages), **wiring}
    if not thermometers:
        for key in THERMOMETER_KEYS:
            data.pop(key, None)
            options.pop(key, None)
    return {
        # A well-formed ULID: Home Assistant generates entry ids with one and
        # a stray I, L, O or U here is a shape no installation has.
        "entry_id": "01JHPA9NGHTHACNTNR00000001",
        "title": "Heat Pump Optimizer",
        "version": int(version.group(1)),
        "data": data,
        "options": options,
        "unique_id": _seed_unique_id(data),
    }


def _seed_unique_id(data: dict) -> str:
    """``entry_identity`` of the seed; A8's already-configured abort needs it."""
    tests_dir = str(Path(__file__).resolve().parent)
    cc = str(ROOT / "custom_components")
    stub = str(Path(tests_dir) / "hastub")
    for path in (stub, tests_dir, cc):
        if path not in sys.path:
            sys.path.insert(0, path)
    from heatpump_optimizer.config_flow import entry_identity

    return entry_identity(data)


def _forecast_literal(now: datetime) -> str:
    """A 48-hour hourly forecast, written into the template weather entity."""
    start = now.replace(minute=0, second=0, microsecond=0)
    rows = []
    for i in range(48):
        at = start + timedelta(hours=i)
        temp = -1.0 if 0 <= at.hour < 8 else 3.0
        rows.append(
            "{'datetime': '%s', 'condition': 'cloudy', 'temperature': %s, "
            "'wind_speed': 3.0, 'precipitation': 0.0}" % (at.isoformat(), temp)
        )
    return "[" + ", ".join(rows) + "]"


CONFIGURATION_YAML = """\
# Minimal, offline, and deliberately not `default_config`: every component
# here is one the integration reaches. The template entities stand in for the
# house sensors a real entry points at.
homeassistant:
  name: Nightly HA
  latitude: 59.33
  longitude: 18.07
  elevation: 20
  unit_system: metric
  time_zone: Europe/Stockholm
  currency: SEK

http:

logger:
  default: warning
  logs:
    custom_components.heatpump_optimizer: debug

template:
  - sensor:
      - name: "CI indoor temperature"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
        state: "21.2"
      - name: "CI outdoor temperature"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
        state: "1.5"
      - name: "CI DHW temperature"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
        state: "48.0"
      - name: "CI heat pump power"
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        state: "1200"
  # Trigger-based on purpose: a plain template weather entity renders
  # condition and temperature but leaves forecast_hourly_template empty, and
  # `weather.get_forecasts` then returns [] with nothing logged. The start
  # trigger fires inside hass.async_start(), before the solve this lane waits
  # for.
  - trigger:
      - platform: homeassistant
        event: start
      - platform: time_pattern
        minutes: "/5"
    weather:
      - name: "CI weather"
        condition_template: "cloudy"
        temperature_template: "{{ 1.5 }}"
        temperature_unit: "°C"
        humidity_template: "{{ 75 }}"
        forecast_hourly_template: "{{ FORECAST }}"
"""


def _stage(workdir: Path, *, thermometers: bool = True) -> tuple[Path, Path]:
    """Build the two mounts: a config directory, and the driver's own dir.

    The package is copied from the tracked tree file by file -- never the
    working directory -- so an untracked stray cannot make the container pass,
    and nothing but the package lands under ``custom_components``.
    """
    config = workdir / "config"
    driver = workdir / "opt"
    (config / CONFIG_DIR_NAME).mkdir(parents=True)
    driver.mkdir()
    listed = subprocess.run(
        ["git", "ls-files", f"{PACKAGE_REL}/"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    if not listed:
        raise SystemExit(f"no tracked files under {PACKAGE_REL}/")
    for rel in listed:
        dest = config / CONFIG_DIR_NAME / Path(rel).relative_to(CONFIG_DIR_NAME)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
    yaml = CONFIGURATION_YAML.replace(
        "FORECAST", _forecast_literal(datetime.now(timezone.utc))
    )
    (config / "configuration.yaml").write_text(yaml)
    shutil.copy2(Path(__file__).resolve(), driver / "nightly_ha.py")
    (driver / "seed.json").write_text(
        json.dumps(_seed_payload(thermometers=thermometers), indent=1)
    )
    (driver / ROSTER_NAME).write_text(json.dumps(load_committed_roster()))
    # #536: the contract module and the stub it speaks about, mounted beside
    # the driver rather than under /config -- nothing here may become a
    # `tests/` sibling of the package, which is the branch of _worker_env no
    # installation takes and which `shape:no_tests_sibling` exists to refuse.
    shutil.copy2(ROOT / "tests" / "ha_contract.py", driver / "ha_contract.py")
    shutil.copytree(ROOT / "tests" / "hastub", driver / "hastub")
    return config, driver


def _docker(
    image: str,
    config: Path,
    driver: Path,
    budget: float,
    timeout: float,
    extra: list[str] | None = None,
):
    command = [
        "docker", "run", "--rm",
        "--add-host", f"{TIBBER_HOST}:127.0.0.1",
        "-e", "TZ=Europe/Stockholm",
        "-v", f"{config}:{IN_CONFIG}",
        "-v", f"{driver}:{IN_DRIVER_DIR}:ro",
        "--entrypoint", "python3",
        image,
        f"{IN_DRIVER_DIR}/nightly_ha.py", "--inside",
        "--plan-budget", str(budget),
        *(extra or ()),
    ]
    print("$ " + " ".join(command), flush=True)
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


def _markers(completed) -> list[str]:
    return [
        line[len(MARKER):]
        for line in completed.stdout.splitlines()
        if line.startswith(MARKER)
    ]


def _merge_completed(first, second):
    """One marker carrying the union, so run:all_checks_ran sees both passes."""
    first_markers = _markers(first)
    if len(first_markers) != 1:
        return first
    inside = json.loads(first_markers[0])
    second_markers = _markers(second)
    if len(second_markers) == 1:
        inside.update(json.loads(second_markers[0]))
    body = "\n".join(
        line
        for src in (first.stdout, second.stdout)
        for line in src.splitlines()
        if not line.startswith(MARKER)
    )
    return types.SimpleNamespace(
        stdout=body + "\n" + MARKER + json.dumps(inside) + "\n",
        stderr=(first.stderr or "") + "\n" + (second.stderr or ""),
        returncode=0 if first.returncode == 0 and second.returncode == 0 else 1,
    )


def partition_blocking_probe(chunks: tuple[str, ...] | list[str]) -> tuple[str, str]:
    """Pin half is outside the begin/end window; the probe half is inside.

    Each stream is split on its own. Concatenating the a3e log onto the first
    run's log before the split would put the second setup after the first
    window and hide an a3e offender from the pin.
    """
    pin_parts: list[str] = []
    probe_parts: list[str] = []
    for chunk in chunks:
        if BLOCKING_PROBE_BEGIN in chunk:
            pre, rest = chunk.split(BLOCKING_PROBE_BEGIN, 1)
            pin_parts.append(pre)
            if BLOCKING_PROBE_END in rest:
                mid, post = rest.split(BLOCKING_PROBE_END, 1)
                probe_parts.append(mid)
                pin_parts.append(post)
            else:
                probe_parts.append(rest)
        else:
            pin_parts.append(chunk)
    return "\n".join(pin_parts), "\n".join(probe_parts)


def check_blocking_positive_control(checks: Checks, probe_text: str) -> None:
    found = set(BLOCKING_CALL.findall(probe_text))
    checks.check(
        BLOCKING_POSITIVE_CONTROL,
        bool(found),
        (
            f"{len(found)} report(s) inside the probe window: {sorted(found)}"
            if found
            else "lane regex saw nothing inside the probe window; "
            "cannot tell no-blocking-call from cannot-see (#588)"
        ),
    )


def _scan_pin(checks: Checks, text: str) -> None:
    for name, needle in FORBIDDEN.items():
        hits = [line for line in text.splitlines() if needle in line]
        checks.check(
            name,
            not hits,
            f"{len(hits)} line(s)" + (f", first: {hits[0][:200]}" if hits else ""),
        )
    # A blocking-call report is a WARNING that carries a stack, not an
    # exception, so the stack after one belongs to the pin below rather than
    # to this check -- otherwise #525 would read as an integration crash.
    parts = text.split(TRACEBACK_HEAD)
    ours = [
        block
        for before, block in zip(parts, parts[1:])
        if PACKAGE_NAME in "\n".join(block.splitlines()[:40])
        and BLOCKING_REPORT not in before[-2000:]
    ]
    checks.check(
        "log:no_integration_traceback",
        not ours,
        f"{len(ours)} traceback(s) naming {PACKAGE_NAME}"
        + (f"; first:\n{TRACEBACK_HEAD}{ours[0][:600]}" if ours else ""),
    )
    # The loose anchor's matches are the population the pin is computed over,
    # so a line it claims and `BLOCKING_CALL` cannot parse silently shrinks
    # that population to nothing -- which reads as "no offenders" (#533).
    blamed = {line for line in text.splitlines() if BLOCKING_AT_OURS.search(line)}
    unparsed = sorted(line for line in blamed if not BLOCKING_CALL.search(line))
    checks.check(
        "log:blocking_report_parsed",
        not unparsed,
        f"{len(blamed)} report(s) blame this package, {len(unparsed)} unparsed"
        + (f"; first: {unparsed[0][:300]}" if unparsed else ""),
    )
    found = set(BLOCKING_CALL.findall(text))
    checks.check(
        "log:no_new_blocking_call",
        found <= KNOWN_BLOCKING,
        f"{len(found)} offender(s) seen; "
        f"new: {sorted(found - KNOWN_BLOCKING)}",
    )
    checks.check(
        "log:blocking_pin_not_stale",
        KNOWN_BLOCKING <= found,
        f"{len(KNOWN_BLOCKING)} pinned; "
        f"fixed but still pinned: {sorted(KNOWN_BLOCKING - found)}",
    )


def _scan_streams(checks: Checks, *chunks: str) -> None:
    pin, probe = partition_blocking_probe(chunks)
    _scan_pin(checks, pin)
    check_blocking_positive_control(checks, probe)


def _scan(checks: Checks, text: str) -> None:
    _scan_streams(checks, text)


def _report(
    checks: Checks,
    completed,
    config: Path,
    extra_logs: tuple[str, ...] = (),
) -> int:
    reported = [
        line[len(MARKER):]
        for line in completed.stdout.splitlines()
        if line.startswith(MARKER)
    ]
    checks.check(
        "run:driver_reported",
        len(reported) == 1,
        f"{len(reported)} result markers in the container's output",
    )
    # The container's own check lines, always. Without this a green run says
    # only "ALL 20 checks PASSED" and a reader cannot see WHICH twenty ran --
    # which is the shape of a lane nobody trusts and nobody reads.
    print("--- inside the container ---")
    for line in completed.stdout.splitlines():
        if line[:6] in ("  ok  ", "  FAIL", "  ..  "):
            print(line)
    inside = json.loads(reported[0]) if len(reported) == 1 else {}
    if set(inside) != set(INSIDE_CHECKS):
        missing = sorted(set(INSIDE_CHECKS) - set(inside))
        checks.check("run:exit_status", False, f"checks never ran: {missing}")
    else:
        checks.results.update(inside)
        checks.check(
            "run:exit_status",
            completed.returncode == 0,
            f"the container exited {completed.returncode}",
        )
    log = config / LOG_NAME
    log_text = log.read_text(errors="replace") if log.is_file() else ""
    _scan_streams(
        checks,
        completed.stdout or "",
        completed.stderr or "",
        log_text,
        *extra_logs,
    )
    # Both rosters, by name. A driver that died after two checks already fails
    # above; this is the other half -- a check that stopped being reached, or
    # was renamed, on either side of the container boundary (#533).
    ran = set(checks.results) | {"run:all_checks_ran"}
    want = set(INSIDE_CHECKS) | set(OUTSIDE_CHECKS)
    checks.check(
        "run:all_checks_ran",
        ran == want,
        f"{len(ran)} of {len(want)} ran; missing: {sorted(want - ran)}; "
        f"undeclared: {sorted(ran - want)}",
    )
    failed = checks.failures()
    if failed:
        print("\n--- container output ---")
        print(completed.stdout[-20000:])
        print(completed.stderr[-20000:])
        print(f"\nFAILED: {len(failed)} of {len(checks.results)} checks: {failed}")
        return 1
    print(f"\nALL {len(checks.results)} checks PASSED")
    return 0


def _run_outside(args: argparse.Namespace) -> int:
    checks = Checks()
    # mkdtemp and rmtree(ignore_errors), not TemporaryDirectory: Home Assistant
    # runs as root in the container and leaves root-owned files (blueprints,
    # .storage) in the bind mount that the runner's user cannot remove.
    # `ignore_cleanup_errors=True` does not cover that -- its handler calls
    # _resetperms, whose chmod raises PermissionError outside the ignore path,
    # and the lane reported ALL 20 checks PASSED and then exited 1 (measured,
    # job 101525... of run 34047698688). Cleanup is not a verdict.
    tmp = Path(tempfile.mkdtemp(prefix="nightly-ha-"))
    tmp_default = Path(tempfile.mkdtemp(prefix="nightly-ha-a3e-"))
    try:
        config, driver = _stage(tmp, thermometers=True)
        config_e, driver_e = _stage(tmp_default, thermometers=False)
        try:
            first = _docker(
                args.image, config, driver, args.plan_budget, args.timeout
            )
            second = _docker(
                args.image, config_e, driver_e, args.plan_budget, args.timeout,
                extra=["--a3e-only"],
            )
        except subprocess.TimeoutExpired:
            checks.check("run:driver_reported", False, f"no result after {args.timeout}s")
            return 1
        extra_logs = ()
        log_e = config_e / LOG_NAME
        if log_e.is_file():
            extra_logs = (log_e.read_text(errors="replace"),)
        return _report(
            checks, _merge_completed(first, second), config, extra_logs=extra_logs
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(tmp_default, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default="homeassistant/home-assistant:stable")
    parser.add_argument("--inside", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--a3e-only", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--plan-budget", type=float, default=240.0)
    parser.add_argument("--timeout", type=float, default=1500.0)
    args = parser.parse_args(argv)
    return _run_inside(args) if args.inside else _run_outside(args)


if __name__ == "__main__":
    sys.exit(main())

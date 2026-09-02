#!/usr/bin/env python3
"""Entity organisation and typing hygiene: the B4 numbers, before and after.

Audit round 1, fix group B4 (issues #173 #174 #175 #176 #177 #178 #179;
register rows D8-01, D8-03, D8-04, D8-05, D8-06, D7-06, D4-10).

What it measures (one line each; every number is an exact count, tolerance 0):

  numpy_leaves            leaves of ``native_value`` / ``extra_state_attributes``
                          that are numpy objects, summed over every sensor of
                          every scenario                               [D8-01]
  numpy_leaking_sensors   distinct sensors with at least one such leaf [D8-01]
  dhw_prefixes            distinct object-id prefixes (the first word after
                          ``heat_pump_optimizer_``) among the sensors whose
                          unique-id key starts with ``dhw``            [D8-03]
  stat_kind_categories    distinct ``entity_category`` values across the
                          sensors that publish a ``stat_kind`` attribute [D8-04]
  accuracy_waits          1 if ``PredictionAccuracySensor`` is unavailable and
                          carries a ``waiting_for`` code on a coordinator that
                          has scored no interval yet; 0 if it publishes
                          Unknown instead                              [D8-05]
  disabled_not_diagnostic disabled-by-default sensors whose entity_category
                          is not DIAGNOSTIC                            [D8-06]
  sensors / diagnostic / disabled   the D4-10 counts                   [D4-10]
  dead_symbols            module-level symbols of the package (functions,
                          classes, constants) with zero references in any code
                          file of the repository outside their own definition
                          and no dynamic route to them, where a dynamic route
                          is a ``getattr(<module>, f"PREFIX{...}")`` whose
                          literal prefix matches the name. Names with a
                          dynamic route are reported as ``dynamic_rescued``
                          (the four CONF keys the round-1 judge rescued with a
                          runtime sentinel) and never as dead          [D7-06]

Command, from the repository root:

    PYTHONPATH=tests/hastub python tools/audit/round1/B4/entity_hygiene.py

The sensors are constructed through the real ``sensor.async_setup_entry``
over a real ``HeatPumpOptimizerCoordinator`` for each of the five topologies
of ``tests/golden.py:coordinator_scenarios()``, with the same injected 48 h of
prices and forecasts as ``tests/golden.py:_capture_coordinator`` and, on top
of that, one real solve per topology so the schedule, the current action and
the plan views are populated: the golden capture never solves, and an empty
schedule cannot leak anything. The clock is frozen at ``golden.START``.

Expected at the baseline, origin/main b4d08f7 (v6.2.14), Apple M1 8 GB:
  numpy_leaves=100 numpy_leaking_sensors=1 dhw_prefixes=3 stat_kind_categories=2
  accuracy_waits=0 disabled_not_diagnostic=2 sensors=55 diagnostic=10
  disabled=6 dead_symbols=5 dynamic_rescued=4
After the B4 fix:
  numpy_leaves=0 numpy_leaking_sensors=0 dhw_prefixes=1 stat_kind_categories=1
  accuracy_waits=1 disabled_not_diagnostic=0 sensors=55 diagnostic=15
  disabled=6 dead_symbols=0 dynamic_rescued=4

Instrumented symbols: ``sensor.async_setup_entry`` (construction); every
sensor's ``native_value`` and ``extra_state_attributes``, i.e. the published
boundary that ``HeatPumpOptimizerSensorBase.__init_subclass__`` wraps;
``PredictionAccuracySensor.available``; the class attributes
``_attr_entity_category`` and ``_attr_entity_registry_enabled_default``; and
the package's module ASTs. Perturbations under which each number must move:
deleting the ``np.generic`` conversion in ``sensor._finite`` raises
numpy_leaves above 0; re-adding ``EntityCategory.DIAGNOSTIC`` to
``PlanNarrativeSensor`` raises stat_kind_categories to 2; reverting one
``dhw_`` translation key raises dhw_prefixes to 2; removing
``_WaitsForEvidenceMixin`` from ``PredictionAccuracySensor`` drops
accuracy_waits to 0; removing ``EntityCategory.DIAGNOSTIC`` from an ECL110
sensor raises disabled_not_diagnostic; restoring any of the five deleted
symbols raises dead_symbols by one.

Writes nothing. Nothing here is a timing, but the contract's thread_factor,
load1 and swapins lines are printed for completeness (``ru_nswap`` is always
0 on macOS).
"""
from __future__ import annotations

import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import ast
import asyncio
import re
import resource
import sys
import time
from collections import Counter, defaultdict
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np

import golden  # noqa: E402  tests/golden.py: coordinator_scenarios(), START
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.helpers.entity import EntityCategory  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import const, sensor  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

PACKAGE = Path("custom_components/heatpump_optimizer")
START = golden.START

_cpu0 = time.process_time()
_thread0 = time.thread_time()


# ---------------------------------------------------------------------------
# A solved coordinator per topology
# ---------------------------------------------------------------------------


def solved_coordinator(config: dict):
    """``tests/golden.py:_capture_coordinator``'s coordinator, plus one solve."""
    hass = FakeHass()
    entry = FakeEntry(data=config)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (START + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]
    horizon = coord._forecast_arrays()
    state, optimizer = coord._solve_snapshot()
    result = optimizer.optimize(
        state,
        horizon.prices,
        horizon.outdoor_temps,
        horizon.wind_speeds,
        horizon.precipitation,
        horizon.solar_radiation,
        START,
        horizon.price_known,
        horizon.pv_surplus,
    )
    coord._optimization_result = result
    coord._current_action = optimizer.get_current_action(result, START)
    coord.data = coord._build_data_dict()
    return hass, entry, coord


def construct(hass, entry, coord) -> list:
    """Every sensor the platform adds, through the real ``async_setup_entry``."""
    added: list = []
    hass.data.setdefault(const.DOMAIN, {})[entry.entry_id] = coord
    asyncio.run(sensor.async_setup_entry(hass, entry, added.extend))
    return added


# ---------------------------------------------------------------------------
# Leaf walkers
# ---------------------------------------------------------------------------


def numpy_leaves(value, path: str, found: list[str]) -> int:
    if isinstance(value, (np.generic, np.ndarray)):
        found.append(f"{path}={type(value).__name__}")
        return 1
    if isinstance(value, dict):
        return sum(numpy_leaves(v, f"{path}.{k}", found) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return sum(
            numpy_leaves(v, f"{path}[{i}]", found) for i, v in enumerate(value)
        )
    return 0


# ---------------------------------------------------------------------------
# Dead symbols by AST reachability
# ---------------------------------------------------------------------------

#: Names Home Assistant (or Python) calls without any reference in this
#: repository's code. A module-level name in this set is never "dead".
FRAMEWORK_NAMES = {
    "async_setup",
    "async_setup_entry",
    "async_unload_entry",
    "async_migrate_entry",
    "async_remove_entry",
    "async_reload_entry",
    "async_get_options_flow",
    "async_get_config_entry_diagnostics",
}

CODE_GLOBS = (
    "tests/**/*.py",
    "tests/**/*.mjs",
    "custom_components/**/*.js",
    "custom_components/**/*.json",
    "custom_components/**/*.yaml",
    ".github/**/*.yml",
)


def dead_symbols() -> tuple[list[tuple[str, int, str]], list[tuple[str, int, str]]]:
    files = sorted(PACKAGE.glob("*.py"))
    trees = {f: ast.parse(f.read_text()) for f in files}

    refs: Counter[str] = Counter()
    dynamic_prefixes: set[str] = set()
    for tree in trees.values():
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                refs[node.id] += 1
            elif isinstance(node, ast.Attribute):
                refs[node.attr] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                # ``from .x import name`` is an alias node, not a Name.
                for alias in node.names:
                    refs[alias.name.rsplit(".", 1)[-1]] += 1
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "getattr"
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.JoinedStr)
                and node.args[1].values
                and isinstance(node.args[1].values[0], ast.Constant)
            ):
                dynamic_prefixes.add(str(node.args[1].values[0].value))

    definitions: list[tuple[str, int, str, bool]] = []
    for f, tree in trees.items():
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                definitions.append((f.name, node.lineno, node.name, False))
            elif isinstance(node, ast.ClassDef):
                # ``class X(ConfigFlow, domain=DOMAIN)``: registered by the
                # framework through the keyword, never by name.
                definitions.append((f.name, node.lineno, node.name, bool(node.keywords)))
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        definitions.append((f.name, node.lineno, target.id, False))
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                definitions.append((f.name, node.lineno, node.target.id, False))

    # References from the rest of the repository's code. Python files are
    # parsed and only ``Name`` / ``Attribute`` / import-alias nodes count: a string literal
    # naming a symbol (``hasattr(const, "X")`` in a test that pins a deletion,
    # a docstring) is not a use. Everything else is a word-boundary grep.
    other_refs: Counter[str] = Counter()
    other_text = []
    for pattern in CODE_GLOBS:
        for p in Path(".").glob(pattern):
            if PACKAGE in p.parents and p.suffix == ".py":
                continue
            try:
                text = p.read_text()
            except (UnicodeDecodeError, OSError):
                continue
            if p.suffix == ".py":
                try:
                    tree = ast.parse(text)
                except SyntaxError:
                    other_text.append(text)
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name):
                        other_refs[node.id] += 1
                    elif isinstance(node, ast.Attribute):
                        other_refs[node.attr] += 1
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        for alias in node.names:
                            other_refs[alias.name.rsplit(".", 1)[-1]] += 1
            else:
                other_text.append(text)
    other_blob = "\n".join(other_text)

    dead: list[tuple[str, int, str]] = []
    rescued: list[tuple[str, int, str]] = []
    for fname, lineno, name, framework_registered in definitions:
        if framework_registered or name in FRAMEWORK_NAMES:
            continue
        if name.startswith("__") and name.endswith("__"):
            continue
        # An Assign's own target is one Name node; a def's name is none.
        own = 1 if _is_assignment(trees, fname, lineno, name) else 0
        if refs[name] - own > 0:
            continue
        if other_refs[name]:
            continue
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", other_blob):
            continue
        if any(name.startswith(prefix) for prefix in dynamic_prefixes):
            rescued.append((fname, lineno, name))
            continue
        dead.append((fname, lineno, name))
    return dead, rescued


def _is_assignment(trees, fname, lineno, name) -> bool:
    for f, tree in trees.items():
        if f.name != fname:
            continue
        for node in tree.body:
            if getattr(node, "lineno", None) != lineno:
                continue
            if isinstance(node, ast.Assign):
                return any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
            if isinstance(node, ast.AnnAssign):
                return isinstance(node.target, ast.Name) and node.target.id == name
    return False


# ---------------------------------------------------------------------------
# The measurement
# ---------------------------------------------------------------------------


def main() -> int:
    scenarios = golden.coordinator_scenarios()
    total_leaves = 0
    leaking: dict[str, int] = defaultdict(int)
    examples: list[str] = []
    all_sensors: list = []
    accuracy_waits = None

    dt_util.freeze(START)
    try:
        for name, config in scenarios.items():
            hass, entry, coord = solved_coordinator(config)
            sensors = construct(hass, entry, coord)
            all_sensors = sensors
            steps = len(coord.data.get("schedule") or [])
            scenario_leaves = 0
            for s in sensors:
                found: list[str] = []
                n = numpy_leaves(s.native_value, f"{s._key}.state", found)
                n += numpy_leaves(
                    getattr(s, "extra_state_attributes", None),
                    f"{s._key}.attributes",
                    found,
                )
                if n:
                    leaking[s._key] += n
                    scenario_leaves += n
                    if len(examples) < 6:
                        examples.append(f"{name}: {found[0]}")
            total_leaves += scenario_leaves
            print(
                f"scenario {name}: schedule_steps={steps} numpy_leaves={scenario_leaves}"
            )
            if accuracy_waits is None:
                acc = next(s for s in sensors if s._key == "prediction_accuracy")
                mae = (coord.data.get("accuracy") or {}).get("temperature_mae")
                waits = (not acc.available) and (
                    acc.extra_state_attributes.get("waiting_for") is not None
                )
                print(
                    f"prediction_accuracy on a fresh coordinator: temperature_mae="
                    f"{mae!r} available={acc.available} waiting_for="
                    f"{acc.extra_state_attributes.get('waiting_for')!r}"
                )
                accuracy_waits = 1 if waits else 0
    finally:
        dt_util.freeze(None)

    for line in examples:
        print(f"LEAK {line}")
    for key, n in sorted(leaking.items()):
        print(f"LEAKING_SENSOR {key} leaves={n}")

    # D8-03: object-id prefixes of the hot-water domain.
    clusters: dict[str, list[str]] = defaultdict(list)
    for s in all_sensors:
        if not s._key.startswith("dhw"):
            continue
        object_id = s.entity_id.split(".", 1)[1].removeprefix("heat_pump_optimizer_")
        clusters[object_id.split("_", 1)[0]].append(object_id)
    for prefix, ids in sorted(clusters.items()):
        print(f"DHW_PREFIX {prefix}: {sorted(ids)}")

    # D8-04: the stat_kind family's categories.
    family = {
        s._key: getattr(s, "_attr_entity_category", None)
        for s in all_sensors
        if (getattr(s, "extra_state_attributes", None) or {}).get("stat_kind")
    }
    for key, cat in sorted(family.items()):
        print(f"STAT_KIND {key}: entity_category={cat!r}")

    # D8-06 / D4-10: categories and the disabled roster.
    diagnostic = {
        s._key
        for s in all_sensors
        if getattr(s, "_attr_entity_category", None) == EntityCategory.DIAGNOSTIC
    }
    disabled = {
        s._key
        for s in all_sensors
        if getattr(s, "_attr_entity_registry_enabled_default", True) is False
    }
    for key in sorted(disabled - diagnostic):
        print(f"DISABLED_NOT_DIAGNOSTIC {key}")
    print(f"DIAGNOSTIC {sorted(diagnostic)}")
    print(f"DISABLED {sorted(disabled)}")

    # D7-06: dead module-level symbols.
    dead, rescued = dead_symbols()
    for fname, lineno, name in dead:
        print(f"DEAD {fname}:{lineno} {name}")
    for fname, lineno, name in rescued:
        print(f"DYNAMIC_RESCUED {fname}:{lineno} {name}")

    print(f"RESULT numpy_leaves={total_leaves} leaves")
    print(f"RESULT numpy_leaking_sensors={len(leaking)} sensors")
    print(f"RESULT dhw_prefixes={len(clusters)} prefixes")
    print(f"RESULT dhw_sensors={sum(len(v) for v in clusters.values())} sensors")
    print(f"RESULT stat_kind_categories={len(set(family.values()))} categories")
    print(f"RESULT accuracy_waits={accuracy_waits} flag")
    print(f"RESULT disabled_not_diagnostic={len(disabled - diagnostic)} sensors")
    print(f"RESULT sensors={len(all_sensors)} entities")
    print(f"RESULT diagnostic={len(diagnostic)} sensors")
    print(f"RESULT disabled={len(disabled)} sensors")
    print(f"RESULT dead_symbols={len(dead)} symbols")
    print(f"RESULT dynamic_rescued={len(rescued)} symbols")

    cpu = time.process_time() - _cpu0
    thread = time.thread_time() - _thread0
    print(f"RESULT thread_factor={cpu / thread if thread else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

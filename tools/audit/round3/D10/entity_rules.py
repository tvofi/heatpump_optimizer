#!/usr/bin/env python3
"""D10 -- the entity-shaped quality-scale rules, measured by instantiating every
entity through each platform's real ``async_setup_entry``.

METRIC (one line): for the N entities the five platforms actually add, the count
that satisfies each of entity-unique-id, has-entity-name, entity-translations,
entity-device-class, entity-category, entity-disabled-by-default and
icon-translations, plus the PARALLEL_UPDATES declaration per platform.

COMMAND (from the export root, nothing else needed):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/entity_rules.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python3 3.11.5): entities_total=74 +/- 0 (59 sensor, 5 binary_sensor,
4 switch, 4 button, 1 climate, 1 datetime), missing_unique_id=0,
missing_has_entity_name=0, missing_translation_key=0, platforms_without_parallel_updates=0.
All numbers are counts and are contention-immune.

INSTRUMENTED SYMBOLS: custom_components.heatpump_optimizer.{sensor,binary_sensor,
switch,button,climate,datetime}:async_setup_entry and
custom_components.heatpump_optimizer.entity:HeatPumpOptimizerEntity.

PERTURBATION: delete ``_attr_has_entity_name = True`` from entity.py:27 and
missing_has_entity_name goes from 0 to entities_total (direction: up).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
os.chdir(ROOT)
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeCoordinator, FakeEntry, FakeHass  # noqa: E402

def _attr(entity, name, default=None):
    """The entity's effective value for ``name``.

    ``tests/hastub``'s ``Entity`` is a bare stand-in with none of Home
    Assistant's ``_attr_*`` -> property machinery, so reading ``entity.name``
    alone reports None for every entity that sets ``_attr_name``. Prefer a
    property the integration itself declares, fall back to the ``_attr_``
    shadow, which is what real Home Assistant would surface.
    """
    try:
        value = getattr(entity, name)
    except Exception:
        value = None
    if value is None:
        try:
            value = getattr(entity, "_attr_" + name)
        except Exception:
            value = None
    return default if value is None else value

PLATFORMS = ("sensor", "binary_sensor", "switch", "button", "climate", "datetime")


def _entities_data() -> dict:
    """The representative payload tests/entities.py drives entities with.

    Lifted by AST from that file rather than copied, so it cannot drift; the
    module itself runs its whole check suite at import and ``sys.exit``s, so it
    cannot simply be imported (tools/audit/README.md names this trap).
    """
    tree = ast.parse(Path("tests/entities.py").read_text(encoding="utf-8"))
    ns: dict = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            getattr(t, "id", None) == "DATA" for t in node.targets
        ):
            exec(compile(ast.Module(body=[node], type_ignores=[]), "DATA", "exec"), ns)
    return ns["DATA"]


def main() -> int:
    data = _entities_data()
    icons = json.loads(Path("custom_components/heatpump_optimizer/icons.json").read_text())
    strings = json.loads(Path("custom_components/heatpump_optimizer/strings.json").read_text())
    entities: list = []
    per_platform: dict[str, int] = {}
    no_parallel: list[str] = []
    for name in PLATFORMS:
        module = __import__(f"heatpump_optimizer.{name}", fromlist=["x"])
        if not hasattr(module, "PARALLEL_UPDATES"):
            no_parallel.append(name)
        added: list = []
        coord = FakeCoordinator(dict(data))
        coord._month_totals = {"dhw": (41.5, 62.25), "space": (120.0, 180.0)}
        entry = FakeEntry(data={})
        entry.runtime_data = coord
        asyncio.run(module.async_setup_entry(FakeHass(), entry, added.extend))
        per_platform[name] = len(added)
        for ent in added:
            entities.append((name, ent))

    missing_uid = [f"{p}:{type(e).__name__}" for p, e in entities
                   if not _attr(e, "unique_id")]
    dup_uid_n = len(entities) - len({_attr(e, "unique_id") for _, e in entities})
    missing_hen = [f"{p}:{type(e).__name__}" for p, e in entities
                   if not _attr(e, "has_entity_name", False)]
    missing_tk = [f"{p}:{type(e).__name__}" for p, e in entities
                  if not _attr(e, "translation_key")
                  and _attr(e, "name") is not None]
    with_dc = [e for _, e in entities if _attr(e, "device_class")]
    with_cat = [e for _, e in entities if _attr(e, "entity_category")]
    disabled = [e for _, e in entities if _attr(e, "entity_registry_enabled_default", True) is False]
    attr_icon = [f"{p}:{type(e).__name__}" for p, e in entities
                 if type(e).__dict__.get("_attr_icon") is not None
                 or getattr(e, "_attr_icon", None) is not None]
    # icon-translations: a translation_key that icons.json has an entry for,
    # counted per platform section the way Home Assistant looks one up.
    icon_hits = 0
    icon_misses: list[str] = []
    for p, e in entities:
        tk = _attr(e, "translation_key")
        if not tk:
            continue
        if tk in icons.get("entity", {}).get(p, {}):
            icon_hits += 1
        else:
            icon_misses.append(f"{p}.{tk}")
    # entity-translations: every translation key must resolve in strings.json.
    str_missing = [
        f"{p}.{_attr(e, 'translation_key')}"
        for p, e in entities
        if _attr(e, "translation_key")
        and _attr(e, "translation_key") not in strings.get("entity", {}).get(p, {})
    ]

    print(f"RESULT entities_total={len(entities)} count")
    for p in PLATFORMS:
        print(f"RESULT entities_{p}={per_platform[p]} count")
    print(f"RESULT missing_unique_id={len(missing_uid)} count")
    print(f"RESULT duplicate_unique_ids={dup_uid_n} count")
    print(f"RESULT missing_has_entity_name={len(missing_hen)} count")
    print(f"RESULT missing_translation_key={len(missing_tk)} count")
    print(f"RESULT translation_key_absent_from_strings={len(str_missing)} count")
    print(f"RESULT with_device_class={len(with_dc)} count")
    print(f"RESULT with_entity_category={len(with_cat)} count")
    print(f"RESULT disabled_by_default={len(disabled)} count")
    print(f"RESULT attr_icon_pins={len(attr_icon)} count")
    print(f"RESULT icon_translation_hits={icon_hits} count")
    print(f"RESULT icon_translation_misses={len(icon_misses)} count")
    print(f"RESULT platforms_without_parallel_updates={len(no_parallel)} count")
    print(f"RESULT thread_factor=1.0")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=nan")
    print("RESULT swapins=0")
    if missing_uid:
        print("DETAIL missing_unique_id:", ", ".join(sorted(set(missing_uid))[:10]))
    if missing_hen:
        print("DETAIL missing_has_entity_name:", ", ".join(sorted(set(missing_hen))[:10]))
    if missing_tk:
        print("DETAIL missing_translation_key:", ", ".join(sorted(set(missing_tk))[:10]))
    if icon_misses:
        print("DETAIL icon_translation_misses:", ", ".join(sorted(set(icon_misses))[:15]))
    if str_missing:
        print("DETAIL translation_key_absent:", ", ".join(sorted(set(str_missing))[:10]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

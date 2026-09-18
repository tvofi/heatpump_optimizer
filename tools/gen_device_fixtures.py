#!/usr/bin/env python3
"""Generate the device-pre-fill registry fixtures from upstream definitions.

W1067-G7b's source tables (``custom_components/heatpump_optimizer/
device_prefill.py``) say which of a heat-pump integration's entities fill
which option. What that integration actually publishes is not this
repository's to assert, so the fixtures those tables are tested against are
**generated from the upstream definitions at a pinned commit**, never typed.

Honest scope: a fixture proves the mapping against one source's definitions
at one commit. It proves nothing about a live device, and nothing about a
model file this repository has not seen. Drift is noticed when the pin is
bumped: re-run with ``--check`` and a changed upstream fails here, before any
table is re-derived.

    python3 tools/gen_device_fixtures.py --repo ~/tuya_heat_pump --write
    python3 tools/gen_device_fixtures.py --repo ~/tuya_heat_pump --check

The suite never runs either mode: it reads the written fixture only, with no
network and no sibling checkout. ``--check`` is the maintainer's, run at the
recorded commit when a pin moves.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

FIXTURES = pathlib.Path(__file__).resolve().parent.parent / "tests" / "fixtures"

#: The model file each fixture is generated from, at the commit recorded in
#: it. ``slug`` is the device-name slug the coordinator builds from the
#: device name (``coordinator.py``: lowercased, spaces and hyphens to
#: underscores); the fixture uses the model's own product name so the
#: fixture's unique ids read as a real install's.
TUYA_HEAT_PUMP = {
    "fixture": "tuya_heat_pump_000004k4z6.json",
    "repo": "tvofi/tuya_heat_pump",
    "commit": "fda9bed19395267898570d72fe5e9324f523d574",
    "path": "custom_components/tuya_heat_pump/models/000004k4z6.py",
    "platform": "tuya_heat_pump",
    "device_name": "Rotenso Windmi",
    #: ``models/__init__.py`` hands each platform its own table; the platform
    #: modules build ``f"{slug}_{key}"`` from that table's keys.
    "tables": {
        "SENSOR_TYPES": "sensor",
        "BINARY_SENSOR_TYPES": "binary_sensor",
        "SWITCH_TYPES": "switch",
        "NUMBER_TYPES": "number",
        "SELECT_TYPES": "select",
    },
}


def _slug(text: str) -> str:
    """Home Assistant's entity-id slug, and the coordinator's device slug."""
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", text.lower())).strip("_")


def _device_slug(name: str) -> str:
    """The coordinator's own device slug (``coordinator.py``): lowercase,
    spaces and hyphens to underscores, and nothing else touched."""
    return name.lower().replace(" ", "_").replace("-", "_")


def _show(repo: pathlib.Path, commit: str, path: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "show", f"{commit}:{path}"],
        capture_output=True, text=True, check=True,
    ).stdout


def _records(spec: dict, source: str) -> list[dict]:
    """The entity-registry records the model file's tables describe.

    The model files are plain data: module-level dicts and no imports. They
    are executed rather than parsed so a value the upstream computes (a fault
    bitmap, a conversion string) is read as upstream reads it.
    """
    namespace: dict = {}
    exec(compile(source, spec["path"], "exec"), namespace)  # noqa: S102
    slug = _device_slug(spec["device_name"])
    records = []
    for table, domain in spec["tables"].items():
        for key, config in (namespace.get(table) or {}).items():
            name = config.get("name", key)
            records.append({
                "platform": spec["platform"],
                "unique_id": f"{slug}_{key}",
                # has_entity_name is true on every platform there, so Home
                # Assistant prefixes the device name.
                "entity_id": f"{domain}.{slug}_{_slug(name)}",
                "original_name": name,
                "translation_key": config.get("translation_key"),
                "device_class": config.get("device_class"),
                "unit": config.get("unit"),
                "state_class": config.get("state_class"),
            })
    return sorted(records, key=lambda r: r["entity_id"])


def build(spec: dict, repo: pathlib.Path) -> dict:
    return {
        "_generated_by": "tools/gen_device_fixtures.py",
        "upstream_repo": spec["repo"],
        "upstream_commit": spec["commit"],
        "upstream_path": spec["path"],
        "platform": spec["platform"],
        "device_name": spec["device_name"],
        "records": _records(spec, _show(repo, spec["commit"], spec["path"])),
    }


def load(name: str) -> dict:
    """One written fixture. The only entry point the test suite uses."""
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _dump(fixture: dict) -> str:
    return json.dumps(fixture, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=pathlib.Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    failures = 0
    for spec in (TUYA_HEAT_PUMP,):
        target = FIXTURES / spec["fixture"]
        built = _dump(build(spec, args.repo))
        if args.write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(built, encoding="utf-8")
            print(f"wrote {target}")
            continue
        recorded = target.read_text(encoding="utf-8") if target.exists() else ""
        if recorded == built:
            print(f"{spec['fixture']}: matches {spec['repo']} {spec['commit'][:7]}")
        else:
            failures += 1
            print(f"{spec['fixture']}: DIFFERS from {spec['repo']} {spec['commit'][:7]}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

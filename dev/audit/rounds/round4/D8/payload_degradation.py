#!/usr/bin/env python3
"""D8 — every entity against a degraded published payload.

METRIC: with every entity of every platform built through the real
``async_setup_entry`` against a solved all-features payload, the number of
(entity, perturbation) pairs whose ``native_value`` / ``is_on`` /
``extra_state_attributes`` / ``available`` raises instead of returning a
value.  Perturbations, each applied to a fresh copy of the payload:
``None`` payload, ``{}`` payload, and for each of the ~160 published keys in
turn: the key deleted, and the key set to ``None``.

A raise here is not cosmetic: Home Assistant calls these properties on every
state write, logs the traceback each cycle, and the entity stops updating.

COMMAND (from the export root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D8/payload_degradation.py

It also answers the reachability question the raises raise: how many
``<obj>.get("key", <non-None default>)`` call sites in the six platform modules
name a key that the matrix ever publishes as ``None`` (a ``get`` default
applies to an ABSENT key, never to a present ``None``).

EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697, 8-core Apple M1):
    entities=74  keys=164  perturbations=330  probes=24420      (exact)
    raises=4  raise_TypeError=2  raise_AttributeError=2         (exact)
      -- all four on payload states the coordinator cannot produce:
         current_action is never None (initialised {}, only ever assigned a
         dict), and outdoor_temperature is a float field written only under
         `if reading.ok`, which requires `value is not None`.
    get_default_sites=79  get_default_sites_top_level=64         (exact)
    published_keys_none_in_some_cell=24                          (exact)
    get_default_sites_over_a_none_key=0                          (exact)
Counts only; contention-immune; no network.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import ast  # noqa: E402
import copy  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from collections import Counter  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.argv.append("--no-solve")  # entity_matrix is imported, not run

_spec = importlib.util.spec_from_file_location(
    "d8_entity_matrix", "tools/audit/round4/D8/entity_matrix.py"
)
em = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(em)

from homeassistant.util import dt as dt_util  # noqa: E402

from golden import START, coordinator_scenarios  # noqa: E402


def probe_all(ent, platform: str) -> None:
    """Everything Home Assistant reads off an entity on a state write."""
    ent.available
    if platform == "sensor":
        ent.state
        ent.native_value
    elif platform == "binary_sensor":
        ent.is_on
    elif platform == "switch":
        ent.is_on
    elif platform == "climate":
        ent.current_temperature
        ent.target_temperature
        ent.hvac_mode
        ent.hvac_action
    elif platform == "datetime":
        ent.native_value
    getattr(ent, "extra_state_attributes", None)


PLATFORM_FILES = (
    "sensor", "binary_sensor", "button", "climate", "switch", "datetime",
)


def get_default_sites() -> list[tuple[str, int, str, str, str]]:
    """Every ``<obj>.get("literal", <non-None default>)`` in the platforms.

    The reachability question behind the ``none[<key>]`` perturbations: a
    ``dict.get(key, default)`` supplies the default only when the key is
    ABSENT, so a key published as ``None`` walks straight past it.
    """
    sites = []
    for name in PLATFORM_FILES:
        tree = ast.parse(
            Path(f"custom_components/heatpump_optimizer/{name}.py").read_text()
        )
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and len(node.args) == 2
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                default = node.args[1]
                if isinstance(default, ast.Constant) and default.value is None:
                    continue
                sites.append(
                    (
                        name,
                        node.lineno,
                        node.args[0].value,
                        ast.unparse(default),
                        ast.unparse(node.func.value),
                    )
                )
    return sites


def none_keys_over_matrix() -> dict[str, int]:
    """Published top-level keys that are ``None`` in at least one cell."""
    from golden import coordinator_scenarios as _scen

    out: dict[str, int] = {}
    dt_util.freeze(START)
    for topo in _scen().values():
        for overlay in em.FEATURE_OVERLAYS.values():
            hass, entry, coord = em.build_coordinator({**topo, **overlay})
            payload = em.run_cycle(
                coord, hass, offset=0.6, spread=0.5, base_t=-5.0,
                peak=200.0, slot=0, solve=False,
            )
            for key, value in payload.items():
                if value is None:
                    out[key] = out.get(key, 0) + 1
    dt_util.freeze(None)
    return out


def main() -> int:
    dt_util.freeze(START)
    cfg = {
        **coordinator_scenarios()["coord_all_features"],
        **em.FEATURE_OVERLAYS["all"],
    }
    hass, entry, coord = em.build_coordinator(cfg)
    base = dict(
        em.run_cycle(
            coord,
            hass,
            offset=0.6,
            spread=0.5,
            base_t=-5.0,
            peak=200.0,
            slot=0,
            solve=True,
        )
    )

    keys = sorted(base)
    perturbations: list[tuple[str, object]] = [("payload=None", None), ("payload={}", {})]
    for key in keys:
        perturbations.append((f"del[{key}]", ("del", key)))
        perturbations.append((f"none[{key}]", ("none", key)))

    entities: list[tuple[str, object]] = []
    for pname, module in em.PLATFORMS.items():
        for ent in em.collect(module, hass, entry, coord):
            entities.append((pname, ent))

    raises: list[str] = []
    kinds: Counter = Counter()
    probes = 0
    for label, spec in perturbations:
        if spec is None:
            payload = None
        elif spec == {}:
            payload = {}
        else:
            op, key = spec  # type: ignore[misc]
            payload = copy.deepcopy(base)
            if op == "del":
                payload.pop(key, None)
            else:
                payload[key] = None
        coord.data = payload
        for pname, ent in entities:
            probes += 1
            try:
                probe_all(ent, pname)
            except Exception as exc:  # noqa: BLE001
                kinds[f"{type(exc).__name__}"] += 1
                raises.append(f"{label}|{pname}|{em.ident(ent)}|{type(exc).__name__}: {exc}")
    dt_util.freeze(None)

    sites = get_default_sites()
    nones = none_keys_over_matrix()
    top_level = [
        st for st in sites
        if "coordinator.data" in st[4] or st[4] in ("data", "self._data()")
    ]
    exposed = sorted({(st[0], st[1], st[2]) for st in top_level if st[2] in nones})

    out = Path("tools/audit/round4/D8/degradation_detail.json")
    out.write_text(
        json.dumps(
            {
                "raises": raises[:400],
                "kinds": dict(kinds),
                "none_keys": nones,
                "get_default_sites_over_a_none_key": exposed,
            },
            indent=1,
        )
    )

    print(f"RESULT entities={len(entities)} count")
    print(f"RESULT keys={len(keys)} count")
    print(f"RESULT perturbations={len(perturbations)} count")
    print(f"RESULT probes={probes} count")
    print(f"RESULT raises={len(raises)} probes")
    for kind, n in sorted(kinds.items()):
        print(f"RESULT raise_{kind}={n} probes")
    print(f"RESULT get_default_sites={len(sites)} call_sites")
    print(f"RESULT get_default_sites_top_level={len(top_level)} call_sites")
    print(f"RESULT published_keys_none_in_some_cell={len(nones)} keys")
    print(f"RESULT get_default_sites_over_a_none_key={len(exposed)} call_sites")
    print(f"# detail written to {out}")
    # Harness contract (tools/audit/README.md): the three conditions lines.
    # This harness reports COUNTS only -- no wall, CPU or RSS number -- so the
    # thread factor cannot contaminate anything here; the pin is applied
    # anyway, above the numpy import, and stated so a reader need not infer it.
    import resource

    print("RESULT thread_factor=1.00 ratio")
    print("RESULT timing_results_reported=0 count")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""ARCH2-s5 (round 10, D7): one setting, two selectors -- the setup wizard against the options registry.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py [--bump KEY]

Instrumented symbols: ``config_flow:HeatPumpOptimizerConfigFlow.async_step_<page>`` (driven, the
widget objects the flow DELIVERS in its schema are what is counted) and
``config_flow:_OPTION_FIELDS`` (the registry each wizard key also has a row in).

Metrics (count key: the widget object the wizard page's schema delivers, per field):
  wizard_fields     fields the six wizard pages render
  in_registry       of those, keys that also have an ``_OPTION_FIELDS`` row
  spelled_twice     of those, fields whose widget is NOT the registry row's object (built a second time)
  disagree          of those, fields whose selector fingerprint (type + config) differs from every row's
  menu_fallbacks    options-menu fallback labels in code; menu_disagree: those differing from
                    translations/en.json (the label shown when the translation lookup fails)
  golden_equal      1 when golden.capture_config_flow() equals tests/golden/config_flow.json

Perturbation: ``--bump KEY`` multiplies that key's registry max by 2 before driving the flow (a
one-line production edit, simulated on the loaded module). On the baseline, ``--bump
heat_pump_cop_nominal`` moves disagree 0 -> 2 (building_extras and thermal keep their own copy); on
a tree where the wizard reads the registry it stays 0, because the second copy no longer exists.

Counts only: contention-immune. Writes nothing.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402


def repo_root(start):
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


REPO = repo_root(__file__)
sys.path[:0] = [str(REPO / "tests"), str(REPO / "custom_components")]

from harness import FakeHass  # noqa: E402
from heatpump_optimizer import config_flow as cf  # noqa: E402

WIZARD = ("temperature", "building_extras", "thermal", "zones", "dhw", "weather_sensitivity")
#: The other initial-flow form pages, measured with --all: the first two screens and the quick path.
OTHER = ("user", "user_sensors", "quick_setup", "building_describe")


def fingerprint(widget):
    cfg = getattr(widget, "config", None)
    return (type(widget).__name__, tuple(sorted((k, repr(v)) for k, v in dict(cfg or {}).items())))


def bump(key):
    """Double the registry max of ``key`` in place: the one-line edit, applied to the loaded module."""
    rows = [r for r in cf._OPTION_FIELDS if r.key == key]
    assert rows, key
    for r in rows:
        r.widget.config = {**r.widget.config, "max": r.widget.config["max"] * 2}


def _leaves(schema):
    """(marker, widget) for every field, a ``section()``'s fields included."""
    for marker, value in schema.schema.items():
        inner = getattr(value, "schema", None)
        if isinstance(inner, cf.vol.Schema):
            yield from _leaves(inner)
        else:
            yield marker, value


def measure(steps=WIZARD):
    flow = cf.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    out = {"wizard_fields": 0, "in_registry": 0, "spelled_twice": 0, "disagree": 0}
    seats = []
    for step in steps:
        schema = asyncio.run(getattr(flow, f"async_step_{step}")()).get("data_schema")
        for marker, widget in _leaves(schema):
            key = str(marker)
            out["wizard_fields"] += 1
            rows = [r for r in cf._OPTION_FIELDS if r.key == key]
            if not rows:
                continue
            out["in_registry"] += 1
            if any(widget is r.widget for r in rows):
                continue
            out["spelled_twice"] += 1
            seats.append(f"{step}:{key}")
            if all(fingerprint(widget) != fingerprint(r.widget) for r in rows):
                out["disagree"] += 1
                seats.append(f"  DISAGREES {step}:{key}")
    return out, seats


def menus():
    en = json.loads((REPO / "custom_components/heatpump_optimizer/translations/en.json").read_text())
    F = cf.HeatPumpOptimizerOptionsFlow
    n, bad = 0, []
    for menu, steps in (("init", F._TOP_MENU), ("advanced", F._ADVANCED_MENU)):
        for st in steps:
            n += 1
            if F._MENU_LABELS[st] != en["options"]["step"][menu]["menu_options"].get(st):
                bad.append(f"{menu}.{st}: code {F._MENU_LABELS[st]!r} vs en.json "
                           f"{en['options']['step'][menu]['menu_options'].get(st)!r}")
    return n, bad


def golden_equal():
    import golden
    committed = json.loads((REPO / "tests/golden/config_flow.json").read_text())
    return int(json.loads(json.dumps(golden.capture_config_flow(), sort_keys=True)) == committed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bump")
    ap.add_argument("--all", action="store_true", help="also the other initial-flow form pages")
    a = ap.parse_args()
    if a.bump:
        bump(a.bump)
    out, seats = measure()
    for s in seats:
        print(f"  {s}")
    for k, v in out.items():
        print(f"RESULT {k}={v} count")
    if a.all:
        other, oseats = measure(OTHER)
        for s in oseats:
            print(f"  other {s}")
        for k, v in other.items():
            print(f"RESULT other_{k}={v} count")
    n, bad = menus()
    for b in bad:
        print(f"  {b}")
    print(f"RESULT menu_fallbacks={n} count")
    print(f"RESULT menu_disagree={len(bad)} count")
    if not a.bump:
        print(f"RESULT golden_equal={golden_equal()} bool")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""D14 class P6 detector: consumer reads of a key no producer writes, with a silent fallback.

Metric (one line): p6_unproduced_reads = distinct (consumer file:line, key path) lookups on the
payload ``HeatPumpOptimizerCoordinator._build_data_dict`` returns, made while every entity of
every PLATFORM_LIST platform and the diagnostics download is read, whose key is absent from
that payload in EVERY driven cell (topology x cycle) and whose name is written as a key by no
production source line (static literal search), i.e. the reader's fallback is the only value
it ever gets.

Count key: the key the consumer asks the *delivered* payload for (recorded inside a dict
subclass installed as ``coordinator.data``), never a name the harness supplies. A fix that
makes the producer write the key moves the count; a fix that deletes the read moves it too.

Arms:
  A  runtime: the recording payload above, over the five golden coordinator topologies
     (tests/golden.py:coordinator_scenarios), each driven through the real
     _update_current_state + async_run_optimization + _build_data_dict, two cycles.
  B  entity-id references: every ``sensor.heat_pump_optimizer_*``-shaped id written in
     blueprints/, the card (www/*.js) and the package, against the ids the platforms build
     (entity_id attribute, else f"{domain}.heat_pump_optimizer_{translation_key}").
  C  static: getattr/hasattr(obj, "<literal>", default) whose literal no production code
     assigns or defines (a field only a test double writes).

Clean fixture (zero): --self-test builds a tiny producer/consumer pair in memory and checks
the recorder reports only the unproduced key.

Perturbation (one-line production edit, in memory): --perturb deletes the line of
_build_data_dict that writes "heat_pump_power_series"/"house_power_series" (recompiled from the
method's own source; the static producer scan reads the same cut text); the sensor-gap advisor
and the sensor-advisor attribute read both keys, so p6_unproduced_reads goes UP (2 -> 5). This is the re-introduction of
R7 D8-01 (#1460), whose pre-fix tree is 1e4e4b9e^.

Run (repository root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D14/s1/p6_keys.py
  ... p6_keys.py --perturb            (re-introduction; count must rise)
  ... p6_keys.py --self-test          (clean fixture; count must be 0)
  cd <export of 1e4e4b9e^> && PYTHONPATH=tests/hastub python <abs path>/p6_keys.py   (pre-fix tree)
Expected at baseline 1936d5ca: see REPORT.md (exact; counts are deterministic).
Machine: round-9 box B8 (4 cores, 15 GB, Linux, CPython 3.14.0rc2).
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import argparse
import ast
import asyncio
import importlib
import json
import logging
import re
import sys
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--tree", default=".")
ap.add_argument("--perturb", action="store_true")
ap.add_argument("--self-test", action="store_true")
ap.add_argument("--json", default=None)
ARGS = ap.parse_args()
TREE = Path(ARGS.tree).resolve()
# tests/harness.py inserts the RELATIVE paths "tests" and "custom_components", so the package
# measured is always the one under the working directory: measure another tree from its root.
if TREE != Path.cwd().resolve():
    sys.exit(f"run from the tree under measurement: cd {TREE} && PYTHONPATH=tests/hastub python <this file>")
for sub in ("tests/hastub", "tests", "custom_components"):
    sys.path.insert(0, str(TREE / sub))
logging.disable(logging.CRITICAL)
PKG = TREE / "custom_components" / "heatpump_optimizer"

_T0P, _T0T = time.process_time(), time.thread_time()

READS: dict[tuple[str, str], set[str]] = {}   # (site, keypath) -> set(cell)
PRESENT: dict[tuple[str, str], set[str]] = {}
CELL = ["?"]


def _site() -> str:
    f = sys._getframe(2)
    while f is not None:
        fn = f.f_code.co_filename
        if "heatpump_optimizer" in fn and "p6_keys" not in fn:
            return f"{Path(fn).name}:{f.f_lineno}"
        f = f.f_back
    return "?"


class Rec(dict):
    """A dict that records every key looked up on it, and wraps nested dicts."""

    __slots__ = ("_path",)

    def _note(self, key, present):
        if not isinstance(key, str):
            return
        k = (_site(), f"{self._path}{key}")
        (PRESENT if present else READS).setdefault(k, set()).add(CELL[0])

    def _wrap(self, key, v):
        if type(v) is dict:
            w = Rec(v)
            w._path = f"{self._path}{key}."
            return w
        return v

    def get(self, key, default=None):
        present = dict.__contains__(self, key)
        self._note(key, present)
        return self._wrap(key, dict.__getitem__(self, key)) if present else default

    def __getitem__(self, key):
        present = dict.__contains__(self, key)
        self._note(key, present)
        return self._wrap(key, dict.__getitem__(self, key))

    def __contains__(self, key):
        self._note(key, dict.__contains__(self, key))
        return dict.__contains__(self, key)


def rec(d, path=""):
    r = Rec(d)
    r._path = path
    return r


# ---------------------------------------------------------------------------
def self_test() -> int:
    READS.clear()
    PRESENT.clear()
    CELL[0] = "selftest"
    data = rec({"a": 1, "nest": {"b": 2}})
    data.get("a")
    data["nest"].get("b")
    data.get("zzz_unproduced", 0)
    miss = sorted(k for (_s, k) in READS)
    ok = miss == ["zzz_unproduced"]
    print(f"RESULT selftest_unproduced={len(miss)} count")
    print("RESULT selftest_ok=%d count" % ok)
    READS.clear()
    PRESENT.clear()
    clean = rec({"a": 1})
    clean.get("a")
    print(f"RESULT clean_fixture_unproduced={len(READS)} count")
    return 0 if ok and not READS else 1


# ---------------------------------------------------------------------------
def _read_entity(ent) -> None:
    for cls in type(ent).__mro__:
        if not cls.__module__.startswith("heatpump_optimizer"):
            continue
        for name, member in vars(cls).items():
            if isinstance(member, property) and not name.startswith("__"):
                try:
                    getattr(ent, name)
                except Exception:
                    pass


def arm_a() -> dict:
    from harness import FakeEntry, FakeHass, FakeState  # type: ignore
    import golden  # type: ignore
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer import coordinator as coord_mod
    import heatpump_optimizer as integration
    from datetime import timedelta

    if ARGS.perturb:
        # The one-line deletion, made in memory on the method's own source: the same text the
        # static producer scan reads (PERTURB_DROP below), so both arms see the line gone.
        import inspect
        import textwrap
        src = textwrap.dedent(inspect.getsource(coord_mod.HeatPumpOptimizerCoordinator._build_data_dict))
        cut = "\n".join(l for l in src.splitlines() if PERTURB_LINE not in l)
        assert cut != src, "perturbation line not found"
        ns: dict = {}
        exec(compile(cut, str(PKG / "coordinator.py"), "exec"), coord_mod.__dict__, ns)
        coord_mod.HeatPumpOptimizerCoordinator._build_data_dict = ns["_build_data_dict"]

    diag = None
    try:
        diag = importlib.import_module("heatpump_optimizer.diagnostics")
    except Exception:
        pass
    start = golden.START
    cells = 0
    top_keys_union: set[str] = set()
    for name, cfg in golden.coordinator_scenarios().items():
        cfg = dict(cfg)
        cfg.setdefault("indoor_temp_entity", "sensor.indoor")
        cfg.setdefault("outdoor_temp_entity", "sensor.outdoor")
        dt_util.freeze(start)
        try:
            hass = FakeHass()
            hass.states.set("sensor.indoor", FakeState("21.4"))
            hass.states.set("sensor.outdoor", FakeState("-3.0"))
            entry = FakeEntry(data=cfg)
            coord = coord_mod.HeatPumpOptimizerCoordinator(hass, entry)
            coord._prices = [
                {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                 "starts_at": (start + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
                for h in range(48)]
            coord._weather_forecast = [
                {"datetime": (start + timedelta(hours=h)).isoformat(),
                 "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
                 "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
            coord._solar_radiation_forecast = [
                max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]
            entry.runtime_data = coord
            for cycle in range(2):
                async def run():
                    await coord._update_current_state()
                    if cycle:
                        await coord.async_run_optimization()
                asyncio.run(run())
                data = coord._build_data_dict()
                top_keys_union |= set(data)
                CELL[0] = f"{name}/c{cycle}"
                cells += 1
                coord.data = rec(data)
                for platform in integration.PLATFORM_LIST:
                    mod = importlib.import_module(f"heatpump_optimizer.{platform}")
                    ents: list = []
                    asyncio.run(mod.async_setup_entry(hass, entry, ents.extend))
                    for e in ents:
                        _read_entity(e)
                if diag is not None and hasattr(diag, "async_get_config_entry_diagnostics"):
                    try:
                        asyncio.run(diag.async_get_config_entry_diagnostics(hass, entry))
                    except Exception:
                        pass
        finally:
            dt_util.freeze(None)
    return {"cells": cells, "top_keys": top_keys_union}


CONSUMER_MODULES = {"sensor.py", "binary_sensor.py", "climate.py", "switch.py", "button.py",
                    "datetime.py", "diagnostics.py"}


PERTURB_LINE = 'data["heat_pump_power_series"], data["house_power_series"] = _power_windows(self)'


def producer_literals() -> set[str]:
    """Every string written as a dict key or a subscript-store key in a production module
    that is not a platform/diagnostics consumer (a platform's own attribute dict naming the
    same key is the consumer's output, not a producer of the payload)."""
    out: set[str] = set()
    for p in PKG.rglob("*.py"):
        if p.name in CONSUMER_MODULES:
            continue
        text = p.read_text()
        if ARGS.perturb and p.name == "coordinator.py":
            text = "\n".join(l for l in text.splitlines() if PERTURB_LINE not in l)
        t = ast.parse(text)
        for n in ast.walk(t):
            if isinstance(n, ast.Dict):
                for k in n.keys:
                    if isinstance(k, ast.Constant) and isinstance(k.value, str):
                        out.add(k.value)
            elif isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Store):
                s = n.slice
                if isinstance(s, ast.Constant) and isinstance(s.value, str):
                    out.add(s.value)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "dict":
                out.update(kw.arg for kw in n.keywords if kw.arg)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ("setdefault",):
                if n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                    out.add(n.args[0].value)
    return out


# ---------------------------------------------------------------------------
ID_RE = re.compile(r"\b(sensor|binary_sensor|switch|climate|button|datetime)\.heat_pump_optimizer_[a-z0-9_]+\b")


def arm_b() -> dict:
    """Entity ids referenced vs entity ids built."""
    import heatpump_optimizer as integration
    from harness import FakeEntry, FakeHass  # type: ignore
    from heatpump_optimizer import coordinator as coord_mod
    hass = FakeHass()
    entry = FakeEntry(data={"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
                            "dhw_tank_volume": 180.0})
    coord = coord_mod.HeatPumpOptimizerCoordinator(hass, entry)
    coord.data = coord._build_data_dict()
    entry.runtime_data = coord
    built: set[str] = set()
    for platform in integration.PLATFORM_LIST:
        mod = importlib.import_module(f"heatpump_optimizer.{platform}")
        ents: list = []
        asyncio.run(mod.async_setup_entry(hass, entry, ents.extend))
        for e in ents:
            eid = getattr(e, "entity_id", None)
            if not eid:
                tk = getattr(e, "_attr_translation_key", None) or getattr(e, "translation_key", None)
                if tk:
                    eid = f"{platform}.heat_pump_optimizer_{tk}"
            if eid:
                built.add(str(eid))
    refs: dict[str, set[str]] = {}
    roots = [TREE / "blueprints", PKG / "www"]
    files = [p for r in roots if r.exists() for p in r.rglob("*") if p.is_file() and p.suffix in (".yaml", ".js", ".mjs")]
    files += list(PKG.rglob("*.py"))
    for p in files:
        text = p.read_text(errors="replace")
        if p.suffix == ".yaml":
            # a blueprint's reference is a value it hands Home Assistant (an input default
            # or an entity_id), not prose in a description naming a legacy id
            text = "\n".join(l for l in text.splitlines()
                              if re.match(r"\s*(-\s*)?(default|entity_id)\s*:", l))
        for m in ID_RE.finditer(text):
            refs.setdefault(m.group(0), set()).add(str(p.relative_to(TREE)))
    # an id that is a prefix of a built id (pattern construction in code) is not a reference miss
    dangling = {i: sorted(f) for i, f in refs.items()
                if i not in built and not any(b.startswith(i) for b in built)}
    return {"built": len(built), "refs": len(refs), "dangling": dangling}


# ---------------------------------------------------------------------------
def arm_c() -> list:
    def defined(paths):
        names = set()
        for p in paths:
            t = ast.parse(p.read_text())
            for n in ast.walk(t):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    names.add(n.name)
                elif isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store):
                    names.add(n.attr)
                elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                    names.add(n.id)
                elif isinstance(n, ast.keyword) and n.arg:
                    names.add(n.arg)
                elif isinstance(n, ast.arg):
                    names.add(n.arg)
                elif (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "setattr"
                      and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant)):
                    names.add(n.args[1].value)
        return names
    pk = defined(PKG.rglob("*.py"))
    # Names Home Assistant core itself provides on the objects these calls probe
    # (State, ConfigEntry, ConfigEntries, UnitSystem, HTTP, the Lovelace resource
    # collection, FlowHandler, DataUpdateCoordinator, datetime). Their producer is
    # upstream, so they are external, not P6.
    upstream = {"async_update_entry", "_get_reauth_entry", "cur_step", "async_on_unload",
                "async_start_reauth", "last_update_success", "async_items", "register_static_path",
                "async_update_item", "last_updated", "last_changed", "last_reported", "isoformat",
                "temperature_unit"}
    out = []
    for p in sorted(PKG.rglob("*.py")):
        t = ast.parse(p.read_text())
        for n in ast.walk(t):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("getattr", "hasattr")
                    and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant)
                    and isinstance(n.args[1].value, str)):
                a = n.args[1].value
                if a not in pk and a not in upstream:
                    out.append(f"{p.name}:{n.lineno} {a}")
    return out


def main() -> int:
    if ARGS.self_test:
        return self_test()
    a = arm_a()
    produced = producer_literals()
    unproduced = {}
    for (site, keypath), cells in READS.items():
        # absent in every cell in which it was read, and never present at that site
        if (site, keypath) in PRESENT:
            continue
        leaf = keypath.rsplit(".", 1)[-1]
        top = keypath.split(".", 1)[0]
        if "." not in keypath and keypath in a["top_keys"]:
            continue
        unproduced[(site, keypath)] = {"cells": len(cells), "literal_written": leaf in produced}
    silent = {k: v for k, v in unproduced.items() if not v["literal_written"]}
    cond = {k: v for k, v in unproduced.items() if v["literal_written"]}
    print("# arm A: reads absent in every driven cell")
    for (site, kp), v in sorted(silent.items()):
        print(f"SEAM A-unproduced {site} {kp} cells={v['cells']}")
    for (site, kp), v in sorted(cond.items()):
        print(f"SEAM A-conditional {site} {kp} cells={v['cells']} (a producer literal exists; not driven)")
    b = arm_b()
    print("# arm B: entity ids referenced but never built")
    for i, f in sorted(b["dangling"].items()):
        print(f"SEAM B {i} in {','.join(f)}")
    c = arm_c()
    print("# arm C: getattr/hasattr on a name no production code defines")
    for s in c:
        print(f"SEAM C {s}")
    tf = (time.process_time() - _T0P) / max(time.thread_time() - _T0T, 1e-9)
    print(f"RESULT cells={a['cells']} count")
    print(f"RESULT distinct_reads={len(READS) + len(PRESENT)} count")
    print(f"RESULT p6_unproduced_reads={len(silent)} count")
    print(f"RESULT p6_conditional_reads={len(cond)} count")
    print(f"RESULT p6_dangling_entity_ids={len(b['dangling'])} count")
    print(f"RESULT entity_ids_built={b['built']} count")
    print(f"RESULT p6_undefined_getattr={len(c)} count")
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")
    if ARGS.json:
        Path(ARGS.json).write_text(json.dumps({
            "silent": [list(k) for k in sorted(silent)], "conditional": [list(k) for k in sorted(cond)],
            "dangling": b["dangling"], "getattr": c}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

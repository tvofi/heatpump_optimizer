#!/usr/bin/env python3
"""ARCH2-s4 (round 10, D7): store-load seams that raise on a stored payload that is not a mapping.

Metric:   count of store-load seams (seam rule below) whose call raises when every
          ``QuarantiningStore.async_load`` returns a non-mapping JSON value ([1] or "x");
          a seam that returns, resets or starts afresh counts 0. Count key: the exception
          the production seam lets escape, never the payload's type label.
Seam rule: every function in custom_components/heatpump_optimizer that awaits ``<x>.async_load()``
          on a store or calls ``store.load_mapping`` (printed as SEAM lines; the harness refuses
          to report when a seam it found has no driver, so a new seam cannot hide).
Instrumented symbols: store:QuarantiningStore.async_load (patched to the payload), and through it
          notifier:Notifier.async_load, dhw_learning:DhwProfileLearner.async_load_profile/_draws,
          legionella:LegionellaGuard.async_load, debugger:DebugCollector.async_load,
          coordinator:HeatPumpOptimizerCoordinator._async_load_* and coordinator:_stored_fuse_advisor,
          store:load_mapping.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s4/load_prelude.py [--perturb]
Perturbation: --perturb swaps ``notifier.Notifier.async_load`` for a body routed through
          ``store.load_mapping`` (in memory); the count must fall (to_zero on main).
Expected (baseline 9061fbd3d710, Apple M1, darwin): raising_seams=1 (notifier:Notifier.async_load);
          --perturb: raising_seams=0. Exact (a count).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast  # noqa: E402
import asyncio  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer import boost, debugger, notifier, pump_arbiter, store  # noqa: E402

PKG = ROOT / "custom_components" / "heatpump_optimizer"
CFG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
}


def seams() -> list[str]:
    """``module:Owner.function`` for every function that loads a store (the seam rule)."""
    found = []
    for path in sorted(PKG.glob("*.py")):
        tree = ast.parse(path.read_text())

        def visit(node, owner):
            for ch in ast.iter_child_nodes(node):
                if isinstance(ch, ast.ClassDef):
                    visit(ch, ch.name)
                elif isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    hit = False
                    for n in ast.walk(ch):
                        if isinstance(n, ast.Call) and isinstance(n.func, (ast.Attribute, ast.Name)):
                            name = n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id
                            if name == "load_mapping":
                                hit = True
                            if name == "async_load" and isinstance(n.func, ast.Attribute):
                                recv = ast.unparse(n.func.value)
                                hit = hit or "store" in recv.lower()
                    if hit:
                        found.append(f"{path.stem}:{(owner + '.') if owner else ''}{ch.name}")
                    visit(ch, owner)
                else:
                    visit(ch, owner)

        visit(tree, None)
    # The boundary itself and the helper are not consumers.
    return [s for s in found if s not in ("store:QuarantiningStore.async_load",)]


async def _via_load_mapping(self) -> None:
    """The perturbation: Notifier.async_load through the shared prelude."""
    raw = await store.load_mapping(self._store, "notifier state")
    sent = (raw or {}).get("sent")
    if isinstance(sent, dict):
        self._sent = {k: v for k, v in sent.items() if isinstance(k, str) and isinstance(v, str)}
        self._baseline = False


def drivers(coord):
    hass = coord.hass
    collector = debugger.DebugCollector(hass, "arch2s4", lambda coro: coro.close())
    note = notifier.Notifier(hass, "arch2s4", lambda coro: coro.close())
    return {
        "coordinator:_stored_fuse_advisor": lambda: cm._stored_fuse_advisor(coord._ledger_store),
        "coordinator:HeatPumpOptimizerCoordinator._async_load_thermal_learning": coord._async_load_thermal_learning,
        "coordinator:HeatPumpOptimizerCoordinator._async_load_price_model": coord._async_load_price_model,
        "coordinator:HeatPumpOptimizerCoordinator._async_load_ledger": coord._async_load_ledger,
        "coordinator:HeatPumpOptimizerCoordinator._async_load_accuracy": coord._async_load_accuracy,
        "coordinator:HeatPumpOptimizerCoordinator._async_load_energy_totals": coord._async_load_energy_totals,
        "coordinator:HeatPumpOptimizerCoordinator._async_load_manual_plan": coord._async_load_manual_plan,
        "coordinator:HeatPumpOptimizerCoordinator._async_load_snapshots": coord._async_load_snapshots,
        "dhw_learning:DhwProfileLearner.async_load_profile": coord._dhw_learner.async_load_profile,
        "dhw_learning:DhwProfileLearner.async_load_draws": coord._dhw_learner.async_load_draws,
        "legionella:LegionellaGuard.async_load": coord._legionella.async_load,
        "notifier:Notifier.async_load": note.async_load,
        "debugger:DebugCollector.async_load": collector.async_load,
        "store:load_mapping": lambda: store.load_mapping(coord._ledger_store, "probe"),
        # needs an AwayState and an entity reader; covered by driving load_mapping itself:
        "away:restore_override": None,
        "boost:restore": lambda: boost.restore(coord),
        "pump_arbiter:_load": lambda: pump_arbiter._load(coord),
    }


def main(argv: list[str]) -> int:
    t_cpu, t_thr = time.process_time(), time.thread_time()
    perturb = "--perturb" in argv
    if perturb:
        notifier.Notifier.async_load = _via_load_mapping
    found = seams()
    raising: set[str] = set()
    driven: set[str] = set()
    for payload in ([1], "x"):
        async def fake_load(self, _p=payload):
            return _p

        store.QuarantiningStore.async_load = fake_load
        coord = cm.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=dict(CFG)))
        table = drivers(coord)
        missing = [s for s in found if s not in table]
        if missing:
            print("RESULT undriven_seams=" + ",".join(missing))
            return 2
        for seam in found:
            fn = table[seam]
            if fn is None:
                continue
            driven.add(seam)
            try:
                asyncio.run(fn())
            except Exception as err:  # noqa: BLE001 - the measured escape
                raising.add(seam)
                print(f"RAISES {seam} payload={payload!r}: {type(err).__name__}: {err}")
    # Where the escape lands: the entry's setup path awaits the notifier's load unguarded.
    setup_raises = 0
    coord = cm.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=dict(CFG)))
    try:
        asyncio.run(notifier.async_setup_notifier(coord.hass, coord.config_entry, coord))
    except Exception as err:  # noqa: BLE001 - the measured escape
        setup_raises = 1
        print(f"RAISES notifier:async_setup_notifier payload='x': {type(err).__name__}: {err}")
    print(f"RESULT setup_notifier_raises={setup_raises} count")
    for s in found:
        print(f"SEAM {s}{'' if s in driven else ' (via store:load_mapping)'}")
    print(f"RESULT seams={len(found)} count")
    print(f"RESULT driven_seams={len(driven)} count")
    print(f"RESULT raising_seams={len(raising)} count")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a (count; no timing RESULT)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

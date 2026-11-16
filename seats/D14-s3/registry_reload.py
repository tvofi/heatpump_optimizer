#!/usr/bin/env python3
"""D14-s3 (round 11, nightly-replay axis): N-registry-leak over replayed reloads.

The replay lane replays a reload (``controls.reloads``) by building a new
coordinator handed the last publish -- it never runs the old entry's unload.
This detector replays ``tests/replay/synthetic-dhw-only.json`` for 3 h with
reloads at +1 h and +2 h, and runs the PRODUCTION unload
(``heatpump_optimizer.async_unload_entry`` -> ``async_shutdown``, then every
``entry.async_on_unload`` callback, as ``ConfigEntry.async_unload`` runs them)
on the old entry before each new coordinator is built. When the replay has returned and
every local is gone, it collects garbage and counts the coordinators still
alive, and names what holds each one (the first module-level owner on the
referrer chain).

Metric: live ``HeatPumpOptimizerCoordinator`` objects after the replay
returned and ``gc.collect()``, less the same count with no reload (the null
control: what a single never-unloaded entry leaves). Count key: the
production objects themselves (weakrefs taken at construction).
Perturbation (``--perturb``): ``early_cutoff.detach`` (the unload half of the
weak registry whose value reaches its key) becomes a no-op -> count goes up.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s3/registry_reload.py
Expected at 92d38ecb6: see REPORT.md (exact counts). Machine: box B7, 4 vCPU.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replaykit  # noqa: E402

import argparse  # noqa: E402
import asyncio  # noqa: E402
import gc  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
import types  # noqa: E402
import weakref  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402

ARMS = {"no_reload": 0, "two_reloads": 2}


def holders(obj, depth=6) -> list[str]:
    """The module-level owners on the referrer chains of ``obj`` (BFS)."""
    seen, frontier, found = {id(obj)}, [obj], []
    mods = {id(vars(m)): name for name, m in list(sys.modules.items()) if m is not None
            and hasattr(m, "__dict__")}
    for _ in range(depth):
        nxt = []
        for o in frontier:
            for r in gc.get_referrers(o):
                if id(r) in seen or r is frontier or r is nxt or isinstance(r, types.FrameType):
                    continue
                seen.add(id(r))
                if id(r) in mods:
                    key = next((k for k, v in r.items() if v is o), "?")
                    found.append(f"{mods[id(r)]}.{key}")
                    continue
                nxt.append(r)
        frontier = nxt[:400]
    return sorted(set(found))[:8]


def child(tree: Path, arm: str, perturb: bool) -> dict:
    doc = json.loads((tree / "tests" / "replay" / "synthetic-dhw-only.json").read_text())
    start = datetime.fromisoformat(doc["window"]["start"])
    doc["window"]["end"] = (start + timedelta(hours=3)).isoformat()
    doc.setdefault("controls", {})["reloads"] = [
        (start + timedelta(hours=1 + i)).isoformat() for i in range(ARMS[arm])]
    refs: list = []

    def setup(ctx):
        import heatpump_optimizer as integration
        from heatpump_optimizer import coordinator as cm
        if perturb:
            # The one-line re-introduction: the registry's unload half is a no-op.
            from heatpump_optimizer import early_cutoff
            early_cutoff.detach = lambda held: None
        cls = cm.HeatPumpOptimizerCoordinator
        real_init = cls.__init__
        state = {"last": None}

        def init(self, hass, entry, *a, **kw):
            prev = state["last"]
            if kw.get("skip_first_solve") and prev is not None:
                # The production unload of the entry being replaced.
                entry.runtime_data = prev
                ok = asyncio.run(integration.async_unload_entry(hass, entry))
                # Then what ConfigEntry.async_unload does after the component's
                # unload: every async_on_unload callback, once, list cleared.
                callbacks, entry._on_unload = list(entry._on_unload), []
                for cb in callbacks:
                    res = cb()
                    if asyncio.iscoroutine(res):
                        asyncio.run(res)
                ctx.setdefault("unloads", []).append(bool(ok))
            real_init(self, hass, entry, *a, **kw)
            state["last"] = self
            refs.append(weakref.ref(self))
        cls.__init__ = init
        ctx["state"] = state

    out = replaykit.run(tree, doc, 30, setup)
    out["ctx"].pop("state", None)
    del out
    for _ in range(3):
        gc.collect()
    live = [r() for r in refs if r() is not None]
    return {"arm": arm, "constructed": len(refs), "live": len(live),
            "holders": [holders(c) for c in live]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, default=replaykit.ROOT)
    ap.add_argument("--arm", choices=tuple(ARMS))
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--child", action="store_true")
    a = ap.parse_args()
    tree = a.tree.resolve()
    if a.child:
        replaykit.emit(child(tree, a.arm, a.perturb))
        return 0
    t0 = time.monotonic()
    import concurrent.futures as cf
    arms = [a.arm] if a.arm else list(ARMS)
    extra = ["--perturb"] if a.perturb else []
    with cf.ThreadPoolExecutor(len(arms)) as ex:
        res = dict(zip(arms, ex.map(lambda arm: replaykit.child(
            Path(__file__).resolve(), tree, ["--arm", arm, *extra]), arms)))
    for arm, d in res.items():
        if d is None:
            print(f"RESULT {arm}_ran=0 count")
            continue
        print(f"arm {arm}: constructed={d['constructed']} live_after_gc={d['live']}")
        for h in d["holders"]:
            print(f"  held by {h}")
        print(f"RESULT {arm}_live_coordinators={d['live']} count")
    if all(res.get(k) for k in ARMS):
        print(f"RESULT leaked_per_reload_excess="
              f"{res['two_reloads']['live'] - res['no_reload']['live']} count")
    print(f"RESULT wall_s={time.monotonic() - t0:.1f} s (provisional)")
    replaykit.tail_results()
    return 0


if __name__ == "__main__":
    sys.exit(main())

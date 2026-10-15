#!/usr/bin/env python3
"""ARCH2-s2 (round 10, D7): in-place hub writes reachable from the coordinator's EVENT callbacks.

hub_solve_writes roots the census at the scheduled cycle and the two solves, so a hub written in place
from a Home Assistant event callback (the ECL110 MQTT state message, the peak-guard meter event, the
defrost and pump listeners) is counted by no score metric: shared_inplace_writes excludes the hubs.
This harness runs hub_solve_writes' own site census (``_sites``) from those callbacks as roots.

Metric: distinct (file, line, hub, field) in-place write sites under the event roots, counter C4 on.
Count key: the static write sites of the measured tree (a rebind of the hub is not a site).
Instrumented symbols: archscore.metrics.hub_solve_writes:_sites over
        coordinator:HeatPumpOptimizerCoordinator._async_handle_ecl110_state_message,
        ._on_power_event, ._on_defrost_event.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s2/event_hub_writes.py [ROOT|--ref REF] [--patch P]
Perturbation: --patch P4_event_readings_published_whole.patch on the baseline reads 0 (from 3);
        planting ``ctx._current_state.peak_guard_active = True`` back reads 1.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


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


REPO = repo_root(__file__)
sys.path.insert(0, str(REPO / "tools" / "audit"))

from archscore import counters as K, score  # noqa: E402
from archscore.metrics import common as C, hub_solve_writes as H  # noqa: E402

BASELINE = "9061fbd3d710d5894b7083d8a58b8203f9e7aa97"
EVENT_ROOTS = ("_async_handle_ecl110_state_message", "_on_power_event", "_on_defrost_event")


def sites(root: Path) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="arch2s2-ev-") as tmp:
        K.flatten(root.resolve(), Path(tmp), inline=True)
        pkg = C.load(tmp)
        eng = C.engine(pkg)
        out: set = set()
        for r in EVENT_ROOTS:
            q = f"{C.COORD_MODULE}:{C.COORD_CLASS}.{r}"
            if q in pkg.funcs:
                out |= {x[:4] for x in H._sites(eng, q)}
        C.reset_caches()
        return [f"{f}:{ln} {h}.{fl}" for f, ln, h, fl in sorted(out)]


def main(argv: list[str]) -> int:
    args = argv[1:]
    with tempfile.TemporaryDirectory(prefix="arch2s2-tree-") as tmp:
        if "--ref" in args:
            root = score.tree_of(args[args.index("--ref") + 1], Path(tmp))
        else:
            pos = [a for a in args if not a.startswith("--")]
            root = Path(pos[0]) if pos and "--patch" not in args else REPO
            if "--patch" in args:
                root = score.tree_of(BASELINE, Path(tmp))
        if "--patch" in args:
            patch = (HERE / args[args.index("--patch") + 1]).resolve()
            subprocess.run(["git", "apply", "--include=custom_components/*", str(patch)], cwd=root, check=True)
        found = sites(root)
    for s in found:
        print(f"  {s}")
    print(f"RESULT event_hub_inplace_writes={len(found)} count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

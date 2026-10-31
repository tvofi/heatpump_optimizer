#!/usr/bin/env python3
"""The replay lane's cycle_cost arms, clean against doubled (#2205's instrument).

Written by the #2205 fixer. The nightly slow lane failed ``cycle_cost sees a
doubled cycle cpu`` on synthetic-dhw-only.json: the cpu-doubled arm read
cpu_ratio 3.5628 against a 3.576 cap, with the clean arm at 1.8804. This
drives ``tests/replay.py --one`` (the lane's own subprocess entry point) for
each arm N times and prints, per run, the arm's cost dict and
``hot/clean``: the doubled arm's cpu_ratio over the median clean cpu_ratio
(cross-process, so load moves it). The exact figure is the arm's own
``injected_ratio`` in its cost dict, present from #2205's head on: the spin
over the clean span its metric times, >= 1 for a doubling (the base's cpu
arm spun ``_async_update_data`` alone and printed none). The ``memory`` arm
is the null control: its ``hot/clean`` must not move between base and head.

Every row carries load1 (``os.getloadavg``) taken before the run, and the
reference solve's thread_factor (process CPU / this-thread CPU of
``tests/stress.py``'s ``reference_solve``, under its own BLAS pin), measured
in this process before the arms run. Run from a worktree root, at the base
and at the head:

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r10_2205_replay_cost_arms.py [N]
"""
from __future__ import annotations

import json
import os
import statistics
import subprocess
import sys
from pathlib import Path

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
FIXTURE = ROOT / "tests" / "replay" / "synthetic-dhw-only.json"
MARK = "<<<replay-json>>>"  # tests/replay.py MARK


def thread_factor() -> float:
    sys.path.insert(0, str(ROOT / "tests"))
    from stress import reference_solve  # pins BLAS threads before numpy loads
    reference_solve()
    rows = [reference_solve() for _ in range(3)]
    return round(sum(r[1] for r in rows) / max(sum(r[2] for r in rows), 1e-9), 3)


def run(arm: str | None) -> dict:
    cmd = [sys.executable, str(ROOT / "tests" / "replay.py"), "--one", str(FIXTURE)]
    if arm:
        cmd += ["--inject-cost", arm]
    load1 = round(os.getloadavg()[0], 2)
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    line = next((ln for ln in proc.stdout.splitlines() if ln.startswith(MARK)), None)
    if line is None:
        raise SystemExit(f"arm {arm}: rc={proc.returncode}: {proc.stderr[-800:]}")
    return {"load1": load1, **json.loads(line[len(MARK):])["cost"]}


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    print(f"RESULT thread_factor={thread_factor()} (reference solve, BLAS pinned to "
          f"{os.environ.get('OPENBLAS_NUM_THREADS')} thread)")
    clean = []
    for i in range(n):
        c = run(None)
        clean.append(c["cpu_ratio"])
        print(f"clean[{i}] {c}")
    mid = statistics.median(clean)
    print(f"RESULT clean cpu_ratio median={mid} min={min(clean)} max={max(clean)}")
    for arm in ("cpu", "loop", "memory"):
        ratios, injected = [], []
        for i in range(n):
            h = run(arm)
            ratios.append(round(h["cpu_ratio"] / mid, 3))
            injected.append(h.get("injected_ratio"))
            print(f"{arm}[{i}] {h} hot/clean={ratios[-1]}")
        print(f"RESULT {arm} hot/clean cpu_ratio median={statistics.median(ratios)} "
              f"min={min(ratios)} max={max(ratios)} injected_ratio={injected}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

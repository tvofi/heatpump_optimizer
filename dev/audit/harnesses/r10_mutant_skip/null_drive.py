#!/usr/bin/env python3
"""The skip's null control, by real drives (#1930 fold (e), r10-mutant-skip).

`replay.py` proves no ledger kill sits on a `never` row. This drives the
pairs themselves: a seeded sample of `never` rows per driver -- each mutant
applied in a worker tree and run through that driver exactly as the lane
does (`run_script`, judged by `killed()` against an untraced baseline). Every
one must survive: a kill is a pair the skip would have lost.

The positive control, so a survival cannot be the harness's own blindness:
for each driver, ledger `killed_by` rows it holds on `reached` rows, driven
the same way. Each must die.

    python3 dev/audit/harnesses/r10_mutant_skip/null_drive.py \
        --matrix dev/audit/harnesses/r10_mutant_skip/matrix.tsv \
        --per-driver 6 --seed 1930 --jobs 3
"""
from __future__ import annotations

import argparse
import random
import sys
import tempfile
import threading
from collections import defaultdict
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
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import mutation_table as mt  # noqa: E402
from replay import read_matrix  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--per-driver", type=int, default=6)
    ap.add_argument("--positive", type=int, default=2)
    ap.add_argument("--seed", type=int, default=1930)
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args(argv)
    rows = read_matrix(Path(a.matrix))
    sites = {s["anchor"]: s for s in mt.inventory()}
    kb = mt.load_budgets().get("killed_by", {})
    rng = random.Random(a.seed)

    never: dict[str, list[str]] = defaultdict(list)
    killers: dict[str, list[str]] = defaultdict(list)
    for (anchor, driver), state in sorted(rows.items()):
        if state == "never" and anchor in sites:
            never[driver].append(anchor)
        entry = kb.get(anchor)
        if (state == "reached" and anchor in sites
                and mt.disposition_matches(entry, sites[anchor])
                and entry.get("killed_by") == driver):
            killers[driver].append(anchor)
    tasks: list[tuple[str, str, str]] = []
    for driver in sorted(never):
        pick = rng.sample(never[driver], min(a.per_driver, len(never[driver])))
        tasks += [("null", driver, x) for x in pick]
        pos = rng.sample(killers[driver], min(a.positive, len(killers[driver])))
        tasks += [("positive", driver, x) for x in pos]
    print(f"{len(tasks)} drive(s): "
          f"{sum(t[0] == 'null' for t in tasks)} never-row null(s) over "
          f"{len(never)} driver(s), "
          f"{sum(t[0] == 'positive' for t in tasks)} positive control(s)",
          flush=True)

    work = Path(tempfile.mkdtemp(prefix="reach-null-"))
    trees = [mt.clone_tree(work / f"w{i}") for i in range(a.jobs)]
    lock = threading.Lock()
    baselines: dict[str, mt.ScriptRun] = {}
    blocks: dict[str, threading.Lock] = defaultdict(threading.Lock)
    results: list[tuple[str, str, str, bool | None]] = []
    queue = list(tasks)

    def baseline(w: int, driver: str) -> mt.ScriptRun:
        with blocks[driver]:
            if driver not in baselines:
                args, env = mt.drive_spec(driver, "HEAD^1")
                baselines[driver] = mt.run_script(driver, trees[w], 3 * 3600,
                                                  args, env)
        return baselines[driver]

    def work_on(w: int) -> None:
        while True:
            with lock:
                if not queue:
                    return
                arm, driver, anchor = queue.pop(0)
            base = baseline(w, driver)
            site = sites[anchor]
            path = trees[w] / site["file"]
            original = path.read_text()
            lines = original.splitlines(True)
            lines[site["line"] - 1] = site["new"] + "\n"
            path.write_text("".join(lines))
            try:
                args, env = mt.drive_spec(driver, "HEAD^1")
                run = mt.run_script(driver, trees[w], 3 * 3600, args, env)
            finally:
                path.write_text(original)
            hit = None if run.timed_out else mt.killed(driver, run, base)
            with lock:
                results.append((arm, driver, anchor, hit))
            print(f"  {arm} {driver} {anchor}: "
                  f"{'KILLED' if hit else 'timed out' if hit is None else 'survived'}"
                  f" (rc={run.rc} failed={run.failed}, baseline rc={base.rc})",
                  flush=True)

    try:
        mt._share(a.jobs, work_on)
    finally:
        for t in trees:
            mt.drop_tree(t)
    red = sorted(d for d, b in baselines.items() if b.rc != 0)
    nulls = [r for r in results if r[0] == "null"]
    pos = [r for r in results if r[0] == "positive"]
    lost = [r for r in nulls if r[3]]
    blind = [r for r in pos if not r[3]]
    print(f"\nBASELINES red: {red or 'none'}")
    print(f"NULL never rows driven {len(nulls)}: killed {len(lost)}, "
          f"survived {sum(r[3] is False for r in nulls)}, "
          f"timed out {sum(r[3] is None for r in nulls)}")
    print(f"POSITIVE ledger kills on reached rows driven {len(pos)}: "
          f"killed {len(pos) - len(blind)}, not killed {len(blind)}")
    for r in lost:
        print(f"  LOST KILL {r[1]} {r[2]}: a never row its driver killed")
    for r in blind:
        print(f"  NOT REPRODUCED {r[1]} {r[2]}")
    ok = not lost and not red and all(r[3] is not None for r in nulls)
    print("NULL CONTROL: " + ("no never row was killed" if ok
                              else "REFUTED or inconclusive"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

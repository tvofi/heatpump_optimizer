#!/usr/bin/env python3
"""R11-HOTFIX-MUTATION-DRIVER-CAP harness: the `tests / mutation` job's wall clock.

    cd <checkout> && python3 <this> [--base REF] [--scale N] [--cost S=SECS]...

Runs the checkout's own `tests/mutation_table.py` main() exactly as tests.yml's
drive step calls it (`--scope changed --base REF --max 10 --jobs 3`), with the
real draw, driver order, worker trees, lazy settles, null control and
`drive_pool` schedule. Only `run_script` is stubbed: each driver run sleeps
its cost divided by `--scale` and is red iff the tree carries a drawn mutant
(an AST change, so the comment-only null control stays green) and the driver
is that site's `killed_by` pin. An unpinned site is killed by nothing, its
whole sweep paid -- an upper bound. A driver's cost is its `recorded_seconds`
(tests/closures.json), overridden by `--cost` (the CI log's measured baseline
of a ref-driven driver, whose recording times a stub).

Prints one line per drawn site (its pin, or `unpinned`), one per site the
draw passed over, one per driver (runs, recorded seconds summed) and
`ESTIMATE <s> s` = the span from the first stubbed driver run's start to the
last one's end, times `--scale`: the drive's schedule at the recorded seconds,
not a CI measurement, and without the job's setup and inventory minutes. Run it in a checkout with the program under test; the before/after
pair is two checkouts of one head, one carrying the patched program.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import tempfile
import sys
import threading
import time
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--scale", type=float, default=100.0)
    ap.add_argument("--cost", action="append", default=[], metavar="S=SECS")
    args = ap.parse_args(argv)

    root = Path.cwd()
    sys.path.insert(0, str(root / "tests"))
    import mutation_table as mt  # noqa: E402  (the checkout's own program)

    cost = mt.recorded_seconds()
    for spec in args.cost:
        name, _, secs = spec.partition("=")
        cost[name] = float(secs)
    killed_by = mt.load_budgets().get("killed_by", {})
    drawn: list[dict] = []
    real_sampled = mt.sampled_pool

    def sampled(*a, **k):
        pool, held = real_sampled(*a, **k)
        drawn[:] = pool
        return pool, held

    runs: dict[str, list[float]] = {}
    span: list[float] = []
    lock = threading.Lock()

    def stub(script, cwd, timeout, extra_args=None, extra_env=None):
        red = False
        for mut in drawn:
            text = (Path(cwd) / mut["file"]).read_text()
            lines = text.splitlines()
            if (len(lines) >= mut["line"]
                    and lines[mut["line"] - 1] == mut["new"]
                    and ast.dump(ast.parse(text)) != ast.dump(ast.parse(
                        (root / mut["file"]).read_text()))):
                red = mt.pinned_script(killed_by, mut) == script
                break
        secs = cost.get(script, 0.0)
        start = time.monotonic()
        time.sleep(secs / args.scale)
        with lock:
            runs.setdefault(script, []).append(secs)
            span.extend((start, time.monotonic()))
        return mt.ScriptRun(1 if red else 0, 1 if red else 0, secs,
                            "  FAIL stub\n1 of 1 STUB CHECKS FAILED\n" if red
                            else "ok\n")

    mt.sampled_pool = sampled
    mt.run_script = stub
    log = tempfile.TemporaryFile("w+")  # main() line-buffers its stdout
    with contextlib.redirect_stdout(log):
        rc = mt.main(["--scope", "changed", "--base", args.base, "--max", "10",
                      "--jobs", "3"])
    # The first driver run's start to the last's end: the inventory, draw and
    # worktree setup before it are this machine's real seconds, not a scaled
    # driver's, so scaling them would charge them 100 times over.
    wall = (max(span) - min(span)) if span else 0.0
    for mut in drawn:
        print(f"SITE {mt.triage_key(mut)} "
              f"{mt.pinned_script(killed_by, mut) or 'unpinned'}")
    log.seek(0)
    for line in log.read().splitlines():
        if "passed over" in line:
            print(f"PASSED {line.strip()}")
    for s, secs in sorted(runs.items()):
        print(f"DRIVER {s} runs={len(secs)} seconds={sum(secs):.0f}")
    print(f"MAIN rc={rc}")
    print(f"ESTIMATE {wall * args.scale:.0f} s at --scale {args.scale:.0f} "
          f"({wall * args.scale / 60:.0f} min against the job's 160)")
    return rc


if __name__ == "__main__":
    sys.exit(main())

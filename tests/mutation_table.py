#!/usr/bin/env python3
"""A mutation table as a gate: does the suite NOTICE a changed production line?

Coverage says a line ran. It cannot say a check would fail if the line were
wrong, and five W5-G7 tranches measured the gap: twenty-two checks executed the
line they were named for and pinned nothing, and twenty-five production guards
turned out to be deletable with no check failing. Every one of those was green
coverage. `tests/coverage_ratchet.py` holds the floor; this holds the meaning.

**Scope is the files that were actually tested.** On a pull request the changed
production files are mutated; a test-only diff is mapped through the closure
recording in `tests/closures.json` -- the same recording the scoped gate selects
by -- so "the files this change tested" is read off a measurement rather than
guessed. `--scope full` puts every production module in scope, which is the
nightly's job and far too slow for a pull request.

**Each mutant is driven only by the scripts whose recorded closure reaches its
file.** Driving every script would cost a full suite per mutant; driving one
hand-picked script would let a mutant survive because its driver never imports
the module, and a survivor that says nothing about the suite is worse than no
survivor at all.

**The kill rule reads the whole output.** #805 recorded the alternative: a
pre-screen that read the last 1200 bytes scored seven real kills as survivors,
because two scripts print their summary line before trailing log noise. A mutant
is killed when a driver's exit status changes, or when its `N of M ... FAILED`
count rises above the baseline's.

**Nothing is mutated in the working tree.** Each worker mutates its own copy, so
a run killed mid-mutant cannot leave a production file edited -- the failure mode
an in-place `try/finally` still has, because a SIGKILL does not run `finally`.

**The budget is a one-sided cap on the survivor FRACTION, and deliberately not
the exact-count ratchet `tests/structure.py` and `tests/coverage_ratchet.py`
use.** Those measure the whole tree deterministically, so an exact count is
reproducible and "improved and not yet recorded" is a fair refusal. This does
not: the pool is a seeded sample drawn from whichever files the diff put in
scope, so two clean branches touching different modules draw different pools and
score differently through no fault of either. An exact-count ratchet over that
would go red at random, which is how a gate teaches seats to re-record it
unread. So the cap is a rate, it only moves down, and the run prints every
survivor by file, line and operator -- the table is the product, the cap only
stops it rotting.

A survivor is not automatically a defect. An equivalent mutant cannot be killed
by any test, and several of the twenty-five guards W5-G7 measured are worth
keeping for the cause they buy rather than the outcome a check could see.

    python3 tests/mutation_table.py --scope changed --base origin/main
    python3 tests/mutation_table.py --scope full --jobs 4
    python3 tests/mutation_table.py --scope changed --record --reason "..."

Prior art, deliberately not imported: `tools/audit/round3/D3/mutant_pool.py` and
its `prescreen.py` measure the same property over a hand-recorded mutant list at
a frozen baseline SHA. That is audit evidence and has to keep answering for the
tree it was run against; a gate has to follow the tree instead. The six
operators below are that tool's, and a change to either should read the other.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = "custom_components/heatpump_optimizer/"
PRODUCTION = ROOT / PKG
BUDGETS = ROOT / "tests" / "mutation_budgets.json"
CLOSURES = ROOT / "tests" / "closures.json"

_NUM = re.compile(r"-?\d+\.?\d*")
_FAILED = re.compile(r"^\s*(\d+) of (\d+) .*FAILED\s*$", re.M)


# ---------------------------------------------------------------- operators

def _one_line(node, lines) -> bool:
    end = getattr(node, "end_lineno", None)
    return end is not None and end == node.lineno


def _indent(s: str) -> str:
    return s[: len(s) - len(s.lstrip())]


def candidates(path: Path):
    """Single-line mutants of one production file.

    Six operators, each a change a careless edit could really make: a clamp
    dropped, a guard switched off, a raise or a return removed, a conjunction
    weakened, a module constant doubled.
    """
    src = path.read_text()
    lines = src.splitlines()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return
    sole = set()
    for node in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            body = getattr(node, field, None)
            if isinstance(body, list) and len(body) == 1:
                sole.add(body[0].lineno)

    try:
        rel = str(path.relative_to(ROOT))
    except ValueError:
        # Called on a file outside the checkout -- a worker's copy, or the
        # synthetic module tests/entities.py drives the operators over.
        rel = str(path)
    for node in ast.walk(tree):
        ln = getattr(node, "lineno", None)
        if ln is None or ln > len(lines):
            continue
        line = lines[ln - 1]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in ("min", "max") and len(node.args) == 2
                and _one_line(node, lines)):
            seg = ast.get_source_segment(src, node)
            arg0 = ast.get_source_segment(src, node.args[0])
            if seg and arg0 and seg in line and line.count(seg) == 1:
                yield dict(kind="CLAMP_DROP", file=rel, line=ln, old=line,
                           new=line.replace(seg, f"({arg0})"))
        if (isinstance(node, ast.If) and _one_line(node.test, lines)
                and not node.orelse and stripped.startswith("if ")
                and stripped.endswith(":")):
            yield dict(kind="GUARD_OFF", file=rel, line=ln, old=line,
                       new=_indent(line) + "if False:")
        if isinstance(node, (ast.Raise, ast.Return)) and _one_line(node, lines):
            if ln in sole:
                continue
            kind = "RAISE_DEL" if isinstance(node, ast.Raise) else "RETURN_DEL"
            if kind == "RETURN_DEL" and getattr(node, "value", None) is None:
                continue
            yield dict(kind=kind, file=rel, line=ln, old=line,
                       new=_indent(line) + "pass")
        if (isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And)
                and _one_line(node, lines) and " and " in line
                and line.count(" and ") == 1):
            yield dict(kind="BOOLOP", file=rel, line=ln, old=line,
                       new=line.replace(" and ", " or "))
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        tgt = node.targets[0]
        if not isinstance(tgt, ast.Name) or not tgt.id.isupper():
            continue
        if not isinstance(node.value, ast.Constant):
            continue
        v = node.value.value
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            continue
        ln = node.lineno
        line = lines[ln - 1]
        if "=" not in line:
            continue
        head, tail = line.split("=", 1)
        m = _NUM.search(tail)
        if not m:
            continue
        new_val = "1.0" if v == 0 else repr(
            round(v * 2, 6) if isinstance(v, float) else v * 2
        )
        yield dict(kind="CONST", file=rel, line=ln, old=line,
                   new=head + "=" + tail[: m.start()] + new_val + tail[m.end():])


# -------------------------------------------------------------------- scope

def load_closures() -> dict[str, list[str]]:
    raw = json.loads(CLOSURES.read_text())
    return raw.get("closures", raw)


def changed_paths(base: str) -> list[str]:
    """Files this branch changed, three-dot against `base` (never two-dot)."""
    merge_base = subprocess.run(
        ["git", "merge-base", base, "HEAD"], cwd=ROOT,
        capture_output=True, text=True,
    ).stdout.strip()
    if not merge_base:
        return []
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{merge_base}...HEAD"], cwd=ROOT,
        capture_output=True, text=True,
    ).stdout
    changed = {ln.strip() for ln in out.splitlines() if ln.strip()}
    # Plus what is not committed yet. In CI the diff is the whole change and
    # this adds nothing; run by hand it is the difference between scoping the
    # work in front of the seat and scoping its last commit.
    status = subprocess.run(
        ["git", "status", "--porcelain", "-z"], cwd=ROOT,
        capture_output=True, text=True,
    ).stdout
    for entry in status.split("\0"):
        if len(entry) > 3:
            changed.add(entry[3:].strip())
    return sorted(changed)


def scope_files(scope: str, base: str) -> tuple[list[Path], str]:
    """The production files in scope, and the sentence that says why."""
    if scope == "full":
        return sorted(PRODUCTION.rglob("*.py")), "every production module"
    changed = changed_paths(base)
    if not changed:
        return [], "nothing changed against the base"
    direct = sorted({
        ROOT / p for p in changed
        if p.startswith(PKG) and p.endswith(".py") and (ROOT / p).exists()
    })
    if direct:
        return direct, f"{len(direct)} production file(s) this diff changes"
    closures = load_closures()
    scripts = [p for p in changed if p.startswith("tests/") and p.endswith(".py")]
    reached = sorted({
        ROOT / f for s in scripts for f in closures.get(s, [])
        if f.startswith(PKG) and f.endswith(".py") and (ROOT / f).exists()
    })
    if reached:
        return reached, (
            f"{len(reached)} production file(s) in the measured closure of "
            f"{len(scripts)} changed test script(s)"
        )
    return [], "no production file is in scope for this diff"


def drivers_for(rel: str, closures: dict, allow: list[str]) -> list[str]:
    """The candidate scripts whose MEASURED closure contains one file."""
    return [s for s in allow if rel in closures.get(s, ())]


# ------------------------------------------------------------------- runner

def run_script(script: str, cwd: Path, timeout: int) -> tuple[int, int, float]:
    """(exit status, failed-check count, seconds) for one gate script.

    Reads the WHOLE of stdout: the last `N of M ... FAILED` line anywhere in it,
    not the tail of a buffer (#805).
    """
    started = time.monotonic()
    try:
        proc = subprocess.run(
            [sys.executable, script], cwd=cwd, capture_output=True, text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONPATH": "tests/hastub"},
        )
    except subprocess.TimeoutExpired:
        # A mutant that hangs its driver is noticed, not silently survived.
        return 124, 0, time.monotonic() - started
    hits = _FAILED.findall(proc.stdout)
    return proc.returncode, (int(hits[-1][0]) if hits else 0), time.monotonic() - started


def clone_tree(dest: Path) -> Path:
    """A real, independent checkout for one worker to mutate.

    `git worktree add` rather than a plain file copy, and the reason is
    measured: the first version copied files alone, the copy had no `.git`,
    and thirteen `tests/entities.py` checks plus one in `tests/features.py`
    failed there for the environment rather than for the code. A baseline that
    red makes every verdict after it meaningless -- which the baseline guard
    below caught, but a driver with fourteen broken checks cannot kill a
    mutant those checks were the ones to see.

    The worktree carries HEAD; the working tree is then overlaid on top of it,
    tracked edits and untracked-not-ignored files alike, so the mutants are
    driven against the tree in front of the seat rather than against its last
    commit. The object store is shared, so this costs a checkout and not the
    83 MB gitdir, four times over.
    """
    subprocess.run(
        ["git", "worktree", "add", "--detach", "--quiet", str(dest), "HEAD"],
        cwd=ROOT, check=True, capture_output=True,
    )
    listing = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, check=True, capture_output=True,
    ).stdout
    tar = subprocess.run(
        ["tar", "-c", "--null", "-T", "-", "-f", "-"], cwd=ROOT, check=True,
        input=listing, stdout=subprocess.PIPE,
    ).stdout
    subprocess.run(["tar", "-x", "-C", str(dest)], input=tar, check=True)
    return dest


def drop_tree(dest: Path) -> None:
    subprocess.run(
        ["git", "worktree", "remove", "--force", str(dest)],
        cwd=ROOT, capture_output=True,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", choices=("changed", "full"), default="changed")
    ap.add_argument("--base", default="origin/main")
    ap.add_argument(
        "--scripts",
        default="tests/open_meteo.py,tests/solar_alignment.py,tests/plan_view.py,"
                "tests/edge.py,tests/entities.py,tests/validate.py,"
                "tests/optimality.py,tests/features.py",
        help="candidate drivers; each mutant runs only those whose recorded "
             "closure contains its file, cheapest measured first",
    )
    ap.add_argument("--per-file", type=int, default=3,
                    help="cap per production file, so one big module cannot "
                         "crowd out every other file in scope")
    ap.add_argument("--max", type=int, default=8)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--seed", type=int, default=20260911)
    ap.add_argument("--timeout", type=int, default=1200)
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--reason", default="")
    args = ap.parse_args()
    # Line-buffered on purpose. A nightly whose whole table appears only when
    # the process exits shows NOTHING when its timeout kills it -- the one run
    # whose partial table is worth most.
    sys.stdout.reconfigure(line_buffering=True)

    budgets = json.loads(BUDGETS.read_text())
    cap = float(budgets["max_survivor_fraction"][args.scope])
    files, why = scope_files(args.scope, args.base)
    allow = [s for s in args.scripts.split(",") if s]
    closures = load_closures()
    print(f"MUTATION TABLE -- scope {args.scope}: {why}")
    if not files:
        print("  no production file in scope; nothing to mutate")
        print("\nMUTATION TABLE PASSED (empty scope)")
        return 0

    rng = random.Random(args.seed)
    pool: list[dict] = []
    for path in files:
        rel = str(path.relative_to(ROOT))
        drivers = drivers_for(rel, closures, allow)
        if not drivers:
            print(f"  no recorded closure reaches {rel}; skipped")
            continue
        got = list(candidates(path))
        rng.shuffle(got)
        for mut in got[: args.per_file]:
            mut["drivers"] = drivers
            pool.append(mut)
    rng.shuffle(pool)
    pool = pool[: args.max]
    if not pool:
        print("  no mutant is both generatable and drivable")
        print("\nMUTATION TABLE PASSED (empty pool)")
        return 0
    needed = sorted({s for mut in pool for s in mut["drivers"]})
    print(f"  {len(pool)} mutant(s) over {len(files)} file(s); "
          f"drivers in play: {', '.join(needed)}")

    work = Path(tempfile.mkdtemp(prefix="mutation-table-"))
    made: list[Path] = []
    try:
        base_tree = clone_tree(work / "baseline")
        made.append(base_tree)
        baseline: dict[str, tuple[int, int, float]] = {}
        for s in needed:
            rc, failed, secs = run_script(s, base_tree, args.timeout)
            baseline[s] = (rc, failed, secs)
            print(f"  baseline {s}: rc={rc} failed={failed} {secs:.0f}s")
        if any(rc != 0 for rc, _, _ in baseline.values()):
            print("\nMUTATION TABLE BREACHED")
            print("  - the baseline is already red, so no mutant's verdict "
                  "means anything. Fix the suite first.")
            return 1
        # Cheapest first, measured here rather than carried: a kill then costs
        # the cheapest driver that can see it.
        for mut in pool:
            mut["drivers"].sort(key=lambda s: baseline[s][2])

        jobs = max(1, min(args.jobs, len(pool)))
        trees = [clone_tree(work / f"w{i}") for i in range(jobs)]
        made.extend(trees)
        results: list[tuple[dict, str]] = []

        def drive(job: tuple[int, dict]) -> None:
            idx, mut = job
            tree = trees[idx % jobs]
            path = tree / mut["file"]
            lines = path.read_text().splitlines(True)
            i = mut["line"] - 1
            if i >= len(lines) or lines[i].rstrip("\n") != mut["old"]:
                results.append((mut, "SKIP-MOVED"))
                return
            lines[i] = mut["new"] + "\n"
            mutated = "".join(lines)
            try:
                ast.parse(mutated)
            except SyntaxError:
                # A mutant that cannot run reports as a survivor, and a survivor
                # reads as a finding about production. W5-G7 t5 measured two.
                results.append((mut, "SKIP-UNPARSEABLE"))
                return
            original = path.read_text()
            path.write_text(mutated)
            try:
                verdict = "LIVES"
                for s in mut["drivers"]:
                    rc, failed, _ = run_script(s, tree, args.timeout)
                    if rc != baseline[s][0] or failed > baseline[s][1]:
                        verdict = f"killed by {s}"
                        break
            finally:
                path.write_text(original)
            results.append((mut, verdict))

        with ThreadPoolExecutor(max_workers=jobs) as ex:
            # Serialised per worker tree by the index, so two mutants never
            # edit one copy at the same time.
            for i in range(jobs):
                ex.submit(lambda i=i: [drive((i, m))
                                       for m in pool[i::jobs]])
    finally:
        for tree in made:
            drop_tree(tree)
        subprocess.run(["git", "worktree", "prune"], cwd=ROOT,
                       capture_output=True)
        shutil.rmtree(work, ignore_errors=True)

    survivors = []
    for mut, verdict in sorted(results, key=lambda r: (r[0]["file"], r[0]["line"])):
        mark = "LIVES" if verdict == "LIVES" else (
            "SKIP " if verdict.startswith("SKIP") else "ok   ")
        note = "" if verdict in ("LIVES",) else f"  -- {verdict.lower()}"
        print(f"  {mark} {mut['file']}:{mut['line']} {mut['kind']}{note}")
        if verdict == "LIVES":
            survivors.append(mut)

    evaluated = sum(1 for _, v in results if not v.startswith("SKIP"))
    n = len(survivors)
    rate = n / evaluated if evaluated else 0.0
    print(f"\n  {n} survivor(s) of {evaluated} evaluated = {rate:.1%}, "
          f"cap {cap:.1%}")
    for mut in survivors:
        print(f"    {mut['file']}:{mut['line']} {mut['kind']}: "
              f"{mut['old'].strip()[:72]}")

    if args.record:
        if rate > cap:
            print("\nREFUSED to record: a cap only moves down. "
                  f"{rate:.1%} > the recorded {cap:.1%}; either kill the "
                  "survivors or raise it as a deliberate, argued edit.")
            return 1
        budgets["max_survivor_fraction"][args.scope] = round(rate, 4)
        budgets["last_measured"][args.scope] = {
            "survivors": n, "evaluated": evaluated,
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        if args.reason:
            budgets["reason"] = args.reason
        BUDGETS.write_text(json.dumps(budgets, indent=2) + "\n")
        print(f"\nRECORDED max_survivor_fraction[{args.scope}]={rate:.4f}")
        return 0
    if evaluated == 0:
        print("\nMUTATION TABLE PASSED (nothing evaluated)")
        return 0
    if rate > cap:
        print("\nMUTATION TABLE BREACHED")
        print(f"  - {rate:.1%} of mutants survived against a cap of {cap:.1%}. "
              "A survivor is a production line no check would notice being "
              "wrong. Pin the ones above, or argue in the body that they are "
              "equivalent mutants and raise the cap deliberately.")
        return 1
    print("\nMUTATION TABLE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

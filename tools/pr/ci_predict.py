#!/usr/bin/env python3
"""Predict, from the three-dot diff alone, the CI reds a fixer's head will meet.

WHY THIS EXISTS. Round 9's fix heads went to review and were then reddened by
two jobs whose repair a static read of the tree could have named first:
`closures` (a file no closure lists, a new import an existing closure does not
list, a new harness the INERT-read table does not list) and `mutation` (a site
the diff adds with no pin). The autofix jobs meant to repair them repaired
none of the twenty runs measured on this round's eight fix pull requests
(R9-RO-11's pre-study, in its PR body), so the red reached a reviewer's head
every time. That premise no longer holds for INERT READS: since #2049
(R9-CI-1) `closures-autofix` merges them, and since #2129 a scoped run
re-records the reading script, so the bot repairs one after the push
(run 38296697023: scoped, `AUTOFIX: changed`). It still refuses before the
push, because that repair costs a red `closures` run and a bot commit on the
reviewer's head; `--apply-inert` writes the entry the recording would, the
one repair a Darwin seat can make (the read is a child's, which only Linux
`strace` sees; dev/audit/rca/R10-RCA-INERT-PREDICT.md). Three arms call CI's own functions: UNCLASSIFIED
(`closure.orphan_files`), the INERT test inside both closure arms
(`closure.is_inert`), and ADDED UNPINNED (`mutation_table`'s source-only
ratchet). One is this predictor's own model, because CI learns the answer by
running: the import arm resolves imports statically where CI records them at
run time. (A fourth arm, NO RECORDING, read the `rec tests/...` lines of
`tests/derive_closures.sh`; round-9 C1 derived the full arm's recording set
from the tree and the class stopped being expressible -- `no_recording` below
says so where it stood.) Every arm is
scoped to what the three-dot diff adds or changes, so a red main already
carries is never charged to a branch. Nothing here runs a test, a recording
or a mutant: seconds, never a heavy script.

    python3 tools/pr/ci_predict.py [--base origin/main] [--apply-inert]

Prints one `PREDICT <job> ...` line per predicted red and a last line
`CI PREDICT: ...`. rc 1 when a closures or `fast` red is predicted, 0 when
none is, 2 when the base does not resolve. ADDED UNPINNED sites print but never
set the rc: `mutation-autofix` may pin them after the push (`ci-autofix.md`),
so `prepr.sh` step 6d warns and the body owes each one a disposition.
`--apply-inert` adds every predicted INERT READS entry to `tests/closures.json`
through `closure.write_closures`, then predicts again; the entry it writes is
an over-approximation at worst, the direction `_fold_inert_reads` keeps.

What it cannot see, said so the quiet line is not over-read: a data file a
script opens by name (#1987's `services.yaml`), a read behind a dynamic path,
and a closure whose recording a merge from `main` alone moves. Those stay
`closures`'s, and `ci-autofix.md` says who repairs them.
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path


def git(root: Path, *args: str) -> str | None:
    out = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else None


def show(root: Path, ref: str, path: str) -> str | None:
    return git(root, "show", f"{ref}:{path}")


# --- import edges -----------------------------------------------------------
# The roots a test process imports from: the repository (the package, as
# `custom_components.heatpump_optimizer`), `tests/` (each script's own dir)
# and `tests/hastub` (PYTHONPATH in every lane).
SEARCH = ("", "tests", "tests/hastub")


def imported_paths(src: str, path: str, tracked: set[str]) -> set[str]:
    """Tracked files the module at `path` imports, resolved statically."""
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError:
        return set()
    here = Path(path).parent
    found: set[str] = set()

    def resolve(parts: list[str], roots) -> None:
        for r in roots:
            base = Path(r).joinpath(*parts) if parts else Path(r)
            for cand in (f"{base}.py", f"{base}/__init__.py"):
                if cand in tracked:
                    found.add(cand)
                    return

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                resolve(a.name.split("."), SEARCH)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                pkg = here
                for _ in range(node.level - 1):
                    pkg = pkg.parent
                parts = node.module.split(".") if node.module else []
                roots = (str(pkg.joinpath(*parts)) if parts else str(pkg),)
                resolve([], roots)
                for a in node.names:
                    resolve([a.name], roots)
            elif node.module:
                parts = node.module.split(".")
                resolve(parts, SEARCH)
                for a in node.names:
                    resolve(parts + [a.name], SEARCH)
    found.discard(path)
    return found


def module_level_imports(root: Path, path: str, tracked: set[str]) -> set[str]:
    """Imports at a module's top level only: what importing it executes."""
    try:
        src = (root / path).read_text()
    except (OSError, UnicodeDecodeError):
        return set()
    return top_imports(src, path, tracked)


def top_imports(src: str, path: str, tracked: set[str]) -> set[str]:
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError:
        return set()
    top = ast.Module(body=[n for n in tree.body
                           if isinstance(n, (ast.Import, ast.ImportFrom))],
                     type_ignores=[])
    return imported_paths(ast.unparse(top), path, tracked)


def under_scoped(root, base, changed, tracked, closures, inert_reads, closure,
                 pairs=None):
    """New import edges from a file a closure lists to a file it does not.

    Only edges this diff ADDS: an edge already present at the base and still
    absent from a recorded closure is a lazy import the recording never
    executed, which the committed table already reflects. A new edge's target
    is followed through ITS top-level imports, which importing it executes.
    """
    hits: dict[tuple[str, str], tuple[set[str], set[str]]] = {}
    for a in sorted(changed):
        if not a.endswith(".py") or a not in tracked:
            continue
        try:
            head_src = (root / a).read_text()
        except (OSError, UnicodeDecodeError):
            continue
        old = show(root, base, a)
        # Top-level edges only: an import inside a function runs only when a
        # script calls it, which no static read can tell (#1987's
        # quiet_windows -> silent_mode edge sits in a function guard_pins
        # never calls, and `closures` stayed green on it).
        new_edges = top_imports(head_src, a, tracked) - (
            top_imports(old, a, tracked) if old is not None else set())
        if not new_edges:
            continue
        reach = set(new_edges)
        todo = list(new_edges)
        while todo:
            for nxt in module_level_imports(root, todo.pop(), tracked):
                if nxt not in reach:
                    reach.add(nxt)
                    todo.append(nxt)
        # A closure that lists `a` may only READ it (structure.py parses the
        # package as text). It EXECUTES `a` when it lists every module `a`
        # imported at its top level at the base: that is what importing `a`
        # ran there.
        ran = top_imports(old, a, tracked) if old is not None else set()
        if not ran:
            continue
        for script, files in closures.items():
            listed = set(files)
            if a not in listed or not ran <= listed:
                continue
            for b in sorted(reach):
                if b.startswith("tests/hastub/"):
                    # The stub is every importer's, already listed by any
                    # script that imports the package; a reader that lists
                    # the package as text and not the stub executes neither.
                    continue
                if closure.is_inert(b):
                    if b in set(inert_reads.get(script, [])):
                        continue
                    kind = "INERT READS"
                    if pairs is not None:
                        pairs.add((script, b))
                elif b not in listed:
                    kind = "UNDER-SCOPED"
                else:
                    continue
                scripts, froms = hits.setdefault((kind, b), (set(), set()))
                scripts.add(script)
                froms.add(a)
    return [("closures", f"{kind} {b}: read by {len(sc)} script(s) whose "
             f"closure omits it ({', '.join(sorted(sc)[:3])}"
             f"{', ...' if len(sc) > 3 else ''}), a new import from "
             f"{', '.join(sorted(fr)[:2])}{', ...' if len(fr) > 2 else ''}")
            for (kind, b), (sc, fr) in sorted(hits.items())]


def inert_siblings(changed, inert_reads, closure, pairs=None):
    """A new INERT file beside files a script's INERT-read list names.

    A script that reads a directory by glob (`harness_headers.py` over
    `dev/audit/harnesses/`) opens every file added there; its committed
    `inert_reads` lists them one by one, so a new sibling it does not list is
    CI's `INERT READS UNDER-APPROXIMATED`. Keyed on directory and suffix: three
    listed siblings of the same suffix, so the two files `entities.py` names
    one by one in `tools/audit/seat/` are not mistaken for a glob.
    """
    preds = []
    for f in sorted(changed):
        if not closure.is_inert(f):
            continue
        d, suf = str(Path(f).parent), Path(f).suffix
        for script, files in inert_reads.items():
            if f in files:
                continue
            sib = [g for g in files if str(Path(g).parent) == d and Path(g).suffix == suf]
            if len(sib) >= 3:
                preds.append(("closures", f"INERT READS {script}: {f} "
                              f"(a new file beside {len(sib)} it lists)"))
                if pairs is not None:
                    pairs.add((script, f))
    return preds


def no_recording(root, base, changed, closure):
    """Nothing, since round-9 C1 planned the full arm.

    This arm read the ``rec tests/...`` lines of ``tests/derive_closures.sh``
    and predicted `NO recording this run` for a selectable script the diff
    added that no lane named, or whose name a lane edit dropped. The full
    arm's recording set is now derived from the tree (``lane-plan
    --all-scripts``: every runnable test script but the SLOW_GATED ones), so
    there is no lane file a new selectable script has to be added to and no
    line whose deletion could drop a recording -- the class cannot fire.
    The job's own missing-recording check holds the derive against the same
    derived roster, so a dropped recording is loud on CI without a
    prediction.
    """
    return []


def orphans(changed, closure):
    """A changed file in no closure and on no list: entities.py's refusal."""
    return [("fast", f"UNCLASSIFIED {f}: in no measured closure and not on "
             f"INERT -- tests/entities.py refuses it, and every script that "
             f"imports it is UNDER-SCOPED")
            for f in closure.orphan_files() if f in changed]


def stale_pin_preds(problems, base):
    """`completeness_problems` lines as ledger predictions, scoped to the diff.

    A problem line starts `FILE:SCOPE KIND DIGEST[#N]: ...`. It refuses when
    FILE or the pin's own file under tests/mutation_ledger/ is in the diff;
    otherwise it is main's, and prints as a warning job (`mutation`).
    """
    names = git(Path.cwd(), "diff", "--name-only", "--no-renames", f"{base}...HEAD") or ""
    changed = set(names.split())
    ledger = [c.rsplit("/", 1)[-1] for c in changed if c.startswith("tests/mutation_ledger/")]
    out = []
    for p in problems:
        key = p.split(": ", 1)[0]
        file_, _, rest = key.partition(":")
        parts = rest.split(" ")
        stem = ""
        if len(parts) == 3:
            stem = f"{parts[0]}.{parts[1]}.{parts[2].split('#')[0]}"
        mine = file_ in changed or (stem and any(n.startswith(stem) for n in ledger))
        out.append(("ledger", f"STALE PIN {p}") if mine else
                   ("mutation", f"STALE PIN ON MAIN (not this diff's) {p}"))
    return out


def unpinned(base):
    """`mutation`'s source-only ratchet, CI's own functions, no mutant run."""
    import mutation_table as m
    budgets = m.load_budgets()
    sites = m.inventory()
    pinned_out = m.unpinned_sites(budgets, sites)
    # The other direction (RCA stale-pins): a pin whose site the diff edited,
    # moved or deleted. `mutation` refuses it from the same `inventory()` this
    # already ran, and `mutation-autofix` only adds pins, never drops one.
    # Diff-scoped like every other refusing arm: a stale pin main already
    # carries is the orchestrator's, so it warns and names main.
    stale = stale_pin_preds(m.completeness_problems(budgets, sites), base)
    base_sites = m.base_unpinned_sites(base, sites)
    if base_sites is None:
        return stale + [("mutation", f"BASE UNREADABLE {base}: the ratchet has nothing "
                 f"to compare against, and CI refuses that too")]
    added = m.added_unpinned(pinned_out, base_sites, m.diff_sides(base))
    return stale + [("mutation", f"ADDED UNPINNED {k}: {s['old'].strip()[:60]}")
                    for k, s in m.added_keys(added)]


def predict(root: Path, base_ref: str, pairs: set | None = None
            ) -> tuple[int, list[tuple[str, str]], str]:
    base = (git(root, "merge-base", base_ref, "HEAD") or "").strip()
    if not base:
        return 2, [], f"no merge base between {base_ref} and HEAD"
    sys.path[:0] = [str(root / "tests"), str(root / "tests" / "hastub")]
    import closure
    names = git(root, "diff", "--name-only", "--no-renames", f"{base}...HEAD") or ""
    tracked = set((git(root, "ls-files") or "").split())
    changed = {p for p in names.split() if p in tracked}
    table = json.loads((root / "tests" / "closures.json").read_text())
    closures, inert_reads = table["closures"], table.get("inert_reads", {})
    preds: list[tuple[str, str]] = []
    preds += orphans(changed, closure)
    preds += no_recording(root, base, changed, closure)
    preds += under_scoped(root, base, changed, tracked, closures, inert_reads,
                          closure, pairs)
    preds += inert_siblings(changed, inert_reads, closure, pairs)
    preds += unpinned(base)
    seen, out = set(), []
    for p in preds:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return (1 if any(j != "mutation" for j, _ in out) else 0), out, base


def apply_inert(root: Path, pairs: set) -> list[tuple[str, str]]:
    """Add each (script, file) to `inert_reads` through the table's one writer.

    What CI's Linux recording would merge: the read is a child process's, so
    a Darwin `--single` cannot record it, and a hand edit of the JSON is the
    layout `closure.layout_errors` refuses. Returns the pairs it added.
    """
    import closure
    path = root / "tests" / "closures.json"
    payload = json.loads(path.read_text())
    table = payload.setdefault("inert_reads", {})
    added = sorted(p for p in pairs if p[1] not in table.get(p[0], ()))
    for script, f in added:
        table[script] = sorted(set(table.get(script, ())) | {f})
    if added:
        closure.write_closures(path, payload)
    return added


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--apply-inert", action="store_true",
                    help="write every predicted INERT READS entry, then predict again")
    args = ap.parse_args(argv)
    root = Path((git(Path.cwd(), "rev-parse", "--show-toplevel") or ".").strip())
    pairs: set[tuple[str, str]] = set()
    rc, preds, base = predict(root, args.base, pairs)
    if args.apply_inert and rc != 2:
        added = apply_inert(root, pairs)
        for script, f in added:
            print(f"APPLIED inert_reads {script}: {f}")
        if added:
            rc, preds, base = predict(root, args.base)
    if rc == 2:
        print(f"CI PREDICT: {base}")
        return 2
    for job, line in preds:
        print(f"PREDICT {job:<8} {line}")
    if any(j == "ledger" for j, _ in preds):
        print("CI PREDICT: a STALE PIN's file under tests/mutation_ledger/ is "
              "deleted by hand; `mutation-autofix` never drops one, and pins "
              "the edited line afresh once it is gone")
    jobs = sorted({j for j, _ in preds if j != "mutation"})
    sites = sum(1 for j, l in preds if j == "mutation" and l.startswith("ADDED"))
    if sites:
        print(f"CI PREDICT: {sites} unpinned site(s) the diff adds -- a "
              f"warning; the body owes each a line under ## Unpinned sites")
    if any(j == "closures" and l.startswith("INERT READS") for j, l in preds):
        print("CI PREDICT: an INERT READS entry is written with "
              "`python3 tools/pr/ci_predict.py --apply-inert` and committed; "
              "a Darwin --single cannot record a child's read, and the bot's "
              "repair costs a red closures run and a commit on the reviewed head")
    if jobs:
        reds = sum(1 for j, _ in preds if j != "mutation")
        print(f"CI PREDICT: {reds} predicted red(s) on {', '.join(jobs)} "
              f"against {base[:12]} -- repair before the handoff; who repairs "
              f"which is ci-autofix.md's")
    else:
        print(f"CI PREDICT: no closures or fast red predicted against "
              f"{base[:12]} (a data-file read is not seen)")
    return rc


if __name__ == "__main__":
    sys.exit(main())

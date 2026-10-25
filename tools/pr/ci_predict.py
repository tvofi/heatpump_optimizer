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
reviewer's head; `--apply-inert` writes the entry the recording would, which
for a child process's read (harness_headers' scan) is the one repair a Darwin
seat can make, since only Linux `strace` sees it
(dev/audit/rca/R10-RCA-INERT-PREDICT.md). Four arms call CI's own functions: UNCLASSIFIED
(`closure.orphan_files`), the INERT test inside both closure arms
(`closure.is_inert`), ADDED UNPINNED (`mutation_table`'s source-only
ratchet), and LAYOUT (`layout.guard`, the guard `fast` runs, which refuses a
diff re-adding a moved path or citing one: #2554's forward-carry, since
`prepr.sh` ran it and `body_push.sh`, which runs only this, did not). Two
more run CI's own command where no local path ran it the way CI does
(dev/audit/rca/R10-RCA-2671-WAVE-SCRIPT.md): REF PRIVACY
(`ref_privacy.py --check`, `instrument-self-tests`, which no local path ran)
and AGREEMENT (`wave-script`'s agreement lane under the base's copy, as the
pull request is graded, where `prepr.sh` step 3f4 runs the head's). One is this predictor's own model, because CI learns the answer by
running: the import arm resolves imports statically where CI records them at
run time. (A fourth arm, NO RECORDING, read the `rec tests/...` lines of
`tests/derive_closures.sh`; round-9 C1 derived the full arm's recording set
from the tree and the class stopped being expressible -- `no_recording` below
says so where it stood.) Every arm is
scoped to what the three-dot diff adds or changes, so a red main already
carries is never charged to a branch. Nothing here runs a test, a recording
or a mutant: seconds, never a heavy script, but for AGREEMENT, which runs the
lane in a throwaway clone (about 10 s) and only on a diff to a file it loads.

    python3 tools/pr/ci_predict.py [--base origin/main] [--apply-inert] [--body FILE]
    python3 -I tools/pr/ci_predict.py --self-test

Prints one `PREDICT <job> ...` line per predicted red and a last line
`CI PREDICT: ...`. rc 1 when any red but `mutation`'s is predicted, 0 when
none is, 2 when the base does not resolve. ADDED UNPINNED sites print but never
set the rc: `mutation-autofix` may pin them after the push (`ci-autofix.md`),
so `prepr.sh` step 6d warns and the body owes each one a disposition.
`--apply-inert` adds every predicted INERT READS entry to `tests/closures.json`
through `closure.write_closures`, then predicts again; the entry it writes is
an over-approximation at worst, the direction `_fold_inert_reads` keeps.

`--body FILE` adds a fifth arm, the carry check `pr-contract` runs on the body
(R10-CI-LAYOUT-P2 carry 6): `tools/audit/carry_audit.py`'s own `audit`, imported
from the checkout under test and never restated, so a finding item routed to a
destination the roster lacks is predicted as `PREDICT pr-contract / pr-contract
CARRY ...` and sets the rc. It runs only when a body is given.

Job names are the check names of `ci.yml`'s units (`tests / closures`, ...,
`JOB` below); `ledger` is no check, only the file a stale pin leaves behind.

What it cannot see, said so the quiet line is not over-read: a data file a
script opens by name (#1987's `services.yaml`), a read behind a dynamic path,
and a closure whose recording a merge from `main` alone moves. Those stay
`closures`'s, and `ci-autofix.md` says who repairs them. What it does see it
names the repair for, per arm, on a `CI PREDICT:` line: before a PR exists no
bot runs, so a predicted red is the fixer's (R10-HANDOFF-PREPR-BOUNCE M3).
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path


# The check name each internal arm key is CI's after the layout cut-over
# (DESIGN-P2 section 9); gate.REQUIRED pins every value but `ledger`.
JOB = {"closures": "tests / closures", "fast": "tests / fast (3.14)",
       "mutation": "tests / mutation", "carry": "pr-contract / pr-contract",
       "wave-script": "governance / wave-script", "instrument": "governance / instrument-self-tests"}


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
                 pairs=None, scripts=None):
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
                    if scripts is not None:
                        scripts.add(script)
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
    listed siblings of the same suffix, so the one file `entities.py` names
    in `tools/audit/seat/` is not mistaken for a glob. A sibling counts only
    while it is INERT: a glob files nothing else under `inert_reads`, and an
    entry whose file later left the list stays listed -- `entities.py`'s five
    in `tools/audit/seat/` (R10-CI-LAYOUT-P1: CI's FULL closures run was green
    at e93de866 with `orchestrator_tick.py` changed and unlisted).
    """
    preds = []
    for f in sorted(changed):
        if not closure.is_inert(f):
            continue
        d, suf = str(Path(f).parent), Path(f).suffix
        for script, files in inert_reads.items():
            if f in files:
                continue
            sib = [g for g in files if str(Path(g).parent) == d and Path(g).suffix == suf
                   and closure.is_inert(g)]
            if len(sib) >= 3:
                preds.append(("closures", f"INERT READS {script}: {f} "
                              f"(a new file beside {len(sib)} it lists)"))
                if pairs is not None:
                    pairs.add((script, f))
    return preds


def left_inert(changed, closures, inert_reads, closure, scripts=None):
    """A file this diff's INERT edit took out of INERT that a closure omits.

    The committed table files a Python child's read of an INERT file under
    `inert_reads` alone (`closure.strace_files` splits by the classifier that
    recorded it). Once `tests/closure.py` excepts the file, a recording at
    this head files the read in the closure, so a closure that omits it is
    CI's UNDER-SCOPED: probe B2's harness_headers.py on r10_ci_layout_u5's
    run_part.py and unitcheck.py (job 120398407061), which 6b never records
    because a closure.py edit makes the case FULL. Charged only to a diff
    that edits tests/closure.py, so main's own table is never a branch's red.
    """
    if "tests/closure.py" not in changed:
        return []
    preds = []
    for script, files in sorted(inert_reads.items()):
        listed = set(closures.get(script, ()))
        for f in sorted(files):
            if f not in listed and not closure.is_inert(f):
                preds.append(("closures", f"UNDER-SCOPED {script}: {f} leaves INERT "
                              f"in this diff; the table lists it under inert_reads "
                              f"only, and a recording at this head files it in the closure"))
                if scripts is not None:
                    scripts.add(script)
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


def carry_preds(root: Path, body: str) -> list[tuple[str, str]]:
    """`pr-contract`'s carry_audit check over the body: CI's own function.

    `carry_audit.audit` is the check `pr-contract` runs (`carry_audit.py check
    --body`); a row that is not routed is the line it would print.
    """
    sys.path.insert(0, str(root / "tools" / "audit"))
    try:
        import carry_audit
        res = carry_audit.audit(Path(body).read_text(), [], carry_audit.load_dests(root))
    except Exception as e:  # a roster the tree cannot read is a red CI would also print
        return [("carry", f"CARRY UNREADABLE {type(e).__name__}: {e}")]
    finally:
        sys.path.pop(0)
    return [("carry", f"CARRY {r['status'].upper()} item {r['id']}"
             + (f" ({'; '.join(r['bad'])})" if r["bad"] else "")
             + f": {' '.join(r['text'].split())[:80]!r}")
            for r in res["rows"] if r["status"] != "routed"]


def layout_preds(root: Path, base: str) -> list[tuple[str, str]]:
    """The layout guard `fast` runs (`tests/layout.py`, run_always): CI's own
    `guard`, over the commit HEAD against the merge base and with HEAD's
    manifest, so what is predicted is what is pushed, as every other arm.

    CI runs it on a checkout of the head, whose index is that commit; the
    guard's `rev` form reads the commit instead of the index, the form its
    own `--replay` uses. A tree with no layout guard has none to predict; a
    guard that raises is a red CI would also print.
    """
    if not (root / "tests" / "layout.py").exists():
        return []
    try:
        import layout
        manifest = json.loads(show(root, "HEAD", layout.MANIFEST) or "")
        found = layout.guard(root, manifest, base, "HEAD")
    except Exception as e:
        return [("fast", f"LAYOUT UNREADABLE {type(e).__name__}: {e}")]
    return [("fast", f"LAYOUT {f}") for f in found]


def privacy_preds(root: Path) -> list[tuple[str, str]]:
    """`instrument-self-tests`'s `ref_privacy.py --check`, which no local path
    ran (dev/audit/rca/R10-RCA-2671-WAVE-SCRIPT.md, countermeasure B): its own
    registry and content checks over the commit HEAD, judged with the
    runner's identity as CI's run is. Its run on a seat adds the seat's home
    and name, which CI never judges by, and matches the home as a substring:
    the root account's home is inside the path of the root-cause role
    contract, which 28 tracked files cite.
    """
    seat = root / "tools" / "audit" / "seat"
    if not (seat / "ref_privacy.py").is_file():
        return []
    sys.path.insert(0, str(seat))
    try:
        import ref_privacy as rp
        found = rp.sites(rp.grep("HEAD"))
        bad = (rp.registry_refusals(found, lambda p: show(root, "HEAD", p) or "") if found
               else ["the scan found no push site at all, so it checked nothing"])
        runner = rp.Identity.made(("/".join(("", "home", "runner")),), ("runner",), None)  # built: a spelled
        bad += rp.content_check("HEAD", root, runner)[2]                                    # home is refused
    except Exception as e:
        bad = [f"UNREADABLE {type(e).__name__}: {e}"]
    return [("instrument", f"REF PRIVACY REFUSE {b}") for b in bad]


# The agreement lane at either layout, in the order `wave-script` tries them.
AGREEMENT = (".claude/workflows/agreement.mjs", "tools/policy/agreement.mjs")
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def lane_files(root: Path) -> set[str]:
    """What the agreement lane loads: agreement_py.py's own `closure` (its
    restore precondition's list) and agreement.mjs's, its relative imports and
    `load`/`at` literals over every .mjs file those reach."""
    import layout
    mjs = next((p for p in AGREEMENT if (root / p).is_file()
                and (root / p).with_name("agreement_py.py").is_file()), None)
    if mjs is None:
        return set()
    sys.path.insert(0, str(root / Path(mjs).parent))
    import agreement_py
    seen = set(agreement_py.closure(root, root / Path(mjs).with_name("agreement_py.py")))
    stack = [mjs]
    while stack:
        p = layout.locate(stack.pop(), root=root)
        if p in seen or not p.endswith(".mjs") or not (root / p).is_file():
            continue
        seen.add(p)
        src = (root / p).read_text()
        stack += [str(Path(p).parent / m) for m in re.findall(r"from '(\./[^']+)'", src)]
        stack += re.findall(r"\b(?:load|at)\('([^']+)'\)", src)
    return seen


def agreement_preds(root: Path, base_ref: str, changed: set[str]) -> list[tuple[str, str]]:
    """`wave-script`'s agreement lane as CI runs it on the pull request: the
    merge of HEAD into the base tip (base first), the job's restore pathspecs
    checked out from that tip, in a clone whose origin/main is the tip (a live
    origin/main past the PR moves the merge-subject walk onto its own merges).

    prepr.sh step 3f4 runs the head's copy, push-to-main's direction; the two
    differ only where the diff edits a file the lane loads, so that diff is
    the key (dev/audit/rca/R10-RCA-2671-WAVE-SCRIPT.md, countermeasure A:
    #2671's registration passed 3f4 and was UNREGISTERED under the base's
    copy). A base without the lane runs none, as the job skips it.
    """
    hit = sorted(changed & lane_files(root))
    tip = (git(root, "rev-parse", "--verify", f"{base_ref}^{{commit}}") or "").strip()
    if not hit or not tip or not any(git(root, "cat-file", "-e", f"{tip}:{p}") is not None for p in AGREEMENT):
        return []
    import shutil
    import tempfile
    import agreement_py
    from throwaway_git import throwaway_git_clone
    head = (git(root, "rev-parse", "HEAD") or "").strip()
    tmp = Path(tempfile.mkdtemp(prefix="hpo-ci-predict-agreement-"))
    r = tmp / "r"
    try:
        env = throwaway_git_clone(root, r, "-q", "--shared", "--no-checkout")

        def run(*a: str) -> subprocess.CompletedProcess:
            return subprocess.run(a, cwd=r, env=env, capture_output=True, text=True)

        run("git", "update-ref", "refs/remotes/origin/main", tip)
        run("git", "checkout", "-q", "--detach", tip)
        if run("git", "merge", "-q", "--no-ff", "-m", f"Merge {head} into {tip}", head).returncode:
            return [("wave-script", f"AGREEMENT UNMERGED: HEAD does not merge into {tip[:12]}, "
                                    f"and CI runs nothing on a conflict; merge the base first")]
        shutil.rmtree(r / ".claude" / "workflows" / "vendor", ignore_errors=True)
        specs = agreement_py.restore_specs((r / agreement_py.WORKFLOW).read_text())
        (tmp / "pinned.list").write_text(run("git", "diff", "--no-renames", "--name-only", "-z", EMPTY_TREE, tip, "--", *specs).stdout)
        run("git", "checkout", tip, f"--pathspec-from-file={tmp / 'pinned.list'}", "--pathspec-file-nul")
        py = next(p for p in (".claude/workflows/agreement_py.py", "tools/policy/agreement_py.py") if (r / p).is_file())
        out = run(sys.executable, "-I", py, "--out", str(tmp / "agreement.json"))
        if out.returncode == 0:
            out = run("node", next(p for p in AGREEMENT if (r / p).is_file()), "--py-json", str(tmp / "agreement.json"))
    except (OSError, StopIteration, ValueError) as e:
        return [("wave-script", f"AGREEMENT UNRUN {type(e).__name__}: {e}")]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if out.returncode == 0:
        return []
    lines = [l for l in out.stdout.splitlines() if l.strip()] or [f"rc {out.returncode}: {out.stderr.strip()[-200:]}"]
    why = [l.strip() for l in lines if l.split()[0] in ("UNRESTORED", "DIVERGENT", "UNREGISTERED", "DEAD", "REFUSED")]
    result = next((l for l in reversed(lines) if l.startswith("RESULT ")), lines[-1].strip())
    return [("wave-script", f"AGREEMENT {result} (the base's copy, over {', '.join(hit)})")] + \
           [("wave-script", f"AGREEMENT {w}") for w in why]


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


def predict(root: Path, base_ref: str, pairs: set | None = None,
            scripts: set | None = None, body: str | None = None) -> tuple[int, list[tuple[str, str]], str]:
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
    preds += layout_preds(root, base)
    preds += privacy_preds(root)
    preds += agreement_preds(root, base_ref, changed)
    preds += no_recording(root, base, changed, closure)
    preds += under_scoped(root, base, changed, tracked, closures, inert_reads,
                          closure, pairs, scripts)
    preds += inert_siblings(changed, inert_reads, closure, pairs)
    preds += left_inert(changed, closures, inert_reads, closure, scripts)
    preds += unpinned(base)
    if body:
        preds += carry_preds(root, body)
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


def repairs(root: Path, preds, scripts: set) -> list[str]:
    """The repair line for each refusing closures/fast arm, before the handoff.

    Before a PR exists no bot runs, so the arm's repair is the fixer's
    (dev/audit/rca/R10-HANDOFF-PREPR-BOUNCE.md, countermeasure M3): a closure
    is re-recorded with `--single` per script, whose cost is what CI's last
    recording of it took (one took five times that on a Darwin seat, the RCA's
    section 1), and a file in no closure is classified in the same diff.
    """
    out = []
    if scripts:
        rec = json.loads((root / "tests" / "closures.json").read_text()).get("recorded", {})
        secs = sum(float(rec.get(s, {}).get("seconds") or 0) for s in scripts)
        many = len(scripts) > 3
        out.append(f"an UNDER-SCOPED closure is re-recorded in the diff, one script at a time: "
                   f"{'; '.join(f'tests/derive_closures.sh --single {s}' for s in sorted(scripts))} "
                   f"(CI's last recordings of the {len(scripts)} took {secs:.0f} s in all)"
                   + ("; that many is the orchestrator's to record on Linux, asked for before the handoff"
                      if many else ""))
    if any(j == "fast" and l.startswith("LAYOUT") for j, l in preds):
        out.append("a LAYOUT refusal is repaired in the diff as `python3 -I tests/layout.py --guard` "
                   "names it: a re-added moved path goes where it lives, a citation is re-pointed to "
                   "its new path, and a new file goes where tests/layout.json says")
    if any(j == "wave-script" for j, _ in preds):
        out.append("an AGREEMENT refusal is CI's verdict under the base's copy of the lane, so an edit to "
                   "the lane is graded by the copy it replaces: repair what the base's copy refuses, and a "
                   "registration only the head's copy carries has no local repair "
                   "(dev/audit/rca/R10-RCA-2671-WAVE-SCRIPT.md, cause 3): the body names it under ## Red checks")
    if any(j == "instrument" for j, _ in preds):
        out.append("a REF PRIVACY refusal is repaired as `python3 -I tools/audit/seat/ref_privacy.py --check` "
                   "names it: a push site guarded and registered in PUSHERS, a published host path scrubbed")
    if any(j == "fast" and l.startswith("UNCLASSIFIED") for j, l in preds):
        out.append("an UNCLASSIFIED file is classified in the diff (CLAUDE.md): one a test script reads joins "
                   "that script's closure through tests/derive_closures.sh --single <script>; one no script "
                   "reads goes on INERT in tests/closure.py")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--apply-inert", action="store_true",
                    help="write every predicted INERT READS entry, then predict again")
    ap.add_argument("--body", help="the pull-request body: also predict pr-contract's carry check")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    root = Path((git(Path.cwd(), "rev-parse", "--show-toplevel") or ".").strip())
    pairs: set[tuple[str, str]] = set()
    scripts: set[str] = set()
    rc, preds, base = predict(root, args.base, pairs, scripts, args.body)
    if args.apply_inert and rc != 2:
        added = apply_inert(root, pairs)
        for script, f in added:
            print(f"APPLIED inert_reads {script}: {f}")
        if added:
            scripts = set()
            rc, preds, base = predict(root, args.base, None, scripts, args.body)
    if rc == 2:
        print(f"CI PREDICT: {base}")
        return 2
    for job, line in preds:
        print(f"PREDICT {JOB.get(job, job):<8} {line}")
    if any(j == "ledger" for j, _ in preds):
        print("CI PREDICT: a STALE PIN's file under tests/mutation_ledger/ is "
              "deleted by hand; `mutation-autofix` never drops one, and pins "
              "the edited line afresh once it is gone")
    jobs = sorted({JOB.get(j, j) for j, _ in preds if j != "mutation"})
    sites = sum(1 for j, l in preds if j == "mutation" and l.startswith("ADDED"))
    if sites:
        print(f"CI PREDICT: {sites} unpinned site(s) the diff adds -- a "
              f"warning; the body owes each a line under ## Unpinned sites")
    inert = sum(1 for j, l in preds if j == "closures" and l.startswith("INERT READS"))
    if inert:
        print("CI PREDICT: an INERT READS entry is written with "
              "`python3 tools/pr/ci_predict.py --apply-inert` and committed: "
              "the entry CI's Linux recording would merge, before the push, "
              "where the bot's repair after it costs a red closures run and a "
              "commit on the reviewed head")
    for line in repairs(root, preds, scripts):
        print(f"CI PREDICT: {line}")
    if jobs:
        reds = sum(1 for j, _ in preds if j != "mutation")
        who = ("`--apply-inert` repairs them" if inert == reds else
               f"`--apply-inert` repairs the {inert} INERT READS, the lines "
               f"above the rest" if inert else
               "the lines above name each arm's repair")
        print(f"CI PREDICT: {reds} predicted red(s) on {', '.join(jobs)} "
              f"against {base[:12]} -- repair before the handoff; {who}")
    else:
        print(f"CI PREDICT: no closures, fast, wave-script or instrument red predicted against "
              f"{base[:12]} (a data-file read is not seen)")
    return rc


def self_test() -> int:
    """The carry arm over a plant and a null, through carry_audit's own audit."""
    import tempfile
    root = Path((git(Path.cwd(), "rev-parse", "--show-toplevel") or ".").strip())
    sys.path.insert(0, str(root / "tools" / "audit"))
    import carry_audit
    grp = next(n for n, g in carry_audit.load_dests(root).groups.items()
               if carry_audit.roster_lib.is_open(g))
    body = "## Forward-carry\n\n- %s\n\n  Carry: %s\n"
    cases = [("a carry to a group of the roster is predicted green", body % ("a finding", grp), 0),
             ("a carry to a group the roster lacks is predicted red", body % ("a finding", "R10-NO-SUCH-GROUP"), 1),
             ("a finding with no carry at all is predicted red", "## Forward-carry\n\n- a finding\n", 1)]
    bad = 0
    for label, text, want in cases:
        with tempfile.NamedTemporaryFile("w", suffix=".md") as f:
            f.write(text)
            f.flush()
            got = 1 if carry_preds(root, f.name) else 0
        print(f"  {'ok  ' if got == want else 'FAIL'} {label}")
        bad += got != want
    bad += plant_self_test(root)
    gate = root / "tools" / "ci" / "gate.py"
    if gate.exists():
        sys.path.insert(0, str(root / "tools" / "ci"))
        import gate as g
        pinned = set(g.REQUIRED["pr"])
        # instrument-self-tests is no required context: its red blocks no merge, and is
        # predicted because a red check is still owed an answer (defect-root-cause.md).
        miss = [v for k, v in JOB.items() if k not in ("carry", "instrument") and v not in pinned]
        print(f"  {'ok  ' if not miss else 'FAIL'} every JOB value is a name gate.REQUIRED owes{' -- ' + str(miss) if miss else ''}")
        bad += bool(miss)
    print(f"ci_predict self-test: {bad} failed")
    return 1 if bad else 0


# The home the self-test's predictor runs under: a seat's, which CI never judges by.
SEAT_HOME = "/opt/hpo-ci-predict-seat"


def plant_self_test(root: Path) -> int:
    """The layout, REF PRIVACY and AGREEMENT arms end to end: the predictor as
    a process over a throwaway clone of this head, each plant a commit (or
    two) on a base holding this file, each arm's repair line beside its red.

    LAYOUT plants are the guard's own refusals of a landed move, read from
    this tree's tests/layout.json: the file re-added at its old path, then
    under a second commit (the guard reads the merge base, not HEAD's parent),
    then with that entry dropped from the manifest, staged and not
    committed (HEAD's manifest is the one pushed), a citation of it, and a
    manifest that does not parse. REF PRIVACY's are an unregistered push site
    and a guarded pusher's guard dropped in HEAD but restored in the index.
    AGREEMENT's is #2671's shape, a grammar in two files registered only in
    the head's agreement.mjs, which the base's copy finds UNREGISTERED. The
    nulls: a line that cites, pushes and registers nothing, each red plant
    staged and not committed (what is pushed is HEAD), a line naming the
    seat's home (CI judges with the runner's identity), a head copy of
    agreement.mjs that exits 1 at once (CI never runs it), a grammar the base
    tip registers and shares (CI grades HEAD merged into the tip, not HEAD
    alone), and an unregistered grammar in files the lane does not load (the
    key: prepr step 3f4 refuses that under either copy, so the arm need not).
    """
    import shutil
    import tempfile
    sys.path.insert(0, str(root / "tests"))
    try:
        from throwaway_git import throwaway_git_clone
    finally:
        sys.path.pop(0)
    manifest = json.loads((root / "tests" / "layout.json").read_text())
    tracked = set((git(root, "ls-files") or "").split())
    dirs = {p[:i + 1] for p in tracked for i, c in enumerate(p) if c == "/"}
    old = next((r["old"] for r in manifest["retired"] if r.get("new") and not r["old"].endswith("/")
                and r["old"] not in tracked | dirs), None)
    ag = next((p for p in AGREEMENT if p in tracked), None)
    sys.path.insert(0, str(root / "tools" / "audit" / "seat"))
    try:
        import ref_privacy as rp
    finally:
        sys.path.pop(0)
    guarded = next((p for p, (kind, _) in sorted(rp.PUSHERS.items()) if kind == rp.GUARDED and p in tracked), None)
    if old is None or ag is None or guarded is None:
        print("  FAIL the plants have a landed retired file to re-add, an agreement lane to register in "
              "and a guarded pusher")
        return 1

    def app(text):
        return lambda s: s + text

    def unlisted(s):
        m = json.loads(s)
        m["retired"] = [e for e in m["retired"] if e["old"] != old]
        return json.dumps(m)

    def unguard(s):
        return s.replace("ref_privacy", "ref_privacx")

    def reguard(s):
        return s.replace("ref_privacx", "ref_privacy")

    grammar = 'import re\n_CI_PREDICT_PLANT = re.compile(r"ci-predict-plant-(\\d+)-x")\n'
    register = {ag: lambda s: s.replace("const SHARED_GRAMMARS = {\n", "const SHARED_GRAMMARS = {\n"
                                        '  "ci-predict-plant-(\\\\d+)-x": "identical:ci_predict self-test plant",\n', 1),
                "tests/wood_advisor.py": app(grammar), "tools/audit/archscore/score.py": app(grammar)}
    site = " ".join(["_CI_PREDICT_PLANT = 'git",
                     "push origin HEAD'\n"])         # split, or this line is a push site itself
    push = {"tools/audit/archscore/score.py": app(site)}
    readd, cite = f"LAYOUT placement: {old} re-adds a moved path", f"LAYOUT new-reference: tests/wood_advisor.py cites retired path {old}"
    shared = {"tests/wood_advisor.py": app(grammar), "tools/audit/archscore/score.py": app(grammar)}

    def side_merge(run):
        """A branch merge whose subject is no template, then a main already past it: what a
        live origin/main shows the merge-subject walk once the PR has merged (the RCA's refused=3)."""
        h = run("git", "rev-parse", "HEAD").stdout.strip()
        run("git", "checkout", "-q", "--detach", base)
        (r / "tests" / "wood_advisor.py").write_text((r / "tests" / "wood_advisor.py").read_text() + "# side\n")
        run("git", "commit", "-qam", "side")
        side = run("git", "rev-parse", "HEAD").stdout.strip()
        run("git", "checkout", "-q", "--detach", h)
        run("git", "merge", "-q", "--no-ff", "-m", "Merge branch 'side' into plant", side)
        past = run("git", "commit-tree", "HEAD^{tree}", "-p", "HEAD", "-m", "past").stdout.strip()
        run("git", "update-ref", "refs/heads/main", past)
    # (label, [(edits, True: committed | False: staged | "tip": the --base, beside HEAD)], job,
    #  the predicted line's text or None for a null, rc); a callable step runs git itself
    cases = [("a file re-added at a path whose move landed is predicted red", [({old: app("")}, True)], "fast", readd, 1),
             ("the re-added path under a second commit is predicted red", [({old: app("")}, True),
              ({"tests/wood_advisor.py": app("# a comment\n")}, True)], "fast", readd, 1),
             ("the re-added path with its entry dropped from the staged manifest is predicted red",
              [({old: app("")}, True), ({"tests/layout.json": unlisted}, False)], "fast", readd, 1),
             ("a new line citing a landed path is predicted red", [({"tests/wood_advisor.py": app(f"# see {old}\n")}, True)],
              "fast", cite, 1),
             ("a manifest that does not parse is predicted red", [({"tests/layout.json": lambda s: "{"}, True)],
              "fast", "LAYOUT UNREADABLE", 1),
             ("a comment citing nothing is predicted green (null control)",
              [({"tests/wood_advisor.py": app("# a comment\n")}, True)], "fast", None, 0),
             ("the re-added path staged and not committed is predicted green (null control)",
              [({old: app("")}, False)], "fast", None, 0),
             ("an unregistered push site is predicted red", [(push, True)], "instrument",
              "REF PRIVACY REFUSE tools/audit/archscore/score.py", 1),
             ("a guarded pusher's guard dropped in HEAD and restored in the index is predicted red",
              [({guarded: unguard}, True), ({guarded: reguard}, False)], "instrument",
              f"REF PRIVACY REFUSE {guarded}: registered", 1),
             ("a line that pushes nothing and names the seat's home is predicted green (null control: "
              "CI judges with the runner's identity)",
              [({"tools/audit/archscore/score.py": app(f'_CI_PREDICT_PLANT = "{SEAT_HOME}/x"\n')}, True)],
              "instrument", None, 0),
             ("the push site staged and not committed is predicted green (null control)", [(push, False)],
              "instrument", None, 0),
             ("a grammar registered only in the head's copy is predicted red", [(register, True)], "wave-script",
              "AGREEMENT RESULT divergent=0 unregistered=1", 1),
             ("a grammar the base tip shares and registers, under a HEAD that only edits the lane, is predicted "
              "green (CI merges HEAD into the tip)", [(register, "tip"), ({ag: app("// a comment\n")}, True)],
              "wave-script", None, 0),
             ("a grammar in two files the lane does not load, the lane untouched, is not run (null control: the "
              "key; prepr step 3f4 refuses it under either copy)", [(shared, True)], "wave-script", None, 0),
             ("a lane edit under a branch merge, main already past it, is predicted green (null control: CI's "
              "origin/main is the base)", [({ag: app("// a comment\n")}, True), side_merge], "wave-script", None, 0),
             ("a comment in the lane is predicted green (null control)", [({ag: app("// a comment\n")}, True)],
              "wave-script", None, 0),
             ("a head copy of the lane that exits 1 is predicted green (null control: CI runs the base's)",
              [({ag: lambda s: "process.exit(1)\n" + s}, True)], "wave-script", None, 0),
             ("the registration staged and not committed is predicted green (null control)", [(register, False)],
              "wave-script", None, 0)]
    marker = {"fast": "LAYOUT", "instrument": "REF PRIVACY", "wave-script": "AGREEMENT"}
    head = (git(root, "rev-parse", "HEAD") or "").strip()
    tmp = Path(tempfile.mkdtemp(prefix="hpo-ci-predict-plant-"))
    r = tmp / "r"
    try:
        env = throwaway_git_clone(root, r, "-q", "--shared", "--no-checkout")

        def run(*a: str) -> subprocess.CompletedProcess:
            return subprocess.run(a, cwd=r, env=env, capture_output=True, text=True)

        # The base is this tree and this file, on main's side of the merge
        # base: the lane walks first-parent merge subjects, and a branch's own
        # merges are on CI's second parent, never walked there.
        run("git", "checkout", "-q", "--detach", head)
        shutil.copy(Path(__file__), r / "tools" / "pr" / "ci_predict.py")
        run("git", "add", "-A")
        main = (git(root, "merge-base", "HEAD", "origin/main") or head).strip()
        base = run("git", "commit-tree", run("git", "write-tree").stdout.strip(), "-p", main, "-m", "predictor").stdout.strip()
        run("git", "update-ref", "refs/remotes/origin/main", base)
        penv = {**env, "HOME": SEAT_HOME}
        bad = 0
        for label, steps, job, want, rc in cases:
            run("git", "checkout", "-q", "-f", "--detach", base)
            run("git", "clean", "-qfd")
            tip = base
            run("git", "update-ref", "refs/heads/main", base)
            for step in steps:
                if callable(step):
                    step(run)
                    continue
                edits, commit = step
                for p, edit in edits.items():
                    (r / p).parent.mkdir(parents=True, exist_ok=True)
                    (r / p).write_text(edit((r / p).read_text() if (r / p).exists() else ""))
                run("git", "add", "-A")
                if commit:
                    run("git", "commit", "-qm", label)
                if commit == "tip":
                    tip = run("git", "rev-parse", "HEAD").stdout.strip()
                    run("git", "checkout", "-q", "--detach", base)
            out = subprocess.run((sys.executable, "-I", "tools/pr/ci_predict.py", "--base", tip), cwd=r, env=penv,
                                 capture_output=True, text=True)
            lines = out.stdout.splitlines()
            tag = f"PREDICT {JOB[job]} {marker[job]}"
            fix = any(l.startswith(f"CI PREDICT: a{'n' if job == 'wave-script' else ''} {marker[job]} refusal") for l in lines)
            hit = (any(l.startswith(tag) and want in l for l in lines) and fix if want
                   else not any(l.startswith(tag) for l in lines) and not fix)
            ok = hit and out.returncode == rc
            print(f"  {'ok  ' if ok else 'FAIL'} {label} (rc {out.returncode})")
            if not ok:
                print("\n".join(f"         {l}" for l in (lines + out.stderr.splitlines())[-6:]))
            bad += not ok
        return bad
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())

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
(`ref_privacy.py --check`, `instrument-self-tests`, which no local path ran),
WIRING (`selftest_wiring.py --check`, the same job, which a diff adding a
self-testing tool to `tools/` left to CI: #2870's `review_packet.py`) and
AGREEMENT (`wave-script`'s agreement lane under the base's copy, as the
pull request is graded, where `prepr.sh` step 3f4 runs the head's) and
GRADER (every program a job that restores its check source from the base
runs, on CI's tree, when the diff changes a path that job restores:
dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md). One is this predictor's own model, because CI learns the answer by
running: the import arm resolves imports statically where CI records them at
run time. (A fourth arm, NO RECORDING, read the `rec tests/...` lines of
`tests/derive_closures.sh`; round-9 C1 derived the full arm's recording set
from the tree and the class stopped being expressible -- `no_recording` below
says so where it stood.) Every arm is
scoped to what the three-dot diff adds or changes, so a red main already
carries is never charged to a branch. Nothing here runs a test, a recording
or a mutant: seconds, never a heavy script, but for AGREEMENT, which runs the
lane in a throwaway clone (about 10 s) and only on a diff to a path its job
restores, and two opt-in by `--record-self-tests` (prepr's 6d passes it):
GRADER, minutes where keyed (measured in its record), and SELF-TEST READS,
a changed file's own `--self-test`, recorded by `closure._exec_record` and
graded as its host's record by `closure.check`, for each gate script whose
source runs that self-test (0.5 s to 29 s a file, measured;
dev/audit/rca/R10-RCA-CLOSURE-ARGV.md).

    python3 tools/pr/ci_predict.py [--base origin/main] [--apply-inert] [--body FILE] [--record-self-tests]
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
script opens by name (#1987's `services.yaml`) outside a changed file's own
self-test, a read behind a dynamic path,
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
       "wave-script": "governance / wave-script", "instrument": "governance / instrument-self-tests",
       "policy-docs": "governance / policy-docs", "env-matrix": "governance / env-matrix"}


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


# SELF-TEST READS (dev/audit/rca/R10-RCA-CLOSURE-ARGV.md). A gate script that
# RUNS a tool's self-test files every read that run makes, and the recorder
# counts more than opens: `closure._exec_record` files every subprocess argv
# token naming a repo file. #2883 went red on `closures` twice that way, both
# times through tests/entities.py, and the static arms above saw neither: a
# path handed to `git ls-tree` in roster_lib's self-test, and a generator
# state_docs.py spawns. Recording the changed file's own self-test with CI's
# recorder, then grading that record as its host's with CI's own `check`,
# took 4.7 s and named both pairs CI named. A host counts only when its source
# names the file within SELF_TEST_WINDOW lines of a self-test mention: a
# script that lists a file as text (harness_headers' scan) does not run it.
SELF_TEST_WINDOW = 12
SELF_TEST_TIMEOUT = 180
_RECORD_DRIVER = ("import sys; sys.path.insert(0, 'tests'); import closure; "
                  "sys.exit(closure._exec_record(sys.argv[1], sys.argv[2], ['--self-test']))")


def self_test_hosts(root: Path, f: str, closures: dict) -> list[str]:
    """The scripts whose closure lists `f` and whose source runs its self-test.

    `closures` only: a file a host lists under `inert_reads` alone is one it
    reads as text (#2910 review 1: budget_raise_gate.py and selftest_wiring.py
    in tests/entities.py's, each a false red on a green tree). A file is never
    its own host.
    """
    name, hosts = Path(f).name, []
    for script in sorted(closures):
        if script == f or f not in set(closures[script]):
            continue
        try:
            lines = (root / script).read_text(errors="replace").splitlines()
        except OSError:
            continue
        w = SELF_TEST_WINDOW
        if any(re.search(r"self[-_]test", ln) for i, line in enumerate(lines) if name in line
               for ln in lines[max(0, i - w):i + w + 1]):
            hosts.append(script)
    return hosts


def record_self_test(root: Path, f: str, out: Path) -> str | None:
    """`f --self-test` under CI's recorder; None when recorded, else why not."""
    import os
    env = {**os.environ, "PYTHONPATH": "tests/hastub"}
    try:
        subprocess.run([sys.executable, "-c", _RECORD_DRIVER, f, str(out)], cwd=root, env=env,
                       capture_output=True, text=True, timeout=SELF_TEST_TIMEOUT)
    except subprocess.TimeoutExpired:
        return f"not recorded in {SELF_TEST_TIMEOUT} s"
    return None if out.is_file() else "the recorder wrote no record"


def self_test_reads(root, changed, closures, inert_reads, closure, scripts=None,
                    record=record_self_test, notes=None):
    """Each changed file's own self-test, recorded and graded as its host's."""
    import contextlib
    import io
    import tempfile
    preds: list[tuple[str, str]] = []
    for f in sorted(changed):
        if not f.endswith(".py") or not (root / f).is_file():
            continue
        if "--self-test" not in (root / f).read_text(errors="replace"):
            continue
        hosts = self_test_hosts(root, f, closures)
        if not hosts:
            continue
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "rec.json"
            why = record(root, f, out)
            if why is not None:
                if notes is not None:
                    notes.append(f"SELF-TEST READS {f}: {why}; left to CI's closures job")
                continue
            rec = json.loads(out.read_text())
            for host in hosts:
                d = Path(td) / host.replace("/", "_")
                d.mkdir()
                (d / "r.json").write_text(json.dumps({**rec, "script": host}))
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                    rc = closure.check(d, partial=True)
                if rc == 0:
                    continue
                kind, named = None, []
                for line in buf.getvalue().splitlines():
                    if line.startswith("    ") and kind:
                        named.append((kind, line.strip().removeprefix(f"{host}: ")))
                    elif not line.startswith(" "):  # a header; its prose lines indent by two
                        kind = ("INERT" if line.startswith("INERT READS") else
                                "UNDER-SCOPED" if line.startswith("UNDER-SCOPED") else None)
                first = (buf.getvalue().strip().splitlines() or ["no output"])[0]
                for k, g in named or [("CHECK", first)]:
                    preds.append(("closures", f"SELF-TEST READS {k} {host}: {g} (its run of "
                                              f"{f}'s self-test, recorded by closure._exec_record)"))
                if scripts is not None:
                    scripts.add(host)
    return preds


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


def wiring_preds(root: Path, changed: set[str]) -> list[tuple[str, str]]:
    """`instrument-self-tests`'s `selftest_wiring.py --check`: a self-testing
    file under `tools/` that no workflow `run:` line names (UNWIRED), and every
    index gap (MISMATCH, UNINDEXED, DUPLICATE, MISSING) naming a changed file
    (#3004 round 3: a MISMATCH on the page the PR adds went red unpredicted).

    The second arm of the class `privacy_preds` closed, in the same CI job and
    by the same shape of gap: the check runs in CI and no local path runs it,
    so a new instrument lands unwired under a prediction of no red (#2870:
    `review_packet.py`, `98 self-testing, 97 wired, 1 unwired`). Scoped to the
    diff, so a file main already carries unwired is never charged to a branch.
    """
    tool = root / "tools" / "audit" / "seat" / "selftest_wiring.py"
    if not tool.is_file():
        return []
    r = subprocess.run([sys.executable, "-I", str(tool), "--check"], cwd=root,
                       capture_output=True, text=True)
    kinds = ("UNWIRED", "MISMATCH", "UNINDEXED", "DUPLICATE", "MISSING")
    gaps = [ln.split(None, 2) for ln in r.stdout.splitlines()
            if ln.split(None, 1)[:1] and ln.split(None, 1)[0] in kinds]

    def named(p: str) -> bool:
        # DUPLICATE names its target relative to the guide's directory.
        return p in changed or any(c.endswith("/" + p) for c in changed)

    return [("instrument", f"{g[0]} {g[1].rstrip(':')}: "
             + (g[2] if len(g) > 2 else "").strip())
            for g in gaps if len(g) > 1 and named(g[1].rstrip(":"))]


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
# The step a job restores its graders from the base commit in: the jobs that
# hold it are the pull-request direction's whole population.
RESTORE_STEP = "- name: Restore the check source from the base commit"


def job_text(text: str, job: str) -> str:
    m = re.search(rf"^  {re.escape(job)}:\n(.*?)(?=^  [a-z][\w-]*:\n|\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def restore_jobs(text: str) -> list[str]:
    """Each governance.yml job that restores its check source from the base."""
    return [j for j in re.findall(r"^  ([a-z][\w-]*):\n", text, re.M) if RESTORE_STEP in job_text(text, j)]


def restored_hit(names, specs, at_tip, covers) -> list[str]:
    """The diff's paths a job grades with the base's copy of: covered by its
    restore pathspecs and held by the base tip. Only there do the head's and
    CI's copies differ, whatever loads them; a path the tip lacks is not
    restored, and a data file the job does not restore reaches CI as the
    branch has it (corpus_excluded.json, #2916's repair)."""
    return sorted(p for p in names if p in at_tip and any(covers(s, p) for s in specs))


# Each runner token a pinned run line passes, as the predictor's CI tree has it.
RUN_TOKENS = {"$PWD": lambda r, tmp: str(r), "$RUNNER_TEMP": lambda r, tmp: str(tmp),
              "${RUNNER_TEMP}": lambda r, tmp: str(tmp),
              "$(git rev-parse HEAD)": lambda r, tmp: (git(r, "rev-parse", "HEAD") or "").strip()}


def pinned_runs(text: str, root: Path | None = None) -> list[tuple[str, str, tuple[str, ...]]]:
    """Each program a restoring job runs, from governance.yml's own run text, in
    its order: (job, the program's path, its argv as written). With `root`,
    only a path the tree holds: each run line names both layouts and `test -f`
    runs the one that exists."""
    import shlex
    out = []
    for job in restore_jobs(text):
        body = "\n".join(l for l in job_text(text, job).splitlines() if not l.lstrip().startswith("#"))
        for prog, rest in re.findall(r"(?:node|python3(?: -I)?)\s+([\w./-]+\.(?:mjs|py))([^;&|\n]*)", body):
            run = (job, prog, tuple(shlex.split(rest)))
            if (root is None or (root / prog).is_file()) and run not in out:
                out.append(run)
    return out


# The runs the `agreement` arm makes (`--py-json` reads what `--out` writes),
# and the ones that grade nothing, each with its reason.
AGREEMENT_RUNS = {("wave-script", "agreement_py.py", "--out"), ("wave-script", "agreement.mjs", "--py-json")}
GRADER_EXEMPT = {
    ("policy-docs", "policy_lint.mjs", "--report"): "its step ends `|| true`: it prints and never reddens",
}


def run_key(job: str, prog: str, argv) -> tuple[str, ...]:
    return (job, Path(prog).name, *(a for a in argv if a.startswith("--")))


def ci_tree_run(root: Path, tip: str, job: str, steps) -> tuple[str, subprocess.CompletedProcess | None]:
    """Run `steps` (each a function of the tree, its runner and a scratch
    directory) where CI's pull-request run of `job` runs them: the merge of
    HEAD into the base tip (base first), the job's restore pathspecs checked
    out from that tip, in a clone whose origin/main is the tip (a live
    origin/main past the PR moves the merge-subject walk onto its own merges).
    Returns ("unmerged", None) on a conflict, else ("ran", the first failing
    step's process or the last)."""
    import shutil
    import tempfile
    import agreement_py
    from throwaway_git import throwaway_git_clone
    head = (git(root, "rev-parse", "HEAD") or "").strip()
    tmp = Path(tempfile.mkdtemp(prefix="hpo-ci-predict-tree-"))
    r = tmp / "r"
    try:
        env = throwaway_git_clone(root, r, "-q", "--shared", "--no-checkout")

        def run(*a: str) -> subprocess.CompletedProcess:
            return subprocess.run(a, cwd=r, env=env, capture_output=True, text=True)

        run("git", "update-ref", "refs/remotes/origin/main", tip)
        run("git", "checkout", "-q", "--detach", tip)
        if run("git", "merge", "-q", "--no-ff", "-m", f"Merge {head} into {tip}", head).returncode:
            return "unmerged", None
        shutil.rmtree(r / ".claude" / "workflows" / "vendor", ignore_errors=True)
        specs = agreement_py.restore_specs((r / agreement_py.WORKFLOW).read_text(), job)
        (tmp / "pinned.list").write_text(run("git", "diff", "--no-renames", "--name-only", "-z", EMPTY_TREE, tip, "--", *specs).stdout)
        run("git", "checkout", tip, f"--pathspec-from-file={tmp / 'pinned.list'}", "--pathspec-file-nul")
        out = None
        for step in steps:
            out = step(r, run, tmp)
            if out.returncode:
                break
        return "ran", out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def keyed_jobs(root: Path, base_ref: str) -> tuple[str, dict[str, list[str]], object]:
    """(the base tip, each restoring job the diff keys -> its `restored_hit`,
    agreement_py) -- the tip "" when the base or the workflow does not resolve."""
    home = next((d for d in (".claude/workflows", "tools/policy") if (root / d / "agreement_py.py").is_file()), None)
    tip = (git(root, "rev-parse", "--verify", f"{base_ref}^{{commit}}") or "").strip()
    if home is None or not tip:
        return "", {}, None
    sys.path.insert(0, str(root / home))
    import agreement_py
    wf = root / agreement_py.WORKFLOW
    if not wf.is_file():
        return "", {}, agreement_py
    text = wf.read_text()
    names = (git(root, "diff", "--name-only", "--no-renames", f"{tip}...HEAD") or "").split()
    at_tip = set((git(root, "ls-tree", "-r", "--name-only", tip) or "").splitlines())
    keyed = {}
    for job in restore_jobs(text):
        hit = restored_hit(names, agreement_py.restore_specs(text, job), at_tip, agreement_py.covers)
        if hit:
            keyed[job] = hit
    return tip, keyed, agreement_py


def over(hit: list[str]) -> str:
    return ", ".join(hit[:3]) + (f" and {len(hit) - 3} more" if len(hit) > 3 else "")


def agreement_preds(root: Path, base_ref: str) -> list[tuple[str, str]]:
    """`wave-script`'s agreement lane as CI runs it on the pull request
    (`ci_tree_run`).

    prepr.sh step 3f4 runs the head's copy, push-to-main's direction; the two
    differ only where the diff edits a path the job restores, so that diff is
    the key (`restored_hit`; dev/audit/rca/R10-RCA-2671-WAVE-SCRIPT.md,
    countermeasure A: #2671's registration passed 3f4 and was UNREGISTERED
    under the base's copy). A base without the lane runs none, as the job
    skips it.
    """
    tip, keyed, _ = keyed_jobs(root, base_ref)
    hit = keyed.get("wave-script")
    if not hit or not any(git(root, "cat-file", "-e", f"{tip}:{p}") is not None for p in AGREEMENT):
        return []

    def py(r, run, tmp):
        p = next(p for p in (".claude/workflows/agreement_py.py", "tools/policy/agreement_py.py") if (r / p).is_file())
        return run(sys.executable, "-I", p, "--out", str(tmp / "agreement.json"))

    def lane(r, run, tmp):
        return run("node", next(p for p in AGREEMENT if (r / p).is_file()), "--py-json", str(tmp / "agreement.json"))
    try:
        state, out = ci_tree_run(root, tip, "wave-script", (py, lane))
    except (OSError, StopIteration, ValueError) as e:
        return [("wave-script", f"AGREEMENT UNRUN {type(e).__name__}: {e}")]
    if state == "unmerged":
        return [("wave-script", f"AGREEMENT UNMERGED: HEAD does not merge into {tip[:12]}, "
                                f"and CI runs nothing on a conflict; merge the base first")]
    if out.returncode == 0:
        return []
    lines = [l for l in out.stdout.splitlines() if l.strip()] or [f"rc {out.returncode}: {out.stderr.strip()[-200:]}"]
    why = [l.strip() for l in lines if l.split()[0] in ("UNRESTORED", "DIVERGENT", "UNREGISTERED", "DEAD", "REFUSED")]
    result = next((l for l in reversed(lines) if l.startswith("RESULT ")), lines[-1].strip())
    return [("wave-script", f"AGREEMENT {result} (the base's copy, over {over(hit)})")] + \
           [("wave-script", f"AGREEMENT {w}") for w in why]


def grader_runs(text: str, root: Path, job: str) -> list[tuple[str, tuple[str, ...]]]:
    """The runs of `job` the graders arm makes: every one `pinned_runs` reads
    but the `agreement` arm's and `GRADER_EXEMPT`'s."""
    return [(prog, argv) for j, prog, argv in pinned_runs(text, root)
            if j == job and run_key(j, prog, argv) not in GRADER_EXEMPT.keys() | AGREEMENT_RUNS]


def grader_gaps(text: str) -> list[str]:
    """A run line the arm cannot run as CI does (a runner token `RUN_TOKENS`
    does not map), and an exemption no run line still holds. Empty is the
    population closed over governance.yml."""
    runs = pinned_runs(text)
    gaps = [f"{job}: {prog} {' '.join(argv)} passes {a!r}, which RUN_TOKENS does not map"
            for job, prog, argv in runs for a in argv if "$" in a and a not in RUN_TOKENS
            and not any(a.startswith(t) and a[len(t):].startswith("/") for t in RUN_TOKENS)]
    held = {run_key(job, prog, argv) for job, prog, argv in runs}
    gaps += [f"GRADER_EXEMPT: no run line still holds {' '.join(e)}" for e in GRADER_EXEMPT if e not in held]
    return gaps


def grader_preds(root: Path, base_ref: str) -> list[tuple[str, str]]:
    """Each run of each restoring job the diff keys (`restored_hit`), as CI
    runs it on the pull request (`ci_tree_run`): every `grader_runs` program,
    restored or the head's own, since a head copy that loads a restored file
    grades with the base's copy of it too. The jobs run side by side, one CI
    tree each; a refusal names the run and the restored paths that keyed it."""
    from concurrent.futures import ThreadPoolExecutor
    tip, keyed, agreement_py = keyed_jobs(root, base_ref)
    if not keyed:
        return []
    text = (root / agreement_py.WORKFLOW).read_text()

    def one(job: str) -> list[tuple[str, str]]:
        hit, results = keyed[job], []

        def step(prog, argv):
            def grade(r, run, tmp):
                args = [RUN_TOKENS[a](r, tmp) if a in RUN_TOKENS else
                        next((RUN_TOKENS[t](r, tmp) + a[len(t):] for t in RUN_TOKENS if a.startswith(t + "/")), a)
                        for a in argv]
                cmd = (sys.executable, "-I", prog) if prog.endswith(".py") else ("node", prog)
                out = run(*cmd, *args)
                if out.returncode:
                    results.append((prog, argv, out))
                return subprocess.CompletedProcess(out.args, 0, out.stdout, out.stderr)  # run every step
            return grade
        runs = grader_runs(text, root, job)
        try:
            state, _ = ci_tree_run(root, tip, job, tuple(step(p, a) for p, a in runs))
        except (OSError, StopIteration, ValueError) as e:
            return [(job, f"GRADER UNRUN {type(e).__name__}: {e}")]
        if state == "unmerged":
            return [(job, f"GRADER UNMERGED: HEAD does not merge into {tip[:12]}, and CI runs nothing "
                          f"on a conflict; merge the base first")]
        preds = []
        for prog, argv, out in results:
            lines = [l.strip() for l in out.stdout.splitlines() if l.strip()] or \
                [f"rc {out.returncode}: {out.stderr.strip()[-200:]}"]
            first = next((l for l in lines if l.startswith(("ERROR", "FAIL", "REFUSED", "BLIND", "DEAD", "MISSING",
                                                            "NOT WIRED", "STALE", "DRIFT", "SELF-TEST FAILED"))
                          and "probe, expected" not in l), lines[-1])
            label = " ".join((Path(prog).name, *argv))
            preds.append((job, f"GRADER {label} REFUSED by the base's copy, over {over(hit)}: {first[:240]}"))
        return preds
    with ThreadPoolExecutor(max_workers=len(keyed)) as pool:
        return [p for preds in pool.map(one, sorted(keyed)) for p in preds]


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


def null_control_preds(m, files: list[str]) -> list[tuple[str, str]]:
    """`mutation`'s null-control refusal over a pool's files, CI's `null_for`."""
    if files and m.null_for([{"file": f} for f in files]) is None:
        return [("mutation", f"NO NULL CONTROL in {', '.join(files)}: no full-line "
                 "comment to drive the null control; add one")]
    return []


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
    keyed = m.added_keys(added)
    # `tests / mutation` refuses a pool with no whole-line comment (null_for) and
    # no autofix job repairs it (#2997 rounds 1 and 2): a red, not a warning.
    nonull = null_control_preds(m, sorted({s["file"] for _, s in keyed}))
    return stale + nonull + [("mutation", f"ADDED UNPINNED {k}: {s['old'].strip()[:60]}")
                             for k, s in keyed]


# The arms, in the order they run. `--only` selects one where a caller needs a
# single question answered: `prepr.sh --fill-red` derives the `mutation` red
# alone, and reaching it by running every other arm cost 6.5 s of CPU against
# the 5 s budget the seat's checks meet (eight others then; R10-FLOW-JIDOKA's
# review, 2026-10-26).
ARMS = ("orphans", "layout", "privacy", "wiring", "agreement", "graders", "no-recording",
        "under-scoped", "inert-siblings", "left-inert", "mutation", "self-test-reads")


def is_red(job: str, line: str) -> bool:
    """A prediction that sets the rc: every arm but `mutation`'s warnings. The
    null-control refusal is `mutation`'s one red, as no autofix job repairs it."""
    return job != "mutation" or line.startswith("NO NULL CONTROL")


def predict(root: Path, base_ref: str, pairs: set | None = None,
            scripts: set | None = None, body: str | None = None,
            only: str | None = None, record: bool = False,
            notes: list | None = None) -> tuple[int, list[tuple[str, str]], str]:
    if only is not None and only not in ARMS:
        raise SystemExit(f"ci_predict: --only {only} is not one of {', '.join(ARMS)}")
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
    arms = (
        ("orphans", lambda: orphans(changed, closure)),
        ("layout", lambda: layout_preds(root, base)),
        ("privacy", lambda: privacy_preds(root)),
        ("wiring", lambda: wiring_preds(root, changed)),
        ("agreement", lambda: agreement_preds(root, base_ref)),
        ("graders", lambda: grader_preds(root, base_ref)),
        ("no-recording", lambda: no_recording(root, base, changed, closure)),
        ("under-scoped", lambda: under_scoped(root, base, changed, tracked, closures,
                                              inert_reads, closure, pairs, scripts)),
        ("inert-siblings", lambda: inert_siblings(changed, inert_reads, closure, pairs)),
        ("left-inert", lambda: left_inert(changed, closures, inert_reads, closure, scripts)),
        ("mutation", lambda: unpinned(base)),
        ("self-test-reads", lambda: self_test_reads(root, changed, closures, inert_reads,
                                                    closure, scripts, notes=notes)),
    )
    preds: list[tuple[str, str]] = []
    for name, arm in arms:
        # The arms that run a gate's programs: on --record-self-tests (prepr 6d)
        # or by name. `graders` takes minutes where it is keyed, so body_push.sh's
        # seconds-budget run leaves it to prepr (R10-RCA-PREPR-HEAD-GRADERS).
        if (only is None and (name not in ("self-test-reads", "graders") or record)) or name == only:
            preds += arm()
    if body:
        preds += carry_preds(root, body)
    seen, out = set(), []
    for p in preds:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return (1 if any(is_red(j, l) for j, l in out) else 0), out, base


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
    if any(j == "closures" and l.startswith("SELF-TEST READS INERT") for j, l in preds):
        out.append("a SELF-TEST READS INERT file is one the host really records, so `--apply-inert` "
                   "cannot clear it: it leaves INERT through INERT_EXCEPT in tests/closure.py and "
                   "joins the host's closure by the --single above, the route #2883 took "
                   "(dev/audit/rca/R10-RCA-CLOSURE-ARGV.md)")
    if any(j == "fast" and l.startswith("LAYOUT") for j, l in preds):
        out.append("a LAYOUT refusal is repaired in the diff as `python3 -I tests/layout.py --guard` "
                   "names it: a re-added moved path goes where it lives, a citation is re-pointed to "
                   "its new path, and a new file goes where tests/layout.json says")
    if any(j == "wave-script" for j, _ in preds):
        out.append("an AGREEMENT refusal is CI's verdict under the base's copy of the lane, so an edit to "
                   "the lane is graded by the copy it replaces: repair what the base's copy refuses, and a "
                   "registration only the head's copy carries has no local repair "
                   "(dev/audit/rca/R10-RCA-2671-WAVE-SCRIPT.md, cause 3): the body names it under ## Red checks")
    if any(l.startswith("GRADER ") for _, l in preds):
        out.append("a GRADER refusal is CI's verdict under the base's copy of every path the job restores, so an "
                   "exclusion, registration or rule written into a restored grader, or into anything it loads, is "
                   "graded by the copy it replaces: move it into the data the grader reads (corpus_excluded.json "
                   "for named-docs, #2916's repair), or land the grader change first "
                   "(dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md); the body names it under ## Red checks")
    if any(j == "instrument" for j, _ in preds):
        out.append("a REF PRIVACY refusal is repaired as `python3 -I tools/audit/seat/ref_privacy.py --check` "
                   "names it: a push site guarded and registered in PUSHERS, a published host path scrubbed")
    if any(j == "fast" and l.startswith("UNCLASSIFIED") for j, l in preds):
        out.append("an UNCLASSIFIED file is classified in the diff (CLAUDE.md): one a test script reads joins "
                   "that script's closure through tests/derive_closures.sh --single <script>; one no script "
                   "reads goes on INERT in tests/closure.py")
    return out


# --- re-keying `## Unpinned sites` after a main merge (P70, P125) -----------
# open_pr.sh and update_pr.sh merge origin/main into a handoff, and a main commit that inserts a line
# above a disposed site shifts its `file:line KIND` key: prepr step 7d then refuses a body whose
# every disposition still holds (2026-10-25: 19 sites on R10-PARAMS-OWNER, 15 on R10-ARCH-SHAPES,
# each a fixer round trip). A key is rewritten only when its line, mapped through
# `git diff -U0 <from> HEAD -- <file>`, lands outside every hunk on a line whose text is identical
# and occurs once in the file at HEAD, and the mutation inventory still holds that KIND there. A
# changed, removed, ambiguous or new site is left as it is, so 7d still refuses it; no disposition
# is ever written. The rewrite is recorded as one `## Head` note (head_note.py).
SITE_KEY = re.compile(r"(?<![A-Za-z0-9_./-])([A-Za-z0-9_./-]+\.py):(\d+) ([A-Z][A-Z_]*)(?![A-Za-z0-9_])")
HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+\d+(?:,(\d+))? @@", re.M)


def moved_line(diff: str, line: int) -> int | None:
    """`line` at the diff's old side, at its new side; None when a hunk changed or removed it."""
    shift = 0
    for a, b, d in HUNK.findall(diff):
        a, b, d = int(a), int(b or 1), int(d or 1)
        if b == 0:  # an insertion after old line a
            shift += d if a < line else 0
        elif a <= line < a + b:
            return None
        elif a + b <= line:
            shift += d - b
    return line + shift


def inventory_kinds(root: Path, path: str) -> set[str]:
    """The `file:line KIND` keys the mutation inventory holds for one file at the worktree."""
    sys.path[:0] = [str(root / "tests"), str(root / "tests" / "hastub")]
    import mutation_table as m
    return {m.triage_key(s) for s in m.inventory([root / path])}


def rekey_body(root: Path, body: str, frm: str, kinds=inventory_kinds) -> tuple[str, list[str], list[str]]:
    """The body with its moved keys rewritten, the `old -> new` list, and each key kept with why."""
    lines = body.split("\n")
    on, done, kept, cache = False, [], [], {}
    for n, text in enumerate(lines):
        if text.startswith("## "):
            on = re.fullmatch(r"## Unpinned sites\s*", text) is not None
        if not on:
            continue
        def one(mt):
            f, old, kind = mt.group(1), int(mt.group(2)), mt.group(3)
            key = f"{f}:{old} {kind}"
            if f not in cache:
                cache[f] = (git(root, "diff", "-U0", "--no-renames", frm, "HEAD", "--", f),
                            show(root, frm, f), show(root, "HEAD", f))
            diff, was, now = cache[f]
            if diff is None or was is None or now is None:
                kept.append(f"{key}: {f} does not read at {frm[:12]} and HEAD"); return mt.group(0)
            new = moved_line(diff, old)
            if new is None:
                kept.append(f"{key}: the merge changed or removed its line"); return mt.group(0)
            if new == old:
                return mt.group(0)
            w, h = was.split("\n"), now.split("\n")
            if not (0 < old <= len(w) and 0 < new <= len(h)) or w[old - 1] != h[new - 1]:
                kept.append(f"{key}: line {new} at HEAD is not its text"); return mt.group(0)
            if h.count(h[new - 1]) != 1:
                kept.append(f"{key}: its text is on {h.count(h[new - 1])} lines at HEAD"); return mt.group(0)
            if f"{f}:{new} {kind}" not in kinds(root, f):
                kept.append(f"{key}: the inventory holds no {kind} at line {new}"); return mt.group(0)
            done.append(f"{key} -> {f}:{new} {kind}")
            return f"{f}:{new} {kind}"
        lines[n] = SITE_KEY.sub(one, text)
    return "\n".join(lines), done, kept


def rekey_main(root: Path, path: str, frm: str) -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from head_note import prefix
    body = Path(path).read_text()
    out, done, kept = rekey_body(root, body, frm)
    for k in kept:
        print(f"REKEY KEPT {k}")
    for d in done:
        print(f"REKEY {d}")
    if done:
        head = (git(root, "rev-parse", "HEAD") or "").strip()
        out = prefix(out, f"`{head}` re-keys {len(done)} `## Unpinned sites` line(s) the main merge moved "
                          f"from `{frm}`, each to the line at this head with identical text and kind "
                          f"(`ci_predict.py --rekey-body`): " + "; ".join(done) + ".")
        Path(path).write_text(out)
    print(f"REKEY: {len(done)} re-keyed, {len(kept)} kept")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--apply-inert", action="store_true",
                    help="write every predicted INERT READS entry, then predict again")
    ap.add_argument("--body", help="the pull-request body: also predict pr-contract's carry check")
    ap.add_argument("--only", choices=ARMS,
                    help="run only this arm: a caller that needs one question answered")
    ap.add_argument("--record-self-tests", action="store_true",
                    help="also record each changed file's own self-test a gate script runs "
                         "(SELF-TEST READS: seconds per file) and run each restoring job's programs "
                         "the diff keys (GRADER: minutes where keyed), so prepr's 6d passes it")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--rekey-body", metavar="BODY", help="re-key BODY's moved `## Unpinned sites` lines in place")
    ap.add_argument("--from", dest="frm", metavar="SHA", help="with --rekey-body: the code sha the keys were taken at")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    root = Path((git(Path.cwd(), "rev-parse", "--show-toplevel") or ".").strip())
    if args.rekey_body:
        if not args.frm:
            ap.error("--rekey-body needs --from <code-sha>")
        return rekey_main(root, args.rekey_body, args.frm)
    pairs: set[tuple[str, str]] = set()
    scripts: set[str] = set()
    notes: list[str] = []
    rc, preds, base = predict(root, args.base, pairs, scripts, args.body, args.only,
                              args.record_self_tests, notes)
    if args.apply_inert and rc != 2:
        added = apply_inert(root, pairs)
        for script, f in added:
            print(f"APPLIED inert_reads {script}: {f}")
        if added:
            scripts = set()
            notes = []
            rc, preds, base = predict(root, args.base, None, scripts, args.body, args.only,
                                      args.record_self_tests, notes)
    if rc == 2:
        print(f"CI PREDICT: {base}")
        return 2
    for job, line in preds:
        print(f"PREDICT {JOB.get(job, job):<8} {line}")
    for line in notes:
        print(f"NOTE    {line}")
    if any(j == "ledger" for j, _ in preds):
        print("CI PREDICT: a STALE PIN's file under tests/mutation_ledger/ is "
              "deleted by hand; `mutation-autofix` never drops one, and pins "
              "the edited line afresh once it is gone")
    jobs = sorted({JOB.get(j, j) for j, l in preds if is_red(j, l)})
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
        reds = sum(1 for j, l in preds if is_red(j, l))
        who = ("`--apply-inert` repairs them" if inert == reds else
               f"`--apply-inert` repairs the {inert} INERT READS, the lines "
               f"above the rest" if inert else
               "the lines above name each arm's repair")
        print(f"CI PREDICT: {reds} predicted red(s) on {', '.join(jobs)} "
              f"against {base[:12]} -- repair before the handoff; {who}")
    else:
        ran = args.record_self_tests or args.only == "self-test-reads"
        seen = (" unless a changed file's own self-test makes it" if ran else "")
        print(f"CI PREDICT: no closures, fast, governance or instrument red predicted against "
              f"{base[:12]} (a data-file read is not seen{seen})")
    return rc


def wiring_self_test(root: Path) -> int:
    """`wiring_preds` over a planted unwired tool, its wired twin and a null."""
    import shutil
    import tempfile
    src = root / "tools" / "audit" / "seat" / "selftest_wiring.py"
    if not src.is_file():
        print("  FAIL the wiring arm has no selftest_wiring.py to drive")
        return 1
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        t = Path(d)
        (t / "tools" / "audit" / "seat").mkdir(parents=True)
        shutil.copy2(src, t / "tools" / "audit" / "seat" / "selftest_wiring.py")
        (t / "tools" / "x.py").write_text('if __name__ == "__main__":\n    pass  # --self-test\n')
        wf = t / ".github" / "workflows"
        wf.mkdir(parents=True)
        unwired = "jobs:\n  j:\n    steps:\n      - run: echo nothing\n"
        wired = "jobs:\n  j:\n    steps:\n      - run: python3 -I tools/x.py --self-test\n"
        cases = [
            ("an unwired self-testing tool the diff adds is predicted red",
             unwired, {"tools/x.py"}, 1),
            ("the same tool named by a workflow run line is not", wired, {"tools/x.py"}, 0),
            ("null control: a tool main already carries is not this branch's", unwired, set(), 0),
        ]
        for label, body, changed, want in cases:
            wf.joinpath("w.yml").write_text(body)
            got = len(wiring_preds(t, changed))
            print(f"  {'ok  ' if got == want else 'FAIL'} {label}")
            bad += got != want
        # The index arms: a MISMATCH on an instrument page, changed and not.
        seat = t / "tools" / "audit" / "seat"
        (seat / "instruments").mkdir()
        page = "tools/audit/seat/instruments/a.py.md"
        (seat / "INSTRUMENTS.md").write_text("- [`z.py`](instruments/a.py.md) — a\n")
        (t / page).write_text("# `a.py`\n\n- `a.py` — a.\n")
        wf.joinpath("w.yml").write_text(wired)
        for label, changed, want in (
                ("a planted MISMATCH on a changed instrument page is predicted red", {page}, 1),
                ("null control: the same MISMATCH on a page the diff leaves alone", set(), 0)):
            got = len(wiring_preds(t, changed))
            print(f"  {'ok  ' if got == want else 'FAIL'} {label}")
            bad += got != want
    return bad


def null_control_self_test(root: Path) -> int:
    """`null_control_preds` over a comment-free pool, a commented one and a mix."""
    sys.path[:0] = [str(root / "tests"), str(root / "tests" / "hastub")]
    import mutation_table as m
    base = "custom_components/heatpump_optimizer"
    bare, commented = f"{base}/flow_meter.py", f"{base}/button.py"
    bad = 0
    for label, files, want in (
            ("a pool of only a comment-free file is predicted red", [bare], 1),
            ("null control: a pool holding a commented file predicts nothing", [commented], 0),
            ("a mixed pool still has a null control", [bare, commented], 0),
            ("an empty pool predicts nothing", [], 0)):
        got = len(null_control_preds(m, files))
        print(f"  {'ok  ' if got == want else 'FAIL'} {label}")
        bad += got != want
    # The real path: predict(only="mutation") over a diff adding one unpinned
    # site, so `unpinned()`'s call site and `is_red` are driven, not only the
    # predicate (review of #3042 round 1: both survived). Only site discovery
    # is stubbed; `null_for` reads the real file.
    keep = {n: getattr(m, n) for n in ("load_budgets", "inventory", "unpinned_sites",
            "completeness_problems", "base_unpinned_sites", "added_unpinned", "diff_sides")}
    try:
        for label, f, want in (
                ("an unpinned site in a comment-free file is refused, rc=1", bare, 1),
                ("null control: the same site in a commented file is no refusal, rc=0", commented, 0)):
            site = {"file": f, "line": 1, "kind": "CMP", "old": "x == 1"}
            m.load_budgets, m.inventory = (lambda: {}), (lambda: [])
            m.unpinned_sites = lambda b, s, site=site: [site]
            m.completeness_problems = lambda b, s: []
            m.base_unpinned_sites = lambda ref, s: []
            m.added_unpinned = lambda u, b, sides: u
            m.diff_sides = lambda ref: (set(), set())
            rc, preds, _ = predict(root, "HEAD", only="mutation")
            ok = rc == want and any(l.startswith("NO NULL CONTROL") for _, l in preds) == bool(want)
            print(f"  {'ok  ' if ok else 'FAIL'} {label}")
            bad += not ok
    finally:
        for n, v in keep.items():
            setattr(m, n, v)
    return bad


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
    bad += self_test_reads_self_test(root)
    bad += rekey_self_test()
    bad += wiring_self_test(root)
    bad += null_control_self_test(root)
    bad += graders_self_test(root)
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


def graders_self_test(root: Path) -> int:
    """The graders arm's key, population and run, with no load grammar to test.

    Key: on this tree's governance.yml, the two files review rounds 2 and 3
    found outside every load-grammar key -- the vendored parser
    `render_md.mjs` requires and the gate `policy_lint.mjs` spawns -- key all
    three restoring jobs, and the data file #2916's repair moved its entry to
    keys none. Population: every run line is runnable as CI runs it and every
    exemption still matches one, each perturbed once. Run: a throwaway repo
    whose one restoring job grades a corpus through a required vendored file
    and a spawned Python gate, each plant committed on the base; the nulls are
    the repair in an unrestored data file, a corpus-only diff (not keyed) and a
    plant staged but not committed. Last, `predict` reaches the arm by name.
    """
    import shutil
    import tempfile
    sys.path[:0] = [str(root / "tests"), str(root / "tools" / "policy")]
    import agreement_py
    from throwaway_git import throwaway_git_init
    text = (root / agreement_py.WORKFLOW).read_text()
    tracked = set((git(root, "ls-files") or "").split())
    jobs = restore_jobs(text)
    bad = 0

    def ck(label, ok, why=""):
        nonlocal bad
        print(f"  {'ok  ' if ok else 'FAIL'} {label}{' -- ' + why if not ok and why else ''}")
        bad += not ok

    def keys(path, at_tip=tracked):
        return [j for j in jobs if restored_hit([path], agreement_py.restore_specs(text, j), at_tip, agreement_py.covers)]
    three = {"policy-docs", "env-matrix", "wave-script"}
    for path in ("tools/policy/vendor/markdown-it.min.js", "tools/policy/budget_raise_gate.py"):
        ck(f"{path} keys every restoring job", set(keys(path)) == three, str(keys(path)))
    ck("dev/governance/config/corpus_excluded.json keys no job (a data file CI reads as the branch has it)",
       keys("dev/governance/config/corpus_excluded.json") == [])
    ck("a restored path the base tip lacks keys no job (nothing to restore it from)",
       keys("tools/policy/vendor/markdown-it.min.js", tracked - {"tools/policy/vendor/markdown-it.min.js"}) == [])
    runs = {run_key(*r) for r in pinned_runs(text, root)}
    made = {run_key(j, p, a) for j in jobs for p, a in grader_runs(text, root, j)}
    want = {("policy-docs", "policy_lint.mjs"), ("policy-docs", "policy_lint.mjs", "--hooks"),
            ("wave-script", "check-wave-script.mjs"), ("env-matrix", "policy_lint_envmatrix.mjs")}
    ck("the arm makes every pinned run but the agreement arm's and the exempt", made == runs - AGREEMENT_RUNS -
       GRADER_EXEMPT.keys() and want <= made and not made & (AGREEMENT_RUNS | GRADER_EXEMPT.keys()), str(made))
    ck("every pinned run line is runnable as CI runs it (null control: no gap)", grader_gaps(text) == [],
       str(grader_gaps(text)))
    odd = text.replace("node tools/policy/check-wave-script.mjs;", "node tools/policy/check-wave-script.mjs $ODD;", 1)
    ck("a run line passing a token RUN_TOKENS does not map is a gap", odd != text and any("$ODD" in g for g in grader_gaps(odd)))
    unexempt = text.replace("--report", "--reprt")
    ck("an exemption no run line holds is a gap", any(g.startswith("GRADER_EXEMPT") for g in grader_gaps(unexempt)))

    workflow = ("jobs:\n  policy-docs:\n    steps:\n"
                "      - name: Restore the check source from the base commit\n        run: |\n"
                '          git diff --name-only -z "$(git hash-object -t tree /dev/null)" "$PINNED" -- \\\n'
                "            'g/*.mjs' 'g/*.py' 'g/vendor' > \"$RUNNER_TEMP/pinned.list\"\n"
                "      - name: Grade the corpus\n        run: node g/grade.mjs\n")
    grade = ("import { createRequire } from 'module'\nimport { execFileSync } from 'child_process'\n"
             "import fs from 'fs'\nconst require = createRequire(import.meta.url)\n"
             "const lib = require('./vendor/lib.js')\n"
             "const EXCLUDED = new Set([...JSON.parse(fs.readFileSync('data/excluded.json', 'utf8'))])\n"
             "for (const f of fs.readdirSync('corpus').sort()) {\n  if (EXCLUDED.has(f)) continue\n"
             "  const gate = execFileSync('python3', ['g/gate.py', f]).toString().trim()\n"
             "  if (!lib.ok(f) || gate !== 'ok') { console.log(`ERROR ${f}`); process.exit(1) }\n}\n")
    base_files = {".github/workflows/governance.yml": workflow, "g/grade.mjs": grade,
                  "g/vendor/lib.js": "exports.ok = f => !f.startsWith('bad')\n",
                  "g/gate.py": "import sys\nprint('no' if 'worse' in sys.argv[1] else 'ok')\n",
                  "data/excluded.json": "[]\n", "corpus/good.md": "x\n",
                  "tools/policy/agreement_py.py": (root / "tools" / "policy" / "agreement_py.py").read_text()}

    def app(t):
        return lambda s: s + t
    inline = {"g/grade.mjs": lambda s: s.replace("...JSON", "'bad1.md', ...JSON"), "corpus/bad1.md": app("x\n")}
    vendored = {"g/vendor/lib.js": lambda s: s.replace("!f.startsWith('bad')", "true"), "corpus/bad1.md": app("x\n")}
    gated = {"g/gate.py": lambda s: s.replace("'worse' in", "'never' in"), "corpus/worse.md": app("x\n")}
    cases = [("an exclusion written into the restored grader is predicted red (#2916's shape)", inline, True,
              "GRADER grade.mjs REFUSED by the base's copy, over g/grade.mjs: ERROR bad1.md"),
             ("an edit to a vendored file the grader requires is predicted red (round 3's markdown-it.min.js)",
              vendored, True, "over g/vendor/lib.js: ERROR bad1.md"),
             ("an edit to a gate the grader spawns is predicted red (round 2's budget_raise_gate.py)", gated, True,
              "over g/gate.py: ERROR worse.md"),
             ("the exclusion in the unrestored data file, the grader keyed by a comment, is predicted green "
              "(null control: the repair)", {"data/excluded.json": lambda s: '["bad1.md"]\n',
                                             "corpus/bad1.md": app("x\n"), "g/grade.mjs": app("// a comment\n")}, True, None),
             ("a corpus-only diff the base's grader refuses is not run (null control: the key; prepr runs the "
              "same copy CI does)", {"corpus/bad1.md": app("x\n")}, True, None),
             ("the inline exclusion staged and not committed is predicted green (null control)", inline, False, None)]
    tmp = Path(tempfile.mkdtemp(prefix="hpo-ci-predict-graders-"))
    try:
        for label, edits, commit, want in cases:
            r = tmp / f"r{cases.index((label, edits, commit, want))}"
            env = throwaway_git_init(r, "-q", "-b", "main")

            def run(*a):
                return subprocess.run(a, cwd=r, env=env, capture_output=True, text=True)
            for p, body in base_files.items():
                (r / p).parent.mkdir(parents=True, exist_ok=True)
                (r / p).write_text(body)
            run("git", "add", "-A")
            run("git", "commit", "-qm", "base")
            tip = run("git", "rev-parse", "HEAD").stdout.strip()
            for p, edit in edits.items():
                (r / p).write_text(edit((r / p).read_text() if (r / p).exists() else ""))
            run("git", "add", "-A")
            if commit:
                run("git", "commit", "-qm", label)
            got = grader_preds(r, tip)
            ok = (any(j == "policy-docs" and want in l for j, l in got) if want else not got)
            ck(label, ok, str(got))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    g = globals()
    real = g["grader_preds"]
    g["grader_preds"] = lambda _root, _base: [("policy-docs", "GRADER sentinel")]
    try:
        _, preds, _ = predict(root, "HEAD", only="graders")
    finally:
        g["grader_preds"] = real
    ck("predict reaches the graders arm by name (its call site, not only its helper)",
       ("policy-docs", "GRADER sentinel") in preds, str(preds))
    return bad


def self_test_reads_self_test(root: Path) -> int:
    """SELF-TEST READS over planted records, graded by CI's own `check`.

    The table is a scratch one, so every path in it is a real file of this
    tree (`check` refuses a phantom); the host sources are scratch files.
    """
    import tempfile
    sys.path[:0] = [str(root / "tests")]
    import closure
    f, inert, plain = "tests/throwaway_git.py", "dev/audit/rca/R10-RCA-INERT-PREDICT.md", "tests/layout.py"
    if not (closure.is_inert(inert) and not closure.is_inert(plain) and not closure.is_inert(f)):
        print(f"  FAIL the SELF-TEST READS plant needs {inert} INERT, {f} and {plain} not")
        return 1
    bad, saved = 0, closure.CLOSURES
    with tempfile.TemporaryDirectory() as d:
        t = Path(d)
        (t / "tests").mkdir()
        h, n = "tests/entities.py", "tests/harness_headers.py"  # real keys; scratch sources
        far = "\n" * (SELF_TEST_WINDOW + 1)
        i = "tests/doc_claims.py"  # lists the file under inert_reads alone, and names its self-test
        (t / h).write_text("# runs throwaway_git.py\n# through its --self-test\n")
        (t / n).write_text(f"# lists throwaway_git.py as text{far}# its own --self-test\n")
        (t / i).write_text("# throwaway_git.py --self-test\n")
        (t / f).write_text("# throwaway_git.py --self-test\n")
        listed = {h: [f, h], n: [f, n], f: [f]}

        def run(files, reads, inert_reads, changed=(f,), why=None):
            def record(_root, _f, out):
                calls.append(_f)
                out.write_text(json.dumps({"script": _f, "rc": 0, "files": [_f, *files],
                                           "inert_reads": reads}))
                return why
            calls, notes = [], []
            closure.CLOSURES = t / "closures.json"
            ir = {i: [f], **inert_reads}
            closure.write_closures(closure.CLOSURES, {"closures": listed, "inert_reads": ir})
            try:
                preds = self_test_reads(t, set(changed), listed, ir, closure,
                                        record=record, notes=notes)
            finally:
                closure.CLOSURES = saved
            return preds, calls, notes

        cases = [
            ("an INERT read the host's inert_reads omit is predicted for the one host that runs it: "
             "a self-test named two lines from the file counts, one past the window does not, an "
             "inert_reads-only listing does not, and the file is never its own host",
             run([inert], [inert], {}), lambda p, c, n: [x[1].split(":")[0] for x in p]
             == [f"SELF-TEST READS INERT {h}"] and inert in p[0][1]),
            ("a plain read the host's closure omits is UNDER-SCOPED",
             run([plain], [], {}), lambda p, c, n: len(p) == 1 and f"UNDER-SCOPED {h}: "
             + plain in p[0][1]),
            ("null control: a record inside the host's closure is not",
             run([], [], {}), lambda p, c, n: p == [] and c == [f]),
            ("a self-test the recorder cannot finish is a note, never a red",
             run([inert], [inert], {}, why="not recorded in 180 s"), lambda p, c, n: p == [] and len(n) == 1),
            ("null control: a file the diff does not change is never recorded",
             run([inert], [inert], {}, changed=()), lambda p, c, n: p == [] and c == []),
        ]
        for label, got, ok in cases:
            good = ok(*got)
            print(f"  {'ok  ' if good else 'FAIL'} {label}{'' if good else ' -- ' + repr(got[0])}")
            bad += not good
    return bad


def rekey_self_test() -> int:
    """--rekey-body over a scratch repository: a line main moved, and its three null controls."""
    import tempfile
    bad = 0
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
    from throwaway_git import throwaway_git_init
    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        env = throwaway_git_init(r, "-q")
        g = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.test", *a],
                                      cwd=r, env=env, capture_output=True, text=True, check=True).stdout.strip()
        (r / "a.py").write_text("x = 1\ny = 2\nz = y\nz = y\nw = 3\n")
        g("add", "a.py"); g("commit", "-q", "-m", "code")
        frm = g("rev-parse", "HEAD")
        (r / "a.py").write_text("import os\nx = 1\ny = 2\nz = y\nz = y\nw = 4\n")
        g("commit", "-q", "-am", "main")
        def kinds(_root, _f):
            return {"a.py:3 NUM", "a.py:5 NAME"}
        body = ("## Head\n\nh\n\n## Unpinned sites\n\n- a.py:2 NUM: pinned by mutation-autofix\n"
                "- a.py:5 NUM*2: a value check\n- a.py:4 NAME: triage t\n- a.py:1 NUM: a value check\n"
                "\n## Figures\n\na.py:2 NUM outside the section\n")
        out, done, kept = rekey_body(r, body, frm, kinds)
        cases = [
            ("a key whose line only moved is re-keyed to its new line", "- a.py:3 NUM: pinned" in out
             and done[:1] == ["a.py:2 NUM -> a.py:3 NUM"]),
            ("a key whose line text changed is kept (null control)", "- a.py:5 NUM*2:" in out
             and any(k.startswith("a.py:5 NUM: the merge changed") for k in kept)),
            ("a key whose text is on two lines at HEAD is kept (null control)", "- a.py:4 NAME:" in out
             and any("on 2 lines" in k for k in kept)),
            ("a key the inventory holds no such kind for at the new line is kept", "- a.py:1 NUM:" in out
             and any("holds no NUM" in k for k in kept)),
            ("a key outside ## Unpinned sites is never touched", out.endswith("a.py:2 NUM outside the section\n")),
            ("exactly one key is re-keyed", len(done) == 1),
        ]
        for label, ok in cases:
            print(f"  {'ok  ' if ok else 'FAIL'} rekey: {label}")
            bad += not ok
    return bad


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
              "wave-script", None, 0),
             # WIRING's call site, not only its helper: `wiring_self_test` drives
             # `wiring_preds` directly, so without this a deleted
             # `preds += wiring_preds(...)` in `predict` would leave the arm dead
             # and every check above green (#1591's lesson).
             ("a self-testing tool the diff adds with no workflow run line is predicted red",
              [({"tools/audit/seat/planted_selftest.py":
                 app('if __name__ == "__main__":\n    pass  # --self-test\n')}, True)],
              "instrument", ("UNWIRED", "UNWIRED tools/audit/seat/planted_selftest.py:"), 1)]
    marker = {"fast": "LAYOUT", "instrument": "REF PRIVACY", "wave-script": "AGREEMENT"}
    arm = {"LAYOUT": "layout", "REF PRIVACY": "privacy", "AGREEMENT": "agreement", "UNWIRED": "wiring"}
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
            # A case may name its own line marker (a job can hold two arms) as
            # `(marker, text)`; `text` None is that arm's null control. Only
            # that arm runs: a plant under tools/policy/ keys the graders arm,
            # which runs every restoring job's programs (graders_self_test's).
            mark, want_text = want if isinstance(want, tuple) else (marker[job], want)
            out = subprocess.run((sys.executable, "-I", "tools/pr/ci_predict.py", "--base", tip, "--only", arm[mark]),
                                 cwd=r, env=penv, capture_output=True, text=True)
            lines = out.stdout.splitlines()
            tag = f"PREDICT {JOB[job]} {mark}"
            fix = any(l.startswith(f"CI PREDICT: a{'n' if job == 'wave-script' else ''} {marker[job]} refusal") for l in lines)
            hit = (any(l.startswith(tag) and want_text in l for l in lines) and fix if want_text
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

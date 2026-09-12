#!/usr/bin/env python3
"""Derive and apply the scoped gate's dependency closures.

The gate is the throughput bottleneck: a full run is about forty minutes,
and most changes cannot reach most of it. This module lets ``tests/run.sh``
run only the scripts a change can affect -- without anyone ever writing down,
by hand, what a script depends on. Measured on the real suite: a
release-notes change reaches one script, a change to the card's JavaScript
reaches six, a change to the optimizer reaches fourteen of sixteen.

The closures are MEASURED, never declared. ``closure.py record`` runs a test
script for real under two instruments at once:

  * a ``sys.addaudithook`` hook that records every ``open`` the run performs,
    every ``compile``/``exec`` of a file, and every subprocess it spawns; and
  * ``sys.modules`` at the end of the run, filtered to files inside the repo.

The union of those, expressed as repo-relative paths, is the closure. That
catches the things an import graph cannot see -- ``tests/golden/*.json``,
``strings.json``, ``services.yaml``, ``manifest.json``, ``VERSION``, the
translations, ``tests/harness.py``, the plan payload -- because the run
actually opened them. Node scripts (``tests/card.mjs``) are recorded under
``strace`` when it exists, or under ``tests/node_fs_trace.mjs`` (an
``--import`` wrap of ``fs`` and the ESM loader) on Darwin and anywhere
else ``strace`` is missing.

A hand-maintained table would rot on the first refactor and nobody would
notice. This one cannot rot silently either: the post-merge gate on ``main``
re-records every closure while it runs the full suite anyway and fails if the
committed file misses anything a real run touched (``closure.py check``).

Commands
--------
  record <script> --out-dir DIR   run one script instrumented, write its record
  merge  --in-dir DIR             fold records into tests/closures.json
  check  --in-dir DIR [--partial] fail if the committed closures under-approximate
  autofix --in-dir DIR [--partial] [--out PATH]
                                  merge UNDER-SCOPED recordings; print AUTOFIX: <status>
  autofix-report --job J --status S
                                  redden an autofix job that repaired nothing
  select --files ... | --diff REF decide which scripts a change needs
                 [--workdir DIR]  ...and write the plan where run.sh reads it
  affected --files ... | --diff REF | --files-from FILE
                 [--workdir DIR]  decide whether THIS check must run for a change,
                                  and which closures it has to re-derive
  show                            print the committed closures
  selftest                        pin merge() against a silent shrink (#527)

Nothing here imports the integration; recording does, by running the tests.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLOSURES = ROOT / "tests" / "closures.json"

# Scripts that are shared plumbing or are driven by another script, and so are
# never selected on their own. Mirrors the exclusions in tests/run.sh.
# setup_qa_render.mjs is WIRED into the card lane (runs every gate, #101)
# but stays unselectable, the rolling.py pattern: making it selectable
# would need it recorded in the Linux-only derive lanes plus a
# coordinated closures.json update, and its dependencies are the card
# source and the payload -- both already covered by card.mjs's closure,
# which the strace re-recording on main will grow to include dom_stub.mjs
# the next time it runs.
# card_browser.mjs, the real-browser layout lane (issue #96), is excluded
# because it needs Chromium, which no other lane installs: the closures job
# could not record it without growing a browser. It runs in its own job.
# nightly_ha.py (#521) is that shape one step further out: it needs Docker and
# pulls a Home Assistant image, so no gate lane can run it and the closures job
# could not record it without both. Its own nightly job runs it.
NOT_A_TEST = {
    "harness.py", "profiles.py", "closure.py", "gate_lock.py",
    "setup_qa_render.mjs",
    "card_browser.mjs", "nightly_ha.py",
    # The nightly's reporter (#533): its own `nightly-status` job runs it on
    # every pull request, and it needs the GitHub Actions API, which this suite
    # has neither the network nor the token for. Like `nightly_ha.py` above it
    # is NOT_A_TEST and is NOT inert: `tests/entities.py` imports it and drives
    # its four states, so a change to how it classifies selects a script.
    "nightly_status.py",
    # The delivery ledger, which replaced `record_status.py` and its
    # `record-status` job: that check reported main's `record` CONCLUSION, which
    # was `failure` on 28 of main's last 40 commits because it asked whether
    # every merge has a row RIGHT NOW while the protocol promises one SOON, in
    # a batch. Its own `delivery-status` job runs this on every pull request; it
    # walks `<last tag>..origin/main`, which this suite has neither the remote
    # nor a reason to fetch, and its verdict is about the record rather than
    # about this tree. NOT_A_TEST and NOT inert: `tests/entities.py` imports it
    # and drives both sides of its threshold, so a change to how it classifies
    # selects a script.
    "delivery_status.py",
    # The shared DOM stub (#101) and the rig around it, imported by the three
    # Node harnesses (card.mjs, setup_qa_render.mjs, card_drift.mjs): libraries,
    # never run. dom_stub.mjs was missing from this set from v6.1.2 to v6.2.7,
    # and a selectable script with no closure forces a FULL run, so every
    # scoped PR gate in between quietly ran everything.
    "dom_stub.mjs", "card_rig.mjs",
    # Preload for `_record_node` when strace is missing. Not a test.
    "node_fs_trace.mjs",
}
# dst_checks.py is a test, but features.py runs it in a subprocess; it is
# recorded so its closure can be folded into features.py's, never selected.
DRIVEN_BY_OTHERS = {"dst_checks.py": "features.py"}

# Scripts that run only under SLOW=1, and so never run in the `fast` job that
# scoping applies to. Every other path -- push to main, nightly, dispatch --
# forces GATE_SCOPE=full, so their closures could never decide anything
# either. They are excluded from selection rather than recorded because
# recording them is not free: rolling.py alone takes over an hour under the
# audit hook (measured 62 min, against 37 unhooked), which was most of the
# wall clock of a whole re-derivation, spent on an answer nothing reads.
#
# This is a different exclusion from DRIVEN_BY_OTHERS, which means "another
# script runs this one". Nothing runs rolling.py; the gate simply never
# chooses whether to.
#
# Safety: excluding a script from selection cannot cause it to be skipped
# when it would otherwise have run, because scoping never reaches it. If
# scoping is ever extended to the slow job, this set must shrink first --
# hence the assertion in tests/entities.py that every name here is in fact
# SLOW-gated in run.sh.
SLOW_GATED = {"rolling.py"}

# A dependency of a different kind: not "what can change this script's
# answer" but "what has to run first for this script to run at all".
# plan_view.py WRITES the plan payload card.mjs reads, so a scope that picks
# card.mjs and drops plan_view.py leaves the card with no payload -- or, worse
# on a developer's box, with a stale one another run left behind. Selecting
# card.mjs selects its producer too.
PRODUCERS = {
    "tests/card.mjs": ["tests/plan_view.py"],
    # The markup gate renders both sides against the same payload.
    "tests/card_drift.mjs": ["tests/plan_view.py"],
}

# ---------------------------------------------------------------------------
# Paths that no test can read, so a change to them cannot break one. This is
# the only claim in this file that a person makes rather than a run, so it is
# deliberately tiny AND it is checked: `merge` fails if any of these turns up
# inside a recorded closure, because that would mean a test does read it.
#
# Everything else that is not in any closure forces a FULL run. "No test reads
# it" is not something to assume about a file nobody measured.
#
# The list is shorter than it looks like it should be, because the check took
# entries off it:
#
#   README.md, RELEASE_NOTES.md -- tests/entities.py reads both, checking the
#     documented behaviour against the code. They are dependencies.
#   the integration's icon and brand images -- they sit inside
#     custom_components/, so they are inside env_drift.py's rule-widened
#     closure whatever anyone thinks about them, and saying otherwise here is
#     an inconsistency waiting to be believed.
INERT = (
    "LICENSE",
    # The private-advisory pointer (#801). GitHub renders it; no gate script
    # reads it. Same class as LICENSE / DISCLAIMER.md: an unclassified root
    # file forced the FULL suite and failed the orphan check on #819.
    "SECURITY.md",
    "NOTICE",
    "icon.png",
    "docs/",  # except the handover -- see HANDOVER_DIR below
    "tests/README.md",
    ".gitignore",
    # Write-once round-2 audit evidence: harnesses and reports people run by
    # hand, outside the gate. Nothing under tests/ imports or opens them, and
    # the `merge` check below proves it every time the closures are
    # re-derived. Narrowed from `tools/` (#372): that wider prefix also
    # covered tools/release/stamp.py, live release-critical code that was
    # exempt only by sharing a directory with the evidence. Narrowing to
    # tools/audit/ makes stamp.py an ordinary tracked file the recorder must
    # classify, so a test that imports it pulls its closure in on its own --
    # no exemption, no hidden call site.
    "tools/audit/",
    # Everything below is here for one reason: a file that is neither in a
    # closure nor on this list forces the WHOLE suite, because an unmeasured
    # file is not a safe skip. That rule is right, and it was quietly costing
    # full runs. Renaming one identifier in setup_qa_render.mjs -- a script
    # people run by hand to eyeball the setup diagram -- ran all sixteen
    # scripts, stress.py included, for a change no test can see.
    #
    # `orphan_files()` below keeps this list honest: it lists every tracked
    # file that is in no closure and on no list, and tests/entities.py fails
    # when that set is not empty. So a new file has to be classified once,
    # deliberately, instead of silently making every gate full.
    ".abacus.donotdelete",
    ".claude/",
    # Cursor project rules (`.cursor/rules/*.mdc`). Agents load them; nothing
    # under tests/ reads them. Same reason `.claude/` is here.
    ".cursor/",
    # Orientation for a session that starts cold. Claude Code loads a root
    # CLAUDE.md automatically, which is the whole reason it cannot live under
    # docs/ with the rest of the prose. Nothing under tests/ reads it -- unlike
    # README.md and RELEASE_NOTES.md above, which entities.py checks against the
    # code and which are therefore dependencies rather than inert.
    "CLAUDE.md",
    "DISCLAIMER.md",
    # The quality-scale register (#229): a truthful rule-by-rule record in
    # home-assistant/core's own schema. No gate script reads it (hassfest
    # skips it for custom repos), and #229 shipped it without a
    # classification, failing the orphan check on main until this line.
    "custom_components/heatpump_optimizer/quality_scale.yaml",
    # The pull-request template. GitHub renders it into a new body; no gate
    # script reads it. It is NOT under `.github/workflows/`, so the GATE_FILES
    # prefix above does not cover it, and an unclassified file forces the whole
    # suite -- which is how a template edit would otherwise cost a full run.
    # Its headings ARE checked, by policy_lint's pr-body class against the
    # `pr-contract` job's required set, in the governance workflow rather than
    # in this gate.
    ".github/PULL_REQUEST_TEMPLATE.md",
    # GitHub reads it -- for review requests always, for the code-owner check
    # once decision 0008's rule is live; nothing in this gate opens it.
    ".github/CODEOWNERS",
    # Driven by the `browser` CI job, which is never scoped and runs on every
    # pull request regardless. It is a real test; it is simply not one of
    # THIS gate's scripts.
    "tests/card_browser.mjs",
    # The four workflows that are not the gate. Each defines its own jobs,
    # which run on every pull request regardless of what this gate selects --
    # the same argument as `tests/card_browser.mjs` above, one directory over.
    # No test script reads any of them, so a change to one needs no script
    # selected; `tests.yml` is the exception and is a GATE_FILE below.
    # Listed individually rather than as a `.github/workflows/` prefix,
    # because that prefix would also swallow `tests.yml` and silently undo
    # the forced-full rule that is this gate's safety argument.
    # `.github/workflows/governance.yml` was here, on the claim that nothing
    # in the gate reads it. That stopped being true when `tests/entities.py`
    # began reading it to pin the `record-status` job's wiring and its
    # permission widening -- the same correction `nightly_ha.py` needed one
    # entry down, and for the same reason: unreadable by the gate and unread
    # by the gate are different claims, and only the first was ever true. It
    # is now in `tests/entities.py`'s recorded closure, so an edit to it
    # selects that script instead of skipping. A file cannot be both INERT
    # and inside a recorded closure; `closure.py` refuses that pair, which is
    # what turned this from a judgement into a check.
    ".github/workflows/hassfest.yml",
    ".github/workflows/release.yml",
    ".github/workflows/validate.yml",
    # A manual QA render (writes ../setup-qa/). No gate script reads it.
    "tests/setup_qa_render.mjs",
    # tests/nightly_ha.py was here, on the argument that a lane needing Docker
    # is one "no gate script reads and none ever will". The first half held and
    # still does -- it stays on NOT_A_TEST above, and nothing in this gate runs
    # it. The second half was the mistake (#533): its REPORTING is text, and
    # `tests/entities.py` now reads it, so a stale pin or a check renamed out
    # of it fails on the pull request rather than nowhere. Its two offenders
    # from #525 stayed pinned through the #540 that removed them, every nightly
    # green, precisely because no check could see the file. Unreadable by the
    # gate and unread by the gate are different claims, and only the first was
    # ever true here.
)

# Changing the gate itself, or how the closures are derived, invalidates every
# closure at once: run everything.
GATE_FILES = (
    "tests/run.sh",
    "tests/closure.py",
    "tests/closures.json",
    "tests/requirements-ci.txt",
    # `tests.yml` ALONE, not the whole directory. This file defines the job
    # matrix, the interpreter versions, the installed dependencies and the
    # GATE_SCOPE the gate runs under, so a change to it can alter how every
    # script behaves in a way no recorded closure can capture -- which is what
    # a gate file means. The other four workflows cannot: none appears in any
    # recorded closure (`tests/entities.py` reads this one and no other), none
    # sets a gate variable, and none runs a gate script. Under the old
    # directory prefix a documentation-only change to `governance.yml` printed
    # "changes the gate itself, so every closure is suspect" and ran the full
    # suite, `tests/stress.py` included -- about twenty-three minutes to
    # measure a solver that no policy file can reach, on the pull request AND
    # again on the push to main.
    ".github/workflows/tests.yml",
    # How the closures are DERIVED is as load-bearing as the closures: change
    # a lane here and every recording that follows is taken differently.
    "tests/derive_closures.sh",
    "tests/node_fs_trace.mjs",
)


# The one hole in `docs/` (#518). Exactly one handover may exist, and
# `tests/entities.py` reads it to say so -- which makes it a dependency, and a
# file cannot be both read by a test and declared unread. Every OTHER
# `docs/handover*.md` is left unclassified on purpose: it is then in no closure
# and on no list, so `select` refuses to skip anything (MODE: FULL) and
# `orphan_files` reports it. A second handover is therefore refused on the pull
# request that adds it, not on the push to main that follows.
HANDOVER_DIR = "docs/"
HANDOVER_STEM = "handover"


def is_handover(rel: str) -> bool:
    """Anything under `docs/` whose first path segment starts with `handover`.

    Deliberately wider than the one filename: it also catches a dated sibling
    and the `docs/handovers/` directory someone reaches for once the flat name
    is refused, which is the shape the ban would otherwise be one rename from.
    """
    if not rel.startswith(HANDOVER_DIR):
        return False
    first = rel[len(HANDOVER_DIR):].lower().split("/", 1)[0]
    return first.startswith(HANDOVER_STEM)


# tools/audit/ is INERT because it holds write-once evidence nothing in the gate
# reads. preflight.sh is the exception: tests/entities.py executes it, so a
# change to it must select that script. Left inside the prefix it would be
# declared unread while being read -- the INERT-vs-recorded contradiction #357
# exists to refuse, and the same shape that let tests/nightly_ha.py's blocking
# pin go stale in silence (#533).
#
# The same argument reaches `.claude/workflows/`. The stale-policy-corpus pins
# copy `policy_lint.mjs`, everything it imports and the vendored library that
# import graph reaches into a fixture repository, and drive `preflight.sh`
# against them, because POLICY_GLOBS is this repository's one definition of
# "what is policy" and a second copy inside a test is the defect CLAUDE.md
# names. Copying it is reading it: left inside the `.claude/` prefix these
# would be declared unread while tests/entities.py opens them on every run.
#
# This is an exact-match list and the fixture derives its own copy set by
# walking those imports, so the two can disagree: a module added to that graph
# later is copied, read, and then refused here as the #357 contradiction, by
# name. That refusal is the intended degradation -- one line to add, and never
# a file silently declared unread.

# .gitignore left INERT while a gate script reads it is the same contradiction.
# #743 gave tests/card_drift.mjs a `git` call -- claimsAreThisBranchs, the guard
# that stopped it failing branches for another lane's claims -- and every git
# invocation reads .gitignore. CI said so itself: "UNDER-SCOPED: tests/card_drift.mjs
# really reads 1 file(s) the committed closure does not list: .gitignore". It was
# declared unread while being read, so `closures` went red on main and
# closures-autofix could not repair it: merging the recording produces the
# INERT-and-recorded pair #357 exists to refuse, so the bot returns skip-still-fails.
INERT_EXCEPT = (
    "tools/audit/preflight.sh",
    # #817: tests/harness_headers.py read_text's these and spawns them.
    # Declaring the prefix unread while the gate opens the files is #357.
    "tools/audit/round3/D2/dst_window_factors.py",
    "tools/audit/round3/D2/window_size_sweep.py",
    "tools/audit/round3/D5/option_doc_coverage.py",
    ".gitignore",
    ".claude/workflows/policy_lint.mjs",
    ".claude/workflows/brief_lint.mjs",
    ".claude/workflows/counts.mjs",
    ".claude/workflows/render_md.mjs",
    ".claude/workflows/vendor/markdown-it.min.js",
    ".claude/workflows/vendor/markdown-it.LICENSE",
)


def is_inert(rel: str) -> bool:
    if is_handover(rel) or rel in INERT_EXCEPT:
        return False
    return any(rel == p or (p.endswith("/") and rel.startswith(p)) for p in INERT)


def orphan_files() -> list[str]:
    """Tracked files that are in no closure and on no list.

    Each one forces the FULL suite when touched, because `select` refuses to
    skip a script on the strength of a file it has never measured. That refusal
    is correct; a long list of orphans is not. This is the list, so a test can
    hold it at zero and a new file gets classified once instead of silently
    making every gate full.

    A file belongs in exactly one of four places: a measured closure (a test
    reads it), `INERT` (nothing in the gate reads it), `GATE_FILES` (changing
    it invalidates every closure), or `SLOW_GATED` (a test this gate does not
    run). Anything else is an oversight.
    """
    import subprocess

    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True
    ).stdout.split()
    if not CLOSURES.exists():
        return []
    closures = json.loads(CLOSURES.read_text())["closures"]
    covered = {f for files in closures.values() for f in files}
    selectable = set(selectable_scripts())
    slow = {f"tests/{name}" for name in SLOW_GATED}
    return sorted(
        f
        for f in tracked
        if f not in covered
        and f not in selectable
        and f not in slow
        and not is_inert(f)
        and not is_gate_file(f)
    )


def is_gate_file(rel: str) -> bool:
    return any(rel == p or (p.endswith("/") and rel.startswith(p)) for p in GATE_FILES)


def inert_closure_violations(closures: dict[str, list[str]]) -> list[str]:
    """Files declared INERT ("nothing in the gate reads this") that also
    appear inside a recorded closure ("a test does read this"). The two
    declarations contradict, and the recorded trace is the one taken from a
    running process, so a hit here means either INERT is wrong or the
    recorder over-approximated (#357). `merge` has refused a fresh
    re-derivation on this since it was written; the closures CI job runs
    `--record-only` and never calls `merge`, so nothing on that path ever
    asked the question. Called from both `merge` (a fresh fold) and `check`
    (the committed table, which is what the CI job that never reaches
    `merge` actually validates)."""
    return sorted({f for files in closures.values() for f in files if is_inert(f)})


def test_scripts() -> list[str]:
    """Every runnable test script, as repo-relative paths."""
    out = []
    for p in sorted(list((ROOT / "tests").glob("*.py")) + list((ROOT / "tests").glob("*.mjs"))):
        if p.name in NOT_A_TEST:
            continue
        out.append(str(p.relative_to(ROOT)))
    return out


def selectable_scripts() -> list[str]:
    return [
        s
        for s in test_scripts()
        if Path(s).name not in DRIVEN_BY_OTHERS and Path(s).name not in SLOW_GATED
    ]


# ---------------------------------------------------------------------------
# recording


def _rel(path: str) -> str | None:
    """Repo-relative path, or None when the path is outside the repo."""
    if not path:
        return None
    try:
        p = Path(path)
        if not p.is_absolute():
            p = Path.cwd() / p
        p = Path(os.path.normpath(str(p)))
        rel = p.relative_to(ROOT)
    except (ValueError, OSError):
        return None
    s = str(rel)
    if s.startswith(".git/") or s == ".git":
        return None
    if "__pycache__" in s:
        return None
    # The instrument is not a dependency of what it measures.
    if s in ("tests/closure.py", "tests/closures.json"):
        return None
    # A DIRECTORY is not a dependency. The audit hook sees `open` on directories
    # too -- os.scandir, os.listdir and anything that enumerates the tree -- and
    # a directory carries no content a closure can be stale against. Recording
    # them made the two recording paths disagree: #356's per-script `--single`
    # run picked up bare `golden` and `tests` entries for tests/entities.py that
    # the full re-derive does not produce, so `check` reported an
    # under-approximation naming files that do not exist, and every pull request
    # whose scoped set included that script failed `closures` (#365). Anything
    # that is not a regular file goes the same way: a path opened and unlinked
    # within the run is not a dependency either.
    try:
        if not p.is_file():
            return None
    except OSError:
        return None
    return s


def _exec_record(script: str, out_path: str, extra_args: list[str]) -> int:
    """Run `script` in this process under an audit hook and dump its record."""
    opened: set[str] = set()
    spawned: list[list[str]] = []

    def hook(event, args):  # noqa: ANN001 - audit hook signature
        try:
            if event == "open":
                p = args[0]
                if isinstance(p, (str, bytes, os.PathLike)):
                    r = _rel(os.fsdecode(p))
                    if r:
                        opened.add(r)
            elif event in ("compile", "exec"):
                pass
            elif event in ("subprocess.Popen", "os.exec", "os.posix_spawn"):
                argv = args[1] if event == "subprocess.Popen" else args[1]
                try:
                    spawned.append([os.fsdecode(a) for a in argv])
                except Exception:
                    pass
        except Exception:
            pass

    started = time.time()
    rc = 0
    sys.argv = [script, *extra_args]
    sys.addaudithook(hook)
    import runpy

    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as exc:
        rc = int(exc.code or 0) if not isinstance(exc.code, str) else 1
    except BaseException:  # noqa: BLE001 - a failing test still has a closure
        import traceback

        traceback.print_exc()
        rc = 1

    modules = set()
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if f:
            r = _rel(f)
            if r:
                modules.add(r)

    # Any repo path that showed up on a subprocess command line is a real
    # dependency too -- that is how features.py reaches tests/dst_checks.py.
    for argv in spawned:
        for a in argv:
            r = _rel(a)
            if r and (ROOT / r).exists():
                opened.add(r)

    record = {
        "script": _rel(str(Path(script).resolve())),
        "rc": rc,
        "seconds": round(time.time() - started, 1),
        "files": sorted(opened | modules),
        "spawned": [" ".join(a) for a in spawned][:200],
        "how": "audithook+sys.modules",
        "argv": [script, *extra_args],
    }
    Path(out_path).write_text(json.dumps(record, indent=1))
    return rc


_STRACE_OPEN = re.compile(r'openat\([^,]+,\s*"([^"]+)"')


def _require_strace() -> None:
    if shutil.which("strace"):
        return
    print(
        "closure: node recording requires strace, which is not available on "
        f"{platform.system()} ({platform.machine()}). "
        "Re-derive node scripts (tests/*.mjs) on Linux or anywhere strace is "
        "installed; CI's closures job records on Linux.",
        file=sys.stderr,
    )
    raise SystemExit(1)


def _record_node(script: str, out_path: str, env: dict) -> int:
    """Record a node script's repo file reads.

    Linux CI uses strace (openat). Darwin has no strace; SIP blocks dtruss.
    The portable path is ``node --import tests/node_fs_trace.mjs``: wrap
    ``fs`` and the ESM loader. Over-approx is safe; under-approx is not.
    """
    if shutil.which("strace"):
        return _record_node_strace(script, out_path, env)
    return _record_node_preload(script, out_path, env)


def _record_node_strace(script: str, out_path: str, env: dict) -> int:
    _require_strace()
    trace = Path(out_path).with_suffix(".strace")
    started = time.time()
    cmd = ["strace", "-f", "-qq", "-e", "trace=openat", "-o", str(trace),
           "node", script]
    proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    files = set()
    for line in trace.read_text(errors="replace").splitlines():
        m = _STRACE_OPEN.search(line)
        if m:
            r = _rel(m.group(1))
            if r and (ROOT / r).is_file():
                files.add(r)
    trace.unlink(missing_ok=True)
    return _write_node_record(script, out_path, proc, files, "strace", started)


def _record_node_preload(script: str, out_path: str, env: dict) -> int:
    sink = Path(out_path).with_suffix(".nodeopens")
    started = time.time()
    e = dict(env)
    e["CLOSURE_ROOT"] = str(ROOT)
    e["CLOSURE_NODE_TRACE"] = str(sink)
    preload = (ROOT / "tests" / "node_fs_trace.mjs").resolve().as_uri()
    cmd = ["node", "--import", preload, script]
    proc = subprocess.run(cmd, cwd=ROOT, env=e, capture_output=True, text=True)
    files = set()
    if sink.exists():
        try:
            files = {f for f in json.loads(sink.read_text()) if (ROOT / f).is_file()}
        except json.JSONDecodeError:
            files = set()
        sink.unlink(missing_ok=True)
    Path(str(sink) + ".mod").unlink(missing_ok=True)
    return _write_node_record(
        script, out_path, proc, files, "node-fs-trace", started)


def _write_node_record(
    script: str, out_path: str, proc: subprocess.CompletedProcess,
    files: set[str], how: str, started: float,
) -> int:
    record = {
        "script": script if not Path(script).is_absolute() else _rel(script) or script,
        "rc": proc.returncode,
        "seconds": round(time.time() - started, 1),
        "files": sorted(files),
        "spawned": [],
        "how": how,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
    }
    Path(out_path).write_text(json.dumps(record, indent=1))
    return proc.returncode


def record(script: str, out_dir: Path, args: list[str] | None = None) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / (Path(script).name + ".json")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "tests" / "hastub") + os.pathsep + env.get("PYTHONPATH", "")
    if script.endswith(".mjs"):
        return _record_node(script, str(out), env)
    cmd = [sys.executable, str(ROOT / "tests" / "closure.py"), "--exec-record", script,
           str(out), *(args or [])]
    proc = subprocess.run(cmd, cwd=ROOT, env=env)
    return proc.returncode


# ---------------------------------------------------------------------------
# merging and rules


def _is_real_file(rel: str) -> bool:
    """Keep files that exist. A trace also catches directory opens (`tests`,
    `golden`) and paths a run probed and did not find; neither is something a
    change can be made to, and a directory in a closure would match nothing."""
    p = ROOT / rel
    return p.is_file()


# The one part of the integration a behaviour capture cannot reach.
#
# `_widen` gives env_drift the WHOLE integration because no tracer can see
# which files a capture in another worktree depended on. That argument covers
# every Python file, and it does not cover the bundled card: frontend.py
# registers `www/` as a static path (a directory handed to the HTTP layer) and
# never opens the file, so nothing in a capture can read its bytes.
#
# Measured before narrowing the rule, both captures on the same tree with
# `env_drift.py --capture . <out> --all`:
#
#   null control     card asset edited (`www/heatpump-optimizer-card.js:14`,
#                    CARD_VERSION 5.4.20 -> 9.9.99): all 55 scenarios
#                    byte-identical, sha256
#                    294c98fb07f7bac0e16342a13a34c354577cf88c60bc9a1e73c52d4432890c10
#                    on both sides
#   positive control  one token, `thermal_model.py:2683`
#                    (`T_room * dt` -> `T_room * dt * 1.0001`): captures
#                    differ, sha256
#                    656df8995f3692d18d12992679aa0dda6b13e082463763e84ca460636736411c
#
# So the card cannot move a capture, and the capture would notice if it could.
# Re-measured at 48f4263 (the merge base after the fork moved); the sha256s
# above are tied to that tree and will shift the next time anyone re-runs
# this probe on a later one -- what must not shift is null == baseline and
# positive != baseline.
# Without this, every card-only pull request ran env_drift's 55-scenario double
# capture -- the most expensive script in the suite -- to prove a plan that
# could not have changed.
FRONTEND_ASSETS = ("custom_components/heatpump_optimizer/www/",)


def _is_frontend_asset(rel: str) -> bool:
    return any(rel.startswith(prefix) for prefix in FRONTEND_ASSETS)


# A second file the whole-integration rule cannot see, for a different
# reason (#357). quality_scale.yaml was simultaneously declared INERT and
# recorded inside env_drift.py's and golden.py's closures -- a contradiction
# `merge` below refuses, that the closures CI job's `--record-only` path
# never reaches, so it was never checked in the configuration that runs.
#
# Decided by measurement, not by reading, on the same tree with
# `env_drift.py --capture . <out> --all` and a direct call to
# `golden.capture()` over five scenarios:
#
#   null control      quality_scale.yaml edited (a trailing comment line
#                     appended): env_drift capture byte-identical, sha256
#                     294c98fb07f7bac0e16342a13a34c354577cf88c60bc9a1e73c52d4432890c10
#                     before and after; golden.capture() over the first five
#                     SCENARIOS keys (winter_single_dhw, winter_two_zone_dhw,
#                     winter_single_no_dhw, winter_two_zone_no_dhw,
#                     summer_dhw_only) byte-identical, sha256
#                     e8bea574c835572442b70180e7747f2ad0c718e42f34aed12af8ff34fecf1be6
#                     before and after
#   positive control  the same probe line as FRONTEND_ASSETS above,
#                     `thermal_model.py:2683` (`T_room * dt` ->
#                     `T_room * dt * 1.0001`): env_drift capture sha256
#                     changes to
#                     656df8995f3692d18d12992679aa0dda6b13e082463763e84ca460636736411c;
#                     golden.capture() over the same five scenarios changes to
#                     84bd6b951368845c5bdcaca6f420f2baafe9f37cd7880b6b4c64b6765dc69546
#
# hassfest skips the quality-scale register for custom repositories and
# nothing under custom_components/ ever opens it -- unlike the bundled card,
# there is not even a static-path registration to explain the absence, there
# is simply no reader. It stays on INERT; the recorder was the one that was
# wrong, matching the accepted over-approximation ground #251/D3-09 was
# closed on. Re-measured at 48f4263, same caveat as above: the pair
# (identical / different) is the claim, not the exact digits.
NEVER_WIDENED = ("custom_components/heatpump_optimizer/quality_scale.yaml",)


def _widen(closures: dict[str, set[str]]) -> None:
    """Apply, in place, the rules a trace cannot know. Shared by the full fold
    and by the partial (``--single``) overlay, so that re-recording one script
    keeps its rule-widened closure current instead of replacing it with the raw
    trace -- which is how ``env_drift.py`` and ``golden.py`` came to lack
    ``tests/golden/card_claimed_drift.txt`` after it was added, and the
    closures job on main went red for every push."""
    # A script another script drives contributes its whole closure to its
    # driver, and is not selectable on its own.
    for child, parent in DRIVEN_BY_OTHERS.items():
        c, p = f"tests/{child}", f"tests/{parent}"
        if c in closures and p in closures:
            closures[p] |= closures[c]
            del closures[c]

    # PRODUCERS is "must run first" for selection, and the same edge is a
    # closure rule: plan_view.py writes the payload card.mjs and
    # card_drift.mjs read, so anything that can change the payload can
    # change what they test. card_drift.mjs had no copy of this union, which
    # is why a full fold of its 6-file raw trace silently replaced the
    # committed 66 (#527).
    for consumer, producers in PRODUCERS.items():
        if consumer in closures:
            for prod in producers:
                if prod in closures:
                    closures[consumer] |= closures[prod]

    # RULE: env_drift compares BEHAVIOUR between two checkouts, in a
    # subprocess, in a worktree outside this repo. No tracer in this process
    # can see which integration files that behaviour depends on, so the
    # closure is the whole integration -- never a file-name argument.
    ed = "tests/env_drift.py"
    if ed in closures:
        for p in sorted((ROOT / "custom_components").rglob("*")):
            rel = str(p.relative_to(ROOT))
            if (p.is_file() and "__pycache__" not in rel
                    and not _is_frontend_asset(rel) and rel not in NEVER_WIDENED):
                closures[ed].add(rel)
        for p in sorted((ROOT / "tests" / "golden").glob("*")):
            if p.is_file():
                closures[ed].add(str(p.relative_to(ROOT)))
        # The stub Home Assistant the capture runs against, for the same
        # reason. env_drift.py's own header names it: a baseline commit's
        # tracked content "fixes every byte of tests/golden.py,
        # tests/profiles.py, tests/hastub/ and custom_components/", and the
        # coordinator and config-flow captures under --all go through it.
        # The recording lane runs env_drift with a cache key and no capture,
        # so no trace here can see those reads. Until the package root
        # stopped importing the coordinator eagerly they arrived by
        # accident, through an import chain that had nothing to do with what
        # the capture depends on.
        for p in sorted((ROOT / "tests" / "hastub").rglob("*")):
            rel = str(p.relative_to(ROOT))
            if p.is_file() and "__pycache__" not in rel:
                closures[ed].add(rel)
    # golden.py stands in for env_drift in strict mode and captures the same
    # scenarios, so it carries the same closure.
    g = "tests/golden.py"
    if g in closures and ed in closures:
        closures[g] |= closures[ed]



def _fold(records: dict[str, dict]) -> dict[str, list[str]]:
    """Records -> closures, applying the rules a trace cannot know.

    Filtering happens here rather than in the tracer so that it applies
    identically to every record, including ones taken before the filter
    existed.
    """
    closures: dict[str, set[str]] = {}
    for name, rec in records.items():
        closures[name] = {f for f in rec["files"] if _is_real_file(f)}
        # The script's own file is a dependency of itself, even if the tracer
        # somehow missed the read.
        closures[name].add(name)

    _widen(closures)
    return {k: sorted(v) for k, v in sorted(closures.items())}


def _keep_committed_files(name: str, old: set[str], fresh: set[str]) -> list[str]:
    """Never shrink a committed closure. Union, report, continue.

    Under-approximation is the direction that makes the gate skip a script.
    A shrinking sibling used to abort the whole merge, so one unreproducible
    node lane vetoed an unrelated repair, and the refusal told you to run a
    full derive -- the path that replaced 66 with 6 (#527).
    """
    dropped = sorted(old - fresh)
    if not dropped:
        return sorted(fresh)
    print(f"closure: {name} would drop {len(dropped)} file(s) the committed "
          f"closure listed; keeping them.", file=sys.stderr)
    for d in dropped:
        print(f"    {d}", file=sys.stderr)
    return sorted(old | fresh)


def merge(in_dir: Path, out: Path, allow_failures: bool = False,
          partial: bool = False) -> int:
    records = {}
    for f in sorted(in_dir.glob("*.json")):
        rec = json.loads(f.read_text())
        name = rec["script"]
        records[name] = rec
    # DRIVEN_BY_OTHERS scripts ARE recorded (their closure folds into their
    # driver's), so they stay in the expectation; SLOW_GATED ones are not
    # recorded at all, so demanding them here would fail every re-derivation.
    expected = [s for s in test_scripts() if Path(s).name not in SLOW_GATED]
    missing = [s for s in expected if s not in records]
    if missing and not partial:
        print(f"closure: no recording for {', '.join(missing)}", file=sys.stderr)
        return 1
    if not records:
        print("closure: nothing recorded to merge", file=sys.stderr)
        return 1
    # A recording that ended early records only what the run reached before it
    # stopped, which is an UNDER-approximation -- exactly the direction that
    # makes the gate skip a script it should have run. Refuse it.
    broken = sorted(k for k, r in records.items() if r["rc"] != 0)
    if broken and not allow_failures:
        print("closure: these scripts failed while being recorded, so their",
              file=sys.stderr)
        print("closure is only what they reached before stopping:", file=sys.stderr)
        for b in broken:
            print(f"  {b} (exit {records[b]['rc']}) -- see the run output",
                  file=sys.stderr)
        print("Fix them, or re-run with --allow-failures if you have checked",
              file=sys.stderr)
        print("that the run still exercised every import and every file read.",
              file=sys.stderr)
        return 1
    if partial:
        # Overlay just what was recorded onto the committed file: the
        # `--single` path (#90). Every other script's closure stays exactly
        # as committed -- untouched is more trustworthy than stale, and the
        # closures job on main re-derives everything on its own schedule.
        if not out.exists():
            print(f"closure: {out} does not exist; a partial merge needs it",
                  file=sys.stderr)
            return 1
        payload = json.loads(out.read_text())
        closures = payload["closures"]
        recorded = payload.setdefault("recorded", {})
        # Overlay the fresh records on the committed closures and apply the
        # same rules the full fold applies. Without this a single re-record
        # wrote the raw trace, and a rule-widened closure (env_drift.py,
        # golden.py: the whole integration plus every file in tests/golden/)
        # silently lost its widening.
        overlay = {k: set(v) for k, v in closures.items()}
        for k, r in records.items():
            fresh = {f for f in r["files"] if _is_real_file(f)} | {k}
            # node-fs-trace sees Node opens, not strace -f children. Union
            # so Darwin --single can grow a node closure without dropping
            # files only Linux strace recorded.
            if r.get("how") == "node-fs-trace" and k in closures:
                overlay[k] = set(closures[k]) | fresh
            else:
                overlay[k] = fresh
        _widen(overlay)
        touched = set(records)
        for child, parent in DRIVEN_BY_OTHERS.items():
            if f"tests/{child}" in records:
                touched.discard(f"tests/{child}")
                touched.add(f"tests/{parent}")
        for consumer, producers in PRODUCERS.items():
            if consumer in overlay and any(p in records for p in producers):
                touched.add(consumer)
        pair = {"tests/golden.py", "tests/env_drift.py"}
        if touched & pair:
            touched |= pair & set(overlay)
        for k in sorted(touched):
            old = set(closures.get(k, ()))
            closures[k] = _keep_committed_files(k, old, set(overlay[k]))
            if k in records:
                recorded[k] = {
                    "seconds": records[k].get("seconds", 0),
                    "rc": records[k]["rc"],
                }
        payload["closures"] = closures
        out.write_text(json.dumps(payload, indent=1) + "\n")
        print(f"closure: updated {len(touched)} closure(s) in {out}")
        for k in sorted(touched):
            print(f"  {k:26s} {len(closures[k]):4d} files")
        return 0
    closures = _fold(records)
    if out.exists():
        prev = json.loads(out.read_text()).get("closures", {})
        for k, fresh in list(closures.items()):
            closures[k] = _keep_committed_files(k, set(prev.get(k, ())), set(fresh))
    bad = inert_closure_violations(closures)
    if bad:
        print("closure: files on the INERT list are actually read by tests:", file=sys.stderr)
        for b in bad:
            print(f"  {b}", file=sys.stderr)
        print("  remove them from INERT in tests/closure.py.", file=sys.stderr)
        return 1
    payload = {
        "_comment": (
            "MEASURED, not written by hand. Regenerate with "
            "tests/derive_closures.sh; the post-merge gate on main re-records "
            "these and fails if this file misses anything a real run touched."
        ),
        "recorded": {k: {"seconds": records[k]["seconds"], "rc": records[k]["rc"]}
                     for k in sorted(records)},
        "closures": closures,
    }
    out.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"closure: wrote {out} ({len(closures)} scripts)")
    for k, v in closures.items():
        print(f"  {k:26s} {len(v):4d} files")
    return 0


def production_names() -> dict[str, str]:
    """Every top-level name a production module defines, name -> module.

    The ``_``-private majority is deliberately included: a test file
    defining its own ``_apply_house_heat_loss_scale`` is exactly as bad
    as one defining ``HOUSE_LOSS_ALPHA`` -- worse, actually, because the
    underscore reads like an import alias.
    """
    names: dict[str, str] = {}
    comp = ROOT / "custom_components" / "heatpump_optimizer"
    for p in sorted(comp.glob("*.py")):
        try:
            tree = ast.parse(p.read_text())
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                names[node.name] = p.stem
            elif isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        names[t.id] = p.stem
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names[node.target.id] = p.stem
    return names


def no_copies() -> int:
    """Fail when a test file defines a symbol production also defines.

    The rule this enforces is written in tests/README.md and was violated
    twice in one session (issue #91): a test re-implements a production
    formula -- a local confidence curve, a local materiality guard -- and
    asserts against its own copy. The assertion CAN fail, so it survives
    the review that catches tests that cannot, but it fails when the
    TEST FILE's arithmetic changes rather than when production's does,
    and its mutation proofs prove the copy.

    This is deliberately the cheap version the issue proposes: a name
    collision. It is not airtight against a copy that renames the local,
    and it does not try to be -- it raises the cost of the accident,
    which is what this is. Nobody did it on purpose.

    Judged per top-level scope, because that is where a test file's
    helpers live; a same-named LOCAL inside a function is shadowing a
    production name only within those few lines, which the collision
    list would make noisy rather than useful.
    """
    prod = production_names()
    # ``DOMAIN`` and friends are generic enough that a test-local use of
    # the WORD is not a copy claim; anything the tests import is usage,
    # not a definition. Only definitions collide.
    imported_ok = set()
    failed = 0
    for script in test_scripts() + ["tests/harness.py", "tests/profiles.py"]:
        if not script.endswith(".py") or script in NOT_A_TEST:
            if script not in ("tests/harness.py", "tests/profiles.py"):
                continue
        path = ROOT / script
        if not path.exists():
            continue
        tree = ast.parse(path.read_text())
        # What this file legitimately brings in from production: direct
        # from-imports and attributes of imported production modules.
        prod_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and (
                node.module.startswith("heatpump_optimizer")
            ):
                for a in node.names:
                    imported_ok.add(a.asname or a.name)
            elif isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.startswith("heatpump_optimizer"):
                        prod_modules.add(a.asname or a.name.split(".")[-1])
            elif (isinstance(node, ast.Attribute)
                  and isinstance(node.value, ast.Name)
                  and node.value.id in prod_modules):
                imported_ok.add(node.attr)
        for node in tree.body:
            defined: str | None = None
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                defined = node.name
            elif isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    defined = node.targets[0].id
            if defined is None or defined not in prod:
                continue
            print(f"COPY-CLAIMED: {script} defines '{defined}', which is "
                  f"production's {prod[defined]}.{defined}")
            failed += 1
    if failed:
        print()
        print(f"{failed} test-file symbol(s) share a name with production.")
        print("A test must import the production symbol, not re-implement")
        print("it: an assertion against a copy fails when the copy changes,")
        print("not when production does. See tests/README.md -- 'import the")
        print("real thing'.")
        return 1
    print("closure: no test file defines a symbol production also defines")
    return 0


def check(in_dir: Path, partial: bool = False) -> int:
    """Fail if the committed closures MISS anything a fresh run touched.

    Under-approximation is the dangerous direction: it is what makes the gate
    skip a script it should have run. Over-approximation only costs time, so
    it is reported and tolerated.

    ``partial`` is the scoped path of the closures job (see ``affected``):
    only the scripts a diff can reach were re-derived, so the roster check
    below -- "a selectable script with no recording at all" -- would fail by
    construction. It is dropped there and only there, and `affected` returns
    FULL whenever a selectable script has no committed closure, so the scoped
    path cannot run on the tree where that roster check would have fired.
    """
    if not CLOSURES.exists():
        print("closure: tests/closures.json is missing", file=sys.stderr)
        return 1
    committed = json.loads(CLOSURES.read_text())["closures"]
    # Same contradiction `merge` refuses, checked here too (#357): the
    # closures CI job runs `derive_closures.sh --record-only`, which never
    # calls `merge`, so a file that is both INERT and inside a recorded
    # closure was never caught in the configuration that actually executes.
    bad = inert_closure_violations(committed)
    if bad:
        print("closure: files on the INERT list are inside a recorded "
              "closure (committed tests/closures.json):", file=sys.stderr)
        for b in bad:
            print(f"  {b}", file=sys.stderr)
        print("  A file cannot be declared unread (INERT) and recorded as "
              "read (in a closure) at the same time. Either it genuinely "
              "affects that script's output and must leave INERT, or the "
              "recorder over-approximated and should stop recording it "
              "(#357).", file=sys.stderr)
        return 1
    records = {}
    for f in sorted(in_dir.glob("*.json")):
        rec = json.loads(f.read_text())
        records[rec["script"]] = rec
    if not records:
        print("closure: no fresh recordings to check against", file=sys.stderr)
        return 1
    # A recorded entry must be a regular FILE. The scoped and full re-derives
    # silently assume they produce the same closure for the same script, and
    # that assumption is what `--single` rests on; directory entries are how it
    # broke (#365). Checked on the fresh recordings rather than on the committed
    # table, so a recorder that starts emitting them again is caught at the run
    # that emits them, not a merge later.
    non_files = sorted(
        (script, name)
        for script, rec in records.items()
        for name in rec.get("files", ())
        if not (ROOT / name).is_file()
    )
    if non_files:
        print("NOT A FILE: a closure recorded something that is not a regular file;")
        print("  a directory carries no content a closure can be stale against,")
        print("  and recording one makes the scoped and full re-derives disagree (#365).")
        for script, name in non_files:
            print(f"    {script}: {name}")
        return 1
    # LOUD, before anything else: a selectable script with no recording at
    # all is the silent-degradation case (issue #90). The lanes in
    # tests/derive_closures.sh record a fixed roster, so a newly added test
    # script is invisible to the under-approximation comparison below -- it
    # was never run -- and the only symptom used to be the PR gate quietly
    # reverting to full mode while CI stayed green. Failing here, on main,
    # does not block the PR that added the script but does not let the
    # omission survive either.
    unmeasured = [] if partial else [
        s for s in selectable_scripts() if s not in records]
    if unmeasured:
        print("closure: selectable script(s) with NO recording this run:")
        for s in unmeasured:
            print(f"    {s}")
        print()
        print("No closure can be recorded for a script the lanes never ran,")
        print("so the scoped gate silently runs FULL on every PR until this")
        print("is fixed. Add the script to a lane in tests/derive_closures.sh")
        print("(or record just it with: ./tests/derive_closures.sh --single")
        print("                         <script>), then commit the re-derived")
        print("tests/closures.json.")
        return 1
    # Fold only when the recordings cover everything a re-derivation produces
    # -- a partial run cannot fold, because a driver may be missing the very
    # recording that would be folded into it. SLOW_GATED scripts are never
    # recorded, so they must not count towards that expectation or a complete
    # run would look partial and dst_checks.py would be checked as if it were
    # selectable in its own right.
    expected_recordings = {
        s for s in test_scripts() if Path(s).name not in SLOW_GATED
    }
    fresh = _fold(records) if set(records) >= expected_recordings else {
        k: sorted(set(v["files"]) | {k}) for k, v in records.items()
    }
    failed = 0
    for name, files in sorted(fresh.items()):
        have = set(committed.get(name, ()))
        if name not in committed:
            print(f"UNDER-SCOPED: {name} has no committed closure")
            failed += 1
            continue
        missing = sorted(set(files) - have)
        if missing:
            print(f"UNDER-SCOPED: {name} really reads {len(missing)} file(s) "
                  f"the committed closure does not list:")
            for m in missing:
                print(f"    {m}")
            failed += 1
        extra = sorted(have - set(files))
        if extra:
            print(f"note: {name} lists {len(extra)} file(s) this run did not "
                  f"touch (safe: over-scoped)")
    if failed:
        print()
        print(f"{failed} closure(s) are stale. Re-derive the named script:")
        print("    ./tests/derive_closures.sh --single <script>")
        print("and commit tests/closures.json. A full derive_closures.sh off")
        print("Linux replaces node-lane recordings; --single cannot shrink them.")
        return 1
    print("closure: committed closures cover every file this run touched")
    return 0


def autofix_allowed(*, event_name: str, closures_result: str,
                    head_repo: str, repo: str, commit_subject: str,
                    loop_subject: str = "ci: re-record closures") -> bool:
    """True only for a failed same-repo PR job that is not our own push."""
    return (
        event_name == "pull_request"
        and closures_result == "failure"
        and head_repo == repo
        and commit_subject != loop_subject
    )


def retrigger_needed(*, pushed: bool, used_pat: bool) -> bool:
    """GITHUB_TOKEN pushes do not fire pull_request; dispatch must."""
    return pushed and not used_pat


# Both autofix jobs push only on `changed`, and every other status used to fall
# through to job success -- so a job that repaired nothing looked exactly like
# one that did, and `.cursor/rules/ci-autofix.mdc`'s "wait for the bot commit"
# waited for a commit no step would push (#523). These are the statuses that
# owe a human nothing: a repair happened, or none was ever attempted.
#
# `claims-autofix` is a different shape, not a mirror. `apply_inherited_claims`
# reports no attempted-and-failed status at all, and its `skip-not-inherited`
# is the ordinary answer for every `fast` failure that was not INHERITED
# CLAIMS -- unlike `closures-autofix`, that job never asks which it was, so
# reddening it would redden every unrelated `fast` failure a second time. Its
# entry is here for the summary line and to fail closed on a status added
# later, not because anything it returns today means a skipped repair.
AUTOFIX_QUIET = {
    "closures-autofix": (
        "changed", "skip-clean", "skip-not-allowed", "skip-not-under-scoped"),
    # `skip-moves-nothing-claimable` is a REFUSAL rather than a missed repair:
    # the branch's three-dot cannot have moved a fixture, so its claim file is
    # not the bot's to rewrite, and there is nothing for a human to wait for.
    # `skip-cannot-compare` is quiet for the opposite reason -- the three-dot
    # could not be computed, which `check_claims_hygiene` reports as
    # CANNOT COMPARE on the same run, and two jobs shouting one fact is how
    # the earlier three CI failures became unreadable.
    "claims-autofix": ("changed", "skip-not-allowed", "skip-not-inherited",
                       "skip-moves-nothing-claimable", "skip-cannot-compare"),
}

# Keyed by status where the job-wide remedy would misdirect. A failed
# recording is not repaired by re-deriving: the script stopped early, so its
# recorded closure is truncated, and re-deriving it here would record the same
# truncation.
_AUTOFIX_STATUS_REMEDY = {
    "skip-failed-recording":
        "A script exited non-zero WHILE being recorded, so its closure is only\n"
        "what it reached before stopping -- and merging that would under-scope\n"
        "the gate, which is why the merge refuses it. The under-approximation\n"
        "this job was going to repair is real and still unrepaired.\n"
        "Fix the failing script first; the closures job re-records on the next\n"
        "push and this repair then happens on its own.\n",
}

_AUTOFIX_REMEDY = {
    "closures-autofix":
        "Re-derive the failing script yourself and commit tests/closures.json:\n"
        "    ./tests/derive_closures.sh --single <script>\n"
        "Python lanes record through sys.addaudithook, so a Darwin recording of\n"
        "one is sound; a Darwin recording of a node lane can only widen a Linux\n"
        "one, never replace it.",
    "claims-autofix":
        "Rewrite tests/golden/claimed_drift.txt and card_claimed_drift.txt for\n"
        "THIS diff by hand, keeping `claims-for:` and any `# may-drift:` line.",
}


def autofix_repair_failed(job: str, status: str) -> bool:
    """True when `job`'s status means a repair is owed and no commit is coming.

    Fails closed. A status this table does not carry -- one invented later, or
    the empty string a crashed merge step leaves in the job output -- is a
    repair nobody can wait for, and so is an unknown job.
    """
    return status not in AUTOFIX_QUIET.get(job, ())


def autofix_report(job: str, status: str) -> tuple[int, str]:
    """The job's verdict on its own status: exit code, and what to say."""
    if not autofix_repair_failed(job, status):
        return 0, f"{job}: {status} -- nothing owed to a human."
    return 1, (
        f"{job}: {status} -- THE REPAIR DID NOT HAPPEN.\n"
        "No commit will be pushed, so waiting for one waits forever. This is\n"
        "the case `.cursor/rules/ci-autofix.mdc` already lists as a human\n"
        "judgment call, and its rule against re-recording an UNDER-SCOPED\n"
        "yourself does not apply once the bot has reported that it did not.\n"
        + _AUTOFIX_STATUS_REMEDY.get(status, _AUTOFIX_REMEDY.get(job, "")))


def _autofix_report_cmd(job: str, status: str) -> int:
    rc, text = autofix_report(job, status)
    print(text)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        # The point of the finding: legible without opening the log.
        with open(summary, "a") as fh:
            fh.write(f"### {job}\n\n```\n{text}\n```\n")
    return rc


def apply_under_scoped_recordings(in_dir: Path, *, partial: bool = True) -> str:
    """Merge recordings into CLOSURES only when check printed UNDER-SCOPED.

    Returns one of: changed, skip-clean, skip-not-under-scoped,
    skip-failed-recording, skip-merge-failed, skip-still-fails,
    skip-unchanged. Restores the previous closures.json text unless the
    status is changed.
    """
    in_dir = Path(in_dir)
    prev = CLOSURES.read_text() if CLOSURES.exists() else None

    def _restore() -> None:
        if prev is None:
            if CLOSURES.exists():
                CLOSURES.unlink()
        else:
            CLOSURES.write_text(prev)

    try:
        records = [json.loads(p.read_text()) for p in sorted(in_dir.glob("*.json"))]
    except (json.JSONDecodeError, OSError):
        return "skip-merge-failed"
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = check(in_dir, partial=partial)
    except (KeyError, TypeError, json.JSONDecodeError, OSError):
        return "skip-merge-failed"
    if rc == 0:
        return "skip-clean"
    if "UNDER-SCOPED" not in out.getvalue() + err.getvalue():
        return "skip-not-under-scoped"
    # Only now, because `closures-autofix` runs on ANY `closures` failure and
    # a failed recording is common to several of them. Reddening it before the
    # test above would fire on every no-copies, NOT-A-FILE or INERT failure
    # that happened to coincide with one, and send its reader to re-derive a
    # closure that was never stale. Past this line UNDER-SCOPED was printed,
    # so this is not that no-op -- and `merge(allow_failures=False)` below
    # would refuse these records anyway, as `skip-merge-failed`. This says
    # which refusal it was, and keeps it loud (#523). The UNDER-SCOPED may
    # itself be an artefact of the failure (an error path reads files the
    # clean path does not), which is why the remedy is "fix the script", not
    # "re-derive it".
    if any(r.get("rc", 0) != 0 for r in records):
        return "skip-failed-recording"

    try:
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            mrc = merge(in_dir, CLOSURES, allow_failures=False, partial=partial)
    except (KeyError, TypeError, json.JSONDecodeError, OSError):
        _restore()
        return "skip-merge-failed"
    if mrc != 0:
        _restore()
        return "skip-merge-failed"

    out2, err2 = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out2), contextlib.redirect_stderr(err2):
            rc2 = check(in_dir, partial=partial)
    except (KeyError, TypeError, json.JSONDecodeError, OSError):
        _restore()
        return "skip-still-fails"
    if rc2 != 0:
        _restore()
        return "skip-still-fails"
    new = CLOSURES.read_text() if CLOSURES.exists() else None
    if new == prev:
        return "skip-unchanged"
    return "changed"


def _autofix_cmd(in_dir: Path, out: Path, partial: bool) -> int:
    global CLOSURES
    orig = CLOSURES
    CLOSURES = out
    try:
        status = apply_under_scoped_recordings(in_dir, partial=partial)
    finally:
        CLOSURES = orig
    print(f"AUTOFIX: {status}")
    return 0


# ---------------------------------------------------------------------------
# selection


def changed_files(diff_ref: str) -> list[str]:
    base = subprocess.run(["git", "merge-base", diff_ref, "HEAD"], cwd=ROOT,
                          capture_output=True, text=True)
    ref = base.stdout.strip() if base.returncode == 0 else diff_ref
    out = subprocess.run(["git", "diff", "--name-only", f"{ref}...HEAD"], cwd=ROOT,
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"closure: cannot diff against {diff_ref}: {out.stderr.strip()}")
    files = [l.strip() for l in out.stdout.splitlines() if l.strip()]
    # Uncommitted work counts too, so a local `run.sh` scopes to what is
    # actually on disk.
    for extra in (["git", "diff", "--name-only", "HEAD"],
                  ["git", "ls-files", "--others", "--exclude-standard"]):
        o = subprocess.run(extra, cwd=ROOT, capture_output=True, text=True)
        files += [l.strip() for l in o.stdout.splitlines() if l.strip()]
    return sorted(set(files))


def select(files: list[str]) -> dict:
    """Decide what to run. Returns a plan; every decision carries its reason."""
    if not CLOSURES.exists():
        return {"mode": "full", "reason": "tests/closures.json is missing",
                "run": selectable_scripts(), "skip": {}, "changed": files}
    closures = json.loads(CLOSURES.read_text())["closures"]

    scripts = selectable_scripts()
    unknown = sorted(k for k in closures if k not in scripts)
    if unknown:
        return {"mode": "full",
                "reason": f"closures.json describes scripts that no longer exist: "
                          f"{', '.join(unknown)}",
                "run": scripts, "skip": {}, "changed": files}
    uncovered = [s for s in scripts if s not in closures]
    if uncovered:
        return {"mode": "full",
                "reason": f"no closure recorded for {', '.join(uncovered)}",
                "run": scripts, "skip": {}, "changed": files}

    if not files:
        return {"mode": "full", "reason": "no changed files could be determined",
                "run": scripts, "skip": {}, "changed": files}

    for f in files:
        if is_gate_file(f):
            return {"mode": "full",
                    "reason": f"{f} changes the gate itself, so every closure is suspect",
                    "run": scripts, "skip": {}, "changed": files}

    known = {f for files_ in closures.values() for f in files_}
    unmapped = [f for f in files if f not in known and not is_inert(f)]
    if unmapped:
        return {"mode": "full",
                "reason": ("no recorded closure mentions "
                           + ", ".join(unmapped[:6])
                           + (" ..." if len(unmapped) > 6 else "")
                           + " -- an unmeasured file is not a safe skip"),
                "run": scripts, "skip": {}, "changed": files}

    # The belt to the closure's braces: any integration change gets a
    # behavioural diff whether or not the closure saw the file. The bundled
    # card is excluded for the same measured reason `_widen` excludes it --
    # a capture cannot read it (see FRONTEND_ASSETS). Without this, the rule
    # above re-selected env_drift for card-only changes even once its closure
    # no longer listed the card, and the most expensive script in the suite
    # ran on every card pull request to prove a plan that could not move.
    touched_integration = [f for f in files
                           if f.startswith("custom_components/")
                           and not _is_frontend_asset(f)]

    run, skip = [], {}
    for s in scripts:
        hits = sorted(set(files) & set(closures[s]))
        if hits:
            run.append(s)
            continue
        if s == "tests/env_drift.py" and touched_integration:
            run.append(s)
            continue
        skip[s] = {"closure_size": len(closures[s]),
                   "reason": "no changed file is in its measured closure"}

    # Pull in whatever the selected scripts need to have run before them.
    for consumer, producers in PRODUCERS.items():
        if consumer in run:
            for prod in producers:
                if prod in skip:
                    del skip[prod]
                    run.append(prod)
    run = [s for s in scripts if s in run]      # back into suite order

    return {"mode": "scoped", "reason": "", "run": run, "skip": skip,
            "changed": files, "closure_sizes": {s: len(closures[s]) for s in scripts}}


def print_plan(plan: dict, stream=sys.stdout) -> None:
    """The plan, written so a human scanning the log cannot misread it."""
    w = stream.write
    w("########## scoped gate ##########\n")
    if plan["mode"] == "full":
        w("  MODE: FULL -- every test script runs, nothing is scoped out.\n")
        w(f"  reason: {plan['reason']}\n")
        return
    w(f"  MODE: SCOPED -- {len(plan['run'])} script(s) run, "
      f"{len(plan['skip'])} scoped out.\n")
    w(f"  changed files ({len(plan['changed'])}), measured against the "
      f"recorded closures in tests/closures.json:\n")
    for f in plan["changed"][:60]:
        w(f"      {f}\n")
    if len(plan["changed"]) > 60:
        w(f"      ... and {len(plan['changed']) - 60} more\n")
    w("\n")
    for s_ in plan["run"]:
        w(f"      RUN   {s_}\n")
    w("\n")
    for s_, info in plan["skip"].items():
        w(f"      SKIP  {s_}  (closure: {info['closure_size']} files, "
          f"{info['reason']})\n")
    w("\n")
    w("  A skipped script is a claim that no changed file is in its measured\n")
    w("  closure. The claim is re-checked by the FULL unscoped suite that runs\n")
    w("  on every push to main, so a wrong closure turns main red within one\n")
    w("  gate. Set GATE_SCOPE=full to run everything here and now.\n")


def write_plan(plan: dict, workdir: Path) -> None:
    """Emit the plan as three files run.sh can read without parsing JSON."""
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "scope.json").write_text(json.dumps(plan, indent=1))
    if plan["mode"] == "full":
        (workdir / "scope.run").write_text("")   # empty == no scoping
    else:
        (workdir / "scope.run").write_text("\n".join(plan["run"]) + "\n")
    lines = []
    for s, info in plan.get("skip", {}).items():
        lines.append(f"{s}\t{info['closure_size']}\t{info['reason']}")
    (workdir / "scope.skip").write_text("\n".join(lines) + ("\n" if lines else ""))
    import io
    buf = io.StringIO()
    print_plan(plan, buf)
    (workdir / "scope.txt").write_text(buf.getvalue())


# ---------------------------------------------------------------------------
# the closures check's own scope
#
# `select` above decides which TESTS a change needs. This decides whether the
# `closures` job -- the thing that checks the table `select` trusts -- needs to
# run at all, and if so how much of it.
#
# It exists because that job was scoped by the wrong question. It ran on a pull
# request only when the diff ADDED a file under custom_components/ (#332), so a
# change to what a test READS was checked only after it merged: the pull
# request was green, main went red, and a second pull request repaired it.
# That happened five times -- #214, #320, #332, #340, #349 -- and the sharpest
# case is #353, a pull request that exists solely to fix a closure error and
# whose own `closures` check says `skipping`.
#
# Three cases:
#
#   full    a changed file is a GATE_FILE (every closure is suspect at once),
#           is a script this gate cannot re-derive on its own, or -- the case
#           that matters -- is in NO recorded closure and not INERT. Nothing
#           can be inferred about a file the table has never measured.
#   scoped  some recorded closure contains a changed file: re-derive exactly
#           those scripts, then run the same `check`. One entry is ~40 s
#           against 12-22 minutes for the full table.
#   skip    no recorded closure contains any changed file. Nothing the gate
#           runs reads them, so no recording can move. A docs-only pull request
#           must still cost nothing, or the scoping this replaces was pointless.
#
# The order matters, and the skip is LAST on purpose. The first draft asked
# "is every changed file INERT?" first, and that is a different question: a
# file CAN be on INERT and in a recorded closure at the same time -- that is
# exactly the shape quality_scale.yaml took until #357: listed as inert and
# also inside env_drift's rule-widened closure, simultaneously, on main.
# Asking the hand list first would have skipped a change to a file the table
# said a test reads. The table decides the skip; INERT only licenses a
# file's ABSENCE from the table. #357 fixed the recorder so quality_scale.yaml
# no longer sits in both places (measured: it does not move env_drift's or
# golden's output), and `inert_closure_violations()` now asserts that no
# other file does either -- but the ORDER this function applies stays right
# regardless of whether such a file currently exists, which is what the
# synthetic case in tests/entities.py pins.
#
# The `full` rule carries no path prefix on purpose. The first draft said "a
# changed file under custom_components/ that is in no closure", and the
# argument for it -- an unmeasured file is not a safe skip -- has nothing to do
# with that directory: a file under tests/ in no closure is equally unmeasured.
# An inclusion list of one directory fails OPEN when someone adds a file type
# nobody thought about, which is the failure this whole predicate is here to
# stop; the exclusion list (INERT) fails closed. Today the widened rule costs
# nothing measurable -- `orphan_files()` returns 0, so every non-inert tracked
# file is already in some closure -- and the gap it closes is hard to reach on
# purpose: a new file becomes a dependency only when something reads it, and
# that something is itself in a closure, so the `scoped` rule fires anyway.
# It is defensive, not a live hole. (tvofi-claude-09's objection to the
# narrower draft.)


def affected(files: list[str]) -> dict:
    """Decide whether the closures check must run, and on what. Returns a plan."""
    scripts = selectable_scripts()

    def _full(reason: str) -> dict:
        return {"case": "full", "reason": reason, "rederive": [], "why": {},
                "changed": files}

    # The same preconditions `select` applies, for the same reason: a table
    # that does not describe this tree cannot scope anything, in either
    # direction. They also underwrite `check --partial` -- the scoped path
    # never runs on a tree where a selectable script has no closure, so
    # skipping that check's roster test there cannot hide an unrecorded script.
    if not CLOSURES.exists():
        return _full("tests/closures.json is missing")
    closures = json.loads(CLOSURES.read_text())["closures"]
    unknown = sorted(k for k in closures if k not in scripts)
    if unknown:
        return _full("closures.json describes scripts that no longer exist: "
                     + ", ".join(unknown))
    uncovered = [s for s in scripts if s not in closures]
    if uncovered:
        return _full("no closure recorded for " + ", ".join(uncovered))
    if not files:
        return _full("no changed files could be determined")

    gate = [f for f in files if is_gate_file(f)]
    if gate:
        return _full(f"{gate[0]} changes the gate itself, so every closure "
                     f"is suspect")

    # A script another script drives in a SUBPROCESS reaches the table only
    # through its driver's fold, and `--single` cannot record it (dst_checks.py
    # needs HASTUB_TZ set, which only the lane sets). Re-deriving the driver
    # alone would not see the child's new reads, so a change here is not
    # something the scoped path can check.
    driven = [f for f in files if Path(f).name in DRIVEN_BY_OTHERS]
    if driven:
        return _full(f"{driven[0]} is driven in a subprocess by "
                     f"{DRIVEN_BY_OTHERS[Path(driven[0]).name]}; only a full "
                     f"re-derivation folds its reads in")

    known = {f for files_ in closures.values() for f in files_}
    unmapped = [f for f in files if f not in known and not is_inert(f)]
    if unmapped:
        return _full("no recorded closure mentions "
                     + ", ".join(unmapped[:6])
                     + (" ..." if len(unmapped) > 6 else "")
                     + " -- nothing can be inferred about a file the table "
                       "has never measured")

    why: dict[str, dict] = {}
    for s in scripts:
        hits = sorted(set(files) & set(closures[s]))
        if hits:
            why[s] = {"changed": hits, "via": "closure"}
    # A recording is a real run: card.mjs reads the payload plan_view.py
    # writes, so re-deriving the consumer without its producer records a run
    # that found no payload -- and a failed run records only what it reached.
    for consumer, producers in PRODUCERS.items():
        if consumer in why:
            for prod in producers:
                if prod not in why:
                    why[prod] = {"changed": [], "via": f"producer of {consumer}"}
    # Suite order, so the recordings run in the order run.sh would.
    rederive = [s for s in scripts if s in why]
    if not rederive:
        # Everything that changed is absent from every closure, and `unmapped`
        # above already proved each such file is INERT. Nothing a recording
        # could touch has moved.
        return {"case": "skip",
                "reason": "no recorded closure contains any changed file, and "
                          "every one of them is INERT",
                "rederive": [], "why": {}, "changed": files}
    return {"case": "scoped",
            "reason": f"{len(rederive)} closure(s) intersect the diff",
            "rederive": rederive, "why": why, "changed": files}


def print_affected(plan: dict, stream=sys.stdout) -> None:
    """The decision, written so a human scanning the log cannot misread it."""
    w = stream.write
    w("########## closures check ##########\n")
    w(f"  CASE: {plan['case'].upper()} -- {plan['reason']}\n")
    w(f"  changed files ({len(plan['changed'])}):\n")
    for f in plan["changed"][:60]:
        w(f"      {f}\n")
    if len(plan["changed"]) > 60:
        w(f"      ... and {len(plan['changed']) - 60} more\n")
    if plan["case"] == "skip":
        w("  Nothing to re-derive: this check does not run for this change.\n")
        return
    if plan["case"] == "full":
        w("  Every closure is re-derived, exactly as on a push to main.\n")
        return
    w("\n")
    for s in plan["rederive"]:
        info = plan["why"][s]
        pulled = ", ".join(info["changed"][:4]) or info["via"]
        more = f" (+{len(info['changed']) - 4} more)" if len(info["changed"]) > 4 else ""
        w(f"      REDERIVE  {s}  <- {pulled}{more}\n")
    w("\n")
    w("  Every other closure is left alone: no changed file is in it, so a\n")
    w("  fresh recording could not disagree with the committed one. The FULL\n")
    w("  unscoped re-derivation on every push to main re-checks that claim.\n")


def write_affected(plan: dict, workdir: Path) -> None:
    """Emit the decision as files a workflow can read without parsing JSON."""
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "affected.json").write_text(json.dumps(plan, indent=1))
    (workdir / "affected.case").write_text(plan["case"] + "\n")
    (workdir / "affected.scripts").write_text(
        "".join(f"{s}\n" for s in plan["rederive"]))
    import io

    buf = io.StringIO()
    print_affected(plan, buf)
    (workdir / "affected.txt").write_text(buf.getvalue())


# ---------------------------------------------------------------------------
# #527: a full merge used to replace tests/card_drift.mjs's committed 66 with
# the raw 6-file trace, and the refusal that said "run a full re-derivation"
# was the same path. A partial merge aborted the whole overlay at the first
# shrink, so one unreproducible lane vetoed an unrelated repair.


def _selftest_write_records(rec_dir: Path, mapping: dict[str, list[str]]) -> None:
    rec_dir.mkdir(parents=True, exist_ok=True)
    for script, files in mapping.items():
        (rec_dir / f"{Path(script).name}.json").write_text(json.dumps({
            "script": script, "rc": 0, "seconds": 0.1, "files": files,
        }))


def selftest() -> int:
    """Drive merge() and check() against the #527 trap. No suite recording."""
    failed = 0
    n = 0

    def pin(name: str, cond: bool, detail: str = "") -> None:
        nonlocal failed, n
        n += 1
        if cond:
            print(f"  ok   {name}")
        else:
            failed += 1
            extra = f"  [{detail}]" if detail else ""
            print(f"  FAIL {name}{extra}")

    print("\n=== closure shrink guard (#527) ===")
    committed = json.loads(CLOSURES.read_text())["closures"]
    drift = "tests/card_drift.mjs"
    raw_six = [
        "VERSION",
        "tests/card_drift.mjs",
        "tests/card_rig.mjs",
        "tests/dom_stub.mjs",
        "tests/golden/card_claimed_drift.txt",
        "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js",
    ]
    old_drift = set(committed[drift])
    pin(
        "card_drift.mjs's committed closure covers plan_view.py",
        set(committed["tests/plan_view.py"]) <= old_drift,
        f"missing {sorted(set(committed['tests/plan_view.py']) - old_drift)}",
    )
    pin(
        "the 6-file raw trace is a strict subset of that claim",
        set(raw_six) < old_drift,
        f"missing from committed: {sorted(set(raw_six) - old_drift)}",
    )

    expected = [s for s in test_scripts() if Path(s).name not in SLOW_GATED]
    mapping = {}
    for s in expected:
        mapping[s] = list(committed[s]) if s in committed else [s]
    mapping[drift] = raw_six

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        out = td_path / "closures.json"
        out.write_text(CLOSURES.read_text())
        rec = td_path / "rec"
        _selftest_write_records(rec, mapping)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = merge(rec, out, allow_failures=False, partial=False)
        after = json.loads(out.read_text())["closures"][drift]
        dropped = sorted(old_drift - set(after))
        pin(
            "a full merge does not drop files from card_drift.mjs",
            rc == 0 and old_drift <= set(after),
            f"rc={rc} after={len(after)} dropped={len(dropped)} "
            f"first={dropped[:4]!r}",
        )

    grower = "tests/open_meteo.py"
    grower_old = [grower]
    grower_new = [grower, "tests/harness.py"]
    shrinker = "tests/frontend.py"
    shrinker_old = [shrinker, "tests/harness.py"]
    shrinker_new = [shrinker]
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        out = td_path / "closures.json"
        out.write_text(json.dumps({
            "closures": {grower: grower_old, shrinker: shrinker_old},
            "recorded": {},
        }))
        rec = td_path / "rec"
        _selftest_write_records(rec, {grower: grower_new, shrinker: shrinker_new})
        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            rc = merge(rec, out, allow_failures=False, partial=True)
        payload = json.loads(out.read_text())["closures"]
        log = buf.getvalue() + err.getvalue()
        pin(
            "a shrinking script does not abort an unrelated grow",
            rc == 0
            and "tests/harness.py" in payload[grower]
            and "tests/harness.py" in payload[shrinker],
            f"rc={rc} grower={payload.get(grower)!r} "
            f"shrinker={payload.get(shrinker)!r}",
        )
        pin(
            "the shrink path does not tell you to run a full derive",
            "full re-derivation" not in log.lower(),
            f"log={log[-400:]!r}",
        )

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        out = td_path / "closures.json"
        out.write_text(json.dumps({
            "closures": {grower: grower_old},
            "recorded": {},
        }))
        rec = td_path / "rec"
        _selftest_write_records(rec, {grower: grower_new})
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            rc = merge(rec, out, allow_failures=False, partial=True)
        payload = json.loads(out.read_text())["closures"]
        pin(
            "a grow-only partial merge still grows (null control)",
            rc == 0 and payload[grower] == sorted(grower_new),
            f"rc={rc} files={payload.get(grower)!r}",
        )

    widened = {
        drift: {drift},
        "tests/plan_view.py": {"tests/plan_view.py", "tests/profiles.py"},
        "tests/card.mjs": {"tests/card.mjs"},
    }
    _widen(widened)
    pin(
        "card_drift.mjs inherits plan_view.py's closure the way card.mjs does",
        "tests/profiles.py" in widened[drift]
        and "tests/profiles.py" in widened["tests/card.mjs"],
        f"drift={sorted(widened[drift])!r} card={sorted(widened['tests/card.mjs'])!r}",
    )

    crc, log = _selftest_stale_message()
    pin(
        "a stale-closure refusal names --single, not a bare full derive",
        crc == 1
        and "--single" in log
        and "Regenerate with tests/derive_closures.sh and commit" not in log,
        f"rc={crc} log={log[-400:]!r}",
    )

    if failed:
        print(f"\n{failed} of {n} closure shrink pins FAILED")
        return 1
    print(f"\nALL {n} closure shrink pins PASSED")
    return 0


def _selftest_stale_message() -> tuple[int, str]:
    grower = "tests/open_meteo.py"
    global CLOSURES
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        fake = td_path / "closures.json"
        fake.write_text(json.dumps({"closures": {grower: [grower]}}))
        rec = td_path / "rec"
        _selftest_write_records(rec, {grower: [grower, "tests/harness.py"]})
        orig = CLOSURES
        CLOSURES = fake
        buf, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                rc = check(rec, partial=True)
        finally:
            CLOSURES = orig
        return rc, buf.getvalue() + err.getvalue()


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--exec-record":
        return _exec_record(sys.argv[2], sys.argv[3], sys.argv[4:])
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record"); r.add_argument("script"); r.add_argument("--out-dir", required=True)
    # REMAINDER, not "*": the arguments being forwarded start with dashes
    # (--only, --cache-key), and argparse reads those as options of its own.
    # That silently recorded nothing for golden.py and env_drift.py once.
    r.add_argument("--args", nargs=argparse.REMAINDER, default=[])
    m = sub.add_parser("merge"); m.add_argument("--in-dir", required=True)
    m.add_argument("--out", default=str(CLOSURES))
    m.add_argument("--allow-failures", action="store_true")
    m.add_argument("--partial", action="store_true")
    c = sub.add_parser("check"); c.add_argument("--in-dir", required=True)
    c.add_argument("--partial", action="store_true")
    af = sub.add_parser("autofix")
    af.add_argument("--in-dir", required=True)
    af.add_argument("--partial", action="store_true")
    af.add_argument("--out", default=str(CLOSURES))
    ar = sub.add_parser("autofix-report")
    ar.add_argument("--job", required=True)
    # Not required: a merge step that crashed leaves the output empty, and
    # that has to reach the table as a status rather than as a usage error.
    ar.add_argument("--status", default="")
    s = sub.add_parser("select")
    s.add_argument("--files", nargs="*"); s.add_argument("--diff")
    s.add_argument("--json", action="store_true")
    s.add_argument("--workdir")
    f = sub.add_parser("affected")
    f.add_argument("--files", nargs="*"); f.add_argument("--diff")
    # A git-produced list, read from a file rather than the command line: a
    # workflow passing `--files $(cat ...)` splits paths on whitespace and
    # loses a long diff to ARG_MAX.
    f.add_argument("--files-from")
    f.add_argument("--json", action="store_true")
    f.add_argument("--workdir")
    sub.add_parser("show")
    sub.add_parser("no-copies")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "record":
        return record(a.script, Path(a.out_dir), a.args)
    if a.cmd == "merge":
        return merge(Path(a.in_dir), Path(a.out), a.allow_failures,
                      partial=a.partial)
    if a.cmd == "check":
        return check(Path(a.in_dir), a.partial)
    if a.cmd == "autofix":
        return _autofix_cmd(Path(a.in_dir), Path(a.out), a.partial)
    if a.cmd == "autofix-report":
        return _autofix_report_cmd(a.job, a.status)
    if a.cmd == "no-copies":
        return no_copies()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "show":
        print(CLOSURES.read_text())
        return 0
    if a.cmd == "affected":
        files = list(a.files or [])
        if a.files_from:
            files += [l.strip() for l in
                      Path(a.files_from).read_text().splitlines() if l.strip()]
        if a.diff:
            files += changed_files(a.diff)
        plan = affected(sorted(set(files)))
        if a.workdir:
            write_affected(plan, Path(a.workdir))
        if a.json:
            print(json.dumps(plan, indent=1))
        else:
            print_affected(plan)
        # "nothing affected" is an answer, not an error: the workflow reads the
        # decision, and a non-zero exit here would read as a broken check.
        return 0
    files = list(a.files or [])
    if a.diff:
        files += changed_files(a.diff)
    plan = select(sorted(set(files)))
    if a.workdir:
        write_plan(plan, Path(a.workdir))
    if a.json:
        print(json.dumps(plan, indent=1))
    else:
        print_plan(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

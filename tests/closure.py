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
actually opened them. Node scripts (``tests/card.mjs``) are recorded the same
way under ``strace``, since they have no audit hook.

A hand-maintained table would rot on the first refactor and nobody would
notice. This one cannot rot silently either: the post-merge gate on ``main``
re-records every closure while it runs the full suite anyway and fails if the
committed file misses anything a real run touched (``closure.py check``).

Commands
--------
  record <script> --out-dir DIR   run one script instrumented, write its record
  merge  --in-dir DIR             fold records into tests/closures.json
  check  --in-dir DIR [--partial] fail if the committed closures under-approximate
  select --files ... | --diff REF decide which scripts a change needs
                 [--workdir DIR]  ...and write the plan where run.sh reads it
  affected --files ... | --diff REF | --files-from FILE
                 [--workdir DIR]  decide whether THIS check must run for a change,
                                  and which closures it has to re-derive
  show                            print the committed closures

Nothing here imports the integration; recording does, by running the tests.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
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
NOT_A_TEST = {
    "harness.py", "profiles.py", "closure.py", "setup_qa_render.mjs",
    "card_browser.mjs",
    # The shared DOM stub (#101) and the rig around it, imported by the three
    # Node harnesses (card.mjs, setup_qa_render.mjs, card_drift.mjs): libraries,
    # never run. dom_stub.mjs was missing from this set from v6.1.2 to v6.2.7,
    # and a selectable script with no closure forces a FULL run, so every
    # scoped PR gate in between quietly ran everything.
    "dom_stub.mjs", "card_rig.mjs",
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
    "NOTICE",
    "icon.png",
    "docs/",
    "tests/README.md",
    ".gitignore",
    # Audit harnesses and release tooling: scripts people run by hand,
    # outside the gate. Nothing under tests/ imports or opens them, and
    # the `merge` check below proves it every time the closures are
    # re-derived.
    "tools/",
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
    # Driven by the `browser` CI job, which is never scoped and runs on every
    # pull request regardless. It is a real test; it is simply not one of
    # THIS gate's scripts.
    "tests/card_browser.mjs",
    # A manual QA render (writes ../setup-qa/). No gate script reads it.
    "tests/setup_qa_render.mjs",
)

# Changing the gate itself, or how the closures are derived, invalidates every
# closure at once: run everything.
GATE_FILES = (
    "tests/run.sh",
    "tests/closure.py",
    "tests/closures.json",
    "tests/requirements-ci.txt",
    ".github/workflows/",
    # How the closures are DERIVED is as load-bearing as the closures: change
    # a lane here and every recording that follows is taken differently.
    "tests/derive_closures.sh",
)


def is_inert(rel: str) -> bool:
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


def _record_node(script: str, out_path: str, env: dict) -> int:
    """Record a node script's file reads with strace; node has no audit hook."""
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
            if r and (ROOT / r).exists():
                files.add(r)
    trace.unlink(missing_ok=True)
    record = {
        "script": script,
        "rc": proc.returncode,
        "seconds": round(time.time() - started, 1),
        "files": sorted(files),
        "spawned": [],
        "how": "strace",
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
#   null control     card asset edited (a new statement, CARD_VERSION
#                    5.4.19 -> 9.9.99): all 55 scenarios byte-identical,
#                    sha256 1f1dcb966bdf7ae9... on both sides
#   positive control one token in thermal_model.py (`* dt` -> `* dt * 1.0001`):
#                    captures differ
#
# So the card cannot move a capture, and the capture would notice if it could.
# Without this, every card-only pull request ran env_drift's 55-scenario double
# capture -- the most expensive script in the suite -- to prove a plan that
# could not have changed.
FRONTEND_ASSETS = ("custom_components/heatpump_optimizer/www/",)


def _is_frontend_asset(rel: str) -> bool:
    return any(rel.startswith(prefix) for prefix in FRONTEND_ASSETS)


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

    # plan_view.py writes the payload card.mjs reads: anything that can change
    # the payload can change what the card is tested against.
    if "tests/card.mjs" in closures and "tests/plan_view.py" in closures:
        closures["tests/card.mjs"] |= closures["tests/plan_view.py"]

    # RULE: env_drift compares BEHAVIOUR between two checkouts, in a
    # subprocess, in a worktree outside this repo. No tracer in this process
    # can see which integration files that behaviour depends on, so the
    # closure is the whole integration -- never a file-name argument.
    ed = "tests/env_drift.py"
    if ed in closures:
        for p in sorted((ROOT / "custom_components").rglob("*")):
            rel = str(p.relative_to(ROOT))
            if p.is_file() and "__pycache__" not in rel and not _is_frontend_asset(rel):
                closures[ed].add(rel)
        for p in sorted((ROOT / "tests" / "golden").glob("*")):
            if p.is_file():
                closures[ed].add(str(p.relative_to(ROOT)))
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
            overlay[k] = {f for f in r["files"] if _is_real_file(f)} | {k}
        _widen(overlay)
        touched = set(records)
        for child, parent in DRIVEN_BY_OTHERS.items():
            if f"tests/{child}" in records:
                touched.discard(f"tests/{child}")
                touched.add(f"tests/{parent}")
        if "tests/plan_view.py" in records and "tests/card.mjs" in overlay:
            touched.add("tests/card.mjs")
        pair = {"tests/golden.py", "tests/env_drift.py"}
        if touched & pair:
            touched |= pair & set(overlay)
        for k in sorted(touched):
            fresh = sorted(overlay[k])
            old = set(closures.get(k, ()))
            dropped = sorted(old - set(fresh))
            if dropped:
                print(f"closure: {k} drops {len(dropped)} file(s) the committed "
                      f"closure listed:")
                for d in dropped:
                    print(f"    {d}")
                print("  Refusing: a partial update may not shrink a closure. "
                      "Run a full re-derivation instead.", file=sys.stderr)
                return 1
            closures[k] = fresh
            if k in records:
                recorded[k] = {"seconds": records[k]["seconds"], "rc": records[k]["rc"]}
        payload["closures"] = closures
        out.write_text(json.dumps(payload, indent=1) + "\n")
        print(f"closure: updated {len(touched)} closure(s) in {out}")
        for k in sorted(touched):
            print(f"  {k:26s} {len(closures[k]):4d} files")
        return 0
    closures = _fold(records)
    bad = sorted({f for files in closures.values() for f in files if is_inert(f)})
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
        print(f"{failed} closure(s) are stale. Regenerate with "
              f"tests/derive_closures.sh and commit tests/closures.json.")
        return 1
    print("closure: committed closures cover every file this run touched")
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
# file can be on INERT and in a recorded closure at the same time --
# quality_scale.yaml is both on main today, listed as inert and inside
# env_drift's rule-widened closure. Asking the hand list first would have
# skipped a change to a file the table says a test reads. The table decides
# the skip; INERT only licenses a file's ABSENCE from the table.
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
    a = ap.parse_args()
    if a.cmd == "record":
        return record(a.script, Path(a.out_dir), a.args)
    if a.cmd == "merge":
        return merge(Path(a.in_dir), Path(a.out), a.allow_failures,
                      partial=a.partial)
    if a.cmd == "check":
        return check(Path(a.in_dir), a.partial)
    if a.cmd == "no-copies":
        return no_copies()
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

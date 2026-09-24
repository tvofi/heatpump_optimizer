#!/usr/bin/env python3
"""A mutation table as a gate: does the suite NOTICE a changed production line?

Coverage says a line ran. It cannot say a check would fail if the line were
wrong, and five W5-G7 tranches measured the gap: twenty-two checks executed the
line they were named for and pinned nothing, and twenty-five production guards
turned out to be deletable with no check failing. Every one of those was green
coverage. `tests/coverage_ratchet.py` holds the floor; this holds the meaning.

**Scope is the lines the pull request touched.** `--scope changed` draws its
mutants only from sites on production lines the diff adds or modifies
(`changed_lines`), so a survivor it reports is on a line the branch wrote. A
pre-existing line is the nightly's, and a comment-only, docs-only or test-only
diff draws nothing. `--scope full` puts every production module in scope, which
is the nightly's job and far too slow for a pull request.

**Each mutant is driven only by the scripts whose recorded closure reaches its
file.** Driving every script would cost a full suite per mutant; driving one
hand-picked script would let a mutant survive because its driver never imports
the module, and a survivor that says nothing about the suite is worse than no
survivor at all.

**A kill is a failing check, read out of the whole output.** #805 recorded
the alternative to reading all of it: a pre-screen that read the last 1200 bytes
scored seven real kills as survivors, because two scripts print their summary
line before trailing log noise. A mutant is killed when a driver's run is red
AND names more failing checks than the unmutated baseline's (`killed()`). An
exit status alone is not a failed check: #1453 scored structure.py's "improved,
not yet recorded" exit as a kill, and #1521 scored env_drift.py's INHERITED
CLAIMS refusal -- which fires on ANY production edit, a comment included, before
anything is captured -- as a kill of every mutant it drove. Every run also
drives one comment-only edit through every driver in play, and refuses itself
if that null control dies.

**Nothing is mutated in the working tree.** Each worker mutates its own copy, so
a run killed mid-mutant cannot leave a production file edited -- the failure mode
an in-place `try/finally` still has, because a SIGKILL does not run `finally`.

**The budget carries two caps, for two different things.** The survivor
FRACTION (`max_survivor_fraction`) stays a one-sided cap on the sampled run: the
pool is a seeded sample drawn from whichever files the diff put in scope, so two
clean branches touching different modules draw different pools and score
differently through no fault of either, and an exact count over the sample would
go red at random. Beside it sits the exact-count ratchet the sample could not
carry: `unpinned_sites`, an exact count over a DETERMINISTIC inventory of every
candidate site the six operators generate, which `tests/structure.py`'s ratchet
could use only because it measures the whole tree. The inventory below is that
whole tree, so an exact count over it is reproducible and "improved and not yet
recorded" is a fair refusal. A site is unpinned until it carries a disposition
-- a `killed_by` driver or a `survivor_triage` verdict -- and a diff that adds a
site without one raises the count and is refused. The ratchet is what stops a
guard from leaving the tree unaccounted for; recording the sampled run's kills
into the ledger (`killed_by`) is the nightly burn-in's follow-up, not this
enforcement.

A survivor is not automatically a defect. An equivalent mutant cannot be killed
by any test, and several of the twenty-five guards W5-G7 measured are worth
keeping for the cause they buy rather than the outcome a check could see. When
the audit measures a survivor indistinguishable from its original at every
input, record it under `survivor_triage` in the budgets file, pinned to the
line text it was measured on: the fraction then counts only the survivors no
triage has called equivalent, and an unmarked survivor stays a gap (#1217).

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
import contextlib
import io
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import tokenize
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parent.parent
PKG = "custom_components/heatpump_optimizer/"
PRODUCTION = ROOT / PKG
BUDGETS = ROOT / "tests" / "mutation_budgets.json"
CLOSURES = ROOT / "tests" / "closures.json"

_NUM = re.compile(r"-?\d+\.?\d*")
_FAILED = re.compile(r"^\s*(\d+) of (\d+) .*FAILED\s*$", re.M)
# The per-check line the shared harness prints (`tests/harness.py`,
# `Results.check`), and the three drivers that keep their own counter with it.
_CHECK_FAIL = re.compile(r"^\s*FAIL\s+(.+?)\s*$", re.M)
# The other failing-check forms the drivers print (#1521). A summary count:
# `N [<WHAT>] CHECK(S) FAILED` (frontend and deployment_shape name what;
# open_meteo and solar_alignment do not), `N FAILURES` (edge), `N ISSUES:`
# (validate) and env_drift.py's three verdicts. And plan_view.py's `PLAN VIEW
# ISSUES:` heading over one `  - ` bullet per issue. `main()` refuses a run
# whose drivers include one whose source prints none of these forms
# (`verdict_form_problems`), so a driver cannot go blind by printing a new one.
_SUMMARY_FAILS = re.compile(
    r"^\s*(\d+) (?:(?:[A-Z][A-Z -]* )?CHECK\(S\) FAILED|FAILURES\b|ISSUES:"
    r"|UNCLAIMED DRIFT\(S\)|COMMITTED FIXTURE\(S\) ARE STALE"
    r"|STALE CLAIM\(S\))", re.M)
_ISSUE_BULLETS = re.compile(r"^[A-Z][A-Z ]*ISSUES:\n((?:[ \t]+- .*(?:\n|$))+)",
                            re.M)
# An uncaught exception prints its traceback to stderr, whatever the class is
# called -- UpdateFailed, AbortFlow, StopIteration, one carrying notes or a
# multi-line assert message all end differently, so the header is the key.
_TRACEBACK = "Traceback (most recent call last):"
TIMEOUT_RC = 124

# Candidate drivers for `--scripts` are the GATE's recorded set, not a
# hand-kept shortlist (#1211, D3-01). `default_scripts()` derives the list
# from tests/closures.json -- the universe tests/closure.py's `select`
# chooses from when it scopes a diff -- minus the scripts the instrument
# cannot honestly drive, each named below with its property. The previous
# eight-script default drove mutants with 8 of the 24 recorded scripts and
# never ran the differential golden step, so a recorded survivor fraction
# was not the fraction this repository's gate would produce.
#
# This is a derivation, not a preference list: tests/entities.py checks that
# every recorded script is either in DEFAULT_SCRIPTS or below with a reason.
DRIVER_EXCLUSIONS = {
    # `run_script` drives `[sys.executable, script]`; these two are Node
    # programs -- tests/run.sh's e2e lane runs them with `node` -- and their
    # input, the plan payload, is another driver's output (closure.py's
    # PRODUCERS edge), which a one-script invocation never builds.
    "tests/card.mjs": "node program; needs plan_view.py's payload run first",
    "tests/card_drift.mjs": "node program; needs plan_view.py's payload run "
                            "first",
    # golden.py's DEFAULT mode IS the differential: its resolve_mode says
    # "Unset means drift", and drift execs env_drift.py --all <ref> -- the
    # step below. Driving it here would run the same comparison twice. The
    # strict comparison it can run instead reads fixtures recorded on
    # another machine, which tests/run.sh says would "cry wolf": that
    # non-portability is what the drift mode exists to replace.
    "tests/golden.py": "its default mode IS the env_drift.py step",
}


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


def _git(*args: str, root: Path | None = None) -> str:
    return subprocess.run(["git", *args], cwd=root or ROOT,
                          capture_output=True, text=True).stdout


def _code(lines: list[str]) -> list[tuple[str, tuple[str, ...]]]:
    """Each line's indentation and code tokens, comments and blanks dropped.

    Tokenized a line at a time, so a line that opens a bracket or a string
    keeps the tokens read before the tokenizer gives up.
    """
    skip = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
            tokenize.DEDENT, tokenize.ENDMARKER}
    out = []
    for line in lines:
        toks: list[str] = []
        try:
            for tok in tokenize.generate_tokens(io.StringIO(line.strip()).readline):
                if tok.type not in skip:
                    toks.append(tok.string)
        except (tokenize.TokenError, SyntaxError):
            pass
        if toks:
            out.append((_indent(line), tuple(toks)))
    return out


def hunk_lines(diff: str) -> dict[str, set[int]]:
    """The new-side lines of a `git diff -U0`, per file, code hunks only.

    A pure deletion leaves no line to mutate. A hunk whose code tokens and
    indentation match on both sides -- a comment or whitespace edit, a
    trailing comment added to a code line -- is dropped whole.
    """
    out: dict[str, set[int]] = {}
    path, start, old, new = None, 0, [], []

    def flush() -> None:
        if path and new and _code(old) != _code(new):
            out.setdefault(path, set()).update(range(start, start + len(new)))

    for line in diff.splitlines():
        if line.startswith("+++ ") or line.startswith("@@"):
            flush()
            old, new = [], []
            if line.startswith("+++ "):
                path = line[6:] if line.startswith("+++ b/") else None
            else:
                start = int(re.match(r"@@ -\S+ \+(\d+)", line).group(1))
        elif line.startswith("-") and not line.startswith("--- "):
            old.append(line[1:])
        elif line.startswith("+"):
            new.append(line[1:])
    flush()
    return out


def changed_lines(base: str, root: Path | None = None) -> dict[str, set[int]]:
    """The production lines this branch adds or modifies, per file.

    Three-dot against the merge base (never two-dot, which would count
    `base`'s own newer commits), plus what is not committed yet: run by hand
    that is the work in front of the seat, and in CI it adds nothing. An
    untracked production file counts whole.
    """
    root = root or ROOT
    merge_base = _git("merge-base", base, "HEAD", root=root).strip()
    if not merge_base:
        return {}
    out = hunk_lines(_git("diff", "-U0", "--no-renames", "--no-ext-diff",
                          merge_base, "--", PKG, root=root))
    for rel in _git("ls-files", "--others", "--exclude-standard", "--", PKG,
                    root=root).splitlines():
        if rel.endswith(".py"):
            n = len((root / rel).read_text().splitlines())
            out[rel] = set(range(1, n + 1))
    return {f: ln for f, ln in out.items() if f.endswith(".py") and ln}


def scope_files(scope: str, base: str) -> tuple[list[Path], str]:
    """The production files in scope, and the sentence that says why."""
    if scope == "full":
        return sorted(PRODUCTION.rglob("*.py")), "every production module"
    touched = sorted(ROOT / f for f in changed_lines(base)
                     if (ROOT / f).exists())
    if touched:
        return touched, (f"{len(touched)} production file(s) whose code this "
                         "diff adds or modifies")
    return [], "no production code line added or modified against the base"


def drawable(path: Path, rel: str, touched: dict[str, set[int]] | None) -> list[dict]:
    """The candidate sites the pool may draw from one file.

    Every site under `--scope full` (`touched` None); under `--scope changed`
    only the sites on lines `changed_lines` returned for `rel`.
    """
    return [m for m in candidates(path)
            if touched is None or m["line"] in touched.get(rel, ())]


def drivers_for(rel: str, closures: dict, allow: list[str]) -> list[str]:
    """The candidate scripts whose MEASURED closure contains one file."""
    return [s for s in allow if rel in closures.get(s, ())]


def default_scripts() -> str:
    """Every recorded gate script the instrument can drive (#1211).

    The net is derived from tests/closures.json, the recorded table
    tests/closure.py's `select` chooses from, so the instrument scores what
    the gate could run rather than a hand-kept subset that drifts. The only
    names missing are DRIVER_EXCLUSIONS, each carrying the property that
    makes a `run_script` call dishonest.
    """
    recorded = load_closures()
    keep = [s for s in sorted(recorded) if s not in DRIVER_EXCLUSIONS]
    return ",".join(keep)


DEFAULT_SCRIPTS = default_scripts()

# Drivers that compare this tree against a REF rather than a recorded
# fixture. tests/run.sh exports GOLDEN_REF (default origin/main) and its CI
# resolves that per event: the pull request's merge-base -- "exactly the
# code this PR forked from" -- and HEAD^1 on a push or on the nightly. A
# bare `run_script` call would hand env_drift its own origin/main default
# whatever the event, and on a tree that IS origin/main that is the
# self-comparison run.sh skips rather than making ("...is this commit").
# The instrument mirrors the gate's resolution and, where the gate would
# skip, drops the driver for this run with the gate's own sentence.
REF_DRIVEN = ("tests/env_drift.py", "tests/stress.py")


def gate_ref(scope: str, base: str) -> str | None:
    """The ref tests/run.sh would compare this tree against."""
    env = os.environ.get("GOLDEN_REF", "").strip()
    if env:
        return env
    if scope == "full":
        # The nightly's comparison ref (tests.yml resolves HEAD^1 for it).
        return "HEAD^1"
    sha = subprocess.run(
        ["git", "merge-base", base, "HEAD"], cwd=ROOT,
        capture_output=True, text=True,
    ).stdout.strip()
    return sha or None


def _rev(tree: Path, ref: str) -> str | None:
    out = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        cwd=tree, capture_output=True, text=True,
    )
    return out.stdout.strip() or None


def ref_skip_reason(ref: str | None, tree: Path) -> str | None:
    """tests/run.sh's reason not to run a ref-driven driver here, or None.

    The two sentences are lane_golden's own skips: an unresolvable ref
    ("is not available here") and one that resolves to HEAD ("is this
    commit; use GOLDEN_REF=HEAD^1 to check it"). env_drift refuses either
    run itself -- a comparison that cannot fail is not a gate -- so the
    gate skips it out loud; so does the instrument, at the baseline.
    """
    if not ref:
        return "the comparison ref could not be resolved"
    if _rev(tree, ref) is None:
        return f"{ref} is not available here"
    if _rev(tree, ref) == _rev(tree, "HEAD"):
        return f"{ref} is this commit; use GOLDEN_REF=HEAD^1 to check it"
    return None


def drive_spec(script: str, ref: str | None) -> tuple[list[str], dict[str, str]]:
    """How the GATE invokes this script: run.sh's arguments and environment.

    env_drift.py is the drift step and takes its ref after --all
    (tests/run.sh lane_golden); stress.py reads GOLDEN_REF from the
    environment, as the gate exports it. Every other recorded script runs
    bare, and so does env_drift.py when no ref survived the skip check.
    """
    if script == "tests/env_drift.py":
        return ["--all", ref or "origin/main"], {}
    if script == "tests/stress.py":
        return [], ({"GOLDEN_REF": ref} if ref else {})
    return [], {}


# ------------------------------------------------------------ survivor triage
#
# A survivor is not automatically a defect (#1217, D3-07): a mutant measured
# EQUIVALENT to its original -- no input can tell the two apart -- cannot be
# killed by any check, so counting it as a gap makes the recorded fraction
# read worse than the suite is. The marks live in tests/mutation_budgets.json
# under "survivor_triage", keyed like the recorded survivor table prints
# ("FILE:LINE KIND") and pinned to the exact `old` line text the triage was
# made on: an entry whose file:line, operator OR line text no longer matches
# is not applied, because a mark must not outlive the line it explains.
#
# The fraction the cap reads counts only survivors no triage has called
# equivalent. The default for an unmarked survivor is "a real gap": absence
# of a triage is not a finding of equivalence, so a mark can only ever relax
# the one-sided cap deliberately, with a reason, in a reviewed edit.
TRIAGE_VERDICTS = ("equivalent", "gap")
_TRIAGE_KEY = re.compile(rf"^{re.escape(PKG)}[^:\s]+:\d+ [A-Z_]+$")


def triage_key(mut: dict) -> str:
    """The recorded table's key for one survivor, as budgets prints it."""
    return f"{mut['file']}:{mut['line']} {mut['kind']}"


def triaged_equivalent(triage: dict, mut: dict) -> bool:
    """True when a triage marks THIS exact mutant equivalent.

    The key must match and the `old` pin must equal the line text the mutant
    was generated from -- file:line coordinates survive edits that the text
    does not, and an equivalence claim is a claim about the text.
    """
    entry = triage.get(triage_key(mut))
    return bool(
        entry
        and entry.get("verdict") == "equivalent"
        and entry.get("old") == mut["old"]
    )


def survivor_gaps(survivors: list[dict], triage: dict):
    """The survivors, split into (counted as gaps, triaged equivalent).

    The first list is the fraction's numerator: survivors no triage has
    called equivalent, in the order they were reported.
    """
    gaps: list[dict] = []
    equivalent: list[dict] = []
    for mut in survivors:
        (equivalent if triaged_equivalent(triage, mut) else gaps).append(mut)
    return gaps, equivalent


def triage_problems(triage: dict) -> list[str]:
    """Every way the recorded triage is malformed, one sentence each.

    An equivalence mark relaxes a one-sided cap, so it must carry the verdict
    that says so, the line pin it was measured against, and a reason -- an
    unargued claim is exactly the shape this validator exists to refuse.
    """
    out: list[str] = []
    for key, entry in sorted(triage.items()):
        if not _TRIAGE_KEY.match(key):
            out.append(f"{key!r} is not 'FILE:LINE KIND' under {PKG}")
            continue
        if not isinstance(entry, dict):
            out.append(f"{key}: entry is not an object")
            continue
        if entry.get("verdict") not in TRIAGE_VERDICTS:
            out.append(f"{key}: verdict {entry.get('verdict')!r} is not one "
                       f"of {TRIAGE_VERDICTS}")
        if not str(entry.get("reason", "")).strip():
            out.append(f"{key}: no reason -- an unargued equivalence claim "
                       "would quietly relax the fraction")
        if not str(entry.get("old", "")):
            out.append(f"{key}: no `old` line pin -- the mark would outlive "
                       "the line it explains")
    return out


# ------------------------------------------------ deterministic inventory
#
# The fraction cap above is a sample: the seeded draw over `--per-file` and
# `--max` reaches ~1% of the tree, so a guard the sample never draws cannot
# fail the lane, and a cap parked at 1.0 cannot refuse anyway (the rate is a
# fraction in [0, 1]). The inventory below enumerates EVERY candidate the six
# operators generate, deterministically -- `candidates()` walks the AST in a
# fixed order -- so an exact count over it is reproducible and comparable
# between clean branches, which is the property `tests/structure.py`'s ratchet
# has and the sampled pool could not. A site carries a disposition (`killed_by`
# or `survivor_triage`) or it is unpinned; the ratchet refuses when the unpinned
# count grows, and the completeness check refuses when the ledger disagrees
# with the inventory in either direction.


def inventory(files: list[Path] | None = None) -> list[dict]:
    """Every candidate site the six operators generate, deterministically.

    `candidates()` walks the AST breadth-first in a fixed order and `rglob`
    sorts the files, so the list is stable across runs and across clean
    branches. The sort key is the whole identity -- file, line, kind, then the
    `old` text -- so unlike the seeded sample this is the whole tree and an
    exact count over it is a fair ratchet.
    """
    files = files if files is not None else sorted(PRODUCTION.rglob("*.py"))
    out: list[dict] = []
    for path in files:
        out.extend(candidates(path))
    out.sort(key=lambda m: (m["file"], m["line"], m["kind"], m["old"]))
    return out


def dispositions(budgets: dict) -> dict[str, dict]:
    """Every recorded disposition, merged from the two ledger maps.

    `survivor_triage` holds verdicts (equivalent/gap); `killed_by` holds a
    driver name. Both are keyed `file:line KIND` and pinned to the `old` text.
    """
    out: dict[str, dict] = {}
    for key, entry in budgets.get("survivor_triage", {}).items():
        out[key] = dict(entry)
    for key, entry in budgets.get("killed_by", {}).items():
        out[key] = dict(entry)
    return out


def disposition_matches(entry: object, site: dict) -> bool:
    """True when a recorded disposition covers THIS exact site.

    The key is `file:line KIND` and the pin is the exact `old` line text -- a
    mark must not outlive the line it explains.
    """
    if not isinstance(entry, dict):
        return False
    if entry.get("old") != site["old"]:
        return False
    return (
        entry.get("verdict") in TRIAGE_VERDICTS
        or "killed_by" in entry
    )


def unpinned_sites(budgets: dict, sites: list[dict]) -> list[dict]:
    """The candidate sites no recorded disposition covers."""
    disp = dispositions(budgets)
    return [s for s in sites
            if not disposition_matches(disp.get(triage_key(s)), s)]


def ratchet_refusal(budgets: dict, unpinned: list[dict]) -> int | None:
    """The exact-count ratchet's verdict: 1 (refuse) or None (proceed).

    `unpinned_sites` only moves down. A diff that adds a candidate site without
    a disposition raises the count and is refused; a budget with no record yet
    is not refused (there is nothing to ratchet against), and a count at or
    below the record proceeds -- a count below is an improvement to record.
    """
    record = budgets.get("unpinned_sites")
    if record is None:
        return None
    return 1 if len(unpinned) > record else None


def completeness_problems(budgets: dict, sites: list[dict]) -> list[str]:
    """Every way the ledger and the deterministic inventory disagree.

    Two directions, plus the null control: a disposition whose key and `old`
    pin no longer name a site the inventory generates (a mark outliving its
    line, or the inventory having dropped a site), and an empty inventory,
    which is RED rather than green-by-skipping. The forward direction -- a
    site with no disposition -- is the ratchet's count, not a refusal here.
    """
    if not sites:
        return ["0 candidate site(s) in scope -- an empty inventory is a "
                "failed enumeration, not a passing one"]
    out: list[str] = []
    for key, entry in sorted(dispositions(budgets).items()):
        old = entry.get("old") if isinstance(entry, dict) else None
        if not any(triage_key(s) == key and s["old"] == old for s in sites):
            out.append(f"{key}: disposition names no site the inventory "
                       f"generates (old pin {old!r})")
    return out


# A VERBATIM copy of tests/structure.py's cap_problem, the recorded-number
# barrier every ratchet shares (#1583's review). This grader is a single
# standard-library file on purpose -- a job may restore it from the base
# and run it under `python3 -I`, where a sibling import neither resolves
# nor stays the base's -- so it carries the copy, and tests/entities.py
# refuses any copy that differs from the original by one character.
def cap_problem(where: str, table: object, key: str, *, integer: bool = False,
                low: float = 0.0, low_open: bool = False,
                high: float | None = None) -> str | None:
    """Why ``table[key]`` cannot be a ratchet's recorded number, or None.

    The class this closes (#1583's review): Python's json reads ``NaN``,
    ``Infinity``, ``-Infinity`` and ``1e999`` as floats without complaint, and
    every comparison against NaN is False -- ``current > nan`` never fires and
    ``raw < nan`` never fires -- so a cap edited to NaN was an unlimited raise
    that this script printed as ``ok cut_views 110 <= nan``. Infinity passes
    by arithmetic. The other spellings fail differently per script and none of
    them says why: a string crashed one comparison and ``float()``-coerced in
    another (``"nan"`` into NaN), and a bool is 0 or 1 to Python.

    So every ratchet calls this on load and refuses before it compares. It
    refuses: an absent key, a bool, anything not an int or float, a
    non-finite number, a float where ``integer`` asks for a count, a value
    below ``low`` (or equal to it when ``low_open``), and one above ``high``.
    The message names the file, the key and the value, so the refusal is the
    fix's instructions.
    """
    if not isinstance(table, dict) or key not in table:
        return (f"{where}: {key} is absent -- a ratchet with no recorded "
                f"number compares against nothing")
    value = table[key]
    label = f"{where}: {key}={value!r}"
    if isinstance(value, bool):
        return (f"{label} is a boolean, which Python compares as "
                f"{int(value)}; record the number")
    if not isinstance(value, (int, float)):
        return f"{label} is a {type(value).__name__}, not a number"
    if not math.isfinite(value):
        return (f"{label} is not finite: every comparison against NaN is "
                f"false and nothing exceeds Infinity, so this cap would be an "
                f"unlimited raise")
    if integer and not isinstance(value, int):
        return f"{label} is a float where a count is recorded"
    if value < low or (low_open and value == low):
        return f"{label} is {'at or ' if low_open else ''}below {low:g}"
    if high is not None and value > high:
        return f"{label} is above {high:g}"
    return None


def cap_problems(budgets: dict) -> list[str]:
    """Every recorded cap that cannot refuse, one sentence each.

    `rate = survivors/evaluated` is a fraction in [0, 1], so a cap of 1.0
    makes `if rate > cap` unreachable: a run in which every mutant survives
    still prints PASSED. A cap has to be saturable to be a gate.

    Before that, each cap passes `cap_problem` (the verbatim copy above), the
    barrier every ratchet shares: `rate > nan` and `len(unpinned) > nan` are both False, so
    a NaN in either row was an unlimited raise this pre-pass let through
    (#1583's review). `unpinned_sites` may be absent -- the bootstrap
    `ratchet_refusal` documents -- but a present one is a non-negative count.
    """
    where = BUDGETS.name
    fractions = budgets.get("max_survivor_fraction")
    out: list[str] = []
    for scope in ("changed", "full"):
        problem = cap_problem(where, fractions, scope, high=1.0)
        if problem:
            out.append(problem.replace(f": {scope}", f": max_survivor_fraction[{scope}]", 1))
        elif fractions[scope] >= 1.0:
            out.append(f"max_survivor_fraction[{scope}]={fractions[scope]} is "
                       f"unsatisfiable: a survivor rate in [0, 1] can never "
                       f"exceed it")
    if "unpinned_sites" in budgets:
        problem = cap_problem(where, budgets, "unpinned_sites", integer=True)
        if problem:
            out.append(problem)
    return out


# ------------------------------------------------------------------- runner

class ScriptRun(NamedTuple):
    """One gate script's measured result, carrying the output it was judged on.

    The failure count is read out of stdout (#805) and that text -- with
    stderr -- is returned alongside it rather than discarded once the count is
    pulled. It is the only place the failing CHECK is named, and #1134 is a
    refusal that could once name the red script and nothing more.
    """
    rc: int
    failed: int
    seconds: float
    stdout: str = ""
    stderr: str = ""


def failed_checks(run: ScriptRun) -> list[str]:
    """The failing checks one run reported, in the order it printed them.

    The shared harness prints `  FAIL <name>  [detail]` per failed check
    (`tests/harness.py`, `Results.check`) and the drivers that keep their own
    counter print the same line, so the red CHECK is recoverable from the
    stdout `run_script` captures.

    A script that crashes, or one that prints `ISSUES:` bullets rather than
    harness FAIL lines (`tests/plan_view.py`, `tests/validate.py`), names no
    check in that form; the last non-empty line of its output is returned
    instead, which for those is the reason it went red. That fallback is taken
    only on a RED run: a green script has no failing check, so it returns none.
    """
    names = [m.group(1) for m in _CHECK_FAIL.finditer(run.stdout)]
    if names:
        return names
    if run.rc == 0:
        return []
    tail = [ln.strip() for ln in (run.stdout + "\n" + run.stderr).splitlines()
            if ln.strip()]
    return tail[-1:]


def run_script(script: str, cwd: Path, timeout: int,
               extra_args: list[str] | None = None,
               extra_env: dict[str, str] | None = None) -> ScriptRun:
    """(exit status, failed-check count, seconds, stdout, stderr) for one script.

    Reads the WHOLE of stdout: the last `N of M ... FAILED` line anywhere in it,
    not the tail of a buffer (#805). The captured output is returned with the
    counts, so a caller can name the failing CHECK inside a red script and not
    only the script (#1134).

    ``extra_args``/``extra_env`` are how the GATE invokes the ref-driven
    drivers (#1211): `env_drift.py --all <ref>` and stress.py's exported
    GOLDEN_REF. Default None is the bare invocation every other lane uses.
    """
    started = time.monotonic()
    try:
        proc = subprocess.run(
            [sys.executable, script, *(extra_args or ())], cwd=cwd,
            capture_output=True, text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONPATH": "tests/hastub", **(extra_env or {})},
        )
    except subprocess.TimeoutExpired:
        # A mutant that hangs its driver is noticed, not silently survived.
        return ScriptRun(TIMEOUT_RC, 1, time.monotonic() - started, "",
                         f"{script}: timed out after {timeout}s")
    run = ScriptRun(proc.returncode, 0, time.monotonic() - started,
                    proc.stdout, proc.stderr)
    return run._replace(failed=failing_count(run))


def failing_count(run: ScriptRun) -> int:
    """How many failing checks a run names as its own -- 0 for a green run.

    A green run names none, whatever it printed: tests/entities.py's green run
    prints dozens of `FAIL` lines, every one a negative control it drove on
    purpose. A red run's tally is read from the first form it prints, most
    authoritative first: the harness's closing `N of M ... FAILED` (the LAST
    one, as a nested control may print its own earlier), the sum of the
    summary counts (`_SUMMARY_FAILS`; env_drift.py prints up to three), the
    `ISSUES:` bullets, and only then the `FAIL <name>` lines -- plus one for an
    uncaught exception, an assertion the driver never finished, and one for a
    timeout. A red run that names none of these is a refusal, not a verdict.
    """
    if run.rc == 0:
        return 0
    out = run.stdout
    n_of_m = _FAILED.findall(out)
    summaries = [int(n) for n in _SUMMARY_FAILS.findall(out)]
    bullets = [len(b.splitlines()) for b in _ISSUE_BULLETS.findall(out)]
    if n_of_m:
        n = int(n_of_m[-1][0])
    elif summaries:
        n = sum(summaries)
    elif bullets:
        n = sum(bullets)
    else:
        n = len(_CHECK_FAIL.findall(out))
    crashed = _TRACEBACK in run.stderr
    timed_out = run.rc == TIMEOUT_RC and not out
    return n + int(crashed) + int(timed_out)


def killed(script: str, run: ScriptRun, baseline: ScriptRun) -> bool:
    """Whether `script`'s run on a mutant noticed the mutation (#1453, #1521).

    Killed when the run is red AND names more failing checks than the
    unmutated baseline's did -- which, the baseline being green by the time any
    mutant is driven (`baseline_refusal`), means at least one. A changed exit status alone is not a kill: it
    is how a driver also says "nothing here is a violation" (structure.py's
    exit 2 for a metric that only IMPROVED, #1453) and "I refuse to measure
    this diff" (env_drift.py's INHERITED CLAIMS refusal, which fires before any
    capture on every production edit while the fork point carries a claim
    list, #1521). The rule is the same for every driver, so a driver that
    gains a new non-violation status needs no entry anywhere; the old
    per-driver table (`NON_VIOLATION_EXITS`) is retired, because this rule
    reads structure.py's exit 2 as no kill without it. `script` names the
    driver for the caller's verdict line; the rule itself is driver-blind.
    """
    del script
    return run.rc != 0 and failing_count(run) > failing_count(baseline)


# How a driver's SOURCE prints each form `failing_count` reads: a string
# literal (an f-string's constant parts included) that opens a FAIL line or
# carries a summary's wording. Source text, not a run: running every driver
# red is the nightly's cost, and this only has to see that one form exists.
_VERDICT_SOURCE = re.compile(
    r"^\s*FAIL\b|FAILED\b|FAILURES\b|ISSUES:|UNCLAIMED DRIFT\(S\)"
    r"|COMMITTED FIXTURE\(S\) ARE STALE")


def verdict_form_problems(scripts: list[str]) -> list[str]:
    """Each driver whose source prints no failing-check form the rule reads.

    Such a driver can exit red on a mutant and never kill it, which reads as
    a survivor and as a finding about production. A driver that imports
    `tests/harness.py` prints through `Results.check`/`close`, so the harness's
    literals count as its own.
    """
    out: list[str] = []
    for script in scripts:
        path = Path(script) if Path(script).is_absolute() else ROOT / script
        if path.suffix != ".py" or not path.exists():
            continue
        tree = ast.parse(path.read_text())
        sources = [tree]
        if any(isinstance(n, (ast.Import, ast.ImportFrom))
               and "harness" in ([a.name for a in n.names]
                                 + [getattr(n, "module", None) or ""])
               for n in ast.walk(tree)):
            sources.append(ast.parse((ROOT / "tests/harness.py").read_text()))
        if not any(isinstance(n, ast.Constant) and isinstance(n.value, str)
                   and _VERDICT_SOURCE.search(n.value)
                   for t in sources for n in ast.walk(t)):
            out.append(f"{script}: prints no FAIL line, FAILED/FAILURES "
                       "count, ISSUES list or drift verdict, so a red run of "
                       "it can never read as a kill")
    return out


def null_control(path: Path) -> dict | None:
    """A comment-only edit of `path`: the run's built-in null control (#1521).

    The first line that holds a comment and nothing else gains a few words at
    its end, so no line number, no code token and no line count moves. No
    driver can notice it through behaviour, so a driver that "kills" it is
    reacting to the diff's shape -- env_drift.py's claim hygiene did, on every
    mutant -- and every verdict that driver gave in the same run is suspect.
    """
    import io
    import tokenize

    src = path.read_text()
    lines = src.splitlines()
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, SyntaxError):
        return None
    for tok in toks:
        ln = tok.start[0]
        if (tok.type == tokenize.COMMENT and lines[ln - 1].strip() == tok.string
                and len(lines[ln - 1]) < 60):
            try:
                rel = str(path.relative_to(ROOT))
            except ValueError:
                rel = str(path)
            return dict(kind="NULL_COMMENT", file=rel, line=ln,
                        old=lines[ln - 1],
                        new=lines[ln - 1] + " (null control)")
    return None


def null_control_verdict(runs: dict[str, ScriptRun],
                         baseline: dict[str, ScriptRun]) -> str:
    """LIVES, or which drivers "killed" the null control and on what.

    Every driver in play is scored, none is skipped at the first kill, and a
    driver the null control never ran under is a verdict too ("not run"): the
    point is to name every driver that is judging the diff.
    """
    missing = sorted(set(baseline) - set(runs))
    if missing:
        return "not run under " + ", ".join(missing)
    killers = [
        f"{s} ({'; '.join(failed_checks(runs[s])) or 'no FAIL line'})"
        for s in sorted(baseline) if killed(s, runs[s], baseline[s])
    ]
    return "killed by " + ", ".join(killers) if killers else "LIVES"


def null_control_refusal(key: str, verdict: str) -> str | None:
    """The run's refusal when its null control did not survive, else None.

    Anything but LIVES refuses -- a kill, and equally a null control that was
    skipped or never ran, because then nothing separates a kill from a driver
    reacting to the diff itself.
    """
    if verdict == "LIVES":
        return None
    return (f"\nMUTATION TABLE REFUSED -- the null control {key} was "
            f"{verdict}. A comment-only edit changes no behaviour, so a driver "
            "that notices it is judging the diff rather than the code, and "
            "none of this run's kills can be told apart from that.")


def null_for(pool: list[dict]) -> dict | None:
    """The run's null control: a whole-line comment in a file of the pool.

    Read off the file itself, never through `drawable`: the null control is
    this tool's own edit, not the diff's, and a line-scoped pool would
    otherwise filter out the only kind of line it can edit. An empty pool has
    no null control, and main() passes it before asking.
    """
    return next(filter(None, (null_control(ROOT / f)
                              for f in sorted({m["file"] for m in pool}))),
                None)


@contextlib.contextmanager
def null_edit(tree: Path, null: dict):
    """`tree` with the null control's comment written in, restored on exit.

    The edit is the whole null control: a run in a tree it never reached is
    the unmutated baseline again, and would "survive" every driver while
    measuring nothing.
    """
    path = tree / null["file"]
    original = path.read_text()
    lines = original.splitlines(True)
    lines[null["line"] - 1] = null["new"] + "\n"
    path.write_text("".join(lines))
    try:
        yield path
    finally:
        path.write_text(original)


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


# ----------------------------------------------------------------- schedule
#
# The job's wall clock is the baseline plus the slowest worker, and both were
# serial where the verdict did not need them to be (the mutation-timeout root
# cause). The baseline drove every driver in play on one tree while the other
# workers idled -- one full sweep of the net, which #1211 made env_drift.py and
# stress.py part of -- and a mutant's drivers ran only on the worker that drew
# it, so a survivor, which every driver must see, was a second full sweep on
# one worker. Both are spread over the worker trees below. No driver leaves
# the net and no mutant stops sooner than it did, so every verdict is the one
# the serial sweep gave; only which driver is NAMED as a mutant's killer can
# change, as it already could with the measured cheapest-first order.
# The one driver kept off that sharing is EXCLUSIVE below.


def _share(workers: int, work) -> None:
    """Run `work(worker)` on every worker at once; re-raise what any raised."""
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for fut in [ex.submit(work, w) for w in range(workers)]:
            fut.result()


# Drivers that measure the MACHINE while they run, so they never share it.
# stress.py times its solves against tests/stress_budgets.json -- the reason
# `/tmp/hpo-gate.lock` serialises it locally -- and beside three other drivers
# on a CI runner its baseline hit the 1200 s per-driver timeout (#1565's first
# run: rc=124, the table INCONCLUSIVE with no mutant scored) where alone it
# takes 674-960 s. An exclusive driver runs with no other driver in flight, in
# the baseline and for every mutant alike.
EXCLUSIVE = ("tests/stress.py",)


def drive_baselines(needed: list[str], workers: int, run, *, null_run=None,
                    null_out: dict | None = None) -> dict[str, ScriptRun]:
    """Every driver's unmutated run, spread over `workers` trees.

    `run(worker, script)` drives one script in that worker's tree. The shared
    drivers go first, the ref-driven ones at the head of the queue: they are
    the net's longest shared runs, and a long run started last is what sets
    the makespan. Each EXCLUSIVE driver then runs alone.

    `null_run(worker, script)`, when given, drives the null control under the
    same script, and its result lands in `null_out`: a task in the same queue
    beside that script's baseline, never a process beside the workers, and
    alone like the baseline when the script is EXCLUSIVE.
    """
    kinds = (False, True) if null_run is not None else (False,)
    tasks = [(s, k) for s in sorted(needed,
                                    key=lambda s: (s not in REF_DRIVEN, s))
             for k in kinds]
    queue = [t for t in tasks if t[0] not in EXCLUSIVE]
    lock = threading.Lock()
    out: dict[str, ScriptRun] = {}

    def one(w: int, task: tuple[str, bool]) -> None:
        script, is_null = task
        if is_null:
            null_out[script] = null_run(w, script)
        else:
            out[script] = run(w, script)

    def work(w: int) -> None:
        while True:
            with lock:
                if not queue:
                    return
                task = queue.pop(0)
            one(w, task)

    _share(workers, work)
    for task in (t for t in tasks if t[0] in EXCLUSIVE):
        one(0, task)
    return out


def drive_pool(pool: list[dict], workers: int, cost: dict[str, float],
               drive) -> list[tuple[dict, str]]:
    """Each mutant's verdict, its drivers shared over `workers` trees.

    `drive(worker, mut, script)` runs one driver on `mut` in that worker's tree
    and says whether it killed it. A worker sweeps the next unstarted mutant,
    its shared drivers in the order given (cheapest first), stopping at the
    first kill. Once no mutant is left unstarted it helps instead: it takes the
    costliest not-yet-started shared driver of a mutant still undecided, since
    a survivor's sweep is the one that cannot stop early. Every EXCLUSIVE
    driver is deferred past that phase and run alone, one at a time, for each
    mutant no shared driver killed -- so only those pay for it. A mutant is
    killed by the first driver to report a kill, and LIVES only once every one
    of its drivers has run and none did.
    """
    lock = threading.Lock()
    todo = [[s for s in m["drivers"] if s not in EXCLUSIVE] for m in pool]
    running = [0] * len(pool)
    verdict: list[str | None] = [None] * len(pool)
    unstarted = [i for i in range(len(pool)) if todo[i]]
    own: list[int | None] = [None] * workers

    def take(w: int) -> tuple[int, str] | None:
        with lock:
            i = own[w]
            if i is None or verdict[i] is not None or not todo[i]:
                i = own[w] = unstarted.pop(0) if unstarted else None
            if i is not None:
                script = todo[i].pop(0)
            else:
                open_ = [j for j in range(len(pool))
                         if verdict[j] is None and todo[j]]
                if not open_:
                    return None
                i = max(open_, key=lambda j: cost.get(todo[j][-1], 0.0))
                script = todo[i].pop()
            running[i] += 1
            return i, script

    def work(w: int) -> None:
        while (task := take(w)) is not None:
            i, script = task
            hit = drive(w, pool[i], script)
            with lock:
                running[i] -= 1
                if verdict[i] is None and hit:
                    verdict[i] = f"killed by {script}"

    _share(workers, work)
    for i, mut in enumerate(pool):
        for script in (s for s in mut["drivers"] if s in EXCLUSIVE):
            if verdict[i] is None and drive(0, mut, script):
                verdict[i] = f"killed by {script}"
    return [(m, v or "LIVES") for m, v in zip(pool, verdict)]


def baseline_refusal(baseline: dict[str, ScriptRun], scope: str) -> int | None:
    """The verdict on a red baseline, or ``None`` when it is green.

    A red baseline makes every mutant's verdict meaningless: the table
    evaluated nothing, so no mutation information is lost either way. The two
    scopes differ only in what that is worth reporting as, and `mutation` is
    not a required context while `fast` is.

    **The baseline's driver set is a subset of the scoped gate's selection.**
    The drivers are those whose measured closure reaches a file the diff
    wrote code in, and the gate selects every script whose closure reaches a
    changed file, so a red here is `fast`'s red restated. Re-derive that at
    your own merge base: `scope_files("changed", base)` with `drivers_for`,
    against `tests/closure.py select --diff <merge-base>`.

    `--scope full` keeps the refusal: it runs on a schedule, where nothing
    else reports that lane's baseline per commit.

    `run_script` returns the stdout and stderr it judged alongside the counts,
    so this names the red SCRIPT and, from that captured output, the failing
    CHECK inside it -- rather than sending the reader back to re-run the script
    to learn which check went red (#1134).
    """
    red = sorted(s for s, run in baseline.items() if run.rc != 0)
    if not red:
        return None
    print("\nMUTATION TABLE INCONCLUSIVE")
    print("  - the baseline is already red in " + ", ".join(red) +
          ", so no mutant's verdict means anything. Fix the suite first. "
          "A script the scoped gate also selected carries this red on "
          "`fast`; one it scoped out does not, and is covered by the forced "
          "`full` run on `main` rather than by any check on this pull "
          "request.")
    for s in red:
        checks = failed_checks(baseline[s])
        print(f"      {s}: " + ("; ".join(checks) if checks
                                 else "no FAIL line in its output"))
    return 1 if scope == "full" else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", choices=("changed", "full"), default="changed")
    ap.add_argument("--base", default="origin/main")
    ap.add_argument(
        "--scripts",
        default=DEFAULT_SCRIPTS,
        help="candidate drivers; defaults to default_scripts(): every script "
             "tests/closures.json records, minus the DRIVER_EXCLUSIONS, "
             "which carry the property that excludes them. Each mutant runs "
             "only those whose recorded closure contains its file, cheapest "
             "measured first",
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
    # A cap that cannot fail is not a gate (#1412). Refused before any
    # baseline cost, symmetric to the triage check below.
    cap_p = cap_problems(budgets)
    if cap_p:
        print("MUTATION TABLE REFUSED -- a cap that cannot fail:")
        for p in cap_p:
            print(f"    - {p}")
        return 1
    cap = float(budgets["max_survivor_fraction"][args.scope])
    # The survivor triage (#1217): recorded equivalence marks are audit
    # measurements pinned to the line text they were made on. A malformed one
    # moves the fraction, so the run refuses before any baseline cost.
    triage = budgets.get("survivor_triage", {})
    problems = triage_problems(triage)
    if problems:
        print("MUTATION TABLE REFUSED -- survivor_triage in "
              f"{BUDGETS.name} is malformed:")
        for p in problems:
            print(f"    - {p}")
        return 1
    # The deterministic inventory + completeness ledger (#1412). Source-only:
    # no clone, no baseline, no solve, and it covers the WHOLE tree -- the
    # 3816 sites the sampled pool never draws. It runs before the sample
    # because the ratchet is over the whole tree, not over the diff's pool.
    sites = inventory()
    comp = completeness_problems(budgets, sites)
    if comp:
        print("MUTATION TABLE REFUSED -- the ledger disagrees with the "
              "deterministic inventory:")
        for p in comp:
            print(f"    - {p}")
        return 1
    unpinned = unpinned_sites(budgets, sites)
    record = budgets.get("unpinned_sites")
    if ratchet_refusal(budgets, unpinned) == 1:
        print(f"MUTATION TABLE REFUSED -- {len(unpinned)} unpinned site(s) "
              f"against a recorded {record}. A new guard, clamp, removable "
              f"return or doubled constant left the tree without a recorded "
              f"disposition; record it under killed_by or survivor_triage and "
              f"the count falls back.")
        for s in sorted(unpinned, key=lambda m: (m["file"], m["line"]))[:20]:
            print(f"    {triage_key(s)}: {s['old'].strip()[:72]}")
        return 1
    if record is None:
        print(f"  {len(unpinned)} candidate site(s) in the deterministic "
              f"inventory; no `unpinned_sites` recorded yet -- run --record "
              f"to set the ratchet")
    elif len(unpinned) < record:
        print(f"  {len(unpinned)} unpinned site(s) < recorded {record} -- "
              f"re-record with --record to ratchet the count down")
    else:
        print(f"  {len(unpinned)} unpinned site(s) of {len(sites)} candidate "
              f"sites; the ledger agrees with the deterministic inventory")
    files, why = scope_files(args.scope, args.base)
    allow = [s for s in args.scripts.split(",") if s]
    closures = load_closures()
    print(f"MUTATION TABLE -- scope {args.scope}: {why}")
    # The ref the gate would compare against, resolved once in this checkout
    # -- every clone below is a worktree of it at this same HEAD (#1211). A
    # ref-driven driver whose ref the gate itself would skip cannot drive
    # anything here: drop it from the net now, so it never costs a baseline
    # that would then be red for the environment rather than for the code.
    ref = gate_ref(args.scope, args.base)
    for s in list(allow):
        if s in REF_DRIVEN:
            why_skip = ref_skip_reason(ref, ROOT)
            if why_skip:
                allow.remove(s)
                print(f"  SKIP {s} ({why_skip})")
    if not files:
        print("  no production file in scope; nothing to mutate")
        print("\nMUTATION TABLE PASSED (empty scope)")
        return 0

    rng = random.Random(args.seed)
    pool: list[dict] = []
    # A pull request draws only from the lines it wrote (`changed_lines`).
    touched = changed_lines(args.base) if args.scope == "changed" else None
    for path in files:
        rel = str(path.relative_to(ROOT))
        drivers = drivers_for(rel, closures, allow)
        if not drivers:
            print(f"  no recorded closure reaches {rel}; skipped")
            continue
        got = drawable(path, rel, touched)
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
    if any(s in REF_DRIVEN for s in needed):
        print(f"  ref-driven drivers compare against {ref!r} "
              f"(run.sh's GOLDEN_REF resolution)")
    # A driver whose red output the kill rule cannot read can never kill, and
    # every mutant only it reaches would read as a survivor: refuse first.
    blind = verdict_form_problems(needed)
    if blind:
        print("\nMUTATION TABLE REFUSED -- a driver in play prints no "
              "failing-check form `failing_count` reads:")
        for b in blind:
            print(f"    - {b}")
        return 1
    # The null control: a comment-only edit in a file the pool already
    # mutates (`null_for`), driven by EVERY driver in play and never stopped
    # at the first "kill". Its runs are baseline-phase tasks on the worker
    # trees (`drive_baselines`), so it is never a process beside them, and its
    # stress.py run is EXCLUSIVE like any other (#1565).
    null = null_for(pool)
    if null is None:
        print("\nMUTATION TABLE REFUSED -- no full-line comment in any file "
              "in the pool, so the run has no null control and no verdict "
              "can be told apart from a driver reacting to the diff itself")
        return 1
    print(f"  null control: {triage_key(null)}, a comment-only edit every "
          f"driver in play must let survive")

    work = Path(tempfile.mkdtemp(prefix="mutation-table-"))
    made: list[Path] = []
    try:
        # One tree per worker, cloned before the baseline: the baseline and
        # the null control run in them too, each on an unmutated tree.
        jobs = max(1, args.jobs)
        trees = [clone_tree(work / f"w{i}") for i in range(jobs)]
        made.extend(trees)

        def run_baseline(w: int, s: str) -> ScriptRun:
            extra_args, extra_env = drive_spec(s, ref)
            run = run_script(s, trees[w], args.timeout, extra_args, extra_env)
            # One write per line: the workers print concurrently.
            print(f"  baseline {s}: rc={run.rc} failed={run.failed} "
                  f"{run.seconds:.0f}s\n", end="")
            return run

        def run_null(w: int, s: str) -> ScriptRun:
            with null_edit(trees[w], null):
                extra_args, extra_env = drive_spec(s, ref)
                return run_script(s, trees[w], args.timeout, extra_args,
                                  extra_env)

        null_runs: dict[str, ScriptRun] = {}
        baseline = drive_baselines(needed, jobs, run_baseline,
                                   null_run=run_null, null_out=null_runs)
        verdict = baseline_refusal(baseline, args.scope)
        if verdict is not None:
            return verdict
        refusal = null_control_refusal(
            triage_key(null), null_control_verdict(null_runs, baseline))
        if refusal:
            print(refusal)
            return 1
        print(f"  null control {triage_key(null)} survived every driver")
        # Cheapest first, measured here rather than carried: a kill then costs
        # the cheapest driver that can see it.
        for mut in pool:
            mut["drivers"].sort(key=lambda s: baseline[s].seconds)

        results: list[tuple[dict, str]] = []
        mutated: dict[int, str] = {}
        for mut in pool:
            lines = (trees[0] / mut["file"]).read_text().splitlines(True)
            i = mut["line"] - 1
            if i >= len(lines) or lines[i].rstrip("\n") != mut["old"]:
                results.append((mut, "SKIP-MOVED"))
                continue
            lines[i] = mut["new"] + "\n"
            try:
                ast.parse("".join(lines))
            except SyntaxError:
                # A mutant that cannot run reports as a survivor, and a survivor
                # reads as a finding about production. W5-G7 t5 measured two.
                results.append((mut, "SKIP-UNPARSEABLE"))
                continue
            mutated[id(mut)] = "".join(lines)

        def drive(w: int, mut: dict, s: str) -> bool:
            # One task per worker at a time, so a tree carries one mutant.
            path = trees[w] / mut["file"]
            original = path.read_text()
            path.write_text(mutated[id(mut)])
            try:
                extra_args, extra_env = drive_spec(s, ref)
                run = run_script(s, trees[w], args.timeout, extra_args,
                                 extra_env)
                return killed(s, run, baseline[s])
            finally:
                path.write_text(original)

        results += drive_pool(
            [m for m in pool if id(m) in mutated], jobs,
            {s: r.seconds for s, r in baseline.items()}, drive)
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
    gaps, equivalent = survivor_gaps(survivors, triage)
    rate = len(gaps) / evaluated if evaluated else 0.0
    raw = n / evaluated if evaluated else 0.0
    equiv_note = (f" ({len(equivalent)} triaged equivalent, raw {raw:.1%})"
                  if equivalent else "")
    print(f"\n  {n} survivor(s) of {evaluated} evaluated = {rate:.1%}"
          f"{equiv_note}, cap {cap:.1%}")
    for mut in survivors:
        tri = ("  [triaged equivalent]"
               if triaged_equivalent(triage, mut) else "")
        print(f"    {mut['file']}:{mut['line']} {mut['kind']}: "
              f"{mut['old'].strip()[:72]}{tri}")

    if args.record:
        if rate > cap:
            print("\nREFUSED to record: a cap only moves down. "
                  f"{rate:.1%} > the recorded {cap:.1%}; either kill the "
                  "survivors, triage the equivalent ones, or raise it as a "
                  "deliberate, argued edit.")
            return 1
        budgets["max_survivor_fraction"][args.scope] = round(rate, 4)
        # The ratchet only moves down too: the pre-pass above already refused
        # growth, so `unpinned` is at or below the recorded count here.
        budgets["unpinned_sites"] = len(unpinned)
        budgets["last_measured"][args.scope] = {
            # `survivors` is the fraction's numerator -- survivors no triage
            # has called equivalent -- and `equivalent` the part of this run
            # the triage took off it. `survivor_lines` carries the whole
            # table, marks included, so the count can be read back line by
            # line.
            "survivors": len(gaps), "equivalent": len(equivalent),
            "evaluated": evaluated,
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "survivor_lines": [triage_key(m) for m in survivors],
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
              "wrong. Pin the ones above, or record the ones measured "
              "equivalent under survivor_triage in tests/mutation_budgets.json "
              "with the reason that says so.")
        return 1
    print("\nMUTATION TABLE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

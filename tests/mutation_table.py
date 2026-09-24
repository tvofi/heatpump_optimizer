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


def cap_problems(budgets: dict) -> list[str]:
    """Every fraction cap that cannot refuse, one sentence each.

    `rate = survivors/evaluated` is a fraction in [0, 1], so a cap of 1.0
    makes `if rate > cap` unreachable: a run in which every mutant survives
    still prints PASSED. A cap has to be saturable to be a gate.
    """
    out: list[str] = []
    for scope, value in sorted(budgets.get("max_survivor_fraction", {}).items()):
        try:
            f = float(value)
        except (TypeError, ValueError):
            out.append(f"max_survivor_fraction[{scope}]={value!r} is not a "
                       f"number")
            continue
        if f >= 1.0:
            out.append(f"max_survivor_fraction[{scope}]={f} is unsatisfiable: "
                       f"a survivor rate in [0, 1] can never exceed it")
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


def baseline_refusal(baseline: dict[str, ScriptRun], scope: str) -> int | None:
    """The verdict on a red baseline, or ``None`` when it is green.

    A red baseline makes every mutant's verdict meaningless: the table
    evaluated nothing, so no mutation information is lost either way. The two
    scopes differ only in what that is worth reporting as, and `mutation` is
    not a required context while `fast` is.

    **The baseline's driver set is not the scoped gate's selection, and on a
    test-only diff it is much wider.** Where the diff changes production files
    the drivers are a subset of what the gate selects, so a red here really is
    `fast`'s red restated. Where it changes none, `scope_files` falls back to
    every production file in the measured closure of the changed TEST scripts
    (the branch just above), and `drivers_for` returns every net script whose
    closure reaches one of them: measured on this function's own branch, 63
    production files and 19 drivers against the scoped gate's 1 selected
    script. (Both counts follow the driver net: the wider net of #1211 reaches
    more of the same files, and the baseline phase pays for each driver once.)
    That wider net is what a pull request gives up here -- an
    accidental detector, firing only when a scoped-out script happens to be
    red, never when a closure is merely wrong. The designed detectors for that
    hole are `closures`, `closure-scope`, `closures-autofix` and the forced
    `full` run on every push to `main`, and they are required. Re-derive the
    two numbers at your own merge base rather than trusting these:
    `scope_files("changed", base)` with `drivers_for`, against
    `tests/closure.py select --diff <merge-base>`.

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
    # The null control: a comment-only edit in a file the sample already
    # mutates, driven by EVERY driver in play and never stopped at the first
    # "kill". It runs in its own tree BESIDE the serial baseline phase, which
    # drives the same drivers, so it adds that phase's contention and not a
    # second serial pass of every driver to the mutant phase (#1561 review:
    # riding the pool, it put the job at 82 of its 90 minutes).
    null = next(filter(None, (null_control(ROOT / f)
                              for f in sorted({m["file"] for m in pool}))),
                None)
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
        base_tree = clone_tree(work / "baseline")
        made.append(base_tree)
        null_tree = clone_tree(work / "null")
        made.append(null_tree)
        null_path = null_tree / null["file"]
        null_lines = null_path.read_text().splitlines(True)
        null_lines[null["line"] - 1] = null["new"] + "\n"
        null_path.write_text("".join(null_lines))
        null_runs: dict[str, ScriptRun] = {}

        def drive_null() -> None:
            for s in needed:
                extra_args, extra_env = drive_spec(s, ref)
                null_runs[s] = run_script(s, null_tree, args.timeout,
                                          extra_args, extra_env)

        baseline: dict[str, ScriptRun] = {}
        # The `with` joins the null thread even when the baseline raises, so
        # the `finally` below never removes a tree a driver is still running in.
        with ThreadPoolExecutor(max_workers=1) as null_ex:
            null_job = null_ex.submit(drive_null)
            for s in needed:
                extra_args, extra_env = drive_spec(s, ref)
                run = run_script(s, base_tree, args.timeout, extra_args,
                                 extra_env)
                baseline[s] = run
                print(f"  baseline {s}: rc={run.rc} failed={run.failed} "
                      f"{run.seconds:.0f}s")
            null_job.result()
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
                    extra_args, extra_env = drive_spec(s, ref)
                    run = run_script(s, tree, args.timeout, extra_args,
                                     extra_env)
                    if killed(s, run, baseline[s]):
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

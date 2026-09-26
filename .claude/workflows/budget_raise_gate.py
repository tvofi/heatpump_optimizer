#!/usr/bin/env python3
"""budget_raise_gate.py -- a budget raise merges only on the owner's approval.

Decision 0013 as amended on 2026-09-24. The owner's direction that day: only
policy changes and budget RAISES are the code owner's, and a routine edit --
a ledger row, a structure metric re-recorded down -- runs without a human.
CODEOWNERS cannot draw that line, because it owns a path and not a direction:
owning `tests/mutation_budgets.json` put the owner's review on every fix that
re-pinned a ledger line. This check draws it, and the required context
`budget-raise-gate` enforces it.

WHAT IT COMPARES. Every tracked `*_budgets.json` at the merge base of the
pull request's base and head, against the same path at the head (added and
deleted files included). Each file is flattened to leaves -- a dict recurses, a
list and a scalar are one leaf -- and each leaf is classified by the first rule
in that file's SCHEMA whose key pattern matches it:

  max      a cap: higher is a raise, and so is a removed cap
  max0     a cap whose absence means zero (typing's per-code census)
  min      a floor: lower is a raise, and so is a removed floor
  override an owner-granted floor override: absent is the strict state, so its
           appearance is a raise, lowering it is a raise, removing it is not
  capfile  a per-file policy cap: max, but removing it is not a raise when the
           file it caps is gone from the head
  superset a list that may grow and never shrink (a role's `opens` sample)
  frozen   any change is a raise (the typing ruler's toolchain pins)
  free     metadata and records: comments, `recorded_at`, a run's
           measurements, the ledger's per-site dispositions

A leaf no rule matches is `frozen`, and a budget file with no SCHEMA entry is
entirely `frozen`: what the check cannot sign as routine counts as a raise.
A file that does not parse at either end is a raise, and so is a cap or floor
whose head value is not a finite number (NaN, an infinity, a string): the
ratchets compare against NaN and infinity as if they were caps, and pass.

WHAT IT DOES WITH ONE. No raise: exit 0, and the API is never asked. A raise:
exit 0 only when the owner's latest decisive review (APPROVED,
CHANGES_REQUESTED or DISMISSED; a COMMENTED review decides nothing) is APPROVED
and was submitted on this exact head SHA, by the login AND numeric id AND
account type pinned below. Anything else, a failed API read included, is exit 1.

WHAT IT DOES NOT SEE. A ledger disposition (`survivor_triage`, `killed_by`)
is a per-site record, not a cap, and is `free` here: an `equivalent` verdict
the fix reviewer accepted is routine work, not a raise. And a grader that
stops reading its cap file is not a budget edit at all -- that is the
enforcement surface's concern (`codeowners_gap.py`), not this check's.

HOW IT IS RUN. `.github/workflows/budget-raise-gate.yml` restores this file
from the base commit before running it under `python3 -I`, so a pull request
cannot edit the gate that grades it; the workflow re-runs it on
`pull_request_review`, so an approval turns it green without a push.

    python3 -I .claude/workflows/budget_raise_gate.py --base SHA --head SHA --pr N [--repo O/R]
    python3 .claude/workflows/budget_raise_gate.py --self-test
    python3 -I .claude/workflows/budget_raise_gate.py --rerun-stale RUN_ID [--repo O/R]
"""
from __future__ import annotations

import fnmatch
import json
import math
import os
import shutil
import tempfile
import subprocess
import sys

# The code owner, pinned three ways: a login alone can be renamed away and
# re-registered, an id alone says nothing about which account a reader meant.
# `gh api users/tvofi --jq '{login,id,type}'`, 2026-09-24.
OWNER_LOGIN = "tvofi"
OWNER_ID = 70032254
OWNER_TYPE = "User"
DEFAULT_REPO = "tvofi/heatpump_optimizer"
SUFFIX = "_budgets.json"

FREE, MAX, MAX0, MIN, OVERRIDE, CAPFILE, SUPERSET, FROZEN = (
    "free", "max", "max0", "min", "override", "capfile", "superset", "frozen")

# First match wins. A pattern is a tuple of fnmatch segments; a trailing "**"
# matches any remainder, including none.
SCHEMA: dict[str, list[tuple[tuple[str, ...], str]]] = {
    "tests/structure_budgets.json": [
        (("recorded_at",), FREE),
        (("*",), MAX),
    ],
    "tests/mutation_budgets.json": [
        (("_comment",), FREE),
        (("reason",), FREE),
        (("last_measured", "**"), FREE),
        (("survivor_triage", "**"), FREE),
        (("killed_by", "**"), FREE),
        (("max_survivor_fraction", "*"), MAX),
        (("unpinned_sites",), MAX),
    ],
    "tests/coverage_budgets.json": [
        (("recorded_at",), FREE),
        (("reason",), FREE),
        (("pragmas",), MAX),
        (("*_floor",), MIN),
        (("*_ceiling",), MIN),
    ],
    "tests/stress_budgets.json": [
        (("coverage_floor_override", "cites"), FREE),
        (("coverage_floor_override", "floor"), OVERRIDE),
        (("*", "ratio"), MAX),
        (("*", "rss_peak_mb"), MAX),
        (("*", "rss_attrib_mb"), MAX),
        (("*", "traced_peak_mb"), MAX),
    ],
    "tests/typing_budgets.json": [
        (("_comment",), FREE),
        (("recorded_at",), FREE),
        (("census",), FREE),
        (("census", "recorded_at"), FREE),
        (("census", "environment", "**"), FREE),
        (("census", "errors"), MAX),
        (("census", "by_code", "*"), MAX0),
        (("type_ignores",), MAX),
        (("ruler", "**"), FROZEN),
    ],
    ".claude/workflows/policy_budgets.json": [
        (("_band",), MAX),
        (("_*",), FREE),
        (("always_loaded_tokens",), MAX),
        (("corpus_tokens",), MAX),
        (("roles", "*", "cap"), MAX),
        (("roles", "*", "opens"), SUPERSET),
        (("files", "*"), CAPFILE),
    ],
}


def _num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _finite(v) -> bool:
    return _num(v) and math.isfinite(v)


def flatten(obj, prefix: tuple[str, ...] = ()) -> dict[tuple[str, ...], object]:
    """Leaves by key path. A dict recurses (an empty one has no leaves); a
    list or a scalar is one leaf."""
    if isinstance(obj, dict):
        out: dict[tuple[str, ...], object] = {}
        for k, v in obj.items():
            out.update(flatten(v, prefix + (str(k),)))
        return out
    return {prefix: obj}


def _match(pattern: tuple[str, ...], path: tuple[str, ...]) -> bool:
    if pattern and pattern[-1] == "**":
        head = pattern[:-1]
        return len(path) >= len(head) and all(
            fnmatch.fnmatchcase(p, q) for p, q in zip(path, head))
    return len(pattern) == len(path) and all(
        fnmatch.fnmatchcase(p, q) for p, q in zip(path, pattern))


def kind_of(rules, path: tuple[str, ...]) -> str:
    for pattern, kind in rules:
        if _match(pattern, path):
            return kind
    return FROZEN


def _leaf_raise(kind: str, key: str, old, new, have_old: bool, have_new: bool,
                head_has) -> str | None:
    """Why this leaf's change is a raise, or None when it is not one."""
    if kind == FREE or (have_old and have_new and old == new):
        return None
    # `json` reads NaN and Infinity, and the ratchets compare against them as
    # caps: `x <= nan` and `x <= inf` never refuse, so either is no cap at all.
    if kind in (MAX, MAX0, MIN, OVERRIDE, CAPFILE) and have_new and not _finite(new):
        return f"{key}: {old!r} -> {new!r} (not a finite number, so no cap at all)"
    if kind == FROZEN:
        return f"{key}: {old!r} -> {new!r} (a pinned value the gate cannot sign as routine)"
    if kind == SUPERSET:
        if not have_new:
            return f"{key}: removed (a sample that may only grow)"
        if not have_old:
            return None
        if not isinstance(old, list) or not isinstance(new, list):
            return f"{key}: {old!r} -> {new!r} (not a list)"
        lost = [x for x in old if x not in new]
        return f"{key}: dropped {lost!r} (a sample that may only grow)" if lost else None
    if kind == OVERRIDE:
        if not have_new:
            return None
        if not have_old:
            return f"{key}: override added at {new!r} (absent is the strict state)"
    if kind == CAPFILE and not have_new:
        return None if not head_has(key.split(".", 1)[1]) else \
            f"{key}: cap removed while the file it caps is still in the tree"
    if not have_new:
        return f"{key}: removed at {old!r} (a removed cap is no cap)"
    if not have_old:
        if kind == MAX0 and (not _num(new) or new > 0):
            return f"{key}: new at {new!r} (an absent entry here is a cap of zero)"
        return None
    if not (_num(old) and _num(new)):
        return f"{key}: {old!r} -> {new!r} (not a number on both sides)"
    if kind in (MAX, MAX0, CAPFILE):
        return f"{key}: {old!r} -> {new!r} (a cap went up)" if new > old else None
    if kind in (MIN, OVERRIDE):
        return f"{key}: {old!r} -> {new!r} (a floor went down)" if new < old else None
    return f"{key}: unknown kind {kind!r}"


def file_raises(path: str, old_text: str | None, new_text: str | None,
                head_has=lambda p: True) -> list[str]:
    """Every raise in one budget file between the base's text and the head's
    (None: the file is absent at that end)."""
    if old_text == new_text:
        return []
    docs = []
    for side, text in (("base", old_text), ("head", new_text)):
        if text is None:
            docs.append({})
            continue
        try:
            docs.append(json.loads(text))
        except ValueError as e:
            return [f"{path}: does not parse at the {side} ({e}); nothing can be signed as routine"]
    old, new = (flatten(d) for d in docs)
    rules = SCHEMA.get(path, [])
    out = []
    for leaf in sorted(set(old) | set(new)):
        key = ".".join(leaf)
        why = _leaf_raise(kind_of(rules, leaf), key, old.get(leaf), new.get(leaf),
                          leaf in old, leaf in new, head_has)
        if why:
            out.append(f"{path}: {why}")
    if old_text is not None and new_text is None and not out:
        out.append(f"{path}: the file is deleted")
    return out


def approval(reviews: list[dict], head: str) -> tuple[bool, str]:
    """(approved, why): the owner's latest decisive review is an APPROVED one
    submitted on `head`."""
    mine = [r for r in reviews
            if (r.get("user") or {}).get("login") == OWNER_LOGIN
            and (r.get("user") or {}).get("id") == OWNER_ID
            and (r.get("user") or {}).get("type") == OWNER_TYPE]
    decisive = [r for r in mine if r.get("state") in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED")]
    if not decisive:
        return False, f"no decisive review by {OWNER_LOGIN} (id {OWNER_ID}) on this pull request"
    last = decisive[-1]
    if last.get("state") != "APPROVED":
        return False, f"{OWNER_LOGIN}'s latest decisive review is {last.get('state')}"
    if last.get("commit_id") != head:
        return False, (f"{OWNER_LOGIN}'s approval is on {str(last.get('commit_id'))[:12]}, "
                       f"not this head {head[:12]}: an approval covers only the commit it was given on")
    return True, f"{OWNER_LOGIN} approved this head {head[:12]}"


def decide(raises: list[str], reviews_fn, head: str) -> tuple[int, list[str]]:
    lines = [f"RAISE {r}" for r in raises]
    lines.append(f"RESULT budget_raises={len(raises)} count")
    if not raises:
        lines.append("PASS: no budget raise; no owner review is owed")
        return 0, lines
    try:
        reviews = reviews_fn()
    except Exception as e:  # fail closed: a read that failed is not an approval
        lines.append(f"REFUSED: the reviews could not be read ({str(e).splitlines()[0][:160] if str(e) else type(e).__name__}); "
                     "a raise needs the owner's approval, and an unread approval is none")
        return 1, lines
    ok, why = approval(reviews, head)
    lines.append(("PASS: " if ok else "REFUSED: ") + why)
    return (0 if ok else 1), lines


# --- the live run ---------------------------------------------------------

def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def _show(sha: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{sha}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _budget_paths(sha: str) -> set[str]:
    return {p for p in _git("ls-tree", "-r", "--name-only", sha).splitlines()
            if p.endswith(SUFFIX)}


def _reviews(repo: str, pr: str) -> list[dict]:
    out = subprocess.run(
        ["gh", "api", "--paginate", "--slurp", f"repos/{repo}/pulls/{pr}/reviews?per_page=100"],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"gh api exited {out.returncode}: {out.stderr.strip()}")
    pages = json.loads(out.stdout)
    return [r for page in pages for r in page]


def gate(base: str, head: str, pr: str, repo: str) -> int:
    mb = _git("merge-base", base, head).strip()
    head_files = set(_git("ls-tree", "-r", "--name-only", head).splitlines())
    paths = sorted(_budget_paths(mb) | _budget_paths(head))
    raises: list[str] = []
    for p in paths:
        raises += file_raises(p, _show(mb, p), _show(head, p), head_files.__contains__)
    print(f"# merge base {mb[:12]}, head {head[:12]}: {len(paths)} budget file(s): {', '.join(paths)}")
    rc, lines = decide(raises, lambda: _reviews(repo, pr), head)
    print("\n".join(lines))
    return rc


# --- the stale verdict's re-run ----------------------------------------------
#
# Both events write a `budget-raise-gate` check run at the head. When the owner
# approves a raise, the `pull_request_review` run passes, but the
# `pull_request` run that refused before the approval keeps its red on the pull
# request until someone runs `gh run rerun`. `budget-raise-gate-rerun.yml`
# runs `--rerun-stale` on `workflow_run`, from main's copy of this file, and
# asks GitHub to re-run that red run. A re-run re-grades from nothing -- the
# program restored from the base, the reviews read live -- so this writes no
# verdict: a real red re-runs red, and only a head the owner approved turns.

GATE_WORKFLOW = ".github/workflows/budget-raise-gate.yml"
RERUN_CONCLUSIONS = ("failure", "timed_out")


def stale_run(trigger: dict, runs: list[dict]) -> tuple[str, int | None, str]:
    """(action, run id, why): "rerun", "wait" or "none" for one completed run.

    `trigger` is the completed run `workflow_run` names; `runs` the gate's
    `pull_request` runs at its head. Only the NEWEST of those matters -- it is
    the one the pull request shows -- and only when the trigger is a passing
    review run of this very workflow. A trigger that is itself a
    `pull_request` run is refused, which is also what stops a re-run's own
    completion from starting another.
    """
    head = str(trigger.get("head_sha") or "")
    if trigger.get("path") != GATE_WORKFLOW:
        return "none", None, f"the completed run is {trigger.get('path')!r}, not {GATE_WORKFLOW}"
    if trigger.get("event") != "pull_request_review":
        return "none", None, f"the completed run is a {trigger.get('event')!r} run; only a review run re-grades"
    if trigger.get("conclusion") != "success":
        return "none", None, f"the review run concluded {trigger.get('conclusion')!r}; the red stands"
    same = [r for r in runs
            if r.get("workflow_id") == trigger.get("workflow_id")
            and r.get("event") == "pull_request" and r.get("head_sha") == head
            and r.get("id") != trigger.get("id")]
    if not same:
        return "none", None, f"no pull_request run of the gate at {head[:12]}"
    newest = max(same, key=lambda r: (str(r.get("created_at") or ""), r.get("id") or 0))
    if newest.get("status") != "completed":
        return "wait", newest.get("id"), f"run {newest.get('id')} at {head[:12]} is {newest.get('status')}"
    if newest.get("conclusion") in RERUN_CONCLUSIONS:
        return "rerun", newest.get("id"), f"run {newest.get('id')} at {head[:12]} concluded {newest.get('conclusion')}"
    return "none", None, f"run {newest.get('id')} at {head[:12]} concluded {newest.get('conclusion')}; nothing is stale"


def _gh_json(*args: str):
    out = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"gh api {args[-1]} exited {out.returncode}: {out.stderr.strip()[:200]}")
    return json.loads(out.stdout) if out.stdout.strip() else {}


def rerun_stale(run_id: str, repo: str, api=_gh_json, sleep=None, polls: int = 30) -> int:
    """Re-run the gate's stale red `pull_request` run after a passing review run.

    Exit 0 when a re-run was requested or nothing is stale; 1 when the API
    could not be read or refused, so the job is red and the stale verdict is
    named rather than silently left. It is never a required context.
    """
    import time
    sleep = sleep or time.sleep
    try:
        trigger = api(f"repos/{repo}/actions/runs/{int(run_id)}")
        for _ in range(polls):
            runs = api(f"repos/{repo}/actions/workflows/{int(trigger.get('workflow_id') or 0)}/runs"
                       f"?event=pull_request&head_sha={trigger.get('head_sha')}&per_page=100")
            action, rid, why = stale_run(trigger, runs.get("workflow_runs", []))
            if action != "wait":
                break
            print(f"WAIT: {why}")
            sleep(20)
        print(f"{action.upper()}: {why}")
        if action == "rerun":
            api("-X", "POST", f"repos/{repo}/actions/runs/{int(rid)}/rerun")
            print(f"RESULT rerun_requested={rid}")
        elif action == "wait":
            print("REFUSED: the pull_request run did not finish in time; re-run it by hand")
            return 1
        return 0
    except (RuntimeError, ValueError, TypeError) as e:
        print(f"REFUSED: {str(e).splitlines()[0][:200] if str(e) else type(e).__name__}")
        return 1


# --- the self-test ----------------------------------------------------------

def _j(d) -> str:
    return json.dumps(d, indent=1)


def self_test() -> int:
    fails = 0
    n = 0

    def check(name: str, got, want) -> None:
        nonlocal fails, n
        n += 1
        ok = got == want
        fails += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f": got {got!r}, want {want!r}"))

    def raised(path, old, new, head_has=lambda p: True) -> bool:
        return bool(file_raises(path, None if old is None else _j(old),
                                None if new is None else _j(new), head_has))

    # One raise and one routine edit per budget file, each against a null
    # control (the same document on both sides).
    S = "tests/structure_budgets.json"
    s0 = {"coordinator_loc": 9062, "cut_views": 110, "recorded_at": "aaa"}
    check("structure: null control", raised(S, s0, s0), False)
    check("structure: a metric re-recorded down is routine",
          raised(S, s0, {**s0, "coordinator_loc": 9000, "recorded_at": "bbb"}), False)
    check("structure: a metric up is a raise", raised(S, s0, {**s0, "cut_views": 111}), True)
    check("structure: a metric deleted is a raise",
          raised(S, s0, {"coordinator_loc": 9062, "recorded_at": "aaa"}), True)
    check("structure: a new metric is not a raise", raised(S, s0, {**s0, "new_metric": 3}), False)

    M = "tests/mutation_budgets.json"
    m0 = {"_comment": "x", "max_survivor_fraction": {"changed": 0.2, "full": 0.3},
          "unpinned_sites": 3726, "last_measured": {"full": {"survivors": 12}},
          "survivor_triage": {"a.py:1 CONST": {"verdict": "gap"}},
          "killed_by": {"a.py:2 BOOLOP": {"killed_by": "tests/x.py"}}, "reason": "r"}
    check("mutation: null control", raised(M, m0, m0), False)
    check("mutation: ledger rows re-keyed after a line shift are routine",
          raised(M, m0, {**m0, "survivor_triage": {"a.py:5 CONST": {"verdict": "gap"}},
                         "killed_by": {"a.py:6 BOOLOP": {"killed_by": "tests/x.py"},
                                       "b.py:1 GUARD_OFF": {"killed_by": "tests/y.py"}},
                         "unpinned_sites": 3725, "last_measured": {"full": {"survivors": 30}}}), False)
    check("mutation: the unpinned count up is a raise", raised(M, m0, {**m0, "unpinned_sites": 3727}), True)
    check("mutation: a survivor fraction up is a raise",
          raised(M, m0, {**m0, "max_survivor_fraction": {"changed": 0.25, "full": 0.3}}), True)
    check("mutation: the committed count removed is a raise",
          raised(M, m0, {k: v for k, v in m0.items() if k != "unpinned_sites"}), True)

    C = "tests/coverage_budgets.json"
    c0 = {"package_percent_floor": 96.0, "package_percent_ceiling": 96.0, "pragmas": 12,
          "module_percent_floor": 95.0, "recorded_at": "t", "reason": "r"}
    check("coverage: null control", raised(C, c0, c0), False)
    check("coverage: a floor up, a pragma paid off, is routine",
          raised(C, c0, {**c0, "module_percent_floor": 95.5, "pragmas": 11, "reason": "s"}), False)
    check("coverage: a floor down is a raise", raised(C, c0, {**c0, "package_percent_floor": 95.9}), True)
    check("coverage: the ceiling down is a raise", raised(C, c0, {**c0, "package_percent_ceiling": 95.0}), True)
    check("coverage: a pragma added is a raise", raised(C, c0, {**c0, "pragmas": 13}), True)

    T = "tests/stress_budgets.json"
    t0 = {"coverage_floor_override": {"cites": "ruling", "floor": 38},
          "flat/1z/dhw": {"ratio": 47.85, "rss_attrib_mb": 8.5, "rss_peak_mb": 84.3, "traced_peak_mb": 2.04}}
    check("stress: null control", raised(T, t0, t0), False)
    check("stress: a scenario re-recorded cheaper is routine",
          raised(T, t0, {**t0, "flat/1z/dhw": {"ratio": 40.0, "rss_attrib_mb": 8.0,
                                               "rss_peak_mb": 80.0, "traced_peak_mb": 2.0}}), False)
    check("stress: a ratio up is a raise",
          raised(T, t0, {**t0, "flat/1z/dhw": {**t0["flat/1z/dhw"], "ratio": 48.0}}), True)
    check("stress: a scenario dropped is a raise",
          raised(T, t0, {"coverage_floor_override": t0["coverage_floor_override"]}), True)
    check("stress: the override lowered is a raise",
          raised(T, t0, {**t0, "coverage_floor_override": {"cites": "ruling", "floor": 30}}), True)
    check("stress: the override withdrawn is routine (the literal is stricter)",
          raised(T, t0, {k: v for k, v in t0.items() if k != "coverage_floor_override"}), False)
    check("stress: an override granted is a raise",
          raised(T, {k: v for k, v in t0.items() if k != "coverage_floor_override"}, t0), True)

    Y = "tests/typing_budgets.json"
    y0 = {"_comment": ["x"], "ruler": {"mypy": "2.3.1", "third_party": ["numpy"]}, "type_ignores": 0,
          "census": {"errors": 0, "by_code": {}, "environment": {"python": "3.13.15"}, "recorded_at": "a"},
          "recorded_at": "b"}
    check("typing: null control", raised(Y, y0, y0), False)
    check("typing: a re-measured environment and a new record sha are routine",
          raised(Y, y0, {**y0, "recorded_at": "c",
                         "census": {**y0["census"], "environment": {"python": "3.13.16"}, "recorded_at": "d"}}), False)
    check("typing: a type-ignore added is a raise", raised(Y, y0, {**y0, "type_ignores": 1}), True)
    check("typing: an error code appearing is a raise",
          raised(Y, y0, {**y0, "census": {**y0["census"], "by_code": {"arg-type": 1}}}), True)
    check("typing: the ruler's toolchain moved is a raise",
          raised(Y, y0, {**y0, "ruler": {"mypy": "2.4.0", "third_party": ["numpy"]}}), True)

    P = ".claude/workflows/policy_budgets.json"
    p0 = {"_comment": "c", "always_loaded_tokens": 3349, "_band": 500, "corpus_tokens": 55433,
          "roles": {"fixer": {"opens": ["a", "b"], "cap": 5852}},
          "files": {"CLAUDE.md": 211, "old.md": 10}}
    check("policy: null control", raised(P, p0, p0), False)
    check("policy: a cap down, a deleted file's cap dropped, a sample widened are routine",
          raised(P, p0, {**p0, "corpus_tokens": 55000, "files": {"CLAUDE.md": 211},
                         "roles": {"fixer": {"opens": ["a", "b", "c"], "cap": 5852}}},
                 head_has=lambda f: f != "old.md"), False)
    check("policy: a per-file cap up is a raise",
          raised(P, p0, {**p0, "files": {"CLAUDE.md": 212, "old.md": 10}}), True)
    check("policy: the band widened is a raise", raised(P, p0, {**p0, "_band": 600}), True)
    check("policy: a role's sample narrowed is a raise",
          raised(P, p0, {**p0, "roles": {"fixer": {"opens": ["a"], "cap": 5852}}}), True)
    check("policy: a cap dropped while its file stays is a raise",
          raised(P, p0, {**p0, "files": {"CLAUDE.md": 211}}), True)

    # A non-finite head value is no cap at all: each ratchet compares against
    # it and passes (`ok cut_views 110 <= nan`).
    for label, bad in (("NaN", float("nan")), ("+inf", float("inf")), ("-inf", float("-inf")),
                       ("a string", "110"), ("null", None), ("a bool", True)):
        check(f"structure: a metric set to {label} is a raise", raised(S, s0, {**s0, "cut_views": bad}), True)
        check(f"coverage: a floor set to {label} is a raise",
              raised(C, c0, {**c0, "package_percent_floor": bad}), True)
    check("structure: a new metric at NaN is a raise", raised(S, s0, {**s0, "new_metric": float("nan")}), True)
    check("structure: a new metric as a string is a raise", raised(S, s0, {**s0, "new_metric": "5"}), True)
    check("mutation: the survivor fraction at +inf is a raise",
          raised(M, m0, {**m0, "max_survivor_fraction": {"changed": float("inf"), "full": 0.3}}), True)
    check("stress: a ratio at NaN is a raise",
          raised(T, t0, {**t0, "flat/1z/dhw": {**t0["flat/1z/dhw"], "ratio": float("nan")}}), True)
    check("stress: the override floor at -inf is a raise",
          raised(T, t0, {**t0, "coverage_floor_override": {"cites": "ruling", "floor": float("-inf")}}), True)
    check("typing: a new error code at +inf is a raise",
          raised(Y, y0, {**y0, "census": {**y0["census"], "by_code": {"x": float("inf")}}}), True)
    check("policy: a per-file cap at NaN is a raise",
          raised(P, p0, {**p0, "files": {"CLAUDE.md": float("nan"), "old.md": 10}}), True)
    check("a NaN base lowered to a number is not a raise (null control)",
          raised(S, {**s0, "cut_views": float("nan")}, s0), False)

    U = "tests/new_budgets.json"
    check("unknown file: a change with no schema is a raise", raised(U, {"x": 1}, {"x": 0}), True)
    check("unknown file: added is a raise", raised(U, None, {"x": 1}), True)
    check("a budget file deleted is a raise", raised(S, s0, None), True)
    check("a head that does not parse is a raise", bool(file_raises(S, _j(s0), "{")), True)

    # The owner's approval.
    H, OLD = "h" * 40, "o" * 40
    own = {"login": OWNER_LOGIN, "id": OWNER_ID, "type": OWNER_TYPE}
    app = {"login": "hpo-approver[bot]", "id": 330097732, "type": "Bot"}

    def rv(user, state, sha=H):
        return {"user": user, "state": state, "commit_id": sha}

    def rc(raises, reviews):
        def fn():
            if isinstance(reviews, Exception):
                raise reviews
            return reviews
        try:
            return decide(raises, fn, H)[0]
        except Exception as e:  # an escape is a verdict too, and never 0 or 1
            return f"raised {type(e).__name__}"

    R = ["x: 1 -> 2 (a cap went up)"]
    check("no raise: passes with no review at all (null control)", rc([], []), 0)
    check("no raise: never reads the API", rc([], RuntimeError("unreachable")), 0)
    check("an approved raise passes", rc(R, [rv(own, "APPROVED")]), 0)
    check("an unapproved raise fails", rc(R, []), 1)
    check("a raise approved only by the approver App fails", rc(R, [rv(app, "APPROVED")]), 1)
    check("a stale approval on an older SHA fails", rc(R, [rv(own, "APPROVED", OLD)]), 1)
    check("an approval then changes requested fails",
          rc(R, [rv(own, "APPROVED"), rv(own, "CHANGES_REQUESTED")]), 1)
    check("an approval then dismissed fails", rc(R, [rv(own, "APPROVED"), rv(own, "DISMISSED")]), 1)
    check("an approval then a comment still passes", rc(R, [rv(own, "APPROVED"), rv(own, "COMMENTED")]), 0)
    check("a stale approval then a fresh one passes",
          rc(R, [rv(own, "APPROVED", OLD), rv(own, "APPROVED")]), 0)
    check("an account named tvofi with another id fails",
          rc(R, [rv({**own, "id": OWNER_ID + 1}, "APPROVED")]), 1)
    check("the owner's id under another login fails (a rename is re-pinned, not followed)",
          rc(R, [rv({**own, "login": "tvofi-renamed"}, "APPROVED")]), 1)
    check("the owner's id and login on a non-User account fails",
          rc(R, [rv({**own, "type": "Bot"}, "APPROVED")]), 1)
    check("a reviews read that fails, fails closed", rc(R, RuntimeError("HTTP 502")), 1)

    # Every tracked budget file, as it stands: the schema must know it, a copy
    # must not raise against itself, every cap moved the strict way must be
    # routine, and every cap moved the loose way must be a raise. A key the
    # schema no longer matches falls to `frozen`, which the strict move reds.
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        root = subprocess.run(["git", "-C", here, "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True, check=True).stdout.strip()
        tracked = [p for p in subprocess.run(["git", "-C", root, "ls-files"], capture_output=True,
                                             text=True, check=True).stdout.splitlines() if p.endswith(SUFFIX)]
    except (OSError, subprocess.CalledProcessError) as e:
        root, tracked = "", []
        print(f"  FAIL the tracked budget files could not be listed ({e})")
        fails += 1
    check("the tree has budget files to read", len(tracked) >= len(SCHEMA), True)
    for p in tracked:
        text = open(os.path.join(root, p), encoding="utf-8").read()
        doc = json.loads(text)
        leaves = flatten(doc)
        rules = SCHEMA.get(p)
        check(f"{p}: has a schema", rules is not None, True)
        rules = rules or []
        caps = {k: v for k, v in leaves.items()
                if kind_of(rules, k) in (MAX, MAX0, MIN, CAPFILE) and _num(v)}
        check(f"{p}: carries at least one cap the gate reads", len(caps) > 0, True)
        check(f"{p}: null control, the file against itself", file_raises(p, text, text), [])

        def moved(sign: int) -> dict:
            out = json.loads(text)
            for k, v in caps.items():
                d = out
                for seg in k[:-1]:
                    d = d[seg]
                up = kind_of(rules, k) in (MIN,)
                step = 1 if isinstance(v, int) else 0.5
                d[k[-1]] = v + (step if up else -step) * sign
            return out
        strict = file_raises(p, text, _j(moved(1)))
        check(f"{p}: every cap moved the strict way is routine ({len(caps)} cap(s))", strict, [])
        loose = file_raises(p, text, _j(moved(-1)))
        check(f"{p}: every cap moved the loose way is a raise", len(loose), len(caps))

    for name, got, want in _end_to_end():
        check(name, got, want)

    # The stale verdict's re-run: every arm but the first leaves the red alone.
    T0 = {"id": 9, "path": GATE_WORKFLOW, "event": "pull_request_review", "conclusion": "success",
          "head_sha": H, "workflow_id": 5}

    def pr_run(i, conclusion="failure", status="completed", sha=H, wf=5, event="pull_request", at="2026-09-25T0"):
        return {"id": i, "event": event, "status": status, "conclusion": conclusion, "head_sha": sha,
                "workflow_id": wf, "created_at": f"{at}{i}"}

    check("rerun: a passing review run re-runs the red pull_request run at its head",
          stale_run(T0, [pr_run(3)])[:2], ("rerun", 3))
    check("rerun: only the newest pull_request run counts",
          stale_run(T0, [pr_run(3), pr_run(4, "success")])[:2], ("none", None))
    check("rerun: ... and it is the one re-run when it is red",
          stale_run(T0, [pr_run(3, "success"), pr_run(4)])[:2], ("rerun", 4))
    check("rerun: a failing review run re-runs nothing (the red stands)",
          stale_run({**T0, "conclusion": "failure"}, [pr_run(3)])[:2], ("none", None))
    check("rerun: a pull_request trigger re-runs nothing (no loop on the re-run's own completion)",
          stale_run({**T0, "event": "pull_request"}, [pr_run(3)])[:2], ("none", None))
    check("rerun: another workflow's run is not the gate",
          stale_run({**T0, "path": ".github/workflows/tests.yml"}, [pr_run(3)])[:2], ("none", None))
    check("rerun: a red run at another head is left alone",
          stale_run(T0, [pr_run(3, sha=OLD)])[:2], ("none", None))
    check("rerun: a red run of another workflow is left alone",
          stale_run(T0, [pr_run(3, wf=6)])[:2], ("none", None))
    check("rerun: a cancelled run is left alone", stale_run(T0, [pr_run(3, "cancelled")])[:2], ("none", None))
    check("rerun: a run still going is waited for",
          stale_run(T0, [pr_run(3, None, "in_progress")])[:2], ("wait", 3))

    def fake(pages, fail_post=False):
        calls = []

        def api(*a):
            calls.append(a)
            if a[0] == "-X":
                if fail_post:
                    raise RuntimeError("HTTP 403")
                return {}
            if "/workflows/" in a[-1]:
                return {"workflow_runs": pages.pop(0) if len(pages) > 1 else pages[0]}
            return T0
        return api, calls

    api, calls = fake([[pr_run(3, None, "in_progress")], [pr_run(3)]])
    check("rerun: end to end, waits for the run and then re-runs it",
          (rerun_stale("9", "o/r", api, sleep=lambda s: None),
           [c for c in calls if c[0] == "-X"]), (0, [("-X", "POST", "repos/o/r/actions/runs/3/rerun")]))
    api, calls = fake([[pr_run(3, None, "in_progress")]])
    check("rerun: a run that never finishes is a red job, not a silent pass",
          rerun_stale("9", "o/r", api, sleep=lambda s: None, polls=3), 1)
    api, calls = fake([[pr_run(3)]], fail_post=True)
    check("rerun: a refused re-run request is a red job", rerun_stale("9", "o/r", api), 1)
    api, calls = fake([[pr_run(3, "success")]])
    check("rerun: nothing stale posts nothing (null control)",
          (rerun_stale("9", "o/r", api), [c for c in calls if c[0] == "-X"]), (0, []))

    print(f"budget_raise_gate self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


# --- the entry point, end to end ---------------------------------------------
#
# The checks above drive the pure functions. These run this file as CI runs it
# -- `python3 -I <file> --base --head --pr`, its exit status read -- over a
# throwaway repository with a fork point, a base that moved after it and a
# head, and a stub `gh` first on PATH that serves a canned reviews listing and
# logs every call. So `gate()`, `main()` and the `sys.exit` line are graded by
# the status the required context would report.

_STUB_GH = """#!/usr/bin/env python3
import json, os, sys
d = os.environ["BRG_STUB"]
with open(os.path.join(d, "calls"), "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\\n")
spec = json.load(open(os.path.join(d, "reviews.json")))
sys.stdout.write(json.dumps(spec["pages"]))
sys.exit(spec["rc"])
"""


def _end_to_end() -> list[tuple[str, object, object]]:
    out: list[tuple[str, object, object]] = []
    me = os.path.abspath(__file__)
    root = tempfile.mkdtemp(prefix="brg-e2e-")
    try:
        repo, stub = os.path.join(root, "repo"), os.path.join(root, "stub")
        os.makedirs(repo)
        os.makedirs(stub)
        with open(os.path.join(stub, "gh"), "w") as f:
            f.write(_STUB_GH)
        os.chmod(os.path.join(stub, "gh"), 0o700)
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GH_", "GITHUB_"))}
        env.update(PATH=stub + os.pathsep + os.environ.get("PATH", ""), BRG_STUB=stub,
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")

        def git(*a: str) -> str:
            return subprocess.run(["git", *a], cwd=repo, env=env, capture_output=True,
                                  text=True, check=True).stdout.strip()

        def write(files: dict) -> None:
            for rel, doc in files.items():
                full = os.path.join(repo, rel)
                if doc is None:
                    if os.path.exists(full):
                        os.remove(full)
                    continue
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "w") as f:
                    f.write(doc if isinstance(doc, str) else _j(doc))

        def commit(files: dict, msg: str) -> str:
            write(files)
            git("add", "-A")
            git("commit", "-q", "--allow-empty", "-m", msg)
            return git("rev-parse", "HEAD")

        S, P = "tests/structure_budgets.json", ".claude/workflows/policy_budgets.json"
        s0 = {"coordinator_loc": 9062, "cut_views": 110, "recorded_at": "a"}
        p0 = {"always_loaded_tokens": 3349, "files": {"A.md": 10, "gone.md": 5}}
        git("init", "-q", "-b", "main")
        fork = commit({S: s0, P: p0, "A.md": "a\n", "gone.md": "g\n",
                       "tests/zz_budgets.json": {"x": 1}}, "fork")
        # main moves on after the fork and TIGHTENS a cap: the head, which never
        # touched it, is above the base tip but not above the fork point.
        base = commit({S: {**s0, "coordinator_loc": 9000}}, "main tightens")

        def branch(name: str, files: dict) -> str:
            git("checkout", "-q", "-B", name, fork)
            head = commit(files, name)
            git("checkout", "-q", "main")
            return head

        routine = branch("routine", {S: {**s0, "cut_views": 100, "recorded_at": "b"},
                                     P: {**p0, "files": {"A.md": 10}}, "gone.md": None})
        raise_ = branch("raise", {S: {**s0, "cut_views": 111}})
        nan = branch("nan", {S: '{"coordinator_loc": 9062, "cut_views": NaN, "recorded_at": "a"}'})
        added = branch("added", {"tests/new_budgets.json": {"y": 1}})
        deleted = branch("deleted", {"tests/zz_budgets.json": None})
        kept = branch("kept-file", {P: {**p0, "files": {"A.md": 10}}})
        own = {"login": OWNER_LOGIN, "id": OWNER_ID, "type": OWNER_TYPE}

        def run(head: str, pages=None, rc=0, argv=None, repo_env=None):
            with open(os.path.join(stub, "reviews.json"), "w") as f:
                json.dump({"pages": pages if pages is not None else [[]], "rc": rc}, f)
            open(os.path.join(stub, "calls"), "w").close()
            e = dict(env)
            if repo_env:
                e["GITHUB_REPOSITORY"] = repo_env
            r = subprocess.run([sys.executable, "-I", me, *(argv or ["--base", base, "--head", head, "--pr", "7"])],
                               cwd=repo, env=e, capture_output=True, text=True)
            calls = [json.loads(x) for x in open(os.path.join(stub, "calls")).read().splitlines()]
            return r.returncode, r.stdout + r.stderr, calls

        def approved(sha: str) -> dict:
            return {"user": own, "state": "APPROVED", "commit_id": sha}

        rc_, text, calls = run(routine)
        out.append(("e2e: a routine edit exits 0 (null control)", rc_, 0))
        out.append(("e2e: ... reads no reviews", calls, []))
        out.append(("e2e: ... compares at the fork point, not the moved base",
                    "budget_raises=0" in text and f"merge base {fork[:12]}" in text, True))
        out.append(("e2e: ... and reports every budget file it read",
                    "3 budget file(s)" in text, True))
        rc_, text, calls = run(raise_)
        out.append(("e2e: an unapproved raise exits 1", rc_, 1))
        out.append(("e2e: ... names the raise", "cut_views: 110 -> 111" in text, True))
        out.append(("e2e: ... after asking for this PR's reviews, every page",
                    calls, [["api", "--paginate", "--slurp",
                             "repos/tvofi/heatpump_optimizer/pulls/7/reviews?per_page=100"]]))
        rc_, text, calls = run(raise_, pages=[[approved(fork)], [approved(raise_)]])
        out.append(("e2e: a raise approved on the head, on the second page, exits 0", rc_, 0))
        rc_, _, _ = run(raise_, pages=[[approved(raise_)], [approved(fork)]])
        out.append(("e2e: a raise whose latest approval is stale exits 1", rc_, 1))
        rc_, _, _ = run(raise_, pages=[[approved(raise_)]], rc=1)
        out.append(("e2e: a reviews read that exits non-zero exits 1, whatever it printed", rc_, 1))
        rc_, text, _ = run(nan, pages=[[]])
        out.append(("e2e: a cap edited to NaN exits 1", rc_, 1))
        rc_, text, _ = run(added)
        out.append(("e2e: an added budget file with no schema exits 1",
                    (rc_, "tests/new_budgets.json: y: None -> 1" in text), (1, True)))
        rc_, text, _ = run(deleted)
        out.append(("e2e: a deleted budget file exits 1",
                    (rc_, "tests/zz_budgets.json: x: 1 -> None" in text), (1, True)))
        rc_, text, _ = run(kept)
        out.append(("e2e: a per-file cap dropped while the file stays exits 1",
                    (rc_, "files.gone.md" in text), (1, True)))
        rc_, _, calls = run(raise_, argv=["--base", base, "--head", raise_, "--pr", "9", "--repo", "o/r"])
        out.append(("e2e: --repo is the repository asked",
                    [c[-1] for c in calls], ["repos/o/r/pulls/9/reviews?per_page=100"]))
        rc_, _, calls = run(raise_, repo_env="e/f")
        out.append(("e2e: without --repo, GITHUB_REPOSITORY is",
                    [c[-1] for c in calls], ["repos/e/f/pulls/7/reviews?per_page=100"]))
        for label, argv in (("no --pr", ["--base", base, "--head", raise_]),
                            ("an unknown flag", ["--base", base, "--head", raise_, "--pr", "7", "--x", "1"]),
                            ("a trailing flag with no value", ["--base", base, "--head", raise_, "--pr", "7", "--repo"])):
            rc_, _, calls = run(raise_, argv=argv)
            out.append((f"e2e: {label} exits 2 and asks nothing", (rc_, calls), (2, [])))
        rc_, _, _ = run(raise_, argv=["--base", "no-such-ref", "--head", raise_, "--pr", "7"])
        out.append(("e2e: an unresolvable base fails closed", rc_ != 0, True))
    except (OSError, subprocess.CalledProcessError) as e:
        out.append((f"e2e: the throwaway repository could be built ({e})", False, True))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return out


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if argv[:1] == ["--rerun-stale"]:
        rest = dict(zip(argv[2::2], argv[3::2]))
        if len(argv) < 2 or len(argv) % 2 or set(rest) - {"--repo"}:
            print("usage: budget_raise_gate.py --rerun-stale RUN_ID [--repo O/R]", file=sys.stderr)
            return 2
        return rerun_stale(argv[1], rest.get("--repo") or os.environ.get("GITHUB_REPOSITORY") or DEFAULT_REPO)
    args = dict(zip(argv[::2], argv[1::2]))
    if len(argv) % 2 or not {"--base", "--head", "--pr"} <= set(args) or set(args) - {"--base", "--head", "--pr", "--repo"}:
        print(__doc__.strip().splitlines()[-2].strip(), file=sys.stderr)
        return 2
    return gate(args["--base"], args["--head"], args["--pr"],
                args.get("--repo") or os.environ.get("GITHUB_REPOSITORY") or DEFAULT_REPO)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

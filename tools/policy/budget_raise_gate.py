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
account type pinned below, and does not say in its own body that an agent gave
it (AGENT_DECLARED below) -- or, if it does, cites one mandate the owner
recorded on #201 that covers budget raises and was in force when the review
was submitted (MANDATE_GRAMMAR, mandate_check). Anything else, a failed API
read included, is exit 1.

WHAT IT DOES NOT SEE. A ledger disposition (`survivor_triage`, `killed_by`)
is a per-site record, not a cap, and is `free` here: an `equivalent` verdict
the fix reviewer accepted is routine work, not a raise. And a grader that
stops reading its cap file is not a budget edit at all -- that is the
enforcement surface's concern (`codeowners_gap.py`), not this check's.

HOW IT IS RUN. `.github/workflows/budget-raise-gate.yml` restores this file
from the base commit before running it under `python3 -I`, so a pull request
cannot edit the gate that grades it; the workflow re-runs it on
`pull_request_review`, so an approval turns it green without a push.

    python3 -I tools/policy/budget_raise_gate.py --base SHA --head SHA --pr N [--repo O/R]
    python3 tools/policy/budget_raise_gate.py --self-test
    python3 -I tools/policy/budget_raise_gate.py --rerun-stale RUN_ID [--repo O/R]
"""
from __future__ import annotations

import datetime
import fnmatch
import json
import math
import os
import re
import shutil
import tempfile
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
from layout import canon, locate  # noqa: E402  the reorganisation's move map (R9-RO-2)

# The code owner, pinned three ways: a login alone can be renamed away and
# re-registered, an id alone says nothing about which account a reader meant.
# `gh api users/tvofi --jq '{login,id,type}'`, 2026-09-24.
OWNER_LOGIN = "tvofi"
OWNER_ID = 70032254
OWNER_TYPE = "User"
# D11-s1-04 (card C17, tvofi's refusal rather than a delegated identity): a
# seat driving the owner's own credentials posts a review GitHub records as the
# owner's, so login, id and type cannot separate the two -- only the body can,
# where the seat declares itself ("The orchestrator gives it under tvofi's
# explicit mandate") and where every agent-posted GitHub review carries the
# Claude Code footer. Such a review is not the owner's and is dropped before the
# decisive one is chosen, so it neither approves nor supersedes. The residual,
# stated rather than hidden: an agent that declares nothing is not separable
# from the owner on GitHub's record, which no in-tree check can change.
AGENT_DECLARED = re.compile(
    r"orchestrator|\bseats?\b|\bmandate\b|\b(?:on|under) tvofi's|on behalf of|delegat"
    r"|claude\.ai/code|generated (?:by|with) \[?claude", re.I)
# The owner's recorded mandate (tvofi, 2026-10-02, amending the refusal above):
# an agent may approve as tvofi, openly, while a mandate tvofi wrote is in
# force. The record is a comment on the tracking issue by the pinned owner
# account, read from the API at run time; no copy in the tree is trusted. Its
# first line is MANDATE_GRAMMAR, and a comment edited at any time grants
# nothing (anyone with write access can edit it and its author stays tvofi).
# Any later comment by the same account that names the id beside any form of
# "revoke" voids it (MANDATE_REVOKED): the grant is strict and the kill switch
# loose, because over-revoking fails safe. An agent's review names the id, as
# "mandate <id>" or as the comment's `issuecomment-<id>` URL, and that word
# keeps it declared an agent's: authorship is never hidden to pass.
DEFAULT_REPO = "tvofi/heatpump_optimizer"
MANDATE_ISSUE = 201
MANDATE_ISSUE_URL = f"/repos/{DEFAULT_REPO}/issues/{MANDATE_ISSUE}"
MANDATE_GRAMMAR = re.compile(
    rf"MANDATE: agents may approve as {OWNER_LOGIN}, scope (code-owned|budget-raise|all), "
    r"from (\S+) until (\S+)")
MANDATE_REVOKED = re.compile(r"revok", re.I)
MANDATE_CITE = re.compile(r"\bmandate(?: comment)?:? #?(\d{6,})\b|issuecomment-(\d{6,})\b", re.I)
MANDATE_COVERS_RAISE = ("budget-raise", "all")
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
    "dev/governance/config/policy_budgets.json": [
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


def _schema(path: str) -> list:
    """The rules for `path`. The key is the path the file has; `gate` spells a
    moved file by its old path (`canon`) before it asks, and `locate` is the
    other direction."""
    if path in SCHEMA:
        return SCHEMA[path]
    for alt in (locate(path), canon(path)):
        if alt in SCHEMA:
            return SCHEMA[alt]
    return []


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
    rules = _schema(path)
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


def _is_owner(user) -> bool:
    user = user or {}
    return (user.get("login") == OWNER_LOGIN and user.get("id") == OWNER_ID
            and user.get("type") == OWNER_TYPE)


def _when(text):
    """An ISO 8601 instant with a zone, or None: a time with no zone is no time."""
    try:
        t = datetime.datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo is not None else None


def mandate_check(review: dict, cid: int, comment, thread: list[dict]) -> tuple[bool, str]:
    """(in force, why) for the mandate comment `cid` that `review` cites.
    `comment` is that comment as the API returns it (None: it does not exist);
    `thread` is the tracking issue's comments, where a revocation would be."""
    name = f"mandate {cid}"
    if comment is None:
        return False, f"{name} is not a comment that exists"
    if not str(comment.get("issue_url") or "").endswith(MANDATE_ISSUE_URL):
        return False, f"{name} is not a comment on {DEFAULT_REPO}#{MANDATE_ISSUE}"
    if not _is_owner(comment.get("user")):
        return False, (f"{name} was not written by {OWNER_LOGIN} (id {OWNER_ID}), "
                       "and only the owner grants a mandate")
    m = MANDATE_GRAMMAR.fullmatch(((comment.get("body") or "").strip().splitlines() or [""])[0].strip())
    if not m:
        return False, f"{name}'s first line is not the mandate grammar"
    scope, start, until = m.group(1), _when(m.group(2)), m.group(3)
    end = None if until == "programme-end" else _when(until)
    created, updated = _when(comment.get("created_at")), _when(comment.get("updated_at"))
    if start is None or created is None or updated is None or (end is None and until != "programme-end"):
        return False, f"{name} carries a time that is not an ISO 8601 instant with a zone"
    if scope not in MANDATE_COVERS_RAISE:
        return False, f"{name} has scope {scope}, which does not cover budget raises"
    at = _when(review.get("submitted_at"))
    if at is None:
        return False, f"the review citing {name} carries no submission time"
    if at < max(start, created):
        return False, f"{name} was not yet in force at {review.get('submitted_at')}"
    if end is not None and at >= end:
        return False, f"{name} expired at {until}, before the review at {review.get('submitted_at')}"
    if updated != created:
        return False, f"{name} was edited, so the text tvofi gave it under is unknown"
    for c in thread:
        body = c.get("body") or ""
        if (_is_owner(c.get("user")) and MANDATE_REVOKED.search(body)
                and re.search(rf"(?<!\d){cid}(?!\d)", body)):
            return False, f"{name} was revoked by {OWNER_LOGIN}'s comment {c.get('id')}"
    return True, f"{name} (scope {scope}, from {m.group(2)} until {until})"


def approval(reviews: list[dict], head: str, mandate_fn=None) -> tuple[bool, str]:
    """(approved, why): the owner's latest decisive review is an APPROVED one
    submitted on `head`. A review under the owner's account whose body says an
    agent gave it is not the owner's (AGENT_DECLARED), unless it is an approval
    that cites one mandate `mandate_fn(id)` -> (comment, thread) shows in force
    (mandate_check). An agent's other reviews decide nothing, as before."""
    own = [r for r in reviews if _is_owner(r.get("user"))]
    decisive, under, notes = [], {}, []
    for r in own:
        if not AGENT_DECLARED.search(r.get("body") or ""):
            if r.get("state") in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
                decisive.append(r)
            continue
        cited = {int(a or b) for a, b in MANDATE_CITE.findall(r.get("body") or "")}
        if r.get("state") != "APPROVED" or not cited:
            continue
        if len(cited) > 1:
            notes.append(f"review {r.get('id')} cites {len(cited)} mandates, and one decides")
            continue
        cid = cited.pop()
        ok, why = (False, "no mandate could be read") if mandate_fn is None else mandate_check(r, cid, *mandate_fn(cid))
        if ok:
            decisive.append(r)
            under[id(r)] = why
        else:
            notes.append(f"review {r.get('id')}: {why}")
    tail = "".join(f"; {n}" for n in notes)
    if not decisive:
        agent = len(own) - len([r for r in own if not AGENT_DECLARED.search(r.get("body") or "")])
        return False, (f"no decisive review by {OWNER_LOGIN} (id {OWNER_ID}) on this pull request"
                       + (f"; {agent} under that account declare an agent gave them, and an "
                          "agent-driven approval is the owner's only under a mandate in force" if agent else "")
                       + tail)
    last = decisive[-1]
    theirs = [r for r in decisive if id(r) not in under]
    if under and theirs and theirs[-1].get("state") == "CHANGES_REQUESTED":
        return False, (f"{OWNER_LOGIN}'s own latest decisive review is CHANGES_REQUESTED, and a "
                       f"mandated approval does not override it{tail}")
    if last.get("state") != "APPROVED":
        return False, f"{OWNER_LOGIN}'s latest decisive review is {last.get('state')}{tail}"
    if last.get("commit_id") != head:
        return False, (f"{OWNER_LOGIN}'s approval is on {str(last.get('commit_id'))[:12]}, "
                       f"not this head {head[:12]}: an approval covers only the commit it was given on{tail}")
    if id(last) in under:
        return True, (f"an agent approved this head {head[:12]} under {OWNER_LOGIN}'s account, "
                      f"declared as an agent's, under {under[id(last)]}")
    return True, f"{OWNER_LOGIN} approved this head {head[:12]}"


def decide(raises: list[str], reviews_fn, head: str, mandate_fn=None) -> tuple[int, list[str]]:
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
    read: dict = {}

    def mandate(cid):  # each cited mandate is read once per run
        if cid not in read:
            read[cid] = mandate_fn(cid)
        return read[cid]
    try:
        ok, why = approval(reviews, head, mandate if mandate_fn else None)
    except Exception as e:  # fail closed: an unread mandate grants nothing
        lines.append(f"REFUSED: a cited mandate could not be read ({str(e).splitlines()[0][:160] if str(e) else type(e).__name__}); "
                     "a raise needs the owner's approval, and an unread mandate grants none")
        return 1, lines
    lines.append(("PASS: " if ok else "REFUSED: ") + why)
    return (0 if ok else 1), lines


# --- the live run ---------------------------------------------------------

def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def _show(sha: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{sha}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _reviews(repo: str, pr: str) -> list[dict]:
    out = subprocess.run(
        ["gh", "api", "--paginate", "--slurp", f"repos/{repo}/pulls/{pr}/reviews?per_page=100"],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"gh api exited {out.returncode}: {out.stderr.strip()}")
    pages = json.loads(out.stdout)
    return [r for page in pages for r in page]


def _mandate(repo: str, cid: int) -> tuple[dict | None, list[dict]]:
    """The cited comment (None when the API answers 404) and the tracking
    issue's comments since it was written, where a revocation would be."""
    out = subprocess.run(["gh", "api", f"repos/{repo}/issues/comments/{cid}"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        if "HTTP 404" in out.stderr:
            return None, []
        raise RuntimeError(f"gh api exited {out.returncode}: {out.stderr.strip()}")
    comment = json.loads(out.stdout)
    if not str(comment.get("issue_url") or "").endswith(MANDATE_ISSUE_URL):
        return comment, []
    out = subprocess.run(
        ["gh", "api", "--paginate", "--slurp",
         f"repos/{repo}/issues/{MANDATE_ISSUE}/comments?per_page=100&since={comment.get('created_at')}"],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"gh api exited {out.returncode}: {out.stderr.strip()}")
    return comment, [c for page in json.loads(out.stdout) for c in page]


def gate(base: str, head: str, pr: str, repo: str) -> int:
    mb = _git("merge-base", base, head).strip()
    tree = {sha: set(_git("ls-tree", "-r", "--name-only", sha).splitlines()) for sha in (mb, head)}
    # A budget file and a capped file are named old, and read where each end
    # holds them, so a move pull request compares a file with itself.
    head_files = {canon(f) for f in tree[head]}
    paths = sorted({canon(p) for t in tree.values() for p in t if p.endswith(SUFFIX)})
    raises: list[str] = []
    for p in paths:
        raises += file_raises(p, _show(mb, locate(p, tree[mb].__contains__)),
                              _show(head, locate(p, tree[head].__contains__)), head_files.__contains__)
    print(f"# merge base {mb[:12]}, head {head[:12]}: {len(paths)} budget file(s): {', '.join(paths)}")
    rc, lines = decide(raises, lambda: _reviews(repo, pr), head, lambda cid: _mandate(repo, cid))
    print("\n".join(lines))
    return rc


# --- the stale verdict's re-run ----------------------------------------------
#
# Both events write a `budget-raise-gate` check run at the head. When the owner
# approves a raise, the `pull_request_review` run passes, but the
# `pull_request` runs that refused before the approval keep their red on the
# pull request until someone runs `gh run rerun`. `budget-raise-gate-rerun.yml`
# runs `--rerun-stale` on `workflow_run`, from main's copy of this file, and
# asks GitHub to re-run each of those red runs. A re-run re-grades from nothing -- the
# program restored from the base, the reviews read live -- so this writes no
# verdict: a real red re-runs red, and only a head the owner approved turns.

GATE_WORKFLOW = ".github/workflows/budget-raise-gate.yml"
RERUN_CONCLUSIONS = ("failure", "timed_out")


def stale_run(trigger: dict, runs: list[dict]) -> tuple[str, list[int], str]:
    """(action, run ids, why): "rerun", "wait" or "none" for one completed run.

    `trigger` is the completed run `workflow_run` names; `runs` the gate's
    `pull_request` runs at its head. EVERY red one of those is re-run, not
    only the newest: GitHub's ruleset refuses a merge while any suite at the
    head carries a non-success run (#2009), and an author push that re-bodies
    the pull request starts two `pull_request` runs at one head, which both
    refuse a raise (R9-CI-2a). Nothing is re-run while one is still going.
    Only a passing review run of this very workflow triggers it; a trigger
    that is itself a `pull_request` run is refused, which is also what stops
    a re-run's own completion from starting another.
    """
    head = str(trigger.get("head_sha") or "")
    if trigger.get("path") != GATE_WORKFLOW:
        return "none", [], f"the completed run is {trigger.get('path')!r}, not {GATE_WORKFLOW}"
    if trigger.get("event") != "pull_request_review":
        return "none", [], f"the completed run is a {trigger.get('event')!r} run; only a review run re-grades"
    if trigger.get("conclusion") != "success":
        return "none", [], f"the review run concluded {trigger.get('conclusion')!r}; the red stands"
    same = sorted((r for r in runs
                   if r.get("workflow_id") == trigger.get("workflow_id")
                   and r.get("event") == "pull_request" and r.get("head_sha") == head
                   and r.get("id") != trigger.get("id")),
                  key=lambda r: (str(r.get("created_at") or ""), r.get("id") or 0))
    if not same:
        return "none", [], f"no pull_request run of the gate at {head[:12]}"
    going = [r.get("id") for r in same if r.get("status") != "completed"]
    if going:
        return "wait", going, f"run(s) {going} at {head[:12]} still going"
    red = [r.get("id") for r in same if r.get("conclusion") in RERUN_CONCLUSIONS]
    if red:
        return "rerun", red, f"run(s) {red} at {head[:12]} concluded red"
    return "none", [], f"{len(same)} pull_request run(s) at {head[:12]}, none red; nothing is stale"


def _gh_json(*args: str):
    out = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"gh api {args[-1]} exited {out.returncode}: {out.stderr.strip()[:200]}")
    return json.loads(out.stdout) if out.stdout.strip() else {}


def rerun_stale(run_id: str, repo: str, api=_gh_json, sleep=None, polls: int = 30) -> int:
    """Re-run every stale red `pull_request` run of the gate after a passing review run.

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
            action, rids, why = stale_run(trigger, runs.get("workflow_runs", []))
            if action != "wait":
                break
            print(f"WAIT: {why}")
            sleep(20)
        print(f"{action.upper()}: {why}")
        if action == "rerun":
            for rid in rids:
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

    # D11-s1-04 (card C17): an approval under the owner's account whose own
    # body says an agent gave it is not the owner's. The first five bodies are
    # the finder's reproduction, copied from merged PRs' owner reviews
    # (#1637, #1617, the 12-merge snapshot); the last is the footer every
    # agent-posted GitHub review carries.
    for label, body in (
            ("the orchestrator's mandate wording",
             "Owner approval of the code-owned tools/audit/prepr.sh at head e3d0d634. "
             "The orchestrator gives it under tvofi's explicit mandate"),
            ("the 'given by the orchestrator' wording",
             "Owner approval of policy and code-owned paths at head 240b96f3, "
             "given by the orchestrator under tvofi's explicit mandate"),
            ("a seat's wording", "Approved by the fix seat after review"),
            ("a delegation's wording", "Approving on tvofi's behalf"),
            ("a mandate named alone", "Approved under the owner's mandate"),
            ("the agent footer", "LGTM\n\n---\n_Generated by [Claude Code](https://claude.ai/code)_")):
        check(f"a raise approved at the head by an agent-declared review fails ({label})",
              rc(R, [{**rv(own, "APPROVED"), "body": body}]), 1)
    decl = {**rv(own, "APPROVED"), "body": "The orchestrator gives it under tvofi's explicit mandate"}
    check("the owner's own approval at the head still passes beside an agent-declared one",
          rc(R, [rv(own, "APPROVED"), decl]), 0)
    check("an agent-declared approval does not revive the owner's stale one",
          rc(R, [rv(own, "APPROVED", OLD), decl]), 1)
    check("an owner approval with an empty body passes (null control)",
          rc(R, [{**rv(own, "APPROVED"), "body": ""}]), 0)
    check("an owner approval whose body names no agent passes (null control)",
          rc(R, [{**rv(own, "APPROVED"), "body": "Approved: the cap raise is worth it."}]), 0)
    check("the refusal names why",
          "agent" in approval([decl], H)[1], True)

    # The owner's recorded mandate (tvofi, 2026-10-02): an agent's review under
    # the owner's account, declared as such, is decisive when it cites a
    # MANDATE comment tvofi wrote on #201 that covers budget raises and was in
    # force when the review was submitted. Each refusal arm below has a passing
    # neighbour that differs from it in the one field the arm reads.
    MID, RID = 4100000001, 4100000002
    MAND = (f"MANDATE: agents may approve as {OWNER_LOGIN}, scope budget-raise, "
            "from 2026-10-02T06:00Z until 2026-10-03T06:00Z")

    def mandate(body=MAND, user=own, created="2026-10-02T05:30:00Z", updated=None,
                issue=MANDATE_ISSUE, cid=MID) -> dict:
        return {"id": cid, "user": user, "body": body, "created_at": created,
                "updated_at": updated or created,
                "issue_url": f"https://api.github.com/repos/{DEFAULT_REPO}/issues/{issue}"}

    def revoke(cid=MID, user=own, rid=RID) -> dict:
        return {"id": rid, "user": user, "body": f"MANDATE REVOKED {cid}",
                "created_at": "2026-10-02T08:00:00Z", "updated_at": "2026-10-02T08:00:00Z",
                "issue_url": f"https://api.github.com/repos/{DEFAULT_REPO}/issues/{MANDATE_ISSUE}"}

    def agent(sha=H, at="2026-10-02T07:00:00Z", cite=f"mandate {MID}", state="APPROVED") -> dict:
        return {**rv(own, state, sha), "submitted_at": at,
                "body": f"Agent review of the raise, under {OWNER_LOGIN}'s {cite}.\n\n"
                        "---\n_Generated by [Claude Code](https://claude.ai/code)_"}

    def rcm(reviews, comment=None, thread=(), raises=R):
        if comment is None:
            comment = mandate()
        calls.clear()

        def fetch(cid):
            calls.append(cid)
            if isinstance(comment, Exception):
                raise comment
            return (comment if comment != "missing" else None), list(thread)
        try:
            return decide(raises, lambda: reviews, H, fetch)
        except Exception as e:  # an escape is a verdict too, and never 0 or 1
            return f"raised {type(e).__name__}", []
    calls: list = []

    ok_ = rcm([agent()])
    check("mandate: an agent's approval at the head under a budget-raise mandate passes", ok_[0], 0)
    check("mandate: ... and the verdict names the mandate it used",
          any(ln.startswith("PASS: ") and f"mandate {MID}" in ln for ln in ok_[1]), True)
    check("mandate: ... and the review stays declared an agent's (nothing hides authorship)",
          bool(AGENT_DECLARED.search(agent()["body"])), True)
    check("mandate: scope all covers a raise",
          rcm([agent()], mandate(MAND.replace("budget-raise", "all")))[0], 0)
    check("mandate: until programme-end is open-ended",
          rcm([agent(at="2027-06-01T00:00:00Z")],
              mandate(MAND.replace("2026-10-03T06:00Z", "programme-end")))[0], 0)
    check("mandate: the review's comment URL is a citation too",
          rcm([agent(cite=f"mandate https://github.com/{DEFAULT_REPO}/issues/201#issuecomment-{MID}")])[0], 0)
    check("mandate: no raise reads no mandate (null control)",
          (rcm([agent()], raises=[])[0], calls), (0, []))
    # Refusal arm: the mandate has expired.
    check("mandate: a review submitted after `until` fails",
          rcm([agent(at="2026-10-03T06:00:01Z")])[0], 1)
    check("mandate: a review submitted exactly at `until` fails", rcm([agent(at="2026-10-03T06:00:00Z")])[0], 1)
    check("mandate: a review submitted before `from` fails", rcm([agent(at="2026-10-02T05:59:59Z")])[0], 1)
    check("mandate: a `from` back-dated before the comment existed starts at the comment",
          rcm([agent(at="2026-10-02T06:30:00Z")], mandate(created="2026-10-02T06:45:00Z"))[0], 1)
    check("mandate: a mandate edited after the review fails",
          rcm([agent()], mandate(updated="2026-10-02T07:30:00Z"))[0], 1)
    check("mandate: a review with no submitted_at fails", rcm([{**agent(), "submitted_at": None}])[0], 1)
    # Refusal arm: the mandate was revoked.
    check("mandate: a mandate tvofi revoked fails", rcm([agent()], thread=[revoke()])[0], 1)
    check("mandate: ... and the refusal names the revocation",
          any(str(RID) in ln and "revoked" in ln for ln in rcm([agent()], thread=[revoke()])[1]), True)
    check("mandate: a revocation by another account revokes nothing (null control)",
          rcm([agent()], thread=[revoke(user={"login": "someone", "id": 1, "type": "User"})])[0], 0)
    check("mandate: a revocation of another mandate revokes nothing (null control)",
          rcm([agent()], thread=[revoke(cid=MID + 7)])[0], 0)
    # Refusal arm: the mandate comment is not tvofi's.
    check("mandate: a mandate comment by another account fails",
          rcm([agent()], mandate(user={"login": "someone", "id": 1, "type": "User"}))[0], 1)
    check("mandate: a mandate comment by an account named tvofi with another id fails",
          rcm([agent()], mandate(user={**own, "id": OWNER_ID + 1}))[0], 1)
    check("mandate: a mandate comment by the approver App fails", rcm([agent()], mandate(user=app))[0], 1)
    check("mandate: a mandate comment on another issue fails", rcm([agent()], mandate(issue=1838))[0], 1)
    check("mandate: a cited comment that does not exist fails", rcm([agent()], "missing")[0], 1)
    check("mandate: a mandate comment on #201 of another repository fails",
          rcm([agent()], {**mandate(), "issue_url": "https://api.github.com/repos/evil/other/issues/201"})[0], 1)
    check("mandate: a mandate read that fails, fails closed", rcm([agent()], RuntimeError("HTTP 502"))[0], 1)
    check("mandate: a body that is not the grammar fails",
          rcm([agent()], mandate("agents may approve as tvofi for budget raises until Friday"))[0], 1)
    check("mandate: a time with no zone fails",
          rcm([agent()], mandate(MAND.replace("2026-10-02T06:00Z", "2026-10-02T06:00")))[0], 1)
    # Refusal arm: the scope does not cover budget raises.
    check("mandate: scope code-owned does not cover a raise",
          rcm([agent()], mandate(MAND.replace("budget-raise", "code-owned")))[0], 1)
    # Refusal arm: the review is not on the head.
    check("mandate: a mandated approval on a non-head commit fails", rcm([agent(sha=OLD)])[0], 1)
    # What the mandate leaves as it was.
    check("mandate: an agent's approval citing no mandate still fails (null control)",
          rcm([agent(cite="explicit mandate")])[0], 1)
    check("mandate: a review citing two mandates fails",
          rcm([agent(cite=f"mandate {MID} and mandate {MID + 1}")])[0], 1)
    check("mandate: an agent's CHANGES_REQUESTED under a mandate decides nothing",
          rcm([agent(), agent(state="CHANGES_REQUESTED")])[0], 0)
    check("mandate: the owner's own later CHANGES_REQUESTED still decides",
          rcm([agent(), rv(own, "CHANGES_REQUESTED")])[0], 1)
    check("mandate: a mandated approval from another account is not the owner's",
          rcm([{**agent(), "user": app}])[0], 1)
    # Round 2 (fix review of #1843). The kill switch is matched loosely, since
    # over-revoking fails safe and a near miss failed open: tvofi's comment
    # naming the id with any form of "revoke" voids it, on any line.
    for form in (f"MANDATE REVOKED {MID}.", f"MANDATE REVOKED #{MID}", f"MANDATE REVOKED: {MID}",
                 f"Mandate revoked {MID}", f"Ending it now.\nMANDATE REVOKED {MID}",
                 f"I revoke mandate https://github.com/{DEFAULT_REPO}/issues/201#issuecomment-{MID}"):
        check(f"mandate: the revocation {form!r} revokes",
              rcm([agent()], thread=[{**revoke(), "body": form}])[0], 1)
    check("mandate: a revocation naming a longer id that contains this one revokes nothing (null control)",
          rcm([agent()], thread=[{**revoke(), "body": f"MANDATE REVOKED {MID}9"}])[0], 0)
    check("mandate: tvofi's comment naming the id with no revocation word revokes nothing (null control)",
          rcm([agent()], thread=[{**revoke(), "body": f"Agents are working under mandate {MID}."}])[0], 0)
    # A mandate comment edited at any time grants nothing: anyone with write
    # access can edit tvofi's comment, and its user field stays tvofi.
    check("mandate: a mandate edited before the review fails",
          rcm([agent()], mandate(created="2026-09-01T00:00:00Z", updated="2026-10-02T06:30:00Z"))[0], 1)
    check("mandate: ... and the refusal says it was edited",
          any("edited" in ln for ln in rcm([agent()], mandate(updated="2026-10-02T05:31:00Z"))[1]), True)
    check("mandate: a body that is not the grammar is refused as such, not as an unread mandate",
          any("not the mandate grammar" in ln for ln in rcm([agent()], mandate("MANDATE: agents may approve"))[1]),
          True)
    # A mandate lets an agent approve; it does not let one overrule tvofi.
    check("mandate: a mandated approval does not override tvofi's own earlier CHANGES_REQUESTED",
          rcm([rv(own, "CHANGES_REQUESTED"), agent()])[0], 1)
    check("mandate: ... and the refusal says so",
          any("CHANGES_REQUESTED" in ln for ln in rcm([rv(own, "CHANGES_REQUESTED"), agent()])[1]), True)
    check("mandate: tvofi's own later approval clears his CHANGES_REQUESTED, as before (null control)",
          rcm([rv(own, "CHANGES_REQUESTED"), agent(), rv(own, "APPROVED")])[0], 0)
    check("mandate: tvofi's own earlier DISMISSED blocks nothing",
          rcm([rv(own, "DISMISSED"), agent()])[0], 0)

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
          stale_run(T0, [pr_run(3)])[:2], ("rerun", [3]))
    # R9-CI-2a: an author push that re-bodies the pull request starts two
    # `pull_request` runs at one head, and both refuse a raise. The ruleset
    # blocks on a red run in any suite at the head, not the newest alone
    # (#2009), so every red one is re-run, never only the newest.
    check("rerun: two red twins at one head, both re-run",
          stale_run(T0, [pr_run(3), pr_run(4)])[:2], ("rerun", [3, 4]))
    check("rerun: an older red run beside a newer green one is still re-run",
          stale_run(T0, [pr_run(3), pr_run(4, "success")])[:2], ("rerun", [3]))
    check("rerun: ... and a newer red one beside an older green one",
          stale_run(T0, [pr_run(3, "success"), pr_run(4)])[:2], ("rerun", [4]))
    check("rerun: twins both green re-run nothing (null control)",
          stale_run(T0, [pr_run(3, "success"), pr_run(4, "success")])[:2], ("none", []))
    check("rerun: a twin still going is waited for before either is re-run",
          stale_run(T0, [pr_run(3), pr_run(4, None, "in_progress")])[:2], ("wait", [4]))
    check("rerun: a failing review run re-runs nothing (the red stands)",
          stale_run({**T0, "conclusion": "failure"}, [pr_run(3)])[:2], ("none", []))
    check("rerun: a pull_request trigger re-runs nothing (no loop on the re-run's own completion)",
          stale_run({**T0, "event": "pull_request"}, [pr_run(3)])[:2], ("none", []))
    check("rerun: another workflow's run is not the gate",
          stale_run({**T0, "path": ".github/workflows/tests.yml"}, [pr_run(3)])[:2], ("none", []))
    check("rerun: a red run at another head is left alone",
          stale_run(T0, [pr_run(3, sha=OLD)])[:2], ("none", []))
    check("rerun: a red run of another workflow is left alone",
          stale_run(T0, [pr_run(3, wf=6)])[:2], ("none", []))
    check("rerun: a cancelled run is left alone", stale_run(T0, [pr_run(3, "cancelled")])[:2], ("none", []))
    check("rerun: a run still going is waited for",
          stale_run(T0, [pr_run(3, None, "in_progress")])[:2], ("wait", [3]))

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
    api, calls = fake([[pr_run(3), pr_run(4)]])
    check("rerun: end to end, two red twins post two re-runs",
          (rerun_stale("9", "o/r", api, sleep=lambda s: None),
           [c for c in calls if c[0] == "-X"]),
          (0, [("-X", "POST", "repos/o/r/actions/runs/3/rerun"),
               ("-X", "POST", "repos/o/r/actions/runs/4/rerun")]))
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
for key, route in spec.get("routes", {}).items():
    if key in sys.argv[-1]:
        sys.stderr.write(route.get("err", ""))
        sys.stdout.write(json.dumps(route.get("out")))
        sys.exit(route.get("rc", 0))
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
        from throwaway_git import throwaway_git_env, throwaway_git_init  # tests/, on sys.path above
        env = throwaway_git_env({k: v for k, v in os.environ.items()
                                 if not k.startswith(("GIT_", "GH_", "GITHUB_"))})
        env.update(PATH=stub + os.pathsep + os.environ.get("PATH", ""), BRG_STUB=stub)

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
        throwaway_git_init(repo, "-q", "-b", "main")
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
        import layout  # RO-1's own reading of the move map, not the lookup under test
        NP = layout.target(P, layout.load(layout.ROOT)["retired"])
        moved = branch("moved", {P: None, NP: p0})
        moved_up = branch("moved-up", {P: None, NP: {**p0, "always_loaded_tokens": 3350}})
        own = {"login": OWNER_LOGIN, "id": OWNER_ID, "type": OWNER_TYPE}

        def run(head: str, pages=None, rc=0, argv=None, repo_env=None, routes=None):
            with open(os.path.join(stub, "reviews.json"), "w") as f:
                json.dump({"pages": pages if pages is not None else [[]], "rc": rc,
                           "routes": routes or {}}, f)
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
        rc_, text, calls = run(moved)
        out.append(("e2e: a budget file moved to its new path, unchanged, is no raise (R9-RO-2)",
                    (rc_, "budget_raises=0" in text, "3 budget file(s)" in text), (0, True, True)))
        rc_, text, _ = run(moved_up)
        out.append(("e2e: ... and one raised as it moved is a raise, named at its old path",
                    (rc_, f"RAISE {P}: always_loaded_tokens: 3349 -> 3350" in text), (1, True)))
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
        # The mandate, read live: the cited comment by id, then #201's comments
        # since it was written, where a revocation would be.
        cid = 4100000001
        mand = {"id": cid, "user": own, "created_at": "2026-10-02T05:30:00Z",
                "updated_at": "2026-10-02T05:30:00Z",
                "issue_url": f"https://api.github.com/repos/{DEFAULT_REPO}/issues/{MANDATE_ISSUE}",
                "body": (f"MANDATE: agents may approve as {OWNER_LOGIN}, scope budget-raise, "
                         "from 2026-10-02T06:00Z until 2026-10-03T06:00Z")}
        agent_rv = {**approved(raise_), "id": 9, "submitted_at": "2026-10-02T07:00:00Z",
                    "body": f"Agent review under mandate {cid}.\n\n---\n_Generated by [Claude Code](https://claude.ai/code)_"}
        thread_key = f"issues/{MANDATE_ISSUE}/comments"
        rc_, text, calls = run(raise_, pages=[[agent_rv]],
                               routes={f"issues/comments/{cid}": {"out": mand},
                                       thread_key: {"out": [[]]}})
        out.append(("e2e: a raise approved at the head under a mandate in force exits 0",
                    (rc_, f"under mandate {cid}" in text), (0, True)))
        out.append(("e2e: ... after reading the comment, then #201 since it was written",
                    [c[-1] for c in calls][1:],
                    [f"repos/tvofi/heatpump_optimizer/issues/comments/{cid}",
                     f"repos/tvofi/heatpump_optimizer/{thread_key}?per_page=100&since=2026-10-02T05:30:00Z"]))
        revoked = {**mand, "id": cid + 1, "created_at": "2026-10-02T08:00:00Z",
                   "body": f"MANDATE REVOKED {cid}"}
        rc_, text, _ = run(raise_, pages=[[agent_rv]],
                           routes={f"issues/comments/{cid}": {"out": mand},
                                   thread_key: {"out": [[revoked]]}})
        out.append(("e2e: ... and exits 1 once tvofi revokes it", (rc_, "revoked" in text), (1, True)))
        rc_, text, _ = run(raise_, pages=[[agent_rv]],
                           routes={f"issues/comments/{cid}": {"rc": 1, "err": "gh: Not Found (HTTP 404)"}})
        out.append(("e2e: a cited mandate that does not exist exits 1",
                    (rc_, "not a comment that exists" in text), (1, True)))
        rc_, text, _ = run(raise_, pages=[[agent_rv]],
                           routes={f"issues/comments/{cid}": {"rc": 1, "err": "HTTP 502"}})
        out.append(("e2e: a mandate read that fails otherwise exits 1",
                    (rc_, "could not be read" in text), (1, True)))
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

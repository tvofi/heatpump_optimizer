#!/usr/bin/env python3
"""prune_refs.py — reconcile the remote branch refs down to main plus a few
development branches, archive-as-tags first, and never touch one a rule keeps.

    python3 tools/audit/seat/prune_refs.py [--repo OWNER/REPO] [--main main]
        [--refs-file FILE] [--prs-file FILE]
        [--archive-scope {all,orphans}] [--keep-residue]
        [--verdicts-drained] [--roster-file FILE] [--via {push,api}]
        [--topic T] [--apply]
    python3 tools/audit/seat/prune_refs.py --self-test

WHY THIS EXISTS. The round-9 closure (#2086) leaves main plus at most three
development branches and archives every other ref as a tag. Doing that with a
session-local loop is decision 0013's defect shape -- the loop runs once, in a
scratch directory, and no later session can test it. This is the loop, once,
with the group brief's four rules and its four hazards written down as code.

THE RULES (from the R9-CLOSURE-BRANCHES brief):

  keep   `main`, and a ref whose pull request is OPEN -- deleting that head
         closes the pull request.
  delete a ref already merged into main (decision 0010 keeps its commits as
         the merge's second parent, so nothing is lost).
  delete an unmerged `handoff/*` ref whose pull request MERGED -- the head that
         merged superseded it (its commits are the pull request's, not this
         ref's).
  residue a ref with no pull request, or only a CLOSED-unmerged one, has no
         rule that settles it: it is ENUMERATED and dispositioned individually.
         An audit-round evidence ref is the bulk of this; per the owner's
         2026-10-14 ruling it is archived as a tag first, so its citations
         survive, then its branch is deleted.

THE ARCHIVE ARM, and why it precedes every deletion. A deletion is
irreversible for a tip that is not yet reachable from anything else, and the
repository's ruleset protects `main` alone -- nothing stops a wrong deletion
of a branch. So each ref this plan deletes is FIRST retagged at its own commit
under `refs/tags/archive/<family>/<name>` (the branch's own name under
`archive/`; `v*` is the release namespace and stays clear). Tags are not
branches, so the end state -- main plus a few branches -- holds while the
evidence stays citable by tag. The plan is ORDERED: every `tag:` line precedes
every `delete:` line, and with `--archive-scope none` nothing is deleted
either, because an unarchived tip is the one deletion that cannot be undone.
`--archive-scope orphans` (tag only tips not reachable from main) is the
narrower arm the brief's step 3 describes; the default `all` is the owner's
2026-10-14 ruling ("the ~505 non-keep refs go to refs/tags/archive/... ").

THE HAZARDS, each a guard rather than a comment:

  main        `main` is never scheduled for any action; a plan that would act
              on it raises. The ruleset's deletion rule covers `main` and
              nothing else, so this is the one ref that must be reflexive.
  open PR     an open-pull-request ref is never scheduled for deletion, even
              if it also satisfies an earlier rule (the open-PR keep dominates
              -- asserted by a null control in --self-test).
  verdicts    `verdict/*` is the bus watcher's live channel (bus.sh reads the
              proposed and signed verdict refs); the plan REFUSES to schedule
              them for deletion unless `--verdicts-drained`, so pruning cannot
              race the last verdict post.
  citations   a ref cited by a brief that is deleted breaks the linter, not
              the build -- so the citation sweep is a PREREQUISITE of the
              deletion, never something this instrument can enforce. It prints
              the reminder rather than pretending to check it.

THE KEEP GUARDS (R10-CLOSEOUT-CLEANUP, carry 2). A live `claude/*` session
branch is kept whatever its tip (an orchestrator's own branch has a tip in
main and would otherwise read as merged). A `design/<group>` or
`design-verdict/<group>` ref is kept while `--roster-file` records the group
not done; the same ref of a done group is still deleted. With the tip ages
read (the live path), a tip younger than 6 h, or a `dispatch/*` tip younger
than 24 h, is kept, and a tip whose age cannot be read is kept too: an age is
unknowable, never 0.

THE APPLY ARMS. `--via push` (the default) writes by `git push`: every tag as
a `<sha>:refs/tags/archive/<name>` refspec in chunks of 100, then a read-back
of the remote's tags, then `git push --delete` in the same chunks, aborting on
the first refusal -- no GitHub API write at all, where `--via api` makes one
REST write per tag and per delete (2N for N refs) against the shared token
budget. The push arm refuses before the first delete when a ref it would
delete has no tag at its own sha, apart from the names the plan itself lists
as deleted untagged (a `ci-probe/*` ref, or a tip already in main under
`--archive-scope orphans`).

`--topic T` restricts the same classifier and the archive-first step to the
refs of one topic (`handoff/T`, `handoff-body/T`, their `-rN` variants and
`dispatch/*T*`), and refuses the whole topic, touching nothing, when any of
its tips has a `+` line in `git cherry <main> <tip>` (content not on main) or
when any ref of it has an open pull request.

`--apply` is required to act; without it (the default) the run is a dry plan:
nothing remote is written and every action is printed. Reading the refs and
the pull requests never writes: `--refs-file` / `--prs-file` are the offline
path a seat uses to reproduce a plan, and the live path only reads
(`git ls-remote`, `gh pr list`).

Self-test: offline and total. It drives the pure classifier and planner over
synthetic ref/PR sets -- one arm per rule, the residue, and the two refusal
arms (main scheduled, verdicts not drained) -- plus the null control (an
open-PR ref that also matches the merged rule is kept, not deleted) and the
ordering invariant (every tag precedes every delete). No network, no repo.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ref_privacy  # noqa: E402  an archive tag never names this host (#2310)

SELF = "tools/audit/seat/prune_refs.py"
ARCHIVE_PREFIX = "archive/"
HANDOFF_PREFIX = "handoff/"
VERDICT_PREFIX = "verdict/"
CI_PROBE_PREFIX = "ci-probe/"
MAIN_REF = "main"
CLAUDE_PREFIX = "claude/"
DESIGN_PREFIXES = ("design/", "design-verdict/")
DISPATCH_PREFIX = "dispatch/"
YOUNG_TIP_S = 6 * 3600
YOUNG_DISPATCH_S = 24 * 3600
PUSH_CHUNK = 100

# Every rule label the classifier can return, and the action each maps to.
KEEP = "keep"
KEEP_SESSION = "keep-live-session"
KEEP_DESIGN = "keep-open-group-design"
KEEP_YOUNG = "keep-young-tip"
DELETE_MERGED = "delete-merged-into-main"
DELETE_HANDOFF_PR = "delete-handoff-pr-merged"
DELETE_CI_PROBE = "delete-ci-probe"
RESIDUE_CLOSED = "residue-closed-pr"
RESIDUE_NONE = "residue-no-pr"

_KEEP_RULES = {KEEP, KEEP_SESSION, KEEP_DESIGN, KEEP_YOUNG}
_DELETE_RULES = {DELETE_MERGED, DELETE_HANDOFF_PR, DELETE_CI_PROBE}
_RESIDUE_RULES = {RESIDUE_CLOSED, RESIDUE_NONE}


def family_of(name: str) -> str:
    """The branch's first path segment; `handoff/audit-r9-fixplan` -> handoff."""
    return name.split("/", 1)[0]


def archive_tag(name: str) -> str:
    """The archive tag a branch's tip is retagged under.

    `<name>` under the `archive/` namespace, which is the brief's
    `archive/<family>/<name>` because `<name>` already carries the family as
    its first segment. `archive/` is clear of the release `v*` namespace.
    """
    return ARCHIVE_PREFIX + name


def refs_reachable_from_main(main: str) -> set:
    """Every commit reachable from `main`, read from the local objects."""
    out = subprocess.run(["git", "rev-list", main], check=True,
                         capture_output=True, text=True).stdout
    return set(out.split())


def read_refs_file(path: str) -> dict:
    """`git ls-remote --heads` output -> {branch: sha}. The offline arm."""
    refs = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or "refs/heads/" not in line:
                continue
            sha, ref = line.split()[:2]
            refs[ref.split("refs/heads/", 1)[1]] = sha
    return refs


def live_refs(remote: str) -> dict:
    """The live arm: `git ls-remote --heads <remote>` -> {branch: sha}."""
    out = subprocess.run(["git", "ls-remote", "--heads", remote], check=True,
                         capture_output=True, text=True).stdout
    refs = {}
    for line in out.splitlines():
        if "refs/heads/" not in line:
            continue
        sha, ref = line.split()[:2]
        refs[ref.split("refs/heads/", 1)[1]] = sha
    return refs


def index_prs(prs: list) -> dict:
    """branch -> {open, merged, closed} pull-request numbers for that head."""
    index: dict = {}
    for p in prs:
        head = p.get("headRefName")
        if not head:
            continue
        slot = index.setdefault(head, {"open": [], "merged": [], "closed": []})
        state = p.get("state")
        num = p.get("number")
        if state == "OPEN":
            slot["open"].append(num)
        elif state == "MERGED":
            slot["merged"].append(num)
        elif state == "CLOSED":
            slot["closed"].append(num)
    return index


def read_prs_file(path: str) -> list:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def live_prs(repo: str, limit: int) -> list:
    out = subprocess.run(
        ["gh", "pr", "list", "--repo", repo, "--state", "all",
         "--limit", str(limit), "--json", "number,state,headRefName"],
        check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def done_group_branches(roster_path: str) -> frozenset:
    """The branches of the roster's done groups, via `roster_lib`.

    A group recorded `done`/`rca-done` has merged, so its staging branch is
    superseded -- the head that merged is the pull request's. `roster_lib`
    owns both `DONE_STAGES` and `branch_of`, so this reads the same record the
    record beat rows against rather than re-deriving the mapping (#1948).
    """
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import roster_lib
    with open(roster_path, encoding="utf-8") as fh:
        roster = json.load(fh)
    return frozenset(
        roster_lib.branch_of(g)
        for g in roster.get("groups", [])
        if (g.get("resume") or {}).get("stage") in roster_lib.DONE_STAGES)


def open_group_ids(roster_path: str) -> frozenset:
    """The ids of the roster's groups that are not done (`roster_lib.is_open`)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import roster_lib
    with open(roster_path, encoding="utf-8") as fh:
        return frozenset(roster_lib.open_groups(json.load(fh)))


def tip_ages(shas, now: float, git=subprocess.run) -> dict:
    """sha -> committer-date age in seconds, for the shas the local objects hold.

    One `git log --no-walk` for all of them. A sha the checkout lacks is left
    out, and `classify` then keeps its ref: an age is unknowable, never 0.
    """
    shas = sorted(set(shas))
    out = {}
    for i in range(0, len(shas), 500):
        r = git(["git", "log", "--no-walk=unsorted", "--format=%H %ct",
                 *shas[i:i + 500]], capture_output=True, text=True)
        for line in r.stdout.splitlines():
            h, _, ct = line.partition(" ")
            if ct.isdigit():
                out[h] = max(0.0, now - int(ct))
    return out


def classify(name: str, sha: str, prs: dict, main_reachable: set,
             done_branches: frozenset = frozenset(),
             open_groups: frozenset = frozenset(),
             ages: "dict | None" = None) -> str:
    """The rule that settles one ref. Order is the precedence, not a detail.

    `main` first, then an open pull request (the keep that dominates), then a
    tip already merged into main, then a handoff ref whose pull request
    merged, then the residue.

    "whose pull request MERGED" has two evidence sources: a same-named pull
    request that merged (a seat that opened the PR from the handoff ref), and
    the ref being the branch of a roster group the roster records as done --
    the head that merged superseded it even when the PR rode another branch.
    `done_branches` carries the second, from `--roster-file`.

    Between the open-PR keep and the rest sit three more keeps: a `claude/*`
    live session branch, a `design/` or `design-verdict/` ref of a group in
    `open_groups`, and (when `ages` is given) a tip younger than 6 h, a
    `dispatch/*` tip younger than 24 h, or a tip with no readable age.

    A `ci-probe/*` ref (ci_probe.py's namespace) is deletable once no open pull
    request has it as its head, whatever its tip: the open-PR keep above is the
    only thing that holds one.
    """
    if name == MAIN_REF:
        return KEEP
    slot = prs.get(name) or {}
    if slot.get("open"):
        return KEEP
    if name.startswith(CLAUDE_PREFIX):
        return KEEP_SESSION
    for pre in DESIGN_PREFIXES:
        if name.startswith(pre) and name[len(pre):] in open_groups:
            return KEEP_DESIGN
    if ages is not None:
        age = ages.get(sha)
        limit = YOUNG_DISPATCH_S if name.startswith(DISPATCH_PREFIX) else YOUNG_TIP_S
        if age is None or age < limit:
            return KEEP_YOUNG
    if name.startswith(CI_PROBE_PREFIX):
        return DELETE_CI_PROBE
    if sha in main_reachable:
        return DELETE_MERGED
    if name.startswith(HANDOFF_PREFIX) and (slot.get("merged")
                                            or name in done_branches):
        return DELETE_HANDOFF_PR
    if slot.get("closed") or slot.get("merged"):
        return RESIDUE_CLOSED
    return RESIDUE_NONE


def plan(refs: dict, prs: dict, main_reachable: set, *, archive_scope: str,
         keep_residue: bool, verdicts_drained: bool,
         done_branches: frozenset = frozenset(),
         open_groups: frozenset = frozenset(),
         ages: "dict | None" = None) -> dict:
    """The ordered action list for a ref set, or raise on a refused plan.

    Returns {"rows": [(name, sha, family, rule, action)], "actions":
    [(verb, arg, sha)]} where verb is "tag" or "delete". Raises ValueError when
    a plan would touch `main` or a `verdict/*` ref that has not drained.
    """
    rows = []
    for name in sorted(refs):
        rule = classify(name, refs[name], prs, main_reachable, done_branches,
                        open_groups, ages)
        if name == MAIN_REF and rule != KEEP:
            raise ValueError("a plan must never act on main")
        if rule in _RESIDUE_RULES:
            action = "keep" if keep_residue else "archive-delete"
        elif rule in _DELETE_RULES:
            action = "archive-delete"
        else:
            action = "keep"
        if action == "archive-delete" and name.startswith(VERDICT_PREFIX) \
                and not verdicts_drained:
            raise ValueError(
                f"refusing to schedule {name}: the bus watcher reads the "
                f"verdict refs; pass --verdicts-drained once the last verdict "
                f"posts")
        rows.append((name, refs[name], family_of(name), rule, action))

    tags, deletes, untagged = [], [], []
    for name, sha, _fam, rule, action in rows:
        if action != "archive-delete":
            continue
        # A deletion is safe only once its tip is preserved: as a tag (all /
        # orphans) or because the tip already lives in main. `none` archives
        # nothing and therefore deletes nothing -- it is the preview arm.
        if archive_scope == "none":
            continue
        if rule == DELETE_CI_PROBE:
            # a probe ref is throwaway, cited by no brief: deleted without a tag
            deletes.append(("delete", name, sha))
            untagged.append(name)
            continue
        if archive_scope == "all" or sha not in main_reachable:
            # A tag is permanent: one naming this host is refused, plan and all,
            # before anything is written (#2310). The name is not echoed.
            why = ref_privacy.refusal(archive_tag(name))
            if why:
                raise ValueError(f"refusing to archive the tip {sha[:12]}: {why} would publish this host "
                                 f"(#2310); rename or remove that branch by hand")
            tags.append(("tag", archive_tag(name), sha))
        else:
            untagged.append(name)
        deletes.append(("delete", name, sha))
    # THE ORDER IS THE SAFETY: every tag before every delete, so a deletion
    # can never precede the tag that preserves its tip.
    actions = tags + deletes
    return {"rows": rows, "actions": actions, "tags": len(tags),
            "deletes": len(deletes), "untagged": frozenset(untagged)}


def apply_plan(repo: str, actions: list, dry_run: bool) -> list:
    """Create the archive tags, then delete the branches, over the GitHub API."""
    done = []
    for verb, arg, sha in actions:
        if verb == "tag":
            if dry_run:
                done.append(("would-tag", f"{arg}@{sha}"))
                continue
            ref = "refs/tags/" + arg
            r = subprocess.run(
                ["gh", "api", f"repos/{repo}/git/refs", "-f", f"ref={ref}",
                 "-f", f"sha={sha}"], capture_output=True, text=True)
            done.append(("tag", f"{arg}@{sha}") if r.returncode == 0
                        else ("tag-FAILED", f"{arg}: {r.stderr.strip()[:120]}"))
        else:
            if dry_run:
                done.append(("would-delete", f"{arg}@{sha}"))
                continue
            r = subprocess.run(
                ["gh", "api", "-X", "DELETE",
                 f"repos/{repo}/git/refs/heads/{arg}"],
                capture_output=True, text=True)
            done.append(("delete", arg) if r.returncode == 0
                        else ("delete-FAILED", f"{arg}: {r.stderr.strip()[:120]}"))
    return done

class ApplyRefused(RuntimeError):
    """The push arm refused before writing a delete (an unarchived tip)."""


def _chunks(items: list, n: int = PUSH_CHUNK):
    for i in range(0, len(items), n):
        yield items[i:i + n]


def remote_tags(remote: str, git=subprocess.run) -> dict:
    """{tag name: sha} of the remote's `refs/tags/archive/*`, read back."""
    r = git(["git", "ls-remote", "--tags", remote, "refs/tags/archive/*"],
            capture_output=True, text=True)
    if r.returncode != 0:
        raise ApplyRefused(f"cannot read the remote's tags: {r.stderr.strip()[:120]}")
    out = {}
    for line in r.stdout.splitlines():
        sha, _, ref = line.partition("\t")
        if ref and not ref.endswith("^{}"):
            out[ref.split("refs/tags/", 1)[1]] = sha
    return out


def apply_plan_push(remote: str, actions: list, dry_run: bool,
                    untagged: frozenset = frozenset(), chunk: int = PUSH_CHUNK,
                    git=subprocess.run) -> list:
    """Create the archive tags, then delete the branches, by `git push`.

    Tags go first as `<sha>:refs/tags/<tag>` refspecs, `chunk` to a push; the
    remote's tags are then read back; only then do the deletes go, in the same
    chunks. The first refused push aborts the rest (the failure is the last
    entry). A delete whose ref has no tag at its own sha on the remote -- and
    is not in `untagged`, the names the plan itself deletes untagged -- raises
    ApplyRefused before ANY delete is written. Zero GitHub API calls.
    """
    tags = [(a, s) for v, a, s in actions if v == "tag"]
    deletes = [(a, s) for v, a, s in actions if v == "delete"]
    if any(a == MAIN_REF for a, _ in deletes):
        raise ApplyRefused("a plan must never delete main")
    done = []
    if dry_run:
        return ([("would-tag", f"{a}@{s}") for a, s in tags]
                + [("would-delete", f"{a}@{s}") for a, s in deletes])

    def push(args: list) -> "str | None":
        r = git(["git", "push", "-q", remote, *args], capture_output=True, text=True)
        return None if r.returncode == 0 else (r.stderr.strip()[:160] or "push refused")

    for part in _chunks(tags, chunk):
        err = push([f"{s}:refs/tags/{a}" for a, s in part])
        if err:
            done.append(("tag-FAILED", f"chunk of {len(part)} from {part[0][0]}: {err}"))
            return done
        done += [("tag", f"{a}@{s}") for a, s in part]
    have = remote_tags(remote, git) if tags or deletes else {}
    missing = [n for n, s in deletes
               if n not in untagged and have.get(archive_tag(n)) != s]
    if missing:
        raise ApplyRefused(f"{len(missing)} ref(s) to delete lack their archive tag at "
                           f"the same sha on the remote, first {missing[0]}; nothing deleted")
    for part in _chunks(deletes, chunk):
        err = push(["--delete", *[f"refs/heads/{n}" for n, _ in part]])
        if err:
            done.append(("delete-FAILED", f"chunk of {len(part)} from {part[0][0]}: {err}"))
            return done
        done += [("delete", n) for n, _ in part]
    return done


# --topic: one topic's refs, archived-then-deleted, or refused whole.

def topic_matches(name: str, topic: str) -> bool:
    """handoff/T, handoff-body/T, handoff*/T-rN, and dispatch/*T* (a `-T` suffix)."""
    fam, _, tail = name.partition("/")
    rn = re.compile(r"(?:^|-)" + re.escape(topic) + r"(?:-r\d+)?$")
    if fam.startswith("handoff"):
        return bool(re.fullmatch(re.escape(topic) + r"(?:-r\d+)?", tail))
    return fam == "dispatch" and bool(rn.search(tail))


def cherry_plus(main: str, sha: str, git=subprocess.run) -> bool:
    """True when `git cherry <main> <sha>` has a `+` line (content not on main)."""
    r = git(["git", "cherry", main, sha], capture_output=True, text=True)
    if r.returncode != 0:
        return True     # unreadable is not on main
    return any(line.startswith("+") for line in r.stdout.splitlines())


def plan_topic(refs: dict, prs: dict, topic: str, main: str,
               main_reachable: set, git=subprocess.run) -> dict:
    """The plan for one topic, or ValueError naming why it is refused.

    Refused whole -- nothing scheduled -- when no ref carries the topic, when
    any of its refs has an open pull request, or when any tip has a `+` cherry
    line against `main`. Otherwise every topic ref is archived, then deleted.
    """
    mine = {n: s for n, s in refs.items() if n != MAIN_REF and topic_matches(n, topic)}
    if not mine:
        raise ValueError(f"no ref carries the topic {topic!r}")
    opened = sorted(n for n in mine if (prs.get(n) or {}).get("open"))
    if opened:
        raise ValueError(f"topic {topic!r} has an open pull request on {opened[0]}")
    # only a code ref (`handoff/`, `-rN`) is content-checked: a handoff-body or
    # dispatch ref is an orphan commit carrying a body or brief, never a patch
    ahead = sorted(n for n, s in mine.items()
                   if n.startswith(HANDOFF_PREFIX) and s not in main_reachable
                   and cherry_plus(main, s, git))
    if ahead:
        raise ValueError(f"topic {topic!r} is not on main: {ahead[0]} has a '+' "
                         f"cherry line ({len(ahead)} ref(s))")
    p = plan(mine, {}, set(), archive_scope="all", keep_residue=False,
             verdicts_drained=False)
    # every topic ref was proved on main above, so each is archive-delete
    # whatever rule the classifier gave it
    p["rows"] = [(n, s, f, r, "archive-delete") for n, s, f, r, _a in p["rows"]]
    return p


# ---------------------------------------------------------------------------
# self-test: the classifier, the planner, the precedence and the order.

def _check(tag: str, cond: bool, results: list) -> None:
    results.append((tag, bool(cond)))


def _self_test_keeps(results: list) -> None:
    """The keep guards and the topic matcher (pure)."""
    reachable = {"a" * 40}
    merged, orphan = "a" * 40, "b" * 40
    _check("a claude/* ref with a main-reachable tip is kept",
           classify("claude/audit-x", merged, {}, reachable) == KEEP_SESSION, results)
    _check("null: the same tip on a fix/ ref is deleted",
           classify("fix/audit-x", merged, {}, reachable) == DELETE_MERGED, results)
    og = frozenset({"R10-NOT-STARTED"})
    _check("a design/ ref of a not-done group is kept",
           classify("design/R10-NOT-STARTED", orphan, {}, reachable, frozenset(), og)
           == KEEP_DESIGN, results)
    _check("a design-verdict/ ref of a not-done group is kept",
           classify("design-verdict/R10-NOT-STARTED", orphan, {}, reachable,
                    frozenset(), og) == KEEP_DESIGN, results)
    _check("null: the same design/ ref of a done group is still deleted",
           classify("design/R10-DONE", orphan, {}, reachable, frozenset(), og)
           == RESIDUE_NONE, results)
    ages = {orphan: 5 * 3600.0, merged: 7 * 3600.0}
    _check("a tip younger than 6 h is kept",
           classify("fix/y", orphan, {}, reachable, ages=ages) == KEEP_YOUNG, results)
    _check("null: a tip older than 6 h is deleted",
           classify("fix/y", merged, {}, reachable, ages=ages) == DELETE_MERGED, results)
    _check("a dispatch/* tip of 7 h is kept (24 h guard)",
           classify("dispatch/fixer-t", merged, {}, reachable, ages=ages) == KEEP_YOUNG,
           results)
    _check("null: a dispatch/* tip of 25 h is deleted",
           classify("dispatch/fixer-t", merged, {}, reachable,
                    ages={merged: 25 * 3600.0}) == DELETE_MERGED, results)
    _check("a tip whose age is unreadable is kept, never read as 0-or-old",
           classify("fix/y", merged, {}, reachable, ages={}) == KEEP_YOUNG, results)
    _check("no ages given disables the guard (the offline arm)",
           classify("fix/y", merged, {}, reachable, ages=None) == DELETE_MERGED, results)
    _check("the open-PR keep dominates the session keep",
           classify("claude/x", merged, {"claude/x": {"open": [1]}}, reachable) == KEEP,
           results)
    for name, topic, want in (("handoff/t", "t", True), ("handoff-body/t", "t", True),
                              ("handoff/t-r2", "t", True), ("handoff-body/t-r12", "t", True),
                              ("dispatch/fixer-t", "t", True), ("dispatch/t", "t", True),
                              ("handoff/xt", "t", False), ("handoff/t-other", "t", False),
                              ("fix/t", "t", False), ("dispatch/fixer-xt", "t", False)):
        _check(f"topic {topic!r} {'matches' if want else 'skips'} {name}",
               topic_matches(name, topic) is want, results)


def _self_test_git(results: list) -> None:
    """The push arm and --topic against a throwaway bare remote (tests/throwaway_git.py)."""
    import os
    import tempfile
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
    from throwaway_git import throwaway_git_init, throwaway_git_env
    root = tempfile.mkdtemp(prefix="prune_refs_selftest.")
    origin, seat, bindir = (os.path.join(root, n) for n in ("origin.git", "seat", "bin"))
    throwaway_git_init(origin, "-q", "--bare")
    env = throwaway_git_init(seat, "-q", "-b", "main")
    os.makedirs(bindir)
    ghlog = os.path.join(root, "gh.log")

    def g(*a, check=True):
        r = subprocess.run(["git", *a], cwd=seat, env=env, capture_output=True, text=True)
        if check and r.returncode:
            raise RuntimeError(r.stderr)
        return r.stdout.strip()

    def runner(argv, **kw):
        runner.calls.append(list(argv))
        return subprocess.run(argv, cwd=seat, env=env, **kw)
    runner.calls = []

    def commit(fname, text, msg):
        with open(os.path.join(seat, fname), "w") as fh:
            fh.write(text)
        g("add", fname)
        g("commit", "-q", "-m", msg)
        return g("rev-parse", "HEAD")

    g("remote", "add", "origin", origin)
    base = commit("base", "0\n", "base")
    # same change twice, different commits: a branch tip not in main, but no '+' line
    g("checkout", "-q", "-b", "t-ok", base)
    ok_tip = commit("a", "1\n", "topic copy")
    g("checkout", "-q", "main")
    commit("a", "1\n", "main copy")
    g("checkout", "-q", "-b", "t-plus", base)
    plus_tip = commit("only-here", "x\n", "unique")
    g("checkout", "-q", "main")
    g("push", "-q", "origin", "main",
      f"{ok_tip}:refs/heads/handoff/t-ok", f"{ok_tip}:refs/heads/handoff-body/t-ok",
      f"{ok_tip}:refs/heads/dispatch/fixer-t-ok", f"{plus_tip}:refs/heads/handoff/t-plus",
      f"{plus_tip}:refs/heads/handoff-body/t-plus",
      f"{ok_tip}:refs/heads/handoff/t-open")
    for i in range(5):
        g("push", "-q", "origin", f"{base}:refs/heads/fix/n{i}")
    main_reach = set(g("rev-list", "main").split())

    def heads():
        return {ln.split()[1].split("refs/heads/", 1)[1]: ln.split()[0]
                for ln in g("ls-remote", "--heads", origin).splitlines()}

    with open(os.path.join(bindir, "gh"), "w") as fh:
        fh.write(f'#!/bin/sh\necho "$@" >> {ghlog}\nexit ${{GH_STUB_RC:-1}}\n')
    os.chmod(os.path.join(bindir, "gh"), 0o700)
    saved_path = os.environ["PATH"]
    os.environ["PATH"] = bindir + os.pathsep + saved_path

    def gh_calls():
        return len(open(ghlog).read().splitlines()) if os.path.exists(ghlog) else 0

    try:
        # --topic: a topic fully on main is archived, then deleted
        before = heads()
        topic_prs = {"handoff/t-open": {"open": [3]}}
        p = plan_topic(before, {}, "t-ok", "main", main_reach, runner)
        _check("topic on main: plans its handoff, body and dispatch refs, tags first",
               p["tags"] == 3 and p["deletes"] == 3 and
               [a[0] for a in p["actions"]] == ["tag"] * 3 + ["delete"] * 3, results)
        dry = apply_plan_push("origin", p["actions"], True, p["untagged"], git=runner)
        _check("a dry run writes nothing (remote refs unchanged, no push issued)",
               heads() == before and not any("push" in c for c in runner.calls)
               and all(v.startswith("would-") for v, _d in dry), results)
        done = apply_plan_push("origin", p["actions"], False, p["untagged"], chunk=2, git=runner)
        after = heads()
        _check("the topic's refs are gone after the push arm",
               not any(topic_matches(n, "t-ok") for n in after) and "main" in after, results)
        _check("every archive tag exists at the ref's own sha",
               all(remote_tags(origin).get(archive_tag(n)) == before[n]
                   for n in before if topic_matches(n, "t-ok")), results)
        pushes = [c for c in runner.calls if c[:2] == ["git", "push"] and "-q" in c]
        kinds = ["del" if "--delete" in c else "tag" for c in pushes]
        _check("chunk of 2: 2 tag pushes then 2 delete pushes, tags before deletes",
               kinds == ["tag", "tag", "del", "del"], results)
        _check("0 gh calls in the push arm (the gh stub fails on any call)",
               gh_calls() == 0 and all(not v.endswith("FAILED") for v, _d in done), results)
        _check("a handoff-body ref's own unique content is not a cherry refusal",
               not cherry_plus("main", ok_tip, runner)
               and plan_topic({"handoff/t-ok": ok_tip, "handoff-body/t-ok": plus_tip},
                              {}, "t-ok", "main", main_reach, runner)["deletes"] == 2,
               results)
        _check("a topic with a '+' cherry line is refused and nothing is touched",
               _refused(lambda: plan_topic(heads(), {}, "t-plus", "main", main_reach, runner),
                        "not on main") and heads() == after, results)
        _check("null: the refusal reads the cherry, not the name (t-ok passed above)",
               cherry_plus("main", plus_tip, runner) and not cherry_plus("main", ok_tip, runner),
               results)
        _check("a topic with an open PR is refused",
               _refused(lambda: plan_topic(heads(), topic_prs, "t-open", "main", main_reach,
                                           runner), "open pull request"), results)
        _check("a topic with no ref is refused",
               _refused(lambda: plan_topic(heads(), {}, "nope", "main", main_reach, runner),
                        "no ref"), results)

        # the push arm refuses a delete whose tag is missing, before any delete
        refs = heads()
        victim = "fix/n0"
        only_delete = [("delete", victim, refs[victim])]
        _check("a ref to delete lacking its archive tag refuses; nothing deleted",
               _refused(lambda: apply_plan_push("origin", only_delete, False, git=runner),
                        "lack their archive tag", ApplyRefused) and victim in heads(), results)
        _check("null: the same delete listed untagged by the plan proceeds",
               apply_plan_push("origin", only_delete, False, frozenset({victim}),
                               git=runner) == [("delete", victim)]
               and victim not in heads(), results)
        # a tag already on the remote at a DIFFERENT sha: the tag push is refused, abort
        g("push", "-q", "origin", f"{plus_tip}:refs/tags/archive/fix/n1")
        refs = heads()
        acts = [("tag", "archive/fix/n1", refs["fix/n1"]), ("tag", "archive/fix/n2", refs["fix/n2"]),
                ("delete", "fix/n1", refs["fix/n1"]), ("delete", "fix/n2", refs["fix/n2"])]
        out = apply_plan_push("origin", acts, False, chunk=1, git=runner)
        _check("the first refused tag push aborts: no later chunk, no delete",
               out[-1][0] == "tag-FAILED" and len(out) == 1
               and "fix/n1" in heads() and "fix/n2" in heads(), results)
        _check("main is never deletable by the push arm",
               _refused(lambda: apply_plan_push("origin", [("delete", "main", base)], False,
                                                git=runner), "never delete main", ApplyRefused),
               results)

        # null control: the api arm on the same-size plan makes 2N gh writes
        os.environ["GH_STUB_RC"] = "0"
        n = 4
        plan_n = [("tag", f"archive/q{i}", base) for i in range(n)] + \
                 [("delete", f"q{i}", base) for i in range(n)]
        start = gh_calls()
        apply_plan("o/r", plan_n, False)
        _check("null control: the gh-api arm makes 2N writes for N refs",
               gh_calls() - start == 2 * n, results)
        os.environ.pop("GH_STUB_RC")
    finally:
        os.environ["PATH"] = saved_path
        import shutil
        shutil.rmtree(root, ignore_errors=True)


def _refused(fn, needle: str, exc=ValueError) -> bool:
    try:
        fn()
    except exc as e:
        return needle in str(e)
    return False


def self_test() -> int:
    results: list = []
    main_sha = "m" * 40
    merged_sha = "a" * 40          # reachable from main
    orphan_sha = "b" * 40          # parentless, not reachable from main
    reachable = {main_sha, merged_sha}

    def prs(**kw):
        return kw

    # rule: main is always kept
    _check("main keeps", classify("main", main_sha, {}, reachable) == KEEP, results)
    # rule: a tip merged into main is deleted
    _check("merged into main deletes",
           classify("fix/x", merged_sha, {}, reachable) == DELETE_MERGED, results)
    # rule 3: an open pull request is kept
    p = {"fix/x": {"open": [9], "merged": [], "closed": []}}
    _check("open PR keeps", classify("fix/x", orphan_sha, p, reachable) == KEEP,
           results)
    # null control: an open PR on an OTHERWISE-merged ref is still kept
    p = {"fix/x": {"open": [9], "merged": [4], "closed": []}}
    _check("open PR keeps even when merged (null control)",
           classify("fix/x", merged_sha, p, reachable) == KEEP, results)
    # rule 2: an unmerged handoff ref whose PR merged is deleted
    p = {"handoff/x": {"open": [], "merged": [7], "closed": []}}
    _check("handoff whose PR merged deletes",
           classify("handoff/x", orphan_sha, p, reachable) == DELETE_HANDOFF_PR,
           results)
    # ...but a handoff ref whose PR merged AND whose tip is in main takes the
    # merged-into-main rule (same action, earlier rule -- order is asserted)
    _check("merged beats handoff-pr-merged",
           classify("handoff/x", merged_sha, p, reachable) == DELETE_MERGED,
           results)
    # residue: no pull request at all
    _check("no PR is residue",
           classify("verdict/1", orphan_sha, {}, reachable) == RESIDUE_NONE,
           results)
    # residue: a closed-unmerged pull request
    p = {"fix/y": {"open": [], "merged": [], "closed": [3]}}
    _check("closed-unmerged PR is residue",
           classify("fix/y", orphan_sha, p, reachable) == RESIDUE_CLOSED, results)
    # a handoff ref that is NOT merged and whose PR is open stays (rule 3 over 2)
    p = {"handoff/z": {"open": [5], "merged": [], "closed": []}}
    _check("open handoff ref keeps",
           classify("handoff/z", orphan_sha, p, reachable) == KEEP, results)

    # rule 2 via the roster: a handoff ref that is a DONE group's branch is
    # deleted even with no same-named pull request
    _check("handoff ref that is a done group's branch deletes",
           classify("handoff/r9-ux-money", orphan_sha, {}, reachable,
                    frozenset({"handoff/r9-ux-money"})) == DELETE_HANDOFF_PR,
           results)
    _check("...but an OPEN handoff group branch still keeps",
           classify("handoff/r9-ux-money", orphan_sha,
                    {"handoff/r9-ux-money": {"open": [2], "merged": [],
                                             "closed": []}}, reachable,
                    frozenset({"handoff/r9-ux-money"})) == KEEP, results)

    # archive tag naming
    _check("archive tag is the branch under archive/",
           archive_tag("handoff/audit-r9-fixplan") ==
           "archive/handoff/audit-r9-fixplan", results)
    _check("archive tag of a two-segment ref",
           archive_tag("verdict/2132") == "archive/verdict/2132", results)
    _check("family is the first segment",
           family_of("handoff-body/abc") == "handoff-body", results)

    # the planner: every tag precedes every delete
    refs = {"main": main_sha, "fix/x": merged_sha, "handoff/x": orphan_sha}
    prs = {"handoff/x": {"open": [], "merged": [7], "closed": []}}
    plan_all = plan(refs, prs, reachable, archive_scope="all",
                    keep_residue=False, verdicts_drained=True)
    verbs = [a[0] for a in plan_all["actions"]]
    _check("planner tags before deletes",
           verbs == sorted(verbs, key=lambda v: 0 if v == "tag" else 1)
           and "tag" in verbs and "delete" in verbs, results)
    _check("planner never acts on main",
           all(a[1] != "main" for a in plan_all["actions"]), results)

    # --archive-scope orphans skips a tag for a main-reachable tip
    plan_orphans = plan(refs, prs, reachable, archive_scope="orphans",
                        keep_residue=False, verdicts_drained=True)
    tagged = {a[1] for a in plan_orphans["actions"] if a[0] == "tag"}
    _check("orphans scope tags only unmerged tips",
           archive_tag("handoff/x") in tagged and
           archive_tag("fix/x") not in tagged, results)
    _check("orphans scope still deletes the already-merged tip",
           "fix/x" in {a[1] for a in plan_orphans["actions"]
                       if a[0] == "delete"}, results)

    # --archive-scope none deletes nothing (the unarchived tip is un-undoable)
    plan_none = plan(refs, prs, reachable, archive_scope="none",
                     keep_residue=False, verdicts_drained=True)
    _check("archive-scope none deletes nothing",
           not any(a[0] == "delete" for a in plan_none["actions"]), results)

    # --keep-residue keeps the residue
    refs2 = dict(refs, **{"verdict/1": orphan_sha})
    plan_keep = plan(refs2, prs, reachable, archive_scope="all",
                     keep_residue=True, verdicts_drained=True)
    _check("keep-residue keeps a no-PR ref",
           "verdict/1" not in {a[1] for a in plan_keep["actions"]}, results)

    # the ci-probe/ family: deletable unless an open PR has it as head
    _check("a ci-probe ref with no PR deletes",
           classify("ci-probe/a", orphan_sha, {}, reachable) == DELETE_CI_PROBE, results)
    _check("a ci-probe ref with a closed PR deletes",
           classify("ci-probe/a", orphan_sha, {"ci-probe/a": {"open": [], "merged": [], "closed": [4]}},
                    reachable) == DELETE_CI_PROBE, results)
    _check("null: a ci-probe ref that is an open PR's head keeps",
           classify("ci-probe/a", orphan_sha, {"ci-probe/a": {"open": [4], "merged": [], "closed": []}},
                    reachable) == KEEP, results)
    _check("null: a probe/ ref (cloud_relay's) is not the ci-probe family",
           classify("probe/a", orphan_sha, {}, reachable) == RESIDUE_NONE, results)
    plan_probe = plan({"ci-probe/a": orphan_sha, "ci-probe/b": orphan_sha}, {"ci-probe/b": {"open": [4]}},
                      reachable, archive_scope="all", keep_residue=True, verdicts_drained=False)
    _check("the planner deletes the closed probe ref untagged and keeps the open one, even with --keep-residue",
           plan_probe["actions"] == [("delete", "ci-probe/a", orphan_sha)], results)

    # refusal arm: a verdict ref not drained
    raised = False
    try:
        plan({"verdict/1": orphan_sha}, {}, reachable, archive_scope="all",
             keep_residue=False, verdicts_drained=False)
    except ValueError:
        raised = True
    _check("refuses an undrained verdict ref", raised, results)

    # refusal arm: main scheduled for anything is impossible -- a classifier
    # that changed would still be caught by the planner's guard.
    saved = globals()["classify"]
    globals()["classify"] = lambda *a, **k: DELETE_MERGED
    raised = False
    try:
        plan({"main": main_sha}, {}, reachable, archive_scope="all",
             keep_residue=False, verdicts_drained=True)
    except ValueError:
        raised = True
    finally:
        globals()["classify"] = saved
    _check("refuses a plan that would act on main", raised, results)

    # refusal arm (#2310): an archive tag naming a host path refuses the plan
    leaky = "wip-sync/Users-" + "exampleuser-x"
    raised = ""
    try:
        plan({leaky: orphan_sha}, {}, reachable, archive_scope="all",
             keep_residue=False, verdicts_drained=True)
    except ValueError as e:
        raised = str(e)
    _check("refuses an archive tag naming a host path, without echoing it",
           "#2310" in raised and leaky not in raised, results)
    _check("and plans the same tip under a clean name (the null control)",
           plan({"wip-sync/ext-x-0123abcd": orphan_sha}, {}, reachable, archive_scope="all",
                keep_residue=False, verdicts_drained=True)["tags"] == 1, results)

    _self_test_keeps(results)
    _self_test_git(results)

    passed = sum(1 for _t, ok in results if ok)
    for tag, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {tag}")
    print(f"SELF-TEST {'PASS' if passed == len(results) else 'FAIL'} "
          f"({passed} checks)")
    return 0 if passed == len(results) else 1


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default="tvofi/heatpump_optimizer")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--main", default="origin/main")
    ap.add_argument("--refs-file", default="")
    ap.add_argument("--prs-file", default="")
    ap.add_argument("--roster-file", default="",
                    help="the round-9 roster JSON, so rule 2 sees a done "
                         "group's branch as a merged pull request")
    ap.add_argument("--via", choices=("push", "api"), default="push",
                    help="write by batched `git push` (no API call) or one "
                         "REST write per tag and per delete")
    ap.add_argument("--topic", default="",
                    help="restrict to one topic's refs; refused whole when "
                         "its content is not on main or it has an open PR")
    ap.add_argument("--prs-limit", type=int, default=3000)
    ap.add_argument("--archive-scope", choices=("all", "orphans", "none"),
                    default="all")
    ap.add_argument("--keep-residue", action="store_true")
    ap.add_argument("--verdicts-drained", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    refs = (read_refs_file(args.refs_file) if args.refs_file
            else live_refs(args.remote))
    prs_list = (read_prs_file(args.prs_file) if args.prs_file
                else live_prs(args.repo, args.prs_limit))
    main_reachable = refs_reachable_from_main(args.main)
    done_branches = (done_group_branches(args.roster_file)
                     if args.roster_file else frozenset())
    open_groups = (open_group_ids(args.roster_file)
                   if args.roster_file else frozenset())
    ages = (None if args.refs_file
            else tip_ages(refs.values(), time.time()))
    try:
        if args.topic:
            p = plan_topic(refs, index_prs(prs_list), args.topic, args.main,
                           main_reachable)
        else:
            p = plan(refs, index_prs(prs_list), main_reachable,
                     archive_scope=args.archive_scope,
                     keep_residue=args.keep_residue,
                     verdicts_drained=args.verdicts_drained,
                     done_branches=done_branches, open_groups=open_groups,
                     ages=ages)
    except ValueError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({
            "rows": [{"ref": n, "sha": s, "family": f, "rule": r,
                      "action": a} for n, s, f, r, a in p["rows"]],
            "tags": p["tags"], "deletes": p["deletes"],
            "actions": [{"verb": v, "arg": a, "sha": s}
                        for v, a, s in p["actions"]]}, indent=1))
    else:
        for n, s, f, r, a in p["rows"]:
            print(f"{a:14} {r:26} {f:12} {n}@{s[:12]}")
        print(f"\n{len(refs)} ref(s); {p['tags']} tag(s); "
              f"{p['deletes']} deletion(s)")
        print("the citation sweep (brief_lint) is a PREREQUISITE of these "
              "deletions; a brief citing a deleted ref breaks the linter")

    try:
        if args.via == "push":
            done = apply_plan_push(args.remote, p["actions"],
                                   dry_run=not args.apply,
                                   untagged=p["untagged"])
        else:
            done = apply_plan(args.repo, p["actions"], dry_run=not args.apply)
    except ApplyRefused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    if not args.json:
        for verb, detail in done:
            print(f"  {verb:14} {detail}")
    return 1 if any(v.endswith("FAILED") for v, _d in done) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

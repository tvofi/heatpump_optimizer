#!/usr/bin/env python3
"""prune_refs.py — reconcile the remote branch refs down to main plus a few
development branches, archive-as-tags first, and never touch one a rule keeps.

    python3 tools/audit/seat/prune_refs.py [--repo OWNER/REPO] [--main main]
        [--refs-file FILE] [--prs-file FILE]
        [--archive-scope {all,orphans}] [--keep-residue]
        [--verdicts-drained] [--apply]
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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ref_privacy  # noqa: E402  an archive tag never names this host (#2310)

SELF = "tools/audit/seat/prune_refs.py"
ARCHIVE_PREFIX = "archive/"
HANDOFF_PREFIX = "handoff/"
VERDICT_PREFIX = "verdict/"
MAIN_REF = "main"

# Every rule label the classifier can return, and the action each maps to.
KEEP = "keep"
DELETE_MERGED = "delete-merged-into-main"
DELETE_HANDOFF_PR = "delete-handoff-pr-merged"
RESIDUE_CLOSED = "residue-closed-pr"
RESIDUE_NONE = "residue-no-pr"

_KEEP_RULES = {KEEP}
_DELETE_RULES = {DELETE_MERGED, DELETE_HANDOFF_PR}
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


def classify(name: str, sha: str, prs: dict, main_reachable: set,
             done_branches: frozenset = frozenset()) -> str:
    """The rule that settles one ref. Order is the precedence, not a detail.

    `main` first, then an open pull request (the keep that dominates), then a
    tip already merged into main, then a handoff ref whose pull request
    merged, then the residue.

    "whose pull request MERGED" has two evidence sources: a same-named pull
    request that merged (a seat that opened the PR from the handoff ref), and
    the ref being the branch of a roster group the roster records as done --
    the head that merged superseded it even when the PR rode another branch.
    `done_branches` carries the second, from `--roster-file`.
    """
    if name == MAIN_REF:
        return KEEP
    slot = prs.get(name) or {}
    if slot.get("open"):
        return KEEP
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
         done_branches: frozenset = frozenset()) -> dict:
    """The ordered action list for a ref set, or raise on a refused plan.

    Returns {"rows": [(name, sha, family, rule, action)], "actions":
    [(verb, arg, sha)]} where verb is "tag" or "delete". Raises ValueError when
    a plan would touch `main` or a `verdict/*` ref that has not drained.
    """
    rows = []
    for name in sorted(refs):
        rule = classify(name, refs[name], prs, main_reachable, done_branches)
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

    tags, deletes = [], []
    for name, sha, _fam, _rule, action in rows:
        if action != "archive-delete":
            continue
        # A deletion is safe only once its tip is preserved: as a tag (all /
        # orphans) or because the tip already lives in main. `none` archives
        # nothing and therefore deletes nothing -- it is the preview arm.
        if archive_scope == "none":
            continue
        if archive_scope == "all" or sha not in main_reachable:
            # A tag is permanent: one naming this host is refused, plan and all,
            # before anything is written (#2310). The name is not echoed.
            why = ref_privacy.refusal(archive_tag(name))
            if why:
                raise ValueError(f"refusing to archive the tip {sha[:12]}: {why} would publish this host "
                                 f"(#2310); rename or remove that branch by hand")
            tags.append(("tag", archive_tag(name), sha))
        deletes.append(("delete", name, sha))
    # THE ORDER IS THE SAFETY: every tag before every delete, so a deletion
    # can never precede the tag that preserves its tip.
    actions = tags + deletes
    return {"rows": rows, "actions": actions, "tags": len(tags),
            "deletes": len(deletes)}


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


# ---------------------------------------------------------------------------
# self-test: the classifier, the planner, the precedence and the order.

def _check(tag: str, cond: bool, results: list) -> None:
    results.append((tag, bool(cond)))


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
    try:
        p = plan(refs, index_prs(prs_list), main_reachable,
                 archive_scope=args.archive_scope, keep_residue=args.keep_residue,
                 verdicts_drained=args.verdicts_drained,
                 done_branches=done_branches)
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

    done = apply_plan(args.repo, p["actions"], dry_run=not args.apply)
    if not args.json:
        for verb, detail in done:
            print(f"  {verb:14} {detail}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

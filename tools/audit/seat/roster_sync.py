#!/usr/bin/env python3
"""The roster-sync reconciler: derive the factual half of `resume` from the repository.

    python3 tools/audit/seat/roster_sync.py [--repo OWNER/REPO] [--checkout DIR]
        [--roster-ref GITREF | --roster-file PATH] [--roster-path PATH]
        [--branch BR] [--pr-state FILE] [--limit N] [--worktree DIR]
        [--lint-cwd DIR] [--message MSG] [--apply]
    python3 tools/audit/seat/roster_sync.py --self-test

WHY. `resume.stage` is a human claim and nothing compared it with the refs:
twelve complete handoffs sat unopened for up to 96 h while the roster recorded
stale stages. This step is that comparison, run every pass by
`state_docs.py beat --apply`, and it derives only what a read measures:

  MERGED   a group whose branch answers for a merged pull request is `done` at
           that merge commit (`resume.commit`); a merge first observed in this
           pass also has its body's `Carry: <GROUP>` items appended to the
           destination group's `carry` array.
  OPEN     a group whose branch answers for an open pull request is
           `in-progress`, with the number in `resume.pr`.
  no PR    a branch with no open or merged pull request makes no change:
           absence is not evidence, and a closed-unmerged PR is no evidence
           either.

It never overwrites a human disposition. Only a stage in DERIVABLE_STAGES is
rewritten; every other stage -- `deferred`, `refused`, `refuted`, `absorbed`,
`rca-done`, and any wording a later roster introduces -- is left alone and
printed as skipped. The self-test refuses a stage the tree's rosters carry
that neither tuple classifies, so a new wording is classified deliberately.

BRANCH MATCHING is the design's rule (`dev/audit/machinery`, 6.4): the topic
is the basename of `resume.branch` (else the lowercased group id), and a
pull request's head matches when its name, minus a `handoff-body/`, `handoff/`
or `fix/` prefix and a trailing `-pr`, equals the topic or starts with
`<topic>-`. An exact-name rule finds 2 of the live roster's 48 merged groups;
this one finds 47, because a group's PR rides `fix/<topic>` or `<topic>-pr`.

THE WRITE PATH is `roster_edit.py`'s, not a second one: its ops, its
load-validate-dump (`dump`) and its lint gate, through the one
`commit_roster()` both callers use. A dry run is the default; `--apply`
writes. `--roster-file` is a read-only source: a file has no branch to push,
so `--apply` with it is refused.

OFFLINE. `--pr-state FILE` replaces the `gh pr list` read with recorded output
(the same shape: `number`, `state`, `headRefName`, `mergeCommit`), so the
self-test reaches no network. An unreadable read -- gh failing, a malformed
row, a missing file -- is `UNREADABLE` and a refusal, never "no mismatches".
The `gh` window is bounded by --limit and says when it is full: a pull request
older than the window is not measured, and the rule above leaves the group
unchanged rather than guessing.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

SELF = "tools/audit/seat/roster_sync.py"
SEAT = Path(__file__).resolve().parent
sys.path.insert(0, str(SEAT))
sys.path.insert(0, str(SEAT.parent))
import carry_audit  # noqa: E402  the one `Carry:` parser; a second is refused
import ref_privacy  # noqa: E402  a ref or message never names this host (#2310)
import roster_edit  # noqa: E402  the one write path: dump, commit, lint gate
import roster_lib  # noqa: E402  which roster, and what a done stage is

#: The stages a repository measurement may rewrite: the factual working
#: states. A stage outside this tuple is a human disposition and is never
#: overwritten -- the rule that keeps `deferred` and `refused` intact.
DERIVABLE_STAGES = ("not-started", "planned", "queued", "in-progress",
                    "in-flight", "fixing", "handoff", "done")
#: The human dispositions, named so a skip can say which rule protected it.
#: Not exhaustive by design: anything unclassified is protected too, and the
#: self-test refuses a roster stage this tuple and DERIVABLE_STAGES together
#: do not cover. `deferred` and `refuted` are the tree's own rosters' words;
#: `refused`, `absorbed` and `rca-done` are the orchestrator's and design 6.4's.
PROTECTED_STAGES = ("deferred", "refused", "refuted", "absorbed", "rca-done")
#: The branch prefixes a topic is read past, and the suffix a pull-request
#: branch adds (design 6.4's B13 rule).
PREFIXES = ("handoff-body/", "handoff/", "fix/")
PR_SUFFIX = "-pr"
OPEN, MERGED, CLOSED = "OPEN", "MERGED", "CLOSED"
DEFAULT_LIMIT = 1000
SHA_RE = re.compile(r"\A[0-9a-f]{7,40}\Z")
#: A carry item is prose in the roster's array; the parser returns it as a
#: bullet, so the marker is dropped and the item's own words are kept.
BULLET = re.compile(r"\A\s*(?:[-*+]|\d+[.)])\s+")


class Refuse(Exception):
    """A guard refusal with its reason; the caller prints it, fail-closed."""


def run(cmd, cwd=None, input_text=None) -> str:
    r = subprocess.run(cmd, cwd=cwd, input=input_text, capture_output=True,
                       text=True)
    if r.returncode != 0:
        raise Refuse(f"{' '.join(cmd)} (in {cwd or '.'}) failed: "
                     f"{(r.stderr or r.stdout).strip()[:300]}")
    return r.stdout


# ------------------------------------------------------------------- the read
class PR(NamedTuple):
    number: int
    state: str
    head: str
    merge_commit: str | None
    body: str | None


def normalize_pr(row, where: str) -> PR:
    """One pull-request row of the gh shape. A row that does not read is a
    refusal: a silently dropped row is a merge this pass would not see."""
    if not isinstance(row, dict):
        raise Refuse(f"UNREADABLE {where}: not an object")
    try:
        number = int(row["number"])
    except (KeyError, TypeError, ValueError):
        raise Refuse(f"UNREADABLE {where}: no integer number")
    state = str(row.get("state") or "").upper()
    if state not in (OPEN, MERGED, CLOSED):
        raise Refuse(f"UNREADABLE {where} (#{number}): state {state!r}")
    head = row.get("headRefName") or row.get("head") or ""
    if not isinstance(head, str) or not head:
        raise Refuse(f"UNREADABLE {where} (#{number}): no head branch")
    mc = row.get("mergeCommit")
    if isinstance(mc, dict):
        mc = mc.get("oid")
    if mc is None:
        mc = row.get("merge_commit")
    if mc is not None and not SHA_RE.match(str(mc)):
        raise Refuse(f"UNREADABLE {where} (#{number}): merge commit {mc!r}")
    body = row.get("body")
    return PR(number, state, head, None if mc is None else str(mc), body)


def load_prs(repo: str, pr_state: str | None, limit: int) -> tuple[list[PR], str]:
    """Every pull request the read returns, and the line saying what was read.

    Fail-closed (design B11): a failed `gh`, an unparseable fixture or a
    malformed row refuses the pass rather than reporting "no mismatches".
    """
    if pr_state:
        try:
            rows = json.loads(Path(pr_state).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise Refuse(f"UNREADABLE --pr-state {pr_state}: {e}")
        if not isinstance(rows, list):
            raise Refuse(f"UNREADABLE --pr-state {pr_state}: not a list")
        note = f"pull requests: {len(rows)} read offline from --pr-state"
    else:
        r = subprocess.run(
            ["gh", "pr", "list", "--repo", repo, "--state", "all", "--limit",
             str(limit), "--json", "number,state,headRefName,mergeCommit"],
            capture_output=True, text=True)
        if r.returncode:
            raise Refuse(f"UNREADABLE gh pr list ({repo}): "
                         f"{(r.stderr or r.stdout).strip()[:300]}")
        try:
            rows = json.loads(r.stdout)
        except ValueError as e:
            raise Refuse(f"UNREADABLE gh pr list ({repo}): {e}")
        note = f"pull requests: {len(rows)} read from {repo} (--limit {limit})"
        if len(rows) >= limit:
            note += ("; WINDOW FULL: older pull requests are not measured, so "
                     "a branch whose pull request predates it makes no change")
    return [normalize_pr(r, f"row {i}") for i, r in enumerate(rows)], note


def pr_body(pr: PR, repo: str, pr_state: str | None) -> str:
    """The merged pull request's body: in the fixture when it carries one,
    else one targeted read. A failed read refuses the pass."""
    if pr.body is not None:
        return pr.body
    r = subprocess.run(["gh", "api", f"repos/{repo}/pulls/{pr.number}",
                        "--jq", ".body"], capture_output=True, text=True)
    if r.returncode:
        raise Refuse(f"UNREADABLE gh api pulls/{pr.number}: "
                     f"{(r.stderr or r.stdout).strip()[:300]}")
    return r.stdout


# --------------------------------------------------------------- the derive
def norm_head(name: str) -> str:
    """A pull request's head branch as the topic it answers for: one working
    prefix off, one `-pr` suffix off (design 6.4's B13 rule)."""
    for prefix in PREFIXES:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    if name.endswith(PR_SUFFIX):
        name = name[:-len(PR_SUFFIX)]
    return name


def topic_of(group: dict) -> str:
    """The topic a group's work is named after: `resume.branch`'s basename,
    else the lowercased group id -- the design's rule, both arms."""
    branch = (group.get("resume") or {}).get("branch")
    if branch:
        return branch.rstrip("/").rsplit("/", 1)[-1]
    return str(group.get("group") or "").lower()


def matches(roster: dict, prs: list[PR]) -> dict[str, list[PR]]:
    """group id -> the pull requests whose normalized head answers for it."""
    by_topic: dict[str, list[PR]] = {}
    for pr in prs:
        by_topic.setdefault(norm_head(pr.head), []).append(pr)
    out: dict[str, list[PR]] = {}
    for g in roster.get("groups", []):
        topic = topic_of(g)
        if not topic:
            continue
        hits = [pr for name, prs_ in by_topic.items()
                for pr in prs_ if name == topic or name.startswith(topic + "-")]
        out[g["group"]] = sorted(hits, key=lambda p: p.number)
    return out


def chosen(hits: list[PR]) -> PR | None:
    """The pull request that decides a group's stage: an open one wins (work
    is in flight), else the newest merged one; a closed-unmerged PR decides
    nothing."""
    opened = [p for p in hits if p.state == OPEN]
    if opened:
        return max(opened, key=lambda p: p.number)
    merged = [p for p in hits if p.state == MERGED]
    return max(merged, key=lambda p: p.number) if merged else None


class Change(NamedTuple):
    group: str
    stage: str
    pr: int
    merge_commit: str | None
    was: str | None
    state: str


def derive(roster: dict, prs: list[PR]) -> tuple[list[Change], list[tuple], list[PR]]:
    """(changes, skips, transitions): the stage writes a read supports, the
    groups a human disposition protected, and the merged pull requests whose
    group moves to done in this pass -- the only bodies read for `Carry:`."""
    by_group = matches(roster, prs)
    changes: list[Change] = []
    skips: list[tuple] = []
    transitions: list[PR] = []
    for g in roster.get("groups", []):
        gid = g["group"]
        resume = g.get("resume") or {}
        stage = resume.get("stage")
        pr = chosen(by_group.get(gid) or [])
        if pr is None:
            continue
        if stage not in DERIVABLE_STAGES:
            skips.append((gid, stage, pr))
            continue
        if pr.state == OPEN:
            if stage != "in-progress" or resume.get("pr") != pr.number:
                changes.append(Change(gid, "in-progress", pr.number, None, stage,
                                      pr.state))
            continue
        if not pr.merge_commit:
            skips.append((gid, stage, pr, "the merge carries no commit"))
            continue
        # A transition only: a group already done is a settled record, and its
        # commit is not re-recorded (the tick checks a done commit is in main;
        # a pull request's head is, once merged).
        if stage != "done":
            changes.append(Change(gid, "done", pr.number, pr.merge_commit,
                                  stage, pr.state))
            transitions.append(pr)
    return changes, skips, transitions


def carry_plan(roster: dict, transitions: list[PR], repo: str,
               pr_state: str | None) -> tuple[list[tuple], list[tuple]]:
    """(appends, refusals) from a merged body's `Carry: <GROUP>` items.

    The parser is `carry_audit.py`'s (`audit`, hence `items` and `carry_dests`);
    a second one is refused. Only a group token is appended -- an issue, an
    O-brief and a dismissal keep their own record -- and a destination that
    is done is refused, never appended.
    """
    groups = roster_lib.groups_of(roster)
    appends: list[tuple] = []
    refusals: list[tuple] = []
    for pr in transitions:
        result = carry_audit.audit(pr_body(pr, repo, pr_state), [],
                                   carry_audit.Dests(roster, set()))
        for row in result["rows"]:
            for dest in row["dests"]:
                if not carry_audit.GROUP_TOK.match(dest):
                    continue
                g = groups.get(dest)
                if g is None:
                    refusals.append((pr.number, dest, "not a roster group"))
                elif not roster_lib.is_open(g):
                    refusals.append((pr.number, dest,
                                     "the destination is done (resume.stage "
                                     f"{(g.get('resume') or {}).get('stage')})"))
                else:
                    text = " ".join(BULLET.sub("", row["text"], count=1).split())
                    if text in (g.get("carry") or []) or (dest, text) in appends:
                        continue
                    appends.append((dest, text))
    return appends, refusals


def apply_plan(roster: dict, changes: list[Change], appends: list[tuple]) -> None:
    """The derived ops, through roster_edit's own op functions."""
    for c in changes:
        roster_edit.op_set_stage(roster, c.group, c.stage, c.merge_commit)
        if c.stage == "in-progress":
            # The open pull request's number is the one the ask records; a
            # done group's record is its merge commit.
            roster_lib.groups_of(roster)[c.group].setdefault("resume", {})["pr"] = c.pr
    for dest, text in appends:
        roster_edit.op_append_carry(roster, dest, text)


# ------------------------------------------------------------------ the flow
def branch_base(checkout: str, roster_ref: str | None) -> str:
    """`--roster-ref` reduced to a branch name: `origin/<b>` and
    `refs/remotes/origin/<b>` become `<b>`, so a base never doubles a remote."""
    name = roster_ref or "main"
    if name.startswith("refs/remotes/"):
        name = name[len("refs/remotes/"):]
    remotes = run(["git", "-C", checkout, "remote"]).split()
    if "/" in name:
        first, rest = name.split("/", 1)
        if first in remotes and rest:
            return rest
    return name


def target(checkout: str, roster_ref: str | None, branch: str | None,
           roster_path: str | None) -> tuple[str, str]:
    """(base ref, write branch). The write branch is --branch, else the round's
    roster branch -- never the base, so a sync never lands on main."""
    ref = branch_base(checkout, roster_ref)
    base = roster_ref or ("origin/main" if ref == "main" else f"origin/{ref}")
    try:
        rel = roster_lib.roster_path(checkout, base, roster_path)
    except roster_lib.RosterNotFound as e:
        raise Refuse(str(e))
    return ref, branch or roster_lib.round_branch(rel)


def has_ref(checkout: str, ref: str) -> bool:
    return subprocess.run(["git", "-C", checkout, "rev-parse", "--verify",
                           "--quiet", ref + "^{commit}"],
                          capture_output=True).returncode == 0


def sync(a) -> int:
    """One pass: derive, print every change, write only with --apply."""
    try:
        if a.roster_file and a.apply:
            raise Refuse("--roster-file is a read-only source: a file has no "
                         "branch to push; give --roster-ref to write")
        prs, note = load_prs(a.repo, a.pr_state, a.limit)
        print(f"roster_sync: {note}")
        roster_edit.fetch_origin(a.checkout)
        ref, branch = target(a.checkout, a.roster_ref, a.branch, a.roster_path)
        msg = a.message or (f"roster_sync: derive stages from pull requests "
                            f"({SELF})")
        why = ref_privacy.refusal(branch, (("the message", msg),))
        if why:
            raise Refuse(f"{why} would publish this host (#2310); nothing written")
        base = (f"origin/{branch}" if has_ref(a.checkout, f"origin/{branch}")
                else f"origin/{ref}")
        rel = roster_lib.roster_path(a.checkout, base, a.roster_path)
        roster = json.loads(run(["git", "-C", a.checkout, "show",
                                 f"{base}:{rel}"]))
        changes, skips, transitions = derive(roster, prs)
        # The carries are judged against the roster this pass will write: a
        # destination this pass makes done refuses the carry, and the stage
        # writes are applied in memory first on a copy.
        projected = copy.deepcopy(roster)
        apply_plan(projected, changes, [])
        appends, refusals = carry_plan(projected, transitions, a.repo,
                                       a.pr_state)
        for c in changes:
            if c.was == c.stage:
                print(f"roster_sync: {c.group}: record PR #{c.pr} for stage "
                      f"{c.stage}")
            else:
                print(f"roster_sync: {c.group}: stage {c.was} -> {c.stage}"
                      + (f" at {c.merge_commit[:12]}" if c.merge_commit else "")
                      + f" (PR #{c.pr} {c.state})")
        for s in skips:
            why = s[3] if len(s) > 3 else "a human disposition"
            print(f"roster_sync: SKIP {s[0]}: stage {s[1]} is {why} "
                  f"(PR #{s[2].number} {s[2].state}); left alone")
        for dest, text in appends:
            print(f"roster_sync: carry {dest} += {text[:100]!r}")
        for number, dest, why in refusals:
            print(f"roster_sync: REFUSED Carry: {dest} from #{number}: {why}")
        if not changes and not appends:
            print(f"roster_sync: no derived change on {branch}; nothing written")
            return 0
        if not a.apply:
            print(f"roster_sync: dry run: {len(changes)} stage change(s), "
                  f"{len(appends)} carry append(s) would be written to {branch} "
                  "(no --apply)")
            return 0
        parent = None
        made = a.worktree
        if not made:
            parent = Path(tempfile.mkdtemp(prefix="hpo-roster-sync-"))
            made = str(parent / "wt")
        try:
            roster_edit.prepare_worktree(a.checkout, ref, branch, made)
            rel = roster_lib.roster_path(made, None, a.roster_path)
            roster = json.loads((Path(made) / rel).read_text(encoding="utf-8"))
            # Re-derive on the bytes this write path is about to replace, so
            # the edit is computed from the file it lands in, never an older read.
            changes, _, transitions = derive(roster, prs)
            projected = copy.deepcopy(roster)
            apply_plan(projected, changes, [])
            appends, _ = carry_plan(projected, transitions, a.repo, a.pr_state)
            if not changes and not appends:
                print(f"roster_sync: {branch} already carries these; "
                      "nothing written")
                return 0
            apply_plan(roster, changes, appends)
            rc = roster_edit.commit_roster(
                a.checkout, made, rel, roster, msg, True, branch, a.lint_cwd,
                label=(f"roster_sync ({len(changes)} stage, "
                       f"{len(appends)} carry)"))
            if rc == 3:
                # Leave no unpushed commit on the branch: a later pass would
                # otherwise refuse the worktree it finds (unpushed commits).
                run(["git", "-C", made, "reset", "-q", "--hard", base])
            return rc
        finally:
            if parent is not None:
                subprocess.run(["git", "-C", a.checkout, "worktree", "remove",
                                "--force", made], capture_output=True)
                shutil.rmtree(parent, ignore_errors=True)
    except Refuse as e:
        print(f"roster_sync: REFUSED: {e}", file=sys.stderr)
        return 2


# --------------------------------------------------------------------- main
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--repo", default="tvofi/heatpump_optimizer")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--roster-ref", default=None,
                     help="the base ref (default main)")
    src.add_argument("--roster-file",
                     help="a roster file to READ; --apply needs --roster-ref")
    p.add_argument("--roster-path", default=None,
                   help="the roster file, repo-relative (default: the newest "
                        "dev/programme/rosters/wave-r<N>-groups.json)")
    p.add_argument("--branch", default=None,
                   help="the branch the sync lands on (default: the round's "
                        "roster branch)")
    p.add_argument("--checkout", default=".",
                   help="the clone the git operations run in")
    p.add_argument("--pr-state",
                   help="JSON list of pull requests; replaces the gh read "
                        "(no network)")
    p.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                   help=f"the gh pr list window (default {DEFAULT_LIMIT})")
    p.add_argument("--worktree", help="the worktree the write uses")
    p.add_argument("--lint-cwd", help="a fresh origin/main checkout to lint from")
    p.add_argument("--message", help="the commit message")
    p.add_argument("--apply", action="store_true",
                   help="write the derived changes; without it this is a dry run")
    p.add_argument("--self-test", action="store_true")
    return p


def main(argv=None) -> int:
    a = parser().parse_args(sys.argv[1:] if argv is None else argv)
    if a.self_test:
        return run_self_test()
    return sync(a)


def run_self_test() -> int:
    """The self-test under the throwaway-git environment, so every git call
    the ops make inherits a fixed identity and no inherited GIT_DIR."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
    from throwaway_git import throwaway_git_environ
    with throwaway_git_environ():
        return self_test()


# ---------------------------------------------------------------- self-test
def self_test() -> int:
    """Offline: a fixture repository, recorded gh-shaped rows, no network."""
    import contextlib
    import io
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
    from throwaway_git import throwaway_git_clone, throwaway_git_init

    fails: list[str] = []
    n = [0]

    def check(name: str, ok, got="") -> None:
        n[0] += 1
        if not ok:
            fails.append(f"{name} (got: {got})")

    def git(*args, cwd=None, env=None, input_text=None) -> str:
        return run(["git", *args], cwd=cwd, input_text=input_text).strip()

    LINT_OK = ("console.log('TOTAL: 0 error(s) across 1 file(s)');\n")
    LINT_BAD = ("console.log('TOTAL: 1 error(s) across 1 file(s)');\n")
    ROSTER = f"{roster_lib.ROSTERS_DIR}/wave-r9-groups.json"

    def build(tmp: Path, lint_src: str) -> tuple[Path, Path, Path]:
        """(bare origin, driver clone, fixture roster path at the driver)."""
        tmp.mkdir(parents=True, exist_ok=True)
        seed = tmp / "seed"
        seed.mkdir()
        (seed / ".claude" / "workflows").mkdir(parents=True)
        (seed / ".claude/workflows/brief_lint.mjs").write_text(lint_src,
                                                               encoding="utf-8")
        (seed / ROSTER).parent.mkdir(parents=True, exist_ok=True)
        (seed / ROSTER).write_text(roster_edit.dump(ROSTER_FIXTURE),
                                   encoding="utf-8")
        throwaway_git_init(seed, "-q", "-b", "main")
        git("-C", str(seed), "add", "-A")
        git("-C", str(seed), "commit", "-q", "-m", "fixture roster")
        bare = tmp / "origin.git"
        throwaway_git_clone(seed, bare, "-q", "--bare")
        drv = tmp / "drv"
        throwaway_git_clone(bare, drv, "-q")
        return bare, drv, drv / ROSTER

    def roster_at(bare: Path, branch: str) -> dict:
        return json.loads(git("-C", str(bare), "show", f"{branch}:{ROSTER}"))

    def branches(bare: Path) -> str:
        return git("-C", str(bare), "for-each-ref", "--format=%(refname)",
                   "refs/heads/")

    def calls(drv: Path, state: Path, *extra) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = main(["--checkout", str(drv), "--repo", "fixture/roster",
                       "--pr-state", str(state), *extra])
        return rc, out.getvalue(), err.getvalue()

    groups = [
        {"group": "R9-LIVE", "lane": "L1", "issues": [], "fixes": [],
         "after": [], "brief": "live",
         "resume": {"stage": "not-started", "branch": "handoff/r9-live"}},
        {"group": "R9-OPEN", "lane": "L1", "issues": [], "fixes": [],
         "after": [], "brief": "open",
         "resume": {"stage": "queued", "branch": "handoff/r9-open"}},
        {"group": "R9-DEFER", "lane": "L1", "issues": [], "fixes": [],
         "after": [], "brief": "deferred",
         "resume": {"stage": "deferred", "branch": "handoff/r9-defer"}},
        {"group": "R9-DONE", "lane": "L1", "issues": [], "fixes": [],
         "after": [], "brief": "done",
         "resume": {"stage": "done", "branch": "handoff/r9-done",
                    "commit": "b" * 40}},
        {"group": "R9-CARRY", "lane": "L1", "issues": [], "fixes": [],
         "after": [], "brief": "carry",
         "resume": {"stage": "in-progress", "branch": "handoff/r9-carry"}},
        {"group": "R9-DEST", "lane": "L1", "issues": [], "fixes": [],
         "after": [], "brief": "destination",
         "resume": {"stage": "not-started"}},
        {"group": "R9-OVER", "lane": "L1", "issues": [], "fixes": [],
         "after": [], "brief": "over",
         "resume": {"stage": "done"}},
        {"group": "R9-NOPR", "lane": "L1", "issues": [], "fixes": [],
         "after": [], "brief": "no pr",
         "resume": {"stage": "not-started", "branch": "handoff/r9-nopr"}},
        {"group": "R9-PREFIX", "lane": "L1", "issues": [], "fixes": [],
         "after": [], "brief": "prefix",
         "resume": {"stage": "not-started", "branch": "handoff/r9-pre"}},
    ]
    ROSTER_FIXTURE = {"repo": "fixture/roster", "session": "r9-sync",
                      "groups": groups}
    BODY = ("## Friction\n\n"
            "- the widget parser drops a unit. Carry: R9-DEST\n\n"
            "- a quoted example `Carry: R9-DEST` in a code span routes nothing.\n\n"
            "- a real finding for a done group. Carry: R9-OVER\n")
    PRS = [
        {"number": 11, "state": "MERGED", "headRefName": "fix/r9-live-pr",
         "mergeCommit": {"oid": "a" * 40}, "body": "## Friction\n\n- none\n"},
        {"number": 12, "state": "OPEN", "headRefName": "handoff/r9-open"},
        {"number": 13, "state": "MERGED", "headRefName": "handoff/r9-defer",
         "mergeCommit": {"oid": "c" * 40}, "body": "## Friction\n\n- none\n"},
        {"number": 14, "state": "MERGED", "headRefName": "handoff/r9-done",
         "mergeCommit": {"oid": "d" * 40}},
        {"number": 15, "state": "MERGED", "headRefName": "handoff/r9-carry",
         "mergeCommit": {"oid": "e" * 40}, "body": BODY},
        {"number": 16, "state": "CLOSED", "headRefName": "handoff/r9-nopr"},
        {"number": 17, "state": "OPEN", "headRefName": "handoff/r9-prefix"},
    ]
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        bare, drv, _ = build(root / "one", LINT_OK)
        state = root / "prs.json"
        state.write_text(json.dumps(PRS), encoding="utf-8")
        branch = "handoff/audit-r9-roster"
        # NULL CONTROL 1: a dry run writes nothing and creates no branch.
        rc, out, err = calls(drv, state)
        check("dry run rc 0", rc == 0, (rc, err))
        check("dry run creates no roster branch (no --apply writes nothing)",
              branch not in branches(bare), branches(bare))
        check("the dry run prints each change it would make",
              "R9-LIVE: stage not-started -> done at " + "a" * 12 in out
              and "R9-OPEN: stage queued -> in-progress (PR #12 OPEN)" in out,
              out)
        check("the dry run names the carry append",
              "carry R9-DEST +=" in out, out)
        check("the dry run refuses the done destination",
              "REFUSED Carry: R9-OVER from #15" in out
              and "the destination is done" in out, out)
        check("the dry run says the human disposition is left alone",
              "SKIP R9-DEFER: stage deferred is a human disposition" in out, out)

        # APPLY: the derived stages, the merge commit, the carry, and nothing
        # for a branch without a deciding pull request.
        rc, out, err = calls(drv, state, "--apply")
        check("apply rc 0", rc == 0, (rc, out, err))
        check("apply pushes once", branches(bare).count(branch) == 1,
              branches(bare))
        r = roster_at(bare, branch)
        by = roster_lib.groups_of(r)
        check("merged PR: stage done at its merge commit",
              by["R9-LIVE"]["resume"]["stage"] == "done"
              and by["R9-LIVE"]["resume"].get("commit") == "a" * 40
              and "pr" not in by["R9-LIVE"]["resume"],
              by["R9-LIVE"]["resume"])
        check("open PR: stage in-progress with its number",
              by["R9-OPEN"]["resume"]["stage"] == "in-progress"
              and by["R9-OPEN"]["resume"].get("pr") == 12,
              by["R9-OPEN"]["resume"])
        check("a deferred stage is never overwritten",
              by["R9-DEFER"]["resume"]["stage"] == "deferred",
              by["R9-DEFER"]["resume"])
        check("an already-done stage is left alone (its commit is not rewritten)",
              by["R9-DONE"]["resume"]["stage"] == "done"
              and by["R9-DONE"]["resume"]["commit"] == "b" * 40,
              by["R9-DONE"]["resume"])
        check("the merged body's Carry item lands in the destination",
              by["R9-DEST"].get("carry")
              == ["the widget parser drops a unit. Carry: R9-DEST"],
              by["R9-DEST"].get("carry"))
        check("carry_audit's parser is used: a quoted marker in a code span "
              "routes nothing (a second parser would append it)",
              len(by["R9-DEST"].get("carry") or []) == 1,
              by["R9-DEST"].get("carry"))
        check("a Carry: to a done group is refused, not appended",
              "carry" not in by["R9-OVER"], by["R9-OVER"].get("carry"))
        check("no PR, or a closed-unmerged PR, changes nothing",
              by["R9-NOPR"]["resume"]["stage"] == "not-started"
              and by["R9-PREFIX"]["resume"]["stage"] == "not-started",
              (by["R9-NOPR"]["resume"], by["R9-PREFIX"]["resume"]))
        check("the branch is the round's roster branch, not main",
              "refs/heads/main" in branches(bare)
              and json.loads(git("-C", str(bare), "show", f"main:{ROSTER}"))
              == ROSTER_FIXTURE, branches(bare))
        # The round-trip rule, end to end: a no-op pass reproduces the bytes.
        tip = git("-C", str(bare), "rev-parse", f"refs/heads/{branch}")
        before = git("-C", str(bare), "show", f"{branch}:{ROSTER}")
        rc, out, err = calls(drv, state, "--apply")
        check("a no-op pass returns 0 and moves nothing",
              rc == 0 and git("-C", str(bare), "rev-parse",
                              f"refs/heads/{branch}") == tip, (rc, out, err))
        check("a no-op pass reproduces the roster's bytes exactly",
              git("-C", str(bare), "show", f"{branch}:{ROSTER}") == before)
        check("and it writes nothing (the round-trip rule's own words)",
              "nothing written" in out, out)

        # UNREADABLE: a read that fails refuses and writes nothing.
        rc, out, err = calls(drv, root / "no-such.json", "--apply")
        check("an unreadable --pr-state refuses rc 2", rc == 2, rc)
        check("and the refusal is UNREADABLE, never 'no mismatches'",
              "UNREADABLE" in err, err)
        check("and nothing moved", git("-C", str(bare), "rev-parse",
                                       f"refs/heads/{branch}") == tip)
        rc, out, err = calls(drv, state, "--apply", "--roster-file",
                             str(drv / ROSTER))
        check("--roster-file with --apply is refused (no branch to write)",
              rc == 2 and "read-only" in err, (rc, err))

        # THE LINT GATE is in the path: a refused roster is never pushed.
        bare2, drv2, _ = build(root / "two", LINT_BAD)
        rc, out, err = calls(drv2, state, "--apply")
        check("the lint gate refuses the push rc 3", rc == 3, (rc, out, err))
        check("and the branch did not land", branch not in branches(bare2),
              branches(bare2))

    # The live roster's own words: every stage a round's roster carries is
    # classified, so a new wording cannot be silently overwritten.
    root = Path(__file__).resolve().parents[3]
    seen: dict[str, str] = {}
    for path in sorted((root / roster_lib.ROSTERS_DIR).glob("wave-*-groups.json")):
        for g in json.loads(path.read_text(encoding="utf-8")).get("groups", []):
            stage = (g.get("resume") or {}).get("stage")
            if stage is not None:
                seen.setdefault(stage, path.name)
    unknown = {s: f for s, f in seen.items()
               if s not in DERIVABLE_STAGES and s not in PROTECTED_STAGES}
    check("every stage the tree's rosters carry is classified (derivable or "
          "protected)", not unknown, unknown)
    check("the classification covers the tree's rosters at all",
          bool(seen), sorted(seen))

    print(f"roster_sync self-test: {n[0]} checks, {len(fails)} failed")
    for f in fails:
        print("FAIL", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

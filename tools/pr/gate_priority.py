#!/usr/bin/env python3
"""The gate-lease priority a branch earns, derived from the round roster.

    python3 tools/pr/gate_priority.py              # HEAD's branch, live roster
    python3 tools/pr/gate_priority.py --branch B    # an explicit branch
    python3 tools/pr/gate_priority.py --hotfix      # prints 1 when the group is a hotfix, else 0
    python3 tools/pr/gate_priority.py --self-test   # hermetic fixtures

The lease (``tests/gate_lock.py``) is generic: it orders waiters by an integer
it is given and never decides who deserves one. This script is the policy that
supplies the integer, and ``tools/pr/prepr.sh`` step 1b0 exports its answer as
``HPO_GATE_PRIORITY`` for the heavy-slot take and every nested leased step.

CHANNELS, highest precedence first. The first channel that yields a valid
integer wins; a channel that yields none is skipped, never fatal.

1. ``$HPO_GATE_PRIORITY`` -- the caller's explicit override.
2. ``.gate-priority`` in the worktree root -- one line, the group's override.
3. The derived default: the group this branch answers for in the round roster
   (``roster_lib.group_for_branch``, which matches ``resume.branch``) maps
   through ``roster_lib.dispatch_rank``: a hotfix -> 2; an accepted outside
   group or one named in the round's critical-path set, one rank unordered
   between them (owner rulings tvofi 2026-11-07, triage P420, and
   2026-11-08) -> 1; otherwise 0. The lease's three bands
   (``gate_lock.PRIORITY_MAX`` is 2) are exactly those ranks.

THE FETCH IS AT CALL TIME. The roster ref is refreshed before it is read, so a
stale local mirror cannot decide a group is off the critical path. Every
failure -- no origin, a failed fetch or read, no roster, a branch that maps to
no group, a malformed critical-path file -- is 0: fail to FIFO, never to a
crash and never to a stuck queue.

THE CRITICAL-PATH FILE lives beside the roster on the roster ref:

    dev/programme/rosters/critical-path.json
    {"at": "<iso8601>", "critical": ["R10-GROUP", ...]}

``at`` records when the set was published and is not read. ``critical`` is the
list of roster group ids, matched after ``roster_lib.norm_group`` (lowercase,
``_`` as ``-``). The orchestrator republishes the file at each wave edge; an
absent or malformed file means no group is critical.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_SEAT = ROOT / "tools" / "audit" / "seat"
if str(_SEAT) not in sys.path:
    sys.path.insert(0, str(_SEAT))
import roster_lib  # noqa: E402  (after the path insert, as the seat tools do)

PRIORITY_ENV = "HPO_GATE_PRIORITY"
PRIORITY_NORMAL = 0
TOP_PRIORITY = 1  # an outside group or the critical path, one band
HOTFIX_PRIORITY = 2
MARKER_NAME = ".gate-priority"
FETCH_TIMEOUT = 20


def _git(repo: str, *args: str, timeout: float | None = None) -> subprocess.CompletedProcess:
    """``git -C repo``, never prompting for credentials and never raising."""
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    try:
        return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                              text=True, timeout=timeout, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return subprocess.CompletedProcess(args, 1, "", str(exc))


def _current_branch(repo: str) -> str:
    """The checked-out branch, or "" for a detached head (which maps to no group)."""
    r = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    name = r.stdout.strip() if r.returncode == 0 else ""
    return "" if name == "HEAD" else name


def _roster_ref(repo: str) -> str | None:
    """The round roster's remote ref, fetched now; None when unusable.

    ``roster_lib.round_ref`` names ``origin/handoff/audit-r<N>-roster`` from
    the newest roster at ``origin/main``. The branch is fetched before the read
    so the answer is the published set, not whatever this clone last saw. A
    missing ref, a failed fetch or a timeout is None: fail to FIFO.
    """
    try:
        ref = roster_lib.round_ref(roster_lib.git_in(repo))
    except (OSError, ValueError):
        return None
    if ref is None:
        return None
    branch = ref[len("origin/"):] if ref.startswith("origin/") else ref
    if _git(repo, "fetch", "--quiet", "origin", branch,
            timeout=FETCH_TIMEOUT).returncode != 0:
        return None
    return ref


def _rank(branch: str, *, repo: str, ref: str | None, fetch: bool) -> int | None:
    """The roster dispatch rank of the branch's group, None on any failure."""
    try:
        roster_ref = ref
        if roster_ref is None:
            roster_ref = _roster_ref(repo) if fetch else roster_lib.reader_ref(repo, None)
        if roster_ref is None:
            return None
        roster = roster_lib.show_roster(repo, roster_ref)
        group = roster_lib.group_for_branch(roster, branch)
        if group is None:
            return None
        critical = roster_lib.critical_path_groups(repo, roster_ref)
        if critical is None:
            critical = set()
        return roster_lib.dispatch_rank(roster, group, critical)
    except Exception:  # noqa: BLE001 -- a pre-pr helper must never crash a run
        return None


def derived_priority(branch: str, *, repo: str = ".", ref: str | None = None,
                     fetch: bool = True) -> int:
    """2 for a hotfix group, 1 for an outside group or one in the
    critical-path set at the roster ref (a missing or malformed set drops only
    the critical path's 1; an outside group still answers 1).

    0 for every other answer, including every failure. ``ref`` overrides the
    live roster ref (the self-test's fixture); ``fetch=False`` reads the local
    ref without refreshing it.
    """
    rank = _rank(branch, repo=repo, ref=ref, fetch=fetch)
    return {roster_lib.RANK_HOTFIX: HOTFIX_PRIORITY,
            roster_lib.RANK_TOP: TOP_PRIORITY}.get(rank, PRIORITY_NORMAL)


def is_hotfix(branch: str, *, repo: str = ".", ref: str | None = None,
              fetch: bool = True) -> bool:
    """True only when the roster classes the branch's group a hotfix.

    The derived class alone: ``$HPO_GATE_PRIORITY`` and ``.gate-priority`` order
    the lease and say nothing about the group. Every failure is False, so an
    unreadable roster yields the full pre-PR run, never a skipped one.
    """
    return _rank(branch, repo=repo, ref=ref, fetch=fetch) == roster_lib.RANK_HOTFIX


def _declared(raw: str | None) -> int | None:
    """A valid integer from one channel, or None when that channel says nothing."""
    if raw is None:
        return None
    try:
        return int(raw.strip())
    except (AttributeError, ValueError):
        return None


def priority_for_branch(branch: str, *, repo: str = ".", ref: str | None = None,
                        fetch: bool = True, env: dict | None = None) -> int:
    """The integer a caller should declare: env, then marker, then derived."""
    env = os.environ if env is None else env
    explicit = _declared(env.get(PRIORITY_ENV))
    if explicit is not None:
        return explicit
    try:
        text = (Path(repo) / MARKER_NAME).read_text(encoding="utf-8")
    except OSError:
        text = ""
    lines = text.splitlines()
    from_marker = _declared(lines[0] if lines else None)
    if from_marker is not None:
        return from_marker
    return derived_priority(branch, repo=repo, ref=ref, fetch=fetch)


# ------------------------------------------------------------------ self-test
def _self_test() -> int:
    """Hermetic fixtures: a throwaway repository and refs it builds itself.

    The live roster branch is NOT read, so republishing the critical-path set
    cannot turn this red. The fetch-failure arm runs against the throwaway
    repository's missing ``origin`` -- the exact shape a box with no network
    presents, and the arm that proves the failure answer is 0, not a crash.
    """
    import json
    import tempfile

    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_environ, throwaway_git_init

    fails: list[str] = []
    n = [0]

    def check(name: str, ok: bool, got: object = "") -> None:
        n[0] += 1
        if not ok:
            fails.append(f"{name} (got: {got})")

    with throwaway_git_environ(), tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        rosters = repo / roster_lib.ROSTERS_DIR
        rosters.mkdir(parents=True)
        throwaway_git_init(repo, "-q", "-b", "main")

        def commit(message: str) -> str:
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message],
                           check=True)
            return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                                  capture_output=True, text=True, check=True).stdout.strip()

        roster = {"groups": [
            {"group": "R10-CRIT", "resume": {"branch": "handoff/r10-crit"}},
            {"group": "R10-OTHER", "resume": {"branch": "handoff/r10-other"}},
            {"group": "R10-OUT", "source": "outside", "resume": {"branch": "handoff/r10-out"}},
            {"group": "R10-HOT", "kind": "bug", "resume": {"branch": "handoff/r10-hot"}},
            {"group": "R10-OUTCRIT", "source": "outside", "resume": {"branch": "handoff/r10-outcrit"}},
        ]}
        (rosters / "wave-r10-groups.json").write_text(json.dumps(roster))
        no_set = commit("roster only")

        (repo / roster_lib.CRITICAL_PATH_NAME).write_text(json.dumps(
            {"at": "2026-10-20T00:00:00Z", "critical": ["R10-CRIT", "R10-OUTCRIT"]}))
        good = commit("the critical-path set")

        (repo / roster_lib.CRITICAL_PATH_NAME).write_text('{"critical": "R10-CRIT"}')
        malformed = commit("a malformed set")

        (repo / roster_lib.CRITICAL_PATH_NAME).write_text(json.dumps(
            {"at": "2026-10-20T00:00:00Z", "critical": ["R10-CRIT", "R10-OUTCRIT"]}))
        live = commit("republished")

        for name, sha in (("main", live), ("handoff/audit-r10-roster", live)):
            subprocess.run(["git", "-C", str(repo), "update-ref",
                            f"refs/remotes/origin/{name}", sha], check=True)

        def derived(branch: str, at: str | None = None, **kw) -> int:
            return derived_priority(branch, repo=str(repo), ref=at or live,
                                    fetch=kw.get("fetch", False))

        check("a listed group gets priority with no env and no marker",
              derived("handoff/r10-crit") == 1, derived("handoff/r10-crit"))
        check("a hotfix outranks an outside group, which shares the critical path's band "
              "(owner rulings 2026-11-07, 2026-11-08)",
              derived("handoff/r10-hot") == 2 and derived("handoff/r10-out") == 1
              and derived("handoff/r10-out") == derived("handoff/r10-crit")
              and derived("handoff/r10-outcrit") == 1,
              [derived(b) for b in ("handoff/r10-out", "handoff/r10-hot", "handoff/r10-outcrit")])
        check("an outside group needs no critical-path set; a malformed set drops only the critical 1",
              derived("handoff/r10-out", at=no_set) == 1 and derived("handoff/r10-hot", at=malformed) == 2
              and derived("handoff/r10-crit", at=malformed) == 0)
        # Null control: a roster with no outside group and no hotfix orders as at the base.
        plain = {"groups": [g for g in roster["groups"] if g["group"] in ("R10-CRIT", "R10-OTHER")]}
        (rosters / "wave-r10-groups.json").write_text(json.dumps(plain))
        (repo / roster_lib.CRITICAL_PATH_NAME).write_text(json.dumps({"critical": ["R10-CRIT"]}))
        plain_sha = commit("no outside group, no hotfix")
        check("null control: with no outside group and no hotfix, the derived priority is the base's 1 / 0",
              [derived(b, at=plain_sha) for b in ("handoff/r10-crit", "handoff/r10-other", "fix/none")] == [1, 0, 0],
              [derived(b, at=plain_sha) for b in ("handoff/r10-crit", "handoff/r10-other", "fix/none")])
        (rosters / "wave-r10-groups.json").write_text(json.dumps(roster))
        check("is_hotfix: true for the hotfix group only; an outside, a critical and an unmapped branch are not",
              [is_hotfix(b, repo=str(repo), ref=live, fetch=False) for b in
               ("handoff/r10-hot", "handoff/r10-out", "handoff/r10-crit", "handoff/r10-other", "fix/none")]
              == [True, False, False, False, False])
        check("is_hotfix ignores the lease override and fails closed (False) on a failed fetch",
              not is_hotfix("handoff/r10-other", repo=str(repo), ref=live, fetch=False)
              and not is_hotfix("handoff/r10-hot", repo=str(repo), fetch=True))

        def cli(branch: str) -> tuple[int, str]:
            """``main(["--hotfix", ...])`` and its stdout: the line prepr's hotfix_class reads."""
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = main(["--hotfix", "--branch", branch, "--repo", str(repo),
                           "--ref", live, "--no-fetch"])
            return rc, buf.getvalue()

        hot_out_crit_none = ("handoff/r10-hot", "handoff/r10-out", "handoff/r10-crit", "fix/none")
        check("--hotfix prints 1 for the hotfix group's branch, 0 for an outside, a critical and an unmapped one",
              [cli(b) for b in hot_out_crit_none] == [(0, "1\n"), (0, "0\n"), (0, "0\n"), (0, "0\n")],
              [cli(b) for b in hot_out_crit_none])

        # The except arm: a roster read that raises (not a failed fetch, which returns
        # before the read) must fail closed -- not a hotfix, so a full prepr; priority 0.
        def hot_answers() -> tuple[bool, int, tuple[int, str]]:
            return (is_hotfix("handoff/r10-hot", repo=str(repo), ref=live, fetch=False),
                    derived("handoff/r10-hot"), cli("handoff/r10-hot"))

        check("null control: the hotfix branch's unbroken read is (True, 2, '1')",
              hot_answers() == (True, 2, (0, "1\n")), hot_answers())
        real_show = roster_lib.show_roster

        def unreadable(*_a, **_k):
            raise ValueError("fixture: an unreadable roster")

        roster_lib.show_roster = unreadable
        try:
            raised = hot_answers()
        finally:
            roster_lib.show_roster = real_show
        check("a roster read that raises fails closed: not a hotfix, priority 0, --hotfix prints 0",
              raised == (False, 0, (0, "0\n")), raised)
        check("a group that resolves but is not listed stays normal (null control)",
              derived("handoff/r10-other") == 0, derived("handoff/r10-other"))
        check("a branch that maps to no group stays normal",
              derived("fix/no-such-group") == 0, derived("fix/no-such-group"))
        check("the branch's last segment answers for the group without resume.branch",
              derived("fix/r10-crit") == 1, derived("fix/r10-crit"))
        check("an unreadable set is normal, not a crash",
              derived("handoff/r10-crit", at=no_set) == 0, derived("handoff/r10-crit", at=no_set))
        check("a malformed set is normal, not a crash",
              derived("handoff/r10-crit", at=malformed) == 0,
              derived("handoff/r10-crit", at=malformed))
        check("a failed fetch is normal, not a crash",
              derived_priority("handoff/r10-crit", repo=str(repo), fetch=True) == 0,
              derived_priority("handoff/r10-crit", repo=str(repo), fetch=True))

        check("the environment variable overrides the derived default",
              priority_for_branch("handoff/r10-other", repo=str(repo), ref=live,
                                  fetch=False, env={PRIORITY_ENV: "2"}) == 2)
        (repo / MARKER_NAME).write_text("1\n")
        check("the marker overrides the derived default",
              priority_for_branch("handoff/r10-other", repo=str(repo), ref=live,
                                  fetch=False, env={}) == 1)
        check("the environment variable outranks the marker",
              priority_for_branch("handoff/r10-other", repo=str(repo), ref=live,
                                  fetch=False, env={PRIORITY_ENV: "2"}) == 2)
        check("a malformed override is skipped, not fatal",
              priority_for_branch("handoff/r10-crit", repo=str(repo), ref=live,
                                  fetch=False,
                                  env={PRIORITY_ENV: "junk"}) == 1)
        (repo / MARKER_NAME).unlink()
        check("with neither override the derived default still answers",
              priority_for_branch("handoff/r10-crit", repo=str(repo), ref=live,
                                  fetch=False, env={}) == 1)

    print(f"gate_priority self-test: {n[0]} checks, {len(fails)} failed")
    for failure in fails:
        print("FAIL", failure)
    return 1 if fails else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch", default=None,
                        help="the branch whose group is resolved (default: HEAD)")
    parser.add_argument("--repo", default=".", help="repository root (default: cwd)")
    parser.add_argument("--ref", default=None,
                        help="roster ref override, for fixtures (default: the live one)")
    parser.add_argument("--no-fetch", action="store_true",
                        help="read the local roster ref without refreshing it")
    parser.add_argument("--hotfix", action="store_true",
                        help="print 1 when the roster classes the branch's group a hotfix, else 0")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return _self_test()
    branch = args.branch if args.branch is not None else _current_branch(args.repo)
    if args.hotfix:
        print(int(is_hotfix(branch, repo=args.repo, ref=args.ref, fetch=not args.no_fetch)))
        return 0
    print(priority_for_branch(branch, repo=args.repo, ref=args.ref,
                              fetch=not args.no_fetch))
    return 0


if __name__ == "__main__":
    sys.exit(main())

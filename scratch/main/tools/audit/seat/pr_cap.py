#!/usr/bin/env python3
"""The soft cap: it bounds work in progress, so it gates DISPATCH, not opening.

    python3 -I tools/audit/seat/pr_cap.py info --repo OWNER/REPO
    python3 -I tools/audit/seat/pr_cap.py dispatch-gate [--repo PATH]
        [--roster-file PATH | --roster-ref GITREF [--roster-path PATH]]
        [--over-cap REASON]
    python3 -I tools/audit/seat/pr_cap.py --self-test

THE RULING (tvofi, 2026-10-20, moving 2026-10-18's open-PR cap; restated
2026-10-21). The soft cap gates only starting or dispatching a new roster
group; opening or updating a pull request for an owed handoff is never refused
by it. Opening is how work LEAVES work-in-progress, not how it enters. So:
  - `dispatch-gate` refuses when HPO_WIP_CAP (default 6) roster groups have
    `resume.stage` "in-progress". WIP is read through `roster_lib`, the one
    schema reader, at the roster ref, and counted by group id: a group that
    also has an open pull request is still one group, never two. A roster it
    cannot read is a refusal, never a clean zero.
  - `open_pr.sh` and `update_pr.sh` are never refused by the cap; `info` prints the open count as
    information (`open_pr: N open PRs; the cap gates dispatch, not opening`).
    A count gh cannot read says so and still opens: it is not a gate.
    `--over-cap "<reason>"` is still accepted by open_pr.sh so existing
    callers do not break; it says it is advisory and nothing more.
  - `orchestrator_tick.py` prints `WIP: N/6 (open PRs M)` every pass: N from
    `wip_groups`, M from `counted`, flagged at or over the cap. It does not
    dispatch and does not gate; it reports.

WHAT "BOT" MEANS HERE, a design choice. Every pull request this repository's
seats open is authored by the hpo-author App (decision 0011), which GitHub
reports as a bot. Excluding every bot would count nothing, so a bot is an author
GitHub flags as one other than AUTHOR_APP: the merge-main, autofix and
dependency bots.

Lines (one per call, on stderr; exit 0 to pass, 1 to refuse, 2 for usage):
  dispatch: WIP 5/6: may dispatch a new group (G1, G2, ...)
  dispatch: REFUSE: WIP cap: 6/6 at the cap (G1, ...); finish or merge a group,
      or --over-cap <reason>
  dispatch: OVER-CAP: WIP 6/6, overridden: <reason> (G1, ...)
  open_pr: 20 open PRs; the cap gates dispatch, not opening
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys

#: A roster group is work in progress while `resume.stage` is exactly this.
#: The vocabulary is the roster's own; `roster_lib.DONE_STAGES` names the
#: stages that are finished, and a stage neither set names is not counted.
WIP_STAGE = "in-progress"
WIP_CAP_DEFAULT = 6
WIP_CAP_ENV = "HPO_WIP_CAP"
WIP_REFUSE = "dispatch: REFUSE: WIP cap: "
AUTHOR_APP = "app/hpo-author"
COORDINATOR_PATH = "custom_components/heatpump_optimizer/coordinator.py"
COORDINATOR_CAP = 2
FIELDS = "number,title,author"
SELF = os.path.abspath(__file__)
_RL = None


def is_bot(pr: dict) -> bool:
    a = pr.get("author") or {}
    return bool(a.get("is_bot")) and a.get("login") != AUTHOR_APP


def counted(prs: list) -> list:
    """The open pull requests the open count reports, in the order given.

    This is the tick's M and `info`'s N, not a gate: the cap counts roster
    groups (`wip_groups`), so a record: title and another bot's pull request
    are excluded here without being excluded from anywhere that decides.
    """
    out = []
    for pr in prs:
        if str(pr.get("title") or "").startswith("record:"): continue  # mut:caprecord
        if is_bot(pr): continue  # mut:capbot
        out.append(pr)
    return out


def wip_cap_from_env(env=None) -> "int | None":
    """HPO_WIP_CAP as a positive integer, the default when unset, None when invalid."""
    raw = (env if env is not None else os.environ).get(WIP_CAP_ENV, "")
    if raw == "":
        return WIP_CAP_DEFAULT
    return int(raw) if raw.isdigit() and int(raw) > 0 else None


def read_open(repo: str, gh=None) -> "tuple[list | None, str]":
    """(the open pull requests, '') or (None, why they could not be read)."""
    argv = ["pr", "list", "--repo", repo, "--state", "open", "--limit", "200",
            "--json", FIELDS]
    if gh is not None:
        rc, out = gh(argv)
    else:
        try:
            r = subprocess.run(["gh", *argv], capture_output=True, text=True)
        except OSError as e:
            return None, f"gh did not run: {e}"
        rc, out = r.returncode, r.stdout + r.stderr
    if rc != 0: return None, f"gh exited {rc}: {out.strip()[-160:]}"  # mut:capreadrc
    try:
        prs = json.loads(out)
    except ValueError as e:
        return None, f"not JSON: {e}"
    if not isinstance(prs, list):
        return None, "not a list of pull requests"
    if len(prs) >= 200:
        return None, "200 or more returned, the list may be truncated"
    return prs, ""


def open_info(prs: "list | None", why: str) -> "tuple[int, str]":
    """(0, the one line): the open count as information. Opening is never gated."""
    n = None if prs is None else len(counted(prs))
    if n is None: return 0, f"open_pr: open pull requests could not be read ({why}); opening anyway, the cap gates dispatch"  # mut:inforead
    return 0, (f"open_pr: {n} open PRs; the cap gates dispatch, "
               "not opening")


def _roster_lib():
    """roster_lib beside this file, loaded by path: `python3 -I` keeps the
    script's directory off sys.path, so an `import roster_lib` would fail."""
    global _RL
    if _RL is None:
        p = os.path.join(os.path.dirname(SELF), "roster_lib.py")
        spec = importlib.util.spec_from_file_location("roster_lib_pr_cap", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _RL = mod
    return _RL


def wip_groups(roster: dict) -> list:
    """The roster group ids whose `resume.stage` is `WIP_STAGE`, roster order.

    Counted by group id, off the roster alone: the open-pull-request rule
    (`counted`) is a different question and a group that also has an open
    pull request is still one group.
    """
    return [gid for gid, g in _roster_lib().groups_of(roster).items()
            if (g.get("resume") or {}).get("stage") == WIP_STAGE]


def read_roster(repo: str = ".", roster_file: "str | None" = None,
                roster_ref: "str | None" = None,
                roster_path: "str | None" = None) -> "tuple[dict | None, str]":
    """(the roster, where it was read) or (None, why it could not be read).

    `roster_lib` is the one schema reader and `reader_ref` the one answer to
    which ref; nothing here parses a roster or names a ref itself.
    """
    rl = _roster_lib()
    if roster_file:
        try:
            return rl.load_roster_file(roster_file), roster_file
        except (OSError, ValueError) as e:
            return None, f"roster file {roster_file}: {str(e)[:120]}"
    try:
        ref = rl.reader_ref(repo, roster_ref)
        path = rl.roster_path(repo, ref, roster_path)
        return rl.show_roster(repo, ref, path), f"{ref}:{path}"
    except (rl.RosterNotFound, ValueError) as e:
        return None, str(e)[:200]


def dispatch_gate(roster: "dict | None", why: str, cap: "int | None",
                  over_cap: "str | None") -> "tuple[int, str]":
    """(exit status, the one line): refuse at or above the cap, or unread."""
    if cap is None:
        return 1, WIP_REFUSE + f"{WIP_CAP_ENV} is not a positive integer"
    if over_cap is not None and not over_cap.strip():
        return 1, WIP_REFUSE + "--over-cap needs a reason"
    if roster is None: return 1, WIP_REFUSE + f"the roster could not be read ({why}); a count it cannot read is no pass"  # mut:wipunread
    wip = wip_groups(roster)
    n, ids = len(wip), ", ".join(wip)
    if over_cap is not None: return 0, f"dispatch: OVER-CAP: WIP {n}/{cap}, overridden: {over_cap.strip()} ({ids})"  # mut:overcap
    if n < cap: return 0, f"dispatch: WIP {n}/{cap}: may dispatch a new group ({ids})"
    return 1, WIP_REFUSE + f"{n}/{cap} at the cap ({ids}); finish or merge a group, or --over-cap <reason>"  # mut:cap


def coordinator_prs(files_by_pr: dict) -> "tuple[list, list]":
    """(the PRs whose own diff touches the coordinator, the PRs whose diff is unread)."""
    hit = sorted(n for n, fs in files_by_pr.items() if fs is not None and COORDINATOR_PATH in fs)
    unread = sorted(n for n, fs in files_by_pr.items() if fs is None)
    return hit, unread


def _doc_stage() -> dict:
    """The first named group of stages, for the self-test's rosters."""
    return {"groups": [{"group": f"G{i}", "resume": {"stage": s}}
                       for i, s in enumerate(("done", "in-progress", "not-started",
                                              "queued", "fixing", "in-progress",
                                               "in-progress", "in-progress",
                                               "in-progress"))]}


def self_test() -> int:
    total = failed = 0

    def ck(name: str, ok: bool) -> None:
        nonlocal total, failed
        total += 1
        if not ok:
            failed += 1
        print(("  ok   " if ok else "  FAIL ") + name)

    def roster(stages: list) -> dict:
        return {"groups": [{"group": f"G{i}", "resume": {"stage": s}}
                           for i, s in enumerate(stages)]}

    five = roster(["in-progress"] * 5)

    # ---- the WIP count is the roster's in-progress groups ------------------
    ck("WIP is exactly resume.stage in-progress: done, not-started, queued and "
       "fixing are not work in progress",
       wip_groups(_doc_stage()) == ["G1", "G5", "G6", "G7", "G8"])
    ck("a group with an open pull request is ONE group: the count is over group "
       "ids, and the open count is a separate rule",
       wip_groups({"groups": [{"group": "G", "resume": {
           "stage": "in-progress", "branch": "fix/g", "pr": 7}}]}) == ["G"]
       and len(counted([{"number": i, "title": "t", "author": {"login": AUTHOR_APP,
                                                               "is_bot": True}}
                        for i in range(5)])) == 5)
    ck("null control: no in-progress group is 0 WIP, and the gate passes",
       wip_groups(roster(["done", "not-started"])) == []
       and dispatch_gate(roster(["done"]), "", 6, None)[0] == 0)

    # ---- the dispatch gate's arms -----------------------------------------
    rc, line = dispatch_gate(five, "", 6, None)
    ck("5 WIP passes and names the groups",
       rc == 0 and line == "dispatch: WIP 5/6: may dispatch a new group (G0, G1, G2, G3, G4)")
    six = roster(["in-progress"] * 6)
    rc, line = dispatch_gate(six, "", 6, None)
    ck("6 WIP refuses at the cap, naming the count, the groups and both ways past it",
       rc == 1 and line == WIP_REFUSE + "6/6 at the cap (G0, G1, G2, G3, G4, G5); "
       "finish or merge a group, or --over-cap <reason>")
    seven = roster(["in-progress"] * 7)
    rc, line = dispatch_gate(seven, "", 6, None)
    ck("7 WIP refuses too (at or over the cap, not exactly at it)",
       rc == 1 and "7/6 at the cap" in line)
    rc, line = dispatch_gate(six, "", 6, "a merge train is draining")
    ck("--over-cap passes at the cap and logs its reason",
       rc == 0 and line == "dispatch: OVER-CAP: WIP 6/6, overridden: a merge train is draining "
       "(G0, G1, G2, G3, G4, G5)")
    ck("--over-cap with an empty reason refuses",
       dispatch_gate(six, "", 6, "  ")[0] == 1)
    rc, line = dispatch_gate(None, "no roster at origin/main:dev/programme/rosters", 6, None)
    ck("a roster it cannot read refuses, naming why: never a clean zero",
       rc == 1 and "could not be read (no roster at origin/main" in line
       and "no pass" in line)
    roster_obj, why = read_roster("/nonexistent/checkout")
    ck("read_roster over a checkout with no roster is a refusal, not ({} , '')",
       roster_obj is None and why and dispatch_gate(roster_obj, why, 6, None)[0] == 1)
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        fh.write("{not json")
        bad = fh.name
    try:
        roster_obj, why = read_roster(roster_file=bad)
    finally:
        os.unlink(bad)
    ck("a roster file that is not JSON is a refusal, naming it",
       roster_obj is None and "roster file" in why
       and dispatch_gate(roster_obj, why, 6, None)[0] == 1)
    ck("HPO_WIP_CAP: unset is 6, '3' is 3, '0' and 'x' are invalid",
       [wip_cap_from_env(e) for e in ({}, {WIP_CAP_ENV: "3"}, {WIP_CAP_ENV: "0"},
                                      {WIP_CAP_ENV: "x"})] == [6, 3, None, None])
    ck("an invalid cap refuses",
       dispatch_gate(five, "", None, None)[0] == 1
       and WIP_REFUSE + f"{WIP_CAP_ENV} is not a positive integer"
       == dispatch_gate(five, "", None, None)[1])

    # ---- opening is information only --------------------------------------
    app = {"login": AUTHOR_APP, "is_bot": True}
    other_bot = {"login": "app/dependabot", "is_bot": True}
    human = {"login": "tvofi", "is_bot": False}
    rec = {"number": 90, "title": "record: delivery rows", "author": app}
    bot = {"number": 91, "title": "bump a pin", "author": other_bot}
    ck("the authoring App's pull requests count; a record: title and another bot do not",
       len(counted([{"number": i, "title": f"R10-X{i}: t", "author": app}
                    for i in range(5)] + [rec, bot,
                                          {"number": 92, "title": "t",
                                           "author": human}])) == 6)
    twenty = [{"number": i, "title": "t", "author": app} for i in range(20)]
    rc, line = open_info(twenty, "")
    ck("null control: 20 open pull requests are information; opening is not refused",
       rc == 0 and line == "open_pr: 20 open PRs; the cap gates dispatch, not opening")
    rc, line = open_info(None, "gh exited 1: HTTP 403")
    ck("an open count gh cannot read says so and still does not stop an open",
       rc == 0 and "could not be read (gh exited 1" in line and "opening anyway" in line)
    prs, why = read_open("o/r", gh=lambda a: (1, "HTTP 403: rate limit"))
    ck("a gh failure is reported, never read as an empty board",
       prs is None and open_info(prs, why)[0] == 0 and "could not be read" in open_info(prs, why)[1])
    prs, why = read_open("o/r", gh=lambda a: (0, "<html>"))
    ck("output that is not JSON is a refusal of the read", prs is None and "not JSON" in why)
    prs, why = read_open("o/r", gh=lambda a: (0, json.dumps([{"number": i} for i in range(200)])))
    ck("a list at gh's limit may be truncated: refused", prs is None and "truncated" in why)
    prs, why = read_open("o/r", gh=lambda a: (0, "[]"))
    ck("null control: an empty board reads as zero", prs == [] and open_info(prs, why)[1]
       == "open_pr: 0 open PRs; the cap gates dispatch, not opening")
    hit, unread = coordinator_prs({1: [COORDINATOR_PATH], 2: ["x.py"], 3: None})
    ck("coordinator PRs: the diff that touches it counts, an unread diff is named apart",
       hit == [1] and unread == [3])
    print(f"pr_cap self-test: {total} checks, {failed} failed")
    return 1 if failed else 0


def _opt(argv: list, name: str) -> "str | None":
    """The argument after `name`, or None; an absent value is the empty string."""
    if name not in argv:
        return None
    i = argv.index(name)
    return argv[i + 1] if i + 1 < len(argv) else ""


def main(argv: list) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    mode = argv[:1]
    if mode == ["info"]:
        repo = _opt(argv, "--repo")
        if not repo:
            print("pr_cap.py info --repo OWNER/REPO", file=sys.stderr)
            return 2
        prs, why = read_open(repo)
        print(open_info(prs, why)[1], file=sys.stderr)
        return 0
    if mode == ["dispatch-gate"]:
        repo = _opt(argv, "--repo") or "."
        roster, where = read_roster(repo, _opt(argv, "--roster-file"),
                                    _opt(argv, "--roster-ref"),
                                    _opt(argv, "--roster-path"))
        rc, line = dispatch_gate(roster, where, wip_cap_from_env(),
                                 _opt(argv, "--over-cap"))
        print(line, file=sys.stderr)
        return rc
    print(__doc__.split("\n\n")[1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

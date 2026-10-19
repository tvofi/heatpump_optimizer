#!/usr/bin/env python3
"""The soft cap on open pull requests: one counting rule, read by open_pr.sh
before it opens one and by orchestrator_tick.py on every pass.

    python3 -I tools/audit/seat/pr_cap.py gate --repo OWNER/REPO [--over-cap REASON]
    python3 -I tools/audit/seat/pr_cap.py --self-test

THE RULING (tvofi, 2026-10-18, relayed to R10-OPENPR-SILENT by the round-10
orchestrator): open_pr.sh refuses to open a pull request while the open ones
number HPO_OPEN_PR_CAP (default 6) or more, drafts included, `record:`-titled
and bot ones excluded; `--over-cap "<reason>"` overrides it and says so; a
count it cannot read is a refusal, never a pass. The tick also reports how many
counted pull requests touch the coordinator, against a cap of 2.

WHAT "BOT" MEANS HERE, a design choice. Every pull request this repository's
seats open is authored by the hpo-author App (decision 0011), which GitHub
reports as a bot. Excluding every bot would count nothing, so a bot is an author
GitHub flags as one other than AUTHOR_APP: the merge-main, autofix and
dependency bots.

`gate` prints one line on stderr and exits 0 to open, 1 to refuse:
  open_pr: REFUSE: open-PR cap: N open >= CAP; drain before opening (...)
  open_pr: OVER-CAP: N open >= CAP, overridden: <reason>
  open_pr: open-PR cap: N open < CAP
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

CAP_DEFAULT = 6
CAP_ENV = "HPO_OPEN_PR_CAP"
AUTHOR_APP = "app/hpo-author"
COORDINATOR_PATH = "custom_components/heatpump_optimizer/coordinator.py"
COORDINATOR_CAP = 2
FIELDS = "number,title,author"
REFUSE = "open_pr: REFUSE: open-PR cap: "


def is_bot(pr: dict) -> bool:
    a = pr.get("author") or {}
    return bool(a.get("is_bot")) and a.get("login") != AUTHOR_APP


def counted(prs: list) -> list:
    """The open pull requests the cap counts, in the order given."""
    out = []
    for pr in prs:
        if str(pr.get("title") or "").startswith("record:"): continue  # mut:caprecord
        if is_bot(pr): continue  # mut:capbot
        out.append(pr)
    return out


def cap_from_env(env=None) -> "int | None":
    """HPO_OPEN_PR_CAP as a positive integer, the default when unset, None when invalid."""
    raw = (env if env is not None else os.environ).get(CAP_ENV, "")
    if raw == "":
        return CAP_DEFAULT
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


def gate(prs: "list | None", why: str, cap: "int | None", over_cap: "str | None") -> "tuple[int, str]":
    """(exit status, the one line): refuse at or above the cap, or unread."""
    if cap is None:
        return 1, REFUSE + f"{CAP_ENV} is not a positive integer"
    if over_cap is not None and not over_cap.strip():
        return 1, REFUSE + "--over-cap needs a reason"
    if prs is None:
        return 1, REFUSE + f"the open pull requests could not be read ({why}); a count it cannot read is no pass"
    n = len(counted(prs))
    if n < cap:
        return 0, f"open_pr: open-PR cap: {n} open < {cap}"
    if over_cap is not None: return 0, f"open_pr: OVER-CAP: {n} open >= {cap}, overridden: {over_cap.strip()}"  # mut:overcap
    return 1, REFUSE + f"{n} open >= {cap}; drain before opening ({CAP_ENV}, --over-cap <reason>)"  # mut:cap


def coordinator_prs(files_by_pr: dict) -> "tuple[list, list]":
    """(the PRs whose own diff touches the coordinator, the PRs whose diff is unread)."""
    hit = sorted(n for n, fs in files_by_pr.items() if fs is not None and COORDINATOR_PATH in fs)
    unread = sorted(n for n, fs in files_by_pr.items() if fs is None)
    return hit, unread


def self_test() -> int:
    total = failed = 0

    def ck(name: str, ok: bool) -> None:
        nonlocal total, failed
        total += 1
        if not ok:
            failed += 1
        print(("  ok   " if ok else "  FAIL ") + name)

    app = {"login": AUTHOR_APP, "is_bot": True}
    other_bot = {"login": "app/dependabot", "is_bot": True}
    human = {"login": "tvofi", "is_bot": False}
    five = [{"number": i, "title": f"R10-X{i}: t", "author": app} for i in range(5)]
    rec = {"number": 90, "title": "record: delivery rows", "author": app}
    bot = {"number": 91, "title": "bump a pin", "author": other_bot}
    ck("the authoring App's pull requests count; a record: title and another bot do not",
       len(counted(five + [rec, bot, {"number": 92, "title": "t", "author": human}])) == 6)
    rc, line = gate(five + [rec, bot], "", 6, None)
    ck("below the cap opens (5 counted, the record and bot ones excluded)",
       rc == 0 and line == "open_pr: open-PR cap: 5 open < 6")
    rc, line = gate(five + [{"number": 9, "title": "t", "author": app}], "", 6, None)
    ck("at the cap refuses, naming the count and both ways past it",
       rc == 1 and line == REFUSE + "6 open >= 6; drain before opening (HPO_OPEN_PR_CAP, --over-cap <reason>)")
    rc, line = gate(five + [{"number": 9, "title": "t", "author": app}], "", 6, "a merge train is draining")
    ck("--over-cap opens at the cap and logs its reason",
       rc == 0 and line == "open_pr: OVER-CAP: 6 open >= 6, overridden: a merge train is draining")
    ck("--over-cap with an empty reason refuses", gate([], "", 6, "  ")[0] == 1)
    prs, why = read_open("o/r", gh=lambda a: (1, "HTTP 403: rate limit"))
    rc, line = gate(prs, why, 6, None)
    ck("a gh failure is a refusal, never a pass", rc == 1 and "could not be read (gh exited 1" in line)
    prs, why = read_open("o/r", gh=lambda a: (0, "<html>"))
    ck("output that is not JSON is a refusal", gate(prs, why, 6, None)[0] == 1 and "not JSON" in why)
    prs, why = read_open("o/r", gh=lambda a: (0, json.dumps([{"number": i} for i in range(200)])))
    ck("a list at gh's limit may be truncated: refused", prs is None and "truncated" in why)
    prs, why = read_open("o/r", gh=lambda a: (0, "[]"))
    ck("null control: an empty board reads as zero and opens", prs == [] and gate(prs, why, 6, None)[0] == 0)
    ck("HPO_OPEN_PR_CAP: unset is 6, '3' is 3, '0' and 'x' are invalid",
       [cap_from_env(e) for e in ({}, {CAP_ENV: "3"}, {CAP_ENV: "0"}, {CAP_ENV: "x"})] == [6, 3, None, None])
    ck("an invalid cap refuses", gate([], "", None, None)[0] == 1)
    hit, unread = coordinator_prs({1: [COORDINATOR_PATH], 2: ["x.py"], 3: None})
    ck("coordinator PRs: the diff that touches it counts, an unread diff is named apart",
       hit == [1] and unread == [3])
    print(f"pr_cap self-test: {total} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    if argv[:1] != ["gate"] or "--repo" not in argv:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    repo = argv[argv.index("--repo") + 1] if argv.index("--repo") + 1 < len(argv) else ""
    over = None
    if "--over-cap" in argv:
        i = argv.index("--over-cap")
        over = argv[i + 1] if i + 1 < len(argv) else ""
    prs, why = read_open(repo)
    rc, line = gate(prs, why, cap_from_env(), over)
    print(line, file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

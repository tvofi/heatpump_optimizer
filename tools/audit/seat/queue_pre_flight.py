#!/usr/bin/env python3
"""queue_pre_flight.py -- validate a merge queue's admission preconditions before the train launches.

    python3 tools/audit/seat/queue_pre_flight.py <queue.json> [--repo O/R] [--checkout DIR] [--json]
    python3 tools/audit/seat/queue_pre_flight.py --self-test

The merge train stops at the first admission-time refusal (a missing delivery
row, a verdict that does not carry, a worktree it cannot create), and the
entries behind the refused one idle behind it. This instrument runs the train's
own admission reads BEFORE the train launches -- no CI waits, no pushes -- and
prints one line per queue entry:

    #<pr> PASS
    #<pr> PARK (<step>: <why>)   admission-time: the entry would stop the train;
                                 the wording is the train's own Stop wording
    #<pr> FAIL (<step>: <why>)   a hard defect in the queue file itself (the
                                 verdict is not 40-hex, the pull request is not
                                 open, the head cannot be read)

and a summary line `PRE-FLIGHT: <n> entries: <p> PASS, <k> PARK, <f> FAIL`.
Exit 0 only when every entry passed; `--json` prints the same rows as one
object for a calling seat.

THE CHECKS ARE THE TRAIN'S OWN, NOT NEW ONES -- each either delegates to
merge_train.py's method or repeats one admission read of `one`/`admit`, in the
train's order:

  queue      is_sha on the verdict (the train's `queue` stop);
  head       the pull request is open and its head reads (the train reads the
             head at step 1; a closed pull request is a defect the queue file
             carries, so FAIL, not PARK);
  bot tip    `Train.bot_tip` -- a GITHUB_TOKEN tip's pull_request runs are held
             action_required, so until one is approved the head can settle
             green and unmergeable; the train cures it by an App push (its
             recarry) (R9-RC-AUTOFIX-GOVERNANCE). The train's
             own `--pre-flight` passes it (`bot_cured`): the batch routes it
             serial, where its recarry once main moved is that push;
  carry      `app_approve.sh --carry <verdict> <head>`, the train's own step 3 /
             batch-admit read: skipped when the head is still the verdict;
  row        the three-dot diff carries `dev/programme/delivery/<pr>.md` (the
             batch-admit row stop);
  row stale  the row's own status line says the pull request is open
             (R9-ROW-STALE: a row left saying merged under an open pull
             request is stale, and the orchestrator re-cuts it);
  worktree   the branch is not checked out in another worktree of <checkout>,
             which would refuse the train's `git worktree add -B` (recarry);
             the holder's path is reported so the queue entry can be re-pointed;
             passed under the train's `--free-holders` when `Train.freeable`
             clears the holder (clean, at origin/<branch>), which it detaches;
  policy     `Train.policy_gate`, the train's step-5 / batch-admission early
             refusal, verbatim;
  budget     a `*_budgets.json` change lands only under the owner's review at
             the head (the train refuses to mandate-approve a budget change, so
             the review must already sit there), read by budget_raise_gate's own
             `approval` -- the gate's raise reading, mandate citation included.
  findings   every finding item the body and its `Fix review:` verdicts record
             names a valid destination (`Carry:`, finding-propagation.md), read
             by tools/audit/carry_audit.py against origin/main's roster; an
             O-brief is checked in $HPO_BRIEFS_DIR when set. This is where a
             verdict's non-blocking notes are read before they merge unowned.

`--checkout` names the checkout the train will run from (default: this tree's
root), because the worktree namespace it competes with is that checkout's.
Reads only: the instrument fetches, calls `gh` read APIs and runs the carry
comparison; it never pushes, approves, comments or merges.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

import merge_train as mt  # noqa: E402  (same directory; the train's own words)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import carry_audit as ca  # noqa: E402  (tools/audit/: the one parser of `Carry:`)

# The one status line a delivery row carries while its pull request is open
# (record_row.py writes `— **open**,` / `— **merged `<sha7>`**,`).
ROW_STATUS = re.compile(r"— \*\*([^*]+)\*\*")


class PreFlight:
    """One queue read through the train's own admission methods."""

    def __init__(self, repo: str, train: "mt.Train | None" = None,
                 checkout: Path = ROOT, bot_cured: bool = False,
                 free_holders: bool = False, dests: "ca.Dests | None" = None) -> None:
        self.repo = repo
        self.dests = dests  # carry_audit's destinations; read from origin/main on first use
        self.checkout = checkout
        # The train's own pre-flight (`merge_train.py --pre-flight`) passes
        # what it now cures itself: a bot tip (batch routes it serial, whose
        # recarry is the App push) and, under its --free-holders, a holder
        # `Train.freeable` clears. Standalone, both PARK as before.
        self.bot_cured, self.free_holders = bot_cured, free_holders
        self._tmp = tempfile.TemporaryDirectory()
        self.t = train or mt.Train(repo, Path(self._tmp.name), None, "", (), 1)

    def entry(self, item: dict) -> "tuple[str, str, str]":
        """(PASS | PARK | FAIL, step, why) for one queue entry, first refusal
        in the train's admission order; PASS carries empty step and why."""
        pr, v = item.get("pr"), item.get("verdict", "")
        try:
            pr = int(pr)
        except (TypeError, ValueError):
            return "FAIL", "queue", f"pr '{pr}' is not a number"
        if not mt.is_sha(v):
            return "FAIL", "queue", f"verdict '{v}' is not a 40-hex sha"
        code, o = self.t.run(["gh", "pr", "view", str(pr), "--repo", self.repo,
                              "--json", "state,headRefOid,headRefName"])
        pv: dict = {}
        if not code:
            try:
                pv = json.loads(o)
            except ValueError:
                code = 1
        if code or not isinstance(pv, dict):
            return "FAIL", "head", f"could not read the pull request: {o.strip()[-160:]}"
        if pv.get("state") != "OPEN":
            return "FAIL", "head", f"#{pr} is {pv.get('state')}, not open"
        h = pv.get("headRefOid") or ""
        if not mt.is_sha(h):
            return "FAIL", "head", f"could not read the head: {str(h)[:120]}"
        try:
            bot = self.t.bot_tip(h)  # the batch admits through the same read; a
        except mt.Stop as s:         # batch never recarries, so only an App push cures it
            return "PARK", s.step, s.why
        if bot and not self.bot_cured:
            s = self.t.bot_refusal(pr, h, bot)
            return "PARK", s.step, s.why
        if h != v:
            o = self.t.run(["bash", mt.tool("app_approve"), "--carry", v, h])[1]
            if "CARRY: yes" not in o:
                return "PARK", "carry", (o.strip().splitlines() or ["(no output)"])[-1][:200]
        code, base = self.t.run(["git", "merge-base", "origin/main", h])
        if code or not mt.is_sha(base.strip()):
            return "PARK", "files", "git merge-base failed: " + base.strip()[-160:]
        # --no-renames: the train's own read (a rename lists both paths).
        code, out = self.t.run(["git", "diff", "--no-renames", "--name-only", base.strip(), h])
        if code:
            return "PARK", "files", "git diff failed: " + out.strip()[-160:]
        files = out.split()
        row = f"{mt.ROW_DIR}/{pr}.md"
        if row not in files:
            return "PARK", "row", f"#{pr} has no {row} in the three-dot diff"
        if stale := self.row_stale(pr, h, row):
            return "PARK", "row", stale
        branch = item.get("branch") or pv.get("headRefName") or ""
        if holder := self.worktree_holder(branch):
            return "PARK", "recarry", holder
        try:
            self.t.policy_gate(pr, h, files)  # the batch's early refusal, verbatim
        except mt.Stop as s:
            return "PARK", s.step, s.why
        budgets = [f for f in files if f.endswith("_budgets.json")]
        if budgets and (why := self.budget_gate(pr, h, budgets)):
            return "PARK", "policy", why
        if why := self.findings_gate(pr):
            return "PARK", "findings", why
        return "PASS", "", ""

    def findings_gate(self, pr: int) -> str:
        """'' when every finding item of the body and its `Fix review:`
        verdicts is routed to a valid destination (carry_audit.audit), else
        the refusal naming the count and the first item. Fail-closed: a body,
        comment or roster read that fails refuses."""
        code, body = self.t.run(["gh", "api", f"repos/{self.repo}/pulls/{pr}", "--jq", '.body // ""'])
        if code:
            return f"the body could not be read: {body.strip()[-160:]}"
        code, o = self.t.run(["gh", "api", "--paginate", "--slurp",
                              f"repos/{self.repo}/issues/{pr}/comments?per_page=100"])
        try:
            if code:
                raise ValueError(o.strip()[-160:])
            comments = [c for page in json.loads(o) for c in page]
        except (ValueError, TypeError) as e:
            return f"the comments could not be read: {e}"
        if not ca.finding_rows(body, comments)[0]:
            return ""  # nothing to route: the roster is not read
        try:
            if self.dests is None:
                self.dests = ca.load_dests(self.checkout, "origin/main", issue_state=self.issue_state)
        except (ca.roster_lib.RosterNotFound, ValueError) as e:
            return f"the roster could not be read: {str(e)[:160]}"
        bad = [r for r in ca.audit(body, comments, self.dests)["rows"] if r["status"] != "routed"]
        if not bad:
            return ""
        r = bad[0]
        what = "; ".join(r["bad"]) if r["status"] == "bad" else re.sub(r"\s+", " ", r["text"])[:100]
        return (f"{len(bad)} finding item(s) with no valid `Carry:` (carry_audit.py pr {pr}); first: "
                f"{r['where']} item {r['id']} ({r['status']}): {what}")

    def issue_state(self, n: int) -> "str | None":
        code, o = self.t.run(["gh", "api", f"repos/{self.repo}/issues/{n}", "--jq", ".state"])
        return o.strip() or None if not code else None

    def row_stale(self, pr: int, h: str, row: str) -> str:
        """R9-ROW-STALE: '' when the row's status line agrees with the open
        pull request, else the reason it is stale."""
        code, o = self.t.run(["git", "show", f"{h}:{row}"])
        if code:
            return f"the delivery row could not be read at the head: {o.strip()[-120:]}"
        m = ROW_STATUS.search(o)
        if not m:
            return "the delivery row carries no — **status** field"
        if m.group(1).strip() != "open":
            return (f"the delivery row reads **{m.group(1).strip()}**, the pull request is "
                    "open (R9-ROW-STALE: re-cut the row before the train admits it)")
        return ""

    def worktree_holder(self, branch: str) -> str:
        """'' when no worktree of <checkout> holds <branch>, else the refusal
        naming the holder's path."""
        if not branch:
            return ""
        code, o = self.t.run(["git", "-C", str(self.checkout),
                              "worktree", "list", "--porcelain"])
        if code:
            return (f"the worktree list at {self.checkout} could not be read: "
                    f"{o.strip()[-120:]}")
        holder, held = "", None
        for line in o.splitlines():
            if line.startswith("worktree "):
                holder = line[len("worktree "):]
            elif line.startswith("branch refs/heads/") and line[len("branch refs/heads/"):] == branch:
                held = holder
        if held is not None and not (self.free_holders and self.t.freeable(held, branch) is None):
            return (f"{branch} is already checked out at {held}; the train's "
                    "`git worktree add -B` would refuse it -- re-point the "
                    "queue entry's worktree")
        return ""

    def budget_gate(self, pr: int, h: str, budgets: "list[str]") -> str:
        """'' when the owner's review sits at <h> citing an in-force mandate
        (budget_raise_gate's own raise reading), else the refusal."""
        note = f"budget files changed ({', '.join(budgets)})"
        code, o = self.t.run(["gh", "api", "--paginate", "--slurp",
                              f"repos/{self.repo}/pulls/{pr}/reviews?per_page=100"])
        if code:
            return f"{note}: the reviews could not be read: {o.strip()[-160:]}"
        try:
            reviews = [r for page in json.loads(o) for r in page]
            g = mt._mandate_gate()

            def mandate_fn(cid):
                return self.t._mandate_read(cid)
            ok, why = g.approval(reviews, h, mandate_fn)  # the gate's raise reading
        except mt.Stop as s:
            return f"{note}: {s.step}: {s.why}"
        except Exception as e:  # fail closed: an unread approval raises nothing
            return f"{note}: the budget read failed ({str(e).splitlines()[0][:160] if str(e) else type(e).__name__})"
        if not ok:
            return (f"{note}: the owner's review does not sit at this head ({why}); "
                    "a raise is the owner's (0013)")
        return ""


def run_queue(pf: PreFlight, queue: "list[dict]") -> "tuple[list[dict], bool]":
    """Print one line per entry and the summary; (rows, all-passed)."""
    rows: "list[dict]" = []
    for item in queue:
        status, step, why = pf.entry(item)
        pr = item.get("pr")
        print(f"#{pr} {status}" + (f" ({step}: {why})" if step else ""))
        rows.append({"pr": pr, "status": status, "step": step, "reason": why})
    n = len(rows)
    p = sum(r["status"] == "PASS" for r in rows)
    k = sum(r["status"] == "PARK" for r in rows)
    f = sum(r["status"] == "FAIL" for r in rows)
    print(f"PRE-FLIGHT: {n} entries: {p} PASS, {k} PARK, {f} FAIL")
    return rows, n > 0 and p == n


def main(argv: "list[str]") -> int:
    if argv[:1] == ["--self-test"]:
        return _self_test()
    p = argparse.ArgumentParser(prog="queue_pre_flight.py")
    p.add_argument("queue")
    p.add_argument("--repo", default="tvofi/heatpump_optimizer")
    p.add_argument("--checkout", default=str(ROOT),
                   help="the checkout the train will run from; its worktree "
                        "list is the one the train's worktree add competes with")
    p.add_argument("--json", action="store_true", dest="as_json")
    a = p.parse_args(argv)
    queue = json.loads(Path(a.queue).read_text())
    pf = PreFlight(a.repo, checkout=Path(a.checkout))
    rows, clean = run_queue(pf, queue)
    if a.as_json:
        print(json.dumps({"repo": a.repo, "entries": rows,
                          "all_pass": clean}))
    return 0 if clean else 1


def _self_test() -> int:
    passed = failed = 0
    H0, H1 = "a" * 40, "b" * 40
    ROW = f"{mt.ROW_DIR}/7.md"

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + bool(cond), failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    def fake(world: dict):
        def run(argv, cwd=None, stdin=None):
            a = " ".join(argv)
            if argv[:3] == ["gh", "pr", "view"]:
                if world.get("pr_read_breaks"):
                    return 1, "gh: HTTP 500"
                return 0, json.dumps({"state": world.get("pr_state", "OPEN"),
                                      "headRefOid": world.get("pr_head", H0),
                                      "headRefName": world.get("pr_branch", "fix/x")})
            if argv[:2] == ["gh", "api"] and "/commits/" in a:
                sha = a.split("/commits/")[1].split(" ")[0]
                tip = world.get("bot_tips", {}).get(sha)
                if tip is not None:
                    return 0, f"github-actions[bot]\t{tip}"
                if world.get("bot_read_breaks"):
                    return 1, "gh: HTTP 502"
                return 0, f"tvofi\tfix: x ({sha[:7]})"
            if "--carry" in a:
                return 0, world.get("carry", "CARRY: yes only automatic merges")
            if argv[:2] == ["git", "fetch"]:
                return 0, ""
            if "merge-base" in argv:
                if world.get("no_base"):
                    return 1, "fatal: no merge base"
                return 0, "e" * 40
            if "--no-renames" in argv and "--name-only" in argv:
                if world.get("diff_fail"):
                    return 1, "fatal: bad object"
                return 0, "\n".join(world.get("files", ["custom_components/x.py", ROW]))
            if argv[:2] == ["git", "show"]:
                return 0, world.get("row_text", f"- [#7](https://example.test/7) — **open**, t")
            if "status" in argv and "--porcelain" in argv:  # Train.freeable's reads
                return 0, world.get("holder_status", "")
            if argv[:3] == ["git", "-C", "/somewhere/wt"] and "rev-parse" in argv:
                return 0, "1" * 40
            if argv[:2] == ["git", "rev-parse"]:
                return 0, world.get("origin_tip", "1" * 40)
            if "worktree" in argv and "--porcelain" in argv:
                if world.get("wt_fail"):
                    return 1, "fatal: not a git repository"
                return 0, world.get("worktrees", "")
            if "--corpus-filter" in argv:
                return 0, "\n".join(f for f in (stdin or "").split()
                                    if f in ("CLAUDE.md", "AGENTS.md",
                                             "dev/governance/roles/fixer.md"))
            if argv[:2] == ["gh", "api"] and "/reviews" in a:
                if world.get("reviews_fail"):
                    return 1, "gh: HTTP 403"
                return 0, json.dumps([world.get("reviews", [])])
            if argv[:2] == ["gh", "api"] and "/issues/comments/" in a:
                return (0, json.dumps(world["mandate"])) if world.get("mandate") \
                    else (1, "gh: Not Found (HTTP 404)")
            if argv[:2] == ["gh", "api"] and "/issues/201/comments" in a:
                return 0, json.dumps([world.get("thread", [])])
            if argv[:2] == ["gh", "api"] and "/issues/7/comments" in a:
                if world.get("comments_fail"):
                    return 1, "gh: HTTP 502"
                return 0, json.dumps([world.get("comments", [])])
            if argv[:2] == ["gh", "api"] and a.endswith("/pulls/7 --jq .body // \"\""):
                return 0, world.get("body", "")
            return 0, ""
        return run

    _g, owner_review, mandate, revoke = mt.policy_fixture_builders()
    NOW = datetime.datetime.now(datetime.timezone.utc)

    def go(world: "dict | None" = None, verdict: str = H0, **opts) -> "tuple[str, str, str]":
        w = dict(world or {})
        with tempfile.TemporaryDirectory() as d:
            opts.setdefault("dests", ca.Dests({"groups": [
                {"group": "R10-LIVE", "issues": [], "fixes": [], "resume": {"stage": "planned"}},
                {"group": "R10-OVER", "issues": [], "fixes": [], "resume": {"stage": "done"}}]}, set()))
            pf = PreFlight("o/r", train=mt.Train("o/r", Path(d), None, "", (), 1,
                                                 run=fake(w)), checkout=Path(d), **opts)
            return pf.entry({"pr": 7, "verdict": verdict, "branch": "fix/x"})

    check("null control: an open, verdicted, rowed, non-policy entry passes",
          go() == ("PASS", "", ""))
    check("a verdict that is not 40-hex is a FAIL, the train's queue wording",
          go(verdict="xyz") == ("FAIL", "queue", "verdict 'xyz' is not a 40-hex sha"))
    check("a pull request that is not open is a FAIL",
          go({"pr_state": "MERGED"})[:2] == ("FAIL", "head")
          and "MERGED" in go({"pr_state": "MERGED"})[2])
    check("an unreadable pull request is a FAIL",
          go({"pr_read_breaks": True})[:2] == ("FAIL", "head"))
    check("a verdict that does not carry to the head PARKs with the carry line",
          go({"pr_head": H1, "carry": "CARRY: no c1 -> c2: a commit of the branch's own"})[:2] == ("PARK", "carry")
          and "branch's own" in go({"pr_head": H1, "carry": "CARRY: no c1 -> c2: a commit of the branch's own"})[2])
    check("a carried head behind the verdict passes (the carry pass arm)",
          go({"pr_head": H1, "carry": "CARRY: yes only automatic merges"}) == ("PASS", "", ""))
    check("a head whose tip is a GITHUB_TOKEN push PARKs for recarry",
          go({"bot_tips": {H0: "ci: pin killed mutants"}})[:2] == ("PARK", "ci")
          and "GITHUB_TOKEN" in go({"bot_tips": {H0: "ci: pin killed mutants"}})[2])
    check("a head whose author cannot be read PARKs, named as unreadable",
          go({"bot_read_breaks": True})[:2] == ("PARK", "ci") and "could not be read" in go({"bot_read_breaks": True})[2])
    check(f"a pull request with no {ROW} row PARKs, the train's row wording",
          go({"files": ["custom_components/x.py"]})[:2] == ("PARK", "row")
          and ROW in go({"files": ["custom_components/x.py"]})[2])
    check("a row left saying merged under an open pull request PARKs (R9-ROW-STALE)",
          go({"row_text": "- [#7](https://example.test/7) — **merged `abc1234`**, t"})[:2] == ("PARK", "row")
          and "R9-ROW-STALE" in go({"row_text": "- [#7](https://example.test/7) — **merged `abc1234`**, t"})[2])
    check("a row with no status line PARKs",
          go({"row_text": "- [#7](https://example.test/7) t"})[:2] == ("PARK", "row"))
    check("a branch held by another worktree PARKs with the holder's path",
          go({"worktrees": f"worktree /somewhere/wt\nHEAD {H1}\nbranch refs/heads/fix/x\n\n"})[:2] == ("PARK", "recarry")
          and "/somewhere/wt" in go({"worktrees": f"worktree /somewhere/wt\nHEAD {H1}\nbranch refs/heads/fix/x\n\n"})[2])
    BOTW = {"bot_tips": {H0: "ci: pin killed mutants"}}
    check("the train's own pre-flight (bot_cured) passes a bot tip: the train cures it by its recarry",
          go(BOTW, bot_cured=True) == ("PASS", "", ""))
    HELD = {"worktrees": f"worktree /somewhere/wt\nHEAD {'1' * 40}\nbranch refs/heads/fix/x\n\n"}
    check("under the train's --free-holders a clean holder at origin/<branch> passes (the train detaches it)",
          go(HELD, free_holders=True) == ("PASS", "", ""))
    check("... a dirty holder still PARKs under --free-holders",
          go({**HELD, "holder_status": "?? note.md\n"}, free_holders=True)[:2] == ("PARK", "recarry"))
    check("... and one whose HEAD is not origin/<branch> still PARKs (unpushed work)",
          go({**HELD, "origin_tip": "2" * 40}, free_holders=True)[:2] == ("PARK", "recarry"))
    check("a worktree list that cannot be read PARKS, named as unreadable",
          go({"wt_fail": True})[:2] == ("PARK", "recarry"))
    POL = {"files": ["custom_components/x.py", ROW, "dev/governance/roles/fixer.md"]}
    check("a policy head whose owner approval at this head cites a mandate in force passes",
          go({**POL, "reviews": [owner_review(H0, NOW)], "mandate": mandate(NOW)}) == ("PASS", "", ""))
    check("a policy head with no mandate citation PARKs with the train's policy wording",
          go({**POL, "reviews": [owner_review(H0, NOW, cite=False)], "mandate": mandate(NOW)})[:2] == ("PARK", "policy")
          and "cites no mandate" in go({**POL, "reviews": [owner_review(H0, NOW, cite=False)], "mandate": mandate(NOW)})[2])
    check("a policy head with no owner review at its head PARKs, named as the review",
          go({**POL, "reviews": [], "mandate": mandate(NOW)})[:2] == ("PARK", "policy")
          and "no decisive review" in go({**POL, "reviews": [], "mandate": mandate(NOW)})[2])
    check("a policy head whose mandate was revoked PARKS, named as revoked",
          go({**POL, "reviews": [owner_review(H0, NOW)], "mandate": mandate(NOW),
              "thread": [revoke()]})[:2] == ("PARK", "policy"))
    BUD = {"files": ["tests/structure_budgets.json", ROW]}
    check("a budget head whose owner approval cites an in-force mandate passes",
          go({**BUD, "reviews": [owner_review(H0, NOW)], "mandate": mandate(NOW)}) == ("PASS", "", ""))
    check("a budget head without the owner's review at its head PARKS, named as the raise",
          go({**BUD, "reviews": [], "mandate": mandate(NOW)})[:2] == ("PARK", "policy")
          and "budget" in go({**BUD, "reviews": [], "mandate": mandate(NOW)})[2])
    check("a budget head whose mandate was revoked PARKS",
          go({**BUD, "reviews": [owner_review(H0, NOW)], "mandate": mandate(NOW),
              "thread": [revoke()]})[:2] == ("PARK", "policy"))
    check("a budget head whose reviews cannot be read PARKS, fail-closed",
          go({**BUD, "reviews_fail": True, "mandate": mandate(NOW)})[:2] == ("PARK", "policy"))
    FR = "## Head\n\nx\n\n## Friction\n\n- fixer.md: unclear: a disposition pins nothing."
    check("a body whose Friction finding names no destination PARKs on findings",
          go({"body": FR})[:2] == ("PARK", "findings") and "unrouted" in go({"body": FR})[2])
    check("... the same body with `Carry:` to a live group passes (null control)",
          go({"body": FR + " Carry: R10-LIVE"}) == ("PASS", "", ""))
    check("... and with `Carry:` to a done group PARKs, naming it",
          go({"body": FR + " Carry: R10-OVER"})[:2] == ("PARK", "findings")
          and "R10-OVER is done" in go({"body": FR + " Carry: R10-OVER"})[2])
    NOTE = [{"id": 9, "body": "Fix review: merge " + H0 + "\n\nNon-blocking observation: x re-books."}]
    check("a verdict's non-blocking note with no destination PARKs on findings",
          go({"comments": NOTE})[:2] == ("PARK", "findings") and "review 9" in go({"comments": NOTE})[2])
    check("comments that cannot be read PARK, fail-closed",
          go({"comments_fail": True})[:2] == ("PARK", "findings"))
    check("a merge base that cannot be read PARKS, named as the failure",
          go({"no_base": True})[:2] == ("PARK", "files"))
    check("a diff that cannot be read PARKS, named as the failure",
          go({"diff_fail": True})[:2] == ("PARK", "files"))

    # The queue loop and its output contract, over a stubbed PreFlight.
    class Stub(PreFlight):
        def __init__(self, results: "list[tuple[str, str, str]]") -> None:
            self.results = results

        def entry(self, item):
            return self.results.pop(0)

    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rows, clean = run_queue(Stub([("PASS", "", ""), ("PARK", "row", "x"), ("FAIL", "head", "y")]),
                                [{"pr": 7}, {"pr": 8}, {"pr": 9}])
    text = buf.getvalue()
    check("the queue prints one line per entry and the summary, and is not clean",
          rows[1]["status"] == "PARK" and rows[2]["status"] == "FAIL"
          and "#8 PARK (row: x)" in text and "#9 FAIL (head: y)" in text
          and "PRE-FLIGHT: 3 entries: 1 PASS, 1 PARK, 1 FAIL" in text
          and clean is False)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rows, clean = run_queue(Stub([("PASS", "", "")]), [{"pr": 7}])
    check("an all-PASS queue is clean (the summary's null control)",
          clean is True and "PRE-FLIGHT: 1 entries: 1 PASS, 0 PARK, 0 FAIL" in buf.getvalue())

    # The file this instrument delegates to is the tree's own train.
    check("the train this instrument mirrors is in the tree",
          (ROOT / "tools/audit/seat/merge_train.py").is_file())
    check(f"the delivery-row directory the train requires, {mt.ROW_DIR}/, is in the tree",
          (ROOT / mt.ROW_DIR).is_dir())
    check("the mandate reader the budget arm reads is in the tree",
          any((ROOT / c).is_file() for c in mt.GATE_PATHS))

    print(f"queue_pre_flight self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))

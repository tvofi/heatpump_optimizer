#!/usr/bin/env python3
"""The merge train: land a queue of verdicted pull requests, one at a time.

    python3 tools/audit/seat/merge_train.py run <queue.json> [--mandate LABEL]
        [--approver-role ROLE] [--ignore-red NAME]... [--repo OWNER/REPO]
        [--state-dir DIR] [--min-runs N]
    python3 tools/audit/seat/merge_train.py wait-ci <40-hex sha> [--min-runs N]
    python3 tools/audit/seat/merge_train.py --self-test

The queue is a JSON list, merged in order:

    [{"pr": 1869, "verdict": "<40-hex head the merge verdict names>",
      "verdict_comment": "<the verdict comment's id, quoted in a mandate approval>",
      "branch": "<optional; read from the pull request>",
      "worktree": "<optional; a detached one is made under the state directory>",
      "issues": [<optional; the issues the body intends to close, for preflight>]}]

PER PULL REQUEST, IN ORDER; THE TRAIN STOPS AT THE FIRST REFUSAL, because every
later pull request would be graded against a `main` the refused one never joined:
  1. recarry  -- a head that does not contain `origin/main` gets main merged in by
                 `remerge_main.sh` (an automatic merge, no resolution); a conflict
                 or a push that did not land stops the train;
  2. ci       -- every check run at the head completes (all pages, at least
                 --min-runs); a latest run that is not success, skipped or
                 neutral stops it, except the `--ignore-red` names (default
                 `nightly-status`, which grades `main`, not the head);
  3. carry    -- `app_approve.sh --carry <verdict> <head>` must say `CARRY: yes`:
                 the head differs from the verdicted one only by automatic merges;
  4. main     -- `origin/main` is still inside the head after CI (else main moved);
  5. policy   -- no changed file (`--no-renames`, so a rename names the path it
                 left; a failing merge-base or diff stops the train) is policy, as `policy_lint.mjs --corpus-filter`
                 defines it (probed with a sentinel pair first, as preflight.sh
                 does). A POLICY PULL REQUEST IS NEVER APPROVED HERE, by the App
                 or under a mandate: it waits for the owner's own review;
  6. approve  -- `app_approve.sh` at the head. When its refusal is exactly its own
                 code-owned line for this pull request (anchored: a blocked
                 verdict's echoed reason can carry the same words), and `--mandate` was given,
                 the train approves as the account `gh` is logged in as, with a
                 body naming the mandate label, the role, the verdict comment and
                 the carried head. Without `--mandate`, or on any other refusal
                 (missing evidence included), or when a `*_budgets.json` changed
                 (a raise is the owner's, 0013), it stops;
  7. ready, preflight of the title (`REFUSE` stops), merge with
     `--match-head-commit` (retried; `main` re-checked before each attempt),
     the closing-issue read-back, and `worktree_gc.sh`.

It prints one line per step and ends `TRAIN DONE` or `TRAIN STOPPED #<pr> <step>:
<reason>` (exit 1). Every GitHub write is the orchestrator's: run this only
from the orchestrator's machine and identity (decisions 0011, 0013).
Replaces the session-local train3.py / mergewhen.sh / waitci.sh of round 9;
the stale-base guard mergewhen.sh carried is subsumed by step 4, which refuses
any head that does not contain the `main` it merges into.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HEX = frozenset("0123456789abcdef")


def is_sha(s: str) -> bool:
    return len(s) == 40 and set(s) <= HEX
GREEN = ("success", "skipped", "neutral")


class Stop(Exception):
    def __init__(self, step: str, why: str) -> None:
        super().__init__(f"{step}: {why}")
        self.step, self.why = step, why


class Train:
    def __init__(self, repo: str, state: Path, mandate: str | None, role: str,
                 ignore: tuple[str, ...], min_runs: int, run=None, sleep=time.sleep,
                 log=print, polls: int = 120, merge_tries: int = 8) -> None:
        self.repo, self.state, self.mandate, self.role = repo, state, mandate, role
        self.ignore, self.min_runs, self.polls, self.merge_tries = ignore, min_runs, polls, merge_tries
        self.run = run or self._run
        self.sleep, self.log = sleep, log

    @staticmethod
    def _run(argv: list[str], cwd: Path = ROOT, stdin: str | None = None) -> tuple[int, str]:
        r = subprocess.run(argv, cwd=cwd, input=stdin, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def out(self, *argv: str, cwd: Path = ROOT, stdin: str | None = None) -> str:
        return self.run(list(argv), cwd=cwd, stdin=stdin)[1].strip()

    def ok(self, *argv: str, cwd: Path = ROOT) -> bool:
        return self.run(list(argv), cwd=cwd)[0] == 0

    def head(self, pr: int) -> str:
        return self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "headRefOid", "--jq", ".headRefOid")

    def contains_main(self, h: str) -> bool:
        self.run(["git", "fetch", "-q", "origin", "main", h])
        return self.ok("git", "merge-base", "--is-ancestor", "origin/main", h)

    def wait_ci(self, h: str) -> list[str]:
        """The names whose latest run at <h> is not green, once every run completed.

        Green is a fixed list -- success, skipped, neutral -- so a conclusion
        GitHub adds later, or `action_required` and `stale` today, reads red."""
        for _ in range(self.polls):
            # One JSON object per line across every page: past 100 runs a head
            # would otherwise read as complete on its first page alone.
            code, raw = self.run(["gh", "api", "--paginate", "--jq", ".check_runs[]",
                                  f"repos/{self.repo}/commits/{h}/check-runs?per_page=100"])
            try:
                runs = [json.loads(x) for x in raw.splitlines() if x.strip()] if code == 0 else None
            except ValueError:
                runs = None
            if runs and len(runs) >= self.min_runs and all(c.get("status") == "completed" for c in runs):
                last: dict[str, dict] = {}
                for c in sorted(runs, key=lambda c: c.get("started_at") or ""):
                    last[c["name"]] = c
                return sorted(n for n, c in last.items() if c["conclusion"] not in GREEN)
            self.sleep(60)
        return ["TIMEOUT"]

    def policy_paths(self, files: list[str]) -> list[str]:
        filt = ["node", str(ROOT / ".claude/workflows/policy_lint.mjs"), "--corpus-filter"]
        probe = self.run(filt, stdin="CLAUDE.md\ntools/audit/not-a-policy-path.zzz\n")[1].split()
        if probe != ["CLAUDE.md"]:
            raise Stop("policy", "policy_lint.mjs --corpus-filter failed its sentinel probe, so what is policy is undefined here")
        return self.run(filt, stdin="".join(f + "\n" for f in files))[1].split()

    def approve(self, pr: int, h: str, item: dict, files: list[str]) -> str:
        code, o = self.run(["bash", "tools/audit/app_approve.sh", self.repo, str(pr), h])
        if code == 0 and "REFUSE" not in o:
            return "app"
        # Only app_approve.sh's own code-owned refusal line, anchored and for this
        # pull request: a blocked verdict's echoed reason can carry the same words.
        owned = re.search(r"(?m)^app_approve: REFUSE: #%d touches code-owned paths \(([^)]*)\);" % pr, o)
        if owned is None:
            raise Stop("approve", "app_approve.sh refused: " + (o.splitlines() or ["(no output)"])[-1][:200])
        if not self.mandate:
            raise Stop("approve", f"code-owned ({owned.group(1).strip()}) and no --mandate given: the owner's review")
        budgets = [f for f in files if f.endswith("_budgets.json")]
        if budgets:
            raise Stop("approve", f"code-owned and a budget file changed ({', '.join(budgets)}): a raise is the owner's (0013)")
        paths = ", ".join(f"`{p}`" for p in owned.group(1).split())
        body = (f"Agent approval for code-owned {paths}, given by {self.role} under {self.mandate}, at head {h}.\n\n"
                f"Basis: `Fix review: merge {item['verdict']}` (comment {item.get('verdict_comment', '?')}), carried to {h} "
                f"by `app_approve.sh --carry` (automatic main merges only). CI at {h} is green"
                + (f" apart from {', '.join('`%s`' % n for n in self.ignore)}, which grade main." if self.ignore else ".") + "\n")
        bf = self.state / f"approve{pr}.md"
        bf.write_text(body)
        if self.head(pr) != h:
            raise Stop("approve", "head moved before the mandate approval")
        code, o = self.run(["gh", "pr", "review", str(pr), "--repo", self.repo, "--approve", "--body-file", str(bf)])
        if code:
            raise Stop("approve", "the mandate review was refused: " + o[-200:])
        return "mandate"

    def one(self, item: dict) -> None:
        pr, v = int(item["pr"]), item["verdict"]
        if not is_sha(v):
            raise Stop("queue", f"verdict '{v}' is not a 40-hex sha")
        h = self.head(pr)
        if not is_sha(h):
            raise Stop("head", f"could not read the head: {h[:120]}")
        if not self.contains_main(h):
            br = item.get("branch") or self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "headRefName", "--jq", ".headRefName")
            wt = Path(item.get("worktree") or self.state / "wt" / str(pr))
            if not wt.exists():
                self.run(["git", "fetch", "-q", "origin", br])
                if not self.ok("git", "worktree", "add", "-q", "--detach", str(wt), f"origin/{br}"):
                    raise Stop("recarry", f"could not make a worktree at {wt}")
            body = self.state / f"rb{pr}.md"
            body.write_text(self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "body", "--jq", ".body") + "\n")
            code, o = self.run(["bash", "tools/audit/seat/remerge_main.sh", str(pr), str(wt), br, str(body)])
            if "MERGE CONFLICT" in o:
                raise Stop("recarry", "main does not merge without a resolution; that is a fixer's, and a re-review")
            if "PUSHED" not in o:
                raise Stop("recarry", "the main merge pushed nothing: " + o.strip()[-200:])
            h = self.head(pr)
            self.log(f"#{pr} recarry: main merged, head {h[:8]}")
        red = [n for n in self.wait_ci(h) if n not in self.ignore]
        self.log(f"#{pr} {h[:8]} ci red={red}")
        if red:
            raise Stop("ci", "red at the head: " + ", ".join(red))
        self.run(["git", "fetch", "-q", "origin", h])
        o = self.run(["bash", "tools/audit/app_approve.sh", "--carry", v, h])[1]
        if "CARRY: yes" not in o:
            raise Stop("carry", (o.strip().splitlines() or ["(no output)"])[-1][:200])
        if not self.contains_main(h):
            raise Stop("main", "origin/main moved during CI and is not in the head; run the train again")
        code, base = self.run(["git", "merge-base", "origin/main", h])
        if code or not is_sha(base.strip()):
            raise Stop("files", "git merge-base failed: " + base.strip()[-160:])
        # --no-renames: a rename lists both paths, so moving a policy file out of
        # the corpus still names the policy path it left.
        code, out = self.run(["git", "diff", "--no-renames", "--name-only", base.strip(), h])
        if code:
            raise Stop("files", "git diff failed: " + out.strip()[-160:])
        files = out.split()
        pol = self.policy_paths(files)
        if pol:
            raise Stop("policy", f"policy paths changed ({', '.join(pol)}): only the owner's own review approves it")
        if self.head(pr) != h:
            raise Stop("approve", "head moved")
        self.log(f"#{pr} approved ({self.approve(pr, h, item, files)})")
        self.run(["gh", "pr", "ready", str(pr), "--repo", self.repo])
        title = self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "title", "--jq", ".title")
        pf = self.run(["bash", "tools/audit/preflight.sh", *map(str, item.get("issues", []))], stdin=title + "\n")[1]
        if re.search(r"(?m)^\s*REFUSE\b", pf) or not re.search(r"(?m)^\s*clean\b", pf):
            raise Stop("preflight", "the title did not pass preflight.sh: " + pf.strip()[-200:])
        for _ in range(self.merge_tries):
            self.sleep(30)
            if not self.contains_main(h):
                raise Stop("merge", "origin/main moved before the merge; run the train again")
            self.run(["gh", "pr", "merge", str(pr), "--repo", self.repo, "--merge", "--match-head-commit", h])
            st = self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "state,mergeCommit",
                          "--jq", '"\\(.state) \\(.mergeCommit.oid)"')
            if st.startswith("MERGED"):
                self.log(f"#{pr} {st}")
                break
        else:
            raise Stop("merge", f"not merged after {self.merge_tries} attempts")
        owner, name = self.repo.split("/")
        q = ('query={repository(owner:"%s",name:"%s"){pullRequest(number:%d){closingIssuesReferences(first:10)'
             "{nodes{number state}}}}}" % (owner, name, pr))
        self.log(f"#{pr} closes {self.out('gh', 'api', 'graphql', '-f', q)[-160:]}")
        self.run(["bash", "tools/audit/worktree_gc.sh", self.repo])

    def train(self, queue: list[dict]) -> int:
        self.state.mkdir(parents=True, exist_ok=True)
        for item in queue:
            try:
                self.one(item)
            except Stop as s:
                self.log(f"TRAIN STOPPED #{item.get('pr')} {s.step}: {s.why}")
                return 1
        self.log("TRAIN DONE")
        return 0


# ----------------------------------------------------------------- self-test
def _self_test() -> int:
    passed = failed = 0
    H0, H1, V = "a" * 40, "b" * 40, "c" * 40

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + cond, failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    def fake(world: dict):
        calls: list[list[str]] = []

        def run(argv, cwd=ROOT, stdin=None):
            calls.append(argv)
            a = " ".join(argv)
            if argv[:3] == ["gh", "pr", "view"] and "headRefOid" in a:
                return 0, world["heads"].pop(0) if len(world["heads"]) > 1 else world["heads"][0]
            if "merge-base --is-ancestor" in a:
                return (0 if world["contains"].pop(0) else 1) if world["contains"] else 0, ""
            if "remerge_main.sh" in a:
                return 0, world.get("remerge", "PUSHED")
            if "check-runs" in a:
                return 0, "\n".join(json.dumps(c) for c in world.get("runs", []))
            if argv[:3] == ["git", "merge-base", "origin/main"]:
                return world.get("base", (0, "e" * 40 + "\n"))
            if "--carry" in a:
                return 0, world.get("carry", "CARRY: yes")
            if argv[:2] == ["git", "diff"]:
                if "diff_fail" in world:
                    return world["diff_fail"]
                if "renamed" in world:  # git lists a rename's old path only with --no-renames
                    old, new = world["renamed"]
                    return 0, f"{old}\n{new}" if "--no-renames" in argv else new
                return 0, "\n".join(world.get("files", ["custom_components/x.py"]))
            if "--corpus-filter" in a:
                if world.get("broken_filter"):
                    return 0, ""
                return 0, "\n".join(f for f in (stdin or "").split() if f in ("CLAUDE.md", "AGENTS.md", "tools/audit/briefs/fixer.md"))
            if "app_approve.sh" in a:
                return world.get("approve", (0, "APPROVED"))
            if argv[:3] == ["gh", "pr", "review"]:
                return 0, "reviewed"
            if "preflight.sh" in a:
                return 0, world.get("preflight", "  clean    no refusal")
            if "state,mergeCommit" in a:
                return 0, world["merge"].pop(0) if world.get("merge") else "MERGED " + "d" * 40
            return 0, ""
        return run, calls

    green = [{"name": "fast", "status": "completed", "conclusion": "success", "started_at": "1"},
             {"name": "nightly-status", "status": "completed", "conclusion": "failure", "started_at": "1"}]
    item = {"pr": 7, "verdict": V, "verdict_comment": "42", "worktree": "/nonexistent-wt", "branch": "fix/x"}

    def go(world: dict, mandate: str | None = None, q=None, min_runs: int = 1) -> tuple[int, list[str], list[list[str]]]:
        world.setdefault("heads", [H0])
        world.setdefault("contains", [])
        world.setdefault("runs", green)
        lines: list[str] = []
        run, calls = fake(world)
        with tempfile.TemporaryDirectory() as d:
            rc = Train("o/r", Path(d), mandate, "the orchestrator", ("nightly-status",), min_runs, run=run,
                       sleep=lambda s: None, log=lines.append, polls=2, merge_tries=3).train(q or [dict(item)])
            world["approve_body"] = (Path(d) / "approve7.md").read_text() if (Path(d) / "approve7.md").exists() else ""
        return rc, lines, calls

    def merged(calls) -> bool:
        return any(c[:3] == ["gh", "pr", "merge"] for c in calls)

    def approved(calls) -> bool:
        return any(c[:3] == ["gh", "pr", "review"] for c in calls)

    rc, lines, calls = go({})
    check("a green, carried, non-policy pull request merges (null control)", rc == 0 and merged(calls) and lines[-1] == "TRAIN DONE")
    check("nightly-status red is ignored by default", "red=[]" in " ".join(lines))
    rc, lines, calls = go({"runs": green + [{"name": "typing", "status": "completed", "conclusion": "failure", "started_at": "1"}]})
    check("a red required check stops the train before any approval", rc == 1 and "ci:" in lines[-1] and not merged(calls)
          and not any("app_approve.sh" in " ".join(c) and "--carry" not in c for c in calls))
    rc, lines, calls = go({"runs": [{"name": "fast", "status": "completed", "conclusion": "failure", "started_at": "1"},
                                    {"name": "fast", "status": "completed", "conclusion": "success", "started_at": "2"}]})
    check("a re-run that went green supersedes the earlier red", rc == 0 and merged(calls))
    rc, lines, calls = go({"runs": [{"name": "fast", "status": "in_progress", "conclusion": None, "started_at": "1"}]})
    check("CI that never completes stops it as TIMEOUT", rc == 1 and "TIMEOUT" in lines[-1])
    rc, lines, calls = go({"carry": "CARRY: no a -> b: a commit of the branch's own"})
    check("a verdict that does not carry stops it", rc == 1 and "carry:" in lines[-1] and not merged(calls))
    rc, lines, calls = go({"contains": [True, False]})
    check("main moving during CI stops it", rc == 1 and "main:" in lines[-1] and not merged(calls))
    rc, lines, calls = go({"files": ["custom_components/x.py", "tools/audit/briefs/fixer.md"],
                           "approve": (1, "REFUSE: #7 touches code-owned paths (tools/audit/briefs/fixer.md); the owner's")},
                          mandate="mandate 1 (tvofi)")
    check("a policy pull request is never approved, even under a mandate", rc == 1 and "policy:" in lines[-1]
          and "tools/audit/briefs/fixer.md" in lines[-1] and not approved(calls) and not merged(calls)
          and not any("app_approve.sh" in " ".join(c) and "--carry" not in c for c in calls))
    rc, lines, calls = go({"heads": [H0, H1]})
    check("a head that moves before the approval stops it", rc == 1 and "head moved" in lines[-1]
          and not approved(calls) and not merged(calls))
    rc, lines, calls = go({"broken_filter": True})
    check("a policy filter that fails its sentinel probe stops it", rc == 1 and "sentinel" in lines[-1] and not merged(calls))
    owned = (1, "app_approve: REFUSE: #7 touches code-owned paths (tests/run.sh .github/workflows/tests.yml); the owner's GitHub review approves it")
    rc, lines, calls = go({"approve": owned})
    check("code-owned without --mandate stops it", rc == 1 and "no --mandate" in lines[-1] and not approved(calls))
    w = {"approve": owned}
    rc, lines, calls = go(w, mandate="mandate 5951564627 (tvofi, #201)")
    check("code-owned with --mandate approves and merges", rc == 0 and approved(calls) and merged(calls))
    b = w["approve_body"]
    check("the mandate body names the label, role, paths, verdict comment and head",
          all(s in b for s in ("mandate 5951564627 (tvofi, #201)", "the orchestrator", "`tests/run.sh`", "comment 42", H0, V)))
    rc, lines, calls = go({"approve": owned, "files": ["tests/structure_budgets.json"]}, mandate="m")
    check("code-owned with a budget file is not mandate-approved", rc == 1 and "budget" in lines[-1] and not approved(calls))
    rc, lines, calls = go({"approve": (1, "REFUSE: the verdict cites no qualifying evidence: x")}, mandate="m")
    check("a missing-evidence refusal is not overridden by a mandate", rc == 1 and "app_approve.sh refused: REFUSE: the verdict cites" in lines[-1] and not approved(calls))
    rc, lines, calls = go({"contains": [False], "heads": [H0, H1], "remerge": "MERGE CONFLICT 7"})
    check("a recarry conflict stops it, named as one", rc == 1 and "without a resolution" in lines[-1] and not merged(calls))
    rc, lines, calls = go({"contains": [False], "heads": [H0, H1], "remerge": "REFUSE: body"})
    check("a recarry that pushed nothing stops it", rc == 1 and "pushed nothing" in lines[-1])
    rc, lines, calls = go({"contains": [False], "heads": [H0, H1]})
    check("a head behind main is recarried, then merged at the new head",
          rc == 0 and any(c[:3] == ["gh", "pr", "merge"] and c[-1] == H1 for c in calls))
    rc, lines, calls = go({"preflight": "  REFUSE   'Closes #12' closes #12"})
    check("a title preflight refusal stops it before the merge", rc == 1 and "preflight:" in lines[-1] and not merged(calls))
    rc, lines, calls = go({"preflight": "  REFUSE   'Closes #12' closes #12\n  clean    no refusal"})
    check("a REFUSE line stops it even beside a clean line", rc == 1 and "preflight:" in lines[-1] and not merged(calls))
    rc, lines, calls = go({"merge": ["OPEN None", "OPEN None", "MERGED " + "e" * 40]})
    check("the merge is retried until GitHub reports MERGED", rc == 0 and sum(c[:3] == ["gh", "pr", "merge"] for c in calls) == 3)
    rc, lines, calls = go({"merge": ["OPEN None"] * 3})
    check("a merge GitHub never takes stops it", rc == 1 and "merge:" in lines[-1])
    rc, lines, calls = go({}, q=[dict(item), dict(item, pr=8)])
    check("the queue runs in order", rc == 0 and [c[3] for c in calls if c[:3] == ["gh", "pr", "merge"]] == ["7", "8"])
    rc, lines, calls = go({"runs": green + [{"name": "typing", "status": "completed", "conclusion": "failure", "started_at": "1"}]},
                          q=[dict(item), dict(item, pr=8)])
    check("the first refusal stops the queue", rc == 1 and not any(c[:4] == ["gh", "pr", "view", "8"] for c in calls))
    owned7 = (1, "app_approve: REFUSE: #7 touches code-owned paths (tests/run.sh); the owner's GitHub review approves it, not the App")
    echo = (1, "app_approve: REFUSE: the newest allowlisted verdict on #7 is 'Fix review: blocked aaaa policy: "
               "#7 touches code-owned paths (tests/run.sh); and ## Approval is missing', not 'Fix review: merge " + H0 + "'")
    rc, lines, calls = go({"approve": echo}, mandate="m")
    check("a blocked verdict echoing the code-owned words is not mandate-approved (B1)",
          rc == 1 and "app_approve.sh refused" in lines[-1] and not approved(calls) and not merged(calls))
    quoted = (1, "app_approve: REFUSE: the newest allowlisted verdict on #7 is 'Fix review: blocked x approve: "
                 "app_approve: REFUSE: #7 touches code-owned paths (tests/run.sh); the owner', not z")
    rc, lines, calls = go({"approve": quoted}, mandate="m")
    check("a blocked verdict QUOTING app_approve's own code-owned line mid-line is not mandate-approved (anchor)",
          rc == 1 and "app_approve.sh refused" in lines[-1] and not approved(calls) and not merged(calls))
    rc, lines, calls = go({"approve": owned7, "base": (0, "not-a-sha\n")}, mandate="m")
    check("a merge base that exits 0 but is not a sha stops the train", rc == 1 and "files:" in lines[-1] and not approved(calls))
    rc, lines, calls = go({"approve": owned7}, mandate="m")
    check("the anchored code-owned refusal line still takes the mandate path (null control)", rc == 0 and approved(calls))
    rc, lines, calls = go({"approve": (1, owned7[1].replace("#7 ", "#8 "))}, mandate="m")
    check("another pull request's code-owned line does not take the mandate path for this one",
          rc == 1 and "app_approve.sh refused" in lines[-1] and not approved(calls))
    rc, lines, calls = go({"approve": owned7, "heads": [H0, H0, H1]}, mandate="m")
    check("a head that moves between the App's refusal and the mandate review stops it",
          rc == 1 and "head moved before the mandate approval" in lines[-1] and not approved(calls))
    rc, lines, calls = go({"approve": owned7, "renamed": ("AGENTS.md", "docs-agents.md")}, mandate="m")
    check("a rename that moves a policy file out of the corpus is refused as policy (B2)",
          rc == 1 and "policy:" in lines[-1] and "AGENTS.md" in lines[-1] and not approved(calls))
    rc, lines, calls = go({"approve": owned7, "diff_fail": (128, "fatal: bad object")}, mandate="m")
    check("a failing git diff stops the train (B3)", rc == 1 and "files:" in lines[-1] and not approved(calls))
    rc, lines, calls = go({"approve": owned7, "base": (1, "fatal: no merge base")}, mandate="m")
    check("a failing git merge-base stops the train (B3)", rc == 1 and "files:" in lines[-1] and not approved(calls))
    rc, lines, calls = go({}, min_runs=3)
    check("fewer check runs than --min-runs is not complete CI", rc == 1 and "TIMEOUT" in lines[-1] and not merged(calls))
    for c in ("action_required", "stale"):
        rc, lines, calls = go({"runs": green + [{"name": "x", "status": "completed", "conclusion": c, "started_at": "1"}]})
        check(f"{c} is not green", rc == 1 and lines[-1].endswith("red at the head: x") and not merged(calls))
    rc, lines, calls = go({"runs": green + [{"name": "y", "status": "completed", "conclusion": c, "started_at": "1"}
                                            for c in ("skipped",)] + [{"name": "z", "status": "completed",
                                                                        "conclusion": "neutral", "started_at": "1"}]})
    check("skipped and neutral are green (null control)", rc == 0 and merged(calls))
    check("the CI read pages past the first 100 runs",
          any("--paginate" in c and any("check-runs" in x for x in c) for c in calls))
    rc, lines, calls = go({"contains": [True, True, False]})
    check("main moving after approval and before the merge stops it", rc == 1 and "merge:" in lines[-1] and not merged(calls))
    rc, lines, calls = go({"preflight": "  ok       policy corpus -- current"})
    check("a preflight that never says clean stops it", rc == 1 and "preflight:" in lines[-1] and not merged(calls))
    rc, lines, calls = go({}, q=[dict(item, verdict="xyz")])
    check("a queue entry with a malformed verdict sha is refused", rc == 1 and "queue:" in lines[-1])
    print(f"merge_train self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return _self_test()
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repo", default="tvofi/heatpump_optimizer")
    common.add_argument("--min-runs", type=int, default=15, help="a head with fewer check runs is not yet fully queued")
    p = argparse.ArgumentParser(prog="merge_train.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", parents=[common])
    r.add_argument("queue")
    r.add_argument("--mandate", help="the owner's mandate, as quoted in a code-owned approval; omit to never approve one")
    r.add_argument("--approver-role", default="the orchestrator")
    r.add_argument("--ignore-red", action="append", help="a check whose red does not stop the train (default nightly-status)")
    r.add_argument("--state-dir", default=os.path.join(os.environ.get("HPO_STATE_DIR") or os.path.expanduser("~/.local/state/hpo"), "merge_train"))
    w = sub.add_parser("wait-ci", parents=[common])
    w.add_argument("sha")
    a = p.parse_args(argv)
    if a.cmd == "wait-ci":
        red = Train(a.repo, Path("."), None, "", (), a.min_runs).wait_ci(a.sha)
        print("DONE", a.sha, "red:", " ".join(red) or "none")
        return 1 if red else 0
    queue = json.loads(Path(a.queue).read_text())
    ignore = tuple(a.ignore_red) if a.ignore_red else ("nightly-status",)
    return Train(a.repo, Path(a.state_dir), a.mandate, a.approver_role, ignore, a.min_runs).train(queue)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

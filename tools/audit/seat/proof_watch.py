#!/usr/bin/env python3
"""Watch one validating check-run at one pinned head and merge on green.

    python3 tools/audit/seat/proof_watch.py --pr N --head SHA --check NAME \
        [--repo OWNER/REPO] [--poll SECONDS] [--budget HOURS] \
        [--dry-run] [--mode app|owner [--mandate <#201 comment id>]]
    python3 tools/audit/seat/proof_watch.py --self-test

WHY THIS EXISTS. Owner decision P8 (2026-10-12, the throughput pre-study): a
4.5 h validating proof was misread as failed while it was still running, and
the class cost the programme roughly 7 h of green-to-merge decision latency —
the same window #2071 sat in for 8 h 27 m. Between a long run's green and its
merge there is a decision only a watcher can take; the orchestrator polling
by hand is the latency this removes. It watches ONE named check-run at ONE
pinned head of ONE pull request and, when that check completes `success`,
merges the pull request through the repo's own merge path, `merge_pr.sh` —
never its own `gh pr merge`.

THE GUARDS, all hard; every refusal is a report and no merge:
  pinned head   the pull request's live head must read exactly `--head`, on
                every poll and again under the lock before the hand-off. A
                moved head aborts; this instrument never follows a head;
  one check     only the named check's `success` merges. A completed run with
                any other conclusion aborts; a check that has not started yet
                keeps waiting;
  green         the ruleset's other required contexts are read through
                `merge_train.required()` — the train's own list, never a copy
                — and a required context whose latest run at the head
                completed not-green aborts. A required context still running
                keeps waiting;
  budget        past `--budget` hours without the named check green, abort.
                The 4.5 h proof is exactly what a default budget of 6 h is
                for: an instrument that waited forever would re-create the
                misread it exists to prevent;
  mergeable     `mergeable` must read MERGEABLE from the API before anything;
  verdict       `app_approve.sh --dry-run` — the approver's own gate, invoked
                never re-implemented — must pass at the pinned head before
                the merge: the newest allowlisted `Fix review: merge <sha>`
                verdict from `hpo-approver[bot]`, citing an evidence
                directory that exists here and names the head. The evidence
                directory is then read back off the verdict body for
                `merge_pr.sh`'s argv; if the gate passed and the read-back
                still finds nothing qualifying, that divergence aborts rather
                than merging with a guessed directory. A code-owned pull
                request is refused by the gate itself — its approval is the
                owner's GitHub review, not this instrument's lane;
  one instance  an flock on `<state>/proof-watch-<pr>-<head12>.lock`, held
                for the watch's whole life. A relaunched session's second
                watcher refuses rather than double-merging;
  dry-run       `--dry-run` runs every guard and prints what it would hand
                to `merge_pr.sh`, and touches nothing: no lock, no log, no
                state directory, no merge.

Every merge is logged to stdout and `<state>/proof-watch.log` with the pull
request, the head, the check name, the verdict comment id and the merge sha;
every abort is logged too. What it does NOT do: it dispatches no CI, approves
no held runs (the caller did that), and touches no queue.

The self-test stubs the command runner (`--self-test`), so `gh`, the
approver's gate and `merge_pr.sh` are fakes: no network, no keys, no merge.
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

SEAT = Path(__file__).resolve().parent
DEFAULT_REPO = "tvofi/heatpump_optimizer"
DEFAULT_STATE = Path(os.path.expanduser(
    os.environ.get("HPO_STATE_DIR") or "~/.local/state/hpo")) / "proof-watch"
GREEN = ("success", "skipped", "neutral")
HEX = set("0123456789abcdef")


class Abort(Exception):
    """A guard refused: report it, merge nothing, exit 1."""


def _json_docs(raw: str) -> list:
    """What `gh api` prints: concatenated JSON documents, an array per page
    (plain --paginate) or one object per line (--jq '.check_runs[]')."""
    dec, i, out = json.JSONDecoder(), 0, []
    while True:
        while i < len(raw) and raw[i].isspace():
            i += 1
        if i >= len(raw):
            return out
        v, i = dec.raw_decode(raw, i)
        out.extend(v) if isinstance(v, list) else out.append(v)


class Watcher:
    """One watch: one pull request, one pinned head, one named check-run."""

    def __init__(self, repo: str, pr: int, sha: str, check: str,
                 poll: float = 300.0, budget_h: float = 6.0,
                 dry: bool = False, mode: str = "app", mandate: int | None = None,
                 state: Path = DEFAULT_STATE,
                 merge_script: Path | None = None, approve_script: Path | None = None,
                 run=None, sleep=time.sleep, clock=time.monotonic, say=print) -> None:
        self.repo, self.pr, self.sha, self.check = repo, pr, sha, check
        self.poll, self.budget_h, self.dry, self.mode = poll, budget_h, dry, mode
        self.mandate = mandate
        self.state = state
        # The repo's own merge path and the approver's own gate, by path —
        # reused, never re-implemented (tests/README: one governance tool does
        # not re-implement another). Both default to the siblings this file
        # ships beside.
        self.merge_script = merge_script or (SEAT / "merge_pr.sh")
        self.approve_script = approve_script or (SEAT.parents[1] / "pr" / "app_approve.sh")
        self.run = run or self._run
        self.sleep, self.clock, self.say = sleep, clock, say

    @staticmethod
    def _run(argv: list[str], cwd: Path | None = None) -> tuple[int, str]:
        r = subprocess.run(argv, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    # -- reporting ---------------------------------------------------------

    def record(self, msg: str) -> None:
        """stdout always; the state log too — except `--dry-run`, which touches
        nothing, so a dry run leaves no log line and no directory behind."""
        self.say(msg)
        if self.dry:
            return
        self.state.mkdir(parents=True, exist_ok=True)
        with open(self.state / "proof-watch.log", "a") as fh:
            fh.write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + " " + msg + "\n")

    # -- reads -------------------------------------------------------------

    def live_head(self) -> str:
        code, out = self.run(["gh", "pr", "view", str(self.pr), "--repo", self.repo,
                              "--json", "headRefOid", "--jq", ".headRefOid"])
        if code:
            raise Abort(f"could not read #{self.pr}'s head: {out.strip()[-200:]}")
        return out.strip()

    def mergeable(self) -> str:
        code, out = self.run(["gh", "pr", "view", str(self.pr), "--repo", self.repo,
                              "--json", "mergeable", "--jq", ".mergeable"])
        if code:
            raise Abort(f"could not read #{self.pr}'s mergeable state: {out.strip()[-200:]}")
        return out.strip()

    def latest_by_name(self) -> dict[str, dict]:
        code, raw = self.run(["gh", "api", "--paginate", "--jq", ".check_runs[]",
                              f"repos/{self.repo}/commits/{self.sha}/check-runs?per_page=100"])
        if code:
            raise Abort(f"could not read the check-runs at {self.sha[:12]}: {raw.strip()[-200:]}")
        last: dict[str, dict] = {}
        for c in sorted(_json_docs(raw), key=lambda c: c.get("started_at") or ""):
            last[c["name"]] = c
        return last

    def required_names(self) -> list[str]:
        """The ruleset's required contexts, through merge_train's own reader."""
        if str(SEAT) not in sys.path:
            sys.path.insert(0, str(SEAT))  # -I and cron launches
        import merge_train  # the sibling module: the train's list, never a copy
        t = merge_train.Train(self.repo, state=self.state, mandate=None,
                              role="proof-watch", ignore=(), min_runs=0,
                              run=self.run, sleep=self.sleep)
        try:
            return t.required()
        except merge_train.Stop as e:
            raise Abort(f"required contexts unreadable, no merge is judged "
                        f"against a guessed list: {e.step}: {e.why}") from e

    def required_state(self) -> tuple[list[str], list[str]]:
        last = self.latest_by_name()
        names = self.required_names()
        red = sorted(n for n in names if n in last
                     and last[n].get("status") == "completed"
                     and last[n].get("conclusion") not in GREEN)
        pending = sorted(n for n in names
                         if n not in last or last[n].get("status") != "completed")
        return red, pending

    # -- the verdict -------------------------------------------------------

    def verdict_gate(self) -> None:
        """The approver's own gate, in its own dry-run: every refusal it makes,
        this instrument inherits — verdict at the exact head, evidence rules,
        the allowlist. Its refusal is this instrument's refusal."""
        code, out = self.run(["bash", str(self.approve_script),
                              "--dry-run", self.repo, str(self.pr), self.sha])
        if code:
            why = (out.strip().splitlines() or ["(no output)"])[-1][:300]
            raise Abort(f"no valid merge verdict at the pinned head "
                        f"(app_approve --dry-run refused): {why}")

    def _allowlist(self) -> tuple[set[str], int]:
        try:
            src = self.approve_script.read_text()
            authors = re.search(r'^VERDICT_AUTHORS="(.*)"$', src, re.M).group(1)
            vid = int(re.search(r"^VERDICT_AUTHOR_ID=(\d+)", src, re.M).group(1))
        except (OSError, AttributeError):
            raise Abort(f"could not read the verdict allowlist off {self.approve_script}")
        return set(authors.split()), vid

    def verdict_comment(self) -> tuple[int, str]:
        """(comment id, evidence directory) off the verdict the gate just
        accepted — the argv merge_pr.sh needs and the id the merge log owes."""
        authors, vid = self._allowlist()
        code, raw = self.run(["gh", "api", "--paginate",
                              f"repos/{self.repo}/issues/{self.pr}/comments?per_page=100"])
        if code:
            raise Abort(f"could not read the comments on #{self.pr}: {raw.strip()[-200:]}")
        vs = [c for c in _json_docs(raw)
              if (c.get("user") or {}).get("login") in authors
              and (c.get("user") or {}).get("type") == "Bot"
              and (c.get("user") or {}).get("id") == vid
              and (c.get("body") or "").split("\n", 1)[0].strip().lower().startswith("fix review:")]
        if not vs:
            raise Abort(f"no 'Fix review:' verdict from the approver App on #{self.pr}, "
                        f"though the gate passed; refusing the divergence")
        c = sorted(vs, key=lambda c: (c.get("created_at") or "", c["id"]))[-1]
        return c["id"], self.evidence_dir(c.get("body") or "")

    def evidence_dir(self, body: str) -> str:
        """Read back the evidence directory the verdict cites — the same
        token grammar app_approve's gate applies, because merge_pr.sh's argv
        needs a directory and guessing one is a merge on a fabricated verdict.
        The GATE ran in app_approve; a divergence between the two aborts."""
        why = "the verdict names no absolute path at all"
        boundary = r"(?:(?<=[\s([{\x22\x27\x60])|^)"
        for m in re.finditer(boundary + r"(/[^\s\x60\x22]+)", body, re.MULTILINE):
            tok = re.sub(r"^[([{'\x22\x60]+", "", m.group(1)).rstrip("])}.,;:'\x22\x60").rstrip("/")
            if tok.count("/") < 1:
                why = f"{tok} has fewer than two path components"
                continue
            resolved = os.path.realpath(tok)
            if not os.path.isdir(resolved):
                why = f"{tok} is not a directory that exists"
                continue
            if not any(os.scandir(resolved)):
                why = f"{tok} ({resolved}) is empty"
                continue
            for root, _dirs, files in os.walk(resolved):
                for f in files:
                    try:
                        with open(os.path.join(root, f), encoding="utf-8", errors="ignore") as fh:
                            if self.sha in fh.read():
                                return resolved
                    except OSError:
                        continue
            why = f"no file under {tok} names the head {self.sha}"
        raise Abort(f"the verdict cites no qualifying evidence directory: {why}")

    # -- the merge ---------------------------------------------------------

    @contextlib.contextmanager
    def lock(self):
        """One instance per pinned head: a relaunched watcher refuses rather
        than double-merging. Held for the watch's whole life."""
        self.state.mkdir(parents=True, exist_ok=True)
        path = self.state / f"proof-watch-{self.pr}-{self.sha[:12]}.lock"
        with open(path, "a+") as fh:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                raise Abort(f"another proof-watch holds {path} "
                            f"(one instance per pinned head); nothing merged")
            yield

    def do_merge(self, cid: int, evidence: str) -> str:
        argv = ["bash", str(self.merge_script), str(self.pr), self.sha, evidence, self.mode]
        if self.mode == "owner":
            argv += ["--mandate", str(self.mandate)]
        code, out = self.run(argv)
        if code:
            raise Abort(f"{self.merge_script} failed (rc={code}): {out.strip()[-400:]}")
        m = re.search(r"^merged ([0-9a-f]{40})$", out, re.M)
        merge_sha = m.group(1) if m else "(unparsed)"
        self.record(f"PROOF-WATCH MERGE pr=#{self.pr} head={self.sha} check={self.check} "
                    f"verdict_comment={cid} evidence={evidence} merge_sha={merge_sha}")
        return merge_sha

    # -- the watch ---------------------------------------------------------

    def wait_green(self) -> tuple[int, str]:
        self.record(f"PROOF-WATCH watching #{self.pr} at {self.sha[:12]} for check "
                    f"'{self.check}' (poll {self.poll}s, budget {self.budget_h}h)")
        start, deadline = self.clock(), self.budget_h * 3600.0
        # The budget is also a poll-count ceiling: a clock that never advances
        # (or a budget check that stops firing) cannot turn the wait into an
        # unbounded loop — the count runs out and reads as the budget abort.
        for _ in range(int(deadline / max(self.poll, 0.001)) + 2):
            live = self.live_head()
            if live != self.sha:
                raise Abort(f"HEAD MOVED: #{self.pr}'s live head is {live}, pinned "
                            f"{self.sha}; this watch never follows a head; nothing merged")
            named = self.latest_by_name().get(self.check)
            if named is not None and named.get("status") == "completed":
                conc = named.get("conclusion")
                if conc != "success":
                    raise Abort(f"named check '{self.check}' did not succeed at "
                                f"{self.sha[:12]}: conclusion {conc}; nothing merged")
                red, pending = self.required_state()
                if red:
                    raise Abort(f"REQUIRED RED at {self.sha[:12]}: {', '.join(red)}; "
                                f"nothing merged")
                if not pending:
                    break
            if self.clock() - start > deadline:
                raise Abort(f"BUDGET EXCEEDED after {self.budget_h}h: '{self.check}' "
                            f"not green at {self.sha[:12]}; nothing merged")
            self.sleep(self.poll)
        else:
            raise Abort(f"BUDGET EXCEEDED after {self.budget_h}h: '{self.check}' "
                        f"not green at {self.sha[:12]} (poll count ran out); nothing merged")
        mb = self.mergeable()
        if mb != "MERGEABLE":
            raise Abort(f"#{self.pr} reads {mb}, not mergeable; nothing merged")
        self.verdict_gate()
        return self.verdict_comment()

    def watch(self) -> None:
        if self.dry:
            cid, evidence = self.wait_green()
            self.say(f"PROOF-WATCH DRY-RUN: every guard passed at {self.sha[:12]}; would run "
                     f"{self.merge_script} with pr=#{self.pr} head={self.sha} check={self.check} "
                     f"verdict_comment={cid} evidence={evidence} mode={self.mode}; "
                     f"touched nothing")
            return
        with self.lock():
            cid, evidence = self.wait_green()
            self.do_merge(cid, evidence)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Watch one check-run at one pinned head; merge on green.")
    ap.add_argument("--self-test", action="store_true", help="offline stubbed arms")
    ap.add_argument("--pr", type=int, help="the pull request number")
    ap.add_argument("--head", help="the pinned 40-hex head SHA; never followed")
    ap.add_argument("--check", help="the name of the check-run to wait for")
    ap.add_argument("--repo", default=DEFAULT_REPO, help="owner/repo (default %(default)s)")
    ap.add_argument("--poll", type=float, default=300.0, help="seconds between polls (default %(default)s)")
    ap.add_argument("--budget", type=float, default=6.0, help="hours before aborting (default %(default)s)")
    ap.add_argument("--mode", choices=("app", "owner"), default="app",
                    help="the merge identity merge_pr.sh is handed (default %(default)s)")
    ap.add_argument("--mandate", type=int,
                    help="owner mode: the #201 mandate comment id merge_pr.sh reads live")
    ap.add_argument("--dry-run", action="store_true", help="run every guard, touch nothing")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    for flag, v in (("--pr", a.pr), ("--head", a.head), ("--check", a.check)):
        if v is None:
            print(f"proof_watch: REFUSE: {flag} is required (or --self-test)", file=sys.stderr)
            return 2
    if a.mode == "owner" and a.mandate is None:
        # merge_pr.sh refuses owner mode without one; refuse now, not after the watch
        print("proof_watch: REFUSE: --mode owner needs --mandate <#201 comment id>", file=sys.stderr)
        return 2
    if not (len(a.head) == 40 and set(a.head) <= HEX):
        print(f"proof_watch: REFUSE: --head must be the full 40-hex SHA, got '{a.head}'", file=sys.stderr)
        return 2
    w = Watcher(repo=a.repo, pr=a.pr, sha=a.head, check=a.check, poll=a.poll,
                budget_h=a.budget, dry=a.dry_run, mode=a.mode, mandate=a.mandate)
    try:
        w.watch()
    except Abort as e:
        w.record(f"PROOF-WATCH ABORT: {e}")
        return 1
    return 0


# ----------------------------------------------------------------- self-test
# Every arm runs the real Watcher over a stubbed command runner: `gh`, the
# approver's gate and merge_pr.sh are fakes, so nothing here reaches the
# network, a key file, or a merge. The healthy arm and its refusals come in
# pairs, and the dry-run arm asserts the tree it was given is untouched.

def self_test() -> int:
    import shutil
    import tempfile

    SHA = "a" * 40
    OTHER = "b" * 40
    MERGED = "c" * 40
    CHECK = "Validate proof"
    REPO = "o/r"
    PR = 7
    APPR = {"login": "hpo-approver[bot]", "type": "Bot", "id": 330097732}

    W = Path(tempfile.mkdtemp(prefix="proof-watch-selftest."))
    fails, n = 0, 0

    def st(got, want, why):
        nonlocal fails, n
        n += 1
        if got == want:
            print(f"ok   {why}")
        else:
            print(f"FAIL {why} (got {got!r}, want {want!r})")
            fails += 1

    class Fixture:
        def __init__(self):
            self.root = W / f"case{len(cases)}"
            self.root.mkdir()
            self.approve = self.root / "app_approve_stub.sh"
            self.merge = self.root / "merge_pr_stub.sh"
            self.approve.write_text("# the runner is stubbed; this file is only read\n"
                                    "VERDICT_AUTHORS=\"hpo-approver[bot]\"\n"
                                    "VERDICT_AUTHOR_ID=330097732\n")
            self.merge.write_text("# marker\n")
            self.approve_rc = 0
            self.merge_rc = 0
            self.merge_out = f"merged {MERGED}\n"
            self.merge_calls: list[list[str]] = []
            self.pr_head = SHA
            self.checks = [
                {"name": CHECK, "status": "completed", "conclusion": "success",
                 "started_at": "2026-10-12T00:00:00Z"},
                {"name": "Tests", "status": "completed", "conclusion": "success",
                 "started_at": "2026-10-12T00:01:00Z"},
            ]
            self.required = "Tests"
            self.mergeable = "MERGEABLE"
            self.now = [0.0]
            self.evidence = self.root / "evidence"
            self.evidence.mkdir()
            (self.evidence / "verdict.md").write_text(f"fix review at head {SHA}\n")

        def set_verdict(self, body: str | None = None, cid: int = 4242):
            if body is None:
                body = f"Fix review: merge {SHA}\nevidence: {self.evidence}"
            self.verdict = {"id": cid, "created_at": "2026-10-12T01:00:00Z",
                            "user": dict(APPR), "body": body}

        def run(self, argv, cwd=None):
            if argv[0] == "bash" and argv[1] == str(self.approve):
                out = "app_approve: DRY-RUN: every refusal passed\n" if self.approve_rc == 0 \
                    else "app_approve: REFUSE: no 'Fix review:' verdict\n"
                return self.approve_rc, out
            if argv[0] == "bash" and argv[1] == str(self.merge):
                self.merge_calls.append(argv)
                return self.merge_rc, self.merge_out
            if "headRefOid" in argv:
                return 0, self.pr_head + "\n"
            if any(a == f"repos/{REPO}/rulesets" for a in argv):
                return 0, "23698884\n"
            if any(a.startswith(f"repos/{REPO}/rulesets/") for a in argv):
                return 0, self.required + "\n"
            if any(a.startswith("repos/") and "/check-runs" in a for a in argv):
                return 0, "".join(json.dumps(c) + "\n" for c in self.checks)
            if "mergeable" in argv:
                return 0, self.mergeable + "\n"
            if any(a == f"repos/{REPO}/issues/{PR}/comments?per_page=100" for a in argv):
                return 0, json.dumps([self.verdict]) + "\n"
            return 9, f"stub: unhandled command: {' '.join(argv)}\n"

        def sleep(self, secs):
            self.now[0] += max(secs, 1.0)

        def clock(self):
            return self.now[0]

        def watcher(self, dry=False, budget_h=1.0, out=None, mode="app", mandate=None):
            return Watcher(repo=REPO, pr=PR, sha=SHA, check=CHECK, poll=1.0,
                           budget_h=budget_h, dry=dry, mode=mode, mandate=mandate,
                           state=self.root / "state",
                           merge_script=self.merge, approve_script=self.approve,
                           run=self.run, sleep=self.sleep, clock=self.clock,
                           say=(out.append if out is not None else print))

    cases = []

    # (a1) green + verdict + mergeable, --dry-run: reports, touches nothing.
    f = Fixture(); cases.append(f); f.set_verdict()
    out: list[str] = []
    try:
        f.watcher(dry=True, out=out).watch()
    except Abort as e:
        st(f"unexpected abort: {e}", "no abort",
           "(a1) the healthy dry-run arm passes every guard")
    st([ln for ln in out if "DRY-RUN" in ln and "would run" in ln], out[-1:],
       "(a1) dry-run reports what it would hand merge_pr.sh")
    st(f.merge_calls, [], "(a1) dry-run performs no merge")
    st((f.root / "state").exists(), False, "(f) dry-run creates no state directory, log or lock")

    # (a2) the same guards, live: merge_pr.sh is handed pr, pinned head,
    # evidence dir and mode, and the merge is logged with the verdict id.
    f = Fixture(); cases.append(f); f.set_verdict()
    out = []
    w = f.watcher(out=out)
    try:
        w.watch()
    except Abort as e:
        st(f"unexpected abort: {e}", "no abort",
           "(a2) the healthy live arm merges without aborting")
    st(f.merge_calls,
       [["bash", str(f.merge), str(PR), SHA, str(os.path.realpath(f.evidence)), "app"]],
       "(a2) the merge goes through merge_pr.sh with pr, pinned head, evidence and mode")
    # (a3) owner mode hands merge_pr.sh the mandate id it reads live; launched
    # without one, the watch refuses before it polls (the app arm above is the
    # null: no --mandate reaches merge_pr.sh there).
    f3 = Fixture(); cases.append(f3); f3.set_verdict()
    try:
        f3.watcher(out=[], mode="owner", mandate=6175172275).watch()
    except Abort as e:
        st(f"unexpected abort: {e}", "no abort", "(a3) the owner arm merges without aborting")
    st([c[-3:] for c in f3.merge_calls], [["owner", "--mandate", "6175172275"]],
       "(a3) owner mode passes --mandate <id> to merge_pr.sh")
    st(main(["--pr", str(PR), "--head", SHA, "--check", CHECK, "--mode", "owner"]), 2,
       "(a3) --mode owner without --mandate refuses at launch")
    merge_lines = [ln for ln in out if ln.startswith("PROOF-WATCH MERGE")]
    st(len(merge_lines), 1, "(a2) exactly one merge line")
    st(all(k in merge_lines[0] for k in (f"pr=#{PR}", f"head={SHA}", f"check={CHECK}",
                                         "verdict_comment=4242", str(f.evidence),
                                         f"merge_sha={MERGED}")), True,
       "(a2) the merge line names pr, head, check, verdict comment id, evidence and merge sha")
    st((f.root / "state" / "proof-watch.log").exists(), True,
       "(a2) the state log exists after a live merge")
    if (f.root / "state" / "proof-watch.log").exists():
        log = (f.root / "state" / "proof-watch.log").read_text()
        st("PROOF-WATCH MERGE" in log and str(f.evidence) in log, True,
           "(a2) the merge line is in the state log too")

    # (b) the named check fails: abort, no merge. The catch mirrors main(),
    # which turns an Abort into the logged PROOF-WATCH ABORT line.
    f = Fixture(); cases.append(f); f.set_verdict()
    f.checks[0]["conclusion"] = "failure"
    out = []
    w = f.watcher(out=out)
    try:
        w.watch()
        st("no-abort", "abort", "(b) a failing named check aborts")
    except Abort as e:
        st("did not succeed" in str(e), True, "(b) a failing named check aborts, naming the check")
        st(f.merge_calls, [], "(b) no merge after a failed check")
        w.record(f"PROOF-WATCH ABORT: {e}")
        st("PROOF-WATCH ABORT" in (f.root / "state" / "proof-watch.log").read_text(), True,
           "(b) the abort is logged too")

    # (c) budget exceeded while the check is still running.
    f = Fixture(); cases.append(f); f.set_verdict()
    f.checks[0] = {"name": CHECK, "status": "in_progress", "conclusion": None,
                   "started_at": "2026-10-12T00:00:00Z"}
    out = []
    try:
        f.watcher(budget_h=0.001, out=out).watch()  # 3.6 s; each poll advances 1 s
        st("no-abort", "abort", "(c) an exceeded budget aborts")
    except Abort as e:
        st("BUDGET EXCEEDED" in str(e), True, "(c) an exceeded budget aborts with a report")
        st("(poll count ran out)" not in str(e), True,
           "(c) the clock's budget abort fired, not the poll-count fallback")
        st(f.merge_calls, [], "(c) no merge on budget")
        st(any("watching" in ln for ln in out), True, "(c) the watch was announced first")

    # (d) the head moved: never followed.
    f = Fixture(); cases.append(f); f.set_verdict()
    f.pr_head = OTHER
    out = []
    try:
        f.watcher(out=out).watch()
        st("no-abort", "abort", "(d) a moved head aborts")
    except Abort as e:
        st("HEAD MOVED" in str(e) and OTHER in str(e), True, "(d) a moved head aborts, naming both heads")
        st(f.merge_calls, [], "(d) no merge at a moved head")

    # (e) the gate refuses: no valid verdict at the pinned head.
    f = Fixture(); cases.append(f); f.set_verdict()
    f.approve_rc = 1
    out = []
    try:
        f.watcher(out=out).watch()
        st("no-abort", "abort", "(e) a refused verdict gate aborts")
    except Abort as e:
        st("no valid merge verdict" in str(e), True, "(e) a refused verdict gate aborts with its reason")
        st(f.merge_calls, [], "(e) no merge without a verdict")
    st(f.run(["bash", str(f.approve), "--dry-run", REPO, str(PR), SHA])[0], 1,
       "(e) the gate was asked, not assumed")

    # (e2) the gate passes but the verdict cites no qualifying evidence: the
    # read-back divergence aborts instead of merging on a guessed directory.
    f = Fixture(); cases.append(f); f.set_verdict(f"Fix review: merge {SHA}\nno path here")
    out = []
    try:
        f.watcher(out=out).watch()
        st("no-abort", "abort", "(e2) a gate-passing verdict with no evidence path aborts")
    except Abort as e:
        st("no qualifying evidence" in str(e), True, "(e2) the divergence is named")
        st(f.merge_calls, [], "(e2) no merge on an unreadable verdict")

    # (g) a required context red at the head: abort before the merge path.
    f = Fixture(); cases.append(f); f.set_verdict()
    f.checks.append({"name": "Tests", "status": "completed", "conclusion": "failure",
                     "started_at": "2026-10-12T00:02:00Z"})
    out = []
    try:
        f.watcher(out=out).watch()
        st("no-abort", "abort", "(g) a red required context aborts")
    except Abort as e:
        st("REQUIRED RED" in str(e) and "Tests" in str(e), True, "(g) the red context is named")
        st(f.merge_calls, [], "(g) no merge on red")

    # (h) unmergeable: abort.
    f = Fixture(); cases.append(f); f.set_verdict()
    f.mergeable = "CONFLICTING"
    out = []
    try:
        f.watcher(out=out).watch()
        st("no-abort", "abort", "(h) an unmergeable pull request aborts")
    except Abort as e:
        st("not mergeable" in str(e), True, "(h) the mergeable state is named")
        st(f.merge_calls, [], "(h) no merge unmergeable")

    # (i) one instance per pinned head: a second watcher refuses.
    f = Fixture(); cases.append(f); f.set_verdict()
    lockdir = f.root / "state"
    lockdir.mkdir()
    with open(lockdir / f"proof-watch-{PR}-{SHA[:12]}.lock", "a") as held:
        fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        out = []
        try:
            f.watcher(out=out).watch()
            st("no-abort", "abort", "(i) a second watcher on the same head aborts")
        except Abort as e:
            st("another proof-watch holds" in str(e), True, "(i) the held lock is named")
            st(f.merge_calls, [], "(i) no double merge")

    # (j) the merge path itself fails: abort, nothing logged as merged.
    f = Fixture(); cases.append(f); f.set_verdict()
    f.merge_rc = 1
    f.merge_out = "not clean\n"
    out = []
    try:
        f.watcher(out=out).watch()
        st("no-abort", "abort", "(j) a failed merge hand-off aborts")
    except Abort as e:
        st("failed (rc=1)" in str(e), True, "(j) the merge path's refusal is reported")
        st(not any("PROOF-WATCH MERGE" in ln for ln in out), True,
           "(j) no MERGE line is logged for a merge that did not land")

    # (k) the named check's conclusion is anything but success — skipped,
    # neutral, stale — the same refusal as a failure, never a merge.
    f = Fixture(); cases.append(f); f.set_verdict()
    f.checks[0]["conclusion"] = "skipped"
    out = []
    try:
        f.watcher(out=out).watch()
        st("no-abort", "abort", "(k) a skipped named check aborts")
    except Abort as e:
        st("did not succeed" in str(e), True, "(k) skipped reads as not-succeeded")
        st(f.merge_calls, [], "(k) no merge on a skipped check")

    # (l) a required context still running keeps the watch waiting: no abort
    # and no merge on the first poll, then it merges once the context lands.
    # The stub keeps Tests in_progress until the first poll has elapsed, so
    # both reads of a poll (the named check's and required_state's) agree.
    f2 = Fixture(); cases.append(f2); f2.set_verdict()
    orig_run = f2.run
    sleeps: list[float] = []
    f2.sleep = lambda s: sleeps.append(s)

    def run_pending_first(argv, cwd=None):
        s = " ".join(argv)
        if "check-runs" in s and not sleeps:
            return 0, json.dumps({"name": CHECK, "status": "completed",
                                  "conclusion": "success", "started_at": "x"}) + "\n" + \
                json.dumps({"name": "Tests", "status": "in_progress",
                            "conclusion": None, "started_at": "y"}) + "\n"
        return orig_run(argv, cwd)

    f2.run = run_pending_first
    out = []
    w2 = f2.watcher(out=out)
    try:
        w2.watch()
    except Abort as e:
        st(f"unexpected abort: {e}", "no abort",
           "(l) the watch merges once the pending context lands")
    st(bool(sleeps) and bool(f2.merge_calls), True,
       "(l) a pending required context waits a poll, then merges when it lands")
    st(all(s == 1.0 for s in sleeps), True, "(l) the wait polls at the configured cadence")

    shutil.rmtree(W, ignore_errors=True)
    print(f"proof_watch self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

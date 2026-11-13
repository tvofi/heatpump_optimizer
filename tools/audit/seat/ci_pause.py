#!/usr/bin/env python3
"""The merge train's CI pause: free runners for the head by cancelling a low-priority PR's runs.

    python3 tools/audit/seat/ci_pause.py --self-test

Owner ruling (tvofi 2026-10-28, P267): when the account's concurrent-job limit
binds, pause the lowest-priority pull request's CI so main and the train head
get runners. GitHub exposes no account limit, so it binds when a check-run at
the head the train waits on (or at main's tip after a landing) has been `queued`
for `pause_queued_min` minutes -- read from the check-runs `wait_ci` already
fetched on its own poll, no polling loop of its own.

One victim per pass, at most one pass per `pause_gap_min`: the worst
`ci_priority.rank` first, never a `never_pause` tier, the train head, a pull
request the train holds (queued, spooled, seen with a verdict) or one holding a
`Fix review: merge` comment (carry 6: a cancelled run reddens a verdicted PR and
the sweep never undoes it), nor a run at another head. Pause = POST
actions/runs/<id>/cancel for its active runs at its live head, recorded in
`paused.json` beside the train's state as {pr, head, run_ids, paused_at}. Resume
= POST rerun-failed-jobs per recorded run (finished jobs are kept) when the head
and main have no queued check-run, on every train exit and at every train start;
a record whose head moved is dropped unrun.

The pause is the owner's P267 rule and is not governed by the setting's
`priority_cancel`, which switches only the sweep's cancels of queued runs
(carry 6; orchestrator ruling on the review of #3560).

CARRY 6 (ii), the hold: `hold(h)` names a queued run of a priority pull request
(a `never_cancel` tier) while the pull request at <h> is not one; the train asks
it before each re-run it starts (`Train.hold_reruns`). Main's tip is no pull
request and is read as `main-push`, never held. An unreadable listing holds
nothing.
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ci_priority  # noqa: E402
import roster_lib as rl  # noqa: E402

PAUSED = "paused.json"


def _epoch(stamp: "str | None") -> "float | None":
    try:
        return datetime.datetime.fromisoformat(str(stamp).replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        return None


def queued_minutes(runs, now: float) -> "float | None":
    """Minutes the OLDEST `queued` check-run in <runs> has waited, or None with none queued
    (or none with a readable `started_at`: an age computed from nothing is unknowable, not 0)."""
    ages = [(now - t) / 60 for t in (_epoch(c.get("started_at")) for c in runs or ()
                                      if c.get("status") == "queued") if t is not None]
    return max(ages) if ages else None


class CiPause:
    """`train` supplies run(cmd) -> (rc, out), log, wall(), repo, state (Path) and
    protected_prs() -> set[int]; nothing else of the train is read."""

    def __init__(self, train, setting: "dict | None" = None, roster=None) -> None:
        self.t = train
        self.setting = setting
        self.roster = roster  # (roster dict, critical-path set) or None: read on first need
        self.last = 0.0
        self.noted: set = set()
        self.path = Path(train.state) / PAUSED

    # ---------------------------------------------------------------- records
    def read(self) -> list:
        try:
            got = json.loads(self.path.read_text())
        except (OSError, ValueError):
            return []
        return [r for r in got if isinstance(r, dict) and r.get("pr") and r.get("run_ids")] if isinstance(got, list) else []

    def write(self, recs: list) -> None:
        if not recs:
            self.path.unlink(missing_ok=True)
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(recs))
        os.replace(tmp, self.path)

    def _note(self, key, line: str) -> None:
        if key not in self.noted:
            self.noted.add(key)
            self.t.log(line)

    def _api(self, *args: str) -> "object | None":
        code, out = self.t.run(["gh", "api", *args])
        if code:
            return None
        try:
            return json.loads(out) if out.strip() else {}
        except ValueError:
            return None

    # ------------------------------------------------------------------ poll
    def poll(self, runs, h: str) -> None:
        """Called by `wait_ci` on each poll with the check-runs it just read at <h>."""
        now = self.t.wall()
        age = queued_minutes(runs, now)
        if age is None:
            if self.read():
                self.resume_all("head and main have no queued job")
            return
        setting = self.setting or ci_priority.load_setting()
        if age < setting["pause_queued_min"] or now - self.last < setting["pause_gap_min"] * 60:
            return
        self.last = now
        victim = self.pick(h, setting)
        if victim is None:
            self._note(("none", h), f"PAUSE none at {h[:8]}: a job has been queued {int(age)} min, no pausable victim")
            return
        pr, sha, ids = victim
        done = []
        for rid in ids:
            code, out = self.t.run(["gh", "api", "-X", "POST", f"repos/{self.t.repo}/actions/runs/{rid}/cancel"])
            if not code:
                done.append(rid)
        if done:
            self.write(self.read() + [{"pr": pr, "head": sha, "run_ids": done, "paused_at": now}])
            self.t.log(f"PAUSE #{pr} at {sha[:8]}: runs {','.join(map(str, done))} for {h[:8]}")

    def _roster(self):
        if self.roster is None:
            root = HERE.parents[1]
            ref = rl.default_roster_ref(rl.git_in(str(root)))[0]
            roster = rl.show_roster(str(root), ref)
            self.roster = (roster, {rl.norm_group(str(c)) for c in rl.critical_path(roster)})
        return self.roster

    def _verdicted(self, n: int) -> "bool | None":
        """Whether pull request <n> holds a `Fix review: merge` comment at any head (conservative:
        a comment on an older head still protects). None when the comments cannot be read."""
        got = self._api("--paginate", "--slurp", f"repos/{self.t.repo}/issues/{n}/comments?per_page=100")
        if not isinstance(got, list):
            return None
        return any(str(c.get("body") or "").startswith("Fix review: merge") for page in got for c in page)

    def _open(self, why: str) -> "tuple[list, dict, set] | None":
        """(open pull requests as {n, sha, ref, fork}, roster, critical path), or None, noted once."""
        code, out = self.t.run(["gh", "api", "--paginate", "--jq",
                                '.[] | {n: .number, sha: .head.sha, ref: .head.ref, fork: (.head.repo.full_name != "'
                                + self.t.repo + '")}',
                                f"repos/{self.t.repo}/pulls?state=open&per_page=100"])
        if code:
            return None
        try:
            prs = [json.loads(x) for x in out.splitlines() if x.strip()]
            roster, crit = self._roster()
        except Exception as e:  # noqa: BLE001 - an unreadable roster pauses and holds nothing
            self._note(("unread", str(e)[:40]), f"{why} unreadable: {str(e)[:120]}")
            return None
        return prs, roster, crit

    def _tier(self, p: dict, roster: dict, crit: set, setting: dict) -> "tuple[str, tuple]":
        """(tier, rank) of open pull request <p>; a group-less one is tier1 when it touches custom_components/."""
        group = rl.group_for_branch(roster, p["ref"]) or rl.group_for_pr(roster, p["n"])
        prod = False
        if not group:
            fs = self._api("--paginate", "--jq", "[.[].filename]", f"repos/{self.t.repo}/pulls/{p['n']}/files?per_page=100")
            prod = isinstance(fs, list) and any(str(f).startswith("custom_components/") for f in fs)
        return (ci_priority.tier(group, crit, roster, setting, touches_production=prod),
                ci_priority.rank(group, crit, roster, setting, touches_production=prod))

    def hold(self, h: str) -> "str | None":
        """Carry 6 (ii): why a re-run at <h> waits -- the open pull request at <h> is not a priority
        tier and a priority pull request has a run queued -- or None. Main's tip (no open pull
        request at <h>) reads as `main-push`; anything unreadable holds nothing."""
        got = self._open("HOLD")
        if got is None:
            return None
        prs, roster, crit = got
        setting = self.setting or ci_priority.load_setting()
        mine = [p for p in prs if p["sha"] == h]
        if ci_priority.is_priority(self._tier(mine[0], roster, crit, setting)[0] if mine else "main-push", setting):
            return None
        code, out = self.t.run(["gh", "api", "--paginate", "--jq", '.workflow_runs[] | {id, b: .head_branch}',
                                f"repos/{self.t.repo}/actions/runs?status=queued&per_page=100"])
        if code:
            return None
        by_ref = {p["ref"]: p for p in prs if not p["fork"]}
        for r in sorted((json.loads(x) for x in out.splitlines() if x.strip()), key=lambda r: int(r["id"])):
            p = by_ref.get(r.get("b"))
            if p is not None and ci_priority.is_priority(self._tier(p, roster, crit, setting)[0], setting):
                return f"priority #{p['n']} run {r['id']} is queued"
        return None

    def pick(self, h: str, setting: dict) -> "tuple[int, str, list[int]] | None":
        """(pr, head, active run ids) of the worst-ranked pausable pull request, or None."""
        got = self._open("PAUSE")
        if got is None:
            return None
        prs, roster, crit = got
        held = set(self.t.protected_prs()) | {p["n"] for p in prs if p["sha"] == h}
        scored = []
        for p in prs:
            if p["n"] in held or p["fork"]:
                continue
            t, rank = self._tier(p, roster, crit, setting)
            if not ci_priority.may_pause(t, setting):
                continue
            scored.append((rank, p))
        for _, p in sorted(scored, key=lambda x: (x[0], x[1]["n"]), reverse=True):
            if self._verdicted(p["n"]) is not False:
                continue  # a verdict, or comments that could not be read: never a victim
            code, out = self.t.run(["gh", "api", "--paginate", "--jq",
                                    '.workflow_runs[] | select(.status != "completed") | .id',
                                    f"repos/{self.t.repo}/actions/runs?head_sha={p['sha']}&per_page=100"])
            ids = [int(x) for x in out.split() if x.isdigit()] if not code else []
            if ids:
                return p["n"], p["sha"], sorted(ids)
        return None

    # ---------------------------------------------------------------- resume
    def resume_all(self, why: str) -> None:
        """Re-run the failed jobs of every recorded pause whose head is unchanged; drop a moved head."""
        keep = []
        for r in self.read():
            n, head = r["pr"], str(r.get("head") or "")
            cur = self._api(f"repos/{self.t.repo}/pulls/{n}")
            live = ((cur or {}).get("head") or {}).get("sha") if isinstance(cur, dict) else None
            if live is None:
                keep.append(r)  # unreadable: kept, the tick owes it after 60 minutes
                self.t.log(f"RESUME #{n} unread ({why}): record kept")
                continue
            if live != head:
                self.t.log(f"RESUME #{n}: head moved {head[:8]} -> {str(live)[:8]}, record dropped, no re-run")
                continue
            left = []
            for rid in r["run_ids"]:
                code, _ = self.t.run(["gh", "api", "-X", "POST", f"repos/{self.t.repo}/actions/runs/{rid}/rerun-failed-jobs"])
                if code:
                    left.append(rid)
            self.t.log(f"RESUME #{n} at {head[:8]}: runs {','.join(map(str, r['run_ids']))} ({why})"
                       + (f"; not yet re-runnable: {left}" if left else ""))
            if left:
                keep.append({**r, "run_ids": left})
        self.write(keep)


def _self_test() -> int:
    import tempfile
    n = bad = 0

    def check(label, ok):
        nonlocal n, bad
        n += 1
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")
    NOW = 1_800_000_000.0
    iso = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).isoformat().replace("+00:00", "Z")  # noqa: E731
    setting = {**ci_priority.load_setting(), "priority_cancel": True}
    roster = {"groups": [
        {"group": "CPG", "resume": {"branch": "fix/cp"}, "class": "instrument"},
        {"group": "T1", "resume": {"branch": "fix/t1"}, "class": "production"},
        {"group": "LOW", "resume": {"branch": "fix/low"}, "class": "instrument"},
        {"group": "LOWER", "resume": {"branch": "fix/lower"}, "class": "instrument"}]}
    crit = {rl.norm_group("CPG")}
    PRS = [("10", "fix/cp", "c" * 40), ("11", "fix/t1", "d" * 40), ("12", "fix/low", "e" * 40),
           ("13", "fix/lower", "f" * 40), ("14", "fix/head", "a" * 40)]
    HEAD = "a" * 40

    class Fake:
        def __init__(self, state):
            self.state, self.repo, self.posts, self.logs = Path(state), "o/r", [], []
            self.now, self.verdicted, self.prot, self.moved = NOW, set(), set(), set()
            self.active = {"c" * 40: [1], "d" * 40: [2], "e" * 40: [3, 4], "f" * 40: [5]}
            self.queued: "list | None" = []

        def wall(self):
            return self.now

        def log(self, s):
            self.logs.append(s)

        def protected_prs(self):
            return self.prot

        def run(self, cmd):
            c = " ".join(cmd)
            if "-X POST" in c:
                self.posts.append(c.split("repos/o/r/")[1])
                return 0, ""
            if "/pulls?state=open" in c:
                return 0, "\n".join(json.dumps({"n": int(a), "sha": s, "ref": r, "fork": False}) for a, r, s in PRS)
            if "/comments" in c:
                num = int(c.split("issues/")[1].split("/")[0])
                body = "Fix review: merge x" if num in self.verdicted else "hello"
                return 0, json.dumps([[{"body": body}]])
            if "/actions/runs?status=queued" in c:
                return (1, "") if self.queued is None else (0, "\n".join(json.dumps(r) for r in self.queued))
            if "/actions/runs?head_sha=" in c:
                sha = c.split("head_sha=")[1].split("&")[0]
                return 0, " ".join(map(str, self.active.get(sha, [])))
            if "/pulls/" in c and "/files" not in c:
                num = c.split("pulls/")[1].split()[0]
                sha = {a: s for a, r, s in PRS}[num]
                return 0, json.dumps({"head": {"sha": ("9" * 40) if int(num) in self.moved else sha}})
            return 1, ""

    def queued(age_min):
        return [{"status": "queued", "started_at": iso(NOW - age_min * 60)}]
    with tempfile.TemporaryDirectory() as td:
        def mk():
            f = Fake(td)
            Path(td, PAUSED).unlink(missing_ok=True)
            return f, CiPause(f, setting, (roster, crit))
        f, p = mk()
        p.poll(queued(6), HEAD)
        check("a head job queued 6 min pauses the lowest-priority PR (#13) and records it",
              f.posts == ["actions/runs/5/cancel"] and p.read()[0]["pr"] == 13
              and any(x.startswith("PAUSE #13 at ffffffff: runs 5 for aaaaaaaa") for x in f.logs))
        f.active["f" * 40] = []
        f.now += 60
        p.poll(queued(7), HEAD)
        check("at most one pause per pause_gap_min", len(p.read()) == 1)
        f.now += 400
        p.poll(queued(7), HEAD)
        check("the next pass takes the next victim (#12, both runs), never #10 (critical path) or #11",
              [r["pr"] for r in p.read()] == [13, 12] and f.posts[-2:] == ["actions/runs/3/cancel", "actions/runs/4/cancel"])
        f.posts.clear()
        p.poll([{"status": "completed"}], HEAD)
        check("head clears -> rerun-failed-jobs on each recorded run, records gone",
              sorted(f.posts) == sorted(f"actions/runs/{i}/rerun-failed-jobs" for i in (5, 3, 4)) and p.read() == []
              and any(x.startswith("RESUME #13") for x in f.logs))
        f, p = mk()
        p.poll(queued(1), HEAD)
        check("null: a head job queued under the bound pauses nothing", f.posts == [] and p.read() == [])
        p.poll([], HEAD)
        check("null: no queued job pauses nothing", f.posts == [])
        f, p = mk()
        f.active = {"c" * 40: [1], "d" * 40: [2]}
        p.poll(queued(6), HEAD)
        check("a critical-path PR (#10) and a production PR with no lower tier are skipped: tier1 #11 is the victim",
              f.posts == ["actions/runs/2/cancel"])
        f, p = mk()
        f.active = {"c" * 40: [1]}
        p.poll(queued(6), HEAD)
        check("the critical-path tail is never paused", f.posts == [])
        f, p = mk()
        f.verdicted, f.prot = {13}, {12}
        p.poll(queued(6), HEAD)
        check("carry 6: a verdicted PR (#13) and a train-held one (#12) are never victims; the next is",
              f.posts == ["actions/runs/2/cancel"])
        f, p = mk()
        f.prot = {10, 11, 12, 13}
        p.poll(queued(6), HEAD)
        check("the train head (#14, head sha) is never a victim", f.posts == [])
        f, p = mk()
        p.setting = {**setting, "priority_cancel": False}
        p.poll(queued(6), HEAD)
        check("the pause is not the sweep's switch: with priority_cancel off a head job queued 6 min still pauses #13",
              f.posts == ["actions/runs/5/cancel"] and p.read()[0]["pr"] == 13)
        # Carry 6 (ii): the hold the train asks before a re-run.
        f, p = mk()
        f.queued = [{"id": 900, "b": "fix/low"}, {"id": 901, "b": "fix/cp"}]
        check("hold: a non-priority head (#13) waits while priority #10 has a run queued, naming it",
              p.hold("f" * 40) == "priority #10 run 901 is queued")
        check("hold: a priority head (#10, critical path) never waits", p.hold("c" * 40) is None)
        check("hold: main's tip (no open pull request at it) never waits", p.hold("9" * 40) is None)
        f.queued = [{"id": 900, "b": "fix/low"}]
        check("hold null: only non-priority runs queued holds nothing", p.hold("f" * 40) is None)
        f.queued = None
        check("hold: an unreadable queue listing holds nothing", p.hold("f" * 40) is None)
        f, p = mk()
        p.poll(queued(6), HEAD)
        f.moved = {13}
        f.posts.clear()
        p.resume_all("exit")
        check("a moved head is dropped with no re-run", f.posts == [] and p.read() == []
              and any("head moved" in x for x in f.logs))
        f, p = mk()
        p.poll(queued(6), HEAD)
        f2 = Fake(td)
        CiPause(f2, setting, (roster, crit)).resume_all("start")
        check("a leftover record is resumed at the next train's start",
              f2.posts == ["actions/runs/5/rerun-failed-jobs"] and not Path(td, PAUSED).exists())
        check("an unreadable started_at is no age", queued_minutes([{"status": "queued", "started_at": None}], NOW) is None)
        check("queued_minutes is the oldest queued job's age in minutes, exactly",
              queued_minutes(queued(6) + queued(2) + [{"status": "completed", "started_at": iso(NOW - 3600)}], NOW) == 6.0)
        f, p = mk()
        p.poll(queued(setting["pause_queued_min"]), HEAD)
        check("a head job queued exactly pause_queued_min pauses (the bound is inclusive)", f.posts == ["actions/runs/5/cancel"])
        f.posts.clear()
        f.active["f" * 40] = []
        f.now += setting["pause_gap_min"] * 60
        p.poll(queued(9), HEAD)
        check("exactly pause_gap_min after a pause the next pass may pause again", f.posts == ["actions/runs/3/cancel", "actions/runs/4/cancel"])
        f, p = mk()
        p._note("k", "one")
        p._note("k", "two")
        p._note("j", "three")
        check("_note logs once per key", f.logs == ["one", "three"])
        check("_api: a failed command, an unparsable answer and an empty one read as None, None and {}",
              (p._api("nope"), (setattr(f, "run", lambda c: (0, "not json")), p._api("x"))[1],
               (setattr(f, "run", lambda c: (0, "  ")), p._api("x"))[1]) == (None, None, {}))
        Path(td, PAUSED).unlink(missing_ok=True)
        p.write([])
        sub = CiPause(Fake(Path(td) / "new" / "dir"), setting, (roster, crit))
        sub.write([{"pr": 1, "run_ids": [2]}])
        check("write: an empty list with no file is no error; a record lands in a state dir not yet made",
              not Path(td, PAUSED).exists() and sub.read() == [{"pr": 1, "run_ids": [2]}])
    print(f"ci_pause self-test: {n} checks, {bad} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(_self_test() if sys.argv[1:] == ["--self-test"] else 2)

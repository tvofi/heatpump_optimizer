#!/usr/bin/env python3
"""pulse.py -- is the programme still being driven? Read from origin alone.

    python3 -I tools/audit/seat/pulse.py [--repo OWNER/REPO] [--remote R]
        [--checkout DIR] [--opener-h H] [--verdict-h H] [--state-min M]
        [--dump FILE]
    python3 -I tools/audit/seat/pulse.py --snapshot FILE [--now EPOCH] [bounds]
    python3 -I tools/audit/seat/pulse.py --self-test

WHY THIS EXISTS (R10-RCA-ORCH-CONTINUITY, dev/audit/rca/R10-RCA-ORCH-CONTINUITY.md).
Every consumer the programme runs -- the opener, the verdict router, the
merge train, the state beat -- is a process or a turn on one host, launched by
hand and recorded nowhere durable (daemonize.py keeps no bookkeeping by
design), and the one watchdog, the sweep's tick watcher, runs in the session
it would have to watch. So when the session or its host stops, the output is
silence, and silence reads exactly like "nothing owed": round 10 lost four
sessions that way (10-16, 10-17, 10-20, 10-21), each found by the next
session's hand survey.

THE RULE. A consumer is judged by its owed input, never by a process: an input
an off-host producer already delivered to origin that the consumer's own
footprint on origin has not answered within a bound. Every input and every
footprint is a ref or a REST fact, so the verdict is the same from the
orchestrator's host, a cloud seat or a runner where the host is not -- which
is what makes it usable after the host is gone. Three arms:

  opener      a handoff with no pull request -- `bus.sh orphans`, whose
              predicate is invoked, never re-derived (the orphan record itself
              is R10-RCA-HANDOFF-SLIP's) -- aged at least --opener-h (default
              3 h), that arrived after the newest pull request opened from a
              `fix/` or `handoff/` head: the opener produced nothing since that
              input arrived. A standing backlog older than the last opening is
              the orphan record's, not a stop: counted in the detail only;
  verdict     a `review/<N>` verdict (`verdict: #N Fix review: <kind> <sha>`)
              whose pull request is still open at exactly that head, older
              than --verdict-h (default 2 h): a merge verdict the train has not
              landed, or a blocked one nobody routed back to its fixer;
  state-beat  the oldest main first-parent commit newer than the round's state
              ref's last commit (`handoff/audit-r<N>-plan`, the newest N) is
              older than --state-min (default 45 min): the beat regenerates on
              every main move, so a main that keeps moving cannot hide it.

Each arm prints one line, `PULSE <arm> ok|STOPPED|UNREADABLE <detail>`, then
`pulse: 3 arms, S stopped, U unreadable at <utc>`. Exit 1 when any arm is
STOPPED, else 2 when any is UNREADABLE, else 0. An input it could not read is
UNREADABLE and never ok: a shut fetch or a refused API call is not a clean
board. A stamp ahead of the reading clock is an unknowable age (fixer.md step
16): never aged, and named `skew` in the detail.

What it does not see, stated: a programme with nothing owed reads ok however
long it has been stopped -- no cost accrues there but time; a consumer whose
input no off-host producer writes (a local seat's work before its push); and
the record duty of a #201 comment per merge.

Run it where the host is not (a scheduled cloud probe seat), and at a
takeover before the hand survey. --dump writes the snapshot it judged, so a
STOPPED line is re-judgeable with --snapshot. Self-test: offline fixtures.
"""
from __future__ import annotations

import argparse
import calendar
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARMS = ("opener", "verdict", "state-beat")
NS = "refs/hpo-pulse"
VERDICT_RE = re.compile(r"^verdict: #(\d+) Fix review: (\S+) ([0-9a-f]{7,40})\b")
ORPHAN_RE = re.compile(r"^ORPHAN (\S+) (\S+) (\S+?)h? ")
SUMMARY_RE = re.compile(r"^orphans: (\d+) stranded")
PLAN_RE = re.compile(r"^refs/heads/handoff/audit-r(\d+)-plan$")


class Unreadable(Exception):
    pass


def bounds_s(opener_h: float, verdict_h: float, state_min: float) -> dict:
    return {"opener": opener_h * 3600, "verdict": verdict_h * 3600, "state-beat": state_min * 60}


def _age(now: float, t: float) -> float | None:
    """Seconds since t; None when t is ahead of the clock (unknowable)."""
    return None if t > now else now - t


def judge_opener(snap: dict, now: float, bound: float) -> tuple[str, str]:
    o, last = snap.get("orphans"), snap.get("last_open_t")
    if not isinstance(o, dict) or o.get("rc") not in (0, 1):
        return "UNREADABLE", f"bus.sh orphans did not report (rc={o.get('rc') if isinstance(o, dict) else None})"
    lines = str(o.get("out", "")).splitlines()
    if not any(map(SUMMARY_RE.match, lines)):
        return "UNREADABLE", "bus.sh orphans printed no summary line"
    if last is None:
        return "UNREADABLE", "the newest pull-request opening could not be read"
    owed, backlog, unknown = [], 0, 0
    for m in filter(None, map(ORPHAN_RE.match, lines)):
        try:
            h = float(m.group(3))
        except ValueError:
            unknown += 1
            continue
        if h * 3600 < bound:
            continue
        if now - h * 3600 > last:
            owed.append((h, m.group(1)))
        else:
            backlog += 1
    extra = "".join([f"; {backlog} older than the last opening" if backlog else "",
                     f"; {unknown} of unknown age" if unknown else ""])
    if owed:
        owed.sort(reverse=True)
        return "STOPPED", (f"{len(owed)} handoff(s) with no pull request for >= {bound / 3600:g} h and none "
                           f"opened since they arrived ({(now - last) / 3600:.1f} h), "
                           f"oldest {owed[0][1]} {owed[0][0]:.1f} h{extra}")
    return "ok", f"no handoff waiting >= {bound / 3600:g} h on an opener that has opened nothing since{extra}"


def judge_verdict(snap: dict, now: float, bound: float) -> tuple[str, str]:
    vs, heads = snap.get("verdicts"), snap.get("open_heads")
    if not isinstance(vs, list) or not isinstance(heads, dict):
        return "UNREADABLE", "the review refs or the open pull requests could not be read"
    owed, skew = [], 0
    for v in vs:
        head = heads.get(str(v["pr"]))
        if not head or not (head.startswith(v["sha"]) or v["sha"].startswith(head)):
            continue  # merged, closed, or its head moved: the verdict was consumed
        age = _age(now, v["t"])
        if age is None:
            skew += 1
        elif age > bound:
            owed.append((age, v))
    extra = f"; {skew} skew" if skew else ""
    if owed:
        owed.sort(key=lambda x: -x[0])
        age, v = owed[0]
        return "STOPPED", (f"{len(owed)} verdict(s) unconsumed at their head for > {bound / 3600:g} h, "
                           f"oldest #{v['pr']} {v['kind']} {v['sha'][:8]} {age / 3600:.1f} h{extra}")
    return "ok", f"every verdict at an open head is under {bound / 3600:g} h{extra}"


def judge_state(snap: dict, now: float, bound: float) -> tuple[str, str]:
    ref, mt, st = snap.get("state_ref"), snap.get("main_t"), snap.get("state_t")
    if not ref or mt is None or st is None:
        return "UNREADABLE", "main or the round's state ref could not be read"
    age = _age(now, mt)
    if st < mt and age is not None and age > bound:
        return "STOPPED", (f"main moved {age / 60:.0f} min ago and {ref} has not followed "
                           f"(its last commit {(mt - st) / 60:.0f} min before that move)")
    # main_t is the oldest main commit the state ref has not followed, or main's tip.
    return "ok", f"{ref} follows main within {bound / 60:g} min" + ("; skew" if age is None else "")


JUDGES = {"opener": judge_opener, "verdict": judge_verdict, "state-beat": judge_state}


def judge(snap: dict, bounds: dict) -> list[tuple[str, str, str]]:
    now = snap["now"]
    return [(arm, *JUDGES[arm](snap, now, bounds[arm])) for arm in ARMS]


def report(rows: list[tuple[str, str, str]], now: float) -> int:
    for arm, word, detail in rows:
        print(f"PULSE {arm} {word} {detail}")
    stopped = sum(w == "STOPPED" for _, w, _ in rows)
    unread = sum(w == "UNREADABLE" for _, w, _ in rows)
    print(f"pulse: {len(rows)} arms, {stopped} stopped, {unread} unreadable at "
          f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now))}")
    return 1 if stopped else 2 if unread else 0


# --- the live adapters: each returns its input, or None when unreadable ---

def _git(cwd: str, *args: str) -> str:
    return subprocess.run(["git", "-C", cwd, *args], check=True, capture_output=True, text=True).stdout


def read_orphans(cwd: str, remote: str) -> dict | None:
    env = dict(os.environ, HPO_BUS_REMOTE=remote)
    try:
        p = subprocess.run(["bash", str(HERE / "bus.sh"), "orphans", "--min-age-h", "0"],
                           cwd=cwd, env=env, capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return {"rc": p.returncode, "out": p.stdout}


def read_verdicts(cwd: str, remote: str) -> list | None:
    try:
        _git(cwd, "fetch", "-q", "--prune", remote, f"+refs/heads/review/*:{NS}/review/*")
        out = _git(cwd, "for-each-ref", "--format=%(committerdate:unix)%09%(subject)", f"{NS}/review/")
    except subprocess.CalledProcessError:
        return None
    vs = []
    for line in out.splitlines():
        t, _, subj = line.partition("\t")
        m = VERDICT_RE.match(subj)
        if m:
            vs.append({"pr": int(m.group(1)), "kind": m.group(2), "sha": m.group(3), "t": int(t)})
    return vs


def read_last_open(repo: str) -> int | None:
    """Epoch of the newest pull request opened from a fix/ or handoff/ head."""
    for page in range(1, 6):
        try:
            p = subprocess.run(["gh", "api", f"repos/{repo}/pulls?state=all&sort=created&direction=desc"
                                f"&per_page=100&page={page}", "--jq", ".[] | [.head.ref, .created_at] | @tsv"],
                               capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if p.returncode != 0 or not p.stdout.strip():
            return None
        for head, created in (l.split("\t") for l in p.stdout.splitlines()):
            if head.startswith(("fix/", "handoff/")):
                return calendar.timegm(time.strptime(created, "%Y-%m-%dT%H:%M:%SZ"))
    return None


def read_open_heads(repo: str) -> dict | None:
    heads: dict = {}
    for page in range(1, 11):
        try:
            p = subprocess.run(["gh", "api", f"repos/{repo}/pulls?state=open&per_page=100&page={page}",
                                "--jq", '.[] | "\\(.number) \\(.head.sha)"'],
                               capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if p.returncode != 0:
            return None
        rows = [l.split() for l in p.stdout.splitlines() if l.strip()]
        heads.update({n: s for n, s in rows})
        if len(rows) < 100:
            return heads
    return None  # more than ten pages is not a board this reads whole


def read_state(cwd: str, remote: str) -> dict:
    try:
        plans = [(int(m.group(1)), m.group(0)) for m in
                 (PLAN_RE.match(l.split("\t")[-1]) for l in
                  _git(cwd, "ls-remote", remote, "refs/heads/handoff/audit-r*-plan").splitlines()) if m]
        if not plans:
            return {"state_ref": None, "main_t": None, "state_t": None}
        ref = max(plans)[1]
        _git(cwd, "fetch", "-q", remote, f"+refs/heads/main:{NS}/main", f"+{ref}:{NS}/state")
        st = int(_git(cwd, "log", "-1", "--format=%ct", f"{NS}/state").strip())
        main = [int(x) for x in _git(cwd, "log", "--first-parent", "-200", "--format=%ct", f"{NS}/main").split()]
        mt = oldest_unfollowed(main, st)
    except (subprocess.CalledProcessError, ValueError):
        return {"state_ref": None, "main_t": None, "state_t": None}
    return {"state_ref": ref[len("refs/heads/"):], "main_t": mt, "state_t": st}


def oldest_unfollowed(main_times: list[int], state_t: int) -> int:
    """The oldest main commit time newer than the state ref's last commit, else
    main's newest: a main that keeps moving past a dead beat cannot reset the age."""
    return min((t for t in main_times if t > state_t), default=max(main_times))


def repo_of(cwd: str, remote: str) -> str | None:
    try:
        url = _git(cwd, "remote", "get-url", remote).strip()
    except subprocess.CalledProcessError:
        return None
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?/?$", url)
    return m.group(1) if m else None


def snapshot_live(cwd: str, remote: str, repo: str | None) -> dict:
    snap = {"now": int(time.time()), "orphans": read_orphans(cwd, remote),
            "last_open_t": read_last_open(repo) if repo else None,
            "verdicts": read_verdicts(cwd, remote),
            "open_heads": read_open_heads(repo) if repo else None}
    snap.update(read_state(cwd, remote))
    return snap


# --- self-test ---

def self_test() -> int:
    passed = failed = 0

    def check(name: str, ok: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + ok, failed + (not ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")

    now = 1_792_568_400  # 2026-10-21T07:40:00Z, the 10-21 takeover
    H, B = 3600, bounds_s(3, 2, 45)
    s_head, s_blk = "baa75f58ae7f9c00334d92da24d3285e1b047277", "de28f656ba17e2e381471d8d3a50dffdf2840cfc"
    clean = "orphans: 0 stranded, 0 superseded; skipped no-body=3 named=40 ancestor=60 young=1; origin main df6ca4b\n"

    def snap(**kw) -> dict:
        s = {"now": now, "orphans": {"rc": 0, "out": clean}, "last_open_t": now - 9 * H,
             "verdicts": [{"pr": 2526, "kind": "merge", "sha": s_head, "t": now - 20 * 60}],
             "open_heads": {"2526": s_head, "2531": "f" * 40},
             "state_ref": "handoff/audit-r10-plan", "main_t": now - 50 * 60, "state_t": now - 49 * 60}
        s.update(kw)
        return s

    def words(s: dict, b: dict = B) -> dict:
        return {arm: w for arm, w, _ in judge(s, b)}

    # Null control: a driven programme reads ok on every arm, and exits 0.
    healthy = snap()
    check("null control: a healthy board is ok on all three arms",
          words(healthy) == dict.fromkeys(ARMS, "ok"))
    # The 10-21 shape, as measured at the takeover: the #2527 blocked verdict
    # 7.7 h at its head, and nine stranded handoffs that all predate the last
    # opening (23:44Z, 7.9 h before) -- the backlog the orphan record owns.
    stranded = ("ORPHAN r10-merge-pr-mandate 1a2b3c4 110.0h uncovered=3 repair=opener\n"
                "ORPHAN r10-roster-sync 5d6e7f8 10.7h uncovered=1 repair=opener\n" + clean.replace("0 stranded", "2 stranded"))
    d1021 = snap(orphans={"rc": 1, "out": stranded}, last_open_t=now - int(7.9 * H),
                 verdicts=[{"pr": 2527, "kind": "blocked", "sha": s_blk, "t": now - int(7.7 * H)}],
                 open_heads={"2527": s_blk})
    r = {arm: (w, d) for arm, w, d in judge(d1021, B)}
    check("the 10-21 shape: the blocked #2527 verdict 7.7 h at its head is STOPPED",
          r["verdict"][0] == "STOPPED" and "#2527 blocked de28f656 7.7 h" in r["verdict"][1])
    check("the 10-21 shape: a backlog older than the last opening is counted, not a stop",
          r["opener"][0] == "ok" and "2 older than the last opening" in r["opener"][1])
    check("the 10-21 shape: a beat that died with the train is not blamed while main is still",
          r["state-beat"][0] == "ok")
    # The opener stopped: a handoff arrived 4 h ago and nothing was opened since (6 h).
    starved = snap(orphans={"rc": 1, "out": "ORPHAN r10-new 1a2b3c4 4.0h uncovered=1 repair=opener\n"
                            "ORPHAN r10-old 5d6e7f8 50.0h uncovered=1 repair=opener\n" + clean},
                   last_open_t=now - 6 * H)
    ro = {arm: (w, d) for arm, w, d in judge(starved, B)}
    check("a handoff 4 h old with no opening since it arrived: opener STOPPED, the rest ok",
          ro["opener"][0] == "STOPPED" and "oldest r10-new 4.0 h; 1 older than the last opening" in ro["opener"][1]
          and ro["verdict"][0] == ro["state-beat"][0] == "ok")
    check("the same handoff with an opening after it arrived is ok",
          words(snap(orphans=starved["orphans"], last_open_t=now - 1 * H))["opener"] == "ok")
    # The beat dead while the train still merges (10-19 14:11Z-16:45Z).
    beat = snap(main_t=now - 60 * 60, state_t=now - 155 * 60)
    check("main moved 60 min ago, the state ref did not follow: state-beat STOPPED, the rest ok",
          words(beat) == {"opener": "ok", "verdict": "ok", "state-beat": "STOPPED"})
    # Main moved at 60, 30 and 5 min ago past a beat last seen 70 min ago: the
    # age is the oldest unfollowed move's, so the newer moves cannot hide it.
    mts = [now - 5 * 60, now - 30 * 60, now - 60 * 60, now - 90 * 60]
    check("the state-beat age is the oldest main move the state ref has not followed",
          oldest_unfollowed(mts, now - 70 * 60) == now - 60 * 60
          and oldest_unfollowed(mts, now - 2 * 60) == now - 5 * 60)
    # The bounds are honoured: young inputs are not a stop.
    young = snap(orphans={"rc": 1, "out": "ORPHAN r10-x 1a2b3c4 0.5h uncovered=1 repair=opener\n" + clean},
                 verdicts=[{"pr": 2526, "kind": "merge", "sha": s_head, "t": now - 30 * 60}],
                 main_t=now - 10 * 60, state_t=now - 70 * 60)
    check("inputs younger than their bounds are ok on every arm", words(young) == dict.fromkeys(ARMS, "ok"))
    # Perturbation: the same 7.7 h verdict under a 9 h bound is ok -- the bound is what decides.
    check("perturbation: a --verdict-h above the verdict's age reads it ok",
          words(d1021, bounds_s(3, 9, 45))["verdict"] == "ok")
    # Consumed verdicts never fire, however old: merged (absent) or head moved.
    old = [{"pr": 2526, "kind": "merge", "sha": s_head, "t": now - 50 * H},
           {"pr": 2531, "kind": "blocked", "sha": "a" * 40, "t": now - 50 * H}]
    check("a verdict whose pull request merged or whose head moved is consumed",
          words(snap(verdicts=old, open_heads={"2531": "f" * 40}))["verdict"] == "ok")
    # Fail closed: an input not read is UNREADABLE, never ok, and the exit is 2.
    shut = snap(orphans={"rc": 3, "out": "bus: orphans: could not fetch"}, verdicts=None,
                state_ref=None)
    check("an unread last opening is UNREADABLE, never ok",
          words(snap(last_open_t=None))["opener"] == "UNREADABLE")
    check("unreadable inputs read UNREADABLE on every arm, never ok",
          words(shut) == dict.fromkeys(ARMS, "UNREADABLE"))
    check("a state ref with main or its own commit unread is UNREADABLE",
          words(snap(main_t=None))["state-beat"] == words(snap(state_t=None))["state-beat"] == "UNREADABLE")
    check("bus.sh rc 0 with no summary line is UNREADABLE",
          words(snap(orphans={"rc": 0, "out": ""}))["opener"] == "UNREADABLE")
    # A stamp ahead of the clock is unknowable: never aged, named skew.
    sk = {arm: (w, d) for arm, w, d in judge(snap(
        verdicts=[{"pr": 2526, "kind": "merge", "sha": s_head, "t": now + 600}],
        main_t=now + 600, state_t=now - 50 * H), B)}
    check("a stamp ahead of the clock is never aged and is named skew",
          sk["verdict"] == ("ok", sk["verdict"][1]) and "skew" in sk["verdict"][1]
          and sk["state-beat"][0] == "ok" and "skew" in sk["state-beat"][1])
    # The parsers read the real shapes the bus and the reviewer write.
    m = VERDICT_RE.match("verdict: #2527 Fix review: blocked de28f656ba17e2e381471d8d3a50dffdf2840cfc root-cause-unanswered: x")
    check("the verdict subject parser reads a blocked verdict's PR, kind and head",
          bool(m) and m.groups() == ("2527", "blocked", s_blk))
    check("a design-review subject is not a verdict",
          VERDICT_RE.match("design review round 3: orchestration machinery rev 3 (APPROVE)") is None)
    unk = snap(orphans={"rc": 1, "out": "ORPHAN r10-y 1a2b3c4 unknown-age uncovered=? repair=review\n" + clean})
    rr = {arm: (w, d) for arm, w, d in judge(unk, B)}
    check("an orphan of unknown age is named, never aged", rr["opener"][0] == "ok" and "1 of unknown age" in rr["opener"][1])
    # The CLI: --snapshot judges a dumped board, and the exit codes are 1 / 2 / 0.
    with tempfile.TemporaryDirectory() as td:
        codes = []
        for i, s in enumerate((d1021, shut, healthy)):
            f = Path(td) / f"s{i}.json"
            f.write_text(json.dumps(s))
            out = subprocess.run([sys.executable, "-I", __file__, "--snapshot", str(f)],
                                 capture_output=True, text=True)
            codes.append(out.returncode)
            if i == 0:
                last = out.stdout.splitlines()[-1] if out.stdout else ""
        check("--snapshot exits 1 on a stop, 2 on unreadable, 0 on a healthy board", codes == [1, 2, 0])
        check("the summary line counts the arms", last.startswith("pulse: 3 arms, 1 stopped, 0 unreadable at 2026-10-21T07:40:00Z"))
    print(f"pulse self-test: {passed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--repo", help="OWNER/REPO for the REST read (default: from the remote's URL)")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--checkout", default=".", help="a clone of the repository (default: the cwd)")
    ap.add_argument("--opener-h", type=float, default=3.0)
    ap.add_argument("--verdict-h", type=float, default=2.0)
    ap.add_argument("--state-min", type=float, default=45.0)
    ap.add_argument("--snapshot", type=Path, help="judge this dumped snapshot instead of origin")
    ap.add_argument("--now", type=int, help="with --snapshot: the reading clock (epoch seconds)")
    ap.add_argument("--dump", type=Path, help="write the live snapshot judged here")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    b = bounds_s(a.opener_h, a.verdict_h, a.state_min)
    if a.snapshot:
        snap = json.loads(a.snapshot.read_text())
        if a.now is not None:
            snap["now"] = a.now
    else:
        snap = snapshot_live(a.checkout, a.remote, a.repo or repo_of(a.checkout, a.remote))
        if a.dump:
            a.dump.write_text(json.dumps(snap, indent=1) + "\n")
    return report(judge(snap, b), snap["now"])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

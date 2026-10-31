#!/usr/bin/env python3
"""Say which tick OWED lines have outlived a sweep with no live acknowledgement.

    python3 -I tools/audit/seat/owed_unactioned.py --tick <tick.txt> --state <state.json> \
        [--acks <file>]... [--after 2] [--max-board-min 20] [--now <ISO>] [--no-write]
    python3 -I tools/audit/seat/owed_unactioned.py --self-test

WHY THIS EXISTS (dev/audit/rca/R10-RCA-OWED-UNACTIONED.md). The tick prints its
owed lines level-triggered, every pass, and escalates a stranded handoff by age;
the sweep read them and still left them standing for hours, because a line the
orchestrator handled once -- routed to a seat, waited on a named PR, believed the
relay would move -- prints identically after that handling has failed. Nothing
asked again. On 2026-10-28 the critical-path handoff r10-orch-beatd (#2916) stood
1.7 h on `repair=review` while the relay printed HELD-REVIEW on every pass, and
two handoffs routed to the opener at 10:55Z stood 8 h.

WHAT IT DOES. It reads the tick board's owed family -- every `-> ` line that
starts `OWED`, `REVIEW OWED:`, `DISPATCH:`, `OWNER FLAG:`, `DESIGN-BUILD:`,
`MERGE-READY:`, `BLOCKED-UNFIXED:`, `APPROVAL-OWED:` or `UNLEVELLED:` -- and keys each on its obligation: the
handoff topic, or `#<pr>`. A verdict level (`MERGE-READY: #N <head8>`) carries
its head8 as the id, so an acknowledgement covers one head and a new head
re-raises. `APPROVAL-OWED:` means queue the PR for the train, which posts the
approval itself; `UNLEVELLED:` means a merge verdict at the head in a state no level
names, to be read by hand. The state file
counts the sweeps (distinct boards, by the board's provenance time) each key has
stood on. A key standing on `--after` sweeps or more is UNACTIONED unless an
acknowledgement line in an `--acks` file covers it now:

    OWED-ACK <UTC ISO> <key> <id> [ttl=<hours>] <next action; what it waits on>

It is a line of its own (the tool's indented `ack:` echo is not), its reason
holds no `<placeholder>`, and its id is a 7+ character prefix of a sha the
key's lines carry this board, or the whole of the ledger's own id for a kind
with no sha (`-` for a line with none). So a new tip needs a new
acknowledgement, and logging the tool's output acknowledges nothing. An acknowledgement lapses after ttl hours (default 1, at
most 12, the owner's OWNER FLAG threshold), so a handled line comes back and the
handling is checked again. Free text in a queue file is not an acknowledgement.

EXIT. 0: no owed key is unactioned. 1: the UNACTIONED block, oldest first, each
with a ready OWED-ACK line to fill in -- the sweep is not done. 2: cannot say --
no tick file, no provenance line, a board older than --max-board-min, an owed
line it cannot key, an unreadable state file -- never a clean zero. A refused
OWED-ACK line is printed and covers nothing.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import tempfile

FAMILY = re.compile(r"^-> (OWED|REVIEW OWED:|DISPATCH:|OWNER FLAG:|DESIGN-BUILD:|MERGE-READY:|BLOCKED-UNFIXED:|APPROVAL-OWED:|UNLEVELLED:)")
BOARD = re.compile(r"^BOARD measured from origin/main at \S+, (\S+)")
SHA = re.compile(r"\b[0-9a-f]{12,40}\b")
REF = re.compile(r"\b(?:refs/heads/)?(?:handoff-body|handoff|design)/(\S+)")
# Anchored at the line start (a list marker allowed): the tool's own `      ack: OWED-ACK ...`
# echo is not an acknowledgement, and a reason still holding a `<placeholder>` is refused.
ACK = re.compile(r"^\s*(?:[-*]\s+)?OWED-ACK (\S+) (\S+) (\S+)(?: ttl=(\S+))? +(\S.*)$")
PLACEHOLDER = re.compile(r"<[^<>]*>")
ID_FLOOR = 7  # an id shorter than this covers a sha only by being the whole id
TTL_DEFAULT, TTL_MAX = 1.0, 12.0


class Unreadable(Exception):
    pass


def utc(s: str) -> dt.datetime:
    t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError(f"{s}: no zone")
    return t.astimezone(dt.timezone.utc)


def key_of(line: str) -> "tuple[str, list[str]]":
    """(key, shas) for one owed-family line; Unreadable when it names no obligation."""
    body = line[3:]
    shas = [s[:12] for s in SHA.findall(body)]
    m = re.match(r"REVIEW OWED: (#\d+)", body)
    if m:
        return m.group(1), shas
    m = re.match(r"(?:MERGE-READY|BLOCKED-UNFIXED|APPROVAL-OWED): (#\d+) ([0-9a-f]{8})$", body)
    if m:
        return m.group(1), [m.group(2)]
    m = re.match(r"UNLEVELLED: (#\d+) ([0-9a-f]{8}) \S+$", body)
    if m:
        return m.group(1), [m.group(2)]
    m = re.match(r"OWED handoff: (\S+) ", body)
    if m:
        return m.group(1), shas
    m = re.match(r"OWED: OWED \S+ \S+ (\S+) (\S+)", body)
    if m:
        subj = m.group(1)
        shas = shas or [m.group(2)]  # a kind whose id is no sha (push-stuck: a pid)
        r = REF.match(subj)
        return (r.group(1) if r else f"#{subj}" if subj.isdigit()
                else subj.removeprefix("refs/heads/")), shas
    m = REF.search(body)
    if m and re.match(r"(DISPATCH|OWNER FLAG|DESIGN-BUILD): ", body):
        return m.group(1), shas
    raise Unreadable(f"an owed line names no topic or pull request: {line[:120]}")


def board(text: str) -> "tuple[dt.datetime, dict]":
    lines = text.splitlines()
    m = BOARD.match(lines[0]) if lines else None
    if not m:
        raise Unreadable("no `BOARD measured from origin/main at <sha>, <UTC>` provenance line")
    keys: dict = {}
    for line in lines:
        if FAMILY.match(line):
            k, shas = key_of(line)
            e = keys.setdefault(k, {"shas": [], "lines": []})
            e["shas"] += [s for s in shas if s not in e["shas"]]
            e["lines"].append(line)
    return utc(m.group(1)), keys


def acks(texts: list, now: dt.datetime) -> "tuple[dict, list[str]]":
    """{key: [(sha, expiry, reason)]} live now, and the refused lines."""
    live, refused = {}, []
    for name, text in texts:
        for n, line in enumerate(text.splitlines(), 1):
            if "OWED-ACK" not in line:
                continue
            m = ACK.search(line)
            why = None
            if not m:
                why = ("not a line of its own: `OWED-ACK <UTC ISO> <key> <id> [ttl=<h>] <reason>` "
                       "(the tool's own `ack:` echo is not one)")
            elif PLACEHOLDER.search(m.group(5)):
                why = "the reason is still the template's <placeholder>"
            else:
                try:
                    at = utc(m.group(1))
                    ttl = float(m.group(4) or TTL_DEFAULT)
                except ValueError as e:
                    at, ttl, why = None, 0.0, f"unparsable time or ttl ({e})"
                if why is None and not 0 < ttl <= TTL_MAX:
                    why = f"ttl={m.group(4)} outside (0, {TTL_MAX:g}] hours"
                if why is None and at > now + dt.timedelta(minutes=5):
                    why = "stamped ahead of the clock"
            if why:
                refused.append(f"REFUSED ack {name}:{n}: {why}")
                continue
            exp = at + dt.timedelta(hours=ttl)
            if exp > now:
                live.setdefault(m.group(2), []).append((m.group(3), exp, m.group(5)))
    return live, refused


def run(tick: str, state_path: str, ack_texts: list, now: dt.datetime, after: int,
        max_board_min: float, write: bool, out) -> int:
    try:
        when, keys = board(tick)
    except (Unreadable, ValueError) as e:
        out(f"UNREADABLE: {e}")
        return 2
    age = (now - when).total_seconds() / 60
    if age > max_board_min:
        out(f"UNREADABLE: the board is {age:.0f} min old (over {max_board_min:g}); "
            "a stale board cannot say a line was discharged")
        return 2
    try:
        with open(state_path, encoding="utf-8") as fh:
            state = json.load(fh)
        if not isinstance(state.get("keys"), dict):
            raise ValueError("no `keys` object")
        for k, e in state["keys"].items():
            if not (isinstance(e, dict) and isinstance(e.get("first"), str)
                    and isinstance(e.get("sweeps"), int) and not isinstance(e["sweeps"], bool)
                    and e["sweeps"] >= 1):
                raise ValueError(f"entry `{k}` is not {{first: <UTC>, sweeps: <n >= 1>}}")
            utc(e["first"])
    except FileNotFoundError:
        state = {"board": None, "keys": {}}
    except (OSError, ValueError) as e:
        out(f"UNREADABLE: state {state_path}: {e}")
        return 2
    stamp = when.strftime("%Y-%m-%dT%H:%M:%SZ")
    fresh = stamp != state.get("board")
    seen = {}
    for k in keys:
        old = state["keys"].get(k)
        if old is None:
            seen[k] = {"first": stamp, "sweeps": 1}
        else:
            seen[k] = {"first": old["first"], "sweeps": old["sweeps"] + (1 if fresh else 0)}
    if write:
        d = os.path.dirname(os.path.abspath(state_path))
        fd, tmp = tempfile.mkstemp(dir=d, prefix=".owed-unactioned.")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump({"board": stamp, "keys": seen}, fh, indent=1, sort_keys=True)
        os.replace(tmp, state_path)
    live, refused = acks(ack_texts, now)
    for r in refused:
        out(r)
    acked, bad = [], []
    for k, s in sorted(seen.items(), key=lambda kv: (kv[1]["first"], kv[0])):
        ids = keys[k]["shas"]
        cover = [a for a in live.get(k, []) if (a[0] == "-" and not ids) or any(
            x == a[0] or (len(a[0]) >= ID_FLOOR and (x.startswith(a[0]) or a[0].startswith(x)))
            for x in ids)]
        if cover:
            acked.append((k, max(cover, key=lambda a: a[1])))
        elif s["sweeps"] >= after:
            bad.append((k, s))
    out(f"owed: {len(seen)} key(s) on board {stamp}; {len(acked)} acknowledged, "
        f"{len(bad)} unactioned (standing {after}+ sweeps with no live OWED-ACK)")
    for k, (sha, exp, reason) in acked:
        out(f"  acked {k} {sha} until {exp.strftime('%H:%MZ')}: {reason[:100]}")
    if not bad:
        return 0
    out("UNACTIONED")
    for k, s in bad:
        h = (now - utc(s["first"])).total_seconds() / 3600
        out(f"  {k}  sweeps={s['sweeps']} first={s['first']} ({h:.1f}h)")
        for line in keys[k]["lines"]:
            out(f"      {line[:200]}")
        sha = keys[k]["shas"][0] if keys[k]["shas"] else "-"
        out(f"      ack: OWED-ACK <UTC> {k} {sha} ttl=1 <next action, by whom; what it waits on>")
    return 1


# ------------------------------------------------------------------ self-test
def self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + bool(cond), failed + (not cond)
        if not cond:
            print(f"FAIL {name}")

    t0 = utc("2026-10-28T17:20:00Z")

    def tick(at: dt.datetime, *lines: str) -> str:
        return "\n".join([f"BOARD measured from origin/main at beb570c817c4, {at.isoformat()}",
                          "== PRS ==", "-> #2887: mergeable state DIRTY"] + list(lines)) + "\n"

    beatd = ("-> OWED handoff: r10-orch-beatd c991d64cdaef342d282d1a8e991dadc2671f917d 1.6h "
             "uncovered=1 repair=review -- no PR head carries it")
    held = ("-> OWED: OWED 2026-10-28T18:57:09Z handoff-held refs/heads/handoff/r10-orch-beatd "
            "c991d64cdaef342d282d1a8e991dadc2671f917d #2916 REVIEW")
    disp = ("-> DISPATCH: ? refs/heads/handoff/triage-s7-batch49 40bec0ab6c44 opener (8.9h; "
            "last attempt 2026-10-28T17:36:08Z,unopened)")
    review = "-> REVIEW OWED: #2896 5f3a5dd615b5"
    event = ("-> OWED: OWED 2026-10-28T18:11:39Z verdict-unposted 2920 "
             "9328902275ba97b94d71f1778cf23f1eb2df031c Fix review: blocked")

    with tempfile.TemporaryDirectory() as d:
        def go(text, acks_=(), now=None, state="s.json", after=2, write=True):
            lines: list = []
            rc = run(text, os.path.join(d, state), [("acks", a) for a in acks_],
                     now or utc(BOARD.match(text).group(1)) + dt.timedelta(minutes=1),
                     after, 20, write, lines.append)
            return rc, "\n".join(lines)

        # keying: one obligation per topic or pull request, whatever the line's shape
        _, k = board(tick(t0, beatd, held, disp, review, event))
        check("beatd's two line shapes are one key", set(k) == {"r10-orch-beatd", "triage-s7-batch49",
                                                                 "#2896", "#2920"})
        check("the key carries its sha", "c991d64cdaef" in k["r10-orch-beatd"]["shas"])
        check("a non-owed flagged line is not owed", not any("#2887" in x for x in k))
        _, k2 = board(tick(t0, "-> OWED: OWED 2026-10-28T00:53:40Z push-stuck fix-r10-diag-ages 98785 STUCK 1641s"))
        check("a kind with no sha keys on its id column", k2.get("fix-r10-diag-ages", {}).get("shas") == ["98785"])

        # the defect: the same lines on successive boards, nothing acknowledges them
        rc1, o1 = go(tick(t0, beatd, disp))
        check("first sweep: new, not yet unactioned", rc1 == 0 and "UNACTIONED" not in o1)
        rc2, o2 = go(tick(t0 + dt.timedelta(minutes=10), beatd, disp))
        check("second sweep: unactioned, exit 1", rc2 == 1 and "UNACTIONED" in o2
              and "r10-orch-beatd  sweeps=2" in o2 and "triage-s7-batch49  sweeps=2" in o2)
        check("it prints a ready ack line", "ack: OWED-ACK " in o2 and " r10-orch-beatd c991d64cdaef ttl=1" in o2)
        rc2b, o2b = go(tick(t0 + dt.timedelta(minutes=10), beatd, disp))
        check("the same board re-read adds no sweep", "sweeps=2" in o2b and "sweeps=3" not in o2b)
        check("free text in a queue names the topic and covers nothing",
              go(tick(t0 + dt.timedelta(minutes=20), beatd, disp),
                 ["- 17:39Z opener done: batch49 refused BAD-DEST; r10-orch-beatd relay updates #2916"])[0] == 1)

        # acknowledgements: live, matching sha, lapsing
        now = t0 + dt.timedelta(minutes=31)
        ok = [f"OWED-ACK {(now - dt.timedelta(minutes=5)).isoformat()} r10-orch-beatd c991d64cd "
              "release #2916 in cloud-handoff-release; reviewer at e09b123f9 finishing",
              f"OWED-ACK {(now - dt.timedelta(minutes=5)).isoformat()} triage-s7-batch49 40bec0ab6 ttl=2 "
              "opener re-run after RCA-HEADMOVED carry; opener seat s7"]
        rc3, o3 = go(tick(t0 + dt.timedelta(minutes=30), beatd, disp), ok, now=now)
        check("null control: every standing key acknowledged -> exit 0", rc3 == 0 and "2 acknowledged" in o3)
        later = t0 + dt.timedelta(minutes=95)
        rc4, o4 = go(tick(t0 + dt.timedelta(minutes=90), beatd, disp), ok, now=later)
        check("a 1 h ack lapses, a 2 h ack holds", rc4 == 1 and "r10-orch-beatd  sweeps" in o4
              and "triage-s7-batch49  sweeps" not in o4)
        newtip = beatd.replace("c991d64cdaef342d282d1a8e991dadc2671f917d", "a" * 40)
        rc5, _ = go(tick(t0 + dt.timedelta(minutes=40), newtip), ok, now=t0 + dt.timedelta(minutes=41),
                    state="tip.json", after=1)
        check("an ack for the old tip does not cover a new tip", rc5 == 1)
        bad_ack = [f"OWED-ACK {(now + dt.timedelta(hours=1)).isoformat()} r10-orch-beatd c991d64cd later",
                   f"OWED-ACK {now.isoformat()} r10-orch-beatd c991d64cd ttl=48 park it",
                   "OWED-ACK r10-orch-beatd soon"]
        rc6, o6 = go(tick(t0 + dt.timedelta(minutes=30), beatd), bad_ack, now=now,
                     state="bad.json", after=1)
        check("future, over-long and malformed acks are refused and cover nothing",
              rc6 == 1 and o6.count("REFUSED ack") == 3)

        # discharge and the clean board
        rc7, o7 = go(tick(t0 + dt.timedelta(minutes=100), disp), ok, now=later + dt.timedelta(minutes=6))
        check("a discharged key leaves the state", rc7 == 0 and "r10-orch-beatd" not in o7)
        with open(os.path.join(d, "s.json"), encoding="utf-8") as fh:
            check("state drops it too", "r10-orch-beatd" not in json.load(fh)["keys"])
        rc8, o8 = go(tick(t0), state="clean.json", after=1)
        check("null control: an all-clear board exits 0 with 0 keys", rc8 == 0 and "owed: 0 key(s)" in o8)

        # never green by skipping
        check("no provenance line: exit 2", go("-> OWED handoff: x " + "a" * 40 + "\n", now=t0)[0] == 2)
        check("a stale board: exit 2", go(tick(t0, beatd), now=t0 + dt.timedelta(minutes=45),
                                          state="stale.json")[0] == 2)
        check("an owed line it cannot key: exit 2", go(tick(t0, "-> OWED something new"),
                                                       state="unk.json")[0] == 2)
        with open(os.path.join(d, "broken.json"), "w", encoding="utf-8") as fh:
            fh.write("{")
        check("an unreadable state: exit 2", go(tick(t0, beatd), state="broken.json")[0] == 2)
        rc9, _ = go(tick(t0, beatd), state="nowrite.json", write=False)
        check("--no-write writes nothing", not os.path.exists(os.path.join(d, "nowrite.json")))

        # round 2 (#2930 review 1): the tool's own output is no acknowledgement
        e1 = t0 + dt.timedelta(hours=3)
        go(tick(e1, beatd, disp), state="echo.json")
        rce, oe = go(tick(e1 + dt.timedelta(minutes=10), beatd, disp), state="echo.json")
        rcf, of_ = go(tick(e1 + dt.timedelta(minutes=20), beatd, disp), [oe], state="echo.json")
        check("logging the tool's own output acknowledges nothing (exit 1)", rce == 1 and rcf == 1
              and "0 acknowledged" in of_ and "r10-orch-beatd  sweeps=3" in of_)
        filled = oe.replace("ack: OWED-ACK", "OWED-ACK").replace(
            "<next action, by whom; what it waits on>", "opener seat re-runs batch49; waits on #2909's carry")
        filled = "\n".join(l.strip() for l in filled.splitlines() if l.strip().startswith("OWED-ACK"))
        filled = filled.replace("<UTC>", (e1 + dt.timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        rcg, og = go(tick(e1 + dt.timedelta(minutes=30), beatd, disp), [filled], state="echo.json")
        check("null control: the same lines, filled in and timed, acknowledge both", rcg == 0
              and "2 acknowledged" in og)
        ph = (f"OWED-ACK {(e1 + dt.timedelta(minutes=15)).isoformat()} r10-orch-beatd c991d64cdaef "
              "ttl=1 <next action, by whom; what it waits on>")
        rch, oh = go(tick(e1 + dt.timedelta(minutes=40), beatd), [ph], state="ph.json", after=1)
        check("a reason that is still a <placeholder> is refused", rch == 1 and "REFUSED ack" in oh)
        echo = ("      ack: " + ph.replace("<next action, by whom; what it waits on>", "a real reason"))
        rck, ok_ = go(tick(e1 + dt.timedelta(minutes=40), beatd), [echo], state="echo2.json", after=1)
        check("an indented `ack:` echo, timed and reasoned, is still no acknowledgement",
              rck == 1 and "REFUSED ack" in ok_)
        check("the printed template carries no time, so it cannot parse as one",
              "ack: OWED-ACK <UTC> r10-orch-beatd " in oe)
        short = f"OWED-ACK {(e1 + dt.timedelta(minutes=15)).isoformat()} r10-orch-beatd c ttl=1 short id"
        rci, oi = go(tick(e1 + dt.timedelta(minutes=40), beatd), [short], state="short.json", after=1)
        check("an id under 7 characters covers no sha", rci == 1 and "0 acknowledged" in oi)
        pid = f"OWED-ACK {(e1 + dt.timedelta(minutes=15)).isoformat()} fix-r10-diag-ages 98785 ttl=1 seat restarted"
        rcj, _ = go(tick(e1 + dt.timedelta(minutes=40),
                         "-> OWED: OWED 2026-10-28T00:53:40Z push-stuck fix-r10-diag-ages 98785 STUCK 1641s"),
                    [pid], state="pid.json", after=1)
        check("null control: a whole non-sha id (a pid) still covers its key", rcj == 0)
        # P277: the verdict levels, keyed `#<N>` with `<head8>` as the id
        mr, bu = "-> MERGE-READY: #2896 5f3a5dd6", "-> BLOCKED-UNFIXED: #2933 1a2b3c4d"
        ao, ul = "-> APPROVAL-OWED: #3022 0a1b2c3d", "-> UNLEVELLED: #3029 4e5f6a7b BLOCKED/APPROVED"
        for name, line, key, h8 in (("MERGE-READY", mr, "#2896", "5f3a5dd6"),
                                    ("BLOCKED-UNFIXED", bu, "#2933", "1a2b3c4d"),
                                    ("APPROVAL-OWED", ao, "#3022", "0a1b2c3d"),
                                    ("UNLEVELLED", ul, "#3029", "4e5f6a7b")):
            st = f"lv-{name}.json"
            v0 = t0 + dt.timedelta(hours=5)
            go(tick(v0, line), state=st)
            rcl, ol = go(tick(v0 + dt.timedelta(minutes=10), line), state=st)
            check(f"{name}: keyed {key} on its head8, unactioned on the second sweep",
                  rcl == 1 and f"{key}  sweeps=2" in ol and f" {key} {h8} ttl=1" in ol)
            lack = [f"OWED-ACK {(v0 + dt.timedelta(minutes=15)).isoformat()} {key} {h8} "
                    "merge seat lands it after the train; waits on CI"]
            rcm, om = go(tick(v0 + dt.timedelta(minutes=20), line), lack, state=st)
            check(f"{name}: an OWED-ACK on #<N> <head8> covers it", rcm == 0 and "1 acknowledged" in om)
            moved = line.replace(h8, "9e8d7c6b")
            rcn, on = go(tick(v0 + dt.timedelta(minutes=30), moved), lack, state=st)
            check(f"{name}: a new head8 re-raises", rcn == 1 and f"{key}  sweeps=4" in on
                  and f" {key} 9e8d7c6b ttl=1" in on)
        _, kv = board(tick(t0, review, mr))
        check("REVIEW OWED and MERGE-READY on one pull request are one key",
              set(kv) == {"#2896"} and kv["#2896"]["shas"] == ["5f3a5dd615b5", "5f3a5dd6"])
        check("null control: a board without the levels keys as before", set(board(
            tick(t0, beatd, held, disp, review, event))[1]) == {"r10-orch-beatd", "triage-s7-batch49",
                                                                 "#2896", "#2920"})
        with open(os.path.join(d, "entry.json"), "w", encoding="utf-8") as fh:
            json.dump({"board": None, "keys": {"r10-orch-beatd": {"sweeps": 2}}}, fh)
        check("a malformed state entry: exit 2", go(tick(t0, beatd), state="entry.json")[0] == 2)

    print(f"owed_unactioned self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tick")
    ap.add_argument("--state")
    ap.add_argument("--acks", action="append", default=[])
    ap.add_argument("--after", type=int, default=2)
    ap.add_argument("--max-board-min", type=float, default=20.0)
    ap.add_argument("--now")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.tick or not a.state or a.after < 1:
        ap.error("--tick and --state are required, and --after is at least 1")
    try:
        with open(a.tick, encoding="utf-8", errors="replace") as fh:
            tick = fh.read()
        texts = []
        for p in a.acks:
            with open(p, encoding="utf-8", errors="replace") as fh:
                texts.append((os.path.basename(p), fh.read()))
    except OSError as e:
        print(f"UNREADABLE: {e}")
        return 2
    now = utc(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    return run(tick, a.state, texts, now, a.after, a.max_board_min, not a.no_write, print)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

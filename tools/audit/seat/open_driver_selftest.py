"""Self-test of open_driver.py: topic resolution, order, skips, runs, the git layer.

    open_driver.py's own test switch runs this module
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import open_driver as od  # noqa: E402

A = "a" * 40
NOW = 1_800_000_000.0


def sha(c):
    return c * 40


def roster(*names, after=None):
    after = after or {}
    return {"groups": [{"group": n, "resume": {"stage": "not-started"}, "after": after.get(n, [])} for n in names]}


class Fake:
    """A world with no git: tips, bodies, a landed set, launches recorded."""

    def __init__(self, ros, heads=(), landed=(), bodies=None, extra=()):
        self.ros, self.launched, self.landed_set, self.bodies = ros, [], set(landed), bodies or {}
        self.t = {"refs/heads/main": sha("9")}
        for i, (topic, s) in enumerate(heads):
            self.t[f"refs/heads/handoff/{topic}"] = s
            self.t[f"refs/heads/handoff-body/{topic}"] = sha("b")
        for r in extra:
            self.t[r] = sha("c")
        self.dead, self.pid = set(), 100
        self.head = sha("e")  # the tools checkout's HEAD (World.tools_head)

    def tips(self):
        return self.t

    def body_head(self, topic):
        return self.bodies.get(topic, "")

    def landed(self, main, s):
        return s in self.landed_set

    def roster(self):
        return self.ros

    def launch(self, topic, s, title, group):
        self.launched.append((topic, title, group))
        self.pid += 1
        return self.pid

    def alive(self, pid):
        return pid not in self.dead

    def tools_head(self):
        return self.head


def rd(p):
    try:
        return p.read_text()
    except OSError:
        return None


def line(topic, s, ct=None):
    return f"OWED 2026-11-02T00:00:00Z handoff-no-pr refs/heads/handoff/{topic} {s}" + (f" ct={int(ct)}" if ct else "")


def run():
    n = bad = 0

    def check(name, ok):
        nonlocal n, bad
        n += 1
        if not ok:
            bad += 1
            print(f"FAIL {name}")

    G = {"R10-SAV-COMFORT", "R10-ROSTER-OPS", "R10-ROSTER-OPS-2", "R10-PREPR-CAP", "R10-CI-LAYOUT-P1", "R10-CI-LAYOUT-P2",
         "R10-ROSTER-OPS-3", "R10-FLY-TRAIN-DEFAULTS", "R10-UX-HEALTH"}
    r = lambda t, body="": od.resolve(t, G - {"R10-ROSTER-OPS-3"} if t == "r10-roster-ops-3" else G, body)
    check("sav-comfort-p2", r("r10-sav-comfort-p2", "R10-SAV-COMFORT part 2") == ("R10-SAV-COMFORT", "R10-SAV-COMFORT (part 2): r10 sav comfort p2"))
    check("roster-ops-2-p1", r("r10-roster-ops-2-p1", "x\nR10-ROSTER-OPS-2 part 1")[0] == "R10-ROSTER-OPS-2")
    check("prepr-cap-2 by -N", r("r10-prepr-cap-2", "R10-PREPR-CAP")[0] == "R10-PREPR-CAP")
    check("fly-train-defaults-p2", r("r10-fly-train-defaults-p2", "R10-FLY-TRAIN-DEFAULTS")[0] == "R10-FLY-TRAIN-DEFAULTS")
    check("ux-health-p3", r("r10-ux-health-p3", "R10-UX-HEALTH")[1].startswith("R10-UX-HEALTH (part 3): "))
    check("exact wins: roster-ops-2", r("r10-roster-ops-2", "R10-ROSTER-OPS")[0] == "R10-ROSTER-OPS-2")
    check("exact wins: ci-layout-p1", r("r10-ci-layout-p1", "R10-CI-LAYOUT-P2")[0] == "R10-CI-LAYOUT-P1")
    check("exact needs no body", r("r10-ci-layout-p2", "")[0] == "R10-CI-LAYOUT-P2")
    check("null: record topic", r("r10-record-s9-owed", "R10-RECORD")[0] is None)
    check("null: foo-2 body silent", od.resolve("r10-foo-2", G | {"R10-FOO"}, "R10-OTHER")[0] is None)
    check("null: roster-ops-3 names only itself",
          od.resolve("r10-roster-ops-3", G - {"R10-ROSTER-OPS-3"}, "R10-ROSTER-OPS-3 part")[0] is None)
    check("null: absent group, namesake prefix", od.resolve("r10-bar-p2", {"R10-BAR-P"}, "R10-BAR")[0] is None)
    check("null: body names a longer name only", od.resolve("r10-sav-comfort-p2", G, "R10-SAV-COMFORT-EXTRA")[0] is None)
    check("triage by rule", od.resolve("triage-s6-batch105", {"R10-TRIAGE-S6"}, "")[0] == "R10-TRIAGE-S6")
    check("triage falls back to R10-TRIAGE-B<M>", od.resolve("triage-s6-batch105", {"R10-TRIAGE-B105"}, "") == ("R10-TRIAGE-B105", "R10-TRIAGE-B105: triage s6 batch105"))
    check("null: triage with neither group", od.resolve("triage-s6-batch105", {"R10-TRIAGE-S7"}, "")[0] is None)
    pb = od.parse_board(line("r10-a", sha("1")) + "\n" + line("r10-a", sha("2")) + "\n" + line("r10-b", sha("3")))
    check("parse_board: one per topic, the first line wins", pb == [("r10-a", sha("1"), None), ("r10-b", sha("3"), None)])
    # The board the beat passes is the tick's (beat_jobs.py opener: the overlay's tick_log), where
    # every owed level line is flagged `-> OWED: <line>` (orchestrator_tick.py renders `"-> " + "OWED: " + row`).
    # Read only bare lines, the driver parsed nothing from the live board and opened nothing (2026-11-09).
    flagged = "-> OWED: " + line("r10-c", sha("4"), 1794262974) + "\n-> OWED: OWED x handoff-update refs/heads/handoff/r10-d " + sha("5")
    check("parse_board: the tick board's flagged `-> OWED: ` line is read", od.parse_board(flagged) == [("r10-c", sha("4"), 1794262974)])
    check("null: an unflagged board line is not owed", od.parse_board("   OWED: " + line("r10-e", sha("6"))) == [])
    check("override wins", od.resolve("r10-x", G, "", {"r10-x": {"group": "R10-UX-HEALTH", "title": "T"}}) == ("R10-UX-HEALTH", "T"))

    # order: hotfix > outside or critical > record > rest by default (owner
    # rulings tvofi 2026-11-07, triage P420, and 2026-11-08); the file orders
    # what it lists within a class
    items = [("r10-inst", "R10-INST", 1), ("r10-cp", "R10-CP", 2), ("triage-s6-batch1", "R10-TRIAGE-S6", 3),
             ("r10-hotfix-x", "R10-HOTFIX-X", 4)]
    names = lambda pr: [t for t, _, _ in od.order(items, pr, {"r10-cp"})]
    check("default order", names([]) == ["r10-hotfix-x", "r10-cp", "triage-s6-batch1", "r10-inst"])
    check("omitted critical before listed instrument", names(["r10-inst"]).index("r10-cp") < names(["r10-inst"]).index("r10-inst"))
    check("null: omitted non-critical after listed higher class",
          names(["r10-hotfix-x", "r10-cp"]) == ["r10-hotfix-x", "r10-cp", "triage-s6-batch1", "r10-inst"])
    check("omitted higher classes slot before a listed instrument", names(["r10-inst"]) == ["r10-hotfix-x", "r10-cp", "triage-s6-batch1", "r10-inst"])
    check("file order among listed (outside the fence)", names(["r10-inst", "triage-s6-batch1"]).index("r10-inst") < names(["r10-inst", "triage-s6-batch1"]).index("triage-s6-batch1"))
    check("the fence beats the file: a listed instrument is behind an omitted hotfix", names(["r10-inst", "r10-hotfix-x"]).index("r10-hotfix-x") < names(["r10-inst", "r10-hotfix-x"]).index("r10-inst"))
    check("omitted record sorts after listed hotfix", names(["r10-hotfix-x"]).index("triage-s6-batch1") > names(["r10-hotfix-x"]).index("r10-hotfix-x"))
    same = [("r10-a", "R10-A", 1), ("r10-b", "R10-B", 2)]
    check("an omitted topic slots after a listed one of its own class, never before it",
          [t for t, _, _ in od.order(same, ["r10-b"], set())] == ["r10-b", "r10-a"])
    check("critical listed last is still ahead of every non-fenced topic", names(["r10-inst", "triage-s6-batch1", "r10-cp"])[:2] == ["r10-hotfix-x", "r10-cp"])
    check("the fence puts a hotfix first, then outside and critical in the file's order",
          [t for t, _, _ in od.order(items + [("r10-out", "R10-OUT", 5)], ["r10-cp", "r10-out", "r10-hotfix-x", "r10-inst"], {"r10-cp"}, {"r10-out"})][:3]
          == ["r10-hotfix-x", "r10-cp", "r10-out"]
          and [t for t, _, _ in od.order(items + [("r10-out", "R10-OUT", 5)], ["r10-out", "r10-cp", "r10-inst"], {"r10-cp"}, {"r10-out"})][:3]
          == ["r10-hotfix-x", "r10-out", "r10-cp"])
    out_items = items + [("r10-out", "R10-OUT", 5)]
    old_out = items + [("r10-out", "R10-OUT", 1)]
    check("outside and critical share a class behind a hotfix: by default the older handoff first",
          [t for t, _, _ in od.order(out_items, [], {"r10-cp"}, {"r10-out"})]
          == ["r10-hotfix-x", "r10-cp", "r10-out", "triage-s6-batch1", "r10-inst"]
          and [t for t, _, _ in od.order(old_out, [], {"r10-cp"}, {"r10-out"})]
          == ["r10-hotfix-x", "r10-out", "r10-cp", "triage-s6-batch1", "r10-inst"])
    check("an outside topic and a critical one are one class; a hotfix one is a hotfix",
          od.default_class("r10-out", "R10-OUT", set(), {"r10-out"}) == 1
          == od.default_class("r10-cp", "R10-CP", {"r10-cp"}, set())
          and od.default_class("r10-hotfix-o", "R10-HOTFIX-O", set(), {"r10-hotfix-o"}) == 0)
    check("null: no outside set orders byte-identically to a call without the argument",
          od.order(out_items, ["r10-inst"], {"r10-cp"}, frozenset()) == od.order(out_items, ["r10-inst"], {"r10-cp"}))

    def world(lines, ros=None, **kw):
        sd = Path(tempfile.mkdtemp())
        ros = ros or roster("R10-CP", "R10-INST", "R10-OLD", "R10-ONMAIN", "R10-SAV-COMFORT", "R10-X", after={"R10-INST": ["R10-CP"]})
        return sd, Fake(ros, **kw)

    out = []
    def go(sd, w, board, now=NOW):
        out.clear()
        return od.run_pass(board, w, sd, now, out.append)

    heads = [("r10-inst", sha("1")), ("r10-cp", sha("2")), ("r10-onmain", sha("3")), ("r10-x", sha("4")), ("r10-old", sha("5"))]
    board = "\n".join(line(t, s) for t, s in heads)
    sd, w = world(board, heads=heads, landed={sha("3")})
    res = go(sd, w, board)
    check("cp before instrument, cap 2 holds", [t for t, _, _ in w.launched] == ["r10-cp", "r10-inst"])
    # Outside wiring (owner rulings tvofi 2026-11-07, triage P420, and
    # 2026-11-08): the roster's `source` field reaches the order.
    # R10-CP -> R10-INST is the critical path, so the outside group shares
    # their class and the tie-break (topic name) decides: R10-A-OUT is named
    # to sort first, so it opens; with no source field it is plain and waits.
    oros = roster("R10-CP", "R10-INST", "R10-A-OUT", after={"R10-INST": ["R10-CP"]})
    oros["groups"][2]["source"] = "outside"
    oheads = [("r10-inst", sha("1")), ("r10-cp", sha("2")), ("r10-a-out", sha("3"))]
    oboard = "\n".join(line(t, s) for t, s in oheads)
    osd, ow = world(oboard, ros=oros, heads=oheads)
    go(osd, ow, oboard)
    check("run_pass: an outside group opens in the critical path's class, cap 2",
          [t for t, _, _ in ow.launched] == ["r10-a-out", "r10-cp"])
    # A kind "bug" group is a hotfix by roster_lib.is_hotfix with no HOTFIX in its
    # name (#3304 round 2): it opens ahead of the outside group, as the plan and
    # dispatch_rank order it; with no kind it is the rest and the outside opens first.
    bros = roster("R10-OUT", "R10-BUGFIX")
    bros["groups"][0]["source"], bros["groups"][1]["kind"] = "outside", "bug"
    bheads = [("r10-out", sha("1")), ("r10-bugfix", sha("2"))]
    bboard = "\n".join(line(t, s) for t, s in bheads)
    bsd, bw = world(bboard, ros=bros, heads=bheads)
    (bsd / "open-cap.txt").write_text("1\n")
    go(bsd, bw, bboard)
    check("run_pass: a kind-bug group with no HOTFIX name opens ahead of an outside group, cap 1",
          [t for t, _, _ in bw.launched] == ["r10-bugfix"])
    bros["groups"][1].pop("kind")
    bsd, bw = world(bboard, ros=bros, heads=bheads)
    (bsd / "open-cap.txt").write_text("1\n")
    go(bsd, bw, bboard)
    check("run_pass null: the same group with no kind waits behind the outside group",
          [t for t, _, _ in bw.launched] == ["r10-out"])
    nros = roster("R10-CP", "R10-INST", "R10-A-OUT", after={"R10-INST": ["R10-CP"]})
    nsd, nw = world(oboard, ros=nros, heads=oheads)
    go(nsd, nw, oboard)
    check("run_pass null: with no source field the critical path opens first, as before",
          [t for t, _, _ in nw.launched] == ["r10-cp", "r10-inst"])
    check("on-main skipped", res["skipped"].get("r10-onmain") == "landed" and all(t != "r10-onmain" for t, _, _ in w.launched))
    check("cap skip logged", res["skipped"].get("r10-x") == "cap" or res["skipped"].get("r10-old") == "cap")
    (sd / "open-cap.txt").write_text("3\n")
    go(sd, w, board)
    check("cap re-read each pass (live runs counted from PIDs)", len(w.launched) == 3)
    sd, w = world("", heads=heads)
    go(sd, w, "")
    check("null: empty board starts nothing", w.launched == [])
    upd = f"OWED 2026-11-02T00:00:00Z handoff-update refs/heads/handoff/r10-cp {sha('2')}\nOWED x handoff-no-pr refs/heads/handoff-body/r10-cp {sha('2')}"
    sd, w = world(upd, heads=heads)
    go(sd, w, upd)
    check("null: handoff-update / body line ignored", w.launched == [])
    # OPENER-LIVE-TIP (P603): the board is rewritten once per relay pass, so a
    # line can name a handoff sha origin has since moved past. The candidate
    # checks re-run at origin's live tip; only an absent tip is `moved`.
    sd, w = world("", heads=[("r10-cp", sha("2"))])
    go(sd, w, line("r10-cp", sha("7")))
    check("live tip: a board line at A with origin's clean tip B opens at B",
          len(w.launched) == 1 and od._load(sd / "open-driver" / "runs.json", {}).get("r10-cp", {}).get("sha") == sha("2")
          and f"RETIP r10-cp {sha('7')[:8]} -> {sha('2')[:8]}" in out and not any(o.startswith("SKIP") for o in out))
    sd, w = world("", heads=[("r10-cp", sha("2"))], landed={sha("2")})
    go(sd, w, line("r10-cp", sha("7")))
    check("live tip: the checks run at B, so a landed B is skipped landed, never opened",
          w.launched == [] and out[-1] == f"SKIP r10-cp {sha('2')[:8]} landed")
    sd, w = world("", heads=[])
    go(sd, w, line("r10-cp", sha("7")))
    check("null: a line whose handoff ref is gone still prints SKIP moved",
          w.launched == [] and out == [f"SKIP r10-cp {sha('7')[:8]} moved"])
    for tp in ("triage-s9-batch4", "roster-carry-fold"):
        sd, w = world("", ros=roster("ROSTER-CARRY-FOLD", "R10-TRIAGE-S9"), heads=[(tp, sha("2"))])
        go(sd, w, line(tp, sha("2")))
        check(f"{tp} is batched, not opened", w.launched == [] and od.resolve(tp, {"ROSTER-CARRY-FOLD", "R10-TRIAGE-S9"}, "")[0])
    sd, w = world("", heads=[("r10-cp", sha("2"))])
    go(sd, w, line("r10-cp", sha("2")))
    check("null: a production topic is opened as before", len(w.launched) == 1)
    sd, w = world("", heads=[("r10-cp", sha("2"))], extra=["refs/heads/fix/r10-cp-pr"])
    go(sd, w, line("r10-cp", sha("2")))
    check("existing fix branch skipped", w.launched == [])
    sd, w = world("", heads=[("r10-cp", sha("2"))])
    w.t.pop("refs/heads/handoff-body/r10-cp")
    go(sd, w, line("r10-cp", sha("2")))
    check("missing body skipped", w.launched == [])
    sd, w = world("", heads=[("r10-zzz", sha("2"))])
    go(sd, w, line("r10-zzz", sha("2")))
    check("NEEDS-TITLE opens nothing", w.launched == [] and any(o.startswith("NEEDS-TITLE r10-zzz") for o in out))

    # every `handoff-no-pr` board topic is listed, once, each pass: SKIP, NEEDS-TITLE or START (the 2026-11-14
    # aside: r10-arch-docs-delta drew no line). One topic per branch of the pass, the cap arm included.
    lh = [("r10-cp", sha("1")), ("r10-inst", sha("2")), ("r10-onmain", sha("3")), ("r10-x", sha("4")), ("r10-zzz", sha("5")),
          ("triage-s9-batch4", sha("6")), ("r10-old", sha("7")), ("r10-sav-comfort", sha("8"))]
    lb = "\n".join(line(t, s_) for t, s_ in lh + [("r10-gone", sha("9"))])
    sd, w = world("", heads=lh, landed={sha("3")}, extra=["refs/heads/fix/r10-x"])
    w.t.pop("refs/heads/handoff-body/r10-old")
    (sd / "open-cap.txt").write_text("1\n")
    listed = lambda: sorted(o.split()[1] for o in out if o.split()[0] in ("SKIP", "NEEDS-TITLE", "START"))
    go(sd, w, lb)
    first = listed()
    go(sd, w, lb, NOW + 10)
    check("listing: each board topic draws exactly one SKIP, NEEDS-TITLE or START line, on the first pass and the next",
          first == listed() == sorted(t for t, _ in lh + [("r10-gone", sha("9"))]) and len(w.launched) == 1)

    # seen only on rc=0; a failure retries with backoff and prints OWED
    d = lambda sd: sd / "open-driver"
    h1 = [("r10-cp", sha("2"))]
    sd, w = world("", heads=h1)
    b = line("r10-cp", sha("2"))
    go(sd, w, b)
    (d(sd) / "t-r10-cp.rc").write_text("1\n")
    (d(sd) / "t-r10-cp.log").write_text("open_pr: REFUSE: the body lints red\n")
    go(sd, w, b, NOW + 10)
    check("failed open not marked seen", not (d(sd) / "seen.txt").exists() and len(w.launched) == 1)
    check("failed open prints OWED with reason", any(o.startswith("OWED") and "open-refused r10-cp" in o and "REFUSE" in o for o in out))
    check("backoff holds the retry", len(w.launched) == 1)
    go(sd, w, b, NOW + 10 + od.BACKOFF_S + 1)
    check("retry after backoff", len(w.launched) == 2)
    (d(sd) / "t-r10-cp.rc").write_text("1\n")
    go(sd, w, b, NOW + 5000)
    check("backoff schedule: 30 min, 60 min, 2 h cap", [od.backoff(1), od.backoff(2), od.backoff(3), od.backoff(7)] == [1800, 3600, 7200, 7200])
    check("backoff doubles", od.backoff(2) == 2 * od.backoff(1) and od.backoff(99) == od.BACKOFF_MAX_S)
    go(sd, w, b, NOW + 5000 + 3 * 3600)
    (d(sd) / "t-r10-cp.rc").write_text("0\n")
    go(sd, w, b, NOW + 5000 + 4 * 3600)
    check("rc=0 marks seen", f"r10-cp {sha('2')}" in (d(sd) / "seen.txt").read_text())
    k = len(w.launched)
    go(sd, w, b, NOW + 5000 + 5 * 3600)
    check("seen is not reopened", len(w.launched) == k and not any(o.startswith("OWED") for o in out))
    sd, w = world("", heads=h1)
    go(sd, w, b)
    w.dead.add(w.pid)
    (d(sd) / "t-r10-cp.rc").unlink(missing_ok=True)
    go(sd, w, b, NOW + 1)
    check("a killed run (no result, no PID) is a failure", any("open-refused r10-cp" in o and "rc=-1" in o for o in out))

    # three failed runs end the retries: STUCK once per pass, nothing relaunches; a new sha starts fresh
    sd, w = world("", heads=h1)
    go(sd, w, b)
    (d(sd) / "t-r10-cp.log").write_text("open_pr: REFUSE: the body lints red\n")
    (d(sd) / "t-r10-cp.rc").write_text("1\n")
    go(sd, w, b, NOW + 10)
    go(sd, w, b, NOW + 2000)
    (d(sd) / "t-r10-cp.rc").write_text("1\n")
    go(sd, w, b, NOW + 2100)
    check("two failures print OWED, not STUCK", any(o.startswith("OWED") for o in out) and not any(o.startswith("STUCK") for o in out))
    go(sd, w, b, NOW + 6000)
    (d(sd) / "t-r10-cp.rc").write_text("1\n")
    go(sd, w, b, NOW + 6100)
    check("third failure prints exactly one STUCK line, no OWED",
          [o for o in out if o.startswith(("STUCK", "OWED"))] == [f"STUCK r10-cp {sha('2')[:8]} rc=1 open_pr: REFUSE: the body lints red"])
    go(sd, w, b, NOW + 100 * 3600)
    check("stuck: no relaunch after a long time, STUCK again",
          len(w.launched) == 3 and sum(o.startswith("STUCK r10-cp ") for o in out) == 1 and not any(o.startswith("OWED") for o in out))
    w.t["refs/heads/handoff/r10-cp"] = sha("7")
    go(sd, w, line("r10-cp", sha("7")), NOW + 100 * 3600 + 10)
    check("a new sha for a stuck topic launches again", len(w.launched) == 4)

    # STALE CHECKOUT is the environment's refusal (P627): it records the tools checkout HEAD it was refused
    # at, sets no backoff, counts toward no stuck, and is retried on the first pass after that HEAD changes.
    def stale_line(w, name="open_pr"):
        return (f"{name}: REFUSE: STALE CHECKOUT {w.head[:12]} behind origin/main {sha('9')[:12]} by 1 commit(s) "
                "touching tools/audit/seat tools/pr: update the checkout holding /x, or set HPO_ALLOW_STALE_TOOLS=1\n")

    def refuse(sd, text, topic="r10-cp"):
        (d(sd) / f"t-{topic}.log").write_text(text)
        (d(sd) / f"t-{topic}.rc").write_text("1\n")

    key = f"r10-cp {sha('2')}"
    sd, w = world("", heads=h1)
    go(sd, w, b)
    refuse(sd, stale_line(w))
    go(sd, w, b, NOW + 10)
    f = od._load(d(sd) / "fails.json", {}).get(key, {})
    check("stale (i): a STALE CHECKOUT result is no failure counted and sets no backoff, and records the refused HEAD",
          f.get("n") == 0 and f.get("next", 0) <= NOW + 10 and f.get("stale") == w.head[:12])
    check("stale (i): with the HEAD unchanged it is not retried, in the pass that reaps it or after any wait",
          len(w.launched) == 1 and f"SKIP r10-cp {sha('2')[:8]} stale-checkout" in out
          and not go(sd, w, b, NOW + 100 * 3600)["started"] and len(w.launched) == 1)
    check("stale (i): it prints OWED with the refusal, never STUCK",
          [o.split(" ", 2)[2] for o in out if o.startswith(("OWED", "STUCK"))]
          == [f"open-refused r10-cp {sha('2')[:8]} rc=1 {stale_line(w).strip()[:200]}"])
    w.head = sha("f")
    go(sd, w, b, NOW + 100 * 3600 + 1)
    check("stale (ii): after the HEAD changes it is retried on the next pass", len(w.launched) == 2)
    for i in range(od.MAX_TRIES + 2):  # refused again at each new HEAD: more environment refusals than MAX_TRIES
        refuse(sd, stale_line(w))
        go(sd, w, b, NOW + 101 * 3600 + 2 * i)
        w.head = sha("abcdef"[i])
        go(sd, w, b, NOW + 101 * 3600 + 2 * i + 1)
    check("stale (i): any number of STALE CHECKOUT results never reaches stuck: each new HEAD relaunches",
          len(w.launched) == 2 + od.MAX_TRIES + 2 and od._load(d(sd) / "fails.json", {})[key]["n"] == 0
          and not any(o.startswith("STUCK") for o in out))
    w.head = ""
    refuse(sd, stale_line(type("H", (), {"head": sha("f")})))
    go(sd, w, b, NOW + 102 * 3600)
    k = len(w.launched)
    go(sd, w, b, NOW + 102 * 3600 + 1)
    check("stale: an unreadable tools HEAD is not a changed one, so nothing relaunches", len(w.launched) == k)
    # (iii) null control: a merge conflict is the branch's rc 1 and keeps the backoff and the count
    sd, w = world("", heads=h1)
    go(sd, w, b)
    refuse(sd, "open_pr: REFUSE: merging origin/main conflicts in tools/x.py\n")
    go(sd, w, b, NOW + 10)
    f = od._load(d(sd) / "fails.json", {}).get(key, {})
    w.head = sha("f")
    check("stale (iii) null: a merge-conflict rc 1 backs off 1800 s and counts toward MAX_TRIES, whatever the HEAD does",
          f.get("n") == 1 and f.get("next") == NOW + 10 + 1800 and "stale" not in f
          and not go(sd, w, b, NOW + 10 + 1799)["started"] and go(sd, w, b, NOW + 10 + 1801)["started"] == ["r10-cp"])
    # a counted failure followed by the environment's refusal keeps its count and its backoff, extended by nothing
    refuse(sd, stale_line(w))
    go(sd, w, b, NOW + 4000)
    f2 = od._load(d(sd) / "fails.json", {}).get(key, {})
    check("stale: after a counted failure the count and its backoff stand unchanged",
          f2.get("n") == 1 and f2.get("next") == f.get("next") and f2.get("stale") == w.head[:12])
    # (v) the replay: three refusals at 13:34:54Z, the checkout rotated at 13:44:40Z, one pass a minute, cap 3
    t0 = 1_794_404_094.0  # 2026-11-11T13:34:54Z
    rot = t0 + 586  # 13:44:40Z
    h3 = [("r10-hotfix-gate-redispatch-loop", sha("1")), ("r10-cp", sha("2")), ("r10-inst", sha("3"))]
    b3 = "\n".join(line(t, s) for t, s in h3)
    sd, w = world("", ros=roster("R10-HOTFIX-GATE-REDISPATCH-LOOP", "R10-CP", "R10-INST"), heads=h3)
    (sd / "open-cap.txt").write_text("3\n")
    go(sd, w, b3, t0 - 60)
    for t, _ in h3:
        refuse(sd, stale_line(w), t)
    starts, now = [], t0
    while not starts and now < t0 + 7200:
        if now >= rot:
            w.head = sha("f")
        starts = go(sd, w, b3, now)["started"]
        now += 60
    check("stale (v) replay: the three 13:34:54Z refusals are all retried on the first pass after the 13:44:40Z HEAD change",
          sorted(starts) == sorted(t for t, _ in h3) and rot <= now - 60 < rot + 60 and len(w.launched) == 6)
    # the classifier over a generated spelling corpus: only pr_refuse's own line with a HEAD is the environment's
    corpus = [(f"{nm}: {lv}: {ph} {hd}{tl}", lv == "REFUSE" and ph == "STALE CHECKOUT" and hd in (sha("a")[:12], sha("a")) and bool(tl))
              for nm in ("open_pr", "update_pr", "pr") for lv in ("REFUSE", "NOTICE", "refuse", "Refuse")
              for ph in ("STALE CHECKOUT", "stale checkout", "STALE-CHECKOUT", "STALE  CHECKOUT")
              for hd in (sha("a")[:12], sha("a"), sha("a")[:7], "", "g" * 12) for tl in (" behind origin/main x by 1 commit(s)", "")]
    wrong = [text for text, env in corpus if (od.stale_head(text) is not None) != env]
    check(f"stale: the classifier agrees with pr_tools_fresh's line over {len(corpus)} generated spellings", len(corpus) == 480 and not wrong)
    check("stale: a quoted refusal inside another line, and a NOTICE under HPO_ALLOW_STALE_TOOLS, are the branch's",
          od.stale_head("open_pr: REFUSE: the body says `open_pr: REFUSE: STALE CHECKOUT " + sha("a")[:12] + " behind`") is None
          and od.stale_head("open_pr: NOTICE: STALE CHECKOUT " + sha("a")[:12] + " behind origin/main") is None
          and od.stale_head(stale_line(w).strip()) == w.head[:12])

    # the retry verb (OPENER-RETRY-VERB, P678): the cure once an environment failure is fixed, never a hand edit
    def backed_off():
        sd, w = world("", heads=h1)
        go(sd, w, b)
        refuse(sd, "open_pr: REFUSE: prepr step 3 failed\n")
        go(sd, w, b, NOW + 10)
        return sd, w

    sd, w = backed_off()
    check("retry (ii) null: without the verb the pass inside the backoff window skips the topic as backoff",
          go(sd, w, b, NOW + 600)["skipped"].get("r10-cp") == "backoff" and len(w.launched) == 1)
    sd, w = backed_off()
    said = []
    rc = od.retry(sd, "r10-cp", None, said.append)
    check("retry: prints the removed entry's n, next and why, and reads the file back without it",
          rc == 0 and said == [f"RETRY r10-cp {sha('2')[:8]} n=1 next={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW + 10 + 1800))} "
                               "why=open_pr: REFUSE: prepr step 3 failed"]
          and od._load(d(sd) / "fails.json", None) == {})
    check("retry (i): the next pass starts the topic inside its backoff window",
          go(sd, w, b, NOW + 600)["started"] == ["r10-cp"] and len(w.launched) == 2)
    sd, w = backed_off()
    before = (d(sd) / "fails.json").read_bytes()
    said = []
    check("retry (iv): a topic with no entry is refused and fails.json is byte-identical",
          od.retry(sd, "r10-inst", None, said.append) == 1 and len(said) == 1 and said[0].startswith("open_driver retry: REFUSE: ")
          and (d(sd) / "fails.json").read_bytes() == before
          and od.retry(sd, "r10-cp", sha("7"), said.append) == 1 and (d(sd) / "fails.json").read_bytes() == before)
    two = {f"r10-cp {sha('2')}": {"n": 3, "next": NOW, "rc": 1, "why": "a"}, f"r10-cp {sha('7')}": {"n": 1, "next": NOW, "rc": 1, "why": "b"},
           f"r10-cp-2 {sha('2')}": {"n": 1, "next": NOW, "rc": 1, "why": "c"}}
    (d(sd) / "fails.json").write_text(od.json.dumps(two))
    check("retry: a sha names one (topic, sha) entry; no sha removes every entry of that topic and no namesake's",
          od.retry(sd, "r10-cp", sha("7"), said.append) == 0 and sorted(od._load(d(sd) / "fails.json", {})) == [f"r10-cp {sha('2')}", f"r10-cp-2 {sha('2')}"]
          and od.retry(sd, "r10-cp", None, said.append) == 0 and sorted(od._load(d(sd) / "fails.json", {})) == [f"r10-cp-2 {sha('2')}"])
    (d(sd) / "fails.json").write_text(od.json.dumps(two))
    said, real, reads = [], od._load, []
    # a pass that loaded before the verb wrote and rewrote after it: the read-back holds the entry again
    od._load = lambda path, default: (reads.append(path), real(path, default) if len(reads) == 1 else two)[1]
    try:
        rc = od.retry(sd, "r10-cp-2", None, said.append)
    finally:
        od._load = real
    check("retry: a file that does not read back as what was written is refused (rc 1), naming the read-back",
          rc == 1 and len(said) == 2 and said[0].startswith("RETRY r10-cp-2 ")
          and said[1].startswith("open_driver retry: REFUSE: ") and "read back" in said[1])
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "HPO_STATE_DIR": tmp}
        cli = lambda *a: subprocess.run([sys.executable, "-I", od.__file__, *a], capture_output=True, text=True, env=env)
        (Path(tmp) / "open-driver").mkdir()
        (Path(tmp) / "open-driver" / "fails.json").write_text(od.json.dumps(two))
        r1, r2, r3 = cli("retry", "r10-cp-2"), cli("retry", "r10-cp-2"), cli("retry")
        check("retry: the verb from the command line removes the entry (rc 0), refuses it gone (rc 1) and refuses no topic (rc 2)",
              (r1.returncode, r2.returncode, r3.returncode) == (0, 1, 2) and r1.stdout.startswith(f"RETRY r10-cp-2 {sha('2')[:8]} n=1 ")
              and "r10-cp-2" not in (Path(tmp) / "open-driver" / "fails.json").read_text())

    # a topic named like the driver's own log must not overwrite it; a plain one still works
    check("stem: a/b != a%2Fb", od.stem("a/b") != od.stem("a%2Fb"))
    with tempfile.TemporaryDirectory() as tmp:
        sd = Path(tmp) / "sd"
        (sd / "open-driver").mkdir(parents=True)
        (sd / "open-driver" / "open-driver.log").write_text("driver\n")
        wl = od.World(tmp, sd)
        wl.opener = Path(tmp) / "o.sh"
        wl.opener.write_text("echo topic-ran\n")
        for topic in ("open-driver", "r10-plain"):
            rcf = sd / "open-driver" / f"t-{od.stem(topic)}.rc"
            wl.launch(topic, sha("1"), "T", "G")
            for _ in range(100):
                if rcf.exists() and rcf.read_text().strip():
                    break
                time.sleep(0.1)
            check(f"topic {topic!r} launches into its own t- files", rd(sd / "open-driver" / f"t-{od.stem(topic)}.log") == "topic-ran\n")
        check("open-driver.log not overwritten by topic 'open-driver'", rd(sd / "open-driver" / "open-driver.log") == "driver\n")

    # a second pass with the first run still alive must not launch again
    sd, w = world("", heads=h1)
    go(sd, w, b)
    go(sd, w, b, NOW + 10)
    check("live run: one launch over two passes", len(w.launched) == 1)
    check("live run: SKIP ... live logged", any(o == f"SKIP r10-cp {sha('2')[:8]} live" for o in out))

    # STARVED
    sd, w = world("", heads=[("r10-zzz", sha("2"))])
    go(sd, w, line("r10-zzz", sha("2"), NOW - 2 * 3600 - 600))
    check("STARVED at 2 h 10 min", any(o.startswith("STARVED r10-zzz 22222222 2.2h") for o in out))
    go(sd, w, line("r10-zzz", sha("2"), NOW - 2 * 3600 + 600))
    check("null: no STARVED at 1 h 50 min", not any(o.startswith("STARVED") for o in out))

    # the git layer, in a throwaway origin
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
    from throwaway_git import throwaway_git_clone, throwaway_git_init
    with tempfile.TemporaryDirectory() as tmp:
        def g(*a, cwd=tmp + "/c"):
            return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
        throwaway_git_init(tmp + "/o", "-q", "--bare", "-b", "main")
        throwaway_git_clone(tmp + "/o", tmp + "/c", "-q")
        Path(tmp, "c/f").write_text("1")
        g("add", "f"); g("commit", "-qm", "one"); g("fetch", "-q", tmp + "/c", "HEAD:refs/heads/main", cwd=tmp + "/o")
        on_main = g("rev-parse", "HEAD")
        g("checkout", "-q", "-b", "side")
        Path(tmp, "c/f").write_text("2")
        g("commit", "-qam", "two"); side = g("rev-parse", "HEAD")
        g("fetch", "-q", tmp + "/c", "side:refs/heads/handoff/side", "side:refs/heads/handoff-body/side", cwd=tmp + "/o")
        wd = od.World(tmp + "/c", Path(tmp))
        t = wd.tips()
        check("git layer: tips read handoff and main", t.get("refs/heads/handoff/side") == side and t.get("refs/heads/main") == on_main)
        check("git layer: ledger landed true for a main tip", wd.landed(on_main, on_main))
        check("git layer: ledger landed false for an unlanded tip", not wd.landed(on_main, side))
        wd.opener = Path(tmp, "c", "open_pr.sh")
        check("git layer: tools_head is the HEAD of the checkout holding the opener", wd.tools_head() == side)
        wd.opener = Path(tmp, "open_pr.sh")
        check("null: tools_head of a directory in no checkout is empty, never a guess", wd.tools_head() == "")
    # World.launch with hostile topics and a state directory holding a space
    with tempfile.TemporaryDirectory() as tmp:
        sd = Path(tmp) / "state dir"
        (sd / "open-driver").mkdir(parents=True)
        scratch = Path(tmp) / "scratch"
        scratch.mkdir()
        opener = Path(tmp) / "open_pr.sh"
        opener.write_text('printf "%s|" "$@" > "$HPO_ARGS_OUT"; echo ran\n')
        wl = od.World(str(scratch), sd)
        wl.opener = opener
        marker = scratch / "INJECTED"
        for topic in ("r10-a;touch INJECTED", "z$(touch${IFS}INJECTED)", "a/b", "r10-plain"):
            argsf = Path(tmp) / "args.txt"
            argsf.unlink(missing_ok=True)
            os.environ["HPO_ARGS_OUT"] = str(argsf)
            wl.launch(topic, sha("1"), "T x", "G")
            rcf = sd / "open-driver" / f"t-{od.stem(topic)}.rc"
            for _ in range(100):
                if rcf.exists() and rcf.read_text().strip():
                    break
                time.sleep(0.1)
            check(f"launch {topic!r}: rc file written with 0", rcf.exists() and rcf.read_text().strip() == "0")
            check(f"launch {topic!r}: topic arrives as one argument", argsf.exists() and argsf.read_text() == f"{topic}|{sha('1')}|T x|G|")
            check(f"launch {topic!r}: log written", rd(sd / "open-driver" / f"t-{od.stem(topic)}.log") == "ran\n")
        check("launch: no topic executed as shell code", not marker.exists() and not list(Path(tmp).rglob("INJECTED")))

    # a slash topic end to end: run_pass launches it through the real World.launch, a later pass reaps its result
    class Slash(Fake):
        def __init__(self, real, *a, **kw):
            super().__init__(*a, **kw)
            self.real = real

        def launch(self, topic, s, title, group):
            super().launch(topic, s, title, group)
            return self.real.launch(topic, s, title, group)

        def alive(self, pid):
            return self.real.alive(pid)

    with tempfile.TemporaryDirectory() as tmp:
        sd = Path(tmp) / "state dir"
        wr = od.World(tmp, sd)
        wr.opener = Path(tmp) / "open_pr.sh"
        wr.opener.write_text("echo opened\n")
        ws = Slash(wr, roster("A/B"), heads=[("a/b", sha("4"))])
        b = line("a/b", sha("4"))
        go(sd, ws, b)
        rcf = sd / "open-driver" / f"t-{od.stem('a/b')}.rc"
        for _ in range(100):
            if rcf.exists() and rcf.read_text().strip():
                break
            time.sleep(0.1)
        go(sd, ws, b, NOW + 10)
        check("slash topic reaped: RESULT a/b rc=0 with its log's reason", f"RESULT a/b {sha('4')[:8]} rc=0 opened" in out)
        go(sd, ws, b, NOW + 20)
        check("slash topic reaped: seen, not reopened", out == [f"SKIP a/b {sha('4')[:8]} seen"] and len(ws.launched) == 1)

    # World.body_head against a throwaway origin: the first three lines only
    with tempfile.TemporaryDirectory() as tmp:
        def g(*a, cwd=tmp + "/c"):
            return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
        throwaway_git_init(tmp + "/o", "-q", "--bare", "-b", "main")
        throwaway_git_clone(tmp + "/o", tmp + "/c", "-q")
        Path(tmp, "c/BODY.md").write_text("L1\nL2\nL3\nL4\nL5\n")
        g("add", "BODY.md"); g("commit", "-qm", "body")
        g("fetch", "-q", tmp + "/c", "HEAD:refs/heads/handoff-body/bod", cwd=tmp + "/o")
        wb = od.World(tmp + "/c", Path(tmp))
        check("body_head: first three lines of BODY.md", wb.body_head("bod") == "L1\nL2\nL3")
        check("null: body_head of a missing body is empty", wb.body_head("nope") == "")
    print(f"open_driver self-test: {n} checks, {bad} failed")
    return 1 if bad else 0

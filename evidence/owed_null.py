"""Reviewer's own harness for PR 3200 owed_levels: null controls and one-bucket-per-PR."""
import sys, json, os, tempfile, datetime
from pathlib import Path
WT = Path(sys.argv[1]); sys.path.insert(0, str(WT / "tools/audit/seat"))
import importlib.util
spec = importlib.util.spec_from_file_location("ot", WT / "tools/audit/seat/orchestrator_tick.py")
ot = importlib.util.module_from_spec(spec); spec.loader.exec_module(ot)
NOW = ot.NOW
h = lambda n: f"{n:040x}"
tmp = Path(tempfile.mkdtemp())
def mk(prs, queue=None, dispatched=(), readback=None, red=None, files=None, roster=None, refs=(), cts=None, vat=None, train=None):
    q = tmp / f"q{len(list(tmp.iterdir()))}.json"; q.write_text(json.dumps([{"pr": n, "verdict": v} for n, v in (queue or {}).items()]))
    bus = tempfile.mkdtemp(); Path(bus, "dispatched").write_text("".join(f"{n} {hd}\n" for n, hd in dispatched))
    rf = None
    if roster is not None:
        rf = str(tmp / f"r{len(list(tmp.iterdir()))}.json"); Path(rf).write_text(json.dumps(roster))
    tl = None
    if train is not None:
        tl = str(tmp / f"t{len(list(tmp.iterdir()))}.log"); Path(tl).write_text(train)
    git = ot.Stub()
    for ref, sha in refs:
        git.on(("ls-remote", "origin", ref.rsplit("/", 1)[0] + "/*"), out=f"{sha}\trefs/heads/{ref}\n")
    git.on(("ls-remote",), out="")
    for sha, m in (cts or {}).items():
        git.on(("log", "-1", "--format=%ct", sha), out=str(int((NOW - datetime.timedelta(minutes=m)).timestamp())))
    git.on(("fetch",), out=""); git.on(("merge-base", "--is-ancestor"), rc=0)
    gh = ot.Stub()  # every gh call fails loudly and is recorded
    t = ot.Tick("o/r", str(WT), queue=str(q), bus_state=bus, roster_file=rf, train_log=tl, now=NOW, gh=gh, git=git,
                proc=lambda *a: [], bus=None)
    t._readback = readback if readback is not None else {str(p["number"]): [] for p in prs}
    t._verdict_at = vat or {}
    t._red = red or {}; t._files = files or {}
    t.owed_levels("PRS", prs)
    txt = [x["text"] for x in t.sections.get("PRS", [])]
    return [x for x in txt if x.startswith("OWED")], [x for x in txt if x.startswith("buckets:")], gh.calls, txt
P = lambda n, ms="CLEAN", br=None: ot.pr_obj(n, h(n), ms=ms, branch=br)
res = []
def chk(name, ok, extra=""):
    res.append(ok); print(f"RESULT {'ok  ' if ok else 'FAIL'} {name} {extra}")
# N1 train: queued at head, DIRTY and red -> no OWED, bucket train
o, b, calls, _ = mk([P(90, "DIRTY")], queue={90: h(90)}, red={90: ["gate"]}, readback={"90": [f"Fix review: merge {h(90)}"]})
chk("null train (DIRTY+red, queued at head) prints no OWED", o == [] and b == ["buckets: train 1"], f"{o} {b}")
# N2 verdict-pending: dispatched at head, DIRTY + red -> none
o, b, calls, _ = mk([P(91, "DIRTY")], dispatched=[(91, h(91))], red={91: ["gate"]})
chk("null verdict-pending (DIRTY+red, dispatched at head) prints no OWED", o == [] and b == ["buckets: verdict-pending 1"], f"{o} {b}")
# N3 waiting-on by file overlap: lower open PR shares a file
o, b, calls, _ = mk([P(92), P(93, "DIRTY")], red={93: ["gate"]}, files={92: ["x.py"], 93: ["x.py"]})
chk("null waiting-on file overlap (higher PR DIRTY+red) prints no OWED", o == [] and "waiting-on 1" in b[0], f"{o} {b}")
# N4 waiting-on by roster after-edge
roster = {"groups": [{"group": "G-A", "status": "open"}, {"group": "G-B", "after": ["G-A"], "status": "open"}]}
o, b, calls, _ = mk([P(94, br="fix/g-a"), P(95, "DIRTY", br="fix/g-b")], red={95: ["gate"]}, roster=roster)
chk("null waiting-on after-edge prints no OWED for #95", not any("#95" in x for x in o) and "waiting-on 1" in b[0], f"{o} {b}")
# P1 positive controls: same shapes, not in train / pending / waiting -> OWED
o, b, calls, _ = mk([P(96, "DIRTY")])
chk("positive: DIRTY alone owes", len(o) == 1 and o[0].startswith(f"OWED dirty #96 {h(96)[:12]}"), f"{o}")
o, b, calls, _ = mk([P(97)], red={97: ["gate"]})
chk("positive: red with no seat owes red-unowned", len(o) == 1 and "red-unowned #97" in o[0], f"{o}")
# queue verdict at an older head that is NOT an ancestor -> not train
# exactly-one-bucket over a mixed board of 8
prs = [P(90, "DIRTY"), P(91, "DIRTY"), P(92), P(93, "DIRTY"), P(96, "DIRTY"), P(97), P(98), P(99, br="record/autofix")]
o, b, calls, txt = mk(prs, queue={90: h(90)}, dispatched=[(91, h(91))], red={93: ["gate"], 97: ["gate"]},
                      files={92: ["x.py"], 93: ["x.py"]},
                      readback={**{str(p["number"]): [] for p in prs}, "98": [f"Fix review: merge {h(98)}"]})
tot = sum(int(x.rsplit(" ", 1)[1]) for x in b[0][9:].split(", "))
chk("mixed board: 7 non-record PRs, counts sum to 7, OWED only #96 #97", tot == 7 and sorted(x.split()[2] for x in o) == ["#96", "#97"], f"{b} {o}")
chk("no GitHub call made by owed_levels on the mixed board", calls == [], f"{calls[:3]}")
chk("record branch PR in no bucket and no OWED", not any("#99" in x for x in o))
# stale queue verdict: queue verdict is old head and not an ancestor -> not train
q = mk.__defaults__
print(f"RESULT summary {sum(res)}/{len(res)} ok")
sys.exit(0 if all(res) else 1)

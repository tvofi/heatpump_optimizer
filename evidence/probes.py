import sys, json, tempfile
from pathlib import Path
sys.path.insert(0, "tools/audit/seat")
import beat_jobs as bj, beat_jobs_selftest as T
root = Path(tempfile.mkdtemp())
def ctx(name, answers, now=1.8e9):
    s = root / name; (s / "beatd").mkdir(parents=True)
    (s / "sweep-overlay.json").write_text(json.dumps({"repo": "o/r"}))
    f = T.Fake(answers); return bj.Ctx(s, root, run=f, now=now), f
ran = []
def rq(argv):
    op = Path(argv[argv.index("--queue") + 1]).read_text().strip(); ran.append(op)
    Path(argv[argv.index("--report") + 1]).write_text(f"roster: {op} pushed 0123\n"); return 0, "", ""
# P1: partial (unterminated) last line during an orchestrator append
c, f = ctx("p1", {"roster_queue.py": rq})
q = c.state / "roster-drain.queue"
q.write_text("append-carry G2 note text that is lo")      # append caught mid-write
bj.roster_drain(c)
q.write_text("append-carry G2 note text that is long\n")  # the append completes
bj.roster_drain(c)
print("P1 partial-line ops run:", ran)
# P2: orchestrator truncates the drained queue, later re-queues an identical op
ran.clear(); c, f = ctx("p2", {"roster_queue.py": rq})
q = c.state / "roster-drain.queue"; q.write_text("set-stage G1 done\n"); bj.roster_drain(c)
q.write_text(""); bj.roster_drain(c)
q.write_text("set-stage G1 done\n"); bj.roster_drain(c)
print("P2 after truncate+requeue, runs:", ran)
# P3: head A->B->A->B
hv = {"v": ""}
c, f = ctx("p3", {"gh": lambda a: (0, hv["v"], "")})
for h in "abab":
    hv["v"] = f"12 {h*40}\n"; bj.head_watch(c); c.now += 120
print("P3 events:", bj.read(c.digest / "events.txt").splitlines())
# P4: board present but with no provenance line, then board back at same pass
c, f = ctx("p4", {})
b = T.board("2026-11-01T09:00:00+00:00", "MERGE-READY: #9 9a8b7c6d"); c.board.write_text(b); bj.tick_digest(c)
c.board.write_text(""); bj.tick_digest(c); d1 = bj.read(c.digest/"digest.txt")
c.board.write_text(b); bj.tick_digest(c); d2 = bj.read(c.digest/"digest.txt")
print("P4 empty board ->", repr(d1), "| same board back ->", repr(d2))

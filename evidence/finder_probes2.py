"""Round-2 reviewer probes on beat_jobs.py at the head (own instrument)."""
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, "tools/audit/seat")
import beat_jobs as bj, beat_jobs_selftest as T
root = Path(tempfile.mkdtemp())
def fresh(name, answers=None, now=1_800_000_000.0):
    s = root / name; (s / "beatd").mkdir(parents=True)
    (s / "sweep-overlay.json").write_text(json.dumps({"repo": "o/r", "seat_ledger": str(s/"l")}))
    f = T.Fake(answers); return bj.Ctx(s, root, run=f, now=now), f
# Q1: NOT REVIEWABLE on a single board (gap 2: transient between open_pr's two pushes)
c, _ = fresh("q1")
c.board.write_text(T.board("2026-11-01T09:00:00+00:00", "#3200: NOT REVIEWABLE body lacks ## Head"))
bj.tick_digest(c)
print("Q1 NOT REVIEWABLE first board digest:", repr(bj.read(c.digest / "digest.txt")))
# Q2: a null pass after a run of lines that only removes lines: new.txt left stale?
c, _ = fresh("q2")
c.board.write_text(T.board("2026-11-01T09:00:00+00:00", "MERGE-READY: #9 9a8b7c6d"))
bj.tick_digest(c)
c.board.write_text(T.board("2026-11-01T09:04:00+00:00"))
bj.tick_digest(c)
print("Q2 after the line cleared: digest", repr(bj.read(c.digest/"digest.txt")), "new.txt", repr(bj.read(c.digest/"new.txt")), "gone.txt", repr(bj.read(c.digest/"gone.txt")))
# Q3: released hold - which op reaches roster_queue
ops = []
def rq(argv):
    q = argv[argv.index("--queue") + 1]; ops.append(Path(q).read_text().strip())
    Path(argv[argv.index("--report") + 1]).write_text(f"roster: {ops[-1]} G1 pushed abc\n"); return (0, "", "")
c, f = fresh("q3", {"roster_queue.py": rq, "git": (0, "", "")})
(c.state / "roster-drain.queue").write_text("hold dev/x.md set-stage G1 done\n")
bj.roster_drain(c)
print("Q3 op handed to roster_queue on release:", ops)

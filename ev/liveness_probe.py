"""Reviewer's own probe (not the finder's): does settle still recover a lagging-listing mutual deferral
of two gates that the sweep itself re-ran together?  argv[1]: a tools/ci dir holding sweep.py + sweep_selftest.py."""
import sys; sys.path.insert(0, sys.argv[1])
import sweep_selftest as t
BOT = "github-actions[bot]"
runs = [t.run(1, "1", started="3", units=["2"]), t.run(2, "1", started="3", units=["2"]),
        t.run(3, "1", g="success", started="1", units=["5"])]   # run 3: a real source finishing at 5, after gates 1,2 started
for r in runs: r["triggering_actor"] = {"login": "tvofi"}
w = t.World(runs, 3); w.sweep(); a = list(w.posts)
print("step a (late real source):", a)
for rid in (1, 2):   # both re-run together by the bot; both judge 6..7, overlapping; a lagging listing leaves both red
    r = w.runs[rid]; r["run_attempt"] = 2; r["triggering_actor"] = {"login": BOT}
    r["gate"].update(started_at="6", completed_at="7", conclusion="failure")
w.posts = []; w.v_id = 2; w.sweep(); b = list(w.posts)
print("step b (bot pair, both red, mutual deferral):", b)
if b:
    rid = 1 if any("/jobs/10/" in p for p in b) else 2
    r = w.runs[rid]; r["run_attempt"] = 3; r["gate"].update(started_at="8", completed_at="9", conclusion="success")
    w.posts = []; w.v_id = rid; w.sweep(); print("step c (lower re-judged alone, green):", w.posts)
print("RESULT liveness reruns_after_pair=%d stuck_red=%s" % (len(b), "yes" if not b else "no"))

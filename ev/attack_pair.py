"""Reviewer's own probe (not the finder's harness): a bot re-run pair in which the lower decided green
and the higher deferred to it (busy tie-break) and ended red, no source finishing after either start."""
import sys
sys.path.insert(0, sys.argv[1])
import sweep, sweep_selftest as t
BOT = "github-actions[bot]"
for v in (1, 2):
    w = t.World([t.run(1, "10", attempt=2, g="success", started="70", units=["40"]),
                 t.run(2, "11", attempt=2, g="failure", started="72", units=["44"])], v)
    w.runs[1]["gate"]["completed_at"], w.runs[2]["gate"]["completed_at"] = "80", "73"
    for r in w.runs.values():
        r["triggering_actor"] = {"login": BOT}
    rc, out = w.sweep()
    print(f"RESULT pair-lower-green swept_from={v} posts={w.posts}")
    print("   ", out.replace("\n", "\n    "))

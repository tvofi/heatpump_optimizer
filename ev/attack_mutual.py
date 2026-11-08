"""Reviewer's own probe: a bot re-run pair whose gates BOTH deferred to each other again (lagging listing),
both red, no source finishing after either start."""
import sys
sys.path.insert(0, sys.argv[1])
import sweep_selftest as t
for v in (1, 2):
    w = t.World([t.run(1, "1", attempt=2, started="70", units=["40"]), t.run(2, "1", attempt=2, started="70", units=["40"])], v)
    for r in w.runs.values():
        r["gate"]["completed_at"], r["triggering_actor"] = "71", {"login": "github-actions[bot]"}
    rc, out = w.sweep()
    print(f"RESULT mutual-defer-bot-pair swept_from={v} posts={w.posts}")

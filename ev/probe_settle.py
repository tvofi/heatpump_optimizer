"""Reviewer probe (own instrument): a higher-id gate that deferred to a LOWER run whose listing lagged
(busy()'s tie-break, gate self-test 'busy-defer: the higher deferring edit gate defers at once to the
lower whose listing lags'), where the lower's gate is green but does not cover the newest event
(the higher run was created after the lower's gate started). Stamps compare as strings (2-digit)."""
import sys; sys.path.insert(0, ".")
from sweep_selftest import World, run
def scene(v):
    lo = run(1, "10", started="50", units=["40"])           # lower: sources done 40, gate 50-60 green
    lo["gate"].update(conclusion="success", completed_at="60")
    hi = run(2, "52", started="55", units=["53"])           # higher: created 52 (> lo gate start 50), gate 55-56 red deferral
    hi["gate"]["completed_at"] = "56"
    w = World([lo, hi], v)
    rc, out = w.sweep()
    return w.posts, out
for v in (1, 2):
    posts, out = scene(v)
    print(f"swept from run {v}: posts={posts} out={out.splitlines()[-1]!r}")
# null control: the same, but the higher run created BEFORE the lower's gate started -> green branch re-runs it
lo = run(1, "10", started="50", units=["40"]); lo["gate"].update(conclusion="success", completed_at="60")
hi = run(2, "45", started="55", units=["53"]); hi["gate"]["completed_at"] = "56"
w = World([lo, hi], 1); w.sweep(); print(f"null (hi created before lo gate start), swept from run 1: posts={w.posts}")

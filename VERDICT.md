Fix review: merge fa851d7ea2768c25a89a4a9820864d4a1b5fc458

head: fa851d7ea2768c25a89a4a9820864d4a1b5fc458 (re-dispatched head; the closures-autofix bot's record-only commit on 170ac5987)
bus-nonce: 17476a6b89ded526e1b933f4aebf3693

Round 3, re-issued at the moved head. The prior verdict of this round
(blocked 170ac5987 head-moved) stands in the ref's history; this verdict
re-measures the delta and merges. The move is one bot commit,
"ci: re-record closures" (github-actions[bot]), whose entire diff is
tests/closures.json +3/-2: one INERT-list line added and two re-timings.
No production file changed.

## What the move was, verified

git diff 170ac5987..fa851d7e --stat: tests/closures.json only, 3 insertions
2 deletions. The added line is, verbatim:

    "dev/audit/rounds/round9/prestudy/boost_drift_refit.py",

inside the INERT list (tests/closures.json line 3661 at fa851d7ea) -- so the
bot's re-record really does cover the file whose under-approximated INERT
reads reddened the 170ac5987 run. The other two changed lines are the
re-timed "seconds" for tests/config_flow_steps.py (38.0 -> 15.2) and
tests/features.py (730.5 -> 288.5). That red was inherited from main's #2109
(b24adb766 landed boost_drift_refit.py), not authored by this branch, and the
autofix lane repaired it exactly as ci-autofix.md says it does.

## Re-taken at fa851d7e by this reviewer (own runs)

- Arch-score gate, the check's own command, base 23d354970 -> head
  fa851d7e:
      Architecture score: dS +0.0000 NULL
      PASS: dS +0.0000 NULL, no gate metric rose
- footprint.measure at fa851d7e: coord_footprint 2586, no _ending_streak
  entry in charged.
- Control: PYTHONPATH=tests/hastub python3 tests/debug_collect.py at
  fa851d7e prints ALL 70 DEBUG COLLECT CHECKS PASSED, rc 0.
- Revert arm at fa851d7e: debugger.py checked out from 23d354970, the same
  command exits 1 with KeyError: 'row_gaps_h'; restored, tree clean.
- CI at fa851d7e (check-runs API, not a listing): arch-score success,
  typing success, fast (3.14) success. The PR's head is fa851d7e.

## Carried from 170ac5987, where this reviewer measured them (own runs)

The bot commit cannot move any of these -- it touches one JSON data file --
and each is restated with where it ran:
- Typing ruler, pinned pair (mypy 2.3.1, homeassistant-stubs 2026.9.3,
  verified against tests/typing_ruler.py --print-requirements first), run
  from this reviewer's worktree at 170ac5987: ALL 9 typing-ruler checks
  PASSED. CI's typing job at fa851d7e is success.
- Finder's harness (dev/audit/harnesses/r9_dbg2_selftest_price.py, bundle
  sha1 cb6e9e3357648afc41adcadaff218f135908cc3d from origin/handoff/r9-dbg-0)
  at both ends: five ok rows at 23d354970 and five ok rows at 170ac5987,
  inline=1 at both, bundle 588243 B -> 588446 B (+203 B), far under the cap.
- The two deleted killed_by rows are genuinely stale: 4e5181094's tree with
  only the accessor deleted (rows kept) gives completeness_problems = 2, both
  naming debugger.py:_ending_streak; at 1e60f1861 and 23d354970 the ledger
  reads candidate sites 5943, unpinned 4620, completeness problems 0 at both
  ends; grep finds no _ending_streak anywhere at the head.
- Claims and versions against the merge base 969c3a5c8: both claim files,
  VERSION, the manifest and RELEASE_NOTES.md byte-identical; authored
  three-dot diff is the four named files. merge-tree clean.
- Branch-authored reds (pr-contract, arch-score, typing at c901f8f34 and
  4e5181094) are all named and answered in the body's ## Red checks; the
  other red SHAs in the range are main's own commits.

The prior verdict's one open item -- the closures red at 170ac5987 -- is
answered at this head by the bot commit itself (the INERT-list line above)
and CI's closures conclusion at fa851d7e, recorded in evidence/.

Evidence: evidence/ (pr-body.md, typing-head.txt, revert-arm.txt,
revert-arm-newhead.txt, oracle-head.txt, oracle-base.txt, closures-ci.log,
closures-newhead.txt, gate-and-ledger.txt, gate-newhead.txt, mergetree.txt).

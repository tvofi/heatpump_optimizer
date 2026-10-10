# Fix review evidence — PR #2124

Measured head: 9eed9898b78297c47851619daa7171952c914727 (branch fix/r9-postreview-rca)
Authored head: 9a901e7abab9d2bdd2792a1b0208614659922333
Reviewer scratch: /Users/timmalmstrom/hpo-seats/r9rev-2124/ (worktrees wt, wt-parent, wt-red)
Date: 2026-10-10

## RESULT lines

RESULT agreement-lane head: `pair finding-class-id: 3 readers, 38 items, 0 divergent` — AGREEMENT ok (rc 0), run by reviewer from tools/policy/agreement_py.py + agreement.mjs at 9eed9898b
RESULT agreement-lane parent 0cb141661 (the refused first attempt / the registration mutant): `DIVERGENT finding-class-id "N-postreview-merge-red": bugclasses.json ids + "new"=true finding.schema.json enum=false audit-find.js CLASS_GUESS (intake)=false` — AGREEMENT REFUSED (rc 1), reproducing the body's quoted refusal verbatim
RESULT class-arm 04d10721b: rc 1, exactly one site `prepr.sh:1398: printf '%s\n' "$flow" | grep -q 'moved_line "'` (0.099 s)
RESULT class-arm null controls: 23d354970 rc 0 (0.053 s), 00e31e8a3 rc 0 (0.058 s), origin/main rc 0 (0.050 s)
RESULT class-arm bd59a4af1: rc 1, 4 sites (prepr.sh only) — matches the claimed merge-base row
RESULT self-test at 04d10721b (reviewer's own run): rc=2, 134 s, `243 passed, 1 failed`, FAIL row byte-identical to CI's (ev/selftest-at-red.log); finder measured 122 s
RESULT CI at 04d10721b (check-runs API, reviewer): instrument-self-tests failure completed 21:47:51Z; pr-contract failure 21:49:34Z; parent 316a36414: zero failing checks — green at reviewed parent confirmed
RESULT #2072 timeline: 04d10721b 21:45:55Z, red 21:47:51Z, fix head 00e31e8a3 07:29:47Z (9 h 42 m), merged 12:11:35Z (14 h 24 m) — reproduced from git + PR API
RESULT #2066 matrix: 386b7e2ff vs d0f085ffb rc 0 / 0 conflicts; vs 23d354970 rc 1 / 53 conflicting files (finder: 27); 67a832653 vs d0f085ffb 0 / vs 23d354970 56 (finder: 30) — the clean-vs-conflicting direction reproduces at both heads; the file counts differ from the finder's (both runs in a worktree sharing the claimnotes merge driver config)
RESULT fold_ledger check at head: `29 classes, 0 violation(s)` — matches body
RESULT tests/structure.py at head: STRUCTURE RATCHET PASSED
RESULT env_drift --claims-only c729bb32e: ok
RESULT PR #2124 check-runs at 9eed9898b: total 40 — 23 success, 0 failure, 14 skipped, 1 neutral, 2 running; no red check at any branch head CI graded (0cb141661, 9a901e7ab: no failures); the one red in the body's account (prepr agreement lane at the parent) is answered with "no cheaper detector: the lane is the comparison" and demonstrated
RESULT harness-headers inputs byte-identical merge-base..head (dev/audit/rounds, dev/audit/harnesses, dev/audit/waves/w5-g5-195-coverage, tools/audit/judge_batch.py) — the local red is main's, as the body claims

## Census — NOT reproduced as stated (report, not confirm)

Stated enumerator (RCA doc F5, mirrored in bugclasses.json `detector`):
`git log --all --since=2026-10-08 --grep="^Merge remote-tracking branch 'origin/main' into "` → finder: 76.

Reviewer re-derivation, same window, cutoff at the document commit 0cb141661
(2026-10-10T18:11+02:00), over refs reachable from origin (fresh-clone-visible):
124 such merges; the finder's 76 is a strict subset; 48 extras, all reachable
from origin remote refs; 36 of the 48 were pushed and have check-runs.

Of those 36 pushed extras, 17 carry failures beyond nightly-status/delivery-status;
checking parent 1 (check-runs API): 11 were green (or main-graded-only) at the
parent — i.e. merge-reddened instances the census missed. Corrected census:
~26 merge-reddened of ~112-124 recarry-shaped merges, 2026-10-08..10-10
(~8.7/day, ~21%) vs the stated 15/76 (19.7%, ~5/day).

Direction: every correction makes the defect side larger and the rate higher;
the cost test passes a fortiori (standing cost at the corrected ~41 recarries/day
is ~55 min/day against a defect cost of ~4.3 h/day at the corrected rate).
The registered `detector` text in bugclasses.json carries the undercounted
figures; a later re-measure should refresh them.

Artifacts: ../my-recarries.txt, ../extras48-checkruns.txt, ../extras48-failures.txt,
../extras-nondelivery-reds.txt (parent statuses in the review transcript),
f1-*/ (per-tree class-arm runs), selftest-at-red.log/.result, ag-head.log via
transcript (agreement runs logged to /tmp/ag-head.log, /tmp/ag-par.log — copied).

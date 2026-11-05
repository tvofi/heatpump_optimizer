BLOCKED: round-7 resume seat superseded by the FINAL BODY-ONLY dispatch; DST-date seams found, fixed on this ref, not handed off.

This seat ran the round-7 resume dispatch (PROMPT.md at 54b79cce5, base 8ddab3178). At 09:24Z dispatch/fixer-r10-suite-host-determinism moved to the FINAL BODY-ONLY round (base cd0dd1691): "the host-zone class is CLOSED ... the PR merges as is ... NO PRODUCTION OR TEST CHANGE". That round's seat pushed handoff/ at 0cac0fe21b10e28d0a6e99aafd7af0ac84625c09, and handoff-body/ moved to 9b95d2a69d49c535c769fe328a723ca9d72d943b at 10:03Z, so its BLOCKED (kept below) reads as resolved. This seat did NOT push handoff/ or handoff-body/: either push would move the PR head against the ruling and the review freeze.

Question for the orchestrator: route the test-only DST-transition-date seams below as a next part of R10-SUITE-HOST-DETERMINISM (or a new group), or close them. The commits are on this ref and touch no production file.

## What was measured (dev/audit/harnesses/host_zone_features.py, faketime 0.9.10)

- Zone rows at ab57cc053 (round-6 wip + main 8ddab3178), `--suite` under gate, UTC, America/New_York, Asia/Tokyo, Europe/Stockholm, Asia/Kolkata: every script passed except tests/golden.py and tests/env_drift.py --all in each non-UTC zone. `--golden-zones`: the head's 56 of 56 payloads equal the gate row's in every zone; base 8ddab3178 moves the five coord_* scenarios in every non-UTC zone. So that red is the base's zone dependence, which 287669a53 removes; it is green in the gate row. finite_boundary passed in all six rows (the verdict's New_York 1/108 and Kolkata 2/108 are closed). The first run hit its time limit before stress.py and harness_headers.py ran in the first five rows; both passed under Kolkata.
- DST-transition DATE rows (clock started after the change, no jump during the run). The seam: a test offsets the clock as `dt_util.now() +/- timedelta`, which adds on the zone's wall clock, an hour off on a 23 h or 25 h day; production measures every age in UTC (_utc_age_seconds, utc_elapsed_seconds).
  - Europe/Stockholm@2026-10-25T04:00:00: features 1 of 4800 (#1532: hours_since read 3.0 h for a stamp meant 2 h back), solar_alignment 3 failed (got 300 want 240).
  - Europe/Stockholm@2026-03-29T04:00:00: features 8 of 4800 (90-min stale floor, 0.15-1.5 h interval bound, 12 h legionella boost bound); solar_alignment got 180 want 240.
  - Any host date before 2026-06-01 (faketime 2026-03-22 Stockholm, 2026-03-29 UTC): features 1 of 4800, the D1-s3-01 loaders bounding a 2026-06-01 stamp against the host clock.
- After the fixes (tree 38943ff29): features ALL 4800, entities ALL 2623, manual_plan ALL 132, solar_alignment all passed, under UTC, Europe/Stockholm, Stockholm@2026-03-29T04:00, Stockholm@2026-10-25T04:00, America/New_York@2026-03-08T04:00 and America/New_York@2026-11-01T04:00.
- Rule: `grep -cE '\b(dt_util|_[a-z0-9_]*dt)\.now\(\) *[-+] *timedelta' tests/*.py` read 49 sites (features 41, manual_plan 5, entities 2, dst_checks 1) before, 0 after; custom_components reads 0 at both ends. tests/dst_checks.py is a Stockholm-configured fixture outside run.sh: UTC 7/134 and New_York 6/134 red, the same counts at base 8ddab3178; Stockholm all passed.
- Mutants (detached worktrees): finite_boundary_leaf_zone KILLED (New_York 2/108; Tokyo, Stockholm, Kolkata 1/108; UTC passed). solar_day_elapsed KILLED (both Stockholm transition dates red; UTC and Stockholm passed); the unmutated null passed in all four rows.
- Open, measured, not fixed: with the clock CROSSING the spring change mid-run (Europe/Stockholm@2026-03-29T01:59:30), features and entities fail whichever checks run at the jump (early_cutoff, split learner, #1460 windows; the set moves run to run), because unfrozen test blocks read the live clock more than once. CI never crosses a transition (TZ=UTC). No fix built.

## Commits on this ref (none in handoff/ 0cac0fe21)

- 3181c94701daec1fb2738d4c5f5684b747c75f12 host_zone_features: a zone may start the clock at a local instant under faketime
- c82ec277fdade4ade3c8534be5d5eaadfa5e65db features: freeze the D1-s3-01 loaders' clock at the block's own instant
- f1a90f068cff6ddb10a1cbdd397c286f082a9d22 tests: measure elapsed time in UTC where a DST-transition day reads it (solar_alignment, features #1532, harness mutant solar_day_elapsed)
- 38943ff29930bcd63caee911607e8aea91d2e927 tests: offset the clock in UTC, not on the configured zone's wall clock (49 sites)

Not run on these commits: tools/pr/prepr.sh and the scoped gate (stopped when the dispatch was found superseded). python3 tests/structure.py passed at 3181c9470. PR-BODY.md on this ref is the body-only seat's, not this seat's.

## Previous BLOCKED on this ref (the body-only seat's, 09:56Z)

BLOCKED: body_push.sh r10-suite-host-determinism refuses the body.

Code is pushed: refs/heads/handoff/r10-suite-host-determinism at 0cac0fe21b10e28d0a6e99aafd7af0ac84625c09 (main cd0dd1691 merged, prepr.sh rc=0). The final body is on this ref as PR-BODY.md; `prepr.sh --body-check` reads 0 errors.

body_push output: `CARRY-MISSING R10-GATE-LEASE-TOCTOU body item 42008ca4: not in its brief or carries`. The group is in the roster at 7f6468d1 (line 16813), but its `carry` is [] and its brief says "PR 3170", which carry_audit.landed() does not match (it needs the item id or `#3170`/the topic as a whole token). Landing means `append-carry` on handoff/audit-r10-roster, a branch this seat may not write.

Question for the orchestrator: land the carry on the round's roster branch with `python3 tools/audit/carry_audit.py land-ops` (item 42008ca4, body text from PR-BODY.md `## Forward-carry`), then run `bash tools/audit/seat/body_push.sh r10-suite-host-determinism PR-BODY.md` from handoff/r10-suite-host-determinism. The step ref is left in place.

Fix review: merge 4e1c290e0138b4c145b338030b557a62f58950f7

bus-nonce: 13dd7e898abd9677e174315a459234ee

Round 2 (repair round). Round 1 established the substance at b5c9e5bba and
blocked on root-cause-unanswered; this round verifies the repair at the pushed
head 4e1c290e0, a merge that adds only this PR's delivery row to the repair
head 27ad9640e.

## 1. The five fixture re-recordings are add-only (measured)

Recursive leaf-by-leaf comparison of every tests/golden/coord_*.json between
the merge base d3dbf2c3fc42 and the head, over 1850-2076 base leaves per file:

RESULT coord_all_features: CHANGED=0 REMOVED=0 ADDED=33 (all under `sensors`)
RESULT coord_dhw: CHANGED=0 REMOVED=0 ADDED=33
RESULT coord_grid_fee: CHANGED=0 REMOVED=0 ADDED=31
RESULT coord_minimal: CHANGED=0 REMOVED=0 ADDED=31
RESULT coord_two_zone: CHANGED=0 REMOVED=0 ADDED=31
RESULT add-only: ALL FIVE ADD-ONLY

No existing value moved anywhere: no solver float was re-recorded off-canonical
(rule 3 honoured; the "keys added, no value moved" direction is literal).

## 2. The claims are honest (re-run by me)

tests/env_drift.py --all d3dbf2c3f at the head (venv-ci 3.14.7):
RESULT env_drift: NO UNCLAIMED DRIFT: 56 scenario(s) checked against d3dbf2c3f
RESULT env_drift: NO STALE FIXTURE: 56 committed fixture(s) still match
claims-for: 6.7.17 in both claim files; VERSION=6.7.17; manifest 6.7.17; notes
heading v6.7.17; none of the three touched by the diff. Each of the five new
claimed_drift lines states its direction ("keys added, no value moved"); none
of the five also appears in the may-drift list. tests/card_drift.mjs (after
plan_view) at the head:
RESULT card_drift: 39 state(s) moved and claimed, 1 identical
The card claim file's rewrite of the two inert #2010 lines subsumes them: both
states are re-claimed with this diff's own reason, so no excuse was lost and
card_drift is green both ways.

## 3. The pins are real (re-driven by me)

11 killed_by entries added (10 by tests/entities.py, 1 by tests/debug_collect.py
-- counted from the diff), each naming anchor, driver and before/after. Sampled
four; anchors match the head's code (sensor.py:2081-2086 verified). Targeted
mutant re-run at this head: COP-alarm guard -> if False: took entities.py from
ALL 2267 PASSED (baseline re-taken by me, clean) to rc=1 with
"FAIL UX-7: the status is learned, still learning, or needs attention on a COP
alarm". The tally read 2, not the ledger's 1: the second failing check is
entities.py's own R9-F10.13 pin self-test, which re-drives pin 49f1f2ee and
fails because the mutation removed its anchor -- a second detector of the same
line, not an independent red. The pins are additionally enforced live: that
self-test verifies pin reproduction against the real tree on every run.
tools/pr/ci_predict.py --base origin/main at the head prints no ADDED UNPINNED
line.

## 4. Production tree unchanged from the reviewed code head

git diff 574345d95..4e1c290e -- custom_components/ names one file,
debugger.py, whose three commits (5ad913305, 8cfc35591, 1e60f1861, R9-DBG-2)
are all ancestors of origin/main -- main's own change, merged in. No
branch-authored commit after 574345d95 touches custom_components/ (verified by
git log --no-merges over the range). Resolution delta of that main merge judged:
the branch does not touch debugger.py, and entities/env_drift/card_drift are
green at the merged head.

## 5. ## Red checks is truthful in both directions

Check-runs API at b5c9e5bba: exactly four failures -- fast (3.14), mutation,
pr-contract, mutation-autofix. The body names all four and answers each; no
red it fails to name, no name that is not red. At the pushed head every
concluded check is green or skipped (pr-contract success); fast (3.14),
mutation, closures and coverage were in_progress at 21:17Z when measured --
the merge train gates them. The reworded Friction bullet carries no closing
keyword; prepr on the body (PREPR_SKIP_CLOSURES=1, as disclosed) is clean:
PRE-PR 4e1c290e, PR-BODY 0 errors, figures 30 resolved.

## Other contract steps

- merge-tree --write-tree origin/main 4e1c290e: clean, exit 0 (no claim-file
  conflict against main's current tip 6918cb4b2).
- Forward-carry: none owed (body states none; carry-1795 honoured, round 1).
- Head was 4e1c290e at publication (ls-remote re-checked).
- Evidence: /Users/timmalmstrom/hpo-seats/r9rev-2120b/ev/ (addonly.txt,
  envdrift.txt, carddrift.txt, cipredict.txt, pins.txt, mutant-full.log,
  baseline-tally.txt, prepr.txt, checkruns-head.txt; head named herein).

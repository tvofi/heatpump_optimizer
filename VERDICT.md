Fix review: merge 715fbbe5d3805b034667b98858eb65a14b6ad0d2

bus-nonce: 75bb82dfa8b5e831cce760962321e6ee

## Summary

Round 1 at 715fbbe5d3805b034667b98858eb65a14b6ad0d2 (R11-PRE-ROUND-METRICS, part of the group after #3612). The diff is instrument-only (`tools/audit/seat/`, `.github/CODEOWNERS`, `governance.yml`, the closure tables); no `custom_components/` line. The self-tests are not vacuous: all eight of my own mutants, separate from the PR's, are killed. The null control holds, and every figure I could re-take matches. CI is GREEN at this head, and the head merges cleanly with origin/main.

Note: carry-route: the closing `Carry: R11-PRE-ROUND-METRICS` leaves roster carries 5-8 to a "part 2". `fixer.md` allows that only for a split the approved plan names. The split traces only to #3612's citation of owner card E11-N-P744-SCOPE (tvofi 2026-11-15). That card resolves nowhere in the tree, the plan ref or the roster, and the group's roster entry names no parts. Carries 5-8 are already on the group's roster entry, so no finding is lost. This is paperwork, not a block (C5).
Note: body: the opening line says "part 1 of 2", but #3612 merged as part 1. This PR is the second part to land.
Note: code-owned: `.github/CODEOWNERS`, `tools/audit/seat/round_metrics.py` and `tools/audit/seat/scorecard.py` are owned by `@tvofi`, so the owner's approving review is still required at merge.

## Evidence

- RESULT classify: `GREEN 715fbbe5d3805b034667b98858eb65a14b6ad0d2 pending: none red: none` (ev/classify.txt, ev/classify-log.txt). The commit's check-runs API lists 69 runs; none ends other than success, skipped or neutral (ev/check-runs.txt).
- RESULT merge-tree: `git merge-tree --write-tree origin/main 715fbbe5…` exit 0, `LEDGER-MERGE: resolved tests/closures.json`, tree 85a3fb7f (ev/merge-tree.txt). The head is behind main (origin/main 6aa7ddc7) but merges cleanly.
- RESULT self-tests at head: round_metrics `ok (with mutants)`, bottleneck_check `ok`, beat_jobs `263 checks, 0 failed`, scorecard `ok (with mutants)` (ev/selftest-*.txt).
- RESULT reviewer mutants (step 1; my own, not the PR's named set): 8/8 killed (ev/reviewer-mutants.txt):
  - partial-ledger NO-READ off
  - runner attempt match ignored
  - negative lead times kept
  - missing token seat class ignored
  - cancelled runs in the product_green denominator
  - `CI_ATTEMPT_ALARM` 20→21
  - `WORSE` 0.25→0.0
  - restore window start dropped
- RESULT null control: `window_lines` over a missing directory prints 6 of 6 lines `unread (` (ev/figures.txt). This matches the body.
- RESULT figure, digest: at head, `beat_jobs.norm` blanks the "h" wording to `<age>` and keeps the "hours" wording (`4.2 hours`), as the body says (ev/figures.txt).
- RESULT figure, gate checks: `round_metrics.gate_checks` over v7.0.0..v10.0.0 prints `unread at the window's start, 17 at its end`. This matches the body.
- RESULT step 5: `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched by the three-dot diff. Step 4 needs nothing: no fixture moves.
- RESULT `tests/structure.py` at head: `STRUCTURE RATCHET PASSED` (ev/structure.txt). No budget file is in the diff.
- RESULT a7 failing-first: the self-test's `live-never` mutant (the base's behaviour, always the first line) is killed at head (ev/selftest-bottleneck_check.txt).
- Not re-derived (step 8): these figures need a cold scan of about 60 s plus scratch drivers that are not in the tree, so they rest on the fixer's word:
  - the round-10 lead_time percentiles and merge counts (1139; 155/516/468)
  - the producer's cost timings
  - the branch-to-group mapping counts (308/166/38)
- Step 6, class: this is a new instrument, not a defect fix, so the body names no enumeration rule. Under carry 0 the enumerators are round_metrics.py and scorecard.py, and both are in CODEOWNERS in this diff.
- Step 10: the forward carry to R11-PRE-TOKEN-LEDGER states its control (`round_metrics.py --self-test` cases `tokens:`), and the M4 mutant confirms that control kills.
- Step 11: no red at head, so no `## Red checks` answer is owed.
- Review packet: unavailable (ev/review-packet-refusal.txt). I worked from the live PR, the roster at origin/handoff/audit-r10-roster d6fc32d6, and the role pack rendered at origin/main 6aa7ddc7.

## Findings

- Instrument defect, not this PR's: `tools/audit/seat/review_packet.py`'s `LANDED` regex accepts an all-decimal token as a sha. This PR's body cites CI run id 42469369199 on a line that also says "carry 3 … landed". `render` then raises `UNAVAILABLE: git merge-base --is-ancestor 42469369199 …` and writes no packet, so a reviewer starts without one. The sha group should require a hex letter or a resolvable object, and a non-object should be dropped, not raised (ev/review-packet-refusal.txt). Carry: R11-PRE-HANDOFF-BOOKKEEPING

## Friction

- `review_packet.py render` refused on a body citation; the defect is the Findings item. Carry: R11-PRE-HANDOFF-BOOKKEEPING

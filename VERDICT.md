Fix review: merge 253dc4867cf39f2aa9875f5f2540c5b67b7c1018
bus-nonce: 4a8881260b33bb3af3fb54ea694564e5

# Fix review -- PR #2876, R10-HOUSE-GRADE

Reviewed head: 253dc4867cf39f2aa9875f5f2540c5b67b7c1018 (PR head; GitHub's
`headRefOid` matched it through the review). My worktree: a detached worktree
at the head under ~/hpo-seats/r10s6/rev-2876-wt; the base
worktree at 3b4180dcc; mutants in a third worktree. I never ran the fixer's
worktree, pushed the branch, or touched the clean main checkout except to
publish this verdict.

## Results

- Claims. `tests/golden/claimed_drift.txt` gains 20 lines at its tail (14 of
  prose, 5 claim lines, one blank) and no value leaf is re-recorded;
  `claims-for: 7.0.4` equals `VERSION` 7.0.4 in both claim files. The five
  fixtures gain exactly `"envelope_drivers": []` at two paths each: `git diff
  --stat 524c1896b..HEAD -- tests/golden/coord_*.json` = 5 files, 10
  insertions(+), 0 deletions. None of the five is in the may-drift list. Bare
  `python3 tests/env_drift.py` exits 0: `NO UNCLAIMED DRIFT: 5 scenario(s)` and
  `NO STALE FIXTURE: 5`; `--all 524c1896b` exits 0: `NO UNCLAIMED DRIFT: 56`
  and `NO STALE FIXTURE: 56`, all five CLAIMED. The change is a claim
  extension, not a quiet re-record.
- The empty list is the true value for these five, not a mute button. Each
  fixture publishes `envelope: null`; all five report reason
  `heat_loss_learning`. `coordinator.envelope_score` returns
  `(None, reason, [])` on its no-grade paths and `compose_scores` publishes
  the third element, so no non-empty driver list exists for a null grade. The
  head capture reproduces `[]` exactly (no stale fixture), which is the
  empirical check that production emits the empty list here.
- The finder's harness moves at both ends and under its own perturbation.
  `r10_house_grade`: at 3b4180dcc era_spread 67.7, owner 20.3/44.3, monotone
  False, curve_min 0.0, drivers_max_gap None; at head 0.0, 35.2/35.2, True,
  4.23, 0.0; at head `--era-blind` 50.5/16.8/1.61. `r10_scores_envelope`: the
  40 `RESULT band` rows are `tree_grade=50.0` at head and span 21.8..99.9 at
  the base; `split_max_abs_gap=0.0` at both ends and 36.5 under M4.
- Commits. Eight between 524c1896b and the head, matching the report. The
  roster gives R10-HOUSE-GRADE three `files`; finding F2 below.
- Head checks. 55 check-runs at 253dc4867: 39 success, 16 skipped, 0 failure,
  0 null. Both `gate` check-runs (122252356685, 122251924378) are success, and
  both gate job logs end `Judge this head ... PASS`. The quoted
  `FAIL run(s) [40510616385] ... still being judged` is the gate's deferral
  and resolved to PASS; it is not a red.
- Body figures reproduce except one range (F1): features.py `ALL 4463 FEATURE
  CHECKS PASSED`, config_flow_steps `ALL 502 checks PASSED`, structure ratchet
  PASSED, `card_drift.mjs` `1 state(s) moved and claimed, 44 identical`, and
  the split/era/owner/curve/band-uniform figures above.

## Findings

### F1 -- body figure not reproducible (non-blocking; correct the body)

Claim: the body says the base's `band` rows report "`tree_grade=50.0` for
every preset house at this head against 48.7 to 83.6 at the merge base"
(line 127) and "`band` rows' `tree_grade=50.0` against 48.7-83.6" (line 151).
Evidence: in a worktree at 3b4180dcc the 40 `RESULT band` rows span 21.8 to
99.9; 48.7 and 83.6 are exactly two interior rows (`two_zone=1 timber_slab
1960_1980` and `two_zone=1 timber_slab low_energy`). Harness: `PYTHONPATH=
tests/hastub python3 dev/audit/harnesses/r10_scores_envelope.py`, run with
both the base tree's harness and the head's harness against the base tree
(identical 21.8..99.9) and at the head (40 x 50.0). Metric: min/max of
`tree_grade` over the 40 band rows. Perturbation: the head moves every row to
50.0; the base spread is real, so only the stated endpoints are wrong. The
qualitative claim (uniform at head, spread at base) survives.

Carry: R10-HOUSE-GRADE (item ea167ba8)

### F2 -- the roster's `files` under-specifies the seam (non-blocking)

Claim: a commit outside the group's `files` is a finding even if correct.
Evidence: c89e5b5db touches `config_flow.py` and `payload.py`; the roster's
`files` for R10-HOUSE-GRADE lists only coordinator.py, presets.py and the card
JS. Both extra files are inside the group's seam (the questionnaire read moves
to `presets.preset_from_config`, and `payload.Scores` must carry the new key)
and the body discloses them. Harness: `git show --name-only c89e5b5db` against
the roster entry in dev/programme/rosters/wave-r10-groups.json. Metric: two
production files touched and not listed. Perturbation: none needed; the roster
and the diff disagree on the set. Record them at the next roster edit.

Carry: R10-HOUSE-GRADE (item 966df279)

### F3 -- the body's drift-lane command is now two-dot (observation for the orchestrator)

Claim: the drift lane is `python3 tests/env_drift.py --all origin/main`, with
`origin/main` then being 524c1896b (body line 175-179). Evidence: origin/main
has since advanced to 34cd75bf1 (merge of #2745, R10-SAV-COMFORT), and that
run now reports 2 unclaimed drifts, `negative_prices` and `summer_dhw_only`
(`savings_percentage 16.17 vs -13.19` and `5.88 vs -7.62`). Current
origin/main itself claims exactly those two (claimed_drift.txt:62-63, "R10-
SAV-COMFORT: the warm start is debited only what it displaced"). The branch
changes no solver file and neither fixture (`git diff --stat 524c1896b..HEAD`
over optimizer.py, thermal_model.py, accuracy.py, pricing.py and the two
fixtures is empty), and the three-dot run against the merge base 524c1896b is
green: `NO UNCLAIMED DRIFT: 56`, `NO STALE FIXTURE: 56`. Metric: the two-dot
drift set vs the three-dot set. Perturbation: moving the baseline from 60788cb8
(origin/main at my first run) to 524c1896b removes both; they are main's
movement, not this branch's, and no claim is owed by this branch under
CLAUDE.md rule 3.

### F4 -- merge-time claim-file resolution (observation)

`git merge-tree --write-tree origin/main HEAD` refuses only
`tests/golden/claimed_drift.txt`: both sides rewrote the claim list (main's
side carries the two SAV-COMFORT claims, this PR brings the five coord
claims); LEDGER-MERGE resolves tests/closures.json. The orchestrator resolves
the claim list by hand at merge, keeping both sides' live claims. This is the
claimnotes driver doing its job, not a defect of the branch.

## Known limitation, disclosed and not new

`tests/entities.py` classifies presets.py module-wide in `_EC_RESIDUAL`; a
future read added elsewhere in presets.py would inherit that disposition
unjudged. The body states this and routes a per-site census to its owner; it
is not this PR's to change.

## What I could not establish

- I did not re-run the 60m43s `tests / mutation` job locally. I rely on its
  green check-run at the reviewed head, the four committed `killed_by` rows,
  and my own M1/M4 perturbation showing the grade lines are live.
- I did not execute the fixer's two scratch slice drivers (they live outside
  the tree). The tree's own `tests/features.py` (ALL 4463) and
  `tests/config_flow_steps.py` (ALL 502) pass at the head.
- The transient origin/main SHA in my first two-dot baseline header
  (60788cb8...) is not in the local object database; it does not affect the
  conclusion, because current main claims both drifts and the three-dot run is
  green.

Verdict: merge 253dc4867cf39f2aa9875f5f2540c5b67b7c1018. F1's body fix and
F2's roster record are follow-ups for the record, neither touches the code
head.

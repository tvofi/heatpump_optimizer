Fix review: merge e6c2df546902b2d91104494ad812ab79350f5db4
bus-nonce: 8e5e9aec47d9b8c5970b68457ca71c83

# Fix review -- PR #2894, R10-IMMERSION-LATCH, round 1 (first review of this PR)

Reviewed head: `e6c2df546902b2d91104494ad812ab79350f5db4` (GitHub's `headRefOid`
at the start and again before publishing): the authored code head `10f75266e`
plus merges of main and the PR's own delivery row. `git diff 10f75266e HEAD --
custom_components` is empty, so the code measured at `10f75266e` is this head's.
Merge base: `6e5995e51`. Worktree: detached under
`~/hpo-seats/r10s6/rev-prod-s8/2894/`.

## Harness

#2729 came from D15 triage of the owner's bundle (derived ratios only) and has
no committed harness. The roster brief names its controls: a no-element
install drawing 2x its ask books no immersion; a configured booster books only
the excess over nameplate while its flag is on; a flat draw at or below
nameplate books zero; one mutant. Those controls are the `R10-IMMERSION-LATCH`
block of `tests/features.py`. I ran that block myself, at both ends, through
a prefix driver of my own (`ev/mutants/mutants.py`: features.py lines
1..18632 over a copy of the tree with one edit):

- RESULT base `6e5995e51` production with this head's tests: **7 FAIL**. The
  no-element install books `immersion 1.5` (the defect); booster, backup and
  declared-element arms book `immersion 2.45`, the excess over the plan's ask.
- RESULT head (NULL): `FAIL=0`, 1424 ok.

## Mutation proof (reviewer's own, same driver)

All killed:

- RESULT M4 (`actual_kw <= threshold_kw` -> `<`), M5 (`hours <= 0.0` -> `<`)
  and M6 (`threshold_kw <= 0.0` -> `<`): 1 FAIL each, `the carve refuses at its
  bounds`.
- RESULT M7 (`if resistive_line:` -> `if False:`): 6 FAIL.
- RESULT M8 (the pre-fix `if resistive_kwh > 1e-6:` restored): 1 FAIL, `a carve
  smaller than any epsilon is booked`.
- RESULT X1 (the both-flags refusal deleted): 1 FAIL, `both heater flags on
  refuses the line`.
- RESULT X2 (no source still books `immersion`): 3 FAIL, the no-element arm,
  the flags-off arm and the savings null.
- RESULT X3 (the latch ignored): 1 FAIL, `the latch is the gate`.
- RESULT X4 (kWh over zero instead of over the threshold): 3 FAIL, the booster,
  backup and element arms.
- RESULT M3, #2805 (`quantise_setpoint_c(..., rounding="up")` -> nearest,
  driver features.py 1..40490): the `#2805` check FAILS. The NULL at the same
  prefix shows only the `.git`-less copy's `recorded_at (#363)` artifact, which
  both runs share.

## Other checks

- RESULT `ci_predict.py --base origin/main`: `3 unpinned site(s)` (coordinator
  `if resistive_line:` GUARD_OFF, pump_signals:247 CMP_BOUND*2, :249
  CMP_BOUND). These are exactly the three in `## Unpinned sites`, each disposed
  of as pinned by `mutation-autofix`. My M4-M7 confirm all four mutants killed.
  `tests / mutation` is red at this head on those three only (job
  122598261075, `4 of them added by this diff` counting the *2). That is the
  expected bot-pin red; per the dispatch, the pin commit landing on top is
  allowed.
- RESULT `tests/structure_budgets.json` three-dot: `class_excess_loc` 18044 ->
  18038 and `max_class_loc` 8167 -> 8161, both down, earned by the
  coordinator's deleted inline carve. No raise.
- RESULT `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/` are
  untouched by the three-dot diff.
- RESULT review packet: Refusals none, `CARRY-AUDIT: 2 routed`, `FIGURES: 7
  resolved, 1 not verified, 0 refused`.
- RESULT live checks at publish (`ev/checks-at-e6c2df546902b2d91104494ad812ab79350f5db4.txt`): `tests / fast (3.14)`,
  `tests / closures` and `tests / coverage` are success. Red: `tests / mutation`
  only (the bot-pin red above). In progress: `tests / mutation-pins (1)`,
  `prelude` and CodeQL python. The pin commit that lands is allowed by the
  dispatch and carries this verdict only if it passes the carry predicate.

## Findings

- No committed harness for #2729: the brief's controls live only as features
  checks, and the fixer's and my mutant drivers are both out of tree (the
  body's Friction already names `features_block.py`'s header-only limit). The
  checks are the instrument and they re-run. Carry: dismissed: the roster's
  controls are in tests/features.py and move under every mutant above
- The body's `class_excess_loc 18041 <= 18047` / `max_class_loc 8216 <= 8222`
  figure is from an earlier head. At this head the recorded rows are 18038 and
  8161 against main's 18044 and 8167. Carry: dismissed: a stale snapshot of a
  ratchet that only moved further down

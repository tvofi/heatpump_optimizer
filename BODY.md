Part 2 of R11-OUTSIDE-SELF-SETTING-PUMP: roster carries 5, 6 and 7 (#3662 items 0b01d5fd, 06cb4f11, 26742487). Carry 5 is built as departure A and carry 6 as departure B1. Carry 7 is measured and not fixed in this part. Base 3f7f29e778 (#3662's merge).

Accepted departures from the approved note (`design.md` at design/R11-OUTSIDE-SELF-SETTING-PUMP 0acbbc8b91). Both come from BLOCKED.md at handoff-wip/r11-outside-self-setting-pump-p2 db6f3f9476 and were approved by the orchestrator's ruling, refs/heads/inbox/r11-outside-self-setting-pump INBOX line 2 (mandate 6893738184):
- **A (carry 5).** The note says "a refused or frozen cycle between them voids the pair instead of stretching it". Under A, a read cycle that admits no row keeps the pair in flight. The slot it missed is handed out again and held until a row is read under it. The pair voids once `COP_HOLD_HORIZON_S` has passed since its first row, or since `ScaleDither.since` before it has one, and the scale then waits at the base until a row is read. Frozen and unread cycles still void.
- **B1 (carry 6).** `PROBE_VOID_CAP` = 3 probes in a row that a reset ends with no pair read make the next probe park on its first row for `COP_HOLD_HORIZON_S`. The count clears at the re-arm and after any probe that read a pair. B2 (the heat-ask dither (c1) and the closed-loop planner harness) is routed to a new design group by the orchestrator and is not built here.

## Head

d8e8b5fb28cff06f8f1d945bda97e71780e2116c, cut from 3f7f29e778e009f12a2008318b1f879f531ef3a1. origin/main was 7c2f4c30ca at 2026-11-18 (UTC); `git merge-tree --write-tree origin/main HEAD` exits 0, so there is no conflict and no merge. The figures were taken at e26b5120061bc44f824d991d15a982d9f7b3dd74. The head differs from it only by three deleted files under `tests/mutation_ledger/survivor_triage/` (`git diff --stat e26b512006 d8e8b5fb28`: 3 files changed, 18 deletions), so no production, test or harness line differs.

prepr: passed rc=0 at d8e8b5fb28cff06f8f1d945bda97e71780e2116c

## Mutation proof

The fixes were deleted from production one at a time. Each run used `python3 tools/audit/seat/features_block.py --prelude "exec(open('<emit-prelude>').read())" 'COP learner duty floor keys' 'R.section("R10-HOTFIX-COP-UNMEASURED'`, with the prelude from `--emit-prelude` over the same markers:
- **Whole fix removed** (`accuracy.py` at 3f7f29e778, new tests kept). The block `# A read cycle that admits no row (a floor refusal)` fails "two (or three) admitted rows then a floor refusal, over 300 cycles: the pairs complete and the follower latches follows" (latched at [None, None]; pending/pending). The block `# Carry 6 (BLOCKED.md` fails "a re-priced plan resets its probe with no pair read; after PROBE_VOID_CAP (3) ..." with (28 probes, 70 dithered cycles, pending, no `voided`).
- **The hold only** (`self.ahead = want if self.holding else self._next(want)` replaced by `self._next(want)`). This fails "a slot whose row was not read is handed out again and held until one is", "a pair holding for its second row voids once COP_HOLD_HORIZON_S has passed", "a first slot no row is read under ..." and "the next pair's first slot, no row read under it, ...".
- **The B1 park** (`if self.voided >= PROBE_VOID_CAP: self.parked_at = row.at` deleted). This fails "a re-priced plan resets its probe ..." and "a probe that starts at PROBE_VOID_CAP voided ones parks on its first row ...".

Diff mutants: `tools/audit/seat/mutant_run.py --diff <base>...HEAD --in-place --max-mutants 0 --report-only` with the block above as `--cmd`. At e26b512006 every mutant on an added line is killed except the four equivalents named under `## Unpinned sites`. The first run, at ce600a8b91, had 13 survivors. Each of the others received a killing check (`clear()`, the void's flag reset, the step's flag consumption, the horizon's lower bound, the first-slot and next-pair holds, the stale row-read flag on a parked cycle). One survivor showed a dead line, `take`'s `holding` reset, which is deleted. Another showed that the step's `since` assignment was reachable only through the pair start, so `since` is now set at the row that completes a pair.

## Null control

- **Null control 1** (`ScaleDither.levels` returning the base twice), `cop_duty_floor.py` rows `null_dither0_*`. Head and base both read `0/672_scale=1.000 ... band=0.000 verdict=pending` for the heat-led and the self-setting pump. Without the dither, nothing latches at either end.
- **Carry 6 cap.** With `PROBE_VOID_CAP` forced to 1000 (the cap off), the full `cop_duty_floor.py` output equals the departure-A-only output line for line (`diff` exit 0). The cap's effect is confined to the re-priced row. N = 1, 2, 3 and 5 each change only `repriced_heat1.2_true_0.8_x672` (off5 = 16, 18, 20, 24; probes 2, 3, 4, 6). No row in the harness separates them. N = 3 is taken because it lets a probe survive two resets caused by real ask variety before parking it.
- **Carry 7.** `cop_dither_fabric.py` puts each dither row beside its `null_dither0_*` twin and a `no_probe_*` row, which has `MeasuredCop._admits` false.

## Figures

Harness, both ends: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py`, 106 RESULT lines. It was run at 3f7f29e778 with the head's harness file (only rows and columns are added) and at the head. The rows that differ:

| row | base 3f7f29e778 | head e26b512006 |
|---|---|---|
| `sub_min_true_0.6_x384` | 0/384 1.000 off5=16 pending | 0/384 0.933 off5=48 pending |
| `sub_min_true_0.6_x480` | 0/480 1.000 off5=48 pending | 0/480 0.933 off5=144 pending |
| `sub_min_true_0.6_x1440` | 0/1440 1.000 off5=335 pending | 470/1440 0.599 off5=1103 follows |
| `repriced_heat1.2_true_0.8_x672` | 0/672 0.933 off5=140 probes=56 pending | 0/672 1.000 off5=20 probes=4 pending |
| `selfset_2.2_swing0.4_p3_s1` | 3/672 1.003 pending | 3/672 1.000 does_not_follow |
| `selfset_2.2_swing0.3_p4_s1` | 7/672 0.994 pending | 7/672 1.000 does_not_follow |
| `heatled_true_0.45_flat_from0.5` | 657/672 0.500 off5=662 follows | 656/672 0.500 off5=670 follows |
| `heatled_true_0.68_flat_from0.5` | 663/672 0.680 off5=662 follows | 662/672 0.680 off5=670 follows |
| `selfset_2.2_flat_reload70_400_lost` | off5=121 does_not_follow | off5=120 does_not_follow |

- **Carry 5.** `sub_min_true_0.6_x1440` folds 470/1440 and ends at 0.599 (the true scale is 0.6), the figures #3662 recorded for its base and blocked head. At 384 and 480 cycles the probe has not decided, and the scale sits on a dither level. The swing rows with periods of 3 and 4 cycles had tracking-refused cycles voiding their pairs. They now complete pairs and read does_not_follow, the right verdict for a self-setting pump. The `from0.5` rows lose one fold each, and their extra off-1.000 cycles are holds on a dither level.
- **Gap checks** (rule: `grep -c` over the RESULT lines, run at both ends). Self-setting rows latching follows: 0 of 48 at both ends. Heat-led rows reading does_not_follow: 0 of 4 at both ends. Control `heatled_true_0.8_flat_x672` is identical at both ends (672/672 0.800, probes=1, follows), and so are the latch at the 50th row and the uninterrupted sequence in the features checks.
- **Carry 6.** The features check over 336 cycles of the re-priced plan through the coordinator gives 28 probes and 70 dithered cycles at the base. At the head it passes with 4 probes and at most 20 dithered cycles.
- **Carry 7.** `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_dither_fabric.py`, 672 half-hour cycles, real plant, `_async_learn_interval` per cycle. At the head:
  - `dither_true0.8_2C`: house_scale=1.1000, house_samples=578, follows, max_gap_vs_null=0.0174.
  - `null_dither0_true0.8_2C`: 1.1000, 671 samples.
  - `dither_true0.8_9C`: 1.1000, 646 samples, max gap 0.0101.
  - `dither_true1_*`: identical to null (gap 0.0000, 671 samples).

  The same harness at 3f7f29e778 differs only in `dither_true0.8_2C`: 639 samples, max gap 0.0021. Result: the stored fabric value under the dither equals null control 1 to four decimals in every cell, at both ends, so the pricing #3662 read from the code does not reproduce as a stored-value bias. It does reproduce as lost house samples. On cycles the probe runs at its high level, with a COP error (true 0.8) the replay over-prices heat and the house learner refuses the sample. Departure A holds that level through frost-band stretches, where every COP interval is refused `frost_band`, so the loss grows from 32 to 93 samples at 2 °C. Sensitivity control: with no probe, the replay priced at 0.8 against 1.0 moves the stored house scale by 2e-5. Within this instrument the house fit responds to heat pricing only through its acceptance gate. The lower-floor learner is not reached: the two-zone profile pins the house scale at its 0.3 clamp in every arm, so that row is not printed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED at the head. `python3 tools/audit/archscore/score.py --diff 3f7f29e778e009f12a2008318b1f879f531ef3a1 HEAD`: Architecture score: dS +0.0000.
- **Scope.** `tests/closure.py select --diff <merge base>`: MODE: SCOPED -- 27 script(s) run, 6 scoped out. Scoped prepr only (`PREPR_SKIP_CLOSURES=1`). CI is the authority for the rest.

## Red checks

- `mutation` at d8e8b5fb28cf: red by construction on the 20 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push. No cheaper detector is owed: prepr's diff-mutant step ran them locally first, and every site it could drive is killed.

## Unpinned sites

- `custom_components/heatpump_optimizer/accuracy.py:1050 CMP_BOUND` (`ScaleDither.take CMP_BOUND 4dbfdd33`): equivalent, triaged in `tests/mutation_ledger/survivor_triage/accuracy.py/ScaleDither.take.CMP_BOUND.4dbfdd33.json`. This carries the d29ee146 triage of the same comparison, which was one level deeper before this diff.
- `custom_components/heatpump_optimizer/accuracy.py:958 CONST_SWAP` and `custom_components/heatpump_optimizer/accuracy.py:958 STMT_DEL` (the `holding` field default): equivalent, because `step` assigns `holding` before any read on every path. The ledger's inventory generates no site here, so no triage file is written.
- `custom_components/heatpump_optimizer/accuracy.py:1016 CONST_SWAP` (the first pair's number 0 -> 1): equivalent, because pair numbers are only compared for equality and every start follows a void that clears every slot. The ledger's inventory generates no site here, so no triage file is written.
- `custom_components/heatpump_optimizer/accuracy.py:858 CONST`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:986 RETURN_DEL`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:991 GUARD_OFF`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:993 GUARD_OFF`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:995 RETURN_DEL`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1010 BOOLOP`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1010 CMP_BOUND*2`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1010 GUARD_OFF`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1013 GUARD_OFF`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1014 GUARD_OFF`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1019 GUARD_OFF`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1022 BOOLOP`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1040 GUARD_OFF`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1043 GUARD_OFF`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1050 GUARD_OFF`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1135 CMP_BOUND`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1135 GUARD_OFF`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1189 RETURN_DEL`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1196 BOOLOP`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.
- `custom_components/heatpump_optimizer/accuracy.py:1196 GUARD_OFF`: killed by the tests/features.py block named under `## Mutation proof` (mutant_run.py at the head reads no survivor here); `mutation-autofix` pins it on CI.

## Forward-carry

- Carry 7's measured residue: on a heat-led install with a COP error, the dither costs the house learner its samples on high-level cycles. That is 93 of 671 at 2 °C with departure A, against 32 before it, with the stored value unchanged to four decimals. This bears on tuning the dither (the note's follow-up) and on the closed-loop harness. Re-measure with `dev/audit/harnesses/cop_dither_fabric.py` against its `null_dither0_*` rows at that group's merge base. The lower-floor learner is not reached by this instrument and needs a two-zone driver that does not pin the house scale at its clamp. Carry: R11-INTAKE-R10-RESIDUE
- B2 (the heat-ask dither (c1) and the closed-loop planner harness) is not built. Under B1 the re-priced install still learns nothing; it only stops dithering. The control is `repriced_heat1.2_true_0.8_x672`, which reads pending at both ends; identification needs the heat ask itself moved. The orchestrator's ruling (INBOX line 2) routes it to a new design group, which is not on the roster yet; R11-OUTSIDE-SELF-SETTING-PUMP is carries-open. Carry: R11-INTAKE-R10-RESIDUE

## Friction

n/a: nothing in the policy was unclear or contradictory for this part.

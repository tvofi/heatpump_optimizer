Part 2 of R11-OUTSIDE-SELF-SETTING-PUMP: roster carries 5, 6 and 7 (#3662 items 0b01d5fd, 06cb4f11, 26742487). Carry 5 is built as departure A and carry 6 as departure B1. Carry 7 is measured and not fixed in this part. Base 3f7f29e778 (#3662's merge).

Accepted departures from the approved note (`design.md` at design/R11-OUTSIDE-SELF-SETTING-PUMP 0acbbc8b91). Both come from BLOCKED.md at handoff-wip/r11-outside-self-setting-pump-p2 db6f3f9476 and were approved by the orchestrator's ruling, refs/heads/inbox/r11-outside-self-setting-pump INBOX line 2 (mandate 6893738184):
- **A (carry 5).** The note says "a refused or frozen cycle between them voids the pair instead of stretching it". Under A, a read cycle that admits no row keeps the pair in flight. The slot it missed is handed out again and held until a row is read under it. The pair voids once `COP_HOLD_HORIZON_S` has passed since its first row, or since `ScaleDither.since` before it has one, and the scale then waits at the base until a row is read. Frozen and unread cycles still void.
- **B1 (carry 6).** `PROBE_VOID_CAP` = 3 probes in a row that a reset ends with no pair read make the next probe park on its first row for `COP_HOLD_HORIZON_S`. The count clears at the re-arm and after any probe that read a pair. B2 (the heat-ask dither (c1) and the closed-loop planner harness) is routed to a new design group by the orchestrator and is not built here.

Carries outside this part. Carry 0, Carry 1 and Carry 2 were built by part 1 (#3662, merged at 3f7f29e778) and are not touched here. Carry 3 and Carry 4 were dismissed by the owner's 2026-11-16 ruling (both accepted as residuals); per the brief they are neither rebuilt nor reopened, and the roster lists them pending until mark-carry lines land.

## Head

889adacf26621dd6be9f7800ff62883e3019ae92, the PR head eebd64ea18bc7a4f750d6a58a29eadeaa2f0789c (d8e8b5fb28 merged with origin/main f567988b51, plus the delivery row) and two commits on it, the red repair asked by refs/heads/inbox/r11-outside-self-setting-pump INBOX line 3, then merged with the bot's `ci: pin killed mutants` fe95f3778e (mutation-autofix's 20 rows at eebd64ea):
- 7c3157869f `fix(cop-probe)`: the 5 mypy errors in `accuracy.py` (2 arg-type, 1 index, 2 union-attr) are fixed by narrowing, with no ignore added. `ScaleDither.step` builds the slot it wants from the pair it has just ensured. `ScaleDither.take` reads a pair's first slot as the one with no first row (`if first is None:`), which is the flag `_want` sets.
- e40082d743 `chore(ledger)`: 21 `killed_by` rows for the 21 added unpinned sites `tests / mutation` refused at eebd64ea.
- 889adacf26 merges fe95f3778e. The one add/add conflict (`ScaleDither._want.RETURN_DEL.d36267b7`) keeps e40082d743's row. The bot's `ScaleDither.take.GUARD_OFF.d8c3b58d` is deleted: it pins `if not second:` in `take`, a line 7c3157869f removed. Afterwards `tests/mutation_table.py --scope changed --base origin/main --max 0` reads 2091 unpinned sites, equal to the ratchet base, and "the ledger agrees with the deterministic inventory".

origin/main was ae0ed64af8 at 2026-11-18T13:46Z. `git merge-tree --write-tree origin/main HEAD` exits 0, so there is no merge.

The figures below were taken at e26b512006. The production diff since then is 7c3157869f alone. Both harnesses print byte-identical output at d8e8b5fb28 and at e40082d743 (`cmp` exit 0): `cop_duty_floor.py` has 106 RESULT lines and `cop_dither_fabric.py` has 12. Full `tests/features.py` passes at 7c3157869f (rc=0, 0 failed, 881 s).

prepr: passed rc=0 at 889adacf26621dd6be9f7800ff62883e3019ae92

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

- `tests / typing` at eebd64ea: 5 mypy errors in `accuracy.py` (recorded 0). It is repaired by 7c3157869f. At e40082d743, `tests/typing_ruler.py --mypy` under the pinned toolchain (`tests/requirements-typing.txt`, Python 3.14.7) reads ALL 9 typing-ruler checks PASSED; at eebd64ea it read 4 of 12 FAILED, +5 errors. A cheaper detector exists and was not run: the same ruler, local, about 70 s after a one-off install of about 1 min. `run.sh` runs it when `HPO_TYPING_PYTHON` names a pinned interpreter, and otherwise prints the install command and skips it. The process existed, and its precondition (a pinned typing interpreter) was not set on this seat (state b). No countermeasure is built: the gate already prints the skip, and making the pins mandatory would add the install to every seat, typed or not.
- `tests / mutation` at eebd64ea: `MUTATION TABLE REFUSED`, 21 added unpinned sites in `accuracy.py` (`ScaleDither`/`ScaleProbe`). It is repaired by e40082d743, recorded by `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py --jobs 4`, which ended `PIN KILLED: 21 pinned, 0 left unpinned`. The features.py baseline was rc=0 failed=0, and the `NULL_COMMENT` null control survived tests/features.py. The cheaper detector is `--pin-killed` itself, run locally before the handoff (about 2 h of wall-clock on this 4-core seat, because every mutant runs the whole of features.py). The previous handoff left these pins to `mutation-autofix`, whose `mutation-pins` shards had not concluded when `tests / mutation` did.
- `tests / nightly-status`: the scheduled slow-run red inherited from main (INBOX line 3); not answered here.

## Unpinned sites

None: the 21 added sites are pinned in e40082d743. The table's mutants were also driven against the R11 tests/features.py block (`mutant_run.py --spec`, the 22 table sites on added lines at 7c3157869f): 21 KILLED, and `NULL` survived. The one survivor is the slope gate's `>=` -> `>` (`ScaleDither.take CMP_BOUND 4dbfdd33`), whose line is unchanged and is already triaged as equivalent in `tests/mutation_ledger/survivor_triage/accuracy.py/ScaleDither.take.CMP_BOUND.4dbfdd33.json`. That was re-measured at the head: no double `r` near exp(+-0.5 ln 1.15) has `math.log(r)` equal to `FOLLOW_SLOPE_MIN * math.log(FOLLOW_ASK_SPAN)` (a `math.nextafter` scan over 100 doubles either side; 0 hits for either sign).

`mutant_run.py --diff` operators outside the table's inventory (no ledger site is generated, so no triage file):
- `accuracy.py:958 CONST_SWAP` and `STMT_DEL` (the `holding` default): equivalent, because `step` assigns `holding` before any read on every path.
- `accuracy.py:1016 CONST_SWAP` (the first pair's number 0 -> 1): equivalent, because pair numbers are compared only for equality and every start follows a void that clears every slot.

## Forward-carry

- Carry 7's measured residue: on a heat-led install with a COP error, the dither costs the house learner its samples on high-level cycles. That is 93 of 671 at 2 °C with departure A, against 32 before it, with the stored value unchanged to four decimals. This bears on tuning the dither (the note's follow-up) and on the closed-loop harness. Re-measure with `dev/audit/harnesses/cop_dither_fabric.py` against its `null_dither0_*` rows at that group's merge base. The lower-floor learner is not reached by this instrument and needs a two-zone driver that does not pin the house scale at its clamp. Carry: R11-INTAKE-R10-RESIDUE
- B2 (the heat-ask dither (c1) and the closed-loop planner harness) is not built. Under B1 the re-priced install still learns nothing; it only stops dithering. The control is `repriced_heat1.2_true_0.8_x672`, which reads pending at both ends; identification needs the heat ask itself moved. The orchestrator's ruling (INBOX line 2) routes it to a new design group, which is not on the roster yet; R11-OUTSIDE-SELF-SETTING-PUMP is carries-open. Carry: R11-INTAKE-R10-RESIDUE

## Friction

n/a: nothing in the policy was unclear or contradictory for this part.

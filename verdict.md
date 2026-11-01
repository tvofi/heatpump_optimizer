Fix review: blocked 08c2477f20bc79d403cba509c0f0f06ae511edfb suite-red: tests/features.py "#1523 class check null control" fails at this head (CI tests / fast red); the re-cut removed the string the check counts

bus-nonce: 08e89cdbf39a70f2a6b8a84302596709

## Round

Round 2 of PR #3050 (R10-CEILING-PROBE). Round 1 blocked e310b8bb3 as metric-gamed. I know the three-round rule: this block goes to the fixer, and round 3 is the last repair before a minimal re-cut and then a split. The block below is two specific items, each a few lines, so round 3 can pass.

Measured head: 08c2477f20bc79d403cba509c0f0f06ae511edfb. `refs/pull/3050/head` still reads that SHA. Merge base with origin/main (92588d581) is df66556f2b20efd0ebd0db321cbcfafd01530dbf. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so my contract is current. I judged from detached worktrees at the head and at the merge base.

## Block

1. **suite-red: `tests/features.py` fails one check at this head, and CI `tests / fast (3.14)` (job 124789209502) is red on it.** The failing check is `FAIL #1523 class check null control: dropping the experiment's consult re-opens exactly its seam  [[]]`, at `1 of 4735 FEATURE CHECKS FAILED`.
   - Cause: the check (tests/features.py:60263-60270) requires `_p5_src_now.count(_P5_CONSULT) == 1`, where `_P5_CONSULT = "else self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY)"`. The re-cut replaced that expression in `_run_system_identification` with `sysid.hold_reason(self._pump_signals, self._learning_frozen(...), ...)`. The count is 1 at the merge base and 0 at this head.
   - I reproduced it on this seat with the unmutated head's full `tests/features.py` (`ev/full_features_head.out`). CI shows the same.
   - The body still quotes `ALL 4717 FEATURE CHECKS PASSED` from 632bd15b9. The re-cut ran each mutant through `features_block.py` only, and `ci_predict.py` printed `no closures, fast, governance or instrument red predicted`, so nothing before the handoff saw this red.
   - Owed: re-spell `_P5_CONSULT` and its replacement so the null control again drops the freeze consult in the new call. For example, replace `self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY)` in the `hold_reason` call with `None`, matched exactly once. The check must still show that only `_run_system_identification` re-opens. Then run the whole `tests/features.py`, not only the block.
   - Owed in `## Red checks`: name `tests / fast (3.14)` and `tests / mutation-autofix` (`skip-measure-failed`) and answer each. Then pin the four sites (`python3 tests/mutation_table.py --pin-killed --base origin/main`) once features is green, or let autofix pin them on the next head. The cheaper detector was the full `tests/features.py`, or the scoped gate the body already cites, run at the re-cut head before the handoff.
2. **metric-gamed: `tests/structure.py`: the re-recorded `max_class_loc` 8049 and `class_excess_loc` 17642 include 5 lines of layout. The move of logic does not earn them.**
   - Layout: the arm call in `async_arm_system_identification` (coordinator.py:10821) puts six arguments on one 125-column line, and the `hold_reason` call hugs its closing parenthesis.
   - Null control, the round-1 method: I re-wrapped only those two added calls normally (`ev/null_rewrap_r2.diff`). The coordinator then reads 8054 and the class excess 17647, which is `FAIL max_class_loc 8054 > 8049 (+5)` and `FAIL class_excess_loc 17647 > 17642 (+5)` (`ev/structure_null_rewrap.txt`).
   - Even the smallest normal wrap, splitting only the 125-column line, gives 8050, which is over 8049.
   - The move is real and pays 5 lines against the base's 8059 / 17653. The body's "-10 ... a move of logic, not of lines" therefore overstates it by 5.
   - Owed: lay the two calls out normally, re-record `tests/structure_budgets.json` at the honest count (8054 / 17647 by my re-wrap, still down from 8059 / 17653, with no row rising), and correct the -10 figure in the body's Figures to the re-taken numbers.

Nothing else blocks. Every other check below held at this head.

## Findings

- `np.percentile(., 90)` in `DrawRange._ceiling_median` survives both the block (`ALL 61 FEATURES BLOCK PASSED`) and the whole `tests/features.py`. The full run printed only the #1523 failure, which is already red at the unmutated head (`ev/mut_median_p90.out`, `ev/full_features_p90.out`). The item-29 pin uses eleven samples at 3.0 kW plus one outlier, so any upper percentile at or below about the 91st reads 3.0. Design item 29 fixes the median, and an upper-quantile accessor would bias the learned top upward by the store's high tail. Add one check in the re-cut that separates the median from an upper quantile, for example nine at 3.0 kW and three at 4.0 kW, which must read 3.0. Carry: R10-CEILING-PROBE
- The `if armed:` -> `if True:` mutant at sysid.py:2468 changes only the log: it logs "armed" on a refusal. Its only pin is the log-line check `arm_from_config logs the armed kind once when it arms, and says nothing of arming when it does not`, which does kill it (1 of 61). That is acceptable: the only behaviour on that line is the log. This needs no code change and is recorded so later seats do not re-raise it as a weak pin. Carry: dismissed: the mutant's only effect is the log the check asserts

## Evidence

- RESULT head 08c2477f20bc79d403cba509c0f0f06ae511edfb (`ev/HEAD.txt`), merge base df66556f2b20efd0ebd0db321cbcfafd01530dbf.
- RESULT structure, merge base -> head (`ev/structure_base.txt`, `ev/structure_head.txt`): `STRUCTURE RATCHET PASSED` at both.
  - Only two rows move: `class_excess_loc` 17653 -> 17642 and `max_class_loc` 8059 -> 8049. `HeatPumpOptimizerCoordinator` goes 8059 -> 8049 and `SystemIdentification` 1065 -> 1064. Every other `ok` line is identical.
  - `tests/structure_budgets.json` moves only those two keys down, plus `recorded_at`. No key rises.
  - With the null re-wrap: 8054 / 17647, a ratchet FAIL against the recorded budgets (Block 2).
  - The fold call at coordinator.py:9756 was already a 300-plus-column line at the base. This PR appends `experiment_s=...` to it. I left that line unwrapped in the null, so 5 is a floor, not a ceiling.
- RESULT archscore at this head, three bases (`ev/archscore.txt`):
  - `--diff df66556f2` (the true merge base): `dS +0.0006 IMPROVES`, coord_footprint 2389 -> 2388.
  - `--diff 2b6bef7453a8`: `dS +0.0006 IMPROVES`, the same.
  - `--diff 14ed135512e3`: `dS +0.0012 IMPROVES`, coord_footprint 2390 -> 2388.
  - The body's `dS +0.0000 NULL` against 14ed13551 was taken at the older head 632bd15b9 and does not hold at this head.
  - The honest figure for this diff is +0.0006 against the merge base df66556f2.
  - The null re-wrap reads the same +0.0006 (`ev/archscore_null_rewrap.txt`), so archscore is not layout-sensitive here, and the move is a real improvement by that instrument.
- Judgement on the move. Moving `arm_from_config` and `hold_reason` to module functions in sysid.py makes the coordinator wiring only, and puts the decision beside the experiment it governs. That is sound.
  - Placing them at module level keeps them out of the over-300-line `SystemIdentification` class. sysid.py already holds module functions of this kind (`step_detached`, `adoption_decision`).
  - No other structure row moves.
  - `_learning_frozen` is now evaluated eagerly, before the mode test. I read it (coordinator.py:6571-) as a pure read of the signals and the room inputs, so the ordering change has no side effect.
- RESULT block baseline at this head: `ALL 61 FEATURES BLOCK PASSED` (`ev/block_head.out`).
- RESULT median mutants (`ev/mut_*.out`):
  - `np.mean`: 1 of 61, the item-29 median check.
  - `np.max`: 2 of 61, the item-29 check and the synthetic pump.
  - a 15 % agreement test in the accessor: 1 of 61, the item-29 check.
  - `np.percentile(.,90)`: 0 of 61, and it survives the whole suite (Findings).
- RESULT `hold_reason` mutants, all killed:
  - mode branch `if False:`: 1 of 61, the ranking check.
  - freeze ranked before mode: 1 of 61, the ranking check.
  - quiet-window term dropped: 2 of 61, the ranking check and the coordinator quiet-window check.
  - whole chain `return None`: 3 of 61.
- RESULT `arm_from_config` mutants, all killed:
  - `ident.config.enabled = True`: 2 of 61, the switch check and the log check.
  - `if armed:` -> `if True:`: 1 of 61, the log check.
  - `return armed` -> `return None`: 2 of 61.
- RESULT coordinator stand-down:
  - `stand_down(why)` -> `abort(why)`: 2 of 61. An armed probe is held with its reason and a started one is aborted.
  - the stand-down skipped (`if False:`): 2 of 61.
  - Each moved function is called in one statement.
- RESULT flat-price null: deleting the flat-horizon refusal fails 2 of 61, `none starts on a flat price` and `flat-price null`.
- RESULT unpinned sites. `ci_predict.py --base origin/main` lists 4 ADDED UNPINNED sites, which match the body's four (`ev/ci_predict.txt`):
  - sysid.py:1385 GUARD_OFF
  - sysid.py:1387 RETURN_DEL
  - sysid.py:2468 GUARD_OFF
  - sysid.py:2473 RETURN_DEL
  - The 72 earlier sites are now pinned by the bot. `probe_step_hours RETURN_DEL` is triaged as equivalent.
  - `ci_predict` predicts no other red, but it did not foresee the features red in Block 1.
  - I killed each of the four with the planted mutants above.
- RESULT finder's harness `dev/audit/harnesses/ceiling_probe.py`, sha1 4c2f42122ea7cf3f3df04aa46eeb4e19b218ac34 (the finder's port), run from the same file at both trees (`ev/harness_base.txt`, `ev/harness_head.txt`). Output is byte-identical to round 1's at both ends:
  - duty: base `None`, head `'space'`.
  - level: base 35/35/35, head 55/38/25.
  - draw arm: flat at both ends.
  - store: absent at the base; at the head `probe samples 12 | learned top 3.0 | window samples at the ceiling 0 | engaged False`.
- RESULT claim files (`ev/claim_diff_main_head.txt`, `ev/claim_*.txt`).
  - The head's claim lines equal parent 1's (570d22c0d). Against main (df66556f2) the same five `coord_*` names are present, each reason extended with R10-CEILING-PROBE. No claim is dropped or added, and none widens beyond its five fixtures.
  - `claims-for: 7.1.0` equals `VERSION` 7.1.0.
  - `card_claimed_drift.txt` is byte-identical to origin/main.
  - `env_drift.py --all df66556f2`: `CLAIMED` on all five (7 leaves each), `NO UNCLAIMED DRIFT: 56 scenario(s) checked`, `NO STALE FIXTURE: 56 committed fixture(s)` (`ev/env_drift_all.txt`).
- RESULT `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched in the three-dot diff. The delivery row `dev/programme/delivery/3050.md` is in the three-dot diff (+1).
- RESULT `git merge-tree --write-tree origin/main 08c2477f2`: exit 0, tree 979663901, clean (`ev/merge_tree.txt`).
- RESULT scoped gate: `tests/closure.py select --diff df66556f2` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out` (`ev/closure_select.txt`). CI's fast lane prints the same.
- RESULT design items re-verified at this head:
  - `CEILING_MIN_SAMPLES = 12`, `CEILING_LAPSE_DAYS = 45.0`, `CEILING_WINDOW = 48`.
  - `learned_max_kw(now_s)` is the raw median with no agreement test.
  - The fold routes on `pending.get("mode") == "system_identification"`, the key added to the existing `_pending_prediction` dict, with no second capture.
  - `_planned_duty` uses `planned_draw_runs(experiment)`, not a 0.05 literal.
  - These are unchanged from round 1.
- RESULT alternating CPU-budget stress, 4 base and 4 head runs on this Linux seat (`ev/stress_alternating.txt`, `ev/stress_*_*.out`): the loop hit this seat's 30-minute background limit and stopped after 3 base and 2 head runs; head run 3 was cut off and runs 4 never started, so this is 3 + 2, not the 4 + 4 the brief asks for. Every completed run reads `ok   no scenario exceeds its own recorded cost by the budget factor` and `ALL 113 STRESS CHECKS PASSED`. The worst scenario, shoulder/tariff+pv+cycle, read 136.4x, 139.5x and 141.3x at the base and 139.4x and 127.5x at the head, against a 268x budget. The two sides overlap within run-to-run spread, a coin flip, with no regression
- RESULT typing: I did not run `typing_ruler.py --mypy` on this seat, which has no `.venv-typing`. CI's `tests / typing` at this head is success.
- RESULT CI at this head, the whole paginated check-run set (`ev/checks_3.txt`, `ev/classify_last.txt`):
  - `tests / fast (3.14)` failure: Block 1, not named in the body.
  - `tests / mutation` failure. `MUTATION TABLE REFUSED -- ... 4 of them added by this diff`, the four unpinned sites, red by construction until mutation-autofix pins them. The body names it (`ev/mutation_job.log`).
  - Still in progress: `tests / closures`, `tests / mutation-pins (1)`, `codeql / Analyze (python)` and `prelude`. I did not wait on `prelude`, which is not a required context.
  - `tests / mutation-autofix` (job 124800000369) failure: `AUTOFIX: skip-measure-failed -- THE REPAIR DID NOT HAPPEN`. No pin commit will come for the four sites. This is likely a consequence of Block 1's red features baseline, but I did not prove that.
  - `pr-contract / pr-contract` (jobs 124800110005 and 124800608460) failure: `PR-BODY: 2 error(s)`. `## Red checks` names neither `tests / fast (3.14)` nor `tests / mutation-autofix`. A third `pr-contract` run (124800971736) and two `gate` runs are still in progress.
  - Everything else is success or skipped.
  - `merge_train.py classify` read WAIT on every poll: `WAIT ... pending: gate red: none` (exit 3) on every poll, the last at the end of this review (`ev/classify_final.txt`). It never exited 0, 1 or 2, so I have no GREEN or RED reading from it
- Round-1 items not affected by the re-cut held: items 29-34, the claim union, the harness at both ends, and the flat-price null.

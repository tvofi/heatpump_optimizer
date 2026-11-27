R11-ARCH-fabric-learner: the buffer cooling fold, the hourly gains fold, the house step, the stored anchors and the re-anchor law's tail leave the coordinator class for `custom_components/heatpump_optimizer/fabric_learning.py`, a learners-seam module with no `homeassistant` import, per the approved design design/R11-ARCH-fabric-learner 221c246ece (ADR-007). It also bounds `PriceShapeLearner`'s two seen-sets in memory, the #3795 remainder this group's roster carry (item 3795-pricelearner) names.

Refs #3795. This body closes nothing: the roster lists #3795 under this group's `issues` and not under its `fixes`. The price-learner remainder named below is built; whether #3795 closes with it is the orchestrator's.

What is built:
- `fabric_learning.py`: `fold_buffer_cooling`, `fold_internal_gains`, `fold_house_heat_loss`, `heat_loss_anchors` (with `house_heat_loss_anchor`) and `reanchor_learned`, each a function of the values it is handed. Moved with them: the six buffer constants, `HOUSE_LOSS_ALPHA`, `HOUSE_LOSS_MAX_STEP`, the trust region, `house_loss_confidence`, the fitted-zone terms, the learned-zone temperature and the zone capacity, with their docstrings and comments (design fixer note 4, item 6a1f0c24). The cut lands as one pull request (note 3, item 6a1f0c23).
- `coordinator.py`: `_async_learn_buffer_cooling`, `_fold_internal_gains`, `_heat_loss_anchors`, `_reanchor_house_heat_loss_scale` and `_async_learn_house_heat_loss` call the module and keep the clock, the freeze question, the baselines, the counters, the applies and the save. `_house_heat_loss_anchor` is deleted, and its two readers in `tests/features.py` are repointed: the stub's alias is dropped and the call reads `_heat_loss_anchors()` (design fixer note 2, item 6a1f0c22). Stored keys, versions and every expression's operands and order are unchanged.
- The two behaviours the design says move: the re-anchor's three log records are emitted by `fabric_learning`'s logger, text unchanged; the gains fold returns a new list. Design fixer note 1 (item 6a1f0c21): `grep -n '_internal_gains_profile' custom_components/heatpump_optimizer/*.py` returns hits in `coordinator.py` only, and each outward read builds a new list (the store payload's `list(...)`, the two rounded comprehensions), so no holder keeps the old list across a fold.
- Carry 0 (item 3795-pricelearner), built: `price_model.py` (commits 29692afa83, 05e00fb4ce, at the previous fire): `_newest_days` bounds `days_seen` and `quarter_days_seen` to `DAYS_SEEN_RETENTION` after a fold that learned and on `restore`; `store_payload` reads the same function. Stated limit, not built: a complete day older than every retained day, offered to a full set, would be folded, pruned and folded again on the next refresh; the one production caller hands the live price list, which carries today and tomorrow (`## Figures`, the caller rule).

Departures from the design note, each raised here for the reviewer and the orchestrator:
- `HOUSE_LOSS_MAX_STEP` is not imported back into `coordinator.py`. After the cut the coordinator reads it nowhere, so the import is a binding nothing in the package loads and `tests/structure.py` refuses it (`unloaded_package_imports` over its budget by one). Paid by moving its readers to the owner: `tests/features.py`'s re-anchor block, the facade check in `tests/entities.py` (the name leaves its list) and `dev/audit/harnesses/r10_dead_rate_limit.py`, which falls back to the coordinator's name at a tree before the cut. The alternative, a budget raise for a dead binding, was not taken.
- The six buffer constants are not imported back either: `coordinator.py` reads none of them after the cut and no test or harness reads them through it.
- The module's gains fold carries main's arithmetic, not the spike's: #3835 deleted the ridge inside the moved lines (D2-s3-11), and the spike at 63adc6a4a1 still had it.
- `fold_buffer_cooling` loses the start-difference gate. Past the gate that refuses a tank that warmed, the start difference is at least the end difference, so the end gate decides alone; the mutant with the start gate off survived every input before the deletion.
- `coordinator.py` drops the eight imports the cut leaves it not reading (three from `const`, five from `thermal_model`).
- The cut's fall reads 47 statements of `coord_footprint` at main 190ffb10c2, the design note's `## Figures` 48. Design §7 calls a fall other than its figure a revision of the note; the one part that differs is gains (11, the note's 12), the fold #3835 shortened. The cut was finished on the dispatch brief's instruction, so whether the note is revised is the orchestrator's to rule. ADR-007 part 4's figure for the round's running budget is this fall, re-read by `score.py --diff` at the merge that lands it.

## Head

`63ae870a7db21cb7ea68826f424778b5bfda4982` is the head, on merge base 190ffb10c230b6beaf77593b2926d55682e37f47 (origin/main at 2026-11-27T04:50Z). 3eb673372f merges origin/main 190ffb10c2 into the previous fire's step ref 25310141cd, so the base carries #3835; the merge was clean. Every figure below was taken at 598dc6269a unless it names another tree; 63ae870a7d adds, over 598dc6269a, the module-map line in `docs/architecture.md`, the deletion of the 22 stale ledger rows, the re-recorded `tests/closures.json`, a re-worded comment in the new test block and the log-flood registry key in `tests/entities.py`; `git diff 598dc6269a 63ae870a7d -- custom_components` is empty.

## Mutation proof

Driver: each mutant replaces one production text in a separate worktree at 598dc6269a, runs its command with `PYTHONPATH=tests/hastub`, then restores the file.

Module mutants, command `python3 tools/audit/seat/features_block.py "# -- fabric_learning: the fabric folds" "# -- \`_record_quiet_comfort_period\`"` (the new block; restored it reads `ALL 12 FEATURES BLOCK PASSED`). All killed; the set is every gate, constant choice and write-back of the five functions, listed in full:

| mutant (`fabric_learning.py`) | failed |
|---|---|
| buffer: `dt_h <` to `<=` the minimum; `>` to `>=` the maximum; `buffer_temp >` to `>=`; that gate `False`; end gate `<` to `<=`; end gate `False`; finite gate deleted; low bound `<` to `<=`; high bound `>` to `>=` | "fabric: each buffer gate refuses past its edge and folds on it" |
| buffer: alpha choice `observed > rate`; `BUFFER_COOLING_ALPHA_UP` 0.03; `BUFFER_COOLING_ALPHA_DOWN` 0.2; `BUFFER_AMBIENT_TEMP` 19 | "fabric: the buffer envelope adopts a lower observation fast and a higher one slowly" |
| gains: elapsed-time gate dropped; interval-start gate dropped; mass gate deleted | "fabric: no interval start, no elapsed time or no thermal mass hands the profile back unseeded" |
| gains: hour off by one; `INTERNAL_GAINS_ALPHA` doubled | "fabric: the gains fold seeds 24 hours at the configured gain and moves the interval's hour" |
| gains: finite gate deleted; a ridge restored (`- 0.01 * (folded[hour] - g0)`) | "fabric: a zero residual leaves a learned hour where it is, and a non-finite one folds nothing" |
| gains: `list(profile)` to `profile` (the in-place write) | "fabric: the gains fold returns a new list and never writes the one it was handed" |
| gains: clip floor -1.0; ceiling without the 0.05 kW floor; no clip | "fabric: the gains fold clips an hour to [0, three times the configured gain], floored at 0.05 kW" |
| house: two-zone terms branch deleted; trust region 1.0; alpha doubled | "fabric: the house step is learner_newton_step on the fitted zone's terms" |
| anchors: ratio dropped from the two-zone total; two-zone branch `False`; lower anchor's `None` inverted; rounding to 3 places | "fabric: the stored anchors in one zone and in two" |
| re-anchor: void zeroing deleted; zeroing the scale count only; the ratio count only; `void=False`; `step=0.0`; gate returns `learned`; ratio-reset zeroing dropped; scale-reset zeroing dropped; old scale returned; old ratio returned; confidence pair swapped | "fabric: the re-anchor is None below its gate, zeroes evidence a later basis voids, and resets with the count" |
| `house_loss_confidence`: `max(0, ...)` dropped | "fabric: confidence is 0 with no evidence or a negative count, and one alpha after one sample" |

Coordinator mutants, command `python3 tests/features.py` (the whole script: the class's callers are driven by blocks this diff does not edit). All killed:

| mutant (`coordinator.py`) | failed (first of each) |
|---|---|
| buffer: a refused fold replaced by `(0.0, rate)` instead of the return | 8 checks, "an interval under 0.15 h is too short to read a decay from" |
| buffer: applies `observed` for `rate` | "a tighter-looking interval is taken 12.5x harder than a leakier one" |
| buffer: the apply dropped | 4 checks, "buffer cooling learner: a sample a true hour on across the fold is accepted" |
| buffer: previous and current temperature swapped | 4 checks, the same first |
| re-anchor: `if learned is None` never taken | `AttributeError` at `learned.scale_samples`, the script stops |
| re-anchor: the refusal returns `True` for `swapped` | 5 checks, "and a second load over the reseeded configuration re-anchors nothing" |
| re-anchor: the counters' write-back dropped | 7 checks, "an inexpressible measurement resets, not clips onto a bound" |
| re-anchor: the counters swapped | 4 checks, the same first |
| re-anchor: stored basis handed as `None` | 2 checks, "adding a power meter re-anchors both learners at zero confidence" |
| re-anchor: the stored lower nameplate handed as 0.0 | 7 checks, "an options reseed of both zones keeps each zone's learned heat loss" |
| gains: the assignment dropped | `TypeError` on the unseeded profile, the script stops |
| gains: residual sign flipped | 6 checks, "a warm evening hour learns extra gains, tethered under the cap" |
| house: residual sign flipped | 3 checks, "the extracted Newton step leaves the learned scale unchanged" |
| house: scale handed as 1.0 | 2 checks, the same first |
| anchors: ratio handed as 1.0 | 8 checks, "an options reseed of both zones keeps each zone's learned heat loss" |
| anchors: `earned` handed as `False` | 3 checks, "the first fold that replays a measured heat earns the measured_heat basis" |

`price_model.py`, at the previous fire (05e00fb4ce, its lines unchanged since: `git diff 05e00fb4ce 598dc6269a -- custom_components/heatpump_optimizer/price_model.py` is empty): ten mutants against the six `#3795` checks, all killed (each prune in `fold`, the `if learned` predicate, each prune in `restore`, newest to oldest, the constant at 89 and at 91, `_newest_days` as the identity, the payload unbounded).

## Null control

- Failing first: at bbff60038f (the test commit, no module) the new block stops at `ImportError: cannot import name 'fabric_learning' from 'heatpump_optimizer'`. At 29692afa83's parent three of the six `#3795` checks fail (the constant, the window+N fold, the prune on load) and three pass as controls.
- The whole script at both ends, frozen worktrees: `PYTHONPATH=tests/hastub python3 tests/features.py` reads `ALL 6272 FEATURE CHECKS PASSED` at 190ffb10c2 and `ALL 6290 FEATURE CHECKS PASSED` at 598dc6269a; the 18 added are the 12 fabric and 6 `#3795` checks. No check that passes at the base is absent at the head: `comm -23` of the two sorted `ok` name lists prints nothing.
- Score mechanism: each part of the cut alone is inadmissible (`## Figures`, the arm's `--each`), so the fall is the whole cut's and not the module's presence.
- Retention probe's own null: `--null` (a restart per day) reads slope 0.00 at the base, where the baseline arm reads 2.00.

## Figures

- `python3 tools/audit/archscore/score.py --diff 190ffb10c230` at 598dc6269a: `Architecture score: dS +0.0270 IMPROVES`, `coord_footprint 2533 -> 2486`.
- The design's arm, stated without a runnable command because its three files are not in this tree: the spike's arm and module exported from design/R11-ARCH-fabric-learner 63adc6a4a1, the plan's prototypes helper from plan/r11 819aa2e354 placed at its plan path, run with `--at origin/main` at 190ffb10c2 on 2026-11-27. It read: no anchor stop, `coord_footprint 2533 -> 2486`, dS +0.0270. `--each`: buffer 16, gains 11, anchors 3, re-anchor 15, house 2, each alone inadmissible (`dead_members 0 -> 4`; all but buffer also `duplication_copies 11 -> 12`). The design's `## Figures` read 48 with gains 12 (the last departure above).
- `python3 tests/structure.py` at 598dc6269a: `STRUCTURE RATCHET PASSED`. Re-recorded downward in 598dc6269a: `class_excess_loc`, `max_class_loc`, `module_excess_loc`, `functions_cc_over_15`; no budget rises (`git diff 190ffb10c230 598dc6269a -- tests/structure_budgets.json`).
- Acceptance harness `dev/audit/rounds/round11/D7/s2/m3_learner_freeze.py` (sha1 775462488a), `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s2/m3_learner_freeze.py`: `RESULT contaminated_ingest=0 count` at 190ffb10c2 and at 598dc6269a, and `cmp` of the two full outputs reports them identical. It reads flat because #3835 already closed its three cells and this cut changes no freeze answer; `--perturb` reads 0 at both ends too. The companion that does move under a perturbation of the moved code is the mutation table: `BUFFER_COOLING_ALPHA_UP` at 0.03 fails the envelope check (the design's named null control).
- Finder's probe `dev/audit/rounds/round11/sweep/N-unbounded-retention/D14/retention/probe_price_days.py` (sha1 929db15f6c), `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/sweep/N-unbounded-retention/D14/retention/probe_price_days.py`: `retained_keys_slope` 2.00 keys/day at 190ffb10c2, 0.00 at 598dc6269a; `--null` 0.00 at both.
- `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_dead_rate_limit.py` at 598dc6269a: `binds=0`, digest 3187402b35.
- Callers of the price learner's fold, rule `grep -n "_price_learner.fold(" custom_components/heatpump_optimizer/*.py`: one, in `coordinator.py`, handed the live price list.
- Scoped gate at 63ae870a7d, clean worktree, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=190ffb10c230b6beaf77593b2926d55682e37f47 ./tests/run.sh`: `MODE: SCOPED`, exit 0, no script failed; `tests/features.py`, `tests/entities.py`, `tests/finite_boundary.py`, `tests/boost_drift_replay.py` and the golden lane's drift comparison against the merge base (`tests/env_drift.py --all`) are among those it ran, so no golden fixture moved. Both claim files are byte-identical to the merge base: `git diff --quiet 190ffb10c230 63ae870a7d -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt` exits 0.
- Closures: `tests/derive_closures.sh --scripts-from` over the scripts the rule `jq -r '.closures | to_entries[] | select(.value | index("custom_components/heatpump_optimizer/coordinator.py")) | .key' tests/closures.json` prints, merged `--partial`; `tests/entities.py` merged with `--allow-failures` (commit 63ae870a7d's message says why). The full prepr run this needed is the one at 598dc6269a: a new production module is in no closure until recorded.

## Unpinned sites

Every site below is a line this diff adds under `custom_components/`. The `fabric_learning.py` sites are the moved statements: their statements were pinned as killed by `tests/features.py` at their `coordinator.py` anchors, in the 22 rows this diff deletes as stale, and the hand mutants of `## Mutation proof` kill the gates, clips and write-backs again at the new anchors. None was pinned on this head (`--pin-killed` was not run here), so each reads unmeasured by the ledger until `mutation-autofix` pins it.

- `custom_components/heatpump_optimizer/coordinator.py:5483 GUARD_OFF` on `if learned is None:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:5538 GUARD_OFF` on `if fold is None:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:45 CONST` on `BUFFER_COOLING_ALPHA_DOWN = 0.25`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:46 CONST` on `BUFFER_COOLING_ALPHA_UP = 0.02`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:48 CONST` on `BUFFER_COOLING_MAX_SAMPLE_HOURS = 3.0`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:50 CONST` on `BUFFER_AMBIENT_TEMP = 20.0`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:65 CONST` on `HOUSE_LOSS_ALPHA = 0.02`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:79 CONST` on `LEARNER_TRUST_REGION = 0.5`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:93 CLAMP_DROP` on `return 1.0 - (1.0 - HOUSE_LOSS_ALPHA) ** max(0, int(samples)`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:93 RETURN_DEL` on `return 1.0 - (1.0 - HOUSE_LOSS_ALPHA) ** max(0, int(samples)`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:106 GUARD_OFF` on `if params.two_zone_enabled:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:108 RETURN_DEL` on `return params.heat_loss_coefficient, params.room_thermal_mas`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:115 GUARD_OFF` on `if params.two_zone_enabled:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:117 RETURN_DEL` on `return state.room_temperature`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:122 RETURN_DEL` on `return house_loss_terms(params)[1]`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:135 CMP_BOUND` on `if dt_h < BUFFER_COOLING_MIN_SAMPLE_HOURS:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:135 GUARD_OFF` on `if dt_h < BUFFER_COOLING_MIN_SAMPLE_HOURS:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:137 CMP_BOUND` on `if dt_h > BUFFER_COOLING_MAX_SAMPLE_HOURS:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:137 GUARD_OFF` on `if dt_h > BUFFER_COOLING_MAX_SAMPLE_HOURS:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:139 CMP_BOUND` on `if buffer_temp > previous_temp:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:139 GUARD_OFF` on `if buffer_temp > previous_temp:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:145 CMP_BOUND` on `if end_delta < BUFFER_COOLING_MIN_DELTA:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:145 GUARD_OFF` on `if end_delta < BUFFER_COOLING_MIN_DELTA:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:151 GUARD_OFF` on `if not np.isfinite(observed):`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:154 CMP_BOUND*2` on `if observed < low or observed > high:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:154 GUARD_OFF` on `if observed < low or observed > high:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:159 CMP_BOUND` on `if observed < rate`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:162 RETURN_DEL` on `return observed, (1.0 - alpha) * rate + alpha * observed`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:180 CMP_BOUND` on `if previous_time is None or dt_h <= 1e-6:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:180 GUARD_OFF` on `if previous_time is None or dt_h <= 1e-6:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:183 CMP_BOUND` on `if capacity <= 1e-6:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:183 GUARD_OFF` on `if capacity <= 1e-6:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:189 GUARD_OFF` on `if not np.isfinite(y):`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:196 CLAMP_DROP*2` on `np.clip(g, 0.0, INTERNAL_GAINS_MAX_FACTOR * max(g0, 0.05))`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:198 RETURN_DEL` on `return folded`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:226 GUARD_OFF` on `if params.two_zone_enabled:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:231 RETURN_DEL` on `return float(params.heat_loss_coefficient)`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:274 GUARD_OFF` on `if pair is None:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:276 GUARD_OFF` on `if void:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:284 GUARD_OFF` on `if ratio_reset:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:291 GUARD_OFF` on `if scale_reset:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/fabric_learning.py:305 RETURN_DEL` on `return HeatLossLearned(new_scale, scale_samples, new_ratio,`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/price_model.py:99 CONST` on `DAYS_SEEN_RETENTION = 90`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/price_model.py:463 GUARD_OFF` on `if learned:`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/price_model.py:492 RETURN_DEL` on `return set(sorted(days)[-DAYS_SEEN_RETENTION:])`: unmeasured by the ledger at this head. Carry: dismissed: pinned by mutation-autofix

## Red checks

- `mutation` at 63ae870a7db2: red by construction on the 45 sites under `## Unpinned sites`, predicted by `tools/pr/ci_predict.py`; `mutation-autofix` pins killed sites after the push. Cheaper detector: none exists, the pin is written by the job that measures the kill, and it runs only once a pull request does.

## Forward-carry

none

## Friction

none

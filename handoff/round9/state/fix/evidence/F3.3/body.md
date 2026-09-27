<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Round-9 fix F3.3: the defrost, price-shape and peak-tracker stores load only what their own update paths write, cell by cell, and one unreadable row of a price or irradiance feed drops that row, not the feed. Open-Meteo's resolution is the dominant gap, not the smallest. Part of #1647 (P1). Part of #1644 (P2). Fixes #1680 (N-min-gap). Part of #201. Findings D1-s4-01, D1-s4-03, D1-s5-02, D1-s5-03, D1-s5-04. The P1 and P2 RCA seats ran beside F3.1; their barriers are F1.6's and F1.11's, and the declared-domain table (card C1) is F9.3's. N-min-gap has no RCA (N=1).

- **D1-s4-01 (P1, weakened to its finite out-of-range cells).** `DefrostDerate.from_dict` reads every grid cell by cell. A duty cell outside [0, 1] (`observe_duty`'s gate), a negative count, a bool or an unreadable value restarts only its own bucket unmeasured, which `_trusted` reads as no evidence, and logs one warning. Before, a stored duty of 1e300 or -0.5 loaded and pinned its bucket at `DERATE_MIN` for good.
- **D1-s4-03 (P1).** One unreadable cell in a v2 store now costs its bucket, not all twelve, and a v2 store is never labelled a pre-v5.3.0 upgrade: `migrated` is set only when the store has no measured half at all. A v2 store whose measured half is unreadable as a whole restarts it with a warning. The D1-02 accuracy fixture in `tests/features.py` held a `duty` grid without `duty_counts`, a shape no build ever wrote (both keys arrived together in v5.3.0, `64a54195`); it gains the counts, because under the new loader that shape is a corrupt store and warns. This is a design choice the check encodes.
- **D1-s5-02 (P1).** `PriceShapeModel.from_dict` checks each profile against the cone its update path keeps: every bin positive and the largest at most `SHAPE_MAX / SHAPE_MIN` (a quarter hour: `QUARTER_FACTOR_MAX / QUARTER_FACTOR_MIN`) times the smallest. EWMA and renormalisation both preserve that cone, so an honest store never leaves it and loads unchanged; a profile outside it goes through `observe_day`'s own clip and renormalisation, with a warning. `residual_var` above the new `RESIDUAL_VAR_MAX` (`(SHAPE_MAX / SHAPE_MIN) ** 2`, the largest squared residual two bins of that cone allow) restarts at zero, and `days` and `quarter_days` are floored at zero. `PeakTracker` drops a negative stored peak as it drops a non-finite one, and restarts an open window whose sum, sample count, weighted sum or weight is negative or whose factor is outside [0, 1]. The loader is split into two module helpers, `_stored_rows` and `_stored_counts`, which is what pays for the gates in the structure budgets (below).
- **D1-s5-03 (P2, weakened to the entity seam).** `_raw_value`, `_entries_by_day`, `apply_price_adjustments` and `open_meteo._parse_block` catch `OverflowError` with the other conversion failures, so a JSON integer beyond a double drops its own row. Only the entity seam is reachable in production (orjson refuses such an integer over HTTP); the other three sites share the parse and cost one tuple entry each.
- **D1-s5-04 (N-min-gap).** `_parse_block` takes the most common positive gap, the smaller on a tie. The smallest-gap rule's reason still holds: a missing sample does not double the resolution. A three-sample series with one stray stamp still ties to the smaller gap; that edge is left, since a series that short covers no horizon.

Stored fields bound here and the domain each update path enforces (for F9.3's table, card C1; also carried in `.claude/workflows/carry-1647.json`): `DefrostDerate.duty` [0, 1]; `duty_counts`, `duty_events`, `counts` integers ≥ 0; `factors` finite, clamped to [`DERATE_MIN`, `DERATE_MAX`] (unchanged). `PriceShapeModel.shapes` and `quarter_factors` (per hour) in the cone above; `residual_var` finite in [0, `RESIDUAL_VAR_MAX`]; `days`, `quarter_days` ≥ 0. `PeakTracker.peaks` finite and ≥ 0; the open window's `window_sum`, `window_samples`, `window_wsum`, `window_weight` ≥ 0 and `window_factor` in [0, 1].

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Head

Code head `6ea9e6b4c3f70bdc3775468c692d9e6c976821a5` on `handoff/r9-f3-stores-3-v2`: the reviewed code head `585db36e` plus two commits answering the fix review of #1717 (PR head `184ca64d`), a direct price-loader check (`4da36f66`) and the 21 mutation-ledger pins (`6ea9e6b4`). No production line changed. Figures below were measured on `585db36e` or on `f9f12383`, which differs from it only by the carry file, except where a line names `6ea9e6b4`. Merge base `92bce7c4` (`origin/main` when the branch was cut, 2026-09-27T09:50Z). The resume note and this body ride in a transport commit stacked above the code head and are not part of the pull request.

## Mutation proof

Each mutant edits one fix predicate in the tree at the code head, runs this PR's `tests/features.py` section alone (extracted verbatim with the file's header), and restores the file. Unmutated: `ALL 6 F33 PASSED`. Every mutant is killed:

- M1 the duty cell's [0, 1] gate returns True: the D1-s4-01 check.
- M2 a grid with any bad cell dropped whole (the old all-or-nothing read): the D1-s4-01 and D1-s4-03 checks.
- M3 the unreadable-v2 branch removed, so it falls to the upgrade label: the D1-s4-03 check.
- M4 `_in_domain`'s cone test to `if True:`: the price-shape check.
- M5 the `RESIDUAL_VAR_MAX` bound dropped: the price-shape check.
- M6 `_stored_counts`' floor at zero dropped (days and quarter days share it, so the draft's separate M7 folded in): the price-shape check.
- M8 the negative-peak drop removed: the peak check.
- M9 the open-window domain reset disabled: the peak check.
- M10 to M13 `OverflowError` removed from `_raw_value`, `_entries_by_day`, `apply_price_adjustments` and `_parse_block`, one at a time: the D1-s5-03 check, each alone.
- M14 `_parse_block` back to `min(gaps)`: the D1-s5-04 check.

- M15 `_stored_rows`' `return None` after its warning deleted, and M16 `_stored_counts`' shape guard to `if False:` (the two survivors the fix review found under `mutation_table.py --pin-killed`, because every other check drives its payload through the store's scrub): the direct price-loader check, each alone.

Runner and output: `$EV/mut.py`, `$EV/mutants_v2.txt` (15 of 15 killed at `6ea9e6b4`), `$EV/quick.sh`, where `EV=/mnt/project-files/audit-r9/fix/evidence/F3.3`. `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --scope changed --base 92bce7c4 --pin-killed --jobs 4` at `4da36f66` (`$EV/pin.log`): `PIN KILLED: 21 pinned, 0 left unpinned`; its null control `defrost.py:88 NULL_COMMENT` survived every driver. The pins are commit `6ea9e6b4`.

## Null control

- Each finder harness's own control arm reads the same at the merge base and the head: `store_fuzz.py` `healthy_null_control_stuck` 0 and `sibling_factors_stuck` 0; `store_domain_fuzz.py` `price_model_control_invalid` and `peak_tracker_control_invalid` 0 of 1; `price_huge_int.py` control rows 24, 24 and 72; `open_meteo_resolution.py` `healthy_none_steps` 0 of 192.
- The new checks' controls: a healthy defrost store, a learned price model and a real peak tracker each round-trip through their loader to exactly their `as_dict()` and log no warning; a v1 defrost store is still labelled migrated; a missing Open-Meteo sample still infers one hour.
- `store_fuzz.py`'s `flow_bias_bad` reads 6 at both ends. It is not this PR's: F4.1 (#1704, `3e9f1878`) raised `FlowCurveBias`'s stored-bias ceiling to `FLOW_SUPPLY_MAX_C` on purpose, and the harness still bounds it at `FLOW_BIAS_CLAMP_K`; at the finder's baseline it read 0.

## Figures

Harnesses from evidence commit `79aa98ec`, run from an export (`$EXPORT/tools/audit/round9/...`) with `PYTHONPATH=tests/hastub` and the pinned `tests/requirements-ci.txt` stack on Python 3.14, at merge base `92bce7c4` and at `f9f12383`. Outputs `$EV/base/` and `$EV/head/`.

- `$EXPORT/tools/audit/round9/D1/s4/store_fuzz.py` (sha1 `57fd446f0fc9d938a5987673a95553d6ef9b9ac8`): duty_targeted_stuck 53 → 0 of 250 (42 → 0 pinned at `DERATE_MIN`, 53 → 0 silent); stuck_duty 11 → 0; v2_one_bad_cell_flagged_migrated 226 → 0 of 250; v2_one_bad_cell_measured_buckets_discarded 2712 → 250 (each payload now loses only its one bad bucket); nan_bucket_factor_after_200_zero_folds 0.5500 → 1.0000.
- `$EXPORT/tools/audit/round9/D1/s5/store_domain_fuzz.py` (sha1 `d3a6deca5893b93e1b09829506232db405344702`, default `--n 300 --seed 9`): price_model_silent_invalid 11 → 0 (next_still_invalid 9 → 0); peak_tracker_silent_invalid 8 → 0 (2 → 0); crash 0 at both.
- `$EXPORT/tools/audit/round9/D1/s5/price_huge_int.py` (sha1 `859ba7b6c6b6cedc7571a6cdda69ebb6528bad8e`): entity_huge_int_rows 0 → 24; tibber_huge_int_rows 0 → 24; open_meteo_huge_int_rows 0 → 72.
- `$EXPORT/tools/audit/round9/D1/s5/open_meteo_resolution.py` (sha1 `87d9687ed935f4b069a8b655a0e79e496159e949`): stray_1min_none_steps 192 → 0 of 192; stray_5min 192 → 0; stray_30min 94 → 0.
- This PR's `tests/features.py` section, extracted as above (`$EV/quick_base.txt`, `$EV/quick_head.txt`): at the merge base `6 of 6 F33 FAILED`, each check naming the defect (e.g. `tail 0..1.47e+300`, `peaks=[4.25, -50.0]`, `OverflowError` at all four parsers, resolution 60 s and 1800 s); at the head `ALL 6 F33 PASSED`.
- `python3 tests/structure.py` at the code head: `STRUCTURE RATCHET PASSED`, with no budget moved or re-recorded. The first draft of the price loader breached `classes_over_300` (12 > 11, `PriceShapeModel` 314 lines) and `functions_cc_over_25` (9 > 8, its `from_dict` at cc 44); the two module helpers pay both.
- Scope: `python3 tests/closure.py select --diff 92bce7c4 --workdir "$D"`: `MODE: SCOPED -- 23 script(s) run, 3 scoped out`.
- Scoped gate `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=92bce7c4 ./tests/run.sh` at `f9f12383` (`$EV/gate.log`): `25 TEST SCRIPT(S) PASSED; 3 SCOPED OUT AND NOT RUN`, rc 0, `tests/stress.py` included; among them `tests/features.py` `ALL 3458 FEATURE CHECKS PASSED`, `tests/entities.py` `ALL 1975 ENTITY CHECKS PASSED`, `tests/finite_boundary.py` `ALL 51 FINITE BOUNDARY CHECKS PASSED`. The golden drift check passed with no claim, and both claim files are byte-identical to main.
- At `6ea9e6b4`: `tests/features.py` `ALL 3459 FEATURE CHECKS PASSED` (the section now `ALL 7 F33 PASSED`), `tests/entities.py` `ALL 1975 ENTITY CHECKS PASSED`, `tests/structure.py` `STRUCTURE RATCHET PASSED`, scope unchanged at `MODE: SCOPED -- 23 script(s) run, 3 scoped out`.
- `tools/audit/prepr.sh` at `585db36e` (`$EV/prepr_try.txt`): `clean  no refusal`.
- `node .claude/workflows/brief_lint.mjs .claude/workflows/carry-1647.json`: `TOTAL: 0 error(s) across 1 file(s)`.

Class enumerators (`fixer.md` step 8), each run from an export of its sweep commit placed at the tree's own path, at the merge base and at `f9f12383` (`$EV/P1_*.txt`, `$EV/P2_*.txt`, `$EV/S6_*.txt`, `$EV/seamrules_*.txt`):

- P1, `enumerator.py --list` @ `053c4869ad` (sha1 `59212b6b10260d213d285dbdaa920f5a871c32a2`): numfield_seams 28 and numfield_unguarded 13, dtnaive_seams 4 and dtnaive_instance 1, at both ends; the lists differ only by `tariff.py`'s line (389 → 392). Dispositions: `PeakTracker.from_dict` `_window_samples`, closed in this diff by the open-window domain reset (the scan reads only `isfinite`-named checks, and an `int` needs none, so it keeps listing it); comfort_learning `stored_configured`, `learned_weight`, `evidence`, `overrides` and legionella `attempt_peak`, F1.6's instances; `flow_lift` `bias_k`, guarded (the sweep's disposition); `freq_control` `decile`, guarded by F3.2's range check; `curve_learning` `comfortable_days`/`resets`, `dhw_learning` `cooling_samples`, `snapshots` `_bias_days`, `wear` `lifetime`, not applicable (`int()` counters, the sweep's rule); `accuracy.py:78` DTNAIVE, not applicable per the sweep, F1.6's stored-instant stage. The three P1 seams of this PR's findings (`defrost.py` duty, `price_model.py` residual_var, `tariff.py` window_factor) are not returned at either end: each already carried an `isfinite` check or cast the scan does not name, so the finders' harnesses above are their measurement.
- P2, `enumerator.py --seams` @ `c44e7bcd60` (sha1 `d266a4052de977686cd306ae51ae77d4a710ed51`): 29 seams at both ends (11 dhw_enabled, 2 two_zone_enabled, 16 wood_furnace_on), identical output (`diff` empty); all are config-fact seams of other P2 instances and none is in this diff's files. D1-s5-03's own seam rule, `grep -n -A3 "float(raw\|float(raw_v\|float(total" custom_components/heatpump_optimizer/price_model.py custom_components/heatpump_optimizer/open_meteo.py`: three sites at both ends, each catching `OverflowError` at the head; `apply_price_adjustments` (`float(entry.get("total"...`, which the rule does not match) is closed too. A wider scan outside the rule, every `float(` within two lines above `except (TypeError, ValueError):` in the package, returns 29 sites in 15 other files; none is in this lane, and they are reported to the orchestrator as a lead rather than dispositioned here.
- N-min-gap, `enumerate.sh` @ `6b65c9c4a8` (sha1 `bfedc654f2eb086fbbfe09d076a4371ffad74800`): four lines at both ends. `open_meteo.py` `resolution = timedelta(seconds=min(gaps))` is closed in this diff (the head line takes the most common gap); `config_flow.py:2394`, `:3798` and `prefill_offer.py:100` are not applicable (device-identity resolution, a name collision), as the sweep lists them.

## Red checks

`tests/features.py` is red on this branch's own failing-test commit `da2e0c14`, by design (fixer.md step 2: failing test first); no CI check has run on this branch. Cheaper detector: none; the pin is the detector.

## Forward-carry

`.claude/workflows/carry-1647.json` (F9.3, card C1: the defrost, price-shape and peak-tracker domains this PR bound, to declare from the tree). Round 9's roster is not in this tree, so it is the stage's in-tree carry file. The P2 overflow lead above goes to the orchestrator.

## Friction

none

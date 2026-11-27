R11-SEAM-cycle-reporting: how a failure is reported. A persisting save failure is reported once per outage, and the update cycle's generic arm is latched. A broad handler that swallowed an exception now leaves a record. `set_away` refuses an unparseable return time. A target or comfort-weight change publishes a new context, which the held early cut-off reads at each reading. The coordinator carries the typed entry, and the strict-typing row is re-measured. Findings: D1-s3-05, D1-s3-06, D1-s3-07, D10-s1-01, D7-s2-03, D10-s3-01, D10-s3-02. Plan: ADR-003 and ADR-008 (`dev/audit/rounds/round11/PLAN/` at `plan/r11` dbdc1d95fef3). Closes: none (the group's roster entry lists no issue).

What changes, per finding:

- **D1-s3-05.** `store.save_held(owner, what, save)` is the one persist wrapper. A failing save, or a payload builder that raises (built inside `save`), is held through `log_latch.log_held`: an ERROR with the traceback when the outage starts, DEBUG while it holds, and `Resolved` on the first save that lands. All 18 persist handlers route through it. That is the 17 the finding named plus `room_record._persist`, added since. The owner is the kept store, or the coordinator where `away`, `boost` and `pump_arbiter` build a store per call. The records of `duty_switch` and `room_record` are unhashable dataclasses and cannot key the latch. `duty_switch._persist` and `room_record._persist` keep their dirty marks on a failed save through `save_held`'s return value.
- **D1-s3-06.** Both update paths fail through `_fail_update_held`, which holds the error on `hass` under `update_failed_<entry_id>`, and each path's success clears it. The latch is not keyed on the coordinator: a setup retry builds a new coordinator, and a coordinator-keyed latch logged every retry. The finding names that path (`_async_first_refresh_light`), and M2b below pins it.
- **D1-s3-07.** The seven handlers record what they swallowed at DEBUG with the traceback. So do the evidence fallbacks the finding's seam rule also returns: `_stored_fuse_advisor`, `_track_curve_comfort`, `_raise_cop_issue`'s monthly estimate, `_solver_status`, `_multi_start_minimize`'s skipped candidate, `config_flow._omit_unstored_computed`, `config_flow._prefilled_values` and both of `diagnosis.attribute`'s simulation fallbacks. No behaviour changes.
- **D10-s1-01 (ADR-008 part 3).** `away.parse_return_time` is the one public return-time parser, with `away.clears_return_time` naming the clearing spellings. `services.handle_set_away` parses the value before any write. A value that neither clears nor parses is refused with `ServiceValidationError` `away_invalid_return_time`, which `strings.json` and the three translations carry. The coordinator and the datetime entity read the public parser. The mutation-ledger pin on `_parse_return_time` is renamed with it, and `prepr.sh`'s stale-pin self-test greps either spelling.
- **D7-s2-03 (ADR-003 part 1).** `CoordinatorContext.publish_config` publishes a new context whose config is a replaced `OptimizationConfig`. `async_set_target_temperature` and `_apply_comfort_weight` publish through it, so no statement edits a published config in place. ADR-003's stale-holder acceptance led to a change in `early_cutoff`. `arm` stored the handed config in `held.wiring` for the rest of the cycle. `ArbiterInputs` now carries the live config (`opt_config`), which the coordinator's `arbiter_inputs` builds afresh on each read. `early_cutoff.threshold` reads it from the inputs at each reading, and `arm` and `CutoffInputs` hold none. Two test fixtures that armed the cutoff with a config (`tests/dst_checks.py`, `tests/features.py`'s `_EcCoord`) now hand it on their inputs.
- **D10-s3-02.** `HeatPumpOptimizerCoordinator` annotates `config_entry: HeatPumpOptimizerConfigEntry`. `tests/doc_claims.py` gains `untyped_coordinators`, which censuses every `DataUpdateCoordinator` subclass, with a self-test of a bare and a missing annotation and two null controls.
- **D10-s3-01.** `threadpoolctl` ships no `py.typed` and has no stub package, so `quality_scale.yaml`'s strict-typing row is `todo`, with the reason in its comment. The manifest carries the tier `tests/entities.py` derives from the rows, which is `gold`. The other two options were not taken. Dropping the requirement turns off the BLAS thread limit on the Pi, and a typed equivalent does not exist. Release notes owe one line: the manifest's quality scale is gold until `threadpoolctl` is typed.

Alternatives not taken:

- **A per-site `try`/`else` around `log_held` at each of the 18 handlers.** It would have been about 70 lines and eighteen copies of one rule. `save_held` beside `load_mapping` is the store edge's one owner.
- **The store itself as the latch owner everywhere.** `away`, `boost` and `pump_arbiter` build a store per call, so their latch would have died with each call.
- **A callable `opt_config` handed to `early_cutoff.arm`.** This is a second live read beside `inputs`. A test could not drive the coordinator's lambda, which sits inside `_apply_action`.
- **Writing `self._opt_config = replace(...)` through the `_hub` facade.** It makes `_opt_config` an attribute written by the learning seam, and measured `coordinator_attrs` +1, `coordinator_multiassigned_attrs` +1 and `seam_cut_total` +3. `CoordinatorContext.publish_config` moves no row, beside the existing `publish`. `_apply_comfort_weight` calls it unbound, `CoordinatorContext.publish_config(_ctx_of(self), self, ...)`. The `getattr(self, "_ctx", self).publish_config(...)` spelling measured `seam_cut_total` +1, because the seam table reads it as an attribute load on the coordinator. The two spellings make the same call.

## Head

`bf1ca4c8a9bb6727da8d3916073b945798544a8e` merges the authored code head `f7b44e69ec7bbae058edf98f2cecee90b24cdd53` and then merges origin/main `ef797d7940` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`f7b44e69ec7bbae058edf98f2cecee90b24cdd53` merges origin/main `ef797d7940` into the PR head `36417ab5fa`. The one conflict was `dev/audit/config/scopes.json`. This PR's `361cc26c97` and main's `7df39f34` made the same D5 seat `s7` re-cut under `ledger.max_units` 4500. In this PR, `s7` became `tests/features.py` and `s8` gained `tests/f{i,r}*`. On main, `s7` is `tests/fe*` and `s8` is `tests/{a,b,c,d,fi,fr,g}*`. Both cuts put the same files in each seat, so main's hunk already carries the PR's change and the file is taken whole from main. No other file conflicted, and the merge differs from main only in the PR's own files, less `scopes.json` (`git diff --name-only ef797d7940 f7b44e69ec` is the PR's three-dot list without it). Resolution delta for review: `git diff 36417ab5fa f7b44e69ec -- dev/audit/config/scopes.json`, read against main with `git diff ef797d7940 f7b44e69ec -- dev/audit/config/scopes.json` (empty). At the merge: `python3 -I tools/audit/check_scopes.py --self-test --repo .` `SELF-TEST passed (every perturbed scope refused)`; `--ref HEAD --repo .` rc 0, `ok D5 mode=cells seats=10 universe=945` with `s7:1f/0loc/4329u`, `s8:49f/0loc/4044u`, `s9:69f/0loc/3916u`; `python3 -I dev/audit/harnesses/owner_only_channel.py` `RESULT arms=48 failed=0`, `OWNER-ONLY CHANNEL HELD`. Prepr at the merge, scoped (`PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh`): `PRE-PR: f7b44e69ec7bbae058edf98f2cecee90b24cdd53 00000000000000000 rc=0 elapsed=100s`.

`36417ab5fab69c3932eda49da9d79ecd956e621b` merges the authored code head `361cc26c97d27d423469e8e9d66dc3b9a3831e10`.

`361cc26c97d27d423469e8e9d66dc3b9a3831e10` is the code head of this repair: one commit on the PR head `2643502f3809e9d688230e578a08c411439d2a9a`, measured against merge base `fd93aa3e9b161e92ead26e04ba8311b3fc0fc7e5` (`origin/main` at 2026-11-26T23:49Z). It changes only `dev/audit/config/scopes.json`. At `2643502f38`, `governance / instrument-self-tests` (job 140209372226) was red on two steps this diff reaches, and both had the same cause. This PR's `tests/features.py` comments took D5's seat `s7` (`tests/f*`) to 4513 of `text_ledger.py`'s D5 units. The cap is `ledger.max_units` 4500, and `check_scopes.py` refuses a seat over it:
- "Show a planted owner-only canary …": `dev/audit/harnesses/owner_only_channel.py` read `FAIL SCOPES null: the planned shape … passes check_scopes`, `RESULT arms=48 failed=1`. Its planted table embeds the live `scopes.json`.
- "Show the self-tests outside tools/audit/seat/ …": of the step's 22 commands, only `check_scopes.py --self-test --repo .` exited non-zero (rc 1). Its failing arms were "null control: the live D5 and D6 pass the cap and the line", "the default verdict passes the live scopes" and "the default invocation exits 0 on the live scopes".

`python3 -I tools/audit/check_scopes.py --repo . --ref <r>` prints `ok D5` at the merge base `fd93aa3e9b`, where `s7` holds 4487 units, and `FAIL D5 … over ledger.max_units 4500: s7 holds 4513 units` at `2643502f38`. So the red is the diff's, not main's. The ledger's `_rule` says what to do with a seat that grows past the cap: it "is re-cut here, never sampled". The repair re-cuts `s7` to `tests/features.py` alone (4329 units), and `s8` takes `tests/f{i,r}*` (`finite_boundary.py` 160 and `frontend.py` 24, so `s8` holds 3999). No seat's step set changes, and no file is left unowned or owned twice (`check_scopes.py` prints `ok D5 mode=cells seats=10 universe=945`). Two alternatives were not taken:
- Trimming this PR's comments in `features.py` would only fit the metric.
- Raising `max_units` would loosen the cap that keeps a cell finishable.

Re-runs at `361cc26c97`:
- `owner_only_channel.py` prints `RESULT arms=48 failed=0`.
- `check_scopes.py --self-test --repo .` prints `SELF-TEST passed (every perturbed scope refused)`, rc 0.
- `tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- `tests/closure.py select --diff 2643502f38` prints `MODE: SCOPED -- 1 script(s) run`: `tests/entities.py`. With `PYTHONPATH=tests/hastub` it prints `ALL 2786 ENTITY CHECKS PASSED`, rc 0, and `tests/doc_claims.py` prints `ALL 445 checks PASSED`.

`9e0a095d51c4d787469b403dcfa9e268b1e8f081` merges main `e91329c` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`3da16553914c71017ee25fd98486f2125083016c` merges the authored code head `74a0197a205e03a23b79dffa28bb9094b7943097` and then merges origin/main `dbdc71faea` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`0acec3843eb1a9c003b22b691b8856db63299be5` merges the authored code head `74a0197a205e03a23b79dffa28bb9094b7943097` and then merges origin/main `dbdc71faea` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`b478bdaf50f95230b6b0435f9ff6a01ffcbff35b` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

`8b7a4d2e185dbeabd752415240539adb9cac8c38` is the code head of this handoff, measured against merge base `d2128054dbf666460418e5489ad1bfbdeea99e45` (`origin/main` at 2026-11-25T16:14Z). `0e3eab8a87` merges the PR head `2b61181442` (the bot's merge of `origin/main` `d2128054db` into `00f1f0c89e`) into `5be21e3d57`. The only file that conflicts is `tests/structure_budgets.json`, and the ledger driver resolves it. `8b7a4d2e18` re-records that file from `python3 tests/structure.py --record`: every value is unchanged from `5be21e3d57` and only `recorded_at` moves. `STRUCTURE RATCHET PASSED`. `5be21e3d57` was built as follows. It is measured against merge base `d3d66c40408e76351ffc528686353cadf815a05c` (`origin/main` at 2026-11-25T13:20Z) and descends from the earlier code head `753065db1e71` through these commits:
- `7a6f47ed6d` merges `d13c3e840a` into the PR branch, and `b3c29891eb` merges `origin/main` `f52e700df1` (#3738); `git diff b3c29891eb 753065db1e` is empty, so the tree equals the earlier code head's.
- `dcdb80d974` merges `origin/main` `6a58ba5cb3` (#3888).
- `c79fd5022b` merges `origin/main` `d3d66c4040` (#3864, #3893). Its one conflict is `tests/structure_budgets.json`, resolved by the ledger merge driver; no other file conflicts.
- `5be21e3d57` re-records `tests/structure_budgets.json` from `python3 tests/structure.py --record` on the merged tree: `class_excess_loc` 17286, `max_class_loc` 7826, `module_excess_loc` 21751, each equal to the driver's sum and at or below `origin/main`'s (17290, 7834, 21763); `STRUCTURE RATCHET PASSED`. No metric rises, so no raise is owed.

Re-runs at `8b7a4d2e18` with `PYTHONPATH=tests/hastub`: `tests/structure.py` prints `STRUCTURE RATCHET PASSED`, `tests/entities.py` prints `ALL 2763 ENTITY CHECKS PASSED`, and `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` with this body prints `PRE-PR: 8b7a4d2e185dbeabd752415240539adb9cac8c38` rc=0. `git merge-tree --write-tree` of the head with `origin/main` `a2c483548a` and with the PR branch's `69863356be` reports no conflict.

Delta for review of these merges: `git diff dcdb80d974 8b7a4d2e18 -- tests/structure_budgets.json` against `git diff dcdb80d974...d2128054db -- tests/structure_budgets.json`. Every other path of `git diff dcdb80d974 8b7a4d2e18` is main's own, and no production or test file conflicted.

`753065db1e717c6943814fb81b50528c4e6c9b48` was the code head of the previous handoff: it merges `origin/main` `f52e700df1d2` (no conflict; the ledger driver resolved the budget and closure files) into `d13c3e840a`, which merges `origin/main` `dc2b2bab3164` (#3875) into `76b84e40a7` with its one conflict, the `.store` import in `boost.py`, resolved as both sides' names (`admitted` from main, `save_held` from this branch) and every other hunk of each side unchanged.

The group's seven live roster carries (`origin/handoff/audit-r11-roster`), each unchanged by this head:

- Carry 0: the debug-week and diagnostics-bundle field design for a live-bundle (D15) debugger. Not built in this PR: it is part F of R11-CARRY-DRAWMAP (the debug-week trace and the bundle readers, built on `archive/handoff/r10-draw-map-evidence-f` `880b015c8b`). Carry: R11-SEAM-cycle-reporting-p2
- Carry 1: owner rulings S1-S4 (flat-price sweep, trace text columns, probe before fit, the D15 brief line). Not built in this PR: it is part F of R11-CARRY-DRAWMAP (the debug-week trace and the bundle readers, built on `archive/handoff/r10-draw-map-evidence-f` `880b015c8b`). Carry: R11-SEAM-cycle-reporting-p2
- Carry 2: the re-measure of the stored `MAP_ROWS` size (P7) before part F chooses its drop order. Not built in this PR: it is part F of R11-CARRY-DRAWMAP (the debug-week trace and the bundle readers, built on `archive/handoff/r10-draw-map-evidence-f` `880b015c8b`). Carry: R11-SEAM-cycle-reporting-p2
- Carry 3: the trace's pass-record hook (`debugger.pass_record` against `ArbiterState.last_pass`). Not built in this PR: it is part F of R11-CARRY-DRAWMAP (the debug-week trace and the bundle readers, built on `archive/handoff/r10-draw-map-evidence-f` `880b015c8b`). Carry: R11-SEAM-cycle-reporting-p2
- Carry 4: store wear of the debug-week trace and its disclosure in `docs/configuration.md`. Not built in this PR: it is part F of R11-CARRY-DRAWMAP (the debug-week trace and the bundle readers, built on `archive/handoff/r10-draw-map-evidence-f` `880b015c8b`). Carry: R11-SEAM-cycle-reporting-p2
- Carry 5: the bundle readers weighing sweep levels by steady minutes in `draw_range.last_sweep`. Not built in this PR: it is part F of R11-CARRY-DRAWMAP (the debug-week trace and the bundle readers, built on `archive/handoff/r10-draw-map-evidence-f` `880b015c8b`). Carry: R11-SEAM-cycle-reporting-p2
- Carry 6: publishing the running-draw window rows and `map_rows` columns in `draw_range.diagnostics_view`. Not built in this PR: it is part F of R11-CARRY-DRAWMAP (the debug-week trace and the bundle readers, built on `archive/handoff/r10-draw-map-evidence-f` `880b015c8b`). Carry: R11-SEAM-cycle-reporting-p2

`76b84e40a742dfdfba6e4a7c67ce09b577e47bf2` is the code head of this handoff. It is two merges on #3845's head `625cc2c2aef154c507b37cefb015b1c40b27bde7`: `3654956d84` merges `origin/main` `24e3f37620` (#3834) with the three resolutions below, and `76b84e40a7` merges `origin/main` `5594a34a4940`, which merges with no conflict but `tests/structure_budgets.json` and `tests/closures.json`, both resolved by the ledger merge driver. Main changed none of the three conflicted files between `24e3f37620` and `5594a34a4940`, so the resolutions at `3654956d84` carry unchanged. `git diff 625cc2c2ae 76b84e40a7` is main's delta plus those resolutions.

- Merge resolutions at `3654956d84`, each keeping both sides:
  - `coordinator.py`, the cycle's actuation tail: this branch's `early_cutoff.arm(..., boost.held_for(self), self.entry.async_on_unload)` call, which reads the live config from `ArbiterInputs.opt_config`, is kept, and main's off-restore block (`stale = _plan_let_go(self)` and `off_restore.async_cycle(...)`) follows it. Main's extra `_ctx_of(self)._opt_config` argument is dropped, because `early_cutoff.arm` at the head takes `(held, inputs, boosts, on_unload)` and its one call site uses that signature.
  - `pump_arbiter.py`, `ArbiterInputs` fields: this branch's `opt_config: Any = None` and main's `entry: Any = None` are both kept, each with its comment.
  - `tests/entities.py`, the unlatched-log allowance: main's `("circulation.py", "command")` replaces `("coordinator.py", "_async_set_pump")`, as on main. Main's `("coordinator.py", "_async_update_data")` and `("coordinator.py", "_async_first_refresh_light")` rows are not kept, because this branch holds both update paths' failure through `_fail_update_held` (D1-s3-06), so those sites no longer log unlatched.
- `tests/structure_budgets.json` (ledger driver): `class_excess_loc` 17297, `max_class_loc` 7836, `module_excess_loc` 21763. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` at `76b84e40a7`.
- Re-runs at `76b84e40a7` with `PYTHONPATH=tests/hastub`: `tests/entities.py` prints `ALL 2761 ENTITY CHECKS PASSED`, and `tests/features.py` prints `ALL 6129 FEATURE CHECKS PASSED`.

The text below describes the previous handoff, whose code head `c55c713dcd` is an ancestor of `625cc2c2ae`.

`ce185aeaf998928227a9e88076ae72a0ae9e3c34` is the code head of this handoff, merged into #3845's branch. It is four commits on `fa1a024782`, the merge of `origin/main` `608c95decc94` (main's tip at 2026-11-22T10:56Z) into `f418d51c77`, which merged with no conflict but `tests/structure_budgets.json`, resolved by the ledger driver. At `fa1a024782`, `python3 tests/structure.py` printed `FAIL module_excess_loc 21802 > 21779 (+23)`: this branch's growth past `MODULE_LOC_LIMIT` is coordinator.py +19, config_flow.py +1, optimizer.py +2 and pump_arbiter.py +1. It is paid in production code, not by a raise:

- `eded0bde02` moves the #13 peak-tariff option parsers, `_peak_tariff_months` and `_peak_tariff_hours`, from `coordinator.py` to `tariff.py` as `peak_tariff_months` and `peak_tariff_hours`, beside `CapacityTariff`, whose options they parse. Their bodies are unchanged, and `tariff.py` now imports `GridFeeError` and `parse_month_range` from `grid_fee.py`, which imports nothing from `tariff.py`. `coordinator.py` drops 39 lines, and `tariff.py` stays under the limit at 1262. The five mutation-ledger rows of the two parsers move with their sites (`tests/mutation_ledger/{killed_by,survivor_triage}/tariff.py/`), each keeping its digest, with its anchor re-keyed to `tariff.py:peak_tariff_*`. `mutation_table.completeness_problems` over `tariff.py` and `coordinator.py` reports 0 problems. The R10-FEEDS flood probe in `tests/features.py` calls `tariff_mod.peak_tariff_*`, and `tests/entities.py`'s unlatched-WARNING allowance names `("tariff.py", "peak_tariff_*")`.
- `abb3d7a8b8` deletes the two pins whose `old` text the move edited, `_tariff_months` `RETURN_DEL 44fd15ab` and `_tariff_hours` `RETURN_DEL af10f4de` (both killed by `tests/structure.py`). They are listed under `## Unpinned sites`, where mutation-autofix pins them afresh.
- `49d7af550a` records `module_excess_loc` 21779 -> 21767, with only that row moved: `tests/structure.py` exits 2 on an unrecorded gain.
- `ce185aeaf9` adds `grid_fee.py` and `currency.py` to the five closures holding `tariff.py`, as `ci_predict.py` predicted UNDER-SCOPED. `tests/backtest.py` and `tests/edge.py` were re-recorded with `tests/derive_closures.sh --single`, and each gained exactly those two files; the CI-recorded seconds are kept. `tests/optimality.py` exited 1 under this host's recording, and `tests/stress.py` runs about 15 CI minutes, so those two and `tests/validate.py` gained the same two files by hand. `ci_predict.py --only under-scoped` then predicts no closures red. `closures-autofix` re-measures them on CI.

The move is score-neutral: `score.py --diff 608c95decc94 fa1a024782` and `--diff 608c95decc94 eded0bde02` both print `Architecture score: dS +5.7671 IMPROVES`, with the same three rows (see `## Architecture score`). This host has no interpreter carrying Home Assistant and scipy together, so the HA-driven suites were not re-run here. The scoped gate in this update's prepr and CI are the authority for `tests/features.py` and `tests/entities.py`. A stub-package import of `tariff.py` parses `nov-mar` to `[1, 2, 3, 11, 12]` and `07:00-20:00` to `((7.0, 20.0),)`, and logs one WARNING each for `Smarch` and `25:99`.

`f418d51c7719209d311aab8895328249472e312b` is the code head of this handoff; its merge base is `f269ecccb5f1dfd21eca03a3d5dcc43b3a145603`, which is `origin/main` at 2026-11-22T01:31Z. It is two merges of `origin/main` into the reviewed head `7dd02c4135d851fa03afb2f9b2abed65014eaaf7` (merge base `a8efe1d1c2a8f1e0b44cdf1046a0ea4ca2155a3b`): ec1b533f53 merges `e4c929bd1c`, with the resolutions below; f418d51c77 merges `f269ecccb5` (#3729), which touches only `tests/entities.py`, `tests/structure.py`, `tests/structure_budgets.json`, `tools/policy/field_coverage.mjs` and its delivery row, and merges with no conflict but the budget file, resolved by the ledger driver. `git diff 7dd02c4135 f418d51c77` is main's delta plus those resolutions.

- Merge resolutions, each keeping both sides:
  - `coordinator.py`, the `ArbiterInputs(...)` call in the arbiter-inputs build: this branch's `opt_config=ctx._opt_config` and main's `draw=self._accuracy.draw` are both passed.
  - `pump_arbiter.py` imports: this branch's `from .store import QuarantiningStore, load_mapping, save_held` and main's `from .sysid import KIND_PROBE` are both kept.
  - `pump_arbiter.py`, `ArbiterInputs` fields: this branch's `opt_config: Any = None` and main's `draw: Any = None` are both kept, each with its comment.
  - `tests/structure_budgets.json` was resolved by the ledger merge driver (`class_excess_loc` 17313, `max_class_loc` 7860). `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` at ec1b533f53 and again at f418d51c77, where #3729's two new rows (`in_function_copies` 11, `unloaded_package_imports` 14) hold.
- Semantic check of the merge: `pyflakes custom_components/heatpump_optimizer/*.py` at ec1b533f53 prints the same 21 lines as at `origin/main` e4c929bd1c, line numbers ignored, so the merge adds no undefined name and drops no import. Main adds no new `opt_config` read in `pump_arbiter.py` or `early_cutoff.py`, and `early_cutoff.arm` has its one call site, which uses this branch's signature. No semantic repair was needed.
- Re-runs at ec1b533f53 (`git diff ec1b533f53 f418d51c77` changes no file under `custom_components/`) with `PYTHONPATH=tests/hastub`: `tests/features.py` prints `ALL 6041 FEATURE CHECKS PASSED`; `tests/block_duty.py` `ALL 153 BLOCK DUTY CHECKS PASSED`; `tests/guard_pins.py` `ALL 91 GUARD PIN CHECKS PASSED`; `tests/manual_plan.py` `ALL 132 manual plan checks PASSED`; `tests/finite_boundary.py` `ALL 119 FINITE BOUNDARY CHECKS PASSED`; `tests/boost_drift_replay.py` exits 0. Scoped prepr (`PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`) prints `PRE-PR: f418d51c7719209d311aab8895328249472e312b 000000000000000000`.

- The mutation proofs, the block and the architecture score were taken at 7dd02c4135, except M8, which was taken at ac05746327. The strict-typing row and `tests/entities.py`'s tier check are identical at both commits.
- The suite re-runs were taken at 2d4dd773a0. `git diff 2d4dd773a0 7dd02c4135` adds one test check (`diagnosis.attribute`'s baseline) and nothing else.
- The harness heads were taken at 29f755a5c6 and 31b4bf9f1ea2. `## Figures` names the production delta from those commits to the head.
- Merge of origin/main at handoff/r11-merge-3845; conflicts resolved: tests/closures.json and tests/structure_budgets.json (ledger driver).

## Mutation proof

Each mutant below reverts one fix's production line in a scratch worktree at ac05746327. It then runs the checks that pin the fix, and the file is restored after each run. The block runs as `PYTHONPATH=tests/hastub:tests python3 tools/audit/seat/features_block.py '# R11-SEAM-cycle-reporting: how a failure is reported'`, which needs no prelude because the block imports its own names. Unmutated, it prints `ALL 11 FEATURES BLOCK PASSED`.

- **M1, D1-s3-05.** `store.save_held`'s `log_held(owner, key, True, ...)` is changed back to the old `_LOGGER.debug("Could not persist %s: %s", what, err)`. Three checks fail:
  - FAIL "D1-s3-05: a save failing on three passes logs one ERROR with its traceback, …";
  - FAIL "D1-s3-05: a payload builder that raises is held as the store's failure …";
  - FAIL "D1-s3-05: the coordinator's ledger save failing on three cycles logs one ERROR …".
- **M2, D1-s3-06.** `_fail_update_held`'s `log_held(...)` is changed to `_LOGGER.error("Error updating Heat Pump Optimizer: %s", err, exc_info=True)`, the unlatched arm. FAIL "D1-s3-06: an unexpected failure persisting over two cycles, a setup-time refresh and a setup retry's new coordinator logs one ERROR …".
- **M2b, D1-s3-06.** The latch is held on the coordinator instead of `hass` (`log_held(coord, …)`). The same check fails, on the setup retry's second ERROR.
- **M3, D1-s3-07.** `_lbfgsb_restart`'s new DEBUG line is deleted. Two checks fail:
  - FAIL "D1-s3-07: the L-BFGS-B restart, a learner summary and a diagnostics view that raise keep their fallbacks …";
  - FAIL "D1-s3-07 census: each named handler's function holds a broad handler … and none of them is silent".
- **M4, D10-s1-01.** `handle_set_away`'s refusal predicate is changed to `if False:`. FAIL "D10-s1-01: set_away refuses each of six return times that neither clear nor parse …".
- **M5, D7-s2-03.** `CoordinatorContext.publish_config` is changed to edit the shared config in place (`setattr(self._opt_config, k, v)`). Two checks fail:
  - FAIL "D7-s2-03: a target change and a comfort-weight change each publish a new context; …";
  - FAIL "ADR-003 stale holder: …".
- **M6, ADR-003 stale holder.** `arbiter_inputs`'s `opt_config=ctx._opt_config,` is deleted, so the cut-off reads no config at the decision. FAIL "ADR-003 stale holder: after the cutoff is armed, a published configuration change is what the held cutoff reads at the next reading …".
- **M7, D10-s3-02.** The coordinator's `config_entry: HeatPumpOptimizerConfigEntry` line is deleted, and `PYTHONPATH=tests/hastub:tests python3 tests/doc_claims.py` is run. It prints `1 of 443 checks FAILED`: FAIL "every DataUpdateCoordinator subclass annotates config_entry with the typed entry (D10-s3-02), over a census that found at least one".
- **M8, D10-s3-01.** The strict-typing row is put back to `status: done`, and `tests/entities.py` is run. At ac05746327 it fails: FAIL "the manifest declares the tier the register supports cumulatively" `[manifest.json quality_scale='gold'; the register supports 'platinum' cumulatively; …]`. The unmutated run passes (`ALL 2736 ENTITY CHECKS PASSED` at 2d4dd773a0).

- **M9, the repair at `361cc26c97`.** `scopes.json`'s `s7` is put back to `"tests/f*"`, and `s8` loses `"tests/f{i,r}*"`. That is the tree of `2643502f38`. `python3 -I tools/audit/check_scopes.py --repo . --ref 2643502f38` prints `FAIL D5 … over ledger.max_units 4500: s7 holds 4513 units`, rc 1. `owner_only_channel.py` there prints `FAIL SCOPES null: the planned shape …`. Restored, both pass (`## Head`).

## Null control

The unmodified tree (the merge base a8efe1d1c2a8) does each of the following:

- **D1-s3-05.** The base shows the defect at every persist handler. Both of these instruments are listed under `## Figures`, base → head:
  - the block's store-save census reads 18 of 21 store saves swallowed under a broad handler that logs only at DEBUG;
  - the ported lifecycle injection reads 9 reached persist handlers adding no WARNING-or-higher record over the fault-free control.
  The head's census keeps the 3 saves that are under no broad handler (`_async_rewrite_entry`'s rewrite, `_async_load_manual_plan`'s two clears) as `propagates` at both ends.
- **D1-s3-06.** The ported injection reads both update arms adding an ERROR in each of refreshes A1, A2 and B1. At both ends the transition ERROR is in setup A and setup B: the head still reports the transition.
- **D1-s3-07.** The named-handler census reads 13 of 13 handlers silent. The ported injection reads 7 of 7 of the finding's handlers adding no record at any level.
- **D10-s1-01.** `svc_set_away.py`'s control arm, a parseable ISO return time, reads `control_accepted=1` at both ends.
- **D7-s2-03.** `m4_order_context.py` reads `holder_torn_fields=2`. `enum_m4.py` reads 2 `ctx_inplace` rows and the same 8 `ctx_held` readers at both ends.
- **D10-s3-01 and D10-s3-02.** `platinum_rules.py` reads `untyped_requirements=1` at both ends: `threadpoolctl` is still untyped, and only the row claiming otherwise moved. It reads `entry_point_bare=0` at both ends.

## Figures

The harnesses come from `$EXPORT` = `git archive dbdc1d95fef3 dev/audit/rounds/round11` (`plan/r11`). Each line gives the sha1[:12] of the harness, then base → head. Each was run from the measured tree's root as `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/<path>`. The base is the merge base a8efe1d1c2a8. The head readings were taken at 29f755a5c6, except where a line names 31b4bf9f1ea2. `git diff 29f755a5c6 7dd02c4135 -- custom_components` changes exactly three things:
- the update latch's owner, on the config entry since 31b4bf9f;
- the DEBUG message `diagnostics._never_breaks` formats;
- `async_set_target_temperature`'s typed `publish_config` call.

None of the light harnesses below reads these.

- **D10-s1-01**, `$EXPORT/dev/audit/rounds/round11/D10/s1/svc_set_away.py` (dee23d81ccb9):
  - `acknowledged_unparseable` 6 → 0 of `cases=6`;
  - `cleared_existing_return` 3 → 0;
  - `control_accepted` 1 → 1.
- **D7-s2-03**:
  - `$EXPORT/dev/audit/rounds/round11/D7/s2/m4_order_context.py` (d10405db8aab): `holder_torn_fields` 2 → 0.
  - The seam rule, `$EXPORT/dev/audit/rounds/round11/D7/s2/enum_m4.py` (b2be71d66c80), `grep ctx_inplace`: 2 rows (`coordinator.py:_opt_config.target_temp`, `_opt_config.comfort_weight`) → 0.
  - The 8 `ctx_held` holders are the same at both ends and are readers. The ninth holder, ADR-003's `early_cutoff` `held.wiring`, holds no config at the head (`CutoffInputs` has `inputs` and `boosts` only).
- **D10-s3-01 and D10-s3-02**, `$EXPORT/dev/audit/rounds/round11/D10/s3/platinum_rules.py` (7cd70d243ae9):
  - `untyped_requirements_under_done_row` 1 → 0;
  - `coordinator_untyped_config_entry` 1 → 0;
  - `coordinator_untyped_under_done_row` 1 → 0;
  - `untyped_requirements` 1 → 1 (threadpoolctl).
- **D1-s3-05**:
  - The seam rule, `$EXPORT/dev/audit/rounds/round11/D1/s3/persist_seams.py` (976c2ebd0c6a), reads `persist_handlers` 18 → 0. The route moved: the 18 handlers are now calls of `store.save_held`, whose one handler logs through `log_held`.
  - The class census, the block's `_cr_save_sites()` (store-save calls by how a failure is reported), reads `swallowed` 18 → 0, `held` 0 → 18 and `propagates` 3 → 3.
- **D1-s3-05, -06 and -07, lifecycle injection.** The finder's `$EXPORT/dev/audit/rounds/round11/D1/s3/excepts_inject.py` (d0a0871eaa1f, with `d1s3hook.py` 9a05f2fc53f7) is re-keyed to each tree. Its committed `out/reach2.json` holds the handler ids and the fault-free control at 92d38ecb, so at a later tree `--only` matches nothing. The finder's `log_flood.py` (f62353e900ae) wraps it and raises `JSONDecodeError` at both ends, unported. The port runs `excepts_inject.py --reach --reached-file <scratch>`, re-deriving reach and the control at the measured tree, then injects every reached handler: universe 261 → 244, reached 108 → 99, control 9/9 phases at both ends. The per-finding reading is a scratch reader over its JSONL output. Head at 31b4bf9f:
  - **D1-s3-05:** reached persist handlers adding no WARNING-or-higher record over the control, 9 → 0. At the head, `store.py` `save_held` fired 28 times and added WARNING-or-higher per phase `[8, 1, 0, 0, 1, 8, 1, 0, 0]`: each store warns when it first fails in a process, not on every pass.
  - **D1-s3-06, cycle arm (`_async_update_data`):** the armed refreshes A1, A2 and B1 that add an ERROR, 3 → 0. The transition ERROR stays in setup A and setup B at both ends.
  - **D1-s3-06, setup-time arm (`_async_first_refresh_light`):** 3 → 3. The harness models each setup retry as a new `hass` and a new `FakeEntry` (`excepts_inject.py` `setup()`). Home Assistant retries the same `ConfigEntry`, on which the latch is held. The block's check "D1-s3-06: an unexpected failure persisting over two cycles, a setup-time refresh and a setup retry's new coordinator …" drives the real shape: the same entry, the first coordinator shut down. It reads one ERROR at the head, and two under M2b's coordinator-keyed latch.
  - **D1-s3-07:** of the finding's seven reached handlers, those adding no record at any level over the control, 7 → 0.
- **D1-s3-07 seam rule**, `$EXPORT/dev/audit/rounds/round11/D1/s3/silent_broad.py --seams` (6fa2a381dd2a): 34 → 20 handlers. The census asserts its preconditions: each named function holds a broad handler. The 20 at the head, each with its disposition:
  - **Records through a helper the rule does not follow** (5). These are `coordinator.py` `_async_update_data` and `_async_first_refresh_light` (`_fail_update_held` → `log_held`), `async_run_optimization` (`_note_solve_failure`), `_fetch_tibber_prices` (`_tibber_fetch_failed`) and `_fetch_weather_forecast` (`_weather_fetch_failed`). The finder's own null control counts the last two as recorded.
  - **The failure is carried as a value its caller reports** (10):
    - `config_flow.py` `validate_tibber_token` (`'cannot_connect'`);
    - `coordinator.py` `_valve_write_problem` (the problem text);
    - `debugger.py` `run_self_tests` (`outcome['error']`) and `_async_replay` (the reason string);
    - `off_restore.py` `_restore_baseline` (`sent, err`);
    - `optimizer.py` `_multi_start_minimize` (`last_error`, raised once every start fails);
    - `process_worker.py` `_describe`, `_dump` and both of `run_worker`'s arms (the child's status payload, which the parent raises).
  - **Already guarded: a secondary cleanup failure beside a primary cause** (5). These are `coordinator.py` `_shutdown_process_pool`'s three arms and `_run_in_process`'s two fault arms. The swallowed exception is a kill or close of a child that is already being torn down. `_run_in_process` re-raises the primary cause (`raise`; `ProcessWorkerUnavailable … from err`), and `_shutdown_process_pool` reads the child's state next (`worker.poll()`). They are not recorded here because R11-SEAM-cycle-solve's open handoff rewrites those exact arms (`_reap_killed`), and a one-line edit would conflict with it.
  - **Closed in this diff** (14 of the base's 34): the seven, the 5 evidence fallbacks in this PR's files, `config_flow.py`'s 2 and `diagnosis.py`'s 2. The two update arms join the helper row above.
  - The block's named-handler census reads 13 silent → 0 over the 13 named functions.
- **D10-s1-01 seam rule**, `grep -nE 'cv\.string' custom_components/heatpump_optimizer/services.py`: 22 lines at the head. Each one other than `return_time` is already refused when it does not parse:
  - `entry_id` (×10) → `config_entry_not_found`;
  - `entity_id` → `assign_entity_missing` and `assign_entity_wrong_domain`;
  - `dhw_windows` (×3) → `set_thermal_params_invalid_dhw_windows`, `apply_schedule_invalid_dhw_windows` and `simulate_plan_invalid_windows`;
  - `quiet_silent_windows` and `quiet_off_windows` (×6) → `_validated_quiet_updates`'s translated key and `quiet_windows_overlap`;
  - `expires_at` → `manual_plan_invalid_expires_at`.

  `return_time` is closed in this diff.
- **Suites.**
  - The scoped gate ran at 29f755a5c6 with `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=a8efe1d1c2a8 ./tests/run.sh`, under a `gate_lock.py` lease: 23 of 28 scripts passed, and 5 failed. All 5 were re-run at 2d4dd773a0. The rest touch no line `git diff 29f755a5c6 7dd02c4135 -- custom_components` changes. What each failure was:
    - `features.py`: "every raised exception key exists in strings.json and every translation", because the new key was missing from the census's `_ET_KEYS`;
    - `entities.py`: the P6 G probe on `__qualname__`, and the N-log-flood reasoned list still counting both update arms;
    - `arch_score_head.py`: `CYCLE_HUB_WRITERS`' stale `_apply_comfort_weight` row;
    - `typing_ruler.py`: one `union-attr` on `ctx.publish_config`;
    - `structure.py`: exit 2, two unrecorded gains.
  - Re-runs at 2d4dd773a0, each `PYTHONPATH=tests/hastub python3 tests/<script>.py`: the run prints, for each script:
    - `structure.py`: `STRUCTURE RATCHET PASSED`;
    - `typing_ruler.py`: `ALL 12 typing-ruler source checks PASSED`, with `HPO_TYPING_PYTHON=/opt/hpo/venv-ha/bin/python`, the pinned mypy 2.4.1;
    - `arch_score_head.py`: `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`;
    - `doc_claims.py`: `ALL 443 checks PASSED`;
    - `entities.py`: `ALL 2736 ENTITY CHECKS PASSED`;
    - `features.py`: `ALL 6000 FEATURE CHECKS PASSED`.
  - The block at 7dd02c4135 prints `ALL 12 FEATURES BLOCK PASSED`, and the exception-translation section (`features_block.py` from "# D10-17 (#217, …" to "# #226: …", prelude from `--emit-prelude`) prints `ALL 33 FEATURES BLOCK PASSED`.
- **Structure.** `python3 tests/structure.py --record`, in its own commit with the reason, moves `class_excess_loc` 17322 → 17318 and `max_class_loc` 7873 → 7865. No other row moves.

## Architecture score

At this handoff's head, `python3 tools/audit/archscore/score.py --diff 608c95decc94a8240565aba68fa8f0e1dece8c3d eded0bde02` prints "Architecture score: dS +5.7671 IMPROVES": `hub_solve_writes` 1 -> 0 (+5.4429), `private_cross_module` 9 -> 7 (+0.3219) and `coord_footprint` 2525 -> 2521 (+0.0023). The figure is the same at `fa1a024782`, before the module_excess payment, so the move reads as neither better nor worse.  `score.py --diff fa1a024782 eded0bde02`, the payment alone, prints "Architecture score: dS +0.0000 NULL".

`python3 tools/audit/archscore/score.py --diff a8efe1d1c2a8f1e0b44cdf1046a0ea4ca2155a3b`, at 7dd02c4135, printed "Architecture score: dS +5.7671 IMPROVES" with these rows:

- `hub_solve_writes` 1 -> 0 (+5.4429): the planned move (ADR-003, `prototypes.py --only hub`). `_apply_comfort_weight` publishes a new context.
- `private_cross_module` 9 -> 7 (+0.3219): `away._parse_return_time`'s two crossings (`coordinator.py`, `datetime.py`) read the public `parse_return_time`. ADR-008 banks this only with the new reader: `services.handle_set_away` calls `away_mode.clears_return_time` and `away_mode.parse_return_time` before the write, and its failing test is "D10-s1-01: set_away refuses each of six return times …" (M4).
- `coord_footprint` 2528 -> 2524 (+0.0023).

## Unpinned sites

`python3 tools/pr/ci_predict.py --base origin/main --only mutation`, at #3845's head `ce251f9f0f` merged with `eded0bde02` (a scratch merge, which is what this update pushes), names 9 sites. The 11 sites the handoff at `f418d51c77` listed are re-anchored to the head's lines by matching each site's code text (coordinator.py 6120→6085, 6167→6132, 10607→10572). Four of them are already pinned on #3845's branch by mutation-autofix's `e82a26569c`: away.py:621, coordinator.py:10572, optimizer.py:1866 and store.py:746. The payment adds two sites, coordinator.py:8589 and 8593. The kill evidence for the first eleven was taken at 7dd02c4135, each driven by `tools/audit/seat/mutant_run.py --spec` (the NULL run `SURVIVED`) against the command named:

- custom_components/heatpump_optimizer/away.py:621 RETURN_DEL: pinned by mutation-autofix (KILLED by the block's "D10-s1-01: set_away refuses each of six return times …"; pinned in `e82a26569c`)
- custom_components/heatpump_optimizer/coordinator.py:6085 RETURN_DEL: pinned by mutation-autofix (KILLED by `tests/features.py`, `mutant_run.py --spec --in-place --timeout 3000`, at 7dd02c4135: `SURVIVED NULL`, `KILLED coord6133_RETURN_DEL`. The default 600 s timeout cut the NULL run short, which read as `KILLED NULL`)
- custom_components/heatpump_optimizer/coordinator.py:6132 RETURN_DEL: pinned by mutation-autofix (KILLED by the block's "D1-s3-06: …", whose recovered refresh reads the payload)
- custom_components/heatpump_optimizer/coordinator.py:8589 RETURN_DEL: pinned by mutation-autofix (KILLED by `tests/structure.py`, `mutant_run.py --spec --in-place --cmd 'python3 tests/structure.py'` at 49d7af550a: `SURVIVED NULL`, `KILLED tariff_months_RETURN_DEL`; the deleted pin's killer, re-driven on the edited line)
- custom_components/heatpump_optimizer/coordinator.py:8593 RETURN_DEL: pinned by mutation-autofix (KILLED by `tests/structure.py`, `mutant_run.py --spec --in-place --cmd 'python3 tests/structure.py'` at 49d7af550a: `SURVIVED NULL`, `KILLED tariff_hours_RETURN_DEL`; the deleted pin's killer, re-driven on the edited line)
- custom_components/heatpump_optimizer/coordinator.py:10572 RETURN_DEL: pinned by mutation-autofix (KILLED by the block's "D1-s3-07: diagnosis inputs whose state cannot be copied are None, …"; pinned in `e82a26569c`)
- custom_components/heatpump_optimizer/diagnosis.py:95 RETURN_DEL: pinned by mutation-autofix (KILLED by the block's "D1-s3-07 seam rule: a diagnosis whose baseline cannot be simulated is no report (None), …")
- custom_components/heatpump_optimizer/diagnostics.py:375 RETURN_DEL: pinned by mutation-autofix (KILLED by "D1-s3-07: the L-BFGS-B restart, a learner summary and a diagnostics view that raise …")
- custom_components/heatpump_optimizer/optimizer.py:1866 RETURN_DEL: pinned by mutation-autofix (KILLED by the same check; pinned in `e82a26569c`)
- custom_components/heatpump_optimizer/services.py:640 BOOLOP: pinned by mutation-autofix (KILLED by "D10-s1-01: …")
- custom_components/heatpump_optimizer/services.py:640 GUARD_OFF: pinned by mutation-autofix (KILLED by "D10-s1-01: …")
- custom_components/heatpump_optimizer/store.py:744 RETURN_DEL: pinned by mutation-autofix (KILLED by "D1-s3-05: a save failing on three passes …", which reads each call's return)
- custom_components/heatpump_optimizer/store.py:746 RETURN_DEL: pinned by mutation-autofix (KILLED by the same check; pinned in `e82a26569c`)

Two survivors are triaged as equivalent in `tests/mutation_ledger/survivor_triage/`, each with its reason:

- `away.py/parse_return_time.GUARD_OFF.48f338a4.json`: every clearing spelling reaches `stored_instant` and returns `None` without the guard (measured).
- `coordinator.py/_stored_fuse_advisor.RETURN_DEL.d7923b87.json`: nothing follows the `try`.

The two stale pins the diff edited (`_async_update_data` `RETURN_DEL 3bda3d97`, `_async_first_refresh_light` `RETURN_DEL 35324698`, both success returns) were deleted by hand. The `_parse_return_time` kill pin is renamed to `parse_return_time`, with its anchor updated. The payment's two stale pins (`_tariff_months` `RETURN_DEL 44fd15ab`, `_tariff_hours` `RETURN_DEL af10f4de`) were deleted by hand in `abb3d7a8b8`; their lines are 8589 and 8593 above.

Diff mutants at `361cc26c97`: `python3 tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" --cmd "$MUTANT_CMD" --max-mutants 40 --report-only` exits rc 0. It printed 27 `SURVIVED` lines of the 40 drawn, with `MUTANT_CMD` = `env PYTHONPATH=tests/hastub:tests python3 tools/audit/seat/features_block.py --prelude "exec(open('<prelude>').read())" '# R11-SEAM-cycle-reporting: how a failure is reported'`. The prelude is written by `features_block.py --emit-prelude <prelude> '# R11-SEAM-cycle-reporting: how a failure is reported'` at this head. Unmutated, the block prints `ALL 51 FEATURES BLOCK PASSED`. The block was run with no prelude first, as the earlier mutation proof stated, and it raised `NameError: name 'dataclasses' is not defined` at this head. Every survivor is on a `custom_components/` line this PR added before the repair, which changes no `.py` line. The block alone does not reach them. None was driven against the whole `tests/features.py` in this repair. Each is left to the `tests/mutation` lane, which mutation-autofix pins from:

- custom_components/heatpump_optimizer/away.py:632 GUARD_OFF  if False:: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/away.py:320 STMT_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/away.py:421 STMT_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/away.py:455 STMT_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/away.py:558 STMT_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/away.py:565 STMT_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/away.py:575 STMT_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/away.py:578 STMT_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/config_flow.py:792 CONST_SWAP  _LOGGER.debug("A field default raised; not prefilled", exc_info=False): pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/config_flow.py:2550 CONST_SWAP  _LOGGER.debug("Computed default %s not recomputed; value kept", row.key, exc_info=False): pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:2695 CONST_SWAP  _LOGGER.debug("%s summary unavailable", name, exc_info=False): pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:3054 CONST_SWAP  _LOGGER.debug("Stored fuse advice unreadable; not restored", exc_info=False): pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:4764 CALL_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:6114 CALL_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:6114 CONST_SWAP  log_held(self.entry, _UPDATE_FAILED, True): pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:6115 RETURN_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:7695 CALL_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:8189 CALL_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:8297 CALL_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:8338 CALL_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:8542 RETURN_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:8546 RETURN_DEL  pass: pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:9131 CONST_SWAP  _LOGGER.debug("Curve comfort not tracked this cycle", exc_info=False): pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:9409 CONST_SWAP  _LOGGER.debug("Monthly COP-issue estimate unavailable; 0 kWh used", exc_info=False): pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:9971 CONST_SWAP  _LOGGER.debug("COP residual tag skipped", exc_info=False): pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:10531 CONST_SWAP  _LOGGER.debug("Diagnosis inputs not captured", exc_info=False): pinned by mutation-autofix (survived the block only)
- custom_components/heatpump_optimizer/coordinator.py:10537 CONST_SWAP  _LOGGER.debug("Diagnosis wind not captured; recorded as 0", exc_info=False): pinned by mutation-autofix (survived the block only)

## Red checks

- Merge resolution at `f7b44e69ec` (`## Head`): the conflict was `dev/audit/config/scopes.json`, taken from main's `7df39f34`, which makes the same `s7` re-cut. At the merge, `check_scopes.py` (self-test and `--ref HEAD`) passes and `owner_only_channel.py` prints HELD. The merge turns no check red. Main's re-cut now carries the `governance / instrument-self-tests` repair described in `## Head`.
- `gate` at `00f1f0c89e40` (run 45609379755). Its last job, 139313969601 (`--kind code`), printed `FAIL tests / mutation: cancelled (this run)`. An earlier job, 139202621751 (`--kind edit`), printed `FAIL run(s) [45609372065] at this head are still being judged`. `tests / mutation` (job 139191933851) ran from 12:18:53Z to 14:59:07Z, which is the job's `timeout-minutes: 160` (`.github/workflows/tests.yml:1141`). The runner then terminated the mutation table's `python3` children mid-run. No check failed and no survivor was reported: the job was stopped by the clock, not by a red. This seat does not establish why that run took the whole budget. The orchestrator reports a partial GitHub outage over the same hours, which by its note makes a cancelled job a rerun, not a code repair. The new head `8b7a4d2e18` triggers a fresh `tests / mutation`, and that run's `gate` decides. Cheaper detector: none is owed for a cancellation. A local `mutation_table.py` run does not predict CI's runner time.
- `tests / mutation` (predicted by `tools/pr/ci_predict.py` at #3845's head merged with this code): red by construction on the 9 sites still unpinned under `## Unpinned sites`, which are lines this diff adds and none is yet in the ledger. Each is driven there, killed by a named check, or triaged as equivalent; `mutation-autofix` pins the killed sites after the push. Cheaper detector: `ci_predict.py`, which `prepr.sh` already runs offline, so no countermeasure is owed.
- `governance / instrument-self-tests` (predicted by `ci_predict.py`; WORKAROUND P-R11-PREPR-TTL0-FIND): the `reds_arm` self-test (P351) reads 0 where 1 is wanted on a macOS host, because BSD `find` matches `-mmin -0`; this diff touches no instrument. The open ran with `~/.local/state/hpo/overlay-find`, a local shim answering `-mmin -0` with no match. Cheaper detector: the self-test itself, which `prepr.sh` already runs; the fault is the host's, so no countermeasure is owed here. At #3845's head merged with this code, `ci_predict.py --only step-replay`, run with the shim first on PATH, predicts no STEP REPLAY red. `selftest_wiring.py --self-test` (26 checks, 0 failed) and `--check` (151 wired, 0 unwired) exit 0 at both `f418d51c77` and the merged head, so the arm the open predicted does not reproduce here.

- `codeql / Analyze (python)` (job 139693314439, run 45755413224, head `b478bdaf50`): the job started 04:31:40Z, its step `Perform CodeQL Analysis` never recorded a conclusion, and the check ended 06:00:41Z with the annotation "The hosted runner lost communication with the server". No log exists for the job (the log blob returns 404). It is a runner loss, not a finding: the same head's run 45735974913 ran `codeql / Analyze (python)` to `pass` in 2m39s, and the open PRs at 46cdd1f919, fe2b516c71, 7d4124f67a and 0ce590428e read `pass` for it, so the diff reaches no CodeQL result. Cheaper detector: none is owed for a lost runner; a rerun of the job is the answer, and the passing run of the same head is it.
- `tests / nightly-status` (jobs 139048800676, 139191933606, 139392193161, 139531434851, 139589867958 and 139712794553 across the ancestry; exit code 1): the check reads the last concluded scheduled `nightly.yml` run, not this diff. That run, 45731557683 (00:50Z on 2026-11-26), has `nightly-ha (stable)` and `nightly-ha (2025.2.0)` failing 2 of 66 checks (`a5:pages_ok`, `run:exit_status`) and `slow` failing, all on main's tree. Cheaper detector: `nightly-status` itself, which is the standing detector and costs seconds; the red clears when a scheduled nightly concludes green, and this PR touches no nightly lane.

## Forward-carry

none

## Friction

none



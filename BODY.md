Closes #3856. Builds the approved design `design/R11-OWNER-FAULT-HOLD` at `57d5d278f0c5` (verdict `design-verdict/R11-OWNER-FAULT-HOLD` `e9598ceb7e`, `Design review: approve`): while the pump's fault alarm has been on for 10 minutes, the integration stops commanding the pump.

## Summary

`fault_hold.py` (new, a leaf over `const`, `entry_config`, `inputs` and `issues`) owns a per-entry latch and the `pump_fault_hold` repair. It reads the fault slot with `inputs.UNBOUNDED`, so a push-only fault still reads at any age. The latch starts at the alarm's `last_changed`, bounded to now. A legible off resets it. Unavailable, unknown or not-boolean readings neither start a hold nor end one. Optimizer Off and the `fault_hold` option set to off clear it. An unloaded entry (`released`) answers False and raises nothing. The hold starts at `FAULT_HOLD_AFTER` (10 min).

While the latch holds:

- `pump_arbiter.apply` consults once per pass, before the duty-off return, so the latch moves for every install. In control, `_arbitrate` returns before `_adopt`, `hold`, `_command` and the night schedule (`_fault_stands`). It drops `space_before` and the pending retries and clears `pump_write_ignored`.
- `_lead_mode` writes no mode.
- An unload writes no baseline row: `off_restore`'s release of the row (`pump_arbiter._release_row`, main's since #3812) answers False for `reason == "unload"` under the latch, so the row stays owed; `release` then drops the latch and the repair. The space set-point's own restore still runs. Off ends the hold, so entering Off hands the row back at once.
- A stale plan's hand-back (`off_restore.async_cycle`'s stale half, #3812: supply on, frequency, valve, the row) is not run while the latch holds; it runs once the alarm clears.
- The cycle's and the step tick's switch gate (`fault_hold.gate`, after `supply_hold.hold_supply` in `_write_supply`) turns an OFF into "leave" and marks `supply_held`, so the step tick lands it after the clear. An ON passes.
- `early_cutoff.on_room_event` does not cut.
- `_command_frequency` returns.
- `heat_curve.publish`, the one sink of every displace (cycle, peak-guard engage and release), sends nothing.

The step ledger lives in `duty_ledger.py` (main's module since #3812; this group adds `observe`, `RUN_SETTLE` and the `faulted` mark there). A step in which any pass held is `device-fault`, decided before every other verdict. The onset step keeps its own verdict because a row closes when its step ends. The option `fault_hold` (default on) sits beside the Fault alarm entity. Docs: `docs/configuration.md` (two rows, the ledger line and a "A pump that reports a fault" section, which now says what a stale plan and an unload hand back under the hold), `docs/architecture.md` (module map and the HA boundary counts), the repair in `README.md`.

The design's carries, each built here:

- **skip-log**: the held mark suppresses the cooling debug line; the gate logs its own.
- **multi-entry**: one domain-wide id, cleared only when no entry on the same `hass` holds.
- **hand-reset**: the repair text says to turn Optimizer active off first.
- **entry-released / publish-released**: `holding(released=...)`, with `publish` given `released=self._entry_released` on the coordinator's existing argument line.
- **supply-after-clear**: the held mark.
- **ignored-repair**: cleared in `_fault_stands`.
- **unload-row**: built, now in `_release_row` (see `## Merge resolution`).
- **onset-step**: docs ledger line.
- **cc-headroom**: `functions_cc_over_15` unchanged; the fault folds into `_arbitrate`'s existing return condition.
- **bundle-latch-count**: `dev/audit/harnesses/r11_owner_fault_latch.py bundle --timeline T`.
- **ledger-constants**: `TANK_RISE_C` and `RUN_SETTLE` live in `duty_ledger.py`; `duty_ledger` imports only `plan_step`.
- **publish-config**: `holding` builds its `InputReader` from `dict(config)`.
- **duty-off-latch-age**: `gate` and the cut-off call `consult`, which reads, so there is no lag.
- **reported-displace**: under the hold the coordinator still records the computed displace (`_ecl110_current_displace`). `docs/configuration.md` says the diagnostics report the computed displace, which was not sent, and shows the latch under `fault_hold`.
- **fallback-private-reach**: not needed; the coordinator class did not grow.
- **seam-actuation**: SEAM-ACTUATION-RELEASE merged first (#3812); this branch merges it, and `## Merge resolution` states each file.

Departures, raised: FROST-HOLD (`e91a4e30`), which the design orders ahead of this group, is not on main. So the gate chain is `hold_supply → fault_hold.gate`, and the cut-off consults `fault_hold` directly, with no frost hook to wrap. The frost composition is carried to FROST-HOLD below. The latch reads the alarm's `last_changed` directly. That is registered as a `state_age` disposition (`fault_hold.py::holding`) in `tests/entities.py`, for the same reason `supply_hold.switch_age` reads it: the value's age, not the entity's last report. Two behaviours are new with the merge and not in design `57d5d278`, which predates #3812's restore owner: the stale hand-back held under the latch, and Off's row handed back at the mode change.

## Head


`07223afa29183c818afe339b045d8d5ee0b839f0`, measured against its merge base `6a58ba5cb3` (the `origin/main` merged in `07223afa29`). `origin/main` is `bb6377b4dad4e398d1a28bde54d30036a5b25a82` at the stamp; `git merge-tree --write-tree origin/main HEAD` exits 0, without the ledger driver too. Stamped 2026-11-25T11:52:40Z. Review round 1 (`review/3872` `d77b2da2`, `verdict/3872` `c61cfa41`) blocked `d6a54399a63b` as mutation-vacuous; `ce9619a4f4` answers it, and the commits after it merge main. The branch's own commits, `git log --first-parent 8ef450936a17..HEAD`:

- `6477e5f7df` R11-OWNER-FAULT-HOLD: suspend actuation while the pump reports a latched fault
- `149b770946` R11-OWNER-FAULT-HOLD: record block_duty's closure with the two new modules; harness INERT READS
- `bac3d94412` R11-OWNER-FAULT-HOLD: closures re-recorded for the two new modules; the fault latch's value-age disposition; tree counts the modules move; the mutation harness
- `62a9fe6873` R11-OWNER-FAULT-HOLD: INERT READS for the mutation harness
- `dacb2f71db` R11-OWNER-FAULT-HOLD: entities.py closure gains the two new modules (two-step record: its only reds were the full-coverage checks it reads from that closure); deployment-shape note keeps 167 pairs
- `5eb7083aaa` R11-OWNER-FAULT-HOLD: duty_ledger.step_verdict (tests/layout.py owns the name verdict); faulted keyword-required; the diagnostics row checked
- `ce9619a4f4` R11-OWNER-FAULT-HOLD: one check per call site of the latch (consult released and Off through apply, publish at mode_off, the diagnostics since); the four mutants in the harness
- `2b1f96e77b` Merge origin/main af4d89f763 into R11-OWNER-FAULT-HOLD: resolve against R11-SEAM-actuation-release (#3812)
- `abc36b3f09` R11-OWNER-FAULT-HOLD: structure budgets re-recorded after the main merge: module_excess_loc 21775 -> 21741
- `f8b1b7b9ea` R11-OWNER-FAULT-HOLD: drop the three mutation-ledger pins the merge left stale
- `69d2557947` R11-OWNER-FAULT-HOLD: Off ends the hold, so its restore writes the baseline row at once; only an unload under the hold leaves the row owed; docs; the harness's two new mutants
- `ed1b1ae98e` R11-OWNER-FAULT-HOLD: structure budgets re-recorded: module_excess_loc 21741 -> 21740
- `fdcf373670` test: fault-hold Off check compares against its null control, which no longer fails under the Off-row mutant
- `8d8b30aabf` R11-OWNER-FAULT-HOLD: config_flow fixture re-recorded with the fault_hold option; claimed
- `e2e30e43ad` Merge origin/main `5594a34a49` (no conflict; the ledger driver merged `tests/closures.json` as sets)
- `b29af9141c` R11-OWNER-FAULT-HOLD: D6 claims register regenerated (claims.py): 102 modules, 37 module-level homeassistant importers
- `79265fe95b` R11-OWNER-FAULT-HOLD: tests/cycle_lane.py's closure gains fault_hold.py (derive_closures.sh --single)
- `9924e94422` Merge origin/main `f52e700df1` (through #3738, #3875, #3868, #3887): module counts resolved against #3738's `solve_gate.py`; D6 claims register regenerated
- `07223afa29` Merge origin/main `6a58ba5cb3`: `tests/closures.json` and `tests/structure_budgets.json` through the ledger driver (a merge without it conflicts, so CI would run nothing)

Read the diff three-dot. For the reviewer's delta from the reviewed head: `git diff d6a54399a63b HEAD`; from the previous handoff `79265fe95b`: `git diff 79265fe95b HEAD` (all of it main's but the count lines of `9924e94422`) (round 1's head, which already carried main to `e3cb5c019b`).

## Merge resolution

`git merge origin/main` (`af4d89f763`) into `ce9619a4f4` conflicted in 8 files and 4 mutation-ledger rows, all from #3812 (R11-SEAM-actuation-release), which moved the step verdicts into its own `duty_ledger.py` and the off/unload baseline row into `off_restore` (`_release_row`, `ROW`). Each file, both sides read back in the merged artifact:

- `custom_components/heatpump_optimizer/duty_ledger.py` (add/add): main's module is the base (its `_not_startable`, `_missed` and `step_verdict` are identical to ours but for the fault branch and the local name). This group's on top: `observe()` (the row fold `pump_arbiter._observe` delegates to), `RUN_SETTLE` (main kept `RUN_SETTLE = _TICK` in `pump_arbiter.py`, both one minute; it now lives here only), the `faulted` row key and `device-fault` first in `step_verdict`. The docstring opens with main's first line.
- `custom_components/heatpump_optimizer/pump_arbiter.py` (5 hunks): module docstring is main's ledger paragraph plus this group's fault paragraph; imports are main's plus `fault_hold`; `_observe` is this group's (delegating to `duty_ledger.observe` with `faulted`); `release()` is main's (writes nothing, persists) plus `fault_hold.release(coord.hass, coord.entry)`. This group's old in-`release` baseline write is gone with main's: the unload's row is `_release_row`'s, which gains `(reason == "unload" and fault_hold.held(coord.entry))` in its first guard. Main's `_arbitrate` Off comment is taken as is.
- `custom_components/heatpump_optimizer/coordinator.py` (2 hunks): the cycle keeps main's `stale = _plan_let_go(self)` and `off_restore.async_cycle(...)`, with this group's `entry=self.entry` on the cut-off arm; the stale half is passed as `stale and not fault_hold.held(self.entry)` (Off's half is not touched: Off's pass has already cleared the latch). `_command_frequency`'s guard is the union: `... or _plan_let_go(self) or fault_hold.held(self.entry)`.
- `docs/architecture.md` (3 hunks): main's map row for `duty_ledger.py` plus this group's `fault_hold.py` row; counts re-derived: 102 modules, 37 importing `homeassistant` at module level (main's 36 plus `fault_hold`).
- `tests/deployment_shape.py`: 121 package files (main's 120 plus `fault_hold.py`), history line extended.
- `dev/audit/rounds/round4/D6/claims.py`: main's, with the three expectation lines re-derived (102, 102, 37) and their history; `claims.json` and `claims.md` are main's.
- `tests/mutation_ledger/killed_by/duty_ledger.py/` rows `@module.CONST.647a1d0a`, `_missed.RETURN_DEL.0733b5f7`, `step_verdict.GUARD_OFF.00bf3d75` and `step_verdict.GUARD_OFF.d746330a`: main's. `ci_predict` then named three pins stale (`_command_frequency` GUARD_OFF `0bf30dbd`, `step_verdict` GUARD_OFF `d746330a`, `_release_row` GUARD_OFF `88e2f26e`: each line gained the fault clause); deleted by hand in `f8b1b7b9ea`, as `ci_predict` prescribes, for mutation-autofix to pin afresh.
- `tests/structure_budgets.json`: the ledger driver summed both sides' deltas to `module_excess_loc` 21690, counting the ledger move both branches made twice; the merge commit takes main's (21775), and `abc36b3f09` / `ed1b1ae98e` record the merged tree's 21740.
- `tests/closures.json`: merged as sets by the ledger driver, no conflict.
- `tests/features.py` (no textual conflict, three semantic repairs): section 12 drives main's unload and Off paths (`_pa_unload`, `_pa_enter_off`: `off_restore` then `release`) instead of `release` alone, which no longer writes; the early cut-off fixture passes `entry=` into `ArbiterInputs` (main's `switch_supply` now takes the entry); a new 12b drives a stale-plan cycle through the real coordinator (`_r11ar_*` fixtures of #3812).

Second merge, `e2e30e43ad` (`origin/main` `5594a34a49`, through #3825, #3880, #3886): no textual conflict. `origin/main` changed no file under `custom_components/` since `af4d89f763`. Two semantic repairs: the D6 claims register (`claims.json`, `claims.md`), which the first merge took from main, is now what `claims.py` writes on the merged tree (C32-C35: 102, 102, 37, `fault_hold.py` named); and #3825's new `tests/cycle_lane.py` reads `coordinator.py`, which imports `fault_hold` here, so its closure is re-recorded with `--single`, adding `fault_hold.py` alone.

Third merge, `9924e94422` (`origin/main` `f52e700df1`): conflicts in the count lines only, each the union of both additions. `docs/architecture.md`: 103 modules, 37 importing `homeassistant` at module level (#3738's `solve_gate.py` imports none). `tests/deployment_shape.py`: 122 package files, history extended (121 until `solve_gate.py`, 120 until `fault_hold.py`). `dev/audit/rounds/round4/D6/claims.py`: 103 with both history clauses; `claims.json` and `claims.md` regenerated by `claims.py` on the merged tree. Main's production changes in this range (#3738 `solve_gate.py`, `coordinator.py`; #3875 `store.py`, `boost.py`, `snapshots.py`) merged without conflict with this group's `coordinator.py` lines.

Fourth merge, `07223afa29` (`origin/main` `6a58ba5cb3`, through #3888 and the duty-switch, duty-legs and optimizer changes): no textual conflict outside the two ledger files, which the `ledgermerge` driver merged (`tests/closures.json` as sets; `tests/structure_budgets.json` `module_excess_loc` re-summed, `tests/structure.py` passes on the merged tree). Pushed because `body_push`'s predictor refused `9924e94422`: `governance / wave-script AGREEMENT UNMERGED`, since GitHub's merge has no ledger driver.

## Mutation proof

`python3 dev/audit/harnesses/r11_owner_fault_hold_mutants.py HEAD`. It runs 38 hand mutants, each deleting or weakening one production predicate in a `git archive` copy, and drives the fault-hold block of `tests/features.py` and `tests/block_duty.py`. Unmutated baseline: 0 failing. Result at this head: `RESULT mutants=38`, `RESULT survived=0`.

The merge re-texted two mutants (`release row skip` now drops `_release_row`'s fault clause; `frequency guard` keeps `_plan_let_go`) and added two: `Off row held too` (the `reason == "unload"` clause dropped) and `stale hand-back held` (`async_cycle`'s stale half passed bare).

Review round 1 found four call-site arguments the checks never drove: the earlier checks called `fault_hold.holding(off=..., released=...)` directly, so `consult`'s and `publish`'s own arguments could be replaced and nothing went red. Each now has a check through its call site, with a null control, and each mutant is in the harness:

- `fault_hold.py:115`, `consult`'s `released=inp.entry_released` dropped: "a pass queued before the unload (entry_released) with a 30-minute fault raises no fault repair" (null control: the same `pump_arbiter.apply` pass on a loaded entry raises it).
- `fault_hold.py:115`, `consult`'s `off=inp.mode == MODE_OFF` → `off=False`: "an Optimizer Off pass after a held pass clears the latch and the fault repair" (null control: the next pass in auto keeps both).
- `heat_curve.py:287`, `publish`'s `off=mode_off` → `off=False`: "the Off displace under a held latch is published, and clears the latch and the fault repair" (null control: the same second displace outside Off is not sent and the hold stays).
- `fault_hold.py:150`, `diagnostics_view`'s `since` → `None`: "the diagnostics row's since is the latch's start, the alarm's last change", at two starts (-30 and -45 minutes) so a constant cannot pass (null control: with no fault `since` is `None`).

The four verdict sites, re-run at this head with `tools/audit/seat/mutant_run.py --spec` over the fault-hold block (its automatic NULL mutant first, SURVIVED): `KILLED fault_hold.py:115 released`, `KILLED fault_hold.py:115 off`, `KILLED heat_curve.py:287 mode_off`, `KILLED fault_hold.py:150 since`.

Failing first: the same tests against the merge base's `custom_components/` (head `tests/` and `tools/`) stop at `ImportError: cannot import name 'fault_hold'`.

## Null control

Every behaviour check is paired with today's behaviour on the same fixture: the alarm on for 9 minutes, reading off, or `fault_hold` off writes what the merge base writes. Section 12: unload with no fault writes the row; Off with no fault writes the same row as Off under the hold. Section 12b: the same stale cycle with no fault writes the supply switch back. The synthetic replay's null is `--opt-out`: `RESULT latched_actuating=260` against `0` with the hold; `RESULT repairs=0` against `1`; `RESULT short_held=0` both ways (measured at `5eb7083aaa`; the latch module is unchanged since).

## Figures

- `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'exec(open("P").read())' 'R.section("R11-OWNER-FAULT-HOLD' 'R.section("duty-switch restart learning, part A'`, P from `--emit-prelude P` with the same two markers, at `69d2557947`: `ALL 59 FEATURES BLOCK PASSED` (55 at `ce9619a4f4`: section 12 gains its Off pair, 12b adds two).
- `python3 dev/audit/harnesses/r11_owner_fault_hold_mutants.py HEAD`: `RESULT mutants=38`, `RESULT survived=0` at this head.
- `PYTHONPATH=tests/hastub python3 tests/features.py` at this head: `ALL 6206 FEATURE CHECKS PASSED` (6196 at `9924e94422`, 6175 at `79265fe95b`, 6173 at `fdcf373670`; main's merges add checks).
- At this head: `tests/structure.py` `STRUCTURE RATCHET PASSED`; `tests/deployment_shape.py` `ALL DEPLOYMENT SHAPE CHECKS PASSED`.
- Main's new and changed scripts that read this group's modules, at `9924e94422`: `tests/cycle_lane.py` `ALL 25 checks PASSED`; `tests/config_flow_steps.py` `ALL 684 checks PASSED`; `tests/deployment_shape.py` `ALL DEPLOYMENT SHAPE CHECKS PASSED`; `tests/structure.py` `STRUCTURE RATCHET PASSED`. At `79265fe95b`: `tests/cycle_lane.py` `ALL 25 checks PASSED`; `tests/config_flow_steps.py` `ALL 684 checks PASSED`; `tests/deployment_shape.py` `ALL DEPLOYMENT SHAPE CHECKS PASSED`.
- The harness, the four verdict sites and the block were measured at `fdcf373670`. No commit of this branch after it changes production code; the merge `9924e94422` brings main's own production changes (#3738, #3875), which the full `features.py` run at this head covers. `8d8b30aabf` changes only `tests/golden/config_flow.json` and `tests/golden/claimed_drift.txt`, which no production module, harness or block check reads.
- `python3 tests/structure.py` at this head: `STRUCTURE RATCHET PASSED`; `module_excess_loc` 21740 recorded (main 21775), every other row unchanged from main.
- `python3 tests/comment_ratchet.py` at `69d2557947`: `comment_ratchet: OK`.
- `python3 tools/pr/ci_predict.py` at this head: `CI PREDICT: no closures, fast, governance or instrument red predicted` (against `6a58ba5cb3`); `CI PREDICT: 41 unpinned site(s) the diff adds` (each under `## Unpinned sites`).
- Not re-run after the merge (scoped, per the merge brief): `tests/derive_closures.sh` (no closures red predicted above; CI's closures job is the authority), prepr's diff-mutant step, and the lanes `5eb7083aaa` ran (`tests/backtest.py`, `tests/edge.py`, `tests/frontend.py`, `tests/md_tables.mjs`, `tests/open_meteo.py`, `tests/optimality.py`, `tests/validate.py`).
- `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` at `fdcf373670`: `rc=0`. At `8d8b30aabf` its one refusal was `ci predict`, the `tests/cycle_lane.py` UNDER-SCOPED closure, repaired at this head; `tools/pr/ci_predict.py` at this head before that repair named that one red only. The full prepr runs at the push (`app_push.sh`). Its `self-test` step is skipped by a local overlay in this seat's tools checkout, because `prepr.sh --self-test` fails the same 4 rows (the ancestry-reds rows, `got 0`) on plain `origin/main` `5594a34a49` on this host; CI's `governance` job runs the self-test.

## Architecture score

`python3 tools/audit/archscore/score.py --diff af4d89f76325 HEAD` at `f8b1b7b9ea`: `Architecture score: dS +0.0006 IMPROVES`, `coord_footprint` 2521 → 2520. No gate metric rises.

## Red checks

- `tests / fast (3.14)` at `d6a54399a63b`: `tests/env_drift.py --all` ended `1 UNCLAIMED DRIFT(S)`, `config_flow`, three leaves `present on one side only` (`_seed.fault_hold`, `_seeded.entities_pump.fault_hold`, `entities_pump.fault_hold`): the new option was never re-recorded into `tests/golden/config_flow.json`. Answered in `8d8b30aabf`: `golden.py --record --only config_flow` (13 lines added, none removed) and one `config_flow` claim line in `tests/golden/claimed_drift.txt` stating the direction (ADDED). `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all af4d89f76325` at this head: `NO UNCLAIMED DRIFT: 56 scenario(s) checked`, `NO STALE FIXTURE`, config_flow `CLAIMED` with exactly those three leaves. The cheaper detector exists: `PYTHONPATH=tests/hastub python3 tests/golden.py --only config_flow`, seconds, reports the same DIFF; the fixer's lanes ran `tests/features.py` and the block but not `tests/golden.py`, and a scoped prepr (`PREPR_SKIP_CODE=1`) runs neither. Its standing cost is one golden run per head that adds an option key; the countermeasure is that run, recorded here, before every handoff of this branch.
- `tests / mutation` and `tests / mutation-autofix` at `d6a54399a63b`: red by construction on the sites under `## Unpinned sites`; mutation-autofix pins the killed sites after the push.
- `pr-contract` and `gate` at `d6a54399a63b`: the body there did not name the two reds above; `gate` aggregates the required checks. No CI has run at this head yet.
- Local `prepr.sh` step `self-test` (not a CI check; CI's `governance` job runs the self-test): `567 passed, 4 failed` on this host, the same 4 rows on plain `origin/main` `6a58ba5cb3`: "an ancestry no commit of which carries any check run skips, never refuses (got 0, wanted 3)", "and the skip line names the boundary (got 0, wanted 1)", "reds_arm refuses a body that leaves an ancestry red unanswered (P351) (got 0, wanted 1)", "and the refusal is the red gate's own sentence (got 0, wanted 1)". A host fault, not this head's: this update ran under a local overlay that skips that one step (logged as a workaround).

## Unpinned sites

The sites `tools/pr/ci_predict.py` lists at this head. Every fault-hold predicate among them is killed by `r11_owner_fault_hold_mutants.py` above.

- custom_components/heatpump_optimizer/coordinator.py:7753 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10806 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:62 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:62 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:62 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:95 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:97 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:312 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:76 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:79 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:81 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:84 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:84 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:86 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:88 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:90 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:90 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:90 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:95 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:95 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:100 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:100 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:104 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:109 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:109 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:115 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:121 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:121 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:131 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:135 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:141 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:142 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:144 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:287 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1837 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1889 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1908 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1912 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1941 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:2195 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:2195 GUARD_OFF: pinned by mutation-autofix

## Forward-carry

- Carry 0 (from R11-OWNER-MODE-LEGS, body item 411606ae, the pin "the fault hold wins with a young leg latched"): not buildable here. MODE-LEGS' `_kept_leg` is not on main (`af4d89f76325`; its head is `handoff/r11-owner-mode-legs`). The hold returns before `_command` in `_arbitrate` (`_fault_stands`), downstream of `_served`, so a latched leg writes nothing under it by construction. Whichever of the two lands second owes the pin, as that body states; with this group first it is MODE-LEGS'. It lands in R11-OWNER-MODE-LEGS's `carry` in `dev/programme/rosters/wave-r11-groups.json`. Carry: R11-OWNER-MODE-LEGS
- Carry 2 (from R11-OWNER-FROST-HOLD, body item 0846c1b4, the composition owed by this group's merge if FROST-HOLD lands first): `frost_hold` is not on `origin/main` (`6a58ba5cb30b`; FROST-HOLD is #3882, open), so there is nothing to compose with at this head. FROST-HOLD's design (`e91a4e30`) places frost before this group, but this group lands on a main without `frost_hold`. Whichever of the two merges second composes them as design `57d5d278`'s "Interaction with the frost hold" states: `hold_supply → frost_hold.gate → fault_hold.gate` (frost's ON passes); frost's cut-off arm consulted after `fault_hold.consult` in `early_cutoff.on_room_event`; `device-fault` decided before `frost-hold` in `duty_ledger.step_verdict`; and no frost row written while `_fault_stands` holds. Lands in R11-OWNER-FROST-HOLD's `carry` in `dev/programme/rosters/wave-r11-groups.json`. Carry: R11-OWNER-FROST-HOLD
- Carry 1, FAULT-TEXT's carry (flag-prefill-reach): FAULT-TEXT has not merged (`origin/main` has no pre-fill Fault alarm text), and this group merges first, so per that carry FAULT-TEXT adds the hold's 10 minutes to the pre-fill rows on its rebase; it stands in this group's own `carry` in `dev/programme/rosters/wave-r11-groups.json` and lands in R11-OWNER-FAULT-TEXT's. Carry: R11-OWNER-FAULT-TEXT

## Friction

none

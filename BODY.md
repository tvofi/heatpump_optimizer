Closes #3856. Builds the approved design `design/R11-OWNER-FAULT-HOLD` at `57d5d278f0c5` (verdict `design-verdict/R11-OWNER-FAULT-HOLD` `e9598ceb7e`, `Design review: approve`): while the pump's fault alarm has been on for 10 minutes, the integration stops commanding the pump.

## Summary

`fault_hold.py` (new, a leaf over `const`, `entry_config`, `inputs` and `issues`) owns a per-entry latch and the `pump_fault_hold` repair. It reads the fault slot with `inputs.UNBOUNDED`, so a push-only fault still reads at any age. The latch starts at the alarm's `last_changed`, bounded to now. A legible off resets it. Unavailable, unknown or not-boolean readings neither start a hold nor end one. Optimizer Off and the `fault_hold` option set to off clear it. An unloaded entry (`released`) answers False and raises nothing. The hold starts at `FAULT_HOLD_AFTER` (10 min).

While the latch holds:

- `pump_arbiter.apply` consults once per pass, before the duty-off return, so the latch moves for every install. In control, `_arbitrate` returns before `_adopt`, `hold`, `_command` and the night schedule (`_fault_stands`). It drops `space_before` and the pending retries and clears `pump_write_ignored`.
- `_lead_mode` writes no mode.
- `release` writes no baseline row; `off_restore`'s space restore still runs.
- The cycle's and the step tick's switch gate (`fault_hold.gate`, after `supply_hold.hold_supply` in `_write_supply`) turns an OFF into "leave" and marks `supply_held`, so the step tick lands it after the clear. An ON passes.
- `early_cutoff.on_room_event` does not cut.
- `_command_frequency` returns.
- `heat_curve.publish`, the one sink of every displace (cycle, peak-guard engage and release), sends nothing.

The step ledger moves verbatim to `duty_ledger.py` (new; the structure payment). A step in which any pass held is `device-fault`, decided before every other verdict. The onset step keeps its own verdict because a row closes when its step ends. The option `fault_hold` (default on) sits beside the Fault alarm entity. Docs: `docs/configuration.md` (two rows, the ledger line and a "A pump that reports a fault" section), `docs/architecture.md` (module map and the HA boundary counts), the repair in `README.md`.

The design's carries, each built here:

- **skip-log**: the held mark suppresses the cooling debug line; the gate logs its own.
- **multi-entry**: one domain-wide id, cleared only when no entry on the same `hass` holds.
- **hand-reset**: the repair text says to turn Optimizer active off first.
- **entry-released / publish-released**: `holding(released=...)`, with `publish` given `released=self._entry_released` on the coordinator's existing argument line.
- **supply-after-clear**: the held mark.
- **ignored-repair**: cleared in `_fault_stands`.
- **unload-row**: built.
- **onset-step**: docs ledger line.
- **cc-headroom**: `functions_cc_over_15` unchanged; the fault folds into `_arbitrate`'s existing return condition.
- **bundle-latch-count**: `dev/audit/harnesses/r11_owner_fault_latch.py bundle --timeline T`.
- **ledger-constants**: `TANK_RISE_C` and `RUN_SETTLE` live in `duty_ledger.py`; `duty_ledger` imports only `plan_step`.
- **publish-config**: `holding` builds its `InputReader` from `dict(config)`.
- **duty-off-latch-age**: `gate` and the cut-off call `consult`, which reads, so there is no lag.
- **reported-displace**: under the hold the coordinator still records the computed displace (`_ecl110_current_displace`). `docs/configuration.md` says the diagnostics report the computed displace, which was not sent, and shows the latch under `fault_hold`.
- **fallback-private-reach**: not needed; the coordinator class did not grow.
- **seam-actuation**: neither seam group has landed.

Departures, raised: FROST-HOLD (`e91a4e30`), which the design orders ahead of this group, is not on main. So the gate chain is `hold_supply → fault_hold.gate`, and the cut-off consults `fault_hold` directly, with no frost hook to wrap. The frost composition is carried to FROST-HOLD below. The latch reads the alarm's `last_changed` directly. That is registered as a `state_age` disposition (`fault_hold.py::holding`) in `tests/entities.py`, for the same reason `supply_hold.switch_age` reads it: the value's age, not the entity's last report.

## Head

`5eb7083aaaf2377fcac99f287c91653b73ebf4a5`, measured against its merge base `8ef450936a1786abf4bb9610dc3336da4e77e8de`. `origin/main` is `1207ee13b0e439a4acefccabace691785af2ebad` at the stamp; `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged in (fixer step 6). Stamped 2026-11-22T19:16Z. Commits, `git log 8ef450936a17..HEAD`:

- `6477e5f7df` R11-OWNER-FAULT-HOLD: suspend actuation while the pump reports a latched fault
- `149b770946` R11-OWNER-FAULT-HOLD: record block_duty's closure with the two new modules; harness INERT READS
- `bac3d94412` R11-OWNER-FAULT-HOLD: closures re-recorded for the two new modules; the fault latch's value-age disposition; tree counts the modules move; the mutation harness
- `62a9fe6873` R11-OWNER-FAULT-HOLD: INERT READS for the mutation harness
- `dacb2f71db` R11-OWNER-FAULT-HOLD: entities.py closure gains the two new modules (two-step record: its only reds were the full-coverage checks it reads from that closure); deployment-shape note keeps 167 pairs
- `5eb7083aaa` R11-OWNER-FAULT-HOLD: duty_ledger.step_verdict (tests/layout.py owns the name verdict); faulted keyword-required; the diagnostics row checked

Read the diff three-dot.

## Mutation proof

`python3 dev/audit/harnesses/r11_owner_fault_hold_mutants.py HEAD`. It runs 32 hand mutants, each deleting or weakening one production predicate in a `git archive` copy, and drives the fault-hold block of `tests/features.py` and `tests/block_duty.py`. Unmutated baseline: 0 failing. Result: `RESULT mutants=32`, `RESULT survived=0`. Examples, with the check that goes red:

- the 10-minute comparison `>=` → `>`: "the hold starts exactly at FAULT_HOLD_AFTER and not a second before it".
- the comparison dropped: "null control: the same pass with the alarm on for 9 minutes writes the step's row" and 8 more.
- `max_age_minutes=UNBOUNDED` dropped: "a fault on for 70 minutes on an on-change source holds at the first consult, after Off -> On and after a reload" and 19 more.
- the legible-off reset deleted: "a legible off ends the hold".
- the unusable branch resets: "unavailable and unknown keep the latch's start…" and "an unusable reading never ends an active hold".
- `released` guard deleted: "an unloaded entry's displace raises no fault repair".
- `apply`'s consult → `False`: "a fault alarm on for 11 minutes: the control pass writes nothing into the pump" and 9 more.
- `_arbitrate`'s `or _fault_stands(...)` deleted: 4 red.
- `_lead_mode`'s skip deleted: "a switch-on under the hold writes no mode ahead of it".
- `release`'s `and not faulted` deleted: "unload under the hold writes no baseline row".
- `step_verdict`'s fault-first branch → `if False:`: "every held step of the ledger is device-fault (hot water, space)" and 4 more.
- `publish`'s return deleted: "a displace under the hold is not published".
- the cut-off consult → `if False:`: "a warm room under the hold does not cut the pump".
- the frequency guard dropped: "the compressor frequency is not commanded under the hold…".
- the coordinator's gate replaced by its argument: "the cycle's OFF under the hold is left, and the step tick writes it once the alarm clears".
- the diagnostics row deleted: "the diagnostics download shows the fault latch under fault_hold".
- the cut-off's `entry=self.entry` dropped: "the cycle arms the early cut-off with its entry, the key of the fault latch".

Failing first: the same tests against the merge base's `custom_components/` (head `tests/` and `tools/`) stop at `ImportError: cannot import name 'fault_hold'` (the block) and `cannot import name 'duty_ledger'` (`block_duty.py`).

## Null control

Every behaviour check is paired with today's behaviour on the same fixture: the alarm on for 9 minutes, reading off, or `fault_hold` off writes what the merge base writes. The synthetic replay's null is `--opt-out`: `RESULT latched_actuating=260` (every pass inside the latch past 10 minutes actuates) against `0` with the hold; `RESULT repairs=0` against `1`; `RESULT short_held=0` both ways.

## Figures

- `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'exec(open("P").read())' 'R.section("R11-OWNER-FAULT-HOLD' 'R.section("duty-switch restart learning, part A'`, P from `--emit-prelude P` with the same two markers: `ALL 47 FEATURES BLOCK PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/block_duty.py`: `ALL 154 BLOCK DUTY CHECKS PASSED`.
- `python3 dev/audit/harnesses/r11_owner_fault_hold_mutants.py HEAD`: `RESULT mutants=32`, `RESULT survived=0`, baseline 0 failing.
- `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_owner_fault_latch.py synthetic`: `latched_actuating=0`, `short_held=0`, `short_faults=6`, `repairs=1`; with `--opt-out`: `latched_actuating=260`, `short_held=0`, `repairs=0`.
- `python3 tests/structure.py`: every row at or under budget. `module_excess_loc` re-recorded 21779 → 21694, from the ledger's move out of `pump_arbiter.py` and the three selector helpers folded into `_select` in `config_flow.py`. `class_excess_loc` 17317, `max_class_loc` 7868, `functions_cc_over_15` 26, `coordinator_private_reach` 0 and `import_cycle_modules` 0 are unchanged.
- `python3 tests/comment_ratchet.py`: long units 2300 → 2299.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`: `MODE: SCOPED -- 30 script(s) run, 3 scoped out`.
- `tests/derive_closures.sh --single S`: recorded locally (Linux) for the 21 scripts `tools/pr/ci_predict.py` listed UNDER-SCOPED, each exiting 0. `tests/entities.py` is the exception: it was recorded two-step (`--record-only`, then `closure.py merge --partial --allow-failures`). Its only two reds in that run were the deployment-shape checks that read its own closure's full coverage. That closure gains `duty_ledger.py` and `fault_hold.py` only through the merge (`2 of 2748 ENTITY CHECKS FAILED`, both `#1218`).
- Run here at this head, each exit 0: `tests/backtest.py`, `tests/edge.py`, `tests/frontend.py`, `tests/md_tables.mjs`, `tests/open_meteo.py`, `tests/optimality.py` and `tests/validate.py` (`GOLDEN_MODE=drift`, `GOLDEN_REF` the merge base), beside the 22 recorded above and `tests/block_duty.py`. `tests/stress.py` is left to CI: it measures the machine under the gate lease.
- `PYTHONPATH=tests/hastub python3 tests/features.py` at this head: `ALL 6075 FEATURE CHECKS PASSED`.
- The first `tools/pr/prepr.sh` run, at `dacb2f71db`, refused twice. `no-copies`: `tests/layout.py` defines `verdict`, and so did `duty_ledger` (now `step_verdict`). `pr-body`: an empty `## Raise justification`, now omitted. Its diff mutants left 16 survivors: two closed by code and a check (`faulted` keyword-required, the diagnostics row), the rest disposed below. Both refusals are fixed in `5eb7083aaa`, and the receipt below is the run at this head.
- `PREPR_SKIP_CLOSURES=1 MUTANT_CMD=<the group's self-test> bash tools/pr/prepr.sh <this body>` (the closures were recorded above): `PRE-PR: 5eb7083aaaf2377fcac99f287c91653b73ebf4a5 000000000000000000000000000000000000 rc=0`. Receipt `Prepr: 5eb7083aaaf2377fcac99f287c91653b73ebf4a5 694afc12ec199911aaa6976f3cdb58e0d1687c6b`.
- `python3 tools/pr/ci_predict.py`: no closures, fast, governance or instrument red predicted; 40 unpinned sites, listed below.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 8ef450936a17 HEAD`: `Architecture score: dS +0.0006 IMPROVES`, from `coord_footprint` 2525 → 2524. No gate metric rises. The mechanism: `_fault_stands` takes `hass` rather than the coordinator, and `apply` builds its inputs once instead of twice. With the coordinator passed to `_fault_stands`, the same tree read 2529 (WORSENS).

## Red checks

`mutation` at 5eb7083aaaf2 is red by construction on the sites under `## Unpinned sites`; mutation-autofix pins the killed sites after the push.

## Unpinned sites

The 40 sites `tools/pr/ci_predict.py` lists, then the survivors of prepr's diff mutants under the group's self-test (`MUTANT_CMD`: the fault-hold block and `tests/block_duty.py`) that the 40 do not already name. Every fault-hold predicate is killed by `r11_owner_fault_hold_mutants.py` above.

- custom_components/heatpump_optimizer/coordinator.py:10810 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:61 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:61 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:61 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:94 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:96 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:98 GUARD_OFF: pinned by mutation-autofix
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
- custom_components/heatpump_optimizer/pump_arbiter.py:1839 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1891 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1910 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1914 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1943 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:2166 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:7671 STMT_DEL: pinned by mutation-autofix; the `heat_curve.publish` call statement, which this diff only extends with `released=`, driven by the existing heat-curve displace checks in `tests/features.py`
- custom_components/heatpump_optimizer/duty_ledger.py:31 CONST_SWAP: pinned by mutation-autofix; a ledger line moved verbatim from `pump_arbiter.py`, killed there by `tests/features.py`'s pump-duty arbiter section (the re-keyed `tests/mutation_ledger/killed_by/duty_ledger.py/` rows); the group's self-test does not drive it
- custom_components/heatpump_optimizer/duty_ledger.py:35 CONST_SWAP: pinned by mutation-autofix; a ledger line moved verbatim from `pump_arbiter.py`, killed there by `tests/features.py`'s pump-duty arbiter section (the re-keyed `tests/mutation_ledger/killed_by/duty_ledger.py/` rows); the group's self-test does not drive it
- custom_components/heatpump_optimizer/duty_ledger.py:57 CONST_SWAP: pinned by mutation-autofix; a ledger line moved verbatim from `pump_arbiter.py`, killed there by `tests/features.py`'s pump-duty arbiter section (the re-keyed `tests/mutation_ledger/killed_by/duty_ledger.py/` rows); the group's self-test does not drive it
- custom_components/heatpump_optimizer/duty_ledger.py:59 GUARD_OFF: pinned by mutation-autofix; a ledger line moved verbatim from `pump_arbiter.py`, killed there by `tests/features.py`'s pump-duty arbiter section (the re-keyed `tests/mutation_ledger/killed_by/duty_ledger.py/` rows); the group's self-test does not drive it
- custom_components/heatpump_optimizer/duty_ledger.py:62 CONST_SWAP: pinned by mutation-autofix; a ledger line moved verbatim from `pump_arbiter.py`, killed there by `tests/features.py`'s pump-duty arbiter section (the re-keyed `tests/mutation_ledger/killed_by/duty_ledger.py/` rows); the group's self-test does not drive it
- custom_components/heatpump_optimizer/duty_ledger.py:87 CMP_BOUND: pinned by mutation-autofix; a ledger line moved verbatim from `pump_arbiter.py`, killed there by `tests/features.py`'s pump-duty arbiter section (the re-keyed `tests/mutation_ledger/killed_by/duty_ledger.py/` rows); the group's self-test does not drive it
- custom_components/heatpump_optimizer/duty_ledger.py:35 STMT_DEL: pinned by mutation-autofix; a ledger line moved verbatim from `pump_arbiter.py`, killed there by `tests/features.py`'s pump-duty arbiter section (the re-keyed `tests/mutation_ledger/killed_by/duty_ledger.py/` rows); the group's self-test does not drive it
- custom_components/heatpump_optimizer/duty_ledger.py:49 STMT_DEL: pinned by mutation-autofix; a ledger line moved verbatim from `pump_arbiter.py`, killed there by `tests/features.py`'s pump-duty arbiter section (the re-keyed `tests/mutation_ledger/killed_by/duty_ledger.py/` rows); the group's self-test does not drive it
- custom_components/heatpump_optimizer/duty_ledger.py:60 STMT_DEL: pinned by mutation-autofix; a ledger line moved verbatim from `pump_arbiter.py`, killed there by `tests/features.py`'s pump-duty arbiter section (the re-keyed `tests/mutation_ledger/killed_by/duty_ledger.py/` rows); the group's self-test does not drive it

## Forward-carry

- Carry 0 (from R11-OWNER-MODE-LEGS, body item 411606ae, the pin "the fault hold wins with a young leg latched"): not buildable here. MODE-LEGS' `_kept_leg` is not on main at this base (`8ef450936a17`; its head is `handoff/r11-owner-mode-legs`). The hold returns before `_command` in `_arbitrate` (`_fault_stands`), downstream of `_served`, so a latched leg writes nothing under it by construction. Whichever of the two lands second owes the pin, as that body states; with this group first it is MODE-LEGS'. It lands in R11-OWNER-MODE-LEGS's `carry` in `dev/programme/rosters/wave-r11-groups.json`. Carry: R11-OWNER-MODE-LEGS
- FROST-HOLD's design (`e91a4e30`) places frost before this group, but this group lands on a main without `frost_hold`. Whichever of the two merges second composes them as design `57d5d278`'s "Interaction with the frost hold" states: `hold_supply → frost_hold.gate → fault_hold.gate` (frost's ON passes); frost's cut-off arm consulted after `fault_hold.consult` in `early_cutoff.on_room_event`; `device-fault` decided before `frost-hold` in `duty_ledger.step_verdict` (the ledger moved here); and no frost row written while `_fault_stands` holds. Lands in R11-OWNER-FROST-HOLD's `carry` in `dev/programme/rosters/wave-r11-groups.json`. Carry: R11-OWNER-FROST-HOLD
- Carry 1, FAULT-TEXT's carry (flag-prefill-reach): FAULT-TEXT has not merged (`origin/main` has no pre-fill Fault alarm text), and this group merges first, so per that carry FAULT-TEXT adds the hold's 10 minutes to the pre-fill rows on its rebase; it stands in this group's own `carry` in `dev/programme/rosters/wave-r11-groups.json` and lands in R11-OWNER-FAULT-TEXT's. Carry: R11-OWNER-FAULT-TEXT

## Friction

none

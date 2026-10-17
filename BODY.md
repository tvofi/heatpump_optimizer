Why this change, and what it measures.

The R10-N-log-flood barrier (`tests/entities.py` `_R10_LOG_ALLOWED_BY_REASON`) lists eight unlatched WARNING/ERROR sites as OWED: each is reached every cycle or solve, and each is triggered by a condition that persists. This PR routes seven of them through the transition latch, demotes the eighth, deletes the OWED entries, and adds the runtime-probe arms that measure them.

- `coordinator._note_solve_failure`, `_command_valve_target` (three sites), `pump_arbiter._space_target` and `inputs._age_gate` route through `log_latch._log_held`, a leaf module, so the pump arbiter and the input reader import the latch without closing an import cycle through the coordinator.
- The latch owner is whatever outlives the call: the coordinator for its own sites, `hass` for the arbiter and the reader. `ArbiterInputs` is rebuilt every pass and `InputReader` every read, so a latch keyed on either would warn every time; `hass` is stable per install, as the outage latches are. The owner must be weak-referenceable: a caller that passes none (an `ArbiterInputs` snapshot built with `hass=None`) logs the condition every call rather than raising into a cycle.
- `optimizer.optimize`, `_solve_space` and `_optimize_space_only` are demoted to DEBUG: a failed solve already surfaces once through the coordinator's latched `_note_solve_failure`, and the optimizer cannot latch on the coordinator -- it runs in a worker process with a fresh optimizer per solve, and importing the coordinator would put HA glue in the pure solver.
- The stale-plan hold is demoted to DEBUG: its text renders the plan's age and the failed-solve count, both of which advance every cycle while the condition holds, so no stable latched key can suppress it without dropping what the line reports. The call is reached only while stale, so a latch's clear path never runs either; a stable key would warn once per process and stay silent on a later spell. The once-per-occurrence signal is the notifier's `EVENT_PLAN_STALE`, which carries the age -- the existing "UX-4 plan stale" check pins it firing once, staying quiet on repeats, and firing again after the plan was fresh.
- The five killed-pin rows move with `_log_held` to `mutation_ledger/killed_by/log_latch.py/`, each keeping the digest its mutant line carries.

## Head

`7ef037831f46a4f5d89d4c2e9762a0e51e61fef7`

## Mutation proof

Two mutants of the round-3 production lines, each over `tests/features.py`, restored after; the fixed tree reads `ALL 4154 FEATURE CHECKS PASSED` (exit 0).

1. Replace the `_LOGGER.debug` in `coordinator._apply_action` with the latch call the demotion replaced, `_log_held(self, "stale_plan", True, ...)`; `PYTHONPATH=tests/hastub python3 tests/features.py` prints
   `FAIL #2226/#2351: the stale-plan hold logs its advancing age and failure count at DEBUG, so a persisting stale plan never warns every cycle  [[('WARNING', "Plan is 430 minutes old after 1 failed solves; ..."), ... four WARNINGs, one per pass]]`
   and ends `1 of 4154 FEATURE CHECKS FAILED` (exit 1).
2. Delete the owner guard in `log_latch._log_held` (`held = {} if owner is None else _HELD_CONDITIONS.setdefault(owner, {})` back to `held = _HELD_CONDITIONS.setdefault(owner, {})`); the same script prints
   `FAIL #2351: a None owner is logged every call and never raises -- no stable key means no transition to hold, not a cycle-ending exception  [errors=["TypeError: cannot create weak reference to 'NoneType' object", ... four times] rows=[]]`
   and ends `1 of 4154 FEATURE CHECKS FAILED` (exit 1).

## Null control

The runtime probe's `control` arm (a 48-row forecast, prices present) reads `floods=0` at base, at the previous head and at this head. The class enumerator's planted latched fixture is not a seam, and its planted unlatched one is.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED`; `max_class_loc 8635 <= 8635`, `class_excess_loc 18459 <= 18459`, `import_cycle_modules 0 <= 0`, `seam_cut_total 752 <= 752` (the demotion replaces the latch call line for line; no budget moved).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` -- `ALL 2346 ENTITY CHECKS PASSED`, including the R10 N-log-flood barrier over its reasoned list and its planted-site perturbation.
- `PYTHONPATH=tests/hastub python3 tests/features.py` -- `ALL 4154 FEATURE CHECKS PASSED`, including the new stale-plan cadence arm (0 WARNING and 4 DEBUG over four advancing passes) and the ownerless-owner arm.
- `PYTHONPATH=tests/hastub python3 tests/solar_alignment.py` -- `ALL SOLAR ALIGNMENT CHECKS PASSED` (it is the driver the re-keyed `log_latch` pins name).
- `PYTHONPATH=tests/hastub python3 tests/block_duty.py` -- `ALL 46 BLOCK DUTY CHECKS PASSED`; `tests/deployment_shape.py` -- `ALL DEPLOYMENT SHAPE CHECKS PASSED`; `tests/doc_claims.py` -- `ALL 169 checks PASSED`; `tests/validate.py` -- `NO ISSUES`.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` -- `arch_modules_on_disk=78 modules`, `arch_map_listed=78 modules`, and the run leaves `dev/audit/rounds/round4/D6` byte-identical (`git status --porcelain` empty there).
- `PYTHONPATH=tests/hastub python3 tests/arch_score.py` -- `ALL 204 ARCHITECTURE SCORE CHECKS PASSED`.
- `python3 dev/audit/rounds/round10/D14/log_flood/enumerate.py custom_components/heatpump_optimizer` -- `sites=70 latched=6 seams=64` at this head; the same command over `git archive 81b7aa9ff976413ec98592045930647c0e0bac73` prints `sites=80 latched=6 seams=74` and lists `_apply_action`, `_age_gate`, `_command_valve_target` (3), `_note_solve_failure`, `optimize`, `_solve_space`, `_optimize_space_only` and `_space_target` as SEAM. The 64 returning seams are the class's pre-existing dispositions in `dev/audit/rounds/round10/sweep-N-log-flood.md` (guarded, not reached per cycle, per-event actuation, or the latch itself), and the barrier above refuses an unlisted one. The census stops counting the stale-plan hold at either head -- a latch or DEBUG call is not a `_LOGGER.warning` -- so the runtime probe, not the census, is what shows that seam closed rather than moved.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/log_flood/probe.py` -- every arm `floods=0`, exit 0. The same file, copied into a `git archive 81b7aa9ff976413ec98592045930647c0e0bac73` export, reads `stale_plan.floods=2` and exits 1 with `4x Optimization failed: probe solve failure` and `4x Plan is # minutes old after # failed solves; ...`; copied into the previous head's export (`fc9d9186dfd9195992bd87a83dc5eb543e509cf8`) it reads `stale_plan.floods=1` and exits 1 with `4x Plan is # minutes old after # failed solves; ...` -- the per-cycle flood the demotion removes. `--perturb` on this head moves `weather_fetch_fails` from `floods=0` to `floods=1` (`4x No forecast data returned ...`) and exits 1.
- `python3 -I tools/audit/archscore/gate.py --base 81b7aa9ff976413ec98592045930647c0e0bac73 --head 7ef037831f46a4f5d89d4c2e9762a0e51e61fef7 --body <this body>` -- `Architecture score: dS +0.0000 NULL`, `PASS: dS +0.0000 NULL, no gate metric rose`.
- `python3 tests/mutation_table.py --scope changed --base origin/main --max 0 --jobs 1` -- `4343 unpinned site(s) of 6128 candidate sites`, "the ledger agrees with the deterministic inventory", `MUTATION TABLE PASSED (empty pool)` (the mutants themselves are CI's `mutation` job).
- `node tools/policy/policy_lint.mjs --pr-body <this body> --head 7ef037831f46a4f5d89d4c2e9762a0e51e61fef7 --title "record(mutation): re-key _log_held's killed pins to log_latch.py" --author app/hpo-author --paths-file <changed> --existing-file <added> --red arch-score --red "fast (3.14)" --red mutation --red pr-contract` -- `PR-BODY: 0 error(s)` (no token here, so its red-history walk skips rather than reads; `--red` names each check this body answers).
- The scoped gate's own selection, `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`, prints `MODE: SCOPED -- 29 script(s) run, 4 scoped out`; the scripts this seat ran locally are the ones above, and the rest (including `stress.py`, `golden.py` and `harness_headers.py`, which need the machine lease) are CI's `fast (3.14)` job on this head.

## Red checks

- `arch-score` -- red at `83bf0770c`: `coord_footprint 2547 -> 2552` (dS -0.0028), from threading the coordinator into `pump_arbiter._space_target` only to give the latch an owner; `coord_footprint` charges every module-level function handed the coordinator. Cheaper detector: `python3 -I tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`, no runner and no queue; measured standing cost 65 s on this seat. No cheaper check exists that is not that same computation. The owner is `inp.hass`, already in the snapshot, and the function keeps its signature; the gate now reads `dS +0.0000 NULL`.
- `fast (3.14)` -- red at `83bf0770c` on four scripts, every one a count the new leaf moved: `tests/entities.py` (the #1218 selection-cost note pinned 95 production files; `log_latch.py` makes 96), `tests/features.py` (the `#2226` probe attached its handler to the coordinator module's logger, so the latch's child logger went unread), `tests/structure.py` (`class_excess_loc 18468 -> 18459` unrecorded), and `tests/harness_headers.py` (the D6 census header said 77 modules; the executed harness printed 78). Cheaper detector: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` selects and runs exactly these scripts locally; its `MODE: SCOPED` line names the set, and its standing cost is the scripts' own minutes. The counts are self-invalidating figures about the tree that carries them, and each owning check already refuses a stale one -- none was missing, they were not run at the pushed head.
- `mutation` -- red at `83bf0770c`: `MUTATION TABLE REFUSED -- the ledger is not in canonical form`, on five re-keyed `log_latch.py` rows written by hand. Cheaper detector: that refusal is the first seconds of the command CI runs, with no baseline paid before it. `python3 tests/mutation_table.py --normalize` rewrote the rows to canonical bytes; the command now reports the ledger agrees with the deterministic inventory.
- `pr-contract` -- red at `83bf0770c`: `red-history` derives every failure conclusion across the branch's committed heads and refuses a body that does not name each. Cheaper detector: `tools/pr/prepr.sh` step 7c passes every red the pushed commits carry to the same `policy_lint.mjs --pr-body`. Its stated limit is that it reads pushed commits only, so the first handoff push cannot see its own reds -- this body names them, and re-running prepr after the reds appear is the answer, not a new check.

## Forward-carry

none

## Friction

none

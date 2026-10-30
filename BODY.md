R10-SAV-ACTUATION (#2492 carry 5, seam 2). The cycle wrote the pump's power switch once per optimization interval (30 min by default), so a plan step's change reached the pump at the next cycle -- as late as one interval past the step boundary -- and a step's duty verdict in the arbiter's ledger depended on where the cycle fell against the 15-minute step grid. This PR writes the switch at the step boundary from a one-minute tick, and makes the ledger read the meter at each tick rather than the cycle's sample.

Refs #2492. Not closed here: carry 5 seam 2's two owed controls are met (Null control, Mutation proof), and one residue of the duty ledger is routed under Forward-carry to #2492.

**Design note (size M; designer.md binds L/XL only, the brief asked for the note, so it is here).**
- **Owning seam.** The switch's one writer stays `pump_arbiter.switch_supply`. The gated write -- the early cut-off's `MIN_OFF` hold (`early_cutoff.allow_on`) and the blocked-mode OFF skip -- is the coordinator's `_write_supply`, extracted from `_apply_action`, which both the cycle and the tick call; the pure skip decision moved out of the coordinator class into `pump_arbiter.supply_write`. The tick is `pump_arbiter.supply_tick`, armed once by `pump_arbiter.note_supply` from the cycle's write; it takes plain values (`SupplyWiring`: the published `arbiter_inputs` builder, the boost record, the gated write), as `early_cutoff` does, never the coordinator. `tests/seam_map.json` gives `_write_supply` the seam `core`, beside `_apply_action`.
- **Shape.** `ArbiterState` gains `supply` (step start, the command the plan gave it) and `supply_unsub`. Each cycle's write records its command; at each minute, a tick that finds a new step derives that step's command (`step_supply`: the plan's switch for the step, on under a live boost, `None` for a non-plan mode, an experiment, a stale or missing plan, or an instant outside the plan) and writes it **only where it differs from the last command**. The unload (`pump_arbiter.release`) drops the tick (`release_supply`); the arbiter's duty-mode listeners do not, since the supply tick serves every duty mode.
- **One rule for the plan's switch.** `thermal_model.plan_step_runs(result, i)` is the one owner of "does the plan switch the pump on at step i" (`heat_pump_on_schedule`, else `planned_draw_runs` on the step's two draws), read by `optimizer.get_current_action`, the coordinator's published schedule and the tick; the two inline copies are gone.
- **The ledger's reading.** `ArbiterInputs.measured_power_kw` is now `pump_arbiter.live_power_kw` (the configured meter through `InputReader`, at each pass) instead of `_measured_power`, which `_update_current_state` samples once per cycle. Without it the switch moves at the boundary but the ledger folds a reading frozen at the cycle, and the phase dependence stays (mutant M4).
- **Alternatives, and why each lost.** (a) Re-adopt the whole action at each boundary (`boost.adopt_plan(get_current_action(result, now))` then `_apply_action`): it re-arms `early_cutoff` as a new cycle, rewrites the switch every step (undoing a cut after `MIN_OFF`), republishes the ECL110 command and moves `_current_action` under the learners that replay the interval; `get_current_action` also needs the solve's optimizer instance. (b) Write the step's command unconditionally at each boundary: a cut-off on a step the plan keeps on would be undone at the next boundary, against `early_cutoff`'s documented hold (mutant M3). (c) Put the tick in the coordinator class: every structure row sits at zero headroom and `coordinator_attrs` would grow by the record; the side table on `ArbiterState` is the per-coordinator `WeakKeyDictionary` pattern step 17 names. (d) Hand the tick the coordinator: `tools/audit/archscore/` charges every module function taking it (`coord_footprint` rose 2409 -> 2430 on the first cut of this branch); the `SupplyWiring` shape brings it back to `dS +0.0000 NULL`.
- **Sibling sites.** Enumerated as the call sites of `switch_supply` and every reader of the plan's switch rule (Figures): the cycle (`_apply_action` -> `_write_supply`), the tick, and the early cut-off (`early_cutoff.on_room_event`, which writes OFF once and is held by the tick's change-only rule: check 3). The ECL110 displacement (`async_publish_current_action`) and the frequency command are the cycle's other actuators keyed to its phase; they are outside this carry's supply switch and are not changed.

**D15 L5 (roster carry).** The `pump_duty` store domain now declares `written/silent/*` and, as the class the same writer persists (`pump_arbiter._SLOTS + _NIGHT_SLOTS`), the four GCHV night-mode slots, bounded 0..23 and 0..59. The `peak_tracker` snapshot leaves are untouched.

## Head

`1a7150482145938296fd54385129147fedef6742`: the reviewed head `d26a00aa2` plus three commits, `R10-SAV-ACTUATION: pin the step tick's guards against a write the plan did not give` and `R10-SAV-ACTUATION: unload drops the one step tick two cycles armed` (checks in `tests/features.py` only), and `mutation ledger: pin thirteen killed sites` (files under `tests/mutation_ledger/killed_by/` only). No production line changed since `d26a00aa2`, whose merge base is `e5ddba1fad5e6eccfeceaeaaa249bc459963405b`. Figures taken at the earlier code head `3bc559015` (on `88c6ad5bb`) say so; the guard checks, the X mutants, `## Unpinned sites` and the `mutation` red are taken at this head. origin/main is at `2ab53fe90590` (`date -u`: Fri Oct 30 01:17 UTC 2026); `git merge-tree --write-tree origin/main HEAD` reports no conflict, so the branch is not merged forward (fixer.md step 6).

## Mutation proof

Each mutant deletes or neuters one seam's production line in a fresh worktree of the head, then the closure the diff's checks live in, `PYTHONPATH=tests/hastub python3 tests/features.py`, runs whole; the worktree is removed after. Every one is red, and only on the new section's checks (`4578` checks run each time):

- M1, the cycle no longer records or arms (the `pump_arbiter.note_supply(...)` line in `_apply_action` deleted): `2 of 4578 FEATURE CHECKS FAILED` -- `a synthetic install at cycle phase 0 and at 14 min books identical duty verdicts (#2492)`, `the step tick writes the switch at the boundary of each step whose command changes`.
- M2, the tick does not write (`supply_tick`'s `await wiring.write(on)` -> `pass`): `2 of 4578`, the same two.
- M3, the tick writes at every boundary, not on a change (`if on != last:` -> `if True:`): `2 of 4578` -- `the step tick writes the switch at the boundary ...`, `an early cut-off holds across a step boundary the plan keeps on`.
- M4, the ledger reads the cycle's sample (`arbiter_inputs`'s `measured_power_kw=pump_arbiter.live_power_kw(...)` -> `self._measured_power`): `1 of 4578` -- `a synthetic install at cycle phase 0 and at 14 min books identical duty verdicts (#2492)`.
- M5, the silent declaration removed from `store.DOMAINS["pump_duty"]`: `1 of 4578` -- `every slot the pump arbiter persists is declared in the pump_duty store domain`, printing `['written/silent/0']`.
- M6, the tick never armed (`note_supply`'s `async_track_time_interval(...)` -> a no-op): `2 of 4578`, the same two as M1.

The unmutated head: `ALL 4578 FEATURE CHECKS PASSED` (`tests/features.py` in the scoped gate, Figures). The mutant driver is a scratch script, not committed: each mutant is one `str.replace` asserted to match exactly once.

**Round 2: the step tick's guards (fix review `blocked` at `d26a00aa2`, mutation-vacuous).** The section "supply switch at step boundaries" gains `_sa_guarded`: the REAL coordinator runs one `_apply_action` at 06:00 (step 0, plan on, the cycle writes ON and arms the tick), then the armed tick fires at 06:15 (step 1, plan off). The null control is the run with nothing perturbed, where the tick writes `['turn_off']`; each guard's check perturbs one input and asserts the tick writes nothing. Each mutant is one `str.replace` on `pump_arbiter.py`, asserted to match exactly once, run against the section standalone (`tests/features.py`'s preamble plus the section and the five module-level names it reads), then restored:

- X1, `step_supply`'s live-boost branch (`if boosts.active(...): return True`) deleted: red on `the step tick writes nothing at a boundary under a live boost across a boundary whose plan step is off` (`['turn_off']`).
- X2, `step_supply`'s `system_identification` guard deleted: red on `... under a system_identification action`.
- X3, the mode/stale/plan guard narrowed to `if inp.plan is None:`: red on `... under a fixed (comfort) mode` and `... under a stale plan`. Split: X3a (mode term dropped) is red on the comfort check alone, X3b (`inp.plan_stale` dropped) on the stale check alone.
- X4, `supply_tick`'s `if inp.entry_released: return` deleted: red on `... under a released entry`.
- X5, `release`'s `release_supply(held)` deleted: red on `unload drops the one step tick two cycles armed`.
- X6, `note_supply`'s arm-once guard (`if held.supply_unsub is not None: return`, the ledger's `pump_arbiter.py:1219 GUARD_OFF` survivor) deleted: red on the same check -- the unload run takes two cycles, and the second arms a listener `release_supply` never drops (`dropped != ticks`).

Each mutant is red on exactly the check named and no other; the unmutated section prints `ALL 12 FEATURE CHECKS PASSED`, and the null run (`guard=None`) writes `['turn_off']`, so each check's empty write list is the guard's doing, not a tick that never fired. The ledger drive (`## Unpinned sites`) independently records the 1188, 1190, 1192 and 1246 sites killed by `tests/features.py`. X5's line carries no ledger operator, so its proof is this mutant alone.

## Unpinned sites

`PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py --jobs 4 --budget-minutes 60` at the guard-check commit (no production change since): `PIN KILLED: 13 pinned, 13 left unpinned (8 survived, 5 not started for the budget, ...)`. Its null control (`coordinator.py:504 NULL_COMMENT`) survived and the `tests/features.py` baseline read `rc=0 failed=0`. The 13 are committed under `tests/mutation_ledger/killed_by/` (`pump_arbiter.py` 377 CMP_BOUND x2, 377 GUARD_OFF, 379 RETURN_DEL, 1174 BOOLOP and GUARD_OFF, 1188, 1190 and 1192 GUARD_OFF, 1195 RETURN_DEL, 1246, 1252 and 1259 GUARD_OFF). The four sites the review named as surviving (1188, 1190, 1192, 1246) are among them. `--scripts` was narrowed to `tests/features.py`, the one driver that reaches the step tick (no other script in `tests/` names `supply_tick`, `step_supply` or `note_supply`); a survivor there may still die under another driver in CI's lane.

Survivors, each **not pinned and not triaged here** (a triage is a verdict the reviewer judges, and none is automated, `ci-autofix.md`); each is the next round's or the reviewer's call:

- `custom_components/heatpump_optimizer/coordinator.py:7607 GUARD_OFF` (`_write_supply`'s `elif switch_entity:`): the branch only logs a debug line; equivalent in behaviour. The review asked for a recorded verdict; proposed `survivor_triage` verdict `equivalent`, not written in this round because it needs the reviewer's agreement first.
- `custom_components/heatpump_optimizer/pump_arbiter.py:549 RETURN_DEL` (`live_power_kw`'s `return reading.value if reading.ok else None`): not analysed this round.
- `custom_components/heatpump_optimizer/pump_arbiter.py:1176 RETURN_DEL` (`supply_write`'s trailing `return None`): deleting it returns `None` implicitly, equivalent.
- `custom_components/heatpump_optimizer/pump_arbiter.py:1195 CMP_BOUND` (`i >= len(...)` bound): not analysed this round; the test plan is as long as its timestamps, so the bound is not reached.
- `custom_components/heatpump_optimizer/pump_arbiter.py:1219 GUARD_OFF` (`note_supply`'s arm-once guard): a live defect under the mutant -- each cycle armed a listener unload never dropped. Now killed by X6 (`unload drops the one step tick two cycles armed`, committed after the drive); its ledger pin is left to `mutation-autofix`, which pins a killed site, since a second local drive did not fit this round's time.
- `custom_components/heatpump_optimizer/pump_arbiter.py:1222 GUARD_OFF` (`note_supply`'s no-switch-entity return): with no switch the gated write writes nothing.
- `custom_components/heatpump_optimizer/pump_arbiter.py:1243 GUARD_OFF` (`supply_tick`'s same-step return): within a step `step_supply` returns the step's own command, so the change-only rule writes nothing.
- `custom_components/heatpump_optimizer/pump_arbiter.py:1249 GUARD_OFF` (`if on is None: return`): with the guard off, `None != last` writes `None` through `supply_write`, which skips it.

Not started for the budget (`plan_step_runs`), each pinned by `mutation-autofix` if killed, else a survivor for the next round:

- `custom_components/heatpump_optimizer/thermal_model.py:1335 BOOLOP`: not started in the local drive's budget
- `custom_components/heatpump_optimizer/thermal_model.py:1335 CMP_BOUND`: not started in the local drive's budget
- `custom_components/heatpump_optimizer/thermal_model.py:1335 GUARD_OFF`: not started in the local drive's budget
- `custom_components/heatpump_optimizer/thermal_model.py:1338 CMP_BOUND`: not started in the local drive's budget
- `custom_components/heatpump_optimizer/thermal_model.py:1338 RETURN_DEL`: not started in the local drive's budget

## Null control

The same block at the merge base `88c6ad5bb` (the base's production code, this branch's checks): `3 of 4` fail.
- Phase 0 books `['idle-instead', 'delivered', 'delivered', 'delivered', 'space-instead', 'space-instead', 'idle-instead', ...]` and phase 14 books a different list: the verdicts depend on the cycle's phase.
- The switch is written only at the cycles (`(14, 'turn_on'), (44, 'turn_on'), (74, 'turn_off'), ...` at phase 14), never at a boundary.
- The store self-test reports the `pump_duty` record's silent slot off-domain: `written/silent`, `written/silent/0`, `written/silent/1` -- the 3 leaves of D15 L5 -- and the night slots likewise.
- `an early cut-off holds across a step boundary the plan keeps on` passes at the base too: the base never wrote between cycles. It is the guard on the change-only rule, and M3 is its null.

At the head all four pass. An install with no silent row writes no `silent` leaf (`pump_arbiter._entities` gives the slot `None`), so its record reads 0 off-domain leaves at both ends.

## Roster carries

- Carry 1 (carry 5 seam 2 controls, from #2745): (a) the phase 0 / 14 min install books identical verdicts from step 1 (check 1 of the section; `AGREE: yes` at the head, `AGREE: no` at the base, Figures); (b) one mutant per seam, M1, M2/M6 and M4 each turning (a) red (Mutation proof).
- Carry 2 (D15 L5): `written/silent` and the night slots declared in the `pump_duty` domain; 0 off-domain leaves with a silent row at the head, 3 silent leaves at the base; no silent row writes no leaf; M5 removes the declaration and is red (Null control, Mutation proof).
- Carry 3 (actuate at step boundaries, design note first): the step tick, its design note at the top of this body, and in round 2 a check per tick guard (X1-X6).

## Figures

- Cycle-phase control, the fixer's own build of the roster's control (the roster states the control in words and names no instrument): `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_actuation_phase.py` (sha1 `d8871c1b96466f7d0d16df9ecc15454512d6adc5`) prints `AGREE: yes` at the head and `AGREE: no` at the merge base (the same file copied into a detached worktree of `88c6ad5bb`; it uses no symbol the fix added). Its rule: the per-step ledger verdicts of the two installs, compared from step 1.
- The same install as checks: `PYTHONPATH=tests/hastub python3 tests/features.py`, section "supply switch at step boundaries": 4 of 4 pass at the head; at the merge base, the section run alone, 3 of 4 fail (Null control).
- Off-domain `pump_duty` leaves with a silent row: `store.off_domain` over a record holding every slot of `pump_arbiter._SLOTS + _NIGHT_SLOTS` (the census check in that section) reads `[]` at the head; at the merge base it lists `written/silent`, `written/silent/0`, `written/silent/1` and the twelve night-slot leaves.
- Sibling census of the switch's writers: `git grep -n 'switch_supply(' -- custom_components/` returns the definition and two callers, `coordinator.py` in `_write_supply` (the cycle and the tick) and `early_cutoff.py` in `on_room_event` (a one-time OFF, held across a kept step by the change-only rule: check 3, mutant M3). Each is dispositioned; none is open.
- Sibling census of the plan's switch rule: `git grep -n 'heat_pump_on_schedule\|plan_step_runs(' -- custom_components/` returns `optimizer.get_current_action`, `coordinator._apply_result_payload` and `pump_arbiter.step_supply`, all three now through `thermal_model.plan_step_runs`; `optimizer.py` builds the field; `wood_fuel.py` reads the schedule whole as the plan's run series, which every solved result carries (the optimizer builds it), so it needs no per-step fallback -- out of scope, not a reader of one step.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=88c6ad5bbec69bfe157e04597a74d0c9c3e4775c PYTHONPATH=tests/hastub ./tests/run.sh` at the head prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out.` and `30 TEST SCRIPT(S) PASSED; 4 SCOPED OUT AND NOT RUN`, including `features.py`, `entities.py` (`ALL 2470 ENTITY CHECKS PASSED`), `env_drift.py --all` (the golden check in drift mode: no fixture moved, so no claim), `card.mjs`, `stress.py`, `finite_boundary.py` and `harness_headers.py`. The interpreter is a scratch CPython 3.13.17 venv from `tests/requirements-ci.txt` (Friction).
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; `class_excess_loc` 17814 -> 17801 and `max_class_loc` 8155 -> 8153 were re-recorded in their own commit, because the OFF-skip decision left the coordinator class (`pump_arbiter.supply_write`) and `get_current_action`'s inline rule became `plan_step_runs`.
- Architecture: `python3 tools/audit/archscore/score.py --diff 88c6ad5bbec69bfe157e04597a74d0c9c3e4775c HEAD` prints `Architecture score: dS +0.0000 NULL`. Its null: the branch's first cut, whose new arbiter functions took the coordinator, printed `dS -0.0125 WORSENS (inadmissible: coord_footprint 2409->2430)`.
- CI prediction: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` prints `no closures, fast, wave-script or instrument red predicted against 88c6ad5bbec6` and the 24 unpinned sites under `## Unpinned sites` (28 before the pin commit); before the stale-pin commit it predicted 7 `ledger` reds (STALE PIN on the lines this branch moved).
- `node tools/policy/brief_lint.mjs` and `node tools/policy/policy_lint.mjs --budgets` exit 0.

- Round 2, this head: `bash tools/pr/prepr.sh <body>` prints `rc=0` (`gate mode MODE: SCOPED`). The whole `tests/features.py` ran as the pin drive's baseline at the guard-check commit, `rc=0 failed=0 484s`; the last commit's one-check change (the unload run takes two cycles) was run on the section standalone, `ALL 12 FEATURE CHECKS PASSED`, not the whole script. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Architecture score

n/a: `dS +0.0000 NULL`, no metric moved (Figures).

## Red checks

- `tests/entities.py`, in this branch's own local scoped gate at `0816441c4` (never pushed): `1 of 2470 ENTITY CHECKS FAILED`, the R10 N-no-expiry barrier, `mismatch {('pump_arbiter.py', 'step_duty'): (0, 1), ('pump_arbiter.py', '_step_index'): (1, 0)}`. The covering lookup moved from `step_duty` into `_step_index`; the reasoned entry moved with it, same count and same reason (commit `31cffb76d`). The cheaper detector is that barrier itself, run alone (about 11 minutes here) instead of after the whole gate; no new one is owed.
- `ledger` (predicted, never run red): 7 STALE PINs on lines this branch moved, repaired by deleting the pin files as `ci_predict.py` instructs (commit `f5dd21351`). The predictor is the cheaper detector and it fired before any push.
- `tests / nightly-status`: main-graded. It reports `nightly.yml`'s runs on `main` (`MAIN_STATE_REPORTERS` in `tools/policy/policy_lint.mjs`), and this diff touches neither that workflow nor its reporter `tests/nightly_status.py`: `git diff --name-only 88c6ad5bbec69bfe157e04597a74d0c9c3e4775c...HEAD -- .github/workflows/nightly.yml tests/nightly_status.py` prints nothing. A red there grades `main`, not this head.
- `tests / mutation` (`d26a00aa2`, the review's head): red on unpinned sites, four of them guards no check killed (the review's block). Answered: checks added and 13 sites pinned at this head; it stays red on the 13 under `## Unpinned sites` until they are pinned by CI's lane or triaged. The cheaper detector is `mutation_table.py --pin-killed` run locally before the handoff (about 484 s per `tests/features.py` mutant here, so a 26-site drive costs about an hour on four cores); this round ran it, and the round-1 drive's budget left the guard sites unstarted, which is how they reached review.

## Forward-carry

- The duty ledger's first reading of a step is the previous step's tail. `pump_arbiter._observe` folds a run into a row at any tick reading at or above `on_threshold_kw`; at a boundary the arbiter's own one-minute tick and the supply tick fire in the same minute, so the first reading of an OFF step that follows an ON step is the draw from before the switch moved (and a real meter reports later still). The synthetic install at the head books such a step `space-instead` at both phases -- phase-independent, so carry 5 seam 2's control holds, but not `delivered`. A settle window on the row's run fold is the ledger's change, not the actuator's. It lands with #2492, whose group is held in `dev/programme/rosters/wave-r10-groups.json` (R10-SAV-ACTUATION, issues [2492]); this PR therefore says `Refs #2492`, not `Closes`, and the orchestrator decides whether the residue keeps the issue open or moves to a new group. Carry: #2492

## Friction

- seat-venv-pin: cost: `tools/audit/seat/seat_venv.sh` pins CPython 3.14.7 (`tests/typing_budgets.json`), which uv cannot download in this container (`No download found for request: cpython-3.14.7-linux-x86_64-gnu`), and the script refuses the `HPO_PYTHON=/usr/bin/python3.13` override the same way; the gate ran on a scratch 3.13.17 venv built from `tests/requirements-ci.txt`, so the mypy census was not run here. Carry: dismissed: environment-only, the typing census runs in CI

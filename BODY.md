R10-HOTFIX-AWAY-PRESENCE (live user defect, tvofi 2026-10-30; probe report `handoff-body/r10-live-away-heating` aa6e5db30, code chain steps 2 and 3).

**The defect.** `coordinator.py` subscribed state changes for the defrost flag and the peak guard only. An away flag from `away_presence_entity` (a person, a calendar, an `input_boolean`, a presence `binary_sensor`) therefore reached the plan only at the next scheduled update, one `optimization_interval` later (default 30 min). The holiday calendar (`holiday_calendar_entity`) is the other entity whose state switches a comfort band (`away.holiday_dates`, read in `_solve_hubs`), and it had the same gap; the class census below found it.

**The fix.** `away.watch_away_inputs`, called once from the coordinator's construction, registers one `async_track_state_change_event` listener per configured slot and hands each unsubscribe to the entry's `async_on_unload`. A listener requests the coordinator's `async_request_refresh`, the debounced path the away switch already uses, only when the reading the plan uses changes: `interpret_presence(...) is True` for presence (unknown or unavailable reads as home, as `away.resolve` reads it), and the covered dates for the holiday calendar (`_holiday_days`, now shared with `holiday_dates`). A change that leaves that reading where it was asks for nothing. An unconfigured slot registers nothing. An entry with no unload list registers nothing, so no listener is left that nothing could drop.

**The reload window (the brief's second item).** After a set-point change the entry reloads. The first publish is the pre-reload plan (`_reload_handover`) until the background solve lands. The window was already bounded at both ends, by two existing pins:
- A handover stamped more than one update interval ago is dropped (`__init__._take_fresh_handover`; `tests/manual_plan.py` #774).
- Setup requests the replacing solve at once, as the entry background task `heatpump_optimizer_first_solve` (`tests/entities.py`, "an entry's setup defers the first solve to one entry background task"). If that solve fails, the next scheduled update replaces the plan one interval later.

What the card did not show was the window itself. The handover republished the pre-reload cycle's `next_optimization` (that solve plus one interval), so the card's plan health read "Next solve in N min" while the replacing solve was already due. `_republish_handover_ages` now stamps `next_optimization` with the current time, so the card reads "Next solve due now" (`health.next_due`) beside the plan's true age ("solved N min ago", already recomputed). No card change is needed: `healthPlanHtml` already reads `_next_optimization`.

**Scope against the roster's `files`.** The roster names `coordinator.py` and `tests/features.py`. The listener lives in `away.py`, the module that owns presence and holiday interpretation. `pump_arbiter.py` and `early_cutoff.py` register their listeners at module level in the same way. Putting it in the coordinator class would have grown a class with zero headroom on `max_class_loc` and `class_excess_loc`. The coordinator gains one line, the registration. The ratchet is paid by deleting the dead `_unsub_timer` attribute, which has been assigned only `None` since v1.0.0 (ec45dc4d5), so its shutdown branch never ran. A new dev harness, `dev/audit/harnesses/r10_away_presence_listener.py`, is classified by `ci_predict --apply-inert`.

## Head

fddb9a1bf39940c8f137db989322a24bb339729e

Merge base 14ed135512e3d7db899081f2c2639ce5674b8f2a; every figure below was taken against it. `origin/main` has since moved to 7539d1675d7fc8b5020f90b395f4bb0c3485d5b3 (2026-10-31T17:31Z, `git ls-remote origin refs/heads/main`). It changed 26 files, none under `custom_components/` (`git diff --name-only 14ed1355 7539d167 | grep -c '^custom_components/'` prints 0), and `git merge-tree --write-tree origin/main HEAD` against it is clean.

## Mutation proof

Each suite mutant was run as `PYTHONPATH=tests/hastub python3 tests/features.py` M1–M4 in worktrees at 02d59f5d6613441f5d8857940cca6807c7480190, whose production tree is byte-identical to the head's (`git diff --quiet 02d59f5d6 HEAD -- custom_components` exits 0). The head adds two checks to the block since then (the bare-entry check below, and the callable-unload arm), and neither changes what M1–M4 fail. Each mutant fails only checks in this block:

- **M1**: delete the coordinator's `away_mode.watch_away_inputs(...)` line → `3 of 4665 FEATURE CHECKS FAILED`: the flip check, the null control (listener count 0) and the registration check.
- **M2**: `_watch`'s comparison `read(old) != read(new)` → `if True:` → `1 of 4665 FEATURE CHECKS FAILED`: `FAIL R10-HOTFIX-AWAY-PRESENCE null control: a change that leaves the interpreted away state or the holiday dates as they were asks for no refresh` (each hold read `(['async_request_refresh'], 1)`).
- **M3**: delete `handover["next_optimization"] = dt_util.now()` → `1 of 4665 FEATURE CHECKS FAILED`: `FAIL R10-HOTFIX-AWAY-PRESENCE the republished reload handover says the next solve is due now, not the pre-reload cycle's time  [2026-10-31 15:49:26.793833+00:00 vs 2026-10-31 15:29:26.796516+00:00]` (20 min ahead of t0).
- **M4**: drop the holiday entry from `watch_away_inputs`'s `reads` → `3 of 4665 FEATURE CHECKS FAILED`: the flip check (holiday arms `([], 0)`), the null control (holiday holds have no listener) and the registration check (`[['person.tim']]`).
- **M5** (unpinned site `away.py:265 RETURN_DEL`, run at the head fddb9a1bf itself): `_watch` drops its `return`, so the entry's unload list holds `None` → `1 of 4666 FEATURE CHECKS FAILED`: `FAIL R10-HOTFIX-AWAY-PRESENCE no presence entity or calendar, no listener; one each when both are set, and the entry's unload drops both` (`None` on the unload list, and both listeners still registered after the unload).
- **M6** (unpinned site `away.py:244 GUARD_OFF`): delete `if on_unload is None: return` → the bare-entry check alone, driven against the mutant through the same production call (scratch probe, not in the tree): `FAIL raised TypeError: 'NoneType' object is not callable`; at the head it reads `ok`.

**Failing test first.** At the merge base 14ed1355, with this head's `tests/features.py`: `4 of 4666 FEATURE CHECKS FAILED`, namely the flip check (every arm `([], 0)`), the null control (every hold `([], 0)`: no listener), the registration check, and the handover check (`next_optimization` 20 min ahead of t0). These are the four checks this diff adds. The bare-entry check reads `ok` at the base because `watch_away_inputs` is absent there (`getattr` falls back to a no-op). The handover's plan-age null control also reads `ok` at the base.

## Null control

- **Interpreted state unchanged.** Six changes that leave the reading the plan uses where it was ask for no refresh at the head: `person` `work → school` (both away), `home → home` (an attribute rewrite), `unavailable → home` (both read as home); occupancy `on → on`; the holiday calendar `on → on` with the same span, and `off → off` with a new span. The check also requires each listener to be registered (count 1). Without that, an absent listener would pass the null control vacuously. That is why the null control fails at the base (count 0) and under M1 and M4.
- **Handover plan age.** The republished handover keeps its own plan age (10 min, within 9–11), at the base and at the head. Only `next_optimization` moves.
- **The finder's harness reads flat, as it should.** `dev/audit/harnesses/r10_live_away_heating.py` (sha1 822ccca27a2189754ee77e334e1e0544f8901191) drives the solve, which this fix does not touch. Its 13 RESULT/VERDICT lines are byte-identical at the base and at the head (`diff` of the two outputs, run as the probe states: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_live_away_heating.py`). The companion below reads the defect.

## Figures

- Companion harness `dev/audit/harnesses/r10_away_presence_listener.py` (sha1 2f7665bbd7d0c62f793a8dbea9d08c034f36f195), run as `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_away_presence_listener.py` in a worktree at the base (with the harness copied in) and at the head. The rule: per arm, a fresh `HeatPumpOptimizerCoordinator` with the slot configured. `listeners` counts subscriptions on the entity. `refreshes` counts the `async_request_refresh` coroutines the change hands `hass.async_create_task`. `wait_min` is 0 when a refresh is requested, else the coordinator's `update_interval`.
  - Base: 7 flip arms `listeners=0 refreshes=0 wait_min=30.0`. `VERDICT presence flip reaches the plan within 30.0 min (next scheduled update)`. `reload_handover next_solve_in_min=20.0 plan_age_min=10.0`.
  - Head: 7 flip arms `listeners=1 refreshes=1 wait_min=0.0`. 6 hold arms `refreshes=0`. `unconfigured listeners=0`. `VERDICT presence flip reaches the plan within 0.0 min (debounced refresh)`. `reload_handover next_solve_in_min=0.0 plan_age_min=10.0`.
  - Null control in the same run: `VERDICT null control: 0 refresh(es) from 6 changes that keep the interpreted state`, at both ends.
  - "Within the debounce" is Home Assistant's `DataUpdateCoordinator` debouncer on `async_request_refresh`, which the harness does not model. It reads that a refresh is requested, not when it runs.
- `features.py`: the `N of M FEATURE CHECKS FAILED` lines above are its own summary line, R.check failures over checks run.
- Scoped gate, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=14ed135512e3d7db899081f2c2639ce5674b8f2a PYTHONPATH=tests/hastub ./tests/run.sh` at the head. `tests/closure.py select --diff 14ed1355` printed `MODE: SCOPED -- 22 script(s) run, 11 scoped out.` The run ended `2 TEST SCRIPT(S) FAILED`. Neither failure is this diff's, and each was re-run green:
  - `tests/entities.py` raised `PermissionError: Cannot get task port for PID ... This typically requires running as root or having the 'com.apple.system-task-ports' entitlement` at its heartbeat-sampler block (`_hb_stdlib_reads`, guarded only by `find_spec("_remote_debugging")`). CPython's remote unwinder needs that entitlement on macOS; the block's docstring says the lane's container has the Linux capability and this host does not. The diff touches neither that block nor `tests/nightly_ha.py`. Re-run with only `_remote_debugging` hidden from `importlib.util.find_spec` (a scratch wrapper around `runpy.run_path("tests/entities.py")`): `ALL 2493 ENTITY CHECKS PASSED`. The sampler block's own checks were skipped there, so CI runs them.
  - `node tests/card.mjs` died after 602 s with `FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory`, at a load average of about 120. The diff changes no card file. Re-run alone as `NODE_OPTIONS=--max-old-space-size=8192 node tests/card.mjs`: `ALL CARD CHECKS PASSED`.
  - The other 20 passed, among them `ALL 4666 FEATURE CHECKS PASSED`, `STRUCTURE RATCHET PASSED`, `ALL 112 HARNESS HEADER CHECKS PASSED` and `env_drift.py --all 14ed1355`. `tests/stress.py` was scoped out, so its mutation check is CI's.
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED` (in the gate run above). The recording commit (the head) moved `class_excess_loc` 17655→17653, `max_class_loc` 8060→8057, `coordinator_attrs` 142→141 and `coordinator_multiassigned_attrs` 109→108, and set `recorded_at` to the merge base; the reason is in its commit message. The rule: each row as `tests/structure.py` defines it. `class_excess_loc` counts the coordinator's `coordinator.py` helpers in its span: +2 lines (the registration line, and the handover line in the helper `_republish_handover_ages`) minus 4 (the `_unsub_timer` init line and its three-line shutdown branch) is -2. `max_class_loc` counts the class alone: +1 minus 4 is -3.
- **Class census (fixer step 8).** The class: an entity whose state alone switches a band the solve plans with, read only at the scheduled update. The rule: the entity-state reads in the two methods that build the banded solve, `{ sed -n '/^    def _solve_hubs(/,/^    def _solve_record(/p' custom_components/heatpump_optimizer/coordinator.py; sed -n '/^    async def _resolve_away(/,/^    def _adopt_away_override(/p' custom_components/heatpump_optimizer/coordinator.py; } | grep -nE "_entity_state\(|states\.get|holiday_dates\("`. It returns two seams:
  - `away_mode.holiday_dates(self.hass, ctx._config.holiday_calendar_entity, ...)` in `_solve_hubs`: closed in this diff.
  - `self._entity_state(config.presence_entity)` in `_resolve_away`: closed in this diff.

  The open-window relax in `_floor_widening` is not an entity: it comes from `_vent_cusum`, a temperature detector. The listeners the tree already had (`git grep -n "async_track_state_change_event(" -- custom_components/`) follow the defrost flag and the power meters (coordinator), the room sensor (`early_cutoff`) and the pump arbiter's held entities. Each is a reading or a write-hold, not a band switch.

## Unpinned sites

`ci_predict.py --only mutation` lists six sites. Each is disposed of below, and `mutation-autofix` pins each killed site after the push (its lane mutates `custom_components/`):

- `custom_components/heatpump_optimizer/away.py:228 RETURN_DEL`: `_away_of` returns None, so presence never flips. Killed by the flip check. The companion harness at that mutant read `flip_person_leaves refreshes=0`, the base's reading.
- `custom_components/heatpump_optimizer/away.py:244 GUARD_OFF`: killed by the bare-entry check (M6 above).
- `custom_components/heatpump_optimizer/away.py:251 GUARD_OFF`: an unconfigured slot registers on `[None]`. Killed by the registration check. The harness at that mutant read `unconfigured listeners=1`.
- `custom_components/heatpump_optimizer/away.py:262 GUARD_OFF`: M2, killed by the null control.
- `custom_components/heatpump_optimizer/away.py:265 RETURN_DEL`: M5, killed by the registration check.
- `custom_components/heatpump_optimizer/away.py:596 RETURN_DEL`: `holiday_dates` returns None where a frozenset is owed. The scratch probe read `holiday_dates -> None` against `['2026-12-24', '2026-12-25', '2026-12-26']` at the head. Predicted killed by the existing G8 holiday checks in `tests/features.py`, which call `holiday_dates` directly and compare its result to date sets. Not run through the suite locally; CI's `mutation` lane decides it.

## Red checks

- `mutation` at fddb9a1bf399: red by construction on the 6 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Forward-carry

none

## Friction

none

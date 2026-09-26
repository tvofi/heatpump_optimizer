_Requested by **tvofi**_

Root-cause countermeasure RC2 of audit round 9 (`tools/audit/briefs/root-cause.md`, executing `.claude/rules/defect-root-cause.md`, first trigger: the defect reached a release), for v6.6.12 bug 5, "all toggles on after reboot", and the mode-persistence gap in #1621's delivery row. **Stacked on R6** (`handoff/r9-r6-reboot-toggles`, code head `df50ab42`): the check fails on `main` without R6's fix, so it merges after R6.

**Cause, the unexplained remainder: established.** Home Assistant 2026.5 changed the single-entity service path: `entity_service_call` now awaits `entity.async_request_call(...)` for one entity (`homeassistant/helpers/service.py`, 2026.5.0 line 830), which takes the platform's `PARALLEL_UPDATES` semaphore; 2026.4.0 calls `_handle_entity_call` directly for one entity and takes the semaphore only for several (line 848). At v6.6.12 every switch action awaited `coordinator.async_request_refresh()`, which outside the debouncer's 10 s cooldown runs the 33–73 s solve inline, while `switch.py` sets `PARALLEL_UPDATES = 1`. So the first tap after a quiet spell held the slot for the whole solve, every later tap on the platform queued behind it before its setter ran, and a restart cancelled the queued calls (a websocket call is a background task, cancelled at stop). Their stores still said "on", so all four came back on. Reproduced on real Home Assistant core, the real `switch` component and the real coordinator and Store, with only the solve stubbed (`tools/audit/handoff/r9-rc2/queue_probe.py`, Figures): v6.6.12 on 2026.5.0, 20 s solve, four turn-offs 1 s apart, restart at 12 s: all four on after the reboot, 3 of 3 runs, no call completed. #1621 removed the queue incidentally (its `publish_then_refresh` docstring names the `PARALLEL_UPDATES` wait) by moving the refresh off the action.

**Cause, the mode half: R6's, confirmed.** `async_set_mode` wrote `_mode` in memory only; the store got it from the cycle's `_async_save_accuracy`, so a restart or failed refresh before a completed cycle restored the old mode and Optimizer active came back on. After #1621 this is the only route left: `main` restores Optimizer on alone (Figures).

**Process state.**
- **The queue: (d), a precondition changed.** `PARALLEL_UPDATES = 1` (switch, climate, datetime, button) was written for actions that serialize two commands to one machine (switch.py's comment), when a single-entity action did not take the slot. Home Assistant 2026.5 made it take the slot, and the actions were already awaiting a solve. Nothing measured action latency against a slow refresh, and the nightly real-HA lane runs `stable` but asserts neither action latency nor that user state survives a restart.
- **The mode: (a), the process did not exist.** v3.13.0's notes claim "the mode also survives restarts" (`RELEASE_NOTES.md`), and the suite pinned the read side ("a stored optimization mode is adopted", `tests/features.py`), never that a set reaches the store before a restart.
- **Why the gap survived #1621's startup-writer check: (c).** #1621's body checked every writer of `held.until`, `override_active` and `_mode` at startup and found none that restores "on". That is the read side. It did not drive a set followed by a restart with no completed cycle, and its `tests/entities.py` sweep (a `FakeCoordinator` under `EagerHass`) asserts that each action publishes before its refresh starts and asks for exactly one, not that the action returns before the refresh ends nor that the state is stored. Both halves of bug 5 sit in the gap between those assertions and a restart.

**Class reach: every user-set state and where it is persisted relative to its setter** (R6 head). The integration defines no select, number, time or text platform; the user's writes are switch, climate, datetime and button actions, and the services that call the same coordinator setters.

| seam | persisted | disposition |
|---|---|---|
| mode: Optimizer active switch; thermostat hvac mode, preset, on/off; `set_mode` service | at the setter since R6; at cycle end before | row (fails on `main`) |
| away: switch; return-time datetime; `set_away` service | at the setter (`persist_override`) | row |
| boost DHW, boost space: switches; service | at the setter (`boost.persist`) | row |
| comfort target: thermostat; `set_temperature` | entry options through Home Assistant | row |
| manual plan: apply, clear | `_async_save_manual_plan` before the refresh | stated in the setter table |
| comfort-weight reset: button, service | `_async_save_accuracy` before the refresh | stated |
| learned snapshot restore | restores from the store it reads | stated |
| sysid arm: button, service | in memory by design | stated |
| `set_thermal_parameters` | only heat loss, buffer and DHW cooling rates (#86); `house_thermal_mass`, the displace limits and the rest are lost at restart, even after a completed cycle | stated; whether they should persist is Forward-carry |
| buttons awaiting their refresh inline | force run, arm, reset, diagnose | exempt from the latency check: their own platform's slot, so a press never queues a toggle; the reset is stored before its refresh |

Instances in released versions, all "a user's setting does not survive a restart or reload": v2.4.1 (the thermostat target was lost on reload), v3.13.0 (the mode reverted to auto), v6.6.5 #1249 (a cleared entity picker reverted), v6.6.12 bug 5 (both routes above). Four instances in 145 release headings: a round-9 class, so this delivers the class-eliminating barrier.

**Change.** One `tests/features.py` block after R6's check, three checks:
1. Every entity action the switch, climate, datetime and button platforms define, and every coordinator `async_(set|apply|clear|reset|restore|arm|update)_*` setter, is a durability row or says where its state lives. A new action or setter is refused until it is classified.
2. Each row runs its action over a real coordinator whose `async_request_refresh` never completes, under a 0.5 s `wait_for`. It must return: an action that awaits its solve is the v6.6.12 queue.
3. After cancelling the pending refreshes (the restart), a second coordinator on the same entry runs the restart's loads (`_async_load_accuracy`, `boost.restore_session`), and a fresh entity over it must read what the action set.

No production change. The block runs in 0.023 s.

**Cost test** (per release cycle). Standing cost: 0.023 s per `tests/features.py` run; at 49 pull requests a release (v6.6.11 to v6.6.12) and 3 runs each, about 3.4 s, plus one table row per new action. Defect cost: v6.6.12 bug 5 took #1621 (14 commits, 2026-09-25 19:00Z to its merge at 03:08Z, about 8 h of fixer and review), R6 (5 commits, open), this seat, and a patch release, with tvofi's house running the wrong heating state after a reboot. P(recurrence): 4 released instances in 145 releases, 0.028 per release. 0.028 × 8 h is about 13 min against 3.4 s: it passes by two orders of magnitude.

**Found on the way, for R6 rather than a later stage.** R6's save at the setter runs before the accuracy load lands when the user sets a mode during startup, and the load then reads the store the save has just overwritten. At `df50ab42`, 7 stored comfort-learner overrides become 0 (Figures, `tools/audit/handoff/r9-rc2/r6res.py`). Before R6, `async_set_mode` wrote nothing. It went to the round-9 orchestrator for R6's fixer before R6 merges; this block boots with the loads done, so it does not pin that order. The nightly real-HA lane runs `stable`, which is how the 2026.5 change arrived unseen; this block pins the behaviour on any Home Assistant version, so no lane change is owed.

## Head

`f0396766`

## Mutation proof

Each at `f0396766`, the block run alone from the tree's own `tests/features.py` (`tools/audit/handoff/r9-rc2/rc2_run.py`, which extracts it):
- `async_set_mode`'s `_async_save_accuracy()` deleted (R6 reverted): check 3 fails, six mode rows lost.
- `AwaySwitch.async_turn_on` calling `async_set_away(active=True)` (the refresh awaited in the action): check 2 fails, `awaited the solve: ['AwaySwitch.async_turn_on()']`.
- The thermostat's `_async_set_mode` without `refresh=False`: check 2 fails on the thermostat's four mode actions.
- The datetime's `async_set_away(..., refresh=False)` without it: check 2 fails on `AwayReturnDateTime.async_set_value`.
- `boost.set_channel`'s `persist` deleted: check 3 fails on the four boost rows.
- `async_set_away`'s `persist_override` deleted: check 3 fails on the three away rows.
- `async_set_target_temperature`'s options write deleted: check 3 fails on the target row.
- A new switch class with an action, and a new `async_set_legionella` setter: check 1 fails on each.
- Survivor: `publish_then_refresh` returning its refresh coroutine without scheduling it (the refresh never runs). The block passes; `tests/entities.py`'s #1621 sweep, which requires exactly one refresh per action, is the check that holds that.

## Null control

- `f0396766` (R6 plus this): `ALL 3 RC2 BLOCK PASSED`, 30 of 30 runs.
- The block against `main`'s production code (`c9453921`, after #1621): check 3 fails on the six mode rows only. Away, boosts, target and return time pass: #1621 left them durable.
- The block against v6.6.12's production code: check 2 fails on 13 of 14 rows (every action but the target awaited the solve) and check 3 on six.
- Queue probe, real Home Assistant (Figures): the cause does not reproduce with a fast solve (all four off), with the restart after the solve finishes (30 s: all four off, every call completed at 20 s), or on 2026.4.0 (only Optimizer active on: away and the boosts completed in 1–3 s, the mode half alone).

## Figures

- `PYTHONPATH=tests/hastub python3 tests/features.py` at `f0396766`: `ALL 3370 FEATURE CHECKS PASSED`, rc 0.
- `PYTHONPATH=tests/hastub python3 tools/audit/handoff/r9-rc2/rc2_run.py`: `ALL 3 RC2 BLOCK PASSED`; the block's own wall time 0.023 s.
- `python tools/audit/handoff/r9-rc2/queue_probe.py <tree> 20 1 12` on Home Assistant 2026.5.0 (Python 3.14): v6.6.12 `RESULT` all four `is_on=True`, `completed={}`, 3 of 3; `main` `c9453921` Optimizer on, the other three off; R6 `df50ab42` all four off. `... <v6.6.12> 0.05 1 12`: all four off. `... <v6.6.12> 20 1 30`: all four off, every call completed at 20 s. On 2026.4.0, `... <v6.6.12> 20 1 12`: Optimizer on alone.
- `PYTHONPATH=tests/hastub python3 tools/audit/handoff/r9-rc2/r6res.py` at `df50ab42`: `after: overrides 0 mode off`, from 7 stored (the note under Forward-carry).
- `python3 tests/closure.py select --diff df50ab42`: `MODE: SCOPED -- 1 script(s) run, 25 scoped out`, `RUN tests/features.py`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (no production change).

## Red checks

none

## Forward-carry

- `tools/audit/briefs/D1.md` (robustness, store): whether `set_thermal_parameters`' runtime fields should survive a restart. The docs say "writes model parameters at runtime" and do not say they are lost; this block states the seam rather than deciding it.

## Friction

- defect-root-cause: unenforced: the release-escape trigger has no check, so the first two instances of this class (v2.4.1, v3.13.0) were fixed one seam at a time and never counted as a class.
- closures: cost: `tests/features.py` now imports `switch.py` and `button.py`, which its measured closure does not list; the `closures` job reports `UNDER-SCOPED` and `closures-autofix` records it (`ci-autofix.md`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

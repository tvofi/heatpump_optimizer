R10-HOTFIX-AWAY-LIVE: the away switch's override was on disk (`_away` store: active, return 2026-10-31T19:00Z) while every published away view read `away_active false`, `away_override_active false`, and the plan was a home plan (preheat_weather) at `plan_age` 15 min (tvofi, 2026-10-30).

**Cause: candidate (5), the entry reload, by way of the reload handover, plus an unguarded reader of candidate (1)'s restore.** It was not candidate (2), (3) or (4).

- **The handover (the owner's symptom).** `async_unload_entry` stashes the old coordinator's whole `coordinator.data`, and the new entry's setup refresh (`_async_first_refresh_light`) republished it with only the age fields rewritten (`_republish_handover_ages`). The away switch persists at once and asks for a refresh, and that refresh runs a 30-70 s solve on a Pi. An options save in that window (lowering the setpoint) reloads the entry, and the unload cancels the refresh (`async_shutdown` cancels `_refresh_task`, #237). So the handover is the *pre-switch* payload: a plan solved as home, with the away keys false. The new entry published it as fresh. A handover is accepted only while its age is at most one update interval, which is 15 min on this install, and the bundle's `plan_age` of 15 min sits at exactly that limit.
- **The restore gate had writers but no readers.** L3 (`f7567be02`) put `async_set_away`, `set_channel` and `set_block` behind `boost.session_restored`, but nothing made `_resolve_away` wait for the restore. A resolve that runs before the store read lands plans home, and its published view says `override false`.

**Fix: at the seams that own the gaps.**
- `_resolve_away` awaits `boost.session_restored`, as the writers already do.
- The light refresh awaits the same gate. It republishes the handover only when `away.published_under(state, view)` says the payload was published under the restored override. Otherwise it takes the fresh-start path: no plan published, and the background solve, which now resolves after the restore, plans the away band.

Alternatives, and why each lost:
- *Resolve away inside the light refresh and re-fold the view onto the handover.* The recovery estimate goes to the process worker, which would start inside `async_setup_entry`, and the republished plan would still be a home plan under an away view.
- *Move the handover decision into a module-level `_live_handover`.* `structure.py` counts coordinator helpers in the class span (its own pin: helped == inline), so the move paid nothing.

Ruled out by reproduction through the production coordinator, each reading the away band at the next resolve: restore then resolve; the switch then resolve; a stored override with a passed return time, which still expires as before (the fourth check below). Also ruled out under real Home Assistant (a scratch venv, outside the tree): the real `Store` round trip and a real coordinator's restore then resolve both adopt the override.

Not explained by this diff: the bundle's "current step off at a 15 setpoint". In the handover story the published current step is the pre-switch plan's, and 15 °C may simply be the configured floor. I found no action path that reads the away target, but I had no bundle to confirm the configured `min_temp`.

Residual, stated rather than fixed: the light payload's `away_active` stays unresolved until the background solve, now with the restored override shown beside it. Resolving there is the first alternative above. Carry: dismissed: cosmetic until the first solve, and resolving in setup would start the process worker there

## Head

438e7f373fdbd06c95bf2ae13c4ac7c7740d7cb4 (round 2). It is ba982d840701807cbd7011f32cf05f6511eab382, the reviewed and approved head, plus one commit that records a budget: `git diff --stat ba982d840..438e7f373` is `tests/structure_budgets.json` alone, 2 lines (`max_class_loc` 8063 to 8061, `recorded_at` to 5d4e0bcf). Nothing the mutation proof or the class census reads changed. The figures below were taken at 56eb5b5cd127a1d56b40fa21e7afeea773145253, the parent of the round-1 head 97a51d347c03c7f5d4f36bc53ae0ef56eb7583d7; that head added only the mutation-ledger re-key (3 files under `tests/mutation_ledger/killed_by/`); the scoped gate was not re-run for that delta, and `prepr.sh`'s ledger and CI-predict arms were run at the head. `origin/main` is 5d4e0bcfb88413ddf9ca7f0884c36bbec9235447, already an ancestor of this head (`git merge-base --is-ancestor origin/main HEAD` true), so nothing is left to merge.

## Mutation proof

Each fixed gate was deleted or replaced at the head, and the closure was run: `PYTHONPATH=tests/hastub python3 tests/features.py`. Each mutant fails only the check named for its gate:

- M1: delete `await boost.session_restored(self)` in `_resolve_away` → `1 of 4609 FEATURE CHECKS FAILED`: `FAIL R10-HOTFIX-AWAY-LIVE a resolve run before the session restore lands waits for it, and plans the stored override's away band  [((21.0, 19.0, False), False)]`
- M2: delete `await boost.session_restored(self)` in `_async_first_refresh_light` → `1 of 4609 FEATURE CHECKS FAILED`: `FAIL R10-HOTFIX-AWAY-LIVE a reload after the away switch, before its solve published, drops the home handover: ...`
- M3: `away.published_under` → `return True` → `1 of 4609 FEATURE CHECKS FAILED`: the same reload check.

The failing tests at the merge base (the production tree at cc930cdd1, with this head's `tests/features.py`): `2 of 4609 FEATURE CHECKS FAILED`, namely the reload check `[(True, False, (21.0, 19.0, False), 21.0)]` (handover republished, override false, home band) and the resolve-before-restore check `[((21.0, 19.0, False), False)]`. At the head the same four checks read `ok`.

## Null control

- With the store inactive, the reload republishes the handover (`first is published`) and the solve keeps the configured band (`comfort_temp_day == opt_config.comfort_temp_day`, `away_active False`): `ok` at the base and at the head.
- A stored override whose return has passed expires at the resolve (home band, override off): `ok` at the base and at the head.
- The setup-race census's own null control: see Red checks.

## Figures

- `2 of 4609` (base) and `1 of 4609` (each mutant) are `tests/features.py`'s own summary line, run as `PYTHONPATH=tests/hastub python3 tests/features.py` in a worktree at the stated tree. The rule: R.check failures over checks run.
- Bands `(21.0, 19.0, False)` / `15.0`: `_al_bands` in the new block, i.e. `_solve_hubs(8, banded=True)[0].comfort_temp_day`, `.min_temp` and `_away_state.active`.
- `structure.py`: `class_excess_loc` 17672→17670 and `max_class_loc` 8065→8063 at round 1. Round 2: the merge with main 5d4e0bcf measured `max_class_loc` 8061, so CI's `tests/structure.py` read `1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`; `python3 tests/structure.py --record` moved 8063→8061 (-2: the hotfix shrank `HeatPumpOptimizerCoordinator` by 2 lines at that merge) and `recorded_at` to 5d4e0bcf, and no other budget moved. Both are recorded with the reason in the commit message; `python3 tests/structure.py` exits 0 at the head. The rule: each class's span past `GOD_CLASS_LOC_LIMIT`, coordinator helpers counted in. The payment is the light refresh's docstring, rewritten to state the dropped-handover case in fewer lines.
- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 22 script(s) run, 11 scoped out.`, run by `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`: `24 TEST SCRIPT(S) PASSED; 10 SCOPED OUT AND NOT RUN`, rc 0 (`tests/layout.py` ran as run_always); `tests/stress.py` was scoped out, so its mutation check is CI's
- Class census (fixer step 8). The class is readers of session-restored state (the away override and the boost channels) that can run before the restore lands. The rule: `grep -n "_away_state\b\|away_state\.\(override\|active\|recovery\)" custom_components/heatpump_optimizer/*.py` and `grep -n "held_for(" custom_components/heatpump_optimizer/*.py`, with each hit's enclosing function. Dispositions:
  - `_resolve_away` and `_async_first_refresh_light`: closed in this diff.
  - `async_set_away`, `boost.set_channel`, `boost.set_block`: already guarded (L3).
  - `_expire_away_override`: called only from `_resolve_away`. `_adopt_away_override`, `boost.restore`: the restore itself. `_init_features`: the constructor's default.
  - `_solve_hubs`, `_build_data_dict`, `_track_curve_comfort`, `_apply_action`, the `boost.*` sync readers, and `pump_arbiter` (`_silent_target`, `_planned_duty`, `_without_block`, `_share`): reached only from update cycles. Every production setup's first `_async_update_data` is the light refresh (`async_setup_entry` passes `skip_first_solve=True`), which now awaits the gate, so they run after it. That is guarded by this diff, transitively.
  - `AwaySwitch.is_on`, `AwayReturnDateTime.native_value`, `TimedDutySwitch.is_on`, and `async_simulate` (the what-if): entities and services exist only after `async_config_entry_first_refresh` returns and `runtime_data` is assigned, so they are guarded transitively too.
  - No hit is left undispositioned.

## Red checks

Round 2: PR #3015 at ba982d840 was red on two checks.
- `tests/structure.py` (the gate): `1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`, `max_class_loc` budget 8063, measured 8061, at the PR's merge with main 5d4e0bcf. Fixed: recorded by `python3 tests/structure.py --record` in 438e7f373 (the only file changed), the row named in the commit message. The cheaper detector is `tests/structure.py` itself, run after the last merge of main; the round-1 run preceded main's move.
- `governance / instrument-self-tests` (run 41141431903): `tools/pr/prepr.sh --self-test` had 1 failure, `FAIL and pushes a body the lint passes (null control: the same body without the session link) (got 1, wanted 0)`. Not caused by this branch, and not reproduced. Evidence: (1) at this head, which holds main 5d4e0bcf, `env -u BASH_ENV bash tools/pr/prepr.sh --self-test` printed `429 passed, 0 failed`, and that check read `ok`; (2) the three-dot diff touches no instrument (`away.py`, `coordinator.py`, `tests/features.py`, `tests/structure_budgets.json`, `dev/programme/delivery/3015.md`, three mutation-ledger files), and the self-test builds its own throwaway repository; (3) in the failed log the check ran 24 s (23:03:22 to 23:03:46) where its neighbours take 3 to 6 s, and `body_push` returned rc 1 with no body ref pushed; the log prints no ERROR line for it, only two later `fatal: ambiguous argument 'refs/heads/handoff-body/zz-lint'` lines, which are the next check's `rev-parse` of the ref this push never created. That points at a slow or transient step on the runner, not a lint verdict, but I could not read the cause from the log. Main 5d4e0bcf's own run of this job is green. If it recurs it is a flake class for the owner to triage, not this PR's.

- Locally this branch first turned `tests/features.py`'s setup-race census red: `FAIL and the census sees the writers it clears: without the stores' fences, every read held at once differs  [unfenced differs in []]`. That check is the census's null control. With every store read held and the fences removed, the race must still change state. The light refresh now awaits the session-restore gate, which is a fence of the same kind, so the setup refresh waited out the hold and the window reached no writer. The repair keeps the arm's meaning, which is that every fence is removed. The unfenced arm now also patches `boost.session_restored`, the header comment names it, and the arm reads `ok` at the head. The fenced arm is untouched and reads `ok`.
- Cheaper detector: none exists short of running the census. It is the detector, and it caught this before the handoff.
- `tests / mutation`, predicted red by `prepr.sh`'s CI predict at 56eb5b5cd, on two counts. First, a STALE PIN: `_async_first_refresh_light`'s GUARD_OFF anchor 026f6cc7 pinned the line `if handover is not None:`, which this diff rewrote. Second, two ADDED UNPINNED sites on the rewritten line (`coordinator.py:5857` BOOLOP and GUARD_OFF). Repaired before the handoff: the stale anchor is removed, and `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base cc930cdd1a3cfb005ba7ec557f4451ff5e53e364` printed `PIN KILLED: 2 pinned, 0 left unpinned`, with both killed by `tests/features.py` (rc=0 failed=0 to rc=1 failed=1). The cheaper detector is `prepr.sh`'s CI predict itself, a static read that costs seconds per run. It fired before any push, so none is owed.

## Forward-carry

- Any fence a later fix adds to the setup refresh must also be removed in the census's unfenced arm, or the census goes blind. This is now written in the census header in `tests/features.py`, where the next seat touching that refresh reads it. Carry: dismissed: landed in-tree, in the census header in tests/features.py
- R10-HOTFIX-AWAY-SETBACK (in flight) works in `away.py`'s setback seam. No `handoff/r10-hotfix-away-setback` ref exists yet (`git ls-remote origin 'refs/heads/*away-setback*'` lists only its dispatch ref), so its overlap with this diff is unmeasured. This diff adds `published_under` before `persist_override` and does not touch `solve_bands` or `holiday_dates`. Carry: R10-HOTFIX-AWAY-SETBACK

## Friction

none

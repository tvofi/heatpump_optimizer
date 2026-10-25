R10-LEGIONELLA-COMPLETION (D15 live-bundle lead L8; triage `dev/programme/triage/s6-batch24.md#P120`). The owner's export showed the last completed anti-legionella cycle about 66 days old against a 7-day interval, with the last attempt peaking below the configured temperature.

Measured first, at main `f54f40cc1157529fea147456ad67e26c24d67aca`, with `dev/audit/harnesses/r10_legionella_completion.py`. This is a closed loop: the real `HeatPumpOptimizer` is re-solved every 30 min from the real tank, and the real `LegionellaGuard` is fed every 15 min. The pump's physical ceiling is one the model does not know. The last completion is 66 days old and the interval is 7 days.

1. **Does the plan command the cycle?** Yes, in every arm, in the first hour.
   - `reach` (a pump that gets to 65 °C) completes the cycle.
   - `short` (tops out at 57 °C) and `marginal` (59.3 °C, free disinfection on) never complete.
   - `blind` (probe configured but silent) never completes.
   - In every arm the plan's cycle step flaps between step 0 and step 1 from one solve to the next. The boost window therefore closes after one commanded step, and `async_track_cycle` judges that cut-off window as an **attempt**.
2. **What a short cycle did to `hours_since`.** It reset `hours_since` to 0, so the cycle was due a whole interval later. At main the attempts land 145.0 h apart, once a week, each a single cut-off step. The brief's question has the answer "later, not sooner".
3. **Is an overdue cycle loud?** No. No notice reads the last completion.
   - `blind` raised no legionella notice at all.
   - `marginal`'s only notice was `dhw_legionella_unreachable`, raised by the first cut-off window at 55.4 °C. Later windows reached 59.3 °C, which is ≥ target − 1, so they raised nothing.
   - The countdown read healthy throughout (`due_in_hours_end` 122.8 at day 14) while the last completion was 80 days old.
   - `check_mode_block` fires only with a mode block. The boost cap `DHW_LEGIONELLA_BOOST_MAX_HOURS` never fired: the windows were cut off long before 12 h. `DHW_LEGIONELLA_HOLD_MINUTES` is what `marginal` never satisfies.

The fix, in `legionella.py`:

- **Retry within a day.** `hours_since` leaves the cycle due again `DHW_LEGIONELLA_RETRY_HOURS` (24 h) after an attempt when a tank probe is configured. It is capped at the age of the last completion. With no probe the whole interval still applies, as before: a retry nobody can observe learns nothing, and `dhw_legionella_unverified` already speaks for that case. `due_in_hours` follows.
- **Fold a reopened window into its attempt.** A boost window the plan reopens inside that retry keeps its peak and does not re-stamp the attempt. Without this, the step-0/step-1 flap re-stamped the attempt every 30 min across the cheap block: 9 attempts a day in this harness, each logging a warning. The fold was measured, then fixed.
- **A new `dhw_legionella_overdue` notice.** It reads the last confirmed completion alone, and stands while that completion is older than the interval and a probe is configured. Its text is in `strings.json`, `en.json` and `sv.json`. A completion clears it, through `async_track`.
- **The `dhw_legionella_unreachable` text** no longer promises a once-per-interval retry.

The completion test is unchanged: only `async_track`'s observer credit writes `last_cycle`. The configured temperature is untouched.

The guard's notices now go through the existing `issues.set_issue`/`clear_issue` writer instead of five hand-rolled best-effort clears and creates. That pays for the added lines (see `## Figures`, structure).

Alternatives considered:

- **Keep the interval spacing and add only the notice.** It lost because the cycle would stay a week away after every cut-off step. The brief's control "the next attempt must come sooner than the interval" fails.
- **Retry on every solve.** It lost because it re-creates the latch `hours_since`'s docstring was written against: a boost re-commanded every quarter hour.
- **Keep the boost window open across a one-step gap**, so that the flap closes no window. It lost for now because it changes when the control-mode disinfection switch turns off, which `docs/configuration.md` documents per boost. It is carried forward (`## Forward-carry`).

## Head

`439bc041ab9469ec755ef2c4f7bba7da0a1e6ca8`, cut from `origin/main` `f54f40cc1157529fea147456ad67e26c24d67aca` (merge base the same, fetched 2026-10-25). Every figure below was taken at this head unless it names another tree.

## Mutation proof

Each mutant was applied by hand in its own detached worktree. M1–M3, M5 and M6 ran at `c9534b398`; M4 and the final `features.py` ran at this head. `c9534b398` is this head's parent: the head differs only by binding the pending attempt to a local in the fold condition, which M4 mutates. Each ran `PYTHONPATH=tests/hastub python3 tests/<script>.py`.

- M1, retry arm (`_retry_hours` returns `interval_h` always): `2 of 4404 FEATURE CHECKS FAILED`.
  - `a tank that never gets hot is retried a day later, neither latching overdue nor waiting out the interval [7002 h before, 9.6e-08 h after, …]`
  - `…and the timer moves anyway, instead of latching at 192 h`
- M2, overdue arm (`check_overdue()` dropped from `async_observe`): `1 of 4404 FEATURE CHECKS FAILED`, `a cycle overdue since its last confirmed completion is loud, with a silent probe too [short None, silent probe None]`.
- M3, probe gate (`and self._has_probe()` dropped from `check_overdue`'s `watched`): `1 of 4404 FEATURE CHECKS FAILED`, `…a whole interval later, since a retry without a probe learns nothing, and the unverified notice speaks for it rather than the overdue one`.
- M4, fold arm (`if pending is not None and (` → `if False and (`): `1 of 4404 FEATURE CHECKS FAILED`, `a window reopened inside the retry folds into its attempt, peak kept`.
- M5, completion clears the notice (`check_overdue()` dropped from `async_track`): `1 of 4404 FEATURE CHECKS FAILED`, `a cycle that reaches temperature clears the notices and the attempt, and restarts the countdown`.
- M6, the rerouted ceiling memo (`if signature == self.ceiling_notice:` → `if False:`), run with `tests/guard_pins.py`: `1 of 50 GUARD PIN CHECKS FAILED`, `an unchanged ceiling signature does not re-raise the notice`. The pin now counts at `ir.async_create_issue`, which `issues.set_issue` writes, so the reroute did not blind it.

## Null control

- **Reachable target, `reach` arm**, at both ends: the cycle completes, the attempt list is `[]` and `due_in_hours_end` is 146.2. `dhw_legionella_overdue` is raised at the 66-day start and cleared by the completion, so it is absent from `notices_standing` at the head.
- **No probe:** an attempt still spaces the next try by the whole interval. `hours_since` is below 1 h after it, and the unverified notice stands rather than the overdue one (`features.py`, the `_lg_blind` checks).
- **Unmutated head:** `ALL 4404 FEATURE CHECKS PASSED` and `ALL 50 GUARD PIN CHECKS PASSED`.

## Figures

All harness figures come from `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_legionella_completion.py --days 14`. The harness file has sha1 `24f8ca0e6eb1f63c40f32cc9b30652e7a76768e2`. The base copy ran from a scratch copy with that same sha1, in a detached worktree at `f54f40cc1`.

**At main:**
- `short`, `marginal` and `blind` each have `attempt_gaps_h [145.0, 145.0]` and `completions 0`.
- `completion_age_days_end 80.0` and `due_in_hours_end 122.8`.
- `notices_ever`:
  - `blind`: `['dhw_legionella_above_setpoint']`
  - `marginal`: `['dhw_legionella_above_setpoint', 'dhw_legionella_unreachable']`, standing at `reached 55.4`
  - `short`: the same two, standing at `reached 57.0`

**At this head:**
- `short`, `marginal` and `blind` each have attempts every 24.0 h (`attempt_gaps_h`, 13 gaps of `24.0`) and `completions 0`.
- `completion_age_days_end 80.0` and `due_in_hours_end 0.8`.
- `notices_standing` includes `dhw_legionella_overdue {'days': '79', 'interval_days': '7'}` in all three arms.
- `reach` is unchanged from main: `completions 9`, `attempt_hours []`, `due_in_hours_end 146.2`.
- Before the fold, the same harness at an intermediate tree printed `attempt_gaps_h` of eight `0.5` then `19.5`, repeating. That was 9 attempts a day, the measurement the fold answers.
- `completions` counts every change of `last_cycle`. A tank held at temperature is re-credited at most hourly by `async_track`'s own 3600 s guard, so `reach`'s 9 counts re-credits, not 9 cycles.

**Class census (step 8).** The rule is `grep -n "self\.attempt = \|self\.last_cycle = " custom_components/heatpump_optimizer/legionella.py` for the writers, and `grep -rn "\.hours_since()\|due_in_hours()\|dhw_hours_since_legionella\b" custom_components/heatpump_optimizer --include=*.py` for the readers. Every seam it returns, with its disposition:
- `async_load` restoring `attempt` and `last_cycle`, and the fresh-install `last_cycle = now`: read through `hours_since`/`check_overdue` like any other stamp. A fresh install is not overdue by design: the stamp is "now" so a new install does not blast the tank.
- `async_track` writing a completion and clearing the attempt: clears the overdue notice. Closed, M5.
- `async_track_cycle`'s three attempt writers:
  - no probe: interval spacing plus the unverified notice. Guarded, M3 control.
  - probe silent: 24 h retry plus the overdue notice. Closed, M2 `silent` arm.
  - short peak: 24 h retry plus the unreachable and overdue notices. Closed, M1.
- Readers:
  - `coordinator.py`'s `dhw_hours_since_legionella` publish, read by `dhw_planner.py`'s `_dhw_legionella_due`: places the retry inside the horizon (harness: 24.0 h gaps).
  - `coordinator.py`'s `dhw_legionella_due_in_hours` attribute, read by `boost.py`'s `_due_inside_horizon`: the same remainder rule as the planner, so the two agree. Guarded.
  - `check_mode_block`'s `due_in_hours`: unchanged in shape. It now fires a day after a short attempt instead of a week after, which is the overdue truth.

**Scoped gate.** `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 22 script(s) run, 11 scoped out.` Each script in `scope.run` was run at `c9534b398` with `GOLDEN_MODE=drift GOLDEN_REF=origin/main PYTHONPATH=tests/hastub` (node for `.mjs`). All passed except:
- `tests/entities.py`: `2 of 2445 ENTITY CHECKS FAILED`, the same two names `origin/main` fails in this container (`gate-sweep.yml: …` and `graders-head-copy's delivery_status step …`). `PYTHONPATH=tests/hastub python3 tests/entities.py` at `f54f40cc1` prints `2 of 2445 ENTITY CHECKS FAILED`.
- `tests/typing_ruler.py`: `by_code[arg-type] did not grow [recorded 0, measured 1 (+1)]`, fixed at this head (`ALL 12 typing-ruler source checks PASSED`).

`tests/golden.py` printed `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. `git diff --quiet origin/main HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt` exits 0.

**Structure.** `PYTHONPATH=tests/hastub python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. The diff first read `FAIL class_excess_loc 18158 > 18102 (+56)`. It was paid by routing the guard's notices through `issues.set_issue`/`clear_issue` and trimming `async_track_cycle`'s spent history. The budget is re-recorded 18102 → 18096, a lowering, with the reason in commit `c9534b398`'s message. Nothing is raised.

**Architecture.** `PYTHONPATH=tests/hastub python3 tools/audit/archscore/score.py --diff f54f40cc1157529fea147456ad67e26c24d67aca HEAD` prints `Architecture score: dS +0.0077 IMPROVES`, with `literal_clone_copies 186 -> 185` and `shape_copies 44 -> 42`.

**Predictor.** `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against f54f40cc1157` and `25 unpinned site(s) the diff adds`.

## Unpinned sites

Every site is under `custom_components/`, which `mutation-autofix` mutates (`ci-autofix.md`); the arms a behavioural mutant above kills are named. The two stale pins on `hours_since`'s old return line are deleted, as the predictor's `STALE PIN` lines asked.

- `custom_components/heatpump_optimizer/legionella.py:50 CONST`: pinned by `mutation-autofix`; value checked by the `retried a day later` check.
- `custom_components/heatpump_optimizer/legionella.py:57 GUARD_OFF`: pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/legionella.py:60 CMP_BOUND`: pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/legionella.py:60 RETURN_DEL`: pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/legionella.py:345 CMP_BOUND`: pinned by `mutation-autofix`; M4.
- `custom_components/heatpump_optimizer/legionella.py:349 GUARD_OFF`: pinned by `mutation-autofix`; M4.
- `custom_components/heatpump_optimizer/legionella.py:350 CLAMP_DROP`: pinned by `mutation-autofix`; M4.
- `custom_components/heatpump_optimizer/legionella.py:353 GUARD_OFF`: pinned by `mutation-autofix`; M4.
- `custom_components/heatpump_optimizer/legionella.py:489 RETURN_DEL`: pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/legionella.py:610 GUARD_OFF`: pinned by `mutation-autofix`; M1.
- `custom_components/heatpump_optimizer/legionella.py:611 CLAMP_DROP`: pinned by `mutation-autofix`; M1.
- `custom_components/heatpump_optimizer/legionella.py:613 CLAMP_DROP`: pinned by `mutation-autofix`; M1.
- `custom_components/heatpump_optimizer/legionella.py:614 GUARD_OFF`: pinned by `mutation-autofix`; M1.
- `custom_components/heatpump_optimizer/legionella.py:616 CLAMP_DROP`: pinned by `mutation-autofix`; M1.
- `custom_components/heatpump_optimizer/legionella.py:616 RETURN_DEL`: pinned by `mutation-autofix`; M1.
- `custom_components/heatpump_optimizer/legionella.py:621 BOOLOP`: pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/legionella.py:621 CMP_BOUND`: pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/legionella.py:621 GUARD_OFF`: pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/legionella.py:623 RETURN_DEL`: pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/legionella.py:627 CLAMP_DROP`: pinned by `mutation-autofix`; M1.
- `custom_components/heatpump_optimizer/legionella.py:628 CLAMP_DROP`: pinned by `mutation-autofix`; M1.
- `custom_components/heatpump_optimizer/legionella.py:628 RETURN_DEL`: pinned by `mutation-autofix`; M1.
- `custom_components/heatpump_optimizer/legionella.py:655 BOOLOP`: pinned by `mutation-autofix`; M3.
- `custom_components/heatpump_optimizer/legionella.py:658 GUARD_OFF`: pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/legionella.py:701 GUARD_OFF`: pinned by `mutation-autofix`.

## Red checks

- `tests/entities.py` locally, `2 of 2445 ENTITY CHECKS FAILED`: the same two names fail at `origin/main` in this container, so the red is the container's and not this diff's. No cheaper detector is owed, since it is not this branch's.
- `tests/typing_ruler.py`, red at `c9534b398` (`by_code[arg-type] +1`) and fixed at this head. The cheaper detector exists and ran: `tests/typing_ruler.py` locally, in its scope; its standing cost is the script's own run, per push.
- `tests / mutation`: predicted to list the 25 sites above, which `mutation-autofix` pins.

## Forward-carry

- **The step-0/step-1 flap.** The plan's legionella step alternates between step 0 and step 1 on consecutive solves, so `async_track_cycle` sees the boost commanded every other step.
  - This PR folds those windows into one attempt for scheduling.
  - In control mode `_drive_switch` still turns the disinfection switch on and off with each window.
  - With daily retries, an install whose pump cannot reach the target now meets that toggle daily across the cheap block, instead of once a week.
  - The window-debounce alternative (above) changes the per-boost switch contract `docs/configuration.md` documents, so it belongs to the disinfection-switch owner.
  - It goes to the live group nearest the disinfection write path; the orchestrator may re-route it to a group owning `disinfection.py`. This seat writes no brief. Carry: R10-IMMERSION-LATCH
- **A stale peak on the unreachable notice.** `dhw_legionella_unreachable` keeps the peak of the window that first raised it: `marginal` shows 55.4 °C while later windows reached 59.3 °C. It is minor now that the overdue notice stands. Carry: dismissed: the overdue notice now stands beside it and names the completion's age, so the stale peak misleads nobody about whether the tank is disinfected

## Friction

none

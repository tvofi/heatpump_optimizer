R10-LEGIONELLA-COMPLETION (D15 live-bundle lead L8; triage `dev/programme/triage/s6-batch24.md#P120`). The owner's export showed the last completed anti-legionella cycle about 66 days old against a 7-day interval, with the last attempt peaking below the configured temperature.

Measured first with `dev/audit/harnesses/r10_legionella_completion.py`, a closed loop: the real `HeatPumpOptimizer` re-solved every 30 min, the real `LegionellaGuard` fed every 15 min, a pump ceiling the model does not know, a 66-day-old completion and a 7-day interval. At main a cycle that falls short restarts the whole interval (attempts 145.0 h apart), and no notice reads the last completion, so an overdue cycle is silent.

The fix, in `legionella.py`:

- **Retry within a day.** With a tank probe, `hours_since` leaves the cycle due again `DHW_LEGIONELLA_RETRY_HOURS` (24 h) after an attempt, never later than the last completion makes it. With no probe the whole interval still applies, and `dhw_legionella_unverified` speaks for that case.
- **Fold a reopened window into its attempt.** A boost window the plan reopens inside that retry keeps the higher peak and does not re-stamp the attempt (the plan's cycle step flaps between step 0 and step 1).
- **A new `dhw_legionella_overdue` notice.** It reads the last confirmed completion alone, while hot water and disinfection are enabled and a probe is configured; a completion clears it. Text in `strings.json`, `en.json` and `sv.json`.
- The guard's notices go through the existing `issues.set_issue`/`clear_issue` writer.

The completion test and the configured temperature are unchanged.

Round 2 adds two things to the head the round-1 review blocked:

- **The params owner is a callable.** The merged-in main (#2817) made `LegionellaGuard`'s `params` a `Callable[[], ThermalParameters]`. Three reads this branch added (`hours_since`, `_retry_hours`, `check_overdue`) still read it as the object. That raised `AttributeError` on every closed boost window and every cycle, and it is the one cause of this head's typing, fast, coverage-ratchet and mutation-autofix reds (`## Red checks`). The harness now passes the callable too, which main's API takes at both ends.
- **A killing check per live mutation site.** These are the eight sites the verdict named, plus the reviewer's R3 and R4 cases, each in `tests/features.py`.

Alternatives considered:

- **Keep the interval spacing and add only the notice.** It lost because the cycle would stay a week away after every cut-off step. The brief's control "the next attempt must come sooner than the interval" fails.
- **Retry on every solve.** It lost because it re-creates the latch `hours_since`'s docstring was written against: a boost re-commanded every quarter hour.
- **Keep the boost window open across a one-step gap.** It lost because it changes when the control-mode disinfection switch turns off, which `docs/configuration.md` documents per boost. It is carried forward (`## Forward-carry`).
- **Triage the edge mutants as equivalent.** It lost because each one is killable with a frozen clock or a pure call, so a triage would be a step-17 shape.

## Head

`f92502af5dea1fde0f07b830d0540c2c24e4ff0c`, merged with and measured against `origin/main` `7d2056970e08135bdc7c2cab4063427a2efa1c30`, the merge base. At handoff `origin/main` is `f6784210c9c2c89cfe82ec8bf6acb8b412629055` (read 2026-10-26T04:13:47Z). `git merge-tree --write-tree origin/main HEAD` exits 0 against it, so the head is not re-merged (`fixer.md` step 6). Every figure below was taken at this head unless it names another tree.

## Mutation proof

Each mutant was applied to `legionella.py` in a copy of this head's tracked files (no `.git`), and `PYTHONPATH=tests/hastub python3 tests/features.py` and `tests/guard_pins.py` were run there. The copy fails the `recorded_at (#363)` check on every run, as the null control shows, so each count below includes that one line. `tests/guard_pins.py` printed `ALL 50 GUARD PIN CHECKS PASSED` under every mutant.

- Null (comment-only edit): `1 of 4424 FEATURE CHECKS FAILED`, the #363 line alone.
- `days_since_confirmed` CMP_BOUND (`age_h > …` → `>=`): `2 of 4424`, `the overdue notice comes due at the interval, not before and not an interval late`.
- R4, the threshold doubled (`interval_days * 24.0` → `* 48.0`): `3 of 4424`, the same check plus `…and the guard raises it one day past a 7-day interval [None]`.
- Fold bound CMP_BOUND (`< self._retry_hours() * 3600.0` → `<=`): `2 of 4424`, `a window inside the retry folds into its attempt and keeps the higher peak; one at the retry's end is a fresh attempt`.
- Fold peak CLAMP_DROP (`max(peak, self.attempt_peak or peak)` → `(peak)`): `2 of 4424`, the same check (`folded (…, 52.0)`).
- `_pending_attempt` CMP_BOUND (`<= 0` → `< 0`): `2 of 4424`, `an attempt at or before the last completion is spent, and the next window stamps its own`.
- `_pending_attempt` GUARD_OFF (`if False:`): `2 of 4424`, the same check.
- R3, `watched` BOOLOP (`dhw_enabled and dhw_legionella_enabled` → `or`): `2 of 4424`, `the overdue notice stays down with disinfection or hot water off, a tank probe notwithstanding [legionella off {'days': '292', …}]`.
- Overdue memo GUARD_OFF (`if days == self.overdue_notice:` → `if False:`): `2 of 4424`, `the overdue notice is written once per change, not on every cycle`.
- Mode-block warning GUARD_OFF (`if overdue_days is not None:` → `if False:`): `2 of 4424`, `a mode block holding an overdue cycle is logged as a warning [[]]`.

The round-1 behavioural mutants M1–M6 mutate lines this round does not touch, apart from the `self._params()` reads. Their checks are unchanged and green at this head.

## Null control

- **Reachable target, `reach` arm**, at both ends: `completions 9`, `attempt_gaps_h []`, `due_in_hours_end 146.2`. No overdue notice stands at the end.
- **Disinfection or hot water off**, with a probe configured and a 66-day-old stamp: no overdue notice. The same coordinator with the flag restored raises one (the R3 check's own twin).
- **At exactly the interval:** `days_since_confirmed` returns None, and it returns 7 an hour later.
- **Unmutated head:** `ALL 4424 FEATURE CHECKS PASSED` and `ALL 50 GUARD PIN CHECKS PASSED`.

## Figures

**Harness.** `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_legionella_completion.py --days 14`. The file at this head has sha1 `cba192d1ca79c5e3c661ad5c2b52a751ec4803d5`, and the same copy ran in a detached worktree at `7d2056970e08` (base) and at this head.
- Base: `short`, `marginal` and `blind` each give `commanded_steps 5`, `completions 0`, `attempt_gaps_h [145.0, 145.0]`, `completion_age_days_end 80.0` and `due_in_hours_end 122.8`. No `dhw_legionella_overdue` stands in any arm.
- Head: the same three arms each give `commanded_steps 139` and `completions 0`. `attempt_gaps_h` is 13 gaps of `24.0`, `due_in_hours_end` is `0.8`, and `dhw_legionella_overdue {'days': '79', 'interval_days': '7'}` stands in all three.
- `reach` is identical at both ends: `commanded_steps 3`, `completions 9`, `due_in_hours_end 146.2`. `completions` counts every change of `last_cycle`, and `async_track` re-credits a tank held at temperature at most hourly.

**Class census (step 8).** The rule is `grep -n "self\.attempt = \|self\.last_cycle = " custom_components/heatpump_optimizer/legionella.py` for the writers, and `grep -rn "\.hours_since()\|due_in_hours()\|dhw_hours_since_legionella\b" custom_components/heatpump_optimizer --include=*.py` for the readers. It returns the seams round 1 listed, with the same dispositions. This round adds no writer or reader, and its three `self._params()` reads are in `hours_since`, `_retry_hours` and `check_overdue`, the census's own seams. A second rule covers the callable class: `grep -n "self\._params\b[^(]" custom_components/heatpump_optimizer/legionella.py` returns only the constructor's assignment.

**Typing.** `/opt/hpo/venv-ha/bin/python tests/typing_ruler.py --mypy` (mypy 2.3.1, stubs 2026.9.3) prints `ok errors did not grow` and `ALL 9 typing-ruler checks PASSED`. At `538af1321` CI's `tests / typing` printed `legionella.py 6`, `FAIL by_code[attr-defined] did not grow [recorded 0, measured 6 (+6)]`.

**Scoped gate.** `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 22 script(s) run, 11 scoped out.` `GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub GATE_SCOPE=auto ./tests/run.sh` at this head prints `1 TEST SCRIPT(S) FAILED`, `tests/entities.py` (`2 of 2445 ENTITY CHECKS FAILED`, the two container reds under `## Red checks`). Every other script printed its pass line, including `ALL 4424 FEATURE CHECKS PASSED`, `ALL 112 HARNESS HEADER CHECKS PASSED`, `ALL 50 GUARD PIN CHECKS PASSED`, `ALL 9 typing-ruler checks PASSED` and `STRUCTURE RATCHET PASSED`. `git diff --quiet $(git merge-base origin/main HEAD)...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json` exits 0.

**Structure.** `PYTHONPATH=tests/hastub python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. This round re-records nothing.

**Architecture.** `PYTHONPATH=tests/hastub python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD` prints `Architecture score: dS +0.0077 IMPROVES`, with `literal_clone_copies 186 -> 185` and `shape_copies 44 -> 42`.

**Predictor.** `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` exits 0 and prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 7d2056970e08`. It lists no added unpinned site and no stale pin. Before the two deletions and the pins below, it printed `2 predicted red(s) on ledger` (`STALE PIN` on `_retry_hours` and `hours_since` CLAMP_DROP, whose pinned line read `self._params.`) and `10 unpinned site(s) the diff adds`.

## Unpinned sites

No site the diff adds is unpinned at this head; the predictor lists none (`## Figures`). Round 1's body called all 25 "pinned by `mutation-autofix`", and that was false for eight of them. The correction: every site now carries a `killed_by` row under `tests/mutation_ledger/killed_by/legionella.py/`, from CI's `ci: pin killed mutants` (`853a2a5de`) or from this round.

This round's rows come from `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3 --scripts tests/features.py`, which printed `PIN KILLED: 10 pinned, 0 left unpinned` (null control `NULL_COMMENT survived tests/features.py`). Run over every driver in play, the same command printed `MUTATION TABLE INCONCLUSIVE`, because `tests/entities.py`'s baseline carries the two container reds. So the drivers were narrowed to the one that kills.
- `days_since_confirmed` CMP_BOUND (the overdue threshold): killed by `tests/features.py`.
- `LegionellaGuard.async_track_cycle` CMP_BOUND (the fold's retry bound): killed by `tests/features.py`.
- `LegionellaGuard.async_track_cycle` CLAMP_DROP (the fold's peak): killed by `tests/features.py`.
- `LegionellaGuard._pending_attempt` CMP_BOUND and GUARD_OFF: killed by `tests/features.py`.
- `LegionellaGuard.check_overdue` BOOLOP (`watched`) and GUARD_OFF (the memo): killed by `tests/features.py`.
- `LegionellaGuard.check_mode_block` GUARD_OFF (the warning): killed by `tests/features.py`.
- `LegionellaGuard.hours_since` CLAMP_DROP and `LegionellaGuard._retry_hours` CLAMP_DROP: re-pinned on the `self._params()` lines, killed by `tests/features.py`. The two stale rows on the old lines are deleted.

## Red checks

The reds on `538af1321`, read from each job's log:

- `tests / typing`, `tests / fast (3.14)` (7 scripts red, `tests/harness_headers.py` among them), `tests / coverage-ratchet` (package 73.85 %, from a suite that crashed) and `tests / mutation-autofix` (`skip-measure-failed`): **one cause**. The merged-in main (#2817) made `params` a callable, and this branch's three reads used it as the object. Fixed at this head, and the harness `tests/harness_headers.py` executes now passes the callable.
  - The cheaper detector exists: `tests/typing_ruler.py --mypy` names the three lines. Its standing cost is one mypy run (about 2 min here) after any merge of main. The merge was the CI bot's `ci: merge main`, and no seat ran a detector after it.
- `tests / mutation`: the eight sites the verdict named survived every driver. Each now has a killing check (`## Mutation proof`) and a `killed_by` pin (`## Unpinned sites`).
- `pr-contract`: the round-1 body did not answer the reds above. This body does.
- `gate`: the aggregate of the reds above.
- `governance / delivery-status`: red on main's overdue rows for other pull requests. It is not a required context and not this diff's.
- `tests/entities.py` locally: `2 of 2445 ENTITY CHECKS FAILED` (`gate-sweep.yml: …` and `graders-head-copy's delivery_status step …`). The same two fail at `7d2056970e08` in this container, so they are the container's.

## Forward-carry

- **The step-0/step-1 flap.** The plan's legionella step alternates between step 0 and step 1 on consecutive solves. This PR folds those windows into one attempt for scheduling, but in control mode `_drive_switch` still turns the disinfection switch on and off with each window, now daily rather than weekly on a pump that cannot reach the target. The debounce alternative changes the per-boost switch contract `docs/configuration.md` documents. Carry: R10-IMMERSION-LATCH
- **A stale peak on the unreachable notice** (`marginal` keeps 55.4 °C). Carry: dismissed: the overdue notice stands beside it in every arm and names the completion's age, as the body says
- **The class_excess_loc payment's docstring trim** (round 1, `c9534b398`). Carry: dismissed: the budget is lowered, not raised, and no rationale is lost

## Friction

none

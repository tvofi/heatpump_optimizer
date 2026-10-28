fix(learner): freeze house heat-loss learning with no indoor thermometer (#2508)

The house heat-loss learner replays the elapsed interval from `ThermalState.room_temperature` and
then compares the result with that same field. With no indoor temperature entity configured,
`_update_current_state` never writes the field, so both sides hold the constructor's 21.0 C default.
`_learning_frozen` passes an unconfigured slot on purpose, so the sample goes through, and the
coefficient that gets persisted fits neither temperature.

`thermal_model.learner_room_unread(config)` returns the new freeze reason
`INDOOR_UNCONFIGURED_FREEZE` (`not_configured:indoor_temp_entity`) when the indoor entity is not
configured, and `None` when there is no config to inspect. It is a separate predicate, not a wider
`_learning_frozen`, so the unconfigured slots that `_learning_frozen` passes (power, outdoor, thermal
power) still pass. The lower-floor learner reads its own zone's sensor, so it still learns with no
indoor entity. Two call sites in `coordinator.py` consult the predicate:

- `_async_learn_house_heat_loss` hands it to `_replay_gate` as the raw freeze, ahead of
  `_learning_frozen`'s reason. It therefore ranks before the ventilation pass-through, and the
  detector is never fed a constant.
- `_run_system_identification` stands its experiment down on it, because that experiment seeds the
  same coefficient.

The reason is published through the existing path: `_learner_freeze_reason`, then
`_input_health_view()`, then `learner_freeze_reason` and `learners_frozen`.

The choice of shape comes from the fix commit's out-of-tree replay: a closed-loop two-zone plant,
42 days, five plants. This seat did not re-run it. On that replay:

| approach | UA bias |
|---|---|
| today's learner | -26% to -41% |
| freeze (this change) | publishes the configured prior |
| replay driven from the lower-floor sensor | +44% and -53% at the two ends of the observed zone split |
| floor-return proxy | -57% to -72% |
| learner with an indoor entity configured | within 1% |

The last row shows that the missing input is the defect, not the learner.

Refs #2508.

## Head

`e9887cf84e0532438a5f95a758b726f214034c50` (`handoff/r10-learner-default`). It is `f37c0dcae` plus
one merge of origin/main `beb570c81`, which had no conflict. It is not a re-cut. Earlier commits:

- the fix commit `8553201c54a60d3a656fead7d142524f1cb2f64a`
- merge `091211e11` of origin/main `edd7e0e14`
- `71a763148`: two #2508 checks
- `372c510a5`: the call site re-cut to the class budget
- merge `f37c0dcae` of origin/main `6d86acc90`

Three-dot against merge base `beb570c81`: `coordinator.py` +12/-11, `thermal_model.py` +34,
`tests/features.py` +77. These counts are the same as at `f37c0dcae`, because the new merge brings
in no path under `custom_components/`, `tests/features.py` or a budget file.

Since `f37c0dcae` only the body has changed:

- It answers the `arch-score / arch-score` red; see `## Architecture score` and `## Red checks`.
- The closing keyword stays `Refs`. I re-read roster group R10-LEARNER-DEFAULT in
  `dev/programme/rosters/wave-r10-groups.json` at `origin/handoff/audit-r10-roster` `b7e25cf06` and
  at `2ce021c6f`. Both list `issues: [2508]` and `fixes: [2508]`. Main `beb570c81` still lists
  `fixes: []`, and `tools/pr/prepr.sh` step 7 derives the intended list from main's roster. With a
  closing keyword on this issue, the step refuses it as "not in the intended list". So the close waits
  for the roster ref to merge; it is not a body edit.

  On the substance, a close would be correct. The issue asks for three things, and this change
  delivers each:

  1. A freeze with a visible reason, in #1955 (c)'s shape. `INDOOR_UNCONFIGURED_FREEZE` is that
     freeze, published as `learner_freeze_reason`.
  2. A choice between freezing and a substitute observable, made by measurement. The replay table
     above made that choice.
  3. A null control on a configured install. That is the "#2508 null control" check, plus the
     golden run under `## Figures`.

  Once the roster is on main, the orchestrator can change `Refs` to the closing keyword.

The first merge, `091211e11`, had one conflict, in `_async_learn_house_heat_loss`. Main had replaced
`frozen = replay_freeze(self._learning_frozen(...), ...)` with
`heat_kw, clean, frozen, fold = _replay_gate(self, interval, span_heat_kw, self._learning_frozen(...))`.

The resolution is `raw = learner_room_unread(ctx._config) or self._learning_frozen(...)`, passed to
`_replay_gate` as its `raw`:

- `replay_freeze` returns every reason except `UNMETERED_POWER_FREEZE` unchanged, so the room
  reason comes out of the gate as `frozen` and ranks first.
- `heat_energy.replay_gate` then returns `clean=False` for the cycle, so no heat-counter span
  closes over a constant room.

The alternative was `frozen = learner_room_unread(...) or frozen` after the gate. It sets the same
reason but leaves `clean=True`. The span check under `## Mutation proof` tells the two apart.

## Architecture score

Architecture score: dS -0.0006 WORSENS (inadmissible: coord_footprint 2408->2409). Command:
`python3 tools/audit/archscore/score.py --diff beb570c81 e9887cf84`.

- `coord_footprint` 2408 -> 2409: the rise is one new logic statement in
  `HeatPumpOptimizerCoordinator._async_learn_house_heat_loss`. It is the `raw =
  learner_room_unread(ctx._config) or self._learning_frozen(...)` assignment under the `#2508`
  comment. That method's `logic_stmts` count is 35 at the base and 36 at the head, and every other
  coordinator method is unchanged. The statement ranks the house learner's own room freeze ahead of
  `_replay_gate`, which the lower-floor learner shares, so the freeze cannot live inside the gate.

Payments considered; none taken:

1. **Inline `raw` into the `_replay_gate(...)` argument.** Measured with the same `logic_stmts` on
   a scratch copy: class 1977 -> 1976, and the method 36 -> 35. That is flat against the base. It
   computes the same `or`, but as an argument, where the counter does not see it. That is a
   step-17 shape: it moves the metric without improving the code. The named `raw` is also the
   variable the mutation proof's "merge resolution removed" mutant targets. Rejected as gaming.
2. **Put the predicate inside `_replay_gate`, or in `flow_meter.replay_freeze`.** Both serve the
   lower-floor learner too, which must keep learning with no indoor entity (the "#2508 guard"
   check). Doing so would be wrong, not a payment.
3. **Move it into a module helper that takes the coordinator.** The footprint charges by role, so
   the helper's `return ... or ...` is still +1. It only moves the statement. Rejected.
4. **Widen `_learning_frozen` with a required-slot notion.** #2508 forbids widening it ("Do not
   widen _learning_frozen for configured slots"). It would also add statements inside the class.
   Rejected.
5. **Leave `room_temperature` as `None` when the slot is unconfigured, so the existing `observed is
   None` guard catches it.** This changes the planner's input, because the planner steers from that
   default. It is out of this group's scope. It would also publish no freeze reason and would leave
   the span clean, which the span check refuses. Rejected.

No `*_budgets.json` moves: `STRUCTURE RATCHET PASSED`, see `## Figures`.

## Mutation proof

Each run is `tests/features.py` with `PYTHONPATH=tests/hastub`, in a `git archive` tree of
`372c510a5`; `e9887cf84` carries the same production code and tests.

An archive tree is not a git checkout, so the check "and the path that proceeds still stamps a
resolvable recorded_at (#363)" fails in every one of these trees, the unmutated head included
(`recorded_at = 'unknown'`). Every count below includes that failure.

| mutant | result | red checks |
|---|---|---|
| unmutated head | `1 of 4539` | the #363 check only |
| `learner_room_unread` returns `None` (the predicate never freezes) | `4 of 4539` | 1, 2, 3 |
| merge resolution removed (`raw = self._learning_frozen(...)`) | `3 of 4539` | 1, 2 |
| rejected post-gate ordering: `raw` back to `_learning_frozen`, then `frozen = learner_room_unread(ctx._config) or frozen` after the gate | `2 of 4539` | 2 only |
| `config is None` guard deleted | `5 of 4539` | 3, plus three sysid checks the stand-down reaches |

The numbered checks:

1. "#2508: no indoor temperature entity freezes the house heat-loss learner ...". Its red output:
   `samples 1 scale 1.0061538461538462 reason None`.
2. "#2508: a cycle with no indoor entity leaves no heat-counter span clean; a configured one
   does". Its red output: `{'no_indoor': True, 'indoor': True}`.
3. "#2508: a caller that cannot see the entry (config None) invents no freeze; ...".

The three sysid checks are "the control: with no mode entity the experiment is untouched", "#943
wiring: _run_system_identification passes the configured slab pair" and "#943: the honest sizer
leaves a power-limited heavy house ...".

## Null control

Main `edd7e0e14`, whose production code is identical to `beb570c81`'s for these three files, run
with this head's `tests/features.py`:

- Check 1 is red (`samples 1 scale 1.0061538461538462 reason None`), and so is the span check
  (`{'no_indoor': True, 'indoor': True}`). That is the defect on main.
- Both null controls pass there: "#2508 null control: a configured indoor entity still learns, and
  its unconfigured power slot does not freeze it", and "#2508 guard: the lower-floor learner still
  learns with no indoor entity".
- The run then stops at the config-None check's import, because main has no
  `learner_room_unread` (`ImportError`, rc 1).

## Figures

- Scoped gate at `e9887cf84`:
  `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`, on Python
  3.11.17. The mode line reads `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` and the summary
  reads `3 TEST SCRIPT(S) FAILED` (rc 1): `tests/entities.py`, `tests/stress.py`,
  `tests/harness_headers.py`. Each failure is a Python-3.12+ construct that this 3.11 interpreter
  cannot run:
  - `AttributeError: module 'sys' has no attribute 'monitoring'`
  - `SyntaxError: f-string expression part cannot include a backslash`

  The 3.12 re-run and the merge-base control are below. Every other script passed, including
  `ALL 4539 FEATURE CHECKS PASSED` and `STRUCTURE RATCHET PASSED`.
- Golden null control for configured installs (every golden scenario configures an indoor entity), from the same gate run: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`; 37 scenarios read `byte-identical to origin/main` and the rest are listed may-drift fixtures reading `did not move here` (count: `grep -c 'byte-identical to origin/main'` over the run's drift section; a moved fixture prints a non-`ok` line there, and none did).
- The three re-run at `e9887cf84` under Python 3.12.3 (scratch venv, same pins): `ALL 2467 ENTITY CHECKS PASSED`, `ALL 113 STRESS CHECKS PASSED`, `ALL 112 HARNESS HEADER CHECKS PASSED`, each rc 0: `PYTHONPATH=tests/hastub python3 tests/<script>.py`.
- Null control for the 3.11 failures: the same three at merge base `beb570c81` under the same 3.11 venv also fail (`entities.py` the identical `SyntaxError: f-string: expecting '}'` at its line 4253, `stress.py` `7 of 110`, `harness_headers.py` `14 of 112`), so they are the interpreter's, not this diff's.
- `Architecture score: dS -0.0006 WORSENS (inadmissible: coord_footprint 2408->2409)`:
  `python3 tools/audit/archscore/score.py --diff beb570c81 e9887cf84`, run at `date -u`
  2026-10-28 against main `beb570c81`.
- Per-method `logic_stmts` (`tools/audit/archscore/metrics/footprint.py`), applied to the
  coordinator class at `beb570c81`, at `e9887cf84`, and on a scratch copy of `e9887cf84` with `raw`
  inlined:

  | tree | class | `_async_learn_house_heat_loss` | `_run_system_identification` |
  |---|---|---|---|
  | base `beb570c81` | 1976 | 35 | 9 |
  | head `e9887cf84` | 1977 | 36 | 9 |
  | inlined copy | 1976 | 35 | 9 |

- The `1 of 4539` through `5 of 4539 FEATURE CHECKS FAILED` counts come from the same features
  command, in the trees under `## Mutation proof`.

## Red checks

`arch-score / arch-score` concluded red at `bcdd455df` and again at the PR head's latest runs:
`Architecture score: dS -0.0006 WORSENS (inadmissible: coord_footprint 2410->2411)`. The rise is
the one statement this diff adds. `## Architecture score` names it and gives the payments
considered. No cheaper detector exists: `tests/structure.py`'s class budgets count lines, not
`logic_stmts`, and moved no row, so the archscore gate is the first detector, and it ran on the
first push.

`pr-contract / pr-contract` was red at `bcdd455df` for the review-bus refusal
`red-unanswered: concluded red check arch-score / arch-score is not named in ## Red checks`. That
was the body's omission, answered above. It re-takes when this body is set.

`tests / mutation` is red by construction on the one site under `## Unpinned sites`.
`tools/pr/ci_predict.py --base origin/main` at `e9887cf84` still lists it as the only one: `CI PREDICT: 1 unpinned site(s) the diff adds`.

Predicted at `e9887cf84`: `CI PREDICT: no closures, fast, wave-script or instrument red predicted against beb570c817c4`, and `git merge-tree --write-tree origin/main e9887cf84` is clean.

## Unpinned sites

- `custom_components/heatpump_optimizer/thermal_model.py:1449 GUARD_OFF`: the `config is None`
  guard. It is killed when measured: deleting it turns 4 checks red (the last row under
  `## Mutation proof`). It is unpinned only in the mutant ledger, which `mutation-autofix` writes
  after the push.

## Forward-carry

none

## Friction

none

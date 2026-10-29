fix(learner): no indoor thermometer is no observed room for the heat-loss learner, sysid, #16's accuracy and #2's curve comfort (#2508)

With no indoor temperature entity configured, `_update_current_state` never writes
`ThermalState.room_temperature` (it writes it only under `if indoor.ok`), so the field keeps its 21.0 C
constructor default. `_learning_frozen` passes an unconfigured slot on purpose, so every reader that
gates on it alone then reads that constant as a measurement. The house heat-loss learner replays the
elapsed interval from the field and compares the result with the same field, so the coefficient it
persists fits neither temperature.

`thermal_model.learner_room_unread(config)` returns the freeze reason `INDOOR_UNCONFIGURED_FREEZE`
(`not_configured:indoor_temp_entity`) when the indoor entity is not configured, and `None` when there is
no config to inspect. It is a separate predicate, not a wider `_learning_frozen`, so the unconfigured
slots that `_learning_frozen` passes (power, outdoor, thermal power) still pass. The lower-floor learner
reads its own zone's sensor, so it still learns with no indoor entity. Four call sites in
`coordinator.py` consult the predicate. Together they are every seam the rule under `## Figures`
returns:

- `_async_learn_house_heat_loss` hands it to `_replay_gate` as the raw freeze, ahead of
  `_learning_frozen`'s reason. It therefore ranks before the ventilation pass-through, and no
  heat-counter span closes clean over a constant room.
- `_run_system_identification` stands its experiment down on it, because that experiment seeds the
  same coefficient.
- `_record_accuracy` (new in this round) reads no room when it is set. #16's lead-time promises are not
  settled against the default, and the interval's `AccuracySample` keeps its power with
  `actual_temp=None`. Every reader of `actual_temp` already skips `None`: `_paired`, `_refit_pair`,
  `measured_since` and `_settle_interval_diag`.
- `_track_curve_comfort` (new in this round) collects no evidence when it is set. The indoor entity
  writes both `room_temperature` and `upper_floor_temperature`, so both are 21.0 C defaults, and a
  margin of `21.0 - floor` read every tick as a comfortable day would creep #2's bias downward.

The heat-loss freeze is published through the existing path: `_learner_freeze_reason`, then
`_input_health_view()`, then `learner_freeze_reason` and `learners_frozen`.

The choice of a freeze over a substitute observable comes from the first fix commit's out-of-tree
replay: a closed-loop two-zone plant, 42 days, five plants. This seat did not re-run it. On that
replay:

| approach | UA bias |
|---|---|
| today's learner | -26% to -41% |
| freeze (this change) | publishes the configured prior |
| replay driven from the lower-floor sensor | +44% and -53% at the two ends of the observed zone split |
| floor-return proxy | -57% to -72% |
| learner with an indoor entity configured | within 1% |

The last row shows that the missing input is the defect, not the learner.

Refs #2508.

## Review round 1

`origin/review/2919` returned `Fix review: blocked` at `2d151b5c8`. Each item:

1. **mutation-vacuous: the sysid stand-down.** The new check "#2508: a sysid night whose config has
   no indoor entity aborts as not_configured:indoor_temp_entity and records nothing" drives
   `_p5_night` into its step phase, then unconfigures the indoor entity through `harness.with_config`.
   The reviewer's own mutant turns it red: `) or learner_room_unread(getattr(ctx, "_config", None))`
   -> `)`. Its red output is `{'entered_step': True, 'recorded': 1, 'phase': 'step', 'reason': ''}`.
   It is the row `sysid` under `## Mutation proof`. Its null control is the existing "#1523 null
   control: a clean night reaches the step phase and records its tick".
2. **class-open: `_record_accuracy`.** Guarded as described above, with a check, and both of its
   reads are pinned: the lead score (row `acc`) and the sample's `actual_temp` (row `sample`). I
   wrote the class's enumeration rule into the body as a command (`## Figures`, "class seams"). It
   returns seven functions. Each one's disposition is listed there.
3. **Findings: `_track_curve_comfort` and `_record_quiet_comfort_period`.** The first is harmed: its
   `temps` read the 21.0 C room and the 21.0 C upper zone, so a no-indoor single-zone install books
   `21.0 - floor` every tick. It is now guarded (row `curve`). The second reads only
   `result.room_temp_trajectory`, which is a plan and not a reading. The rule returns it with
   `reads_room=False`, and it stays as is. The review's `Carry: R10-LEARNER-DEFAULT` is discharged in this diff, so no later stage has to change how it works.

The new guard in `_track_curve_comfort` pushed `functions_cc_over_15` from 28 to 29. I paid for it by
moving the pure "coldest finite zone less the floor" computation into
`curve_learning.worst_zone_margin_k`, beside the learner that consumes it. That brings
`functions_cc_over_15` back to 28, lowers `class_excess_loc` from 18037 to 18032 and `max_class_loc`
from 8160 to 8155, and brings `coord_footprint` back to 2409. Both lowered rows are re-recorded in
`tests/structure_budgets.json`, with the reason in commit `d01656dad`. No budget is raised.

## Head

`3f97edb7f55ffafbc9ee3538eead3e5d9db2c8a5` (`handoff/r10-learner-default`). It is the reviewed head
`2d151b5c878db63b48a1e9eb48201925650ccfa2` plus three commits, with no merge:

- `3016b33bd`: the `_record_accuracy` and `_track_curve_comfort` guards, and the sysid and accuracy
  checks
- `d01656dad`: `worst_zone_margin_k`, and the structure re-record
- `3f97edb7f`: the check that pins `if margin is None`

`2d151b5c8` merges the authored code head `e9887cf84` with origin/main `b6f6ceca4`. Its history is
the earlier body's: fix commit `8553201c5`, merges `091211e11`, `f37c0dcae` and `e9887cf84`, and
commits `71a763148` and `372c510a5`. In the first merge, `091211e11`, the conflict in
`_async_learn_house_heat_loss` was resolved as
`raw = learner_room_unread(ctx._config) or self._learning_frozen(...)`, passed to `_replay_gate` as its
`raw`. The rejected alternative was `frozen = learner_room_unread(...) or frozen` after the gate. It
leaves `clean=True`, and row `postgate` tells the two apart.

Merge base `b6f6ceca4`. Three-dot (`git diff --stat $(git merge-base origin/main HEAD)...HEAD`):
`coordinator.py` +28/-32, `curve_learning.py` +12, `thermal_model.py` +34, `tests/features.py` +155,
`tests/structure_budgets.json` +3/-3 (`git diff --numstat b6f6ceca4...HEAD`). The delivery row and the ledger entry come from the orchestrator
and the mutation-autofix bot. Origin/main is at `593f57c44` (`date -u` 2026-10-29), and
`git merge-tree --write-tree origin/main HEAD` is clean, so the branch is not merged (fixer step 6).

The closing keyword stays `Refs`. Main's roster still lists R10-LEARNER-DEFAULT with `fixes: []`,
and `tools/pr/prepr.sh` step 7 refuses a closing keyword outside that list. The orchestrator can
change it once the roster ref is on main. On the substance, a close would be correct: this change
delivers the freeze with a visible reason, the measured choice of a freeze over a substitute, and a
null control on a configured install.

## Architecture score

Architecture score: dS -0.0006 WORSENS (inadmissible: coord_footprint 2408->2409). Command:
`python3 tools/audit/archscore/score.py --diff b6f6ceca4 HEAD`.

- `coord_footprint` 2408 -> 2409. This is the same figure as at the reviewed head `2d151b5c8`. The
  two new guards are in-place edits of an existing condition and an existing assignment, so they add
  no statement. Moving the margin computation out of the class paid for the one statement they did
  add (2410 -> 2409 between `3016b33bd` and `d01656dad`). The remaining +1 is the `raw =
  learner_room_unread(ctx._config) or self._learning_frozen(...)` assignment in
  `_async_learn_house_heat_loss`. It ranks the house learner's own room freeze ahead of
  `_replay_gate`, which the lower-floor learner shares, so the freeze cannot live inside the gate.

Payments considered for that statement; none taken (the reviewer judged these five and found no
missed payment):

1. Inline `raw` into the `_replay_gate(...)` argument. This is flat in `logic_stmts` only because
   the counter does not see an argument. That is a step-17 shape, gaming. Rejected.
2. Put the predicate inside `_replay_gate` or `flow_meter.replay_freeze`. Both serve the lower-floor
   learner, which must keep learning ("#2508 guard" check). Wrong, not a payment.
3. Move it into a module helper that takes the coordinator. The footprint charges by role, so this
   only moves the statement. Rejected.
4. Widen `_learning_frozen` with a required-slot notion. #2508 forbids it, and it adds statements
   inside the class. Rejected.
5. Leave `room_temperature` `None` when the slot is unconfigured. This changes the planner's input,
   which is out of this group's scope, and it publishes no freeze reason. Rejected.

A sixth option for this round's guards was a coordinator helper `_room_frozen()` shared by the four
sites. It adds a method and an attribute read to the class, so it costs more footprint than the
in-place guards. Rejected.

## Mutation proof

Each run is `PATH=<venv>/bin:$PATH PYTHONPATH=tests/hastub python tests/features.py` in a
`git worktree add --detach` checkout with one mutant applied. A checkout is not an archive, so the #363
`recorded_at` check passes in every tree. The four reviewer mutants ran in checkouts of `3f97edb7f`.
The other seven ran in checkouts of `d01656dad` with `3f97edb7f`'s `tests/features.py` copied in,
which is `3f97edb7f`'s tree, because that commit changes only that file. The unmutated head reads `ALL 4543 FEATURE CHECKS PASSED`.

| mutant | production edit | result | red checks |
|---|---|---|---|
| `sysid` | `) or learner_room_unread(getattr(ctx, "_config", None))` -> `)` | `1 of 4543` | S |
| `acc` | `actual_now = None if learner_room_unread(...) else ...room_temperature` -> `actual_now = ctx._current_state.room_temperature` | `1 of 4543` | A |
| `sample` | `actual_temp=actual_now,` -> `actual_temp=ctx._current_state.room_temperature,` | `1 of 4543` | A |
| `curve` | `(self._learning_frozen(CONF_INDOOR_TEMP_ENTITY) or learner_room_unread(ctx._config)) is not None` -> `self._learning_frozen(CONF_INDOOR_TEMP_ENTITY) is not None` | `1 of 4543` | A |
| `mguard` | `if margin is None: return` deleted | `1 of 4543` | N |
| `boolop` | `t is not None and np.isfinite(t)` -> `or` | script aborts, rc 1 | `TypeError: ufunc 'isfinite' not supported` |
| `retdel` | `return min(temps) - floor_c if temps else None` -> `pass` | `6 of 4543` | A, W, and four curve-learner checks |
| `none` (`learner_room_unread` returns `None`) | reviewer's `mutant_m_none.diff` | `5 of 4543` | 1, 2, 3, A, S |
| `rawonly` (merge resolution removed) | reviewer's `mutant_m_rawonly.diff` | `2 of 4543` | 1, 2 |
| `postgate` (rejected ordering) | reviewer's `mutant_m_postgate.diff` | `1 of 4543` | 2 |
| `guard` (`config is None` deleted) | reviewer's `mutant_m_guard.diff` | `4 of 4543` | 3, plus three sysid checks |

The checks:

- S: "#2508: a sysid night whose config has no indoor entity aborts as not_configured:indoor_temp_entity and records nothing". Red: `{'entered_step': True, 'recorded': 1, 'phase': 'step', 'reason': ''}`.
- A: "#2508: with no indoor entity no lead promise settles against the 21.0 C default, the interval sample keeps its power with no room, and no curve-comfort margin is booked; a configured entity does all three". Its no-indoor arm is red under `acc` as `{'lead_scored': True, 'sample_room': [21.0], 'curve_worst': None}`, under `sample` as `{'lead_scored': False, 'sample_room': [21.0], 'curve_worst': None}` and under `curve` as `{'lead_scored': False, 'sample_room': [None], 'curve_worst': 2.5}`. Each mutant moves exactly its own field. The configured arm, `{'lead_scored': True, 'sample_room': [21.0], 'curve_worst': 2.5}`, is the null control in every run.
- N: "#2508: a curve-comfort tick with no finite zone books nothing and raises nothing". Red: `tick TypeError("'<=' not supported between instances of 'NoneType' and 'float'")`.
- W: "#2508: the curve-comfort margin is the coldest finite zone less the floor, and no finite zone is no evidence".
- `retdel`'s four curve-learner checks: "the day's evidence is the WORST margin, not the last one", "touching the floor with the bias applied resets it immediately", "and the same dip with no defrost is a genuine miss that still resets", "a new day folds the previous day's worst margin into the curve learner once". The existing curve tests drive the moved computation through `worst_zone_margin_k`.
- 1: "#2508: no indoor temperature entity freezes the house heat-loss learner ...". 2: "#2508: a cycle with no indoor entity leaves no heat-counter span clean; a configured one does". 3: "#2508: a caller that cannot see the entry (config None) invents no freeze; ...".
- The three sysid checks under `guard`: "the control: with no mode entity the experiment is untouched", "#943 wiring: _run_system_identification passes the configured slab pair" and "#943: the honest sizer leaves a power-limited heavy house ...".

## Null control

The reviewed head `2d151b5c8`, run with this head's `tests/features.py` (the same command, Python
3.12.3): check A is red with
`no indoor {'lead_scored': True, 'sample_room': [21.0], 'curve_worst': 2.5}`. That is the
`_record_accuracy` and `_track_curve_comfort` defect at the reviewed head, all three fields at once.
The run then stops at the `worst_zone_margin_k` import (`ImportError`, rc 1), because that tree has no
such function. The sysid site already carried its clause at `2d151b5c8`, so its null control is the
`sysid` mutant above, not this tree.

The configured arm of check A, "#2508 null control: a configured indoor entity still learns, and its
unconfigured power slot does not freeze it", and "#2508 guard: the lower-floor learner still learns
with no indoor entity" all pass at the head. These are the controls on an install that keeps an
indoor entity, or keeps its own lower-zone sensor.

## Figures

- Class seams (fixer step 8). Rule: every function in `coordinator.py` that calls
  `_learning_frozen(...)` with `CONF_INDOOR_TEMP_ENTITY` among its arguments, with whether it loads
  `.room_temperature` and whether it calls `learner_room_unread`. The command is
  `python3 -I seams_2508.py <rev>` with this source (scratch, quoted whole):

  ```python
  import ast, subprocess, sys
  src = subprocess.check_output(["git", "show", f"{sys.argv[1]}:custom_components/heatpump_optimizer/coordinator.py"], text=True)
  for fn in ast.walk(ast.parse(src)):
      if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
          continue
      calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)]
      frozen = any(getattr(c.func, "attr", None) == "_learning_frozen"
                   and any(getattr(a, "id", None) == "CONF_INDOOR_TEMP_ENTITY" for a in c.args) for c in calls)
      reads = any(isinstance(n, ast.Attribute) and n.attr == "room_temperature" and isinstance(n.ctx, ast.Load) for n in ast.walk(fn))
      if frozen:
          unread = any(getattr(c.func, "id", None) == "learner_room_unread" for c in calls)
          print(f"{fn.name}: reads_room={reads} consults_learner_room_unread={unread}")
  ```

  | function | at `3f97edb7f` | disposition |
  |---|---|---|
  | `_async_learn_house_heat_loss` | reads_room=True consults=True | closed in this diff (round 0) |
  | `_run_system_identification` | reads_room=True consults=True | closed in this diff, pinned by S |
  | `_record_accuracy` | reads_room=True consults=True | closed in this diff, pinned by A (`acc`, `sample`) |
  | `_track_curve_comfort` | reads_room=True consults=True | closed in this diff, pinned by A (`curve`) |
  | `_async_learn_lower_floor_loss` | reads_room=False | out of the class: its observable is its own zone sensor ("#2508 guard") |
  | `_inputs_unhealthy` | reads_room=False | out of the class: a health verdict, no room read |
  | `_record_quiet_comfort_period` | reads_room=False | out of the class: reads the plan trajectory |

  The rule's null control is the same command at `2d151b5c8`. It returns the same seven functions,
  with `_record_accuracy` and `_track_curve_comfort` at `reads_room=True consults_learner_room_unread=False`:
  the two open seams the review found. The rule's limit: a reader of `room_temperature` that never
  consults `_learning_frozen` (the planner, which steers from the default) is outside it. Payment 5
  above already records that one as out of this group's scope.
- Feature counts (`ALL 4543 FEATURE CHECKS PASSED`, and each `N of 4543` under `## Mutation proof`):
  the command under `## Mutation proof`, Python 3.11.17 venv with `tests/requirements-ci.txt`'s pins
  installed without hash mode (`--require-hashes` refuses an unpinned line on this interpreter).
- Scoped gate at `3f97edb7f`: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`,
  Python 3.12.3 venv, rc 0. The mode line reads `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` and the
  summary reads `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN`. It includes `ALL 4543 FEATURE CHECKS PASSED` and
  `STRUCTURE RATCHET PASSED`.
- Golden null control for configured installs (every golden scenario configures an indoor entity), from the same gate run:
  `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` and
  `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. 37 scenarios read
  `byte-identical to origin/main` (`grep -c 'byte-identical to origin/main'` over the run's log). A moved
  fixture prints a non-`ok` line there, and none did.
- `python3 tests/structure.py` at `3f97edb7f`: `STRUCTURE RATCHET PASSED`. At `3016b33bd` it read
  `FAIL functions_cc_over_15 29 > 28 (+1)`, and at `d01656dad` before the re-record it read
  `2 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED` (`class_excess_loc 18037 -> 18032`,
  `max_class_loc 8160 -> 8155`).
- `Architecture score: dS -0.0006 WORSENS (inadmissible: coord_footprint 2408->2409)`:
  `python3 tools/audit/archscore/score.py --diff b6f6ceca4 HEAD`. The same command at `2d151b5c8`
  prints the same line, and at `3016b33bd` it printed `coord_footprint 2408->2410`.
- `CI PREDICT: no closures, fast, wave-script or instrument red predicted against b6f6ceca4f03` and `CI PREDICT: 4 unpinned site(s) the diff adds`: `python3 tools/pr/ci_predict.py --base origin/main` at `3f97edb7f`.

## Red checks

`arch-score / arch-score` concluded red at `bcdd455df` with
`Architecture score: dS -0.0006 WORSENS (inadmissible: coord_footprint 2410->2411)`. The rise is the
one statement `## Architecture score` names, together with the payments considered. No cheaper
detector exists: `tests/structure.py`'s class budgets count lines, not `logic_stmts`, so the archscore
gate is the first detector, and it ran on the first push. It has concluded success on every head
since the body answered it.

`pr-contract / pr-contract` was red at `bcdd455df` for
`red-unanswered: concluded red check arch-score / arch-score is not named in ## Red checks`. That
was the body's omission, and it is answered above.

`tests / mutation` (`mutation`) is predicted red at this head, by construction, on the four sites under
`## Unpinned sites`. Each one was killed when measured, and the pin is the ledger entry that
`mutation-autofix` writes after the push (`ci-autofix.md`). No cheaper detector exists: `prepr.sh`
step 6d (`ci_predict.py`) already names each site before the push, and that is the detector this red
answers.

No check concluded red at `2d151b5c8`. This round's own near-red, `functions_cc_over_15` 29 > 28,
was caught locally by `tests/structure.py` before the push and paid for (`## Review round 1`).

## Unpinned sites

`tools/pr/ci_predict.py --base origin/main` at `3f97edb7f` lists the sites below. Each was killed when
measured under `## Mutation proof`. They are unpinned only in the ledger, which `mutation-autofix`
writes after the push, because its lane mutates `custom_components/`.

- `custom_components/heatpump_optimizer/coordinator.py:9044 GUARD_OFF` (`_track_curve_comfort`'s freeze guard): killed by mutant `curve` (check A).
- `custom_components/heatpump_optimizer/coordinator.py:9060 GUARD_OFF` (`if margin is None`): killed by mutant `mguard` (check N).
- `custom_components/heatpump_optimizer/curve_learning.py:62 BOOLOP` (`and` -> `or`): killed by mutant `boolop` (the script aborts on a `None` zone).
- `custom_components/heatpump_optimizer/curve_learning.py:63 RETURN_DEL`: killed by mutant `retdel` (6 checks).

The earlier unpinned site, `thermal_model.py` `learner_room_unread GUARD_OFF`, is pinned now: its
ledger entry `tests/mutation_ledger/killed_by/thermal_model.py/learner_room_unread.GUARD_OFF.48542026.json`
is in the diff, and `ci_predict.py` no longer lists it.

## Forward-carry

none

## Friction

none

Part of #2499.

The unsensed slab (no floor-return sensor) was moved forward open-loop along the previous plan's
`slab_temp_trajectory`, which assumes the heat the plan COMMANDED was delivered. When a pump drew
less (setpoint-driven, capped or modulating down), the slab estimate kept heat that never arrived.
The house heat-loss learner then replayed the next interval from that too-warm slab, found the room
colder than it predicted, and booked the gap as fabric loss. `house_heat_loss_scale` climbed and the
plan booked more heat each day: the brief's over-booking.

The fix: where a power entity exists, `coordinator._propagated_slab` replays the elapsed interval
through `_replay_interval` (the house learner's own replay, same model, and the flow-meter
substitution where a heat meter exists) at the metered space draw `draw_range.space_draw_kw`.
Standby at or below `draw_range.running_kw`'s floor counts as no heat. A resistive element on the
meter, no reading, no previous sample, a zero or negative gap, or a gap past
`HOUSE_LOSS_MAX_SAMPLE_HOURS` falls back to the plan's trajectory, which is the old behaviour. No
heat meter is needed. **An install with no power entity at all is unchanged**: with no draw
reading, the delivery shortfall cannot be told apart from UA (see Null control and Forward-carry).

The fix sits on its own seam. The draw arithmetic (running floor, space share) goes in
`draw_range.py`, which owns the draw concept and has no HA import. The coordinator only orchestrates
(`_propagated_slab` is mapped `core` in `tests/seam_map.json`). Alternatives that lost:
(a) reuse `_interval_space_power` for the slab. It returns `None` under `COP_TRACKING_ERROR_GATE`
exactly when the pump draws far less than commanded, so the slab would fall back to the commanded
trajectory in the very intervals that cause the bias. (b) Correct the learner instead, by skipping
samples after an under-delivery. That starves the learner and leaves the slab wrong for every other
reader. (c) Use a heat-meter-only path. The brief forbids it (every install, no heat meter).

To pay the budgets, the DHW tracking block in `_update_current_state` moved to
`_track_dhw` (seam `dhw`), and `_settle_interval_diag`'s inline space share now calls
`draw_range.space_share`.

This repair round (the `tests / mutation` and `pr-contract` reds at 398daa3e5) adds no production
line. It adds five `#2499` checks to `tests/features.py` that drive the six sites the ratchet counted
unpinned, records their six `killed_by` pins, and merges `origin/main`.

## Head

65d37a7cbb83111e8cb0e929bbe91e571ed1ed4d, merge base 343fb2a2c23dbb1a78142ce869be495187b8d481
(`origin/main` at 2026-10-24T18:45Z). Rule for the production-tree claims below:
`git diff --stat 4a00a3f053c252b3bbf9f0e75ae36d27331f8ac3 343fb2a2c23dbb1a78142ce869be495187b8d481 -- custom_components tests/golden tests/structure_budgets.json tests/mutation_budgets.json tests/mutation_ledger tests/features.py`
prints nothing, and `git diff --stat df2737ed4 65d37a7cb -- custom_components tests/features.py tests/mutation_ledger tests/golden`
prints nothing. So figures taken at base 4a00a3f05 and head df2737ed4 (or f3ca049bf, which differs
from it only by ledger files) describe the same production and test trees as this base and head.

## Mutation proof

Re-run at df2737ed4 from detached worktrees, `PYTHONPATH=tests/hastub python3 tests/features.py`:

- M1, the predicate of the closed-loop branch in `_propagated_slab`:
  `if kw is not None and ...` -> `if False and kw is not None and ...`. Red (`3 of 4367 FEATURE CHECKS FAILED`, rc=1):
  `#2499: a metered pump that drew nothing leaves the slab cooling, not at the plan's commanded 25 degC [slab=25.000]`,
  `#2499: the slab rises with the metered draw, below the commanded trajectory while the pump draws less than 4 kW [slab off/1kW/4kW=25.000/25.000/25.000]`,
  `#2499: a gap of exactly the sample window still advances the slab by the meter; a minute past it follows the plan [slab edge/past=25.000/25.000]`.
- M2, the standby floor in `draw_range.running_kw`:
  `drawn_kw > floor` -> `drawn_kw > 0.0`. Red (`3 of 4367 FEATURE CHECKS FAILED`, rc=1):
  `#2499: a standby draw under the running floor heats nothing [slab standby=22.907 off=22.840]`,
  `#2499: a draw at the running floor is standby, not heat`,
  `#2499: a learned idle draw above the fixed floor raises it to IDLE_MARGIN times the idle draw [idle_kw=0.4]`.
  Both restored; worktrees discarded.

The six ratcheted mutants of this round, driven by
`PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py --jobs 4`
at f3ca049bf (baseline `tests/features.py: rc=0 failed=0`; null control `coordinator.py:510 NULL_COMMENT` survived):
each took `tests/features.py` from `rc=0 failed=0` to `rc=1 failed=2`, and the run printed
`PIN KILLED: 6 pinned, 0 left unpinned`. The recorded pins are the six `killed_by` files under
`tests/mutation_ledger/killed_by/` named in `## Unpinned sites`.

Failing test first (from the original round, production unchanged since): the head's
`tests/features.py` against the merge base's production tree failed the two slab checks M1 names
first, then raised `AttributeError: module 'heatpump_optimizer.draw_range' has no attribute 'space_draw_kw'`.
At the head `ALL 4367 FEATURE CHECKS PASSED` (`PYTHONPATH=tests/hastub python3 tests/features.py` at f3ca049bf).

## Null control

- No power entity (`nometer_half` arm): the row is identical at both ends (scale 1.858,
  plan/deliv 1.908, plan_kwh [15.7, 17.4, 20.2, 24.9, 27.2]). The meter is what moves the result,
  so the fix leaves a no-meter install alone. This is also the residual: the shortfall cannot be
  seen there.
- Flat price, ideal delivery (`null`, `true0.5`, `owner_ideal`): the learned scale stays on the
  truth at both ends (null 1.011 -> 0.98 against true 1.0; true0.5 0.511 -> 0.504 against 0.5;
  owner_ideal 0.611 -> 0.611 against 0.6). With no shortfall, the fix has nothing to correct.
- Slab oracle (`*_oracle` arms seed the TRUE slab): the rows are identical at both ends, by
  construction. They are the upper bound: owner_i01_oracle scale 0.619, plan/deliv 0.854.
- In-test nulls: `#2499: without a power meter the slab follows the plan (null control)`,
  `with no previous sample time the slab follows the plan` and
  `a zero or negative gap replays nothing; the slab follows the plan` pass at the head.
- Mutation-table null: the comment-only edit `coordinator.py:510 NULL_COMMENT` survived `tests/features.py`.

## Figures

Harness `dev/audit/harnesses/r10_demand_overbook.py` (sha1 f0575c58b587d9a41e922fb5393e1a30a7ddba0b,
this head's copy, unchanged this round). Run at both ends from the same copy:
`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_demand_overbook.py --dp`,
base = a worktree at 4a00a3f05, head = f3ca049bf (production identical to this head, rule in `## Head`).
The run is synthetic: 30-min closed loop, real coordinator learners and real optimizer, no heat
sensor, flat price unless `spread`, days 2..end. `scale` is the learned `house_heat_loss_scale`.
`plan/deliv` is the 12-h plan energy at 00:00 and 12:00 summed per day, over the electric energy
delivered. `samples` is the count of accepted house-learner samples.

| arm (true scale) | base scale | head scale | base plan/deliv | head plan/deliv |
|---|---|---|---|---|
| owner_i01 (0.6; 1.5-5 kW clamp, delivers min(3, 0.4c), 0.1 kW idle) | 1.221 | 0.616 | 1.674 | 0.854 |
| owner_i01_spread (0.6; same, price spread) | 1.584 | 0.733 | 1.847 | 0.666 |
| owner_i03 (0.6; 0.3 kW idle) | 1.0 (0 samples) | 1.0 (0 samples) | 1.642 | 1.084 |
| meter_half (1.0; delivers 0.5c) | 2.041 | 1.289 | 1.711 | 1.097 |
| meter_sat3 (1.0; caps at 3 kW) | 1.099 | 0.994 | 1.25 | 1.194 |
| slab3x (1.0; 3x slab mass) | 0.911 | 0.888 | 0.953 | 0.938 |
| nometer_half (1.0; no power entity) | 1.858 | 1.858 | 1.908 | 1.908 |
| owner_i01_oracle (0.6) | 0.619 | 0.619 | 0.854 | 0.854 |
| meter_half_oracle (1.0) | 1.051 | 1.051 | 1.016 | 1.016 |

The head reaches the slab-oracle bound on owner_i01 (0.616 against 0.619, plan/deliv 0.854 both).
meter_half still sits above its oracle (1.289 against 1.051), which is the share of bias this fix
does not remove.

DP reference (`--dp`, owner_i01's last 12-h window). This is a DP over a (room, slab) grid on the
optimizer's own objective with cycling and capacity relaxed (`_dp_reference` docstring), on the
learned model and on the true house:

- learned model: base plan_kwh 6.95 / DP 5.38 (cost gap 0.0665); head plan_kwh 5.27 / DP 3.75 (cost gap 0.158)
- true house from its true slab: base DP needs 1.5 kWh against plan 6.95 (gap 0.9027); head DP needs 3.75 against plan 5.27 (gap 0.1598)

This is one window, and the two ends start from different states. It is a reference, not an
optimality proof (see Forward-carry).

Architecture: `python3 tools/audit/archscore/score.py --diff 343fb2a2c23dbb1a78142ce869be495187b8d481 HEAD`
at 65d37a7cb prints `dS +0.3249` (duplication_copies 39 -> 38, coord_footprint 2463 -> 2465); see
`## Architecture score`. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` at 65d37a7cb. Nothing is raised.

Mutation ratchet: `python3 tests/mutation_table.py --scope changed --base origin/main` at
65d37a7cb prints `3987 unpinned site(s) of 6309 candidate sites, 3990 at the ratchet base
343fb2a2c23dbb1a78142ce869be495187b8d481`; at 425972d27 (398daa3e5 merged with that base, before the pins)
it printed `MUTATION TABLE REFUSED -- 3993 unpinned site(s) against 3990 ..., 6 of them added by this diff`
(the null arm of the same command). `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`
at df2737ed4 prints `CI PREDICT: no closures or fast red predicted`.

Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh`
at 65d37a7cb prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out.` and `1 TEST SCRIPT(S) FAILED`: `tests/entities.py`,
`2 of 2425 ENTITY CHECKS FAILED` (`gate-sweep.yml: on CI's completion ...` and `graders-head-copy's delivery_status step ...`).
Both fail identically on `origin/main` 343fb2a2c in this seat's environment (`PYTHONPATH=tests/hastub python3 tests/entities.py`
there prints `3 of 2425 ENTITY CHECKS FAILED`, the same two plus `gate lease priority`), so they are the environment's, not this diff's;
CI is the judge. Every other script in the scope passed.

Golden: `GOLDEN_MODE=drift GOLDEN_REF=4a00a3f053c252b3bbf9f0e75ae36d27331f8ac3 PYTHONPATH=tests/hastub python3 tests/golden.py`
at f3ca049bf prints `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `no committed fixture is stale`.
Nothing is claimed, and both claim files are untouched.

Class census (step 8). Rule: `grep -n "_open_loop_plan_value(" custom_components/heatpump_optimizer/*.py`
lists each place a plan prediction stands in for an unsensed state. It returns the definition and two call sites:
`slab_temp_trajectory` (closed in this diff, via `_propagated_slab`) and `dhw_temp_trajectory`
(the tank seed in `_update_current_state`). The tank seed is a distinct case: it seeds only while
no tank reading exists, and no learner replays from it. It is left open here and listed under
Forward-carry.

## Architecture score

- `coord_footprint` 2463 -> 2465: `_propagated_slab` adds the orchestration statements that read the meter, call `draw_range.space_draw_kw` and replay through `_replay_interval`. The arithmetic itself is in `draw_range`, and moving the DHW block to `_track_dhw` paid for the rest.

## Unpinned sites

Every site the diff adds now carries a `killed_by` pin; `ci_predict.py` predicts no unpinned site at this head.

- `custom_components/heatpump_optimizer/coordinator.py:1008 CMP_BOUND*2` (`0.0 < dt_h <= HOUSE_LOSS_MAX_SAMPLE_HOURS`): value checks `a gap of exactly the sample window still advances the slab by the meter; a minute past it follows the plan` and `a zero or negative gap replays nothing; the slab follows the plan`; pinned `_propagated_slab.CMP_BOUND.28c622e7`. The lower bound encodes a design choice: a zero-length replay would return the prior slab, and the check prefers the plan's prediction, as for every other interval that measured nothing.
- `custom_components/heatpump_optimizer/coordinator.py:7657 GUARD_OFF` and `custom_components/heatpump_optimizer/coordinator.py:7668 RETURN_DEL` (the moved `_track_dhw` block): value check `a tank reading reaches the DHW learner, and its freeze reason the coordinator; no reading reaches neither`; pinned `HeatPumpOptimizerCoordinator._track_dhw.GUARD_OFF.ba409d06` and `.RETURN_DEL.1b8c73f7`.
- `custom_components/heatpump_optimizer/draw_range.py:295 CLAMP_DROP`: value check `a learned idle draw above the fixed floor raises it to IDLE_MARGIN times the idle draw`; pinned `running_kw.CLAMP_DROP.c0bdb768`.
- `custom_components/heatpump_optimizer/draw_range.py:296 CMP_BOUND`: value check `a draw at the running floor is standby, not heat`; pinned `running_kw.CMP_BOUND.5f36889b`.
- Earlier rounds: `draw_range.py` `running_kw`/`space_draw_kw`/`space_share` and `coordinator.py` `_propagated_slab.RETURN_DEL`, `_update_current_state` GUARD_OFF sites: pinned by `mutation-autofix` (398daa3e5, `ci: pin killed mutants`).

## Red checks

- `tests / mutation` (red at 398daa3e5): `MUTATION TABLE REFUSED -- 3993 unpinned site(s) against 3990`, 6 added by this diff. The previous body gave those six "pinned by `mutation-autofix` if killed", but no check drove them, so the autofix had nothing to pin. Answer: five checks that drive each site, and six pins measured locally (`## Mutation proof`). The cheaper detector exists: `tests/mutation_table.py --pin-killed --scripts tests/features.py`, run before the handoff, names every survivor. Standing cost: one features run per mutant, about 380 s each on a 4-core seat (about 20 min wall here for six mutants at `--jobs 4`).
- `pr-contract` (red at 398daa3e5): `## Red checks` named `mutation`, not `tests / mutation`. prepr's step 7 feeds the bare `mutation` to `policy_lint.mjs --pr-body`; CI feeds the check-run name, and the match is a substring test, so the local check passed a body CI refuses. This body names `tests / mutation`. There is no cheaper detector until prepr feeds CI's name; see `## Friction`.

## Forward-carry

- No-power-meter installs cannot tell a draw shortfall from UA. Harness `dev/audit/harnesses/r10_demand_overbook.py`, arm `nometer_half` (true scale 1.0, the pump delivers half of what is commanded, no power entity): the learned scale stays 1.858 and plan/deliv stays 1.908, identical at base 4a00a3f05 and head f3ca049bf. Against that, the metered arms move (owner_i01 1.221 -> 0.616, true 0.6; meter_half 2.041 -> 1.289). The ideal-delivery null arms stay on the truth at both ends (null 1.011 -> 0.98, true 1.0). So the residual is unobservability, not an unfixed bias. On such an install the health surface must report the learned heat-loss scale as unobservable, not as trustworthy. Carry: R10-UX-HEALTH (orchestrator ruling under mandate 6329234399).
- House learner gets zero evidence on a standby-drawing, under-delivering pump: owner_i03 accepted 0 samples at both ends, because `COP_TRACKING_ERROR_GATE` in `_interval_space_power` refuses every interval. Carry: R10-LEARNER-DEFAULT
- Optimality: on its own learned model, the plan books more kWh than the relaxed DP optimum at both ends (one window: base 6.95 against 5.38, head 5.27 against 3.75). Carry: R10-COP-PARTLOAD
- `dhw_temp_trajectory` open-loop tank seed (class census): Carry: R10-HEAT-METER

## Friction

- R10-PREPR-UNPINNED-RED: unenforced: `tools/pr/prepr.sh` `body_line` adds the bare red name `mutation` for step 6d's unpinned sites, while `pr-contract` passes the check-run name `tests / mutation`; `policy_lint.mjs` matches by substring, so a body naming only `mutation` passes prepr and is refused by CI (#2712 at 398daa3e5). Carry: R10-ORCH-MACHINERY

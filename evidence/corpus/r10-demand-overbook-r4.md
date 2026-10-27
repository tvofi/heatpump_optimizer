Part of #2499.

The unsensed slab (no floor-return sensor) was moved forward open-loop along the previous plan's
`slab_temp_trajectory`. That trajectory assumes the heat the plan COMMANDED was delivered. When a
pump drew less (setpoint-driven, capped or modulating down), the slab estimate kept heat that never
arrived. The house heat-loss learner then replayed the next interval from that too-warm slab, found
the room colder than it predicted, and booked the gap as fabric loss. `house_heat_loss_scale` climbed
and the plan booked more heat each day: the brief's over-booking.

The fix: where a power entity exists, `coordinator._propagated_slab` replays the elapsed interval
through `_replay_interval` at the metered space draw `draw_range.space_draw_kw`. `_replay_interval`
is the house learner's own replay: same model, and the flow-meter substitution where a heat meter
exists. Standby at or below `draw_range.running_kw`'s floor counts as no heat. These fall back to the
plan's trajectory, which is the old behaviour: a resistive element on the meter, no reading, no
previous sample, a zero or negative gap, or a gap past `HOUSE_LOSS_MAX_SAMPLE_HOURS`. No heat meter
is needed. **An install with no power entity at all is unchanged**: with no draw reading, the
delivery shortfall cannot be told apart from UA (see Null control and Forward-carry).

The fix sits on its own seam. The draw arithmetic (running floor, space share) goes in
`draw_range.py`, which owns the draw concept and has no HA import. The coordinator only orchestrates
(`_propagated_slab` is mapped `core` in `tests/seam_map.json`). Alternatives that lost:
(a) Reuse `_interval_space_power` for the slab. It returns `None` under `COP_TRACKING_ERROR_GATE`
exactly when the pump draws far less than commanded, so the slab would fall back to the commanded
trajectory in the very intervals that cause the bias. (b) Correct the learner instead, by skipping
samples after an under-delivery. That starves the learner and leaves the slab wrong for every other
reader. (c) Use a heat-meter-only path. The brief forbids it (every install, no heat meter).

To pay the budgets, the DHW tracking block in `_update_current_state` moved to `_track_dhw`
(seam `dhw`), and `_settle_interval_diag`'s inline space share now calls `draw_range.space_share`.

This round adds no production or test line. It merges the PR head (which carries the
`mutation-autofix` pins) with the previous handoff 65d37a7cb (which carries the five checks and six
pins that drive the sites `tests / mutation` refused), then merges `origin/main`.

## Head

1193fd2280fd01d6b91ef8164caeb44d889ee2e4, merge base c176ee55de7c658b0b870182c5dd55d0843ad8f7
(`origin/main` as this seat fetched it; c176ee55d was committed at 2026-10-24T21:57:48Z. By 2026-10-25T00:16Z `main` had moved to 5c0ee1093, whose delta
since c176ee55d touches only `tests/structure_budgets.json` among the production, test, ledger and
golden paths, and `git merge-tree` merges it clean). Every figure below was taken at this head and
this base.

CI's last run, the one that went red, was on a717ded9a5852254eba157da5a2330d74c876ae2 (`ci: pin killed
mutants`, github-actions). Its parent 5fb0a083b (`record: the delivery row for #2712`) is authored by
`tvofi`, not github-actions, so it is not an autofix commit. Both are merged into this head
(4edfc44a6 merges `origin/fix/r10-demand-overbook` at a717ded9a into the handoff 65d37a7cb). The one
conflict was `tests/mutation_ledger/killed_by/draw_range.py/running_kw.CMP_BOUND.5f36889b.json`, which
both sides pinned as killed. The handoff's `tests/features.py` pin was kept over the autofix's
`tests/entities.py` one, because the `#2499` check written for that site is in `tests/features.py`.
Rule: `git diff --stat 65d37a7cb 1193fd228 -- custom_components tests/features.py tests/mutation_ledger tests/golden`
prints nothing.

## Mutation proof

Run at 1193fd228 from detached worktrees, `PYTHONPATH=tests/hastub python3 tests/features.py`.
The unmutated head prints `ALL 4367 FEATURE CHECKS PASSED` (rc=0).

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

Both worktrees were discarded after the run.

The five mutants `tests / mutation` refused at a717ded9a, re-verified at 1193fd228 one ledger anchor at
a time:
`PYTHONPATH=tests/hastub python3 tests/mutation_table.py --anchor "<anchor>" --scripts tests/features.py --base origin/main --jobs 3`.

| anchor | sites | baseline | null control | verdict |
|---|---|---|---|---|
| `coordinator.py:_propagated_slab CMP_BOUND 28c622e7` | 2 (line 1008) | `tests/features.py: rc=0 failed=0` | `coordinator.py:510 NULL_COMMENT` survived | `PIN RE-VERIFICATION: 2 reproduced, 0 not reproduced` |
| `coordinator.py:HeatPumpOptimizerCoordinator._track_dhw GUARD_OFF ba409d06` | 1 (line 7657) | `rc=0 failed=0` | `coordinator.py:510 NULL_COMMENT` survived | `1 reproduced, 0 not reproduced` |
| `coordinator.py:HeatPumpOptimizerCoordinator._track_dhw RETURN_DEL 1b8c73f7` | 1 (line 7668) | `rc=0 failed=0` | `coordinator.py:510 NULL_COMMENT` survived | `1 reproduced, 0 not reproduced` |
| `draw_range.py:running_kw CLAMP_DROP c0bdb768` | 1 (line 295) | `rc=0 failed=0` | `draw_range.py:57 NULL_COMMENT` survived | `1 reproduced, 0 not reproduced` |

## Null control

- Mutation ratchet, null arm: the same command at a717ded9a (the PR head without the handoff's
  pins), `python3 tests/mutation_table.py --scope changed --base origin/main`, prints
  `MUTATION TABLE REFUSED -- 3992 unpinned site(s) against 3990 at the ratchet base fa4dad4a7..., 5 of them added by this diff`.
  It lists the same four `ADDED UNPINNED` lines CI printed (`coordinator.py:1008 CMP_BOUND*2`,
  `:7657 GUARD_OFF`, `:7668 RETURN_DEL`, `draw_range.py:295 CLAMP_DROP`). At 1193fd228 the same
  command prints `3987 unpinned site(s) of 6309 candidate sites, 3990 at the ratchet base c176ee55d...`
  and lists no `ADDED UNPINNED` line.
- Per-anchor nulls: each re-verification above drove a comment-only edit through `tests/features.py`
  and it survived. Each baseline was `rc=0 failed=0`.
- No power entity (`nometer_half` arm): the row is identical at both ends (scale 1.858, plan/deliv
  1.908, plan_kwh [15.7, 17.4, 20.2, 24.9, 27.2]). The meter is what moves the result, so the fix
  leaves a no-meter install alone. This is also the residual: the shortfall cannot be seen there.
- Ideal delivery (`null`, `true0.5`, `owner_ideal`): the learned scale stays on the truth at both
  ends. null 1.011 -> 0.98 against true 1.0; true0.5 0.511 -> 0.504 against 0.5; owner_ideal
  0.611 -> 0.611 against 0.6. With no shortfall, the fix has nothing to correct.
- Slab oracle (the `*_oracle` arms seed the TRUE slab): the rows are identical at both ends, by
  construction. They are the upper bound: owner_i01_oracle scale 0.619, plan/deliv 0.854.
- In-test nulls: `#2499: without a power meter the slab follows the plan (null control)`,
  `with no previous sample time the slab follows the plan` and
  `a zero or negative gap replays nothing; the slab follows the plan` pass at the head (in the
  `ALL 4367 FEATURE CHECKS PASSED` run).

## Figures

Harness `dev/audit/harnesses/r10_demand_overbook.py` (sha1 f0575c58b587d9a41e922fb5393e1a30a7ddba0b,
this head's copy, unchanged this round). Both ends ran the same copy, taken out of the tree to a
directory of its own:
`PYTHONPATH=tests/hastub:custom_components:tests python3 <copy>/r10_demand_overbook.py --dp`,
with the base end in a worktree at c176ee55d and the head end at 1193fd228. Wall clock was 4m01s at
the head and 4m08s at the base.

The run is synthetic: a 30-min closed loop with the real coordinator learners and the real
optimizer, no heat sensor, flat price unless `spread`, days 2..end. `scale` is the learned
`house_heat_loss_scale`. `plan/deliv` is the 12-h plan energy at 00:00 and 12:00, summed per day,
over the electric energy delivered. `samples` is the count of accepted house-learner samples.

| arm (true scale) | base scale | head scale | base plan/deliv | head plan/deliv | samples base/head |
|---|---|---|---|---|---|
| owner_i01 (0.6; 1.5-5 kW clamp, delivers min(3, 0.4c), 0.1 kW idle) | 1.221 | 0.616 | 1.674 | 0.854 | 323/350 |
| owner_i01_spread (0.6; same, price spread) | 1.584 | 0.733 | 1.847 | 0.666 | 399/391 |
| owner_i03 (0.6; 0.3 kW idle) | 1.0 | 1.0 | 1.642 | 1.084 | 0/0 |
| meter_half (1.0; delivers 0.5c) | 2.041 | 1.289 | 1.711 | 1.097 | 166/187 |
| meter_sat3 (1.0; caps at 3 kW) | 1.099 | 0.994 | 1.25 | 1.194 | 282/279 |
| slab3x (1.0; 3x slab mass) | 0.911 | 0.888 | 0.953 | 0.938 | 287/287 |
| nometer_half (1.0; no power entity) | 1.858 | 1.858 | 1.908 | 1.908 | 287/287 |
| owner_i01_oracle (0.6) | 0.619 | 0.619 | 0.854 | 0.854 | 346/346 |
| meter_half_oracle (1.0) | 1.051 | 1.051 | 1.016 | 1.016 | 201/201 |

The head reaches the slab-oracle bound on owner_i01 (0.616 against 0.619, plan/deliv 0.854 both).
meter_half still sits above its oracle (1.289 against 1.051). That gap is the share of bias this fix
does not remove.

DP reference (`--dp`, owner_i01's last 12-h window). This is a DP over a (room, slab) grid on the
optimizer's own objective, with cycling and capacity relaxed (`_dp_reference` docstring). It is run
on the learned model and on the true house:

- learned model: base plan_kwh 6.95 / DP 5.38 (gap 0.0665); head plan_kwh 5.27 / DP 3.75 (gap 0.158).
- true house from its true slab: base DP needs 1.5 kWh against plan 6.95 (gap 0.9027); head DP
  needs 3.75 against plan 5.27 (gap 0.1598).

This is one window, and the two ends start from different states. It is a reference, not an
optimality proof (see Forward-carry).

Architecture: `python3 tools/audit/archscore/score.py --diff c176ee55de7c658b0b870182c5dd55d0843ad8f7 HEAD`
at 1193fd228 prints `Architecture score: dS +0.3249 WORSENS (inadmissible: coord_footprint 2463->2465)`.
The rows are `duplication_copies 39 -> 38 +0.3261` and `coord_footprint 2463 -> 2465 -0.0012`; see
`## Architecture score`. `python3 tests/structure.py` at 1193fd228 prints `STRUCTURE RATCHET PASSED`.
Nothing is raised.

`PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at 1193fd228 prints
`CI PREDICT: no closures, fast, wave-script or instrument red predicted against c176ee55de7c`.

Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`
prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out.` The run,
`GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh`
at 1193fd228, prints the same mode line and `1 TEST SCRIPT(S) FAILED`, which is `tests/entities.py`
with `2 of 2425 ENTITY CHECKS FAILED`. The two failures are `gate-sweep.yml: on CI's completion ...`
and `graders-head-copy's delivery_status step ...`. The control is `PYTHONPATH=tests/hastub python3 tests/entities.py` in a worktree at the base
c176ee55d. It prints `3 of 2425 ENTITY CHECKS FAILED`: the same two, plus the timing check
`gate lease priority`. So the two fail on `main` in this seat's environment too, and they are not
this diff's; CI is the judge. Every other script in the
scope printed `ok`, `tests/stress.py` and `tests/features.py` included.

Golden: the same run's `env_drift.py --all c176ee55d...` prints
`NO UNCLAIMED DRIFT: 56 scenario(s) checked against c176ee55de7c658b0b870182c5dd55d0843ad8f7` and
`no committed fixture is stale`. Nothing is claimed. `git diff --quiet c176ee55de HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt`
exits 0, so both claim files are byte-identical to the base.

Class census (step 8). Rule: `grep -n "_open_loop_plan_value(" custom_components/heatpump_optimizer/*.py`
lists each place a plan prediction stands in for an unsensed state. At 1193fd228 it returns the
definition (`coordinator.py:1969`) and two call sites. `coordinator.py:1012` is
`slab_temp_trajectory`, the fallback inside `_propagated_slab`, closed in this diff.
`coordinator.py:6369` is `dhw_temp_trajectory`, the tank seed in `_update_current_state`. The tank
seed is a distinct case: it seeds only while no tank reading exists, and no learner replays from it.
It is left open here and listed under Forward-carry.

## Architecture score

- `coord_footprint` 2463 -> 2465: `_propagated_slab` adds the orchestration statements that read the meter, call `draw_range.space_draw_kw` and replay through `_replay_interval`. The arithmetic itself is in `draw_range`, and moving the DHW block to `_track_dhw` paid for the rest. The score prints this row as `inadmissible`, and the `arch-score / arch-score` check is green on it at a717ded9a.

## Unpinned sites

`ci_predict.py` predicts no unpinned site at 1193fd228, and the mutation ratchet lists no `ADDED UNPINNED` line there (`## Null control`). Every site the diff adds carries a `killed_by` pin:

- `custom_components/heatpump_optimizer/coordinator.py:1008 CMP_BOUND*2` (`0.0 < dt_h <= HOUSE_LOSS_MAX_SAMPLE_HOURS`): value checks `a gap of exactly the sample window still advances the slab by the meter; a minute past it follows the plan` and `a zero or negative gap replays nothing; the slab follows the plan`; pinned `_propagated_slab.CMP_BOUND.28c622e7`, re-verified above. The lower bound encodes a design choice: a zero-length replay would return the prior slab, and the check prefers the plan's prediction, as for every other interval that measured nothing.
- `custom_components/heatpump_optimizer/coordinator.py:7657 GUARD_OFF` and `custom_components/heatpump_optimizer/coordinator.py:7668 RETURN_DEL` (the moved `_track_dhw` block): value check `a tank reading reaches the DHW learner, and its freeze reason the coordinator; no reading reaches neither`; pinned `HeatPumpOptimizerCoordinator._track_dhw.GUARD_OFF.ba409d06` and `.RETURN_DEL.1b8c73f7`, re-verified above.
- `custom_components/heatpump_optimizer/draw_range.py:295 CLAMP_DROP`: value check `a learned idle draw above the fixed floor raises it to IDLE_MARGIN times the idle draw`; pinned `running_kw.CLAMP_DROP.c0bdb768`, re-verified above.
- `custom_components/heatpump_optimizer/draw_range.py:296 CMP_BOUND`: value check `a draw at the running floor is standby, not heat`; pinned `running_kw.CMP_BOUND.5f36889b` (kept as `tests/features.py`, `## Head`).
- `draw_range.py` `running_kw`/`space_draw_kw`/`space_share` and `coordinator.py` `_propagated_slab.RETURN_DEL`, `_update_current_state` GUARD_OFF sites: pinned by `mutation-autofix` (398daa3e5, `ci: pin killed mutants`), carried by the merge.

## Red checks

- `tests / mutation` (red at a717ded9a): `MUTATION TABLE REFUSED -- 3992 unpinned site(s) against 3990`, 5 added by this diff. The killing checks and their six pins were on the previous handoff 65d37a7cb, which the PR head did not carry: the head was built from the earlier handoff, then 5fb0a083b and the autofix commit a717ded9a. Answer: this head merges both, and the ratchet passes here (`## Null control`). The cheaper detector exists: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base c176ee55de7c658b0b870182c5dd55d0843ad8f7`, run at a717ded9a, prints the same four `PREDICT tests / mutation ADDED UNPINNED` lines, statically and in seconds. Its standing cost is nil, but it prints them as `a warning`, never a refusal, and it reads the head it is run in. Nothing compares the head a seat measured with the head that reaches the PR. The orchestrator's transfer step is the place for that comparison: `git merge-base --is-ancestor <handoff tip> <PR head>`, a one-line check.
- `pr-contract / pr-contract` (red at a717ded9a): `## Head` did not name a717ded9a, and `## Red checks` did not answer `tests / mutation` at that head. The cheaper detector exists: `tools/pr/prepr.sh --body-check` against the PR head. It is run against the local head, which is a different head here. This body names a717ded9a and 1193fd228, and answers both reds.
- `gate` (red at a717ded9a): it aggregates the two reds above and is answered by them.

## Forward-carry

- No-power-meter installs cannot tell a draw shortfall from UA. Harness `dev/audit/harnesses/r10_demand_overbook.py`, arm `nometer_half` (true scale 1.0, the pump delivers half of what is commanded, no power entity): the learned scale stays 1.858 and plan/deliv stays 1.908, identical at base c176ee55d and head 1193fd228. The metered arms move (owner_i01 1.221 -> 0.616, true 0.6; meter_half 2.041 -> 1.289). The ideal-delivery null arms stay on the truth at both ends (null 1.011 -> 0.98, true 1.0). So the residual is unobservability, not an unfixed bias. On such an install the health surface must report the learned heat-loss scale as unobservable, not as trustworthy. Carry: R10-UX-HEALTH (orchestrator ruling under mandate 6329234399).
- The house learner gets zero evidence on a standby-drawing, under-delivering pump: owner_i03 accepted 0 samples at both ends, because `COP_TRACKING_ERROR_GATE` in `_interval_space_power` refuses every interval. Carry: R10-LEARNER-DEFAULT
- Optimality: on its own learned model, the plan books more kWh than the relaxed DP optimum at both ends (one window: base 6.95 against 5.38, head 5.27 against 3.75). Carry: R10-COP-PARTLOAD
- `dhw_temp_trajectory` open-loop tank seed (class census): Carry: R10-HEAT-METER

## Friction

- R10-FIXER-DISPATCH-REF: contradiction: this seat's payload names the return refs `handoff/r10-demand-overbook-r4` and `handoff-body/r10-demand-overbook-r4` in its Output line, while the brief snapshotted under it says to push `handoff/r10-demand-overbook` and `handoff-body/r10-demand-overbook`. This seat pushed only the `-r4` refs, because the Output line names the return signal and forbids every other branch. Carry: R10-ORCH-MACHINERY
- R10-HARNESS-COPY-NAME: cost: copying `dev/audit/harnesses/r10_demand_overbook.py` out of the tree under the basename `harness.py` (to run one copy at both ends) breaks the harness with `ImportError: cannot import name 'FakeEntry' from 'harness'`. With `tests` on `PYTHONPATH`, the copy's own directory shadows `tests/harness.py`. One wasted run; the copy must keep its own basename. Carry: R10-ORCH-MACHINERY

Fix review: blocked 734ad21fa28847281236822e7a751f9c185d236c claim-drift: on Linux the claimed dhw_cold_tank and horizon_48h do not move (2 STALE) while away_setback and valve_storage_small_tank move unclaimed (2 UNCLAIMED), env_drift.py --all rc=1

bus-nonce: 5ef4149d49fa41ac0f78d25654c27816

## Block

This is fix-review round 2 for #2819, from the cloud reviewer seat, claim `rev-2819-5ef4149d`. I measured head `734ad21fa28847281236822e7a751f9c185d236c` from detached worktrees on Linux x86_64 (`/opt/hpo` CI venv, numpy 2.4.6, scipy 1.17.1). `git ls-remote` showed it was still `refs/pull/2819/head` when this verdict was written. The merge base with origin/main is now `dfcd8d9be` (origin/main itself). The fixer's base `da12aa37d` was measured as well.

1. **claim-drift (step 4).** I ran `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all dfcd8d9be1dab28cfe52f684764befd1e19291de` at the head. It exits rc=1 (`ev/env_drift_all.txt`):
   - The two claims `06eccb1a5` adds are `STALE claim for dhw_cold_tank` and `STALE claim for horizon_48h`. Both scenarios are byte-identical to the merge base on this box, and the tool prints the `RUNNER-CONDITIONAL CANDIDATE (#996 class)` decision tree for each.
   - The same classifier fix moves two other scenarios here, and neither is claimed:
     - `away_setback`: `space_reasons[40,44]` `cheap_price -> idle_coasting`, and `dhw_reasons[40,44]` `idle_other_channel -> idle_coasting` (4 leaves);
     - `valve_storage_small_tank`: `space_reasons[77]` `scheduled -> idle_coasting` (1 leaf).

   This is the drift D8-s1-01's classifier change predicts: sub-running space shares the plan calls off become idle. But on Linux it lands on different scenarios from the ones the macOS arm64 run claimed. The body says every round-2 figure was taken on macOS arm64, and that its `GOLDEN_MODE=drift` run was the claim's null control. That is the dev-box reading `env_drift.py`'s #996 text says the runner overrules. Brief item 5 asked whether the claims reproduce on Linux: they do not. The fix is to follow the tool's pre-agreed decision tree, with the CI runner as judge of record:
   - remove the two claims (or post the #996 instances);
   - claim `away_setback` and `valve_storage_small_tank` with their direction, if the runner shows the same moves;
   - re-run `env_drift.py --all` on Linux.

   `tests / fast (3.14)` was still in progress at write time, so CI has not yet confirmed or refuted this reading. If its `env_drift --all` comes back green on this head, this block is void and the class-open below stands alone.

2. **class-open (step 6), the second block.** Location: `pump_arbiter.py::step_duty`, and `optimizer.py::HeatPumpOptimizer.get_current_action` (`dhw_heating_active`).
   - **The claim.** The body says `optimizer.channel_heating_steps` is now the "one reader of 'does this channel heat at this step'", and that every seat answering that question from a raw draw reads the plan's running rule.
   - **The two seats that still answer it another way.** Both test each circuit's own draw against the pump's running floor, 0.1 kW:
     - `step_duty` uses `planned_draw_runs(space[i])` and `planned_draw_runs(dhw[i])`. This decides which duty the arbiter serves.
     - `get_current_action` uses `dhw_power > 0.1`. That flag feeds the DHW learner's `heating_active`, the climate attributes and the payload.
   - **Why the P2 rule misses them.** The rule spells only 0.05, so it cannot see either seat. `dhw_heating_active` is dispositioned only in the sibling `plan_running_rule` registry (D12-s2-01), as "the DHW circuit's own activity". That is the fact `channel_heating_steps` now owns.
   - **Reviewer probe** (`ev/drivers/channel_rules.py`, my own instrument, disclosed), output in `ev/probe_channel_rules.txt`. At the head, 3 of 6 straddling steps disagree:
     - (space 0.30, dhw 0.08): DHW is heating per `channel_heating_steps`, but `step_duty=space` and `dhw_heating_active=False`.
     - (0.08, 0.50): space is heating, but `step_duty=dhw`.
     - (0.08, 0.08): both channels are heating and the plan runs (0.16 > 0.1), but `step_duty=idle`.
   - **Solver output, not only synthetic steps.** `ev/drivers/golden_split.py` over the 40 committed golden plans that carry both channels finds 7 of 3864 steps (`ev/probe_golden_split.txt`): `cycling_cost` 60, `fuse_guard` 62, `shoulder_two_zone` 84-87 and `tariff_plus_two_zone` 68. Each has a space share of 0.055-0.099 kW beside a DHW draw of 0.6-2.8 kW. On these steps:
     - the space plan sensor says "heating now", and the slot merge counts the step;
     - the space circulation pump, which this PR moves onto `channel_heating_steps`, runs;
     - the arbiter serves duty `dhw` only.

     That is D8-s1-01's shape on the channel axis: a plan sensor heating, the actuating seat not.
   - **Not a regression.** Every one of these readings is the same at the base. But the body states the class closed, and neither seat is in the diff or dispositioned in the body.
   - **To unblock**, do either of these:
     - route `step_duty` and `dhw_heating_active` through `channel_heating_steps`, if the arbiter should serve what the plan views publish (a behaviour change that needs its own golden claim);
     - disposition both in the `channel_active_kw` registry and the body, with the reason the arbiter's per-circuit floor is a different fact, and widen the rule to reach them.

Round 2 delta (`41c7f46d2..9c9d12c82`): the round-1 block itself is closed. `_plan_slots` and the sensor fallback now read the running rule, and the finder's secondary metric falls on Linux (Evidence).

## Findings

- **Instrument reach (step 14).** `tests/entities.py::_p2_match_channel_line` needs a single-op Compare whose source mentions `power|space|_kw|kw|dhw`, or a default named `threshold|*_kw`. Planted into `topology.py` (`ev/p2_rule_null_controls.txt`), it catches the literal compare, the keyword default and a `line_kw` positional default, as the body claims. It misses three spellings:
  - a chained `0.0 < dhw_kw <= 0.05`;
  - a default named `line`;
  - an operand named `override`, or `draw` compared against a local line.

  One such spelling exists in production and neither registry sees it: `coordinator.py` system-identification override, `"heat_pump_on": override > 0.05`. That is the pump's on flag set from 0.05 rather than `planned_draw_runs` (0.1). So is `accuracy.py::AccuracyTracker.power_ratio`, `pred > 0.05`, a sibling of the dispositioned `delivered_ratio` floor. Both predate this diff. Carry: R10-ARCH-SHAPES
- **Round-1 carry still open (finite-float class).** `accuracy.py` `AccuracySample.from_dict.num` is still a nested float coercer with its own bool policy (`float(True)` reads 1.0). It is outside `_finite_float_coercers`' reach, and neither the diff nor the body routes it to `const.finite_float` or dispositions it. Carry: R10-ARCH-SHAPES
- **Round-1 carry still open (unpinned sites).** `## Unpinned sites` still dispositions all 71 sites as "pinned by mutation-autofix". `ci-autofix.md`'s `mutation-autofix` pins killed mutants only, and survivor triage is never automated. `tests / mutation-autofix` was in progress at write time. Survivors among the 71, once its commit lands, owe the `## Red checks` `mutation` line their own answer. Carry: R10-ARCH-SHAPES
- **Body text.** The "Architect note amendment" calls the two round-2 `coordinator.py` hunks "(float coercion only)". They are running-rule plumbing, not float coercion (Evidence). Carry: R10-ARCH-SHAPES

## Evidence

- **Finder harness**, `dev/audit/rounds/round10/D8/s1/f1_active_now.py` (sha1 `766cc95a3b886f3f70d122a167028d2313d78048`, identical at every end), on Linux with `PYTHONPATH=tests/hastub:custom_components` (`ev/f1_*.txt`):

  | end | heating_now_while_off | slot_steps_declared_off |
  |---|---|---|
  | `da12aa37d` | 2 | 5 |
  | `6feac7ece` | 0 | 5 |
  | `dfcd8d9be` (main) | 2 | 5 |
  | head | 0 | 0 |

  - `snapshots=36` and `steps=192` at every end.
  - `--perturb`: `heating_now_while_off=0` at every end, and `slot_steps_declared_off` 5/5/5/0 (untouched by design). The harness moves under its own perturbation.
  - macOS figures (the body): base 1 and 0. Linux figures: base 2 and 5. The harness header says the counts are exact per machine/BLAS. On Linux the slot arm does measure, and it falls 5 -> 0 at this head. The round-2 class claim for the three named seams holds here.
- **Companion**, `dev/audit/harnesses/r10_channel_running_rule.py` (`ev/companion.txt`): `da12aa37d` reads 5/5/2 (`'2 heating periods'`), `6feac7ece` reads 5/5/2, and the head reads 0/0/0 (`sensor_state=None`). `--perturb` reads 0/0/0 at every end, with `perturbed=1`. This matches the body exactly.
- **Rule reach**, `dev/audit/harnesses/r10_channel_line_reach.py head <tree>`: 16 at `da12aa37d`, 15 at `6feac7ece`, 16 at main and 10 at the head. The site lists match the body's dispositions.
- **Mutation proof**, re-run by me in copies of the head worktree with `tests/features.py` (`ev/mutants_features.txt`, `ev/feat_*.txt`). The control prints `ALL 4409 FEATURE CHECKS PASSED`, rc=0. Each mutant fails exactly the check the body names, `1 of 4409`:
  - `_plan_slots` heating to `[p > 0.05 ...]`;
  - `_async_drive_pumps` schedule to `[p > 0.05 ...]`;
  - `classify_space_steps` `_heating_draws` line deleted;
  - `wood_fuel_from_parts` runs to `[p > 0.05 ...]`.

  All four are killed. I did not re-run the `tests/entities.py` sensor and instrument mutants.
- **Coordinator hunks (brief item 2).** `git diff 6feac7ece 9c9d12c82 -- coordinator.py` has five hunks, and none is outside the named set:
  - the `CHANNEL_ACTIVE_KW` import removal;
  - `_async_drive_pumps`: `schedule = channel_heating_steps(result.power_schedule, result.dhw_power_schedule)`, where `plan_commands_heat` now takes bools;
  - `_plan_slots`: threshold parameter removed, two masks added, `shared_kwh` now gated on `other_heating`;
  - the slot loop on `heating`;
  - the simulator's two `other_powers=` arguments.

  The behaviour change is the intended one: the space pump and slots skip steps the plan does not run.
- **coord_footprint (ruling 2).** `tools/audit/archscore/score.py --diff da12aa37d HEAD` at the head gives `Architecture score: dS +1.8325 IMPROVES`, with:
  - duplication_copies 38 -> 35;
  - coord_footprint 2446 -> 2437;
  - params_over_10 7 -> 6;
  - layer_violations 17 -> 13;
  - private_cross_module 12 -> 10.

  `--diff dfcd8d9be HEAD` gives the same. `tests/structure.py` prints `STRUCTURE RATCHET PASSED` (`ev/structure_archscore.txt`). The merge-base figures are confirmed. Per the ruling, I did not block on the +1.
- **Claims file (brief item 4).** Three-dot diff against `dfcd8d9be`: only the two added lines (`ev/claim_diff.txt`). `claims-for: 7.0.4` equals `VERSION` 7.0.4, and each line states its direction. Neither scenario is in the may-drift lists `env_drift.py` printed. The Linux reproduction is under Block.
- **Release stamps.** `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (empty three-dot diff).
- **Merge.** `git merge-tree --write-tree origin/main 734ad21fa` exits rc=0 with tree `8f9013700` and no conflict (`ev/merge_tree.txt`).
- **CI on this head** (check-runs API, 48 runs):
  - Green: arch-score, typing, replay, browser, briefs, env-matrix, instrument-self-tests, policy-docs, budget-raise-gate, closure-scope, hassfest, validate-hacs, wave-script, nightly-status, and mutation-pins 1-12.
  - Red:
    - `tests / mutation` is the predicted unpinned-sites red. The body names it and answers it by `ci_predict.py` (`ci-autofix.md`).
    - `governance / delivery-status` is OVERDUE on #2762 and #2795 only. The log says "This check is NOT a required context and a red here blocks no merge", and this diff's row does not reach the overdue rows, so it is not this PR's.
  - Still running: `tests / fast`, closures, coverage, mutation-autofix and codeql-python. So step 11 is not concluded for them.
- **Head SHA in the body.** The body's `## Head` names `734ad21fa`, the head I measured.

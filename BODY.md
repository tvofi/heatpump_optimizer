Part 1 of outside pull request #3435 (Bankaifan), the counter-span fix: a heat-counter span no longer throws itself away when a cycle inside it ran hot water, under three conditions (the counter is declared to see hot water, the mode dwell observed the charge, no immersion element or pump backup heater on). The charge is removed from the span by its own counter steps, each split by that cycle's dwell (`SpanEnergy.dhw_kwh`), not by a time share of the span. Adopted from the author's commit f47199b6 with its authorship kept (commit 8827be07); parts 2 (boost settle tail) and 3 (refusal reasons and the card) are not in this diff (see `## Forward-carry`).

Design, and alternatives that lost: the author passed a `bridged` bool computed in `coordinator._replay_gate`. That added three computed statements to the coordinator (`coord_footprint` 2497 -> 2500, the arch-score gate inadmissible). In this diff `heat_energy.replay_gate` takes the meter, the plan split, `sees_dhw` and `heater_on`, and calls `HeatEnergyMeter.bridges_hot_water` itself. The coordinator only passes inputs. Paying `class_excess_loc` by folding `_observe_heat_energy`'s locals into the call also lost: it made the call's arguments computed, which `coord_footprint` counts, so 4ef82525 restores it. The one added coordinator line is paid in `_replay_gate`'s docstring, whose list of the gate's inputs repeated `heat_energy.replay_gate`'s. `mutation_table.py --pin-killed` left three survivors on the author's lines. Two were guards no input reaches, so the diff deletes them: the reset of the hot-water total when the first read opens a span (the total is reset at every close and only grows while a span is open), and `total <= 0.0` (dwell shares are only returned over an observed window of positive length). The third, the `rest >= 0.0` boundary, is pinned by a value check: a span whose heat all went to hot water reads 0 kW of space heat. The diff staled three `killed_by` entries (`replay_gate` BOOLOP and RETURN_DEL 087a1e6c, `span_heat` RETURN_DEL a578b06f); they are deleted by hand, and the edited lines are pinned afresh by the pin run.

## Head

da2eef8acd4d175dac1ffbfe6e8423a205d6b513, on origin/main cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf (merge base 6f0ff9d81415bcfee6019327d12d4ded00ae30e4), measured 2026-11-11T10:16Z.

## Mutation proof

Run with `tools/audit/seat/mutant_run.py --in-place --spec <spec> --cmd "python3 tools/audit/seat/features_block.py --prelude 'exec(open(\"<prel.py>\").read())' 'R10-HEAT-METER: a delivered-heat counter' '# The earned basis. A thermal-power install'"` at da2eef8acd4d175dac1ffbfe6e8423a205d6b513, under `PYTHONPATH=tests/hastub`. The block is the R10-HEAT-METER section of `tests/features.py`, through this diff's checks. The prelude execs the module-level definitions that the block reads from earlier in `features.py` (the `_t2_house` family, `NOW`, `_fb_const`, `replace` and the `_fm`/`_tp` harness names). `--through` was not used: at the head it fails one unrelated check (D1-s2-55, a worker job that cannot pickle a class defined under `features_block`), so its NULL is killed. Each mutant is `{name, file, old -> new}`:

- M1-replay-gate-ignores-bridge, heat_energy.py: `carried = interval is not None or meter.bridges_hot_water(plan_split, sees_dhw, heater_on)` -> `carried = interval is not None`
- M2-bridge-ignores-heater: in `bridges_hot_water`, drop `not heater_on and`
- M3-bridge-ignores-sees-dhw: drop `sees_dhw and`
- M4-bridge-ignores-dwell: drop `and ran_hot_water(self.attribution(plan_split))`
- M5-bridge-ignores-counter: drop `self.counter and`
- M6-span-heat-time-split: `if space_kw is not None and ev.attribution.observed and ev.attribution.dhw > 0.0:` -> `if False:`
- M7-negative-rest-kept: drop `and rest >= 0.0`
- M8-unaccounted-as-zero: `rest = None if e.dhw_kwh is None else e.heat_kwh - e.dhw_kwh` -> `rest = e.heat_kwh - (e.dhw_kwh or 0.0)`
- M9-step-space-share: `* shares[1] / (shares[0] + shares[1])` -> `* shares[0] / (shares[0] + shares[1])`
- M10-no-step-fold: delete `self._fold_dhw_step(heat_kwh, at, start is not None)`
- M11-coordinator-immersion-ignored: `coord._immersion_active or coord._pump_signals.electric_heat.resistive_heat)` -> `coord._pump_signals.electric_heat.resistive_heat)`
- M12-coordinator-pump-heater-ignored: the same -> `coord._immersion_active)`
- M13-coordinator-sees-dhw-forced: `probe_install(cfg).heat_sees_dhw,` -> `True,`
- M14-all-hot-water-refused: `rest is not None and rest >= 0.0` -> `rest is not None and rest > 0.0`

```
SURVIVED NULL
KILLED M1-replay-gate-ignores-bridge
KILLED M2-bridge-ignores-heater
KILLED M3-bridge-ignores-sees-dhw
KILLED M4-bridge-ignores-dwell
KILLED M5-bridge-ignores-counter
KILLED M6-span-heat-time-split
KILLED M7-negative-rest-kept
KILLED M8-unaccounted-as-zero
KILLED M9-step-space-share
KILLED M10-no-step-fold
KILLED M11-coordinator-immersion-ignored
KILLED M12-coordinator-pump-heater-ignored
KILLED M13-coordinator-sees-dhw-forced
KILLED M14-all-hot-water-refused
```

## Null control

- The unmodified tree: at the merge base, with this branch's `tests/features.py`, the same block prints `FAIL a counter span carries a hot-water cycle ... [(False, False, False, False, False, False)]` and then raises `AttributeError: 'SpanEnergy' object has no attribute 'dhw_kwh'`. At the head the first arm (counter sees hot water, dwell saw it, no heater) reads True and the other five still read False.
- A span with no hot-water charge learns as before: `dhw_kwh == 0.0`, `space_kw == heat_kw` (check "null control: a span with no charge ..."). The step split only replaces the time split when `attribution.observed and attribution.dhw > 0.0`. At main every such span was already unclean for both fabric learners.
- Both ends of the input range: a fresh meter (no counter, no dwell, zero evidence) bridges nothing. A span with more hot water than heat, or with a step in an unobserved cycle, reads no space figure, not a clamp or a guess (check "a span with more hot water than heat ...").
- Mutant NULL survived (above).

## Figures

- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED`. Every script in `$D/scope.run` was run at da2eef8acd4d175dac1ffbfe6e8423a205d6b513 under `PYTHONPATH=tests/hastub GOLDEN_MODE=drift`, `tests/features.py` included, and each exited 0.
- Pins: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base $(git merge-base origin/main HEAD) --jobs 3`. The second run, at the parent of the pin commit, printed `PIN KILLED: 4 pinned, 0 left unpinned`; the first had pinned 10 and left the 3 survivors named above.
- Goldens: `PYTHONPATH=tests/hastub GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) python3 tests/golden.py` prints `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 6f0ff9d81415bcfee6019327d12d4ded00ae30e4`. The same run with `GOLDEN_REF` unset compares against the current origin/main tip and lists six coordinator-payload fixtures that main moved after the merge base (two-dot), not this diff. Neither claim file is touched.
- `python3 tests/structure.py` rc 0 at da2eef8acd4d175dac1ffbfe6e8423a205d6b513. `class_excess_loc` is at its budget: the added `_replay_gate` line is paid by a docstring line.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` prints `Architecture score: dS +0.0000 NULL`. At 8827be07 (the author's wiring) it printed `WORSENS (inadmissible: coord_footprint 2497->2500)`.
- Seam census (step 8), rule `git grep -n -E "ran_hot_water\(|space_heat_kw\(|replay_gate\(|bridges_hot_water\(" -- custom_components`. The class is a hot-water cycle that spoils or misreads a counter-integrated reading:
  - `heat_energy.span_heat` (space_heat_kw on a span): closed in this diff.
  - `coordinator._replay_gate` and its two callers (house heat loss, lower floor): closed. Both reach the bridge.
  - `coordinator._interval_space_power` (`ran_hot_water` refuses the per-cycle interval): rightly left alone. A per-cycle point replay has no counter step to subtract; the span carries the cycle instead.
  - `coordinator._record_accuracy` (`ran_hot_water` gates the draw fold): out of class. It pairs a point draw with one interval, not a counter span.
  - `coordinator.py` `space_heat_kw(... integrated=False)` on the flow-bias heat: out of class. It is a point reading under the whole-unit rule.

## Red checks

none

## Forward-carry

- Carry 1: Part 2 of outside pull request 3435, the boost settle tail scaled on the time the boost ran and persisted across a restart (boost.py, store.py, const.py and the mode change in coordinator.py), is not in this diff. It is its own roster group by feature triage ruling P613, cut from the author's commit f47199b6 with the authorship kept. Carry: R10-OUTSIDE-LEARNER-ROBUSTNESS-P2
- Carry 2: Part 3 of outside pull request 3435, the refusal reasons at DEBUG and the frozen learner phase with the card in three languages (heat_energy.py, learner_progress.py, payload.py, the card script, tests/card.mjs), is not in this diff. It is its own roster group by feature triage ruling P613, built after part 2 from the same commit. Carry: R10-OUTSIDE-LEARNER-ROBUSTNESS-P3

## Friction

- mutation-proof: cost: `features_block.py --through` cannot be a mutant command for any block past D1-s2-55. That check fails under the block runner (a worker job pickles a class defined in the `features_block` module), so the NULL is killed. This proof used a block with an exec prelude of the earlier definitions instead. Carry: dismissed: a fixer-side workaround exists and is stated above; no later stage depends on --through

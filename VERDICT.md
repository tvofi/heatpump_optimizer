Fix review: blocked 8b127c6d85443c13558417f981237f2596fdcfc1 class-open: axis the hot-water windows in force at an instant unenumerated (e.g. dhw_planner.DhwPlanner next_window_in_hours)

bus-nonce: b62336c7fe8ec4f2e5bcee1fb7f85aaf

Round 1 (no earlier verdict on this PR or probe ref).

## Block

The claim (D17-s3-51 / P2 `dhw_window_in_force`): `dhw_schedule.windows_in_force` owns the hot-water windows in force at an instant, and the published next-window hours read the day's windows. The P2 rule only matches `Attribute` loads of `.dhw_windows`/`.dhw_demand_windows`. So a reader that gets the flat set through a dispositioned site's return value is outside both the rule and every residue category the body states.

That set has an unenumerated member. `dhw_planner.py:1107` takes `windows, learned_windows = self._effective_dhw_windows()`, the flat every-day set. The P2 entry dispositions it as "the fallback set the planner's per-step windows_for_day chain (_dhw_windows_at) resolves". `dhw_planner.py:966-990` does resolve it per step for `in_window`. But `dhw_planner.py:1351` passes the unresolved flat set to `hours_until_next_window(float(hours_mod[0]), windows)`. That value becomes `DhwPlan.next_window_in_hours`, published as `predictive_info["dhw_next_window_in_hours"]` (`optimizer.py:6037`) and exposed by `PredictiveInsightSensor` (`sensor.py:1436`). It also sits beside a `dhw_in_demand_window` that comes from the day-aware `in_window[0]`.

Measured with the reviewer's probe (`ev/probe_planner_next_window.py.txt`), which runs the planner's `_build_dhw_requirements` on "weekdays 06:00-08:30, weekend 08:00-09:30":
- At the head: Saturday 07:00 gives planner `next_window_in_hours` = 0.0. The day's answer is 1.0: `windows_in_force` = [(8.0, 9.5)], against the flat [(6.0, 9.5)], and the coordinator's `_dhw_next_window_in_hours` now gives 1.0. Saturday 05:00 gives 1.0, which is the flat start; the day's answer is 3.0.
- Controls: Monday 07:00 gives 0.0 and the flat spec at Saturday 07:00 gives 0.0, both correct. The same planner numbers at the merge base `f269ecccb5` (`ev/probe_planner_next_window.base.txt`) show the seam existed before the change and the head leaves it unchanged.

The repair is the fixer's: resolve the planner's next window per day (as `in_window` does), or narrow the claim and the disposition to say this reader is excluded. Either way, add a P2 or census check that reads the consumers of `_effective_dhw_windows()`. The finder harness `dhw_window_weekday.py` reads only the coordinator path, which is why `cells_wrong` 18 -> 0 does not see this.

## Findings

none

## Evidence

- Merge: `git merge-tree --write-tree origin/main 8b127c6d85` exits 0 (`ev/merge-tree.txt`). VERSION, the manifest and RELEASE_NOTES.md are untouched, and `tests/golden/` has no diff at the three-dot range, so neither claim file is touched.
- Role files: `git diff <mb>...origin/main -- dev/governance/roles/` changes wording in fix-review.md and fixer.md and adds the axis rule. The ADDENDUM already carries the axis rule, and I applied main's text.
- Mutation proof: 13 targeted mutants over the D17-s3-51, D14-s1-01, D15-s3-01 and D10-s1-02 sites, all killed on the body's named checks (`ev/mutants.txt`). I did not re-run the `tests/entities.py` mutants myself because the script runs past 30 min. I cite CI's `mutation-autofix` pins at this head instead (e.g. `entity.py:PayloadFlagMixin.available BOOLOP 2b124388`, killed by tests/harness_headers.py).
- Finder harnesses at the merge base f269ecccb5 and at this head (`ev/harness/`; the btn_actions.py copy is from the dbdc1d95fef3 export, as the body says). Its sha1 1b1387bb38dd matches the body, and the in-tree copies match their sha1s:
  - `silent_refusals` 2 -> 0, null `controls_raised` 2 -> 2
  - `delta_bare` 3 -> 0, null `impossible_pairs` 0 -> 0
  - `avail_none_cycles` 0 -> 0 (flat at both ends, as the body says)
  - `fam_runs_excess_entity_id_sensor` 2 -> 0, the other platforms 0 -> 0, `fam_runs_excess_name_<en|sv|de>` 0 at the head
  - `state_class_impossible` 0 -> 0
  - `seams_services` 12 -> 0, `seams_widen` 28 -> 0, null `seams_options` 0 -> 0
  - `cells_wrong` 18 -> 0, null `null_cells_wrong` 0 -> 0
  - My base is the current merge base, not the body's a8efe1d1. These numbers match the body's.
- Not re-derived here: the D15-s3-01 synthetic-bundle figures, `Architecture score: dS +3.6150`, and the structure re-records. They are left to CI's arch-score and structure runs.
- The body's `## Head` names c6cb6d936f, not this head. `tools/audit/seat/review_carry.py c6cb6d936f 8b127c6d85` prints `CARRY` (`ev/review_carry.txt`): the two later commits are `ci: re-record closures` and `ci: pin killed mutants`. This is paperwork for the re-cut, not a block.
- CI at this head: I re-ran `merge_train.py classify 8b127c6d85 --pr 3841` until 07:14:54 UTC and every run printed `WAIT ... pending: gate red: none` (`ev/classify.log`). I stopped waiting once the review reached a block, which does not depend on CI.

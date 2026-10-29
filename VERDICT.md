Fix review: merge 5b9dd9b2a4fa1ae079864cff9d31115524328834

bus-nonce: 65554aa411cc4c77b910b891ba4a642d

## Round

Round 2: one earlier review, `verdict/2919`, blocked at `2d151b5c8` as mutation-vacuous on the sysid stand-down.

## Verdict

The round-1 mutant is now killed. Deleting `) or learner_room_unread(getattr(ctx, "_config", None))` from `_run_system_identification` turns exactly one check red: "#2508: a sysid night whose config has no indoor entity aborts as not_configured:indoor_temp_entity and records nothing". The red output is `{'entered_step': True, 'recorded': 1, 'phase': 'step', 'reason': ''}`, which matches the body. The two seams the round-1 review left open (`_record_accuracy` and `_track_curve_comfort`) are guarded, and each guard is pinned by a mutant I ran. The class rule returns no unguarded seam. The branch merges cleanly. The only red check is the predicted, answered `tests / mutation` unpinned-site refusal.

## Findings

none

## Evidence

- Head measured: `5b9dd9b2a4fa1ae079864cff9d31115524328834` (`ev/HEAD.txt`). The PR's `head.sha` was still this SHA at 02:18 UTC. Merge base and origin/main are both `0265f524e9d4810ee179a58d7f5471151ba1cd22`.
- `dev/governance/roles/` has no diff between the merge base and origin/main, so this contract is current.
- Unmutated head: `ALL 4543 FEATURE CHECKS PASSED`, rc 0 (`ev/features-head.log`). Run as `PYTHONPATH=tests/hastub python tests/features.py` with `/opt/hpo/venv-ci` (Python 3.14.7). The body's 4543 is re-derived.
- Mutation proof (step 1). Each mutant ran in its own `git worktree add --detach` at the head; the diffs are `ev/mutant_*.diff` and the logs `ev/features-mutant_*.log`, summarised in `ev/mutants-summary.txt`:
  - RESULT sysid (the stand-down clause removed): `1 of 4543` failed, check S. Killed. This was round 1's surviving mutant.
  - RESULT acc (`actual_now` reads the room unconditionally): `1 of 4543`, check A, no-indoor arm `{'lead_scored': True, 'sample_room': [21.0], 'curve_worst': None}`. Killed.
  - RESULT sample (`actual_temp=ctx._current_state.room_temperature`): `1 of 4543`, check A, `{'lead_scored': False, 'sample_room': [21.0], 'curve_worst': None}`. Killed.
  - RESULT curve (the `learner_room_unread` disjunct dropped from `_track_curve_comfort`): `1 of 4543`, check A, `{'lead_scored': False, 'sample_room': [None], 'curve_worst': 2.5}`. Killed. This covers the lane's `coordinator.py:9044 GUARD_OFF` site.
  - RESULT rawonly (`raw = self._learning_frozen(...)` only): `2 of 4543`, checks 1 and 2 (`span clean {'no_indoor': True, 'indoor': True}`). Killed.
  - RESULT mguard (`if margin is None: return` deleted): `1 of 4543`, check N, `TypeError("'<=' not supported between instances of 'NoneType' and 'float'")`. Killed. This covers the lane's `coordinator.py:9060 GUARD_OFF` site.
  - Each count and red output matches the body's `## Mutation proof` table. In every A run the configured arm, `{'lead_scored': True, 'sample_room': [21.0], 'curve_worst': 2.5}`, stayed as the null control (step 3).
  - I did not re-run the body's `boolop`, `retdel`, `none`, `postgate` and `guard` mutants. Those rows are the fixer's figures, not mine.
- Class rule (step 6). I ran the body's `seams_2508.py` verbatim at both ends (`ev/class-seams.txt`). At the head it returns seven functions. The four that read the room all consult `learner_room_unread`. The other three, `_async_learn_lower_floor_loss`, `_inputs_unhealthy` and `_record_quiet_comfort_period`, have `reads_room=False` and are dispositioned in the body. At `2d151b5c8` the same rule shows `_track_curve_comfort` and `_record_accuracy` at `consults_learner_room_unread=False`, which is the open class the round-1 review found. The rule's stated limit is a reader that never consults `_learning_frozen`. The body records the planner as that reader, outside the group's scope (payment 5).
- Merge (step 13): `git merge-tree --write-tree origin/main 5b9dd9b2a` exit 0, tree `6ad3d5a1f` (`ev/merge-and-version.txt`). The claim files are untouched, so the driver was not invoked.
- Step 5: `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched in the three-dot diff (`ev/merge-and-version.txt`).
- Step 4: `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are untouched, and every golden scenario configures an indoor entity. I did not run `env_drift.py --all`. The no-drift figure is the body's scoped-gate run and CI's green `governance / env-matrix` and `tests / replay`.
- Structure (step 14): `python tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED` (`ev/structure.txt`). Two budgets are lowered (`class_excess_loc` 17991->17986, `max_class_loc` 8160->8155) and none is raised. The decrease comes from moving the coldest-zone margin computation out of the coordinator into `curve_learning.worst_zone_margin_k`, and the `retdel` and `W` checks pin that function. I did not re-derive the body's intermediate figures at `3016b33bd` and `d01656dad`.
- Architecture score: `score.py --diff 0265f524e HEAD` prints `dS -0.0006 WORSENS (inadmissible: coord_footprint 2408->2409)`, the same line the body quotes against `b6f6ceca4`. Against `b6f6ceca4` at today's tree the command prints `dS +2.3477`, because main's own `duplication_copies` 35->29 falls inside that two-dot range (`ev/archscore.txt`). The +1 statement is the `raw = learner_room_unread(...) or self._learning_frozen(...)` assignment. I judged the five payments the body lists and found no payment it missed: a coordinator helper costs more footprint, and the gate itself is shared with the lower-floor learner, which must keep learning. The `arch-score / arch-score` check concluded success at this head.
- CI at this head (step 11), read from the commit's check-runs API (`ev/check-runs-final.txt`, 02:18 UTC). Every gate check concluded success, including `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `tests / replay`, `tests / typing`, `governance / instrument-self-tests` and `codeql / Analyze (python)`. The one exception is `tests / mutation` (job 123210195608), which concluded failure with `MUTATION TABLE REFUSED -- 3729 unpinned site(s) against 3728 ... 4 of them added by this diff` (`ev/mutation-lane.txt`).
  - The four sites it lists are exactly the four the body names under `## Unpinned sites` and answers under `## Red checks`, as `ci_predict.py`'s prediction pinned by the mutation-autofix bot (`ci-autofix.md`). The two coordinator sites are killed by my `curve` and `mguard` mutants above.
  - `tests / mutation-pins (1)` was still in progress at the read. Its pin commit is a bot move of the head, within `orchestrator.md` section 11's carry predicate.
  - A duplicate `prelude` run was also still in progress; its sibling run concluded success.
  - No `pr-contract` run appears in this commit's check-runs listing, so I did not verify its body check at this head.
- Step 10: the body's `## Forward-carry` is `none`, and the round-1 `Carry: R10-LEARNER-DEFAULT` is discharged in this diff by the two guards above.
- Step 9: there is no committed finder's harness. The class rule is a body-quoted script (scratch, not in the tree), and I re-ran it as written. The feature checks are the fixer's.

Fix review: blocked 6ade1643e20a9518e7600703c348abe46feba4a1 mutation-vacuous: coordinator.py _solve_record approach= input forced None survives the block and the whole tests/features.py

bus-nonce: a5a48a0b5d9b4c656c204a9013bd8f8d

## Block

The diff adds one production line that carries the learned approach into the plan: `coordinator.py:6313`, in `_solve_record`, `approach=draw_range.solve_approach(self._accuracy.draw, params, solve_now.timestamp())`. `optimizer.py:4654` reads it as `self._approach = inputs.approach`. No other production road takes the learned profile to `runs.received` in the true objective (`optimizer.py:351`), to the entry energy in `runs.commit` (`optimizer.py:554`) or to the published trajectory.

This round's delta re-resolved exactly this line. `8f63a92211` had a content conflict at `coordinator.py:6309-6317`, between main's `compressor_running=running` and this branch's `compressor_running=duty_switch.running_now(...)` plus `approach=...`. The resolution is correct at this head: it keeps main's walrus `running` and this branch's `approach=` (`ev/delta_coordinator.diff`, `ev/coordinator_6306_6316.txt`). But nothing in the tree would have refused a resolution that took main's side and dropped the `approach=` line. That is the non-obvious risk CI would not detect, so fix-review.md step 12 widens the scope to this one line.

Measured, with one hand mutant at the head: the line replaced by `approach=None`, and nothing else changed (`git diff --stat` shows 1 line):
- The PR's block, `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "exec(open(P).read())" "R11-OUTSIDE-START-APPROACH: a run's"`, reads `ALL 23 FEATURES BLOCK PASSED` (`ev/mut_MC.txt`).
- The whole script, `PYTHONPATH=tests/hastub python3 tests/features.py`, reads `ALL 6365 FEATURE CHECKS PASSED`, rc 0 (`ev/mut_MC_whole_features.log`).
- No other script under `tests/` names `solve_approach`, `inputs.approach` or `_approach`. The only other file that does is the synthetic harness `dev/audit/harnesses/r11_honest_starts_runs.py`, which does not build the coordinator.
- CI's `tests / mutation` draws no mutant of this kind on a keyword-argument line, and the body's 93-site list does not include it. CI's green would not show the survivor either.

With the mutant in place, every install plans and costs as if no approach had been learned, and the whole suite stays green. The feature's headline effect, the approach "learned and priced", is therefore unpinned at its only production entry. The body's mutation table covers the optimizer and runs side through a hand-set `opt._approach`, and the coordinator meter side (case 7), but not this wiring.

Repair, for the fixer to choose: add a coordinator check that drives `_solve_record` (or the solve path above it) with a learned `DrawRange.approach`, and asserts that `SolveInputs.approach` is the profile `solve_approach` returns. Its null arm is a draw with no evidence, which gives `None`. The check must fail under this mutant. The scratch solve at `coordinator.py:11240` has the same shape and was not driven here.

## Findings

- Note: figure: the body's `## Figures` says the block "rerun at the head, passes 19". At this head the same command reads `ALL 23 FEATURES BLOCK PASSED` (`ev/block_head.txt`). The four extra checks came in with the merged handoff commits. Carry: dismissed: paperwork, the fixer updates the body with the repair above

## Evidence

- Head measured: 6ade1643e20a9518e7600703c348abe46feba4a1 (`ev/HEAD.txt`). Round: second review, a later round over 46cdd1f9191180fc1f420a0d5eedd0f758b947ad. Scope: delta per the packet's `## Review scope` (`ev/review-packet.md`), widened only to `coordinator.py:6313` as stated under `## Block`. Roles drift `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty. Carry: dismissed: evidence, not a finding
- Merge with main: `git merge-tree --write-tree origin/main 6ade1643e2` exits 0 (`ev/merge_tree.txt`), with origin/main at cb2026c3b5, the head's own merge base. Carry: dismissed: evidence, not a finding
- Delta: one merge, `6ade1643e2` of `89f93f8f71`. That merge carries main `cb2026c3b5`, #3805's head `0a0dba2c18`, and handoff `95c0bc2719`. To isolate the fixer's resolutions I diffed the head against `git merge-tree --write-tree cb2026c3b5 46cdd1f919` (tree bea50b1c25). The production part is four resolved conflicts:
  - `coordinator.py`: as under `## Block`.
  - `dhw_planner.py`: imports from `dhw_charges`, with the start helpers on `dhw_start`; `commit_charges(..., space_demand, running)`; `suppress_steps` dropped.
  - `optimizer.py`: #3805's `net_under` and `build` exchange, with main's `step_hours=h.step_hours`. It is byte-identical to #3805's `0a0dba2c18` except for that keyword. `simulate_trajectory` takes `step_hours`, and there is no `start_hour=float` call left in `custom_components/`.
  - `dhw_charges.py`: takes #3805's text.
  - Each matches the body's account.
  - Carry: dismissed: evidence, not a finding
- Previous verdict's block 1 is resolved:
  - `python3 -I tools/audit/check_scopes.py --repo .` reads `ok D5 ... s7:1f/0loc/4399u`, rc 0.
  - `--self-test` reads `SELF-TEST passed`, rc 0.
  - `dev/audit/harnesses/owner_only_channel.py` reads `RESULT arms=48 failed=0`, `OWNER-ONLY CHANNEL HELD`, rc 0.
  - Logs: `ev/prior_block_rechecks.txt`, `ev/check_scopes_selftest.txt`.
  - Carry: dismissed: evidence, not a finding
- Previous verdict's block 2 is resolved: `334dd1bf31` is an ancestor of the head. `tests/features.py` defines `_fl_coord` once (`:35883`), and `_fcap_coord` is at `:66400`. The whole script runs to `ALL 6365 FEATURE CHECKS PASSED`, under the one-line mutant above. Carry: dismissed: evidence, not a finding
- Previous verdict's note (unpinned-sites, the `Span` hot-water field) is still carried as dismissed. This round's delta does not touch it. Carry: dismissed: evidence, not a finding
- Control mutant M4 (`optimizer.py:351`, `space if descent else runs.received(` replaced by `runs.received(`) is killed at this head: `1 of 23 FEATURES BLOCK FAILED`, on the true objective's received-draw check (`ev/mut_M4.txt`). The block does exercise the optimizer side of the approach. Carry: dismissed: evidence, not a finding
- Budget: `tests/structure_budgets.json` `module_excess_loc` goes 21600 -> 21649 against main. `tests/structure.py` at the head prints `RESULT module_excess_loc=21649` and `STRUCTURE RATCHET PASSED`. The +49 is the one #3805's `0a0dba2c18` records over its base (21607 -> 21656), as the body's `## Raise justification` states. `budget-raise-gate` is the gate's own answer. Carry: dismissed: evidence, not a finding
- Claim files: the three-dot diff of `tests/golden/claimed_drift.txt` holds only #3805's `cycling_cost` and `everything_on` claims and their may-drift suspensions. `VERSION` (10.1.7), the manifest and `RELEASE_NOTES.md` are untouched (`ev/version_claims.txt`). Carry: dismissed: evidence, not a finding
- CI: `merge_train.py classify 6ade1643e2 --pr 3907` was polled every ~60 s from 10:06Z and read `WAIT ... pending: gate red: none` through 10:29Z (`ev/classify_poll.txt`). No red was read, so no `## Red checks` answer is owed by this verdict. The owed-reds set is in `ev/owed_reds.txt`. The block above stands on a local measurement, whatever CI concludes. Carry: dismissed: evidence, not a finding
- Not re-derived by this seat: the harness-arm figures, the axis grep counts, the closures counts and the architecture-score dS. They are outside a delta round, and CI's `arch-score` was queued. Carry: dismissed: evidence, not a finding

Fix review: merge 04f8ab9fba6b6708aeabee35507b129a61aca4ae

bus-nonce: abeeafaa496b9d956eae66a651471f07
pending-ci: gate

## Scope

Round 2 of this branch's review: a delta review of PR #3562 at head 04f8ab9fba6b6708aeabee35507b129a61aca4ae against the reviewed head 7db7de155fef49a36118c10ca5747b1804babf32 (merge verdict on probe/revt-r10-hotfix-boost-flow-ceiling-c5f7b0ad, commit ea581b6489). The review packet's `## Review scope` line reads `full`, because no verdict on verdict/3562 names 7db7de15. The handoff verdict sits on a probe ref the packet does not read. The dispatch scopes this round as a delta, and fix-review.md step 12 agrees: `review_carry.py 7db7de15 04f8ab9f` prints FRESH-REVIEW, so this is a later round over its delta. 7db7de15 is an ancestor of the head. The first-parent delta is a clean merge of origin/main (35a2c50d28: `git show --remerge-diff` shows no resolution), the record row 9e02464877, and the merge of 72db7df7a0. The branch's own delta is `git diff 9e02464877 04f8ab9f` (22 files). It contains:
- one production hunk, pump_arbiter.py `desired()`, where `_space_boosted` and the `water` local are inlined;
- #3404's mutant harness re-anchored;
- a configuration.md wording change and the features.py restore-value check, both from the lower hotfix R10-HOTFIX-FLOW-SETPOINT-STUCK, merged in;
- 18 mutation-ledger pins and one survivor triage.

## Evidence

- RESULT head: measured at 04f8ab9fba6b6708aeabee35507b129a61aca4ae in a detached worktree (ev/HEAD.txt). The PR body's `## Head` names the same SHA.
- RESULT roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` printed nothing.
- RESULT merge-tree: `git merge-tree --write-tree origin/main 04f8ab9f` against origin/main fdb526895c exits 0. The ledger driver resolved tests/closures.json as a set, and there is no conflict (ev/merge-tree.txt).
- RESULT version untouched: the three-dot range touches none of VERSION, manifest.json or a release heading. Its RELEASE_NOTES.md hunk is the lower hotfix's dated upgrade note, the same one round 1 found, and the delta does not touch it (ev/version-untouched.txt). No golden fixture or claim file is in the range.
- RESULT production delta equivalence: the old `boosted=water and _space_boosted(coord, inp, now)` with `water = _flow_unit(inp.config)` and the new `boosted=_flow_unit(inp.config) and (inp.mode == MODE_BOOST or boost.held_for(coord).active(boost.CHANNEL_SPACE, now))` are the same expression. `_space_boosted`'s body was exactly that disjunction. `and` keeps the short-circuit, so a non-water set-point still never reads `boost.held_for(coord)`. `_flow_unit(inp.config)` is now evaluated twice, which reads config and changes nothing.
- RESULT arbiter block at head: `features_block.py` from `R.section("pump-duty arbiter — mode and set-points per plan step` to `_pa_subs = _PaCoord(` prints `ALL 61 FEATURES BLOCK PASSED`, rc=0 (ev/arbiter-block-head.txt). This re-derives the body's 61. The modified R10-ARBITER-OFF-RESTORE check (restored value `(1, [25.0])`) passes.
- RESULT reviewer mutants on the inlined line (my own driver, a `git archive` copy per mutant, ev/mutants-delta.txt). All five targeted mutants are killed:
  - R0 NULL (the line unchanged) passes the arbiter block, rc=0.
  - R1 `boosted=False`: 4 or more FAILs.
  - R2 the global boost mode dropped: 3 FAILs.
  - R3 the space channel dropped: 4 or more FAILs.
  - R4 (the water guard dropped) survives the arbiter block, as round 1's M15 did. It is killed by a full `tests/features.py` run: the °F set-points block's `_df_dhw_command` (features.py:77969) raises `TypeError: cannot create weak reference to 'NoneType' object` in `desired` (pump_arbiter.py:1281) through boost.py:291 `held_for` (ev/r4-features-full-excerpt.txt). The guard is therefore still load-bearing and still pinned after the inlining.
  - The R4 copy also shows two FAIL lines (`recorded_at = 'unknown'` and a DHW-dip learner check) that the edited line cannot reach. I did not run an unmutated archive copy of the full suite to confirm those two are `git archive` artefacts (no .git), so I attribute the kill only to the traceback above.
- RESULT prior finding 1 resolved: `dev/audit/harnesses/r10_arbiter_off_restore_mutants.py` refused at 7db7de15 (`M02_no_arm`, `M23_arm_ignores_dropped_record`: old text occurs 0 times). At this head it runs to rc=0 with 36 KILLED and `SURVIVED NULL` on both blocks (ev/pr3404-mutants-harness-head.txt). The re-anchor (M03 on the `boosted=False` arm line, M35 moved to the arbiter block) still kills each mutant.
- RESULT prior finding 2: the out-of-tree probe `probe/boost43.py`'s dismissal stands. The delta adds no claim that depends on it.
- RESULT survivor triage: `survivor_triage/pump_arbiter.py/_boost_ceiling_c.CMP_BOUND.c89e426b.json` (`_gate_floor_c(...) < high` -> `<=`, verdict equivalent) is the same survivor S1 that round 1 re-argued independently as equivalent. With `high` equal to the gate, `_bounded` clamps every heating write to the gate whichever arm runs. I accept the triage.
- RESULT ledger pins: the 18 added `--pin-killed` rows carry their measured failed-count reasons. I did not re-run the mutation table, because CI's heavy runs are cited, not re-run (step 11). The `tests / mutation` lane at this head is pending (see CI below).
- RESULT architecture score: I ran `tools/audit/archscore/gate.py --base e23124ff6e (the PR's current merge base) --head 04f8ab9f` with an empty body. It prints `coord_footprint 2503 -> 2504`, dS -0.0006 (ev/archscore-gate.txt). The rise is +1, as the body says. The body's absolute figures, `2505 -> 2506`, are measured at the older merge base 154dbb4c61 and say so; at the current base the same one unit reads 2503 -> 2504. The body's `## Architecture score` line names the metric and the reason, which the gate's admissibility rule requires.
- RESULT payment check (step 14): the payment removes the `_space_boosted` helper and the `water` local, and I confirmed it reduces the rise from 2 units (CI: 2503->2505 at 9e02464877) to 1. The remaining unit is the computed argument in `desired()`, which holds both the coordinator and the call. Moving the fact onto `ArbiterInputs` would charge coordinator.py's builder instead. I found no payment the body missed that would improve the code. coord_footprint is an architecture-score metric, not a `*_budgets.json` key, and tests/structure_budgets.json is not in the delta.
- RESULT carry audit at the head (packet): 1 finding item, 1 routed, 0 unrouted. The body's Forward-carry is dismissed under the owner's 2026-11-13 ruling.
- RESULT owed reds: `merge_train.py owed-reds` lists `tests / mutation`, `tests / typing` and `validate / validate-hacs`. The body answers the earlier `tests / mutation` red at 9e02464877 under `## Red checks`, along with arch-score, fast and mutation-autofix. No red is recorded at this head while it is pending.
- RESULT CI: `merge_train.py classify 04f8ab9f --pr 3562` was polled about every 60 s from 00:55 to 01:31 UTC (ev/classify-log.txt). Every run printed `WAIT 04f8ab9fba6b6708aeabee35507b129a61aca4ae pending: gate red: none`, rc=3. CI had not concluded when the review was complete, so this verdict carries `pending-ci: gate`. The head was re-read before the push and has not moved.

## Findings

none

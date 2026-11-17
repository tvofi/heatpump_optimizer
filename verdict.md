Fix review: merge e385756030a3814631722ee04dcf6733b1f1f0e0

bus-nonce: 0b503b2e03dadffd9bbc6dd8ff3defcb
pending-ci: gate

Round 3: a delta review over the reviewed head c0bc81e0a196a6aeb5fdb386fe85be385a0e53d3. The delta is the bot pin commit 02266951b6, which adds 25 `killed_by` ledger entries, and the orchestrator's main merge e385756030, which resolves one conflict in `tests/features.py`. The PR's own `custom_components/` diff is byte-identical to round 2's. Round 2 found no code defect. Its block was the red required gate. At this head the gate is still pending: `tests / mutation` is red on 2 sites that are killed but not yet pinned, and `tests / mutation-pins (1)` is still running.

## Findings

- Follow-up: `tests/finite_boundary.py` still has no store-wide check that refuses a `whole=` declaration whose cell costs only itself. This diff settles it only for its two floor leaves. The first sibling is `draw/engaged`. Carried from rounds 1 and 2, unchanged. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (pending orchestrator ruling on a store-wide whole cost check, the fixer.md exception the body names)
- Residual: no committed finder harness exists for this group. The body discloses it, and the approved design's mutation targets and null controls stand in. Carry: dismissed: disclosed in the body; an outside finding whose rows are a range, approved design's own harness stands in
- Residual: round 1's mutant M13 (dropping `np.isfinite(floor) and` in `_stored_floor`) is equivalent behind `_sanitize`. Carry: dismissed: equivalent mutant behind the store boundary's _sanitize

## Notes

- Note: root-cause: `## Red checks` answers `tests / mutation` at fd246e8e5ee7 (27 sites), not at this head. At this head it is red on 2 sites, `draw_range.py:825 CLAMP_DROP` and `:849 GUARD_OFF`. Both are killed by the floor block (Evidence), so this is the same pin lag. The owed red `gate` is still not named in that section.
- Note: body: `## Head` repeats the paragraph for e385756030 four times. It also says the two parents "do not merge cleanly". That is accurate: the remerge shows one conflict, in `tests/features.py`, resolved by keeping both blocks.

## Evidence

- Head reviewed: e385756030a3814631722ee04dcf6733b1f1f0e0 (`ev/HEAD.txt`). It was still `refs/pull/3670/head` when this verdict was written. Contract drift: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty (`ev/roles_drift.txt`).
- Delta, from `git log c0bc81e0a1..e385756030`: the PR's own commits are 02266951b6 (github-actions, "ci: pin killed mutants", 25 new `tests/mutation_ledger/killed_by/` files and nothing else) and the merge e385756030 of main 69053da4f9. Everything else comes in from main.
- Merge resolution (`ev/merge_resolution_remerge.txt`): `git show --remerge-diff` has a single hunk, in `tests/features.py`. It keeps the metered-floor block and main's `#3616 R11-OUTSIDE-ROOMS-P1` block one after the other, removes the conflict markers, and changes no line of either block. `MERGE-CLAIM: resolved tests/golden/claimed_drift.txt`.
- No widening. The PR's three-dot `custom_components/` diff at c0bc81e0a1 and at e385756030 has identical bodies once `index`/`@@` lines are ignored (`ev/prod_diff_body_compare.txt`, rc 0). Main brought in 16 production files (rooms, config_flow, services, and 19 lines in coordinator.py). None of their changed lines mentions band, draw, floor_kw, power or `_pump_m*`. git merged `custom_components/` with no resolution.
- Reviewer mutants on the 2 sites still unpinned at this head (`ev/reviewer_mutants.txt`, spec `ev/reviewer_mutants_spec.json`, driver `tools/audit/seat/mutant_run.py` in copy-tree mode). The command was the floor block (`ev/run_block.sh`, which runs `features_block.py` from `# -- R11-OUTSIDE-HONEST-METERED-FLOOR` to `R.section("#3616 R11-OUTSIDE-ROOMS-P1`), with the prelude from `--emit-prelude` (`ev/floor_block_prelude.py`, 11 statements). Results: `SURVIVED NULL`, `KILLED 825_CLAMP_DROP` (`min(floor or cfg_min, top)` becomes `floor or cfg_min`), `KILLED 849_GUARD_OFF` (`elif floor is None:` becomes `elif False:`). rc 0, 2 of 2 killed. `git status` in the worktree was clean afterwards.
- CI `tests / mutation` (job 133874062005, `ev/ci_mutation_133874062005_tail.txt`) reads `MUTATION TABLE REFUSED -- 2129 unpinned site(s) against 2127 at the ratchet base 69053da4f9..., 2 of them added by this diff`, followed by the two `ADDED UNPINNED` lines above.
- Cheap checks at the head (`ev/cheap_checks.txt`): `STRUCTURE RATCHET PASSED`; `ALL 114 FINITE BOUNDARY CHECKS PASSED`; `tests/env_drift.py --all 69053da4f9` gives `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE`, rc 0; `CARD-CLAIMS-IDENTICAL`; the three-dot diff of `VERSION`, `manifest.json` and `RELEASE_NOTES.md` is empty, and `VERSION` is 10.0.2.
- Merge: `git merge-tree --write-tree origin/main e385756030` at origin/main 69053da4f9 returns rc 0 (tree a3dd115dca), with no conflict.
- Not re-derived: the full `tests/features.py` run. My run was cut off by my own 900 s cap while in its last section (`ev/features_head_tail.txt`, rc 124). Every line printed up to then was `ok`. The body's `ALL 5733 FEATURE CHECKS PASSED` is quoted at 95e70c96d4 and I did not re-check it. CI's `tests / fast (3.14)` was in progress when this verdict was written.
- CI wait: `merge_train.py classify e385756030... --pr 3670` printed `WAIT ... pending: gate red: none` (rc 3) on every poll from 06:59Z to past 07:27Z (`ev/classify.txt`), more than 30 minutes, so this verdict carries `pending-ci: gate`. Owed reds are listed in `ev/owed_reds.txt`. `tests / nightly-status` is red and is outside that set.
- Class: one seam, unchanged from rounds 1 and 2. Release (step 16): the delta adds no refusal on an actuator write.

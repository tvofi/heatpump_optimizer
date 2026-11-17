Fix review: merge c0bc81e0a196a6aeb5fdb386fe85be385a0e53d3

bus-nonce: 9eae24af387cf455ef72ab7ddbaa275a
pending-ci: gate

Round 2 (later round over the reviewed head efc63b60e8a9cf5e90adc1fea09bc584bddf8fe0; scope: delta, per the packet's `## Review scope` line).

## Notes

- Note: stale-figure: `## Unpinned sites` lists `coordinator.py:2439 BOOLOP` and `coordinator.py:2439 GUARD_OFF`, numbered on origin/main 6f422812d5. CI's `tests / mutation` at this head (job 133697069503, merged on main 92d38ecb64) prints the same two sites as `coordinator.py:2445`. The draw_range.py and sensor.py sites match one for one. Paperwork, not a block. Carry: dismissed: line numbering of a body figure; CI's own ADDED list at this head is the record
- Note: stale-figure: `## Red checks` names the `tests / mutation` red at fd246e8e5ee7. The same red stands at this head: `MUTATION TABLE REFUSED -- 2197 unpinned site(s) against 2165 at the ratchet base 92d38ecb64..., 32 of them added by this diff`. Its 27 ADDED lines are the body's sites. The answer (pin lag, each site killed locally, no cheaper detector) still holds.

## Findings

- Follow-up: no store-wide check refuses a `whole=` declaration whose bad cell costs only itself. The new `metered floor, declared cost` check covers only `draw/floor_kw` and `draw/floor_since`. The body's own class rule returns `draw/engaged` as a live over-broad licence, declared on main before this diff. I re-derived it at this head (`ev/class_seams_probe.txt`): `engaged='x'` keeps 20 samples, the config and the floor, and only the latch reads False. The body carries it to its own group, pending the orchestrator's ruling on scope. That route is fixer.md's pending-ruling exception, so it is not `carry-missing: own-group`. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR
- Residual: no committed finder harness exists for this group. This is unchanged from round 1. Carry: dismissed: disclosed in the body; an outside finding whose rows are a range, approved design's own harness stands in
- Residual: round 1's mutant M13 (drop `np.isfinite(floor) and` in `_stored_floor`) is equivalent behind `_sanitize`. The delta does not touch `_stored_floor`. Carry: dismissed: equivalent mutant behind the store boundary's _sanitize

## Evidence

- Head reviewed: c0bc81e0a196a6aeb5fdb386fe85be385a0e53d3 (`ev/HEAD.txt`). The branch tip read back at the end is the same SHA. The body's `## Head` names it. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Round 1's block is resolved. `review_carry.py efc63b60e8 c0bc81e0a1` prints FRESH-REVIEW, because of one branch commit, 95e70c96d4. That commit removes `whole=_DRAW_KEY` from `draw/floor_kw` (now `Domain("real", _POS)`) and `draw/floor_since` (now `_COUNT` = `Domain("int", 0)`). It also adds the `metered floor, declared cost` check. The other three commits are merges of main. `git diff 367c3b9cac 95e70c96d4` and `git diff 92d38ecb64 c0bc81e0a1` agree line for line, apart from hunk offsets, so the merges carry no resolution of their own.
- Delta scope: the production delta is two declarations in `store.py` `_ACCURACY`. Both narrow a licence and no loader reads `whole`. Nothing already reviewed is at a non-obvious risk, so the review did not widen.
- Floor block at the head (`tools/audit/seat/features_block.py` with its emitted 11-statement prelude, `ev/floor_block_prelude.py`): `ALL 14 FEATURES BLOCK PASSED`, rc 0 (`ev/floor_block_head.txt`).
- Reviewer mutants (`ev/reviewer_mutants.txt`, driver `ev/reviewer_mutants_driver.py`, every file restored, `git status` clean):
  - M1, `whole=_DRAW_KEY` restored on `draw/floor_kw`: KILLED (declared cost).
  - M2, the same on `draw/floor_since`: KILLED.
  - M3, a loader that drops the samples on a bad `floor_kw`, with the declaration left as cell: KILLED.
  - M4, a loader that drops the configuration on a non-int `floor_since`: KILLED.
  - N0, a null comment-only edit: SURVIVED, as expected.
  - The check therefore holds the declaration to the measured cost in both directions.
- Class: the body's rule (each `_ACCURACY` key whose `whole` is `_DRAW_KEY`) returns `['draw/engaged', 'draw/config/#']` at the head (`ev/class_rule_probe.txt`). That matches the body's two seams. `draw/config/#` drops the samples (the licence holds), and `draw/engaged` is carried (Findings). Null: the good record round-trips (`ev/class_seams_probe.txt`). No seam is left undispositioned.
- `tests/finite_boundary.py`: `ALL 114 FINITE BOUNDARY CHECKS PASSED`. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Full `tests/features.py` at this head: `ALL 5794 FEATURE CHECKS PASSED`, rc 0 (`ev/features_full_head.txt`). The body's `ALL 5733` is stated at 95e70c96d4, before two main merges, and I did not re-derive it at that SHA. The +1 from the declared-cost check is consistent with the 13 to 14 count of the floor block.
- Claims: `tests/env_drift.py --all 92d38ecb64` at the head prints `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE`, with CLAIMED for the five coord fixtures (`ev/env_drift_all_vs_92d38ecb.txt`). `card_claimed_drift.txt` is byte-identical to the merge base. `claims-for: 10.0.2` equals `VERSION`.
- Versions: `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched; the three-dot diff is empty (`ev/versions.txt`).
- Merge: `git merge-tree --write-tree origin/main c0bc81e0a1` gives rc 0 and tree c4b234c61e, with no conflict (`ev/merge_tree.txt`).
- Owed reds (`ev/owed_reds.txt`): the only owed red at this head is `tests / mutation` (job 133697069503). The body's `## Red checks` answers it (pin lag), and its 27 ADDED lines are kept in `ev/ci_mutation_added_sites.txt`. `tests / replay` and `tests / nightly-status` are red but outside the owed set, so they are neither answered nor a block.
- CI: `merge_train.py classify c0bc81e0a1 --pr 3670` printed `WAIT c0bc81e0a196a6aeb5fdb386fe85be385a0e53d3 pending: gate red: none` (rc 3) on every run from 00:50 to 01:19 UTC (`ev/classify_log.txt`). This return therefore carries `pending-ci: gate`.
- Release (step 16): the delta adds no refusal on an actuator write.
- Supersedes: an earlier fire of this seat (same nonce) pushed 371ea27ef9a95544ff7fe00f2ec73542a8013b3a to this probe ref at 2026-11-16T23:18Z. It was `blocked ... ci-red`, because `tests / mutation` was red and mutation-autofix had been cancelled. Since then the `tests / mutation-pins (1..7)` shards have re-run at this head (7 succeeded, the rest in progress at 01:20Z), and classify reads WAIT, not RED. This return replaces that ref by a lease pinned to 371ea27ef9.
- I did not re-run the gate or the mutation table; those are CI's.

Fix review: merge d112c64e4cfc5611f4225c8c5c09e60ef2320fad

bus-nonce: a4e96891a298f021c8671a6a3c0d16ba

Round 3: a delta review over the reviewed head c0bc81e0a196a6aeb5fdb386fe85be385a0e53d3. Round 2's only block was the red required gate. It is cleared: classify now reads GREEN at this head.

## Findings

- Follow-up: `tests/finite_boundary.py` still has no store-wide check that refuses a `whole=` declaration whose cell costs only itself. This is unchanged from rounds 1 and 2. The body names `draw/engaged`, which was on main before this diff, as the first sibling. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR
- Residual: there is no committed finder harness for this group. The body discloses this, and the approved design's own harness stands in. Carry: dismissed: disclosed in the body; an outside finding whose rows are a range, approved design's own harness stands in
- Residual: mutant M13, which drops `np.isfinite(floor) and` in `_stored_floor`, is equivalent behind `_sanitize`. Carry: dismissed: equivalent mutant behind the store boundary's _sanitize

## Notes

- Note: claim-layout: the hand resolution in 9a7fee16a2 put the five coord claim lines inside the comment paragraph of the `# may-drift: flat_prices` entry. They sit between its third and fourth comment lines (`ev/claim_merge_resolution.txt`). Nothing parses differently: `_claimed` skips `#` lines, and `env_drift.py --all` reads `flat_prices` as may-drift at this head. The comment now reads split, though. The stamp empties the list, which repairs it.
- Note: stale-body: the last bullet under `## Null control` is truncated mid-sentence ("every other fixture unmoved (`## Figures").

## Evidence

- Head reviewed: d112c64e4cfc5611f4225c8c5c09e60ef2320fad (`ev/HEAD.txt`). `git ls-remote origin refs/pull/3670/head` printed it when this verdict was written, and the body's `## Head` names it. Contract drift: none in `fix-review.md` (role pack rendered at origin/main).
- Delta: `review_carry.py c0bc81e0a1 d112c64e4c` prints FRESH-REVIEW because 9a7fee16a2 resolves `tests/golden/claimed_drift.txt` by hand. The branch's own commits in the delta are:
  - 02266951b6 and 41ca33b38d: `ci: pin killed mutants`, 20 `killed_by` json files.
  - 9a7fee16a2: the main merge. The resolution is main's 10.0.3 file plus only this branch's five coord claims and their comment block.
  - 4afcaaad6d: the D6 register, C115 `86 -> 88`, the two entity names this branch adds.
  - e6a363735c and d112c64e4c: merges.
- No production widening owed. I diffed the PR's own three-dot diff over custom_components/ and tests/ at the reviewed head and at this head (`ev/own_diff_delta.txt`). Only index hashes and hunk offsets differ; no added or removed line changed. Main's changes to `sensor.py` across the merges (+52 lines) touch none of `ModelStatusSensor`, `_pump_power_end` or the `pump_min_power*` attributes. The merges went through git without conflict except the claim file.
- CI: `merge_train.py classify d112c64e4c --pr 3670` prints `GREEN d112c64e4cfc5611f4225c8c5c09e60ef2320fad pending: none red: none` (rc 0), read twice (`ev/classify.txt`). The packet's digest showed `tests / replay` and `tests / nightly-status` as failures. Neither is in the owed-reds set (`ev/owed_reds.txt`: tests / mutation, tests / typing, validate / validate-hacs, ...), so neither is answered nor a block. `tests / mutation` is green after the bot pin commits, which clears round 2's block.
- Red checks: the body's `## Red checks` answers `tests / fast (3.14)` at 41ca33b38d (D6 register stale after the merge; the cheaper detector is named, none built, with a reason), `gate`, `pr-contract` and `tests / mutation`. I checked that the trigger was answered, not the answer.
- Claims: `tests/env_drift.py --all b6e52b0598` at the head prints `CLAIMED` for coord_all_features, coord_dhw, coord_grid_fee, coord_minimal and coord_two_zone (3 leaves each). It then prints `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE`, rc 0 (`ev/env_drift_all.txt`). `claims-for: 10.0.3` matches main's stamp.
- Versions: the three-dot diff of `VERSION`, `manifest.json`, `RELEASE_NOTES.md` and `card_claimed_drift.txt` is empty. Only `tests/golden/claimed_drift.txt` appears (`ev/claims_versions_3dot.txt`).
- Merge: `git merge-tree --write-tree origin/main d112c64e4c` at origin/main 76bbf63744 returns rc 0 (tree 5c4b986c84), no conflict (`ev/merge_tree.txt`).
- Figures: I did not re-run D6 `claims.py` or `harness_headers.py`. `tests / fast (3.14)` is green at this head, and it is the check that refused the 86/88 mismatch, so I take the C115 figure as verified by CI. I did not re-derive the body's `ALL 5733 FEATURE CHECKS PASSED`. I did not re-run the gate or the mutation table, which are CI's job.
- Mutation proof: the delta changes no production line, so no new mutant is owed. Round 2's reviewer mutants R1 to R4 (4 of 4 killed) stand on unchanged code.
- Class: one seam, unchanged. Release (step 16): the delta adds no refusal on an actuator write.
- Self-audit: `carry_audit.py check` over this verdict prints `CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)`, rc 0 (`ev/carry_audit.txt`). The body was not saved to a local file (this seat has no `gh`), so the run passed an empty `--body`. The packet's own carry_audit of the body at this head read 3 routed, 0 unrouted.

Fix review: merge 8f77851df5b6eea927d9dd19dc853b7b3900088c

bus-nonce: e1749ea79e62e209974e6c9e269407d9
pending-ci: gate

## Evidence

Round 1 (first review; packet scope full). Head reviewed: 8f77851df5b6eea927d9dd19dc853b7b3900088c (`ev/HEAD.txt`); body's code head 3bd933a0d plus a clean main merge (a05a8b00d9) and the delivery row.

- Role contract current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` empty.
- Merge with main: `git merge-tree --write-tree origin/main 8f77851df5` rc=0, tree 16b2693d8a (`ev/merge-tree.txt`).
- VERSION, manifest, RELEASE_NOTES.md, tests/golden and both claim files: three-dot diff from ae0ed64af8 empty.
- Structure budgets move down only (class_excess_loc 17382 -> 17356, max_class_loc 7875 -> 7873); no raise.
- Null control: pm block at head `ALL 12 FEATURES BLOCK PASSED` (`ev/null-pm.txt`); `tests/config_flow_steps.py` `ALL 599 checks PASSED` (`ev/cfs-null.txt`).
- Mutation proof, my mutants, each restored after (`ev/mut-*.txt`); every one killed:
  - zone_trajectories without the two_zone flag: 3 FAIL (R10-CLONE-2238 P3, D12-s1-01 x2).
  - zone_trajectories requiring only the upper list: 1 FAIL (D12-s1-01 None-without-both).
  - `_build_plan_views` passing True: 1 FAIL (single-zone plan rows).
  - sensor_trajectory always room: 1 FAIL; returning the lower floor: 1 FAIL (R10-CLONE-2238 P3).
  - refusal gate `if False:`: 3 FAIL; the refusal call deleted: 3 FAIL; SINGLE_ZONE_HOUSE_FIELDS without the heat-loss key: 1 FAIL; `if field is None: return` disabled: 1 FAIL (null control).
  - `_gap_probe_terms` DHW gate `if True:` and `if False:`: 1 FAIL each (D8-s1-01 and its null control).
  - two_zone_from_config auto arm forced True: 1 FAIL (D12-s2-01).
  - options row's `when=_single_zone` removed: `1 of 599 checks FAILED` (D17-s1-03).
- Finder harnesses from `git archive 819aa2e354 dev/audit/rounds/round11`, sha1s equal the body's, base bc658f9de vs head (`ev/finder-*.txt`):
  - D12/s1/plan_zone.py: zone_plants 8 -> 0, zone_rows 768 -> 0, control_two_zone_rows 96 at both ends.
  - D17/s1/h_zone.py: two_zone_only_no_effect 1 ['house_thermal_mass'] -> 0, single_zone_rendered 9 at both ends.
  - D17/s3/f02_two_zone_inert.py: base auto plan_delta 166.430 / 4.931 kW-steps, on cells 0.000; head ends in the ServiceValidationError the fix raises, as the body states.
  - D8/s1/gapdhw.py: base no_dhw_priced=12 of 22, dhw_null=4 of 6; head ImportError on the renamed private symbol, as the body states.
  - The gapdhw port, rebuilt by this reviewer from the body's patch (my file's sha1 91dd8fda70, not the body's f42e8e5f82: built by me, not the fixer's copy): base no_dhw_priced=12, no_dhw_top=12, dhw_null=4; head no_dhw_priced=0, no_dhw_top=0, dhw_null=4 (`ev/port-*.txt`). The body's figures match.
- Class: the body's four enumeration greps re-read against the diff; every returned site is in the diff or dispositioned (pm-06 for the list readers). The refusal iterates `_loaded_coordinators(hass)`, the same set as the handler's `targets`, so it refuses before any target's write.
- Red checks: `tests / mutation` is red and in the owed-reds set; the body's `## Red checks` names it and answers it (the 11 added sites for mutation-autofix). `tests / nightly-status` red is not in the owed set.
- CI: classify polled every ~90 s from 15:20 to 15:57 UTC, every run `WAIT 8f77851df5b6eea927d9dd19dc853b7b3900088c pending: gate red: none` (`ev/classify-log.txt`); returned with `pending-ci: gate` per the brief. Head re-read at 15:58 UTC: still 8f77851df5.
- Figures re-derived: finder RESULT lines above. Not re-derived: the 5911 features count, unpinned 2101/2091, archscore dS +0.1375 (CI `arch-score` success at this head), the f02_refusal port's figures (the gapdhw port is re-derived above).

## Findings

- Note: stale-body: `## Head` says main is not merged in (fixer step 6), yet the head carries merge commit a05a8b00d9 of origin/main; the same section's first paragraph says main merged cleanly. Paperwork only, the merge resolved without conflict. Carry: dismissed: paperwork on this PR's own body, no later stage reads it

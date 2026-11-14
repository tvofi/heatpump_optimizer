Fix review: merge 5831759301bb8ecabf97feeca3238c2d5ebaef5b

bus-nonce: 1eb35a15176c468b9d6ffbda651d6e44

## Evidence

- Round: the second review, a delta round over the reviewed head 43227286fc18822b7955e54aa5323cc61feab39e (`Fix review: blocked ... mutation-vacuous`, probe `probe/revt-r10-start-counter-edges-12272296`). Scope: `git diff 43227286fc 5831759301` and the prior block resolved (fix-review.md step 12). No pull request exists yet, so there is no review packet and no CI to read. No check runs exist at this head. `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing`, `validate / validate-hacs` (`ev/owed_reds.txt`). None has run at this head, and the body answers `mutation` and `main-conflict` under `## Red checks`.
- Head: the body's `## Head` (handoff-body ref at d5e5b3fa6e) names 5831759301bb8ecabf97feeca3238c2d5ebaef5b, the head I measured (`ev/HEAD.txt`).
- Merge: `git merge-tree --write-tree origin/main 5831759301` at origin/main d7004eaa77 exits 0. The claimnotes/ledger drivers resolve `tests/structure_budgets.json` and `tests/closures.json`, with no conflict (`ev/HEAD.txt`).
- Roles: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- The delta is three commits:
  - 1d15eb6bdb adds one check to `tests/features.py` (21 lines, the timer-armed blip).
  - 5831759301 adds one mutant line (`timer-delay-zero`) to `dev/audit/harnesses/start_counter_edges_mutants.py`.
  - 7d3ab93eed merges origin/main e901e9ef29. Its `--remerge-diff` (`ev/merge_resolution_remerge_diff.txt`) shows hand resolution only in the module counts: `docs/architecture.md` (93 modules, 33 importers, both map rows kept), the round-4 D6 register (`claims.md`, `.json`, `.py`) and `tests/deployment_shape.py` (112 files). Each resolution unions both sides' added module, `running_signal.py` and main's `whatif.py`. The two ledger files are driver-resolved.
  - Every other path in the delta stat (`ev/delta_stat.txt`) is main's own content, merged textually clean. That includes the production files `coordinator.py`, `optimizer.py`, `price_tiles.py`, `whatif.py` and the card.
  - `running_signal.py`, `wear.py` and `duty_switch.py` have an empty diff across the delta.
  - The branch's coordinator hooks (`attach`, `detach`, `subscribe`, the per-refresh `note`) are unchanged. Main's new what-if path (`whatif.scratch_copies`) deep-copies config and params only and never reaches the start counter or the running signal. So the production delta puts no reviewed code at non-obvious risk, and the scope is not widened.
- RESULT mutation (tracked proof re-run at the head, `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/start_counter_edges_mutants.py`, `ev/mutants_head.txt`): `BASELINE [(0, False), (0, False)]`, 22 mutants, 22 KILLED, `RESULT survived=0`, `git status` clean after. `timer-delay-zero` is killed with "1 fail, 0 fail" on "a meter blip shorter than the debounce counts no start (5 s and one second under it), and one second over it counts one; no timer outlives either". This matches the body's 22 of 22.
- Prior block resolved: I applied `delay = 0.0` at `running_signal.py:178` directly and ran the build's features.py block alone (`tools/audit/seat/features_block.py`, `ev/reviewer_delay_mutants.txt`).
  - Unmutated: `ALL 16 FEATURES BLOCK PASSED`.
  - Mutated: `1 of 16 FEATURES BLOCK FAILED`, the new check reading `{5: (1, 0), 29.0: (1, 0), 31.0: (1, 0)}`. This is exactly the body's quoted figures.
  - My own neighbouring mutant, `delay = 1.0` (a debounce shorter than the blip), is killed by the same check with the same reading.
  - The null control inside the check is the 31 s blip, which counts 1 both unmutated and mutated. At 43227286fc the same mutant survived both blocks (the previous verdict's `ev/reviewer_mutants_driver.log`), so the kill comes from this delta's check.
- The check drives the case the block named: the revert lands while the confirm timer is still pending, read at 10 min + 5/29/31 s on a meter-only rig, with no timer left after either case.
- Structure: `python3 tests/structure.py` exits 0 at the head (`ev/structure_head.txt`). It reads class_excess_loc 17446, coordinator_multiassigned_attrs 105, max_class_loc 7887 and seam_cut_total 416. Against origin/main e901e9ef29's budgets (17453, 106, 7894, 416), that matches the body's figures. The budget file moves only down across the delta, through the ledger driver's "both deltas" sum.
- Untouched: `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files have no diff from the merge base.
- Figures not re-derived: I did not re-run the whole `tests/features.py`, the scoped gate, the archscore dS or the CI mutation table. These are CI's heavy runs and none has run (no PR). The body says it did not run the whole script either.

## Findings

None. The prior block is settled in this pull request.

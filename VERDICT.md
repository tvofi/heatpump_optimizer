Fix review: blocked efc63b60e8a9cf5e90adc1fea09bc584bddf8fe0 harness: draw/floor_kw and draw/floor_since are declared whole=_DRAW_KEY in store.py, but a bad cell costs only itself; the licence is false and unneeded

bus-nonce: c478b265f4016848f7c01bab4fbb62b1

Round 1 (first review of this pull request; no --reviewed-head).

## Block

- `custom_components/heatpump_optimizer/store.py` `_ACCURACY` declares the two new leaves `"draw/floor_kw": Domain("real", _POS, whole=_DRAW_KEY)` and `"draw/floor_since": Domain("int", 0, whole=_DRAW_KEY)`. `_DRAW_KEY` reads "the configuration keys the record: unreadable, the samples and the latch are dropped with it". That is false for these leaves. `_stored_floor` reads a bad cell as unset (or 0) and keeps the record. Probe at the head (`ev/bad_floor_cell_cost_probe.txt`): `floor_kw` set to `'x'`, `-1.0`, `True` or `[1]`, and `floor_since` set to `'x'`, `-3` or `1.5`, each keep all 80 samples and the config. Only the bad cell reads unset.
- The licence is not needed. With `whole=` removed from both declarations, `tests/finite_boundary.py` prints `ALL 114 FINITE BOUNDARY CHECKS PASSED` (`ev/finite_boundary_without_whole_on_floor_leaves.txt`). As written, it licenses a future loader change that drops the draw record (its samples, ceiling and latch) on one bad floor cell, and Arm 6 would not see that. This is the inverse of the mis-declaration this diff corrects on `draw/samples` and `draw/ceiling` (the body's "Also corrected in this diff").
- Fix: declare both leaves without `whole` (e.g. `Domain("real", _POS)` and `_COUNT`, as `draw/overdraws` is). Re-run `finite_boundary.py`. This is a production-file declaration, so it blocks under fix-review.md's C5 rule ("one on `custom_components/` blocks").

## Findings

- Follow-up: `tests/finite_boundary.py` has no check that refuses a `whole=` declaration whose cell costs only itself. An over-broad licence passes silently both ways (above). That is how the false declaration reached review. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR
- Residual: no committed finder harness exists for this group. The body discloses it ("no finder harness exists for this group"), and Bankaifan's report gives a range, not a time series. The design's 24 mutation targets and null controls (a) to (c) stand in. They are the fixer's instruments, not the finder's (fix-review.md step 9). Carry: dismissed: disclosed in the body; an outside finding whose rows are a range, approved design's own harness stands in
- Residual: reviewer mutant M13 (drop `np.isfinite(floor) and` in `_stored_floor`) survives the floor block and `finite_boundary.py`. It is equivalent on the real load path: `store.py:757` passes every load through `_sanitize`, which scrubs a non-finite leaf to `None` before `DrawRange.from_dict` (`accuracy.py:526`) reads it. Carry: dismissed: equivalent mutant behind the store boundary's _sanitize

## Evidence

- Head reviewed: efc63b60e8a9cf5e90adc1fea09bc584bddf8fe0 (`ev/HEAD.txt`), at the PR's head at render. Merge base 367c3b9cac. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Merge: `git merge-tree --write-tree origin/main efc63b60e8` rc=0 (tree 0f10a6ae67), no conflict.
- Versions: `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched (three-dot diff empty).
- Failing test first: the floor block on the merge base's `custom_components/` with the head's tests raises `TypeError: solve_band() got an unexpected keyword argument 'applies_floor'` (`ev/floor_block_on_base_production.txt`). At the head: `ALL 13 FEATURES BLOCK PASSED`.
- Reviewer mutants, 18 of my own run against the floor block (`ev/reviewer_mutants.txt`, driver `ev/reviewer_mutants_driver.py`, every file restored, `git status` clean): 16 KILLED. M12 (status sensor drops `**_pump_min_power`) SURVIVED the block and is KILLED by `tests/golden.py` (rc=1: the five coord fixtures' three `pump_min_power*` leaves `present on one side only (the fixture has it)`, `5 STALE CLAIM(S)`; `ev/m12_golden.txt`). M13 is equivalent (Findings).
- Claims: `tests/env_drift.py --all 367c3b9cac` at the head prints `CLAIMED` for exactly coord_all_features, coord_dhw, coord_grid_fee, coord_minimal and coord_two_zone, `3 leaves moved` each, then `no committed fixture is stale` and `NO UNCLAIMED DRIFT: 56 scenario(s) checked`. Every moved fixture is claimed and every claim moved (`ev/env_drift_all_vs_367c3b9cac.txt`). `card_claimed_drift.txt` is byte-identical to the merge base. `claims-for: 10.0.2` equals `VERSION`.
- Figures re-derived at the head: `tests/structure.py` prints `STRUCTURE RATCHET PASSED`. D6 `claims.py` gives C115 `0 of 86 entity names identical in sv and en`, rc 0, and leaves the register unmodified. `finite_boundary.py` gives `ALL 114 FINITE BOUNDARY CHECKS PASSED`. CI `arch-score` succeeded. I did not re-run the gate or the mutation table (CI's).
- Mutation ledger: the nine deleted `killed_by` pins each name an `old` line this diff rewrites, so the deletions are earned by the change.
- `tests / mutation` (job 133449015710) is red: `MUTATION TABLE REFUSED -- 2207 unpinned site(s) against 2175 ... 32 of them added by this diff`. Its ADDED list is identical, line by line, to the body's `## Unpinned sites` on the merged tree (27 lines, 32 sites; `ev/ci_mutation_added_sites.txt`), so the orchestrator's remap holds. The body's `## Red checks` answers this red (pin lag, no cheaper detector) and names `tests / nightly-status`, which is outside the owed set `merge_train.py owed-reds` prints.
- Class: the body names no enumeration rule, and the finding states one seam (the configured floor). This is a one-seam class.
- CI at this head when returned: `merge_train.py classify` still prints `WAIT efc63b60e8a9cf5e90adc1fea09bc584bddf8fe0 pending: gate red: none ` (rc 3, WAIT). This verdict blocks on code and does not depend on CI.
- Release (step 16): the diff adds no refusal on an actuator write.

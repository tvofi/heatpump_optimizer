Fix review: merge 0662bd8e09b3cc3c57c6d6e79ac069ffaa7b297b

bus-nonce: 72041f1191eb7629792a6e1b35d43f2d

Reviewer seat r9c-rev-2025, round 5. I reviewed from a fresh detached worktree, /Users/timmalmstrom/hpo-seats/r9c-rev-2025-r5. The delta from bfaf5486 is bd4ac1df and 9b31227e. The merge 0662bd8e has an empty remerge-diff, and main is unchanged at 2d8cab3f. `git merge-tree --write-tree origin/main 0662bd8e` exits 0. The live head was re-read at posting and had not moved.

**Condition, set by the dispatch:** mutation is red on unpinned sites until R9-CI-1's sharded pin run, and this merge verdict is conditional on mutation going green. Everything else is judged below and holds.

## Round-4 block 1: EntryConfig copies by value (fixed)

- `EntryConfig.__reduce__` -> `_restore(dict(raw), parsed fields)`.
- At the head: `copy.deepcopy`, `copy.copy` and the pickle round trip all return an EntryConfig with equal parsed fields, an equal raw and an equal mapping. My first pickle line read raw_equal=False, but that was my own NaN input (nan != nan). Re-run without NaN: raw_equal=True, mapping_equal=True.
- The deep copy's raw is independent (`deepcopy_raw_independent True`).
- The copy stays frozen (`FrozenInstanceError`), and item assignment is refused.
- Mutant R1 (`__reduce__` renamed away) is KILLED by the new entities.py check "an EntryConfig survives deepcopy and a pickle round trip ...", which fails with TypeError. Null R0 passes (ALL 2217).
- CI: `fast (3.14)` success, job 113069942832. `[00:07:18] ok python3 tests/boost_drift_replay.py (1879s)`, ALL 46 BOOST DRIFT CHECKS PASSED.

## Round-4 block 2: max_class_loc paid in code (fixed)

- **Re-wrap plant re-run:** `plant_rewrap.py` now asserts on its first statement, because there is nothing to re-wrap. Both calls are 3-line again, exactly as on main 8d7903e6.
- **Step-14 null on the new payment:** `plant_unfuse.py` puts the fuse formula back inline at both coordinator sites, exactly as bfaf5486 had it. Result: `RESULT max_class_loc=8823`, `FAIL 8823 > 8817 (+6)`. So the whole payment of 6 is the fuse move.
- **The move earns it.** It removes the formula's second copy (the fuse advisor's `phases`/`230.0` inline) and leaves one definition on the config object that owns the inputs. It is not a reformat.
- Head: `STRUCTURE RATCHET PASSED`, max_class_loc 8817 <= 8817, below the ledger-merged 8821. seam_cut_total 760 and duplication_copies 38 are unchanged. No budget raised.

## The fuse move is behaviour-preserving

- `fuse_kw()` = `fuse_kw_at(amps) if amps > 0 else None`, and `fuse_kw_at(a)` = `a * max(1, int(phases)) * 230.0 / 1000.0`. These are the same expressions as the old `_fuse_kw` and the old advisor line (`smaller * max(1, int(phases)) * 230.0 / 1000.0`).
- Grid against the old formula over the parsed fields: 96 configs (amps in {-5, 0, 0.5, 10, 16, 20, 25, 35, 63, "x", None, inf} x phases in {0, 1, 2, 3, 3.7, "3", -1, "bad"}), plus fuse_kw_at at 4 advisor values each. `mismatches=0`.
- Mutant R2 (the `amps > 0` guard dropped) is KILLED. 6 checks fail, including "only the unbounded cell keeps Cost Power Headroom unavailable" and "the configured fuse is 20 A x 3 phases = 13.8 kW, no fuse is None ...".
- Mutant R3 (the `max(1, ...)` phase clamp dropped) SURVIVES entities.py. It is not a regression: main had no pin on the inline clamp either (no `_fuse_kw` entry in the ledger), and the body lists the site as `entry_config.py:266 CLAMP_DROP` under Unpinned sites for the mutation chain.

## Carried checks at this head

- My scan: HOLDER-MAPPING-READS 0, UNDEFINED {}. ATTR-NOT-A-FIELD lists only `fuse_kw` and `fuse_kw_at`, which are the new EntryConfig methods. My allow-list predates them, so this is not a defect.
- Quiet live apply (my driver): `live_spec='09:00-09:30' live_off_steps=2 reloaded=0`, and the rebuilt coordinator gives the same.

## CI at 0662bd8e (`checkruns_head.tsv`)

- **Success:** typing, closures, coverage, env-matrix, and fast (3.14).
  - fast ran `MODE: SCOPED -- 29 script(s) run`.
  - Results: features ALL 3845, entities ALL 2217, stress ALL 106, boost_drift ALL 46, structure, manual_plan, and `env_drift.py --all 2d8cab3f` ok (golden fixtures in drift mode).
- **mutation: failure** (113069942817): "63 not started for --budget-minutes", nothing measured. The dispatch said 46; CI says 63, because this round adds the fuse and `__reduce__` sites. mutation-autofix: failure (nothing to pin). These are the R9-CI-1 condition above.
- **Not this PR's:** delivery-status, nightly-status, and budget-raise-gate (a cancelled twin; a sibling run succeeded; no leaf raised). The cancelled twin may need a re-run before merge.
- `## Red checks` names the bfaf5486 `fast` red with its answer, plus mutation, mutation-autofix and the earlier rounds' reds. The stray 6fa6f2aa head paragraph is gone.

Evidence: /Users/timmalmstrom/hpo-seats/r9c-rev-2025-ev5. It contains:
- HEAD.txt, checkruns_head.tsv, joblog_113069942832.txt (fast), joblog_113069942817.txt (mutation)
- entryconfig_copy_and_fuse.txt, mutation_entities.txt, entities_R*.txt
- structure_head.txt, structure_plant_unfuse.txt, plant_rewrap_result.txt
- scan_head.txt, quiet_reload.txt, pr-body.md
- the reviewer-built plant_rewrap.py, plant_unfuse.py and mutate_r5.py

Rounds 1-4: r9c-rev-2025-ev, -ev2, -ev3, -ev4.

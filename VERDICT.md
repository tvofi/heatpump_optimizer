Fix review: blocked 9c66410942bceb57ccb753b87d74721854d57ce7 harness: probe out of tree -- the 6840 equivalence probe the triage row and body cite lives at a machine path (fixer.md 18)

bus-nonce: cdd66b91772176b043b6cfeaa22d7bde

Reviewer seat review-2025-r6, round 7 of PR #2025 (R9-EG-B11, #1745). This round reviews the delta 95b08306..9c664109, checked out detached in /Users/timmalmstrom/hpo-seats/review-2025-r6/wt. I prepared against the merge base and measured the head after CI settled. The live head was re-read at posting and is still 9c664109.

**Everything substantive holds. The block is one rule, and the fix is mechanical.** Code before 95b08306 was not re-reviewed, per the dispatch.

## The block: fixer.md step 18

The survivor_triage row `HeatPumpOptimizerCoordinator._forecast_arrays.CMP_BOUND.54c3c7b5.json` cites its measurement as `/Users/timmalmstrom/hpo-seats/r9c-egb11/ev7/equiv_6840.py` (sha1 3e661d15, which matches the file on this machine). The body's Mutation proof cites the same path.

That probe is what a later seat reruns to re-check the equivalence mark, for example when the line or `_liquid_fraction` changes. It is also how the body's figures (552 cases, 0 vs 264) are reproduced. So it must land in this PR (`tools/audit/harnesses/`). The committed ledger row on main would otherwise name one machine's home directory.

`tmp_paths.py` does not scan ledger JSON or body prose, so CI could not catch this. Review owns it (step 9).

**Fix, one pass:**
1. Land `equiv_6840.py` under `tools/audit/harnesses/`, unchanged in substance, and classify it (closure or INERT) so `entities.py` stays green.
2. Point the triage row's `reason` at the tree path. Re-run `mutation_table.py --normalize`; the anchor is unchanged.
3. In the body, cite the tree path in Mutation proof. Name the new head in Head.

## What holds; next round needs only the delta above

### (a) Merges
- **bf372564, 0864a8d2, 5d4f3b04 and 9c664109:** `git merge-tree --write-tree` over each merge's parents reproduces its tree exactly, and the remerge-diff is 0 lines for every one.
- bf372564 and 9c664109 print `LEDGER-MERGE: resolved tests/closures.json`, which is the driver.
- de81043a is the bot's closures re-record, `tests/closures.json` only.

### (b) The 6840 CMP_BOUND equivalence: attacked, and it holds
I traced every path into `precip_array`:
- `_weather_series` timed rows, untimed rows and the no-forecast zeros;
- the padding (`series[-1]` or 0.0).
Every rain value passes `max(0.0, _as_float(...))`, and `_as_float` maps None, text, overflow and non-finite input to the default.

Snow is `max(0.0, float(snow))`, so a NaN answer becomes 0.0, or it stays 0.0. There is one guard site (6840) and one caller of `_liquid_fraction`. `np.any` over an empty array is False on both arms.

My own probe, `liquid_identity.py`, is independent of the fixer's:
- `p * _liquid_fraction(p, 0)` against p, bitwise, over 1,998,978 finite non-negative float64 values. These are random bit patterns covering every exponent and subnormals, plus the edges around 1e-9, 0, -0.0 and max. Result: `RESULT finite_values=1998978 bitwise_differing=0`.
- Control: inf and nan become nan, so the probe detects the only distinguishing input.
- The entity clamp over 15 hostile values (inf, "1e309", 10**400, nan, None, text, -3, -0.0, np.float32 inf, and others) yields only finite values >= 0: `RESULT entity_clamp True`.
- I did not rerun the fixer's 552-case probe. Its sha1 matches.

### (c) The four hand-applied pins in c5e00ae3
- Artifact 11547045879 is `mutation-pins-1` from run 37763212023 at head_sha de81043a, with `status=measured` and `head=de81043a`.
- I compared each pin with its artifact row field by field (anchor, killed_by, old, reason): `RESULT pins=4 artifact_rows=4 mismatches=0`.
- Every reason is CI's `--pin-killed` text. The commit message says nothing was re-measured locally, and nothing in the rows suggests otherwise.

### (d) CI at 9c664109, settled
- `mutation` success (job 113305917181): `MUTATION TABLE PASSED`, 4652 unpinned against 4670 at base dcc77dd0, 0 survivors of 10 evaluated. The ledger agrees with the inventory, and the run is not INCONCLUSIVE.
- Also success: fast (3.14), closures, coverage, coverage-ratchet, typing, env-matrix, browser, policy-docs, pr-contract, instrument-self-tests, CodeQL, hassfest and validate-hacs.
- `delivery-status` (UNCHECKED, 76 rowed, 0 overdue) and `nightly-status` (main's scheduled run 37595831734 at be0cb82) are both main's, and the body answers them.

### Body
The Head section names 9c664109, and every red is named with its answer.

## Instrument finding (not blocking; for finding-propagation)

The pin for `pump_arbiter.py:572 RETURN_DEL` (`_silent_target`) records `killed_by: tests/structure.py`. I applied the mutant (`pass`) at 9c664109 and ran structure.py. It fails only `FAIL dead_top_level_symbols 2 > 1 (+1)`: deleting the return leaves `_inside_silent` unreferenced.

So the pin credits a structural census, not behaviour. Main's earlier pin on the same line (b8dcd2db) had `features.py` killing it with 8 failures.

The fixer applied CI's artifact faithfully, so this is not this PR's defect. It belongs to the pin chain's killer choice under `finding-propagation.md`: a RETURN_DEL whose callee becomes dead is credited to `dead_top_level_symbols`.

Evidence: /Users/timmalmstrom/hpo-seats/review-2025-r6/ev7. It holds:
- HEAD.txt
- mt_*.err and remerge_*.diff
- coord_head.py
- liquid_identity.py and liquid_identity.txt
- the artifact (zip and unzipped) and pins_vs_artifact.txt
- structure_mut_silent_target.txt
- cr_9c66.tsv and job_*.txt
- pr-body.md

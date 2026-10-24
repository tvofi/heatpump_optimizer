Fix review: blocked 3383fb2acfcfaabef1ebeb635253c8140a45ebd5 regression: a scale clamp-reset keeps the ratio solved against the out-of-bounds scale, so the lower zone lands further off than at base

bus-nonce: 25b782dfd9d50bd872ee5b39897e362b

Round: the first fix review of #2698 at this head. Measured head: `3383fb2acfcfaabef1ebeb635253c8140a45ebd5`, re-read with `git ls-remote` just before returning, and unchanged.

## Block

The body says **"Clamp means reset, consistently"**. Commit `b49602160` made the *ratio* reset solve the pair again at zero ratio confidence, because "keeping the scale solved beside the inexpressible ratio kept that ratio's share of the total". The mirror case is still open, and this diff adds it. `_reanchor_house_heat_loss_scale` (coordinator.py, the `if not HOUSE_HEAT_LOSS_SCALE_MIN <= new_scale <= HOUSE_HEAT_LOSS_SCALE_MAX` branch) handles a joint solve whose **scale** leaves `[0.3, 3.0]` in three steps:

1. it resets the scale to 1.0 and zeroes the house samples;
2. it still applies `new_ratio`, which `reanchor_heat_loss` solved jointly with the inexpressible scale;
3. it keeps the ratio's samples.

The ratio is not re-solved at zero scale confidence. At base the ratio was never re-anchored, so this path is new in this diff.

How I measured it: real coordinators over the stock two-zone house, a store the coordinator wrote, then `_async_load_thermal_learning` (`ev/scale-reset-head.txt`, script `ev/scale_reset.py`). In both rows the lower zone at the head is worse than at base, and worse than solving again with the scale's evidence void, `reanchor_heat_loss(..., (0.0, b))`. The joint solve put the scale at 0.280 and 0.279 respectively, below the 0.3 floor:

| learned state | edit (U, L) | measured lower zone | head (scale 1.000) | base, ratio kept | solved again, a = 0 |
|---|---|---|---|---|---|
| s 0.5, r 0.8, 310/147 samples | ×1.8, ×1.4 | 36.0 W/K | 128.3 W/K (ratio 1.0182) | 100.8 W/K | 40.6 W/K (ratio 0.3224) |
| s 0.4, r 1.6, 310/147 samples | ×1.5, ×1.2 | 57.6 W/K | 201.2 W/K (ratio 1.8630) | 172.8 W/K | 60.2 W/K (ratio 0.5573) |

In three more rows (`ev/scale-reset-head.txt`) a solve with zero scale confidence would reset the ratio as well, but the head keeps a ratio of 2.7116 or 1.6607 with all 147 samples.

No features check covers a scale reset beside a learned ratio. The two clamp checks the PR adds both clamp the ratio. Suggested repair: the mirror of `b49602160`, inside the pure function so `coord_footprint` stays flat. Give `reanchor_heat_loss` the scale bounds; when the joint scale leaves them, return the pair solved at confidence `(0.0, b)`, which lands at scale 1.0, together with a scale-reset flag. Pin it with a check that the ratio beside a reset scale equals the ratio from a store whose scale never learned.

## Findings

- The block above: a scale clamp-reset keeps a ratio solved against the out-of-bounds scale. This is a regression against base on the scale-reset path this diff adds. Carry: R10-RATIO-ANCHOR
- The `reanchor_heat_loss` docstring says "Path-independent". At partial confidence it is not: A->B->C gives zones 148.0/240.5 W/K and A->C gives 156.7/271.1 W/K, with 40/20 samples (`ev/attack-head.txt`). The single-zone #86 law has the same property; its old docstring said "path-independent ... at convergence", and the new wording drops that qualifier. This is wording, not behaviour, and can ride the repair push. Carry: dismissed: inherited property of the #86 law, a docstring qualifier only, repairable in the same push as the block

## Evidence

- RESULT mutation proof (step 1). Each mutant was applied in its own worktree at the head (`ev/mutant-*.diff`) and run against `tests/features.py` truncated after the #2239 section: lines 1-9001 plus `R.close`, 750 checks. The unmutated prefix printed `ALL 750 FEATURE CHECKS PASSED`. The failing check names match the body exactly:
  - A: 6 failed;
  - B: 1 failed;
  - C2: 1 failed;
  - D: 5 failed.
  - C1 was not re-run. Mutant C2 reddens the same check through the same branch.
  - I ran the prefix, not the full 4362-check suite. The full head run had not finished when this verdict was written (`ev/features-head.txt`, partial).
- RESULT finder's harness (step 2): `reparam_sites.py` from `2c42ba4a0`, sha1 `0536f495...`. Section 5 raises `TypeError` at both ends, so I deleted it, giving sha1 `e3287226...`, which matches the body. Base: `options_reseed_both_zones.upper_rel_err=0.3681`, `lower=0.2145`, `house=0.0011`, and `snapshot lower=0.2145`. Head: all 0.0000. With `--ratio 1.0` and with `--scale 1.0 --ratio 1.0`, every row reads 0.0000 at both ends (`ev/finder-harness.txt`). Every figure in the body reproduced.
- RESULT in-tree harness `dev/audit/harnesses/r10_ratio_anchor.py`, sha1 `602876e4...`, the fixer's own instrument and disclosed as such. Every base and head figure in the body reproduced, including `meter_add` going from 1.5670/1.9220 with 310/147 samples to 1.0000/1.0000 with 0/0 (`ev/intree-harness.txt`).
- RESULT law check (step 6), `ev/attack-head.txt`: 80 configurations across 4 learned states, 4 confidence pairs and 5 edits. Wherever no clamp fired, the residual against the stated law on the lower zone and the zone total is at most 1e-15, and that includes the ratio-reset rows. The only large residuals are the rows where the scale clamped, which is the block.
- RESULT class rule (step 6): `enumerate.py`. Base `R=3 S=4 A=3 F=9`, head `R=4 S=4 A=2 F=9` (`ev/enumerate.txt`), matching the body. In arm A, `cop_scale` and `solar_aperture/scale` are both dispositioned in the body (Carry #2239).
- `tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED`. The `class_excess_loc` and `max_class_loc` budgets fall by 3 each, earned by moving the law into `thermal_model.py`.
- `git merge-tree --write-tree origin/main 3383fb2acfcfaabef1ebeb635253c8140a45ebd5` (main `9586fce08`): rc 0, no conflict, and no MERGE-CLAIM lines (`ev/merge-tree.txt`).
- VERSION, the manifest version and the notes heading are untouched: pr-contract's own step printed "no version edit". The diff touches no golden or claim file, and I did not run `env_drift.py --all`.
- Head in body: `3383fb2acfcfaabef1ebeb635253c8140a45ebd5` is the head I measured.
- CI on this head, read from the check-runs API while workflows were still running:
  - Red: `tests / mutation`, predicted and answered in the body's `## Red checks` through mutation-autofix.
  - Red: `pr-contract`. It failed at the `codescan_wait.py` step while `codeql / Analyze (python)` was still in progress; its body-lint steps printed clean and `CARRY-AUDIT: 4 routed, 0 unrouted`.
  - Red: `gate`: "run(s) [40096446203] at this head are still being judged".
  - Still running: `fast`, `closures`, `coverage`, `arch-instrument`, `mutation-pins` 1-7, `instrument-self-tests`, `codeql python`.
  - Not judged, because no root-cause block may be posted before the head's workflows conclude (step 11): the red-check answers. The block above does not rest on CI.
- I did not re-run the scoped gate or the mutation table (cite CI's heavy runs).

Fix review: merge c77e7e8f97f5a3904671928720a151aa5283352b

bus-nonce: daade4ce0f4437d46c44a02fd2a42c2d
pending-ci: tests / fast (3.14), tests / coverage, tests / closures, tests / mutation-pins (1), tests / mutation-pins (2)

## Round

First round at this head (no `--reviewed-head`); review scope full.

## Findings

- Note: carry-pending: the sibling seam s1 (the two-zone valve-fed slab's series omission; the install's lower floor 20.428 / 19.864 / 19.300 at +5 / −5 / −15 C, re-taken here byte-identical at both ends) is owed a new issue filed by this pull request (`finding-propagation.md`, sibling seam); the fixer could not file it and carried it pending the orchestrator's ruling. File it at or before the merge. Carry: R11-VALVE-REFERENCE (item s1, pending orchestrator ruling)
- Note: owner-confirmation: carry 1's precondition asks for a reproduction on an install's own valve parameters from a diagnostics bundle; no committed bundle has a single-zone valved install, so the fix reproduces on R10-COMBI-TANK's install shape (`combi` row: 20.734 / 19.214 / 17.694 at e352724335, 21.000 held at the head, re-taken here). Whether that stands in for a bundle stays open for the owner, as the body carries it. Carry: R11-VALVE-REFERENCE (item dispatch-condition, pending owner confirmation)
- Residual: a reviewer mutant survives: `k_slab = p.slab_heat_transfer_floored` → `p.slab_heat_transfer` in `_valve_flow_set` passes all six new checks. It is equivalent wherever `slab_heat_transfer` ≥ 1e-6 kW/K (the property is `max(x, 1e-6)`), and below that the series term goes to 0 either way while `flow_setpoint` floors `emitter_ua` at 1e-6, so no crash and no measurable curve difference. Carry: dismissed: equivalent mutant, it differs only below the 1e-6 kW/K floor

## Evidence

- Head: `c77e7e8f97f5a3904671928720a151aa5283352b` (`ev/HEAD.txt`), re-read from the PR before writing; the body's `## Head` names it. Merge base with origin/main: 92d38ecb64. `git merge-tree --write-tree origin/main c77e7e8f97` exits 0 (tree ac9a27e3d9): no conflict.
- `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty: the contract read is current.
- `VERSION`, `manifest.json`, `RELEASE_NOTES.md` and both claim files are untouched in the three-dot diff.
- Mutation proof (`ev/mutants.txt`), each mutant applied to the head worktree, then the new block run through `features_block.py "# R11-VALVE-REFERENCE (carry 2)" "# R10-HOTFIX-SAV-ESTIMATE: the settlement books step 0"`, then restored. Unmutated: `ALL 6 FEATURES BLOCK PASSED`. The fixer's M1 to M7 all reproduce with the body's figures: M1 settles at 20.499 / 18.952 / 17.405 (3 FAIL); M2 and M3 at 23.446 (2 FAIL each, the clamp check also); M4 and M8 move the `install` digests; M5 FAILs (d); M6 and the BOOLOP `and`→`or` FAIL (c′) at 26.625 against 30.142857142857146; M7 gives a curve of 20.558 C. Reviewer mutants: M8 (free heat on two zones) is killed by the digest; M9 survives as equivalent (Findings).
- `REFERENCE_BASIS` (`ev/reference_basis_mutants.txt`, the reference-basis block with its emitted prelude): unmutated `ALL 10 FEATURES BLOCK PASSED`; 4→5 gives 2 FAIL, and 4→3 (the bump reverted) gives 3 FAIL, including the new `a month stamped 3 … states no saving` check.
- Both ends (`ev/new_block_at_base.txt`): the head's new block on the base e352724335 production tree fails 5 of 6 checks. Only (c′) passes there, as the body states. The `install` and `no valve` digests are the same literals at the base; only the `one-tank` digests differ. Held 20.662 / 19.115 / 17.568 at the base.
- Finder harness, carry 0 (`ev/held_install_base.txt`, `ev/held_install_head.txt`; the head's `r10_sav_held_install.py` against each tree): one-tank held 20.662 / 19.115 / 17.568 at the base, 21.000 at the head (plant 22.975, settled 23.000); combi 20.734 / 19.214 / 17.694 at the base, 21.000 held and 23.000 settled at the head. With the one-tank and combi lines removed, base and head are identical: `NON-SINGLE-ZONE ROWS IDENTICAL` (the null control reproduces).
- Finder harness, carry 1 (`ev/steady_seams_*.txt`, `r10_advisor_steady_seams.py fields`): only the `valve, one tank` pair differs, at 19.88 with 24 of 72 rows at the base and 21.00 with 1 of 72 at the head. Every other line is identical.
- Class (step 6): the body's enumeration rule, re-run at the head (`ev/enumeration_rule.txt`), returns 19 sites. Each is in the diff or dispositioned in the body. The two direct `flow_setpoint` calls (thermal_model.py:2519 `_valve_two_zone_delivery`, :4671 inside `if p.two_zone_enabled:` in the batch substep) are two-zone, and coordinator.py:7753 is behind the `valve_flow_needs_two_zone` hold. The rule returns more than one seam, and every seam is closed or carried (s1).
- Step 14: `structure_budgets.json` `class_excess_loc` 17407 → 17406, and `tests/structure.py` at the head reads `RESULT class_excess_loc=17406`, rc 0 (`ev/structure_head.txt`). The lowering comes from respelling `(p.mixing_valve_mode or MODE_NONE) in (THROTTLING_MODES)` as a membership test, which is semantically equal because `None` and `"none"` are both outside the set, plus a docstring that had to be rewritten for the new branch anyway. That is not gaming. No budget is raised. The two deleted ledger pins name lines this diff rewrote (`REFERENCE_BASIS = 3`, the old `q_hold` line).
- Step 16: the diff adds no refusal on an actuator write.
- Not re-derived here: the stress figures (`ALL 116 STRESS CHECKS PASSED`), the archscore `dS +0.0000`, the BLAS md5 reproduction and the full `tests/features.py` run (which covers the four respelled existing checks) are CI's heavy runs and are cited from the head's checks. My own full `features.py` run is void and not cited: I ran the `REFERENCE_BASIS` mutant in the same worktree while it was running, and it read the mutated `ledger.py`. The scoped gate's `MODE: SCOPED -- 27 script(s) run` is the body's figure.

## CI

- `merge_train.py classify c77e7e8f97f5a3904671928720a151aa5283352b --pr 3685` printed `WAIT c77e7e8f97f5a3904671928720a151aa5283352b pending: gate red: none` (rc 3) on every run from 19:51 to 20:36 UTC, about 45 minutes. The live check runs at this head still in progress: `tests / fast (3.14)`, `tests / coverage`, `tests / closures`, `tests / mutation-pins (1)`, `tests / mutation-pins (2)`. Hence the `pending-ci:` line.
- `governance / instrument-self-tests` concluded success at 20:25, which settles the packet's `introduced-red: unreadable` refusal (it was queued at render).
- Every other required context that has concluded is green: arch-score, budget-raise-gate, codeql ×3, governance env-matrix / policy-docs / wave-script, hassfest, validate-hacs, tests arch-instrument / briefs / browser / closure-scope / typing.

## Red checks

- `tests / mutation` (owed set): `MUTATION TABLE REFUSED -- 2172 unpinned site(s) against 2165 at the ratchet base 92d38ecb64, 7 of them added by this diff`, the seven sites the body's `## Unpinned sites` lists, each with a mutant killed locally. The body's `## Red checks` answers it: the cheaper detector is `ci_predict.py`, already a step of `prepr.sh`, with no standing cost to add. Reviewer-side checks: the ledger CONST and both `flow_setpoint` sites are killed above, and `mutation-pins (1)/(2)` are the autofix pinning them now (`ci-autofix.md`). The trigger is answered.
- `gate` (owed set, job 133567739690 in the edit run 43941710611): `FAIL run(s) [43941712367] at this head are still being judged; their gate decides`. This is a deferral to the push run, not a defect, and classify reads `gate red: none`.
- `tests / nightly-status` is red and outside the owed set: no answer is owed and it blocks nothing.

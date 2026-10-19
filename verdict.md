Fix review: merge 536080c084c3ea201db13860c29bcca577fac5db

bus-nonce: 61d5aad2fc2a9f02578e6d4e44875373

Round 2. Round 1 (comment 6263343957) returned `blocked carry-missing` at this same head. The code head has not moved since. The body was edited, and this round re-measures the code itself rather than carrying round 1's numbers.

- Measured head: 536080c084c3ea201db13860c29bcca577fac5db (ev/HEAD). `git ls-remote origin refs/pull/2435/head` still printed it when this verdict was written.
- Roles contract: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty at both main tips seen (c35302773 and 90557e39e), so the contract is current.

## Round 1's block is resolved

- `## Forward-carry` now reads `Carry: R10-DEAD-RATE-LIMIT`.
- That group is on origin/main in `dev/programme/rosters/wave-r10-groups.json`, with `after: [R10-TRUST-RELATIVE]`. Its first `carry` item states the control as a precondition: "Re-measure at your merge base that the rate limit cannot bind with an arm where it WOULD bind on the pre-R10-TRUST-RELATIVE base (the null control), before deleting anything" (step 10, `finding-propagation.md`).
- pr-contract job 117978195177 at this head printed:
  - `PR-BODY: 0 error(s)`
  - `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`
  - `no version edit`
  - `record red-history ... every failure conclusion across them: mutation`
- The body answers `mutation` under `## Red checks`.

## Mutation proof (step 1)

Each mutant ran in its own scratch worktree at the head with `PYTHONPATH=tests/hastub python3 tests/features.py`. `git status --porcelain` was empty after each one.

- Control, unmutated: `ALL 4215 FEATURE CHECKS PASSED`, rc 0 (ev/features_head_control.txt).
- `reach = trust_region` (the absolute bound restored): `3 of 4215 FEATURE CHECKS FAILED`, rc 1. These are the three checks the body names, with the body's values: scale 0.8999999999999999; target 2.5, bound 3.0; UA 0.40199999999999997 / 0.404 (ev/mut_absolute.txt).
- My mutant `reach = current * trust_region * 0.5`: 4 of 4215 failed (ev/mut_half.txt).
- My mutant `reach = current**0.5 * trust_region`: 3 of 4215 failed (ev/mut_sqrt.txt).
- CLAMP_DROP `target = float((target))`, the site of the new ledger pin: 4 of 4215 failed (ev/mut_drop.txt). The pin is earned.
- My first sequential mutant script was stopped at the 30-minute background limit partway through the `half` mutant (ev/mut_half.killed_partial.txt). The three remaining mutants were re-run in parallel and the results above are from that run. Nothing from the killed run is reported as a result.

## Finder's harness (step 2) and null control (step 3)

- Harness: `reseed_rolling.py` from study/r10-reseed `2c42ba4a0`, sha1 030df96abe88d7b12132798518bc92e466391d99, which matches the body.
- Run at the merge base 1bcc79884 and at this head, defaults, every run rc 0 (ev/rolling.*.txt, ev/rolling_summary.txt).

RESULT ratio_B_over_A.*_post, base -> head:

| plant | metric (base values in this order) | base | head |
|---|---|---|---|
| sz_157 | house_std / house_rmse / fc_mae | 1.0458 / 1.0215 / 1.0617 | 1.0000 on all |
| sz_060 | house_std / house_rmse / fc_mae | 0.5101 / 0.7874 / 0.8355 | 1.0000 on all |
| tz_157_192 | house_std / house_rmse / fc_mae / lower_std / lower_rmse | 0.8667 / 0.8204 / 0.8272 / 0.8831 / 0.8540 | 1.0000 on all |
| sz_null | house_std / house_rmse / fc_mae | 0.9631 / 0.9628 / 0.9653 | 1.0000 on all |
| tz_null | house_std / house_rmse / fc_mae / lower_std / lower_rmse | 0.9980 / 0.9971 / 0.9993 / 1.0006 / 1.0034 | 1.0000 on all |
| `--trust-region 1e9` (sz_157 and tz_157_192, the perturbation) | every metric | 1.0000 | 1.0000 |

What this shows:
- At the head the finding is closed: the reseed is an exact re-parameterisation.
- The harness moves under its own perturbation: with the trust region off, the base ratios also read 1.0000.
- My numbers are identical to round 1's.

Not re-derived exactly (step 8):
- The body's base-side sz_157 reads 1.0483 / 1.0227 / 1.0693 and sz_060 reads 0.5106 / 0.7799 / 0.8259.
- I get the values in the table above, and round 1 got the same values at the body's own base 768bfc0c3. No production or test file differs between the two bases.
- The gap is closed-loop floating-point drift between machines. Its direction and size hold, and the head-side figures (1.0000) reproduce exactly.
- tz_null differs from the body by at most 0.0004.

Bundle-harness figures (the owner's stores): NOT verified. This seat has no access to the bundles, and round 1 checked that harness only on a synthetic bundle. The harness is the fixer's, not the finder's.

## Remaining steps

- Step 6, class. The body's rule returns exactly the two seams it dispositions, `thermal_model.py:1938` (closed) and `:1944` (the rate limit, already relative, and carried as dead) (ev/class_rule.txt). Both call sites pass `_LEARNER_TRUST_REGION`. `_apply_*` holds current >= 0.3, so the relative reach is never 0.
- Steps 4 and 5. The three-dot diff touches no claim file, no golden fixture, VERSION, the manifest or RELEASE_NOTES (ev/version_claims.txt). CI printed `no version edit`.
- Step 7. The body's `## Head` names 536080c08, the head I measured.
- Step 13, merge check.
  - Against c35302773: `git merge-tree --write-tree` gave tree b89b798d7c239300c78b9cab37415da453b8be1b, rc 0 (ev/merge_tree.txt).
  - Main then moved to 90557e39e, which merged #2368. Against it: tree a30f96f657b25ba726fa65ad65935baa884a2df3, rc 0, with `LEDGER-MERGE: resolved tests/closures.json` (inert_reads set merge) (ev/merge_tree_latest.txt).
  - Main's newer thermal_model.py and coordinator.py hunks contain no trust, Newton, HOUSE_LOSS, LOWER_FLOOR or `_LEARNER` term.
  - GitHub cannot run that ledger driver, so it may show the PR as DIRTY. The orchestrator's main merge has to be done locally, as the body already says.
- Step 14. `dS +0.0000 NULL`. The closures.json entry classifies the new harness. The one ledger pin is earned (CLAMP_DROP killed, above).
- Step 15. A one-line local change in the one shared step, with the comments and the constant's comment updated. No breach.

## CI on this head (step 11; commit check-runs API, filter=all, ev/check_runs_all.tsv)

- Every check's latest run is completed, success or skipped. Nothing is pending.
- Earlier reds at this head:
  - validate-hacs and env-matrix: the GitHub API rate limit, as round 1 recorded. Green on re-run.
  - nightly-status: not this PR's, and green on its latest run.
  - pr-contract: rate limit, then round 1's UNROUTED carry. Every pr-contract run from 09:03Z on is green, and those runs started after the last red concluded.
- `mutation` is green at this head, and its earlier red (at ebeda1c0d) is answered in `## Red checks`.

Reviewer-built instruments: none beyond scratch sed mutants, and a script that ran the finder's harness at both trees.

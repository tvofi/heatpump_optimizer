Fix review: merge 9e212cd0e3687575e764517916f5057d79c8e01a

bus-nonce: 2487dee5866579c3b064cbff49fa6ab6

Round 2 (delta review) of PR #2834, R10-ADVISOR-RESIDUE. Measured head `9e212cd0e3687575e764517916f5057d79c8e01a`, still the PR head by `git ls-remote` when this verdict was written. Round 1 was MERGE at `313a19d91` (probe/rev-2834-9895de2a). This round judges only the delta `313a19d91...9e212cd0e`. `dev/governance/roles/` matches origin/main.

## Findings

- Seam (a) is still open at the Plan page's what-if panel, unchanged from round 1. The `whatif` arm, re-run at the head, gives `null 00:00 target_plus_1 plan by start +255.2 +150.9 +123.2 spread 132.0`, and the settled figure has the wrong sign across schedules (`varying 00:00 target_minus_1 … settled +24.6`, `target_plus_1 … settled -25.5`). The body keeps `Part of #2257`, which is consistent with that. The roster at origin/main `5fb833930` (group R10-ADVISOR-RESIDUE, carry index 9) records that the next sub-PR owns the panel, closes #2257, and keeps the group open after this merge. This settles round 1's no-owner finding. Carry: #2257

## Evidence

Brief item 1, the two `_sweep_price` sites refused at `e2a808a6`. Each mutant was run in its own detached worktree at the head, under `PYTHONPATH=tests/hastub python3 tests/features.py` (ev/mut-*.diff, ev/mut-*.summary):
- CLAMP_DROP (`max(abs(level), 0.1)` -> `(abs(level))`): `1 of 4439 FEATURE CHECKS FAILED`, rc 1. The red check is `a free-energy day, and one at the floor's bound, still rank a hotter tank as the dearer one`, with detail `0.0/kWh [0.0 ×7]`.
- CMP_BOUND (`level > 1e-6` -> `level >= 1e-6`): `1 of 4439 FEATURE CHECKS FAILED`, rc 1. The same check is red, with detail `0.0/kWh [0.87 … 1.23]; 1e-6/kWh [0.0 ×7]`.
- Unmutated head: `ALL 4439 FEATURE CHECKS PASSED`, rc 0.
- Both mutants are killed by a named check, and both `killed_by` pins (`3f0ce95ba`) name `tests/features.py`.
- The body reports `2 of 4439` per mutant. The second red there is the `#363` recorded_at check, which the body attributes to its `git archive` copy. My git worktrees do not show that red, and that agrees with the body's explanation.

Brief item 2, the `Closes #2257` premise. It does not hold at this head. The PR body reads `Part of #2257` (intro and Carries item 10) and has no `Closes` keyword. So there is no premature close to judge. Seam (a) is listed under Findings.

Brief item 3, everything else equals round 1:
- custom_components. The added and removed lines of `git diff c9cbe6b45...313a19d91 -- custom_components` and `git diff ed1c9045e...9e212cd0e -- custom_components` are identical. The delta adds no production line.
- The branch's own non-merge commits since round 1 are: `b2946cd12` (the one features.py check), `3f0ce95ba` (two killed_by pins), `f77f0e4cc` (the bot's eight pins) and `e01608bdd` (a single comment line in claimed_drift.txt, giving the measurement base). The other commits are merges of main.
- VERSION (7.0.4), manifest.json and RELEASE_NOTES.md: the three-dot diff against `ed1c9045e` is empty.
- `tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED`. The three-dot diff of `structure_budgets.json` only lowers values (`class_excess_loc` 18086 -> 18085, `max_class_loc` 8241 -> 8236). No budget rises.
- `env_drift.py --all ed1c9045e…` at the head prints `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56`, rc 0 (ev/structure-envdrift-head.log). The claim file holds the five coord_* claims (`data.recent_kwh_price`), and `card_claimed_drift.txt` is byte-identical.
- The head named in the body equals the measured head `9e212cd0e`.
- `git merge-tree --write-tree origin/main(5fb833930) 9e212cd0e` gives rc 0, tree `e83dc14db` (ev/merge-tree.txt).

CI on the head, from the check-runs API (ev/checkruns-head.txt, 55 runs):
- All runs are completed, each as success or skipped.
- These all report success: `tests / mutation`, `pr-contract / pr-contract` (both runs), `gate` (both runs), `governance / delivery-status`, fast, typing, closures, replay, browser, coverage, instrument-self-tests and codeql.

Red checks at `e2a808a6`, from the check-runs API (ev/checkruns-e2a808a6.txt):
- The failures are `gate`, `pr-contract / pr-contract`, `tests / mutation` and `governance / delivery-status`.
- Each one appears in the body's `## Red checks` with a cause and a cheaper detector (`mutation_table.py --pin-killed` before handoff, `prepr.sh --body-check` after CI). For `delivery-status`, the body states it is not a required context and is other PRs' OVERDUE rows.
- No body entry lacks a real check-run.

Harness `whatif` arm (dev/audit/harnesses/r10_advisor_residue.py) at the head, rc 0 (ev/whatif-head.log):
- `rows 24 plan_moves_by_start 24 held_moves_by_start 0`
- `caps rows 12 spread_by_start mean plan 50.4 settled 10.1; … plan 18/36 settled 1/36`
- Both lines are identical to the body and to round 1.

**Source:** the owed trigger-2 RCA for #1721 in [RCA-BULK-3.md](https://github.com/tvofi/heatpump_optimizer/blob/handoff/audit-r9-alt/handoff/round9/state/alt/rca/RCA-BULK-3.md) §1. PR #1721's own "Red checks" section said the cheaper detector was "owed to a root-cause seat", and none had been conducted. Measured at origin/main `3490cb16`. The demonstration is in [rca/bulk3/demo_1721.txt](https://github.com/tvofi/heatpump_optimizer/blob/handoff/audit-r9-alt/handoff/round9/state/alt/rca/bulk3/demo_1721.txt).

## What

#1715 (F11.3, `87d780c7`) made `counts.mjs`'s ruleset comparison compare every leaf against a fixture recorded from an **admin** read, which carries `bypass_actors`. CI reads the ruleset as the Actions `GITHUB_TOKEN`, and GitHub omits that field for that token.

#1715's own PR stayed green because `governance.yml` restores the pinned `.claude/workflows/*.mjs` from the base, so its checks ran the old comparator. The new comparator first ran on the push to main. Main was red for 2 h 21 m on `policy-docs`, `env-matrix` and `pr-contract`, which took a hotfix PR (#1721) and the v6.7.7 stamp.

**Process state: (c).** Two processes existed and were obeyed:
- RC1's `prepr.sh` head-copy runs use the seat's own identity, never the Actions token.
- `graders-head-copy` runs the PR's own copy of a grader, but only for `coverage_ratchet` and `delivery_status`.

**Demonstration** (`field_coverage.mjs --only ruleset --ruleset-json`):

| tree | admin view (null) | Actions view |
|---|---|---|
| `87d780c7` | read=40, refused=0 | **REFUSED** ("unperturbed, is already red") |
| `8b61aed3` | read=40, refused=0 | read=37, refused=0 |

## Cost test

- 1 escape in 12 releases; 141 min of red main, about 11.8 min per release.
- The arm costs about 70 s of runner time per release and 0 s on the critical path.
- **It passes, about 10×.**

## Fix shape (R9-F11.7)

- Add a governance step to `graders-head-copy`: when the three-dot diff touches `.claude/workflows/**`, run the PR's own `policy_lint.mjs` and `field_coverage.mjs` under the read-only `GITHUB_TOKEN`.
- Non-required, like the existing job. `tests.yml` is code-owned, so it merges on tvofi's review.
- **Demonstration owed by the fixer:** red on a branch whose `counts.mjs` is reverted to `87d780c7`, green at main.
- **Class:** P11 (an oracle recorded from a different principal); an instrument-side member.

## Disposition

Scheduled: **R9-F11.7**, after R9-F11.5.

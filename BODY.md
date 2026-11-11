Triage batch 169 records one orchestrator ruling made under mandate 6715477401. It holds one ruling.

- **P584, ACCEPT: SELFTEST-SCOPE-UNION.**
  - Main `a7628041dc` is red on `governance / instrument-self-tests`, step `drift`, with 6 UNDER-SCOPED refusals. The ruling builds a new hotfix group, R10-HOTFIX-SELFTEST-SCOPE-UNION (size S, opus), in two parts.
  - Part 1 adds the 6 measured misses to `tools/ci/selftest_closures.json`.
  - Part 2 is the class barrier: `record` unions instead of replacing, a pre-merge detector for a read added without its table entry, and a measured decision on running the step on pull_request.

The diff is one file against the merge base: `dev/programme/triage/s6-batch169.md`, the ruling. No product behaviour changes.

## Head

`e6a0a049e6faf2f54dea1ef58ee6b235090b3077`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P584 as ACCEPT, and a citation of P584 passes (`None`).
- With P584's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P585 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat a7628041dc...e6a0a049e6faf2f54dea1ef58ee6b235090b3077`: 1 file, 1 commit.
- The figures are static reads at main `a7628041dc` and the job log of 130352715261, as diagnosed by the orchestrator's main-red seat.

## Red checks

`governance / instrument-self-tests` is red at the merge base `a7628041dc`. That red is main's own, and this ruling routes its fix. This one-file record does not touch it.

## Forward-carry

none

## Friction

none

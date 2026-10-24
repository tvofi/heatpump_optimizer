**Record beat — R10 s5, main `144fb4f90`** (state change: ten merges, CI cut-over)

Merged since the last record (`gh pr view <N> --json state,mergeCommit`):

- [#2669](https://github.com/tvofi/heatpump_optimizer/pull/2669) `5c9828fe5` R10-POLICY-LINT-FAMILY
- [#2664](https://github.com/tvofi/heatpump_optimizer/pull/2664) `811cd01aa` R10-FLY-RELAY-REVIEW-FF
- [#2670](https://github.com/tvofi/heatpump_optimizer/pull/2670) `d7cb63508` proposal-triage rulings, batch 1 (P5–P33)
- [#2668](https://github.com/tvofi/heatpump_optimizer/pull/2668) `25816d5eb` R10-FLY-NO-FOOTERS-PUSH-PATHS
- [#2672](https://github.com/tvofi/heatpump_optimizer/pull/2672) `f046076ad` proposal-triage rulings, batch 2 (P34–P41)
- [#2653](https://github.com/tvofi/heatpump_optimizer/pull/2653) `c93a46951` record autofix, 20 merges
- [#2676](https://github.com/tvofi/heatpump_optimizer/pull/2676) `f8cc41ab0` record autofix, #2653
- [#2671](https://github.com/tvofi/heatpump_optimizer/pull/2671) `6120fb513` R10-ORCH-LEDGER
- [#2673](https://github.com/tvofi/heatpump_optimizer/pull/2673) `b927f431a` R10-CI-LAYOUT-P2b — **CI cut-over**
- [#2679](https://github.com/tvofi/heatpump_optimizer/pull/2679) `144fb4f90` record autofix, #2671 #2673 #2676

**CI cut-over.** Ruleset 23698884's `required_status_checks` now lists exactly `["gate"]` (`gh api repos/tvofi/heatpump_optimizer/rulesets/23698884`). A pull request's mergeability is decided by the `gate` context alone; a seat reading the old per-job contexts as required is reading a retired contract.

**State docs.** `tools/audit/seat/state_docs.py --push` from a detached worktree at `144fb4f90`: `already current: handoff/audit-r10-plan at ce577fb7447a` — nothing pushed; the ref already carries this tip's three docs.

**Delivery rows.** `dev/programme/delivery/<N>.md` exists at `144fb4f90` for all ten. Nine read `merged <sha>`; [#2679](https://github.com/tvofi/heatpump_optimizer/pull/2679)'s own row reads `**open**` although GitHub reports MERGED — the unreconciled-word gap `delivery-status-tracking.md` names; the next record autofix owes its upgrade.

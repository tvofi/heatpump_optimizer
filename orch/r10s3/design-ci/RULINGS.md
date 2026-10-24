# R10-CI-LAYOUT owner rulings (mandate 6175172275)

tvofi, 2026-10-18: "yes, take it under the mandate". These rulings apply once the design review approves. A revise item overrides a ruling here and comes back for a new ruling.

- D-1: record-autofix moves out of the Tests push run. Acceptance: a unit test proving the tick still sees its failures.
- D-2: arch-score joins gate_required when the diff reaches custom_components/.
- D-3: keep the merge_group trigger.
- D-4: drop the C1 composition in PR 1, if the design review confirms its proof is covered elsewhere.
- D-5: keep CodeQL's O17 stand-down, with the extracted-files soundness check.
- Variant: the review is an event of ci.yml. Acceptance: a pull_request_review event re-runs only budget-raise-gate and gate (proved by a run's jobs list).

## R-10 (2026-10-19, under mandate 6175172275; R10 owner grant "decisions = recommended")
Option B: pr-contract lists open code-scanning alerts of the matched analyses (refs/pull/N/merge at the carried code run); 4.3 step 5 (LAG_MAX wait) dropped; U6 must show a planted python-only finding listed in --red on the probe PR. Source: probe/design-ci-rev3 8bd4e68f DESIGN-P2 "R-10 owner question".

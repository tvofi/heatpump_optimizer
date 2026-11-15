Group: R11-PRE-ROUND-CHECK-GATE (topic r11-pre-round-check-gate)

## Head

`6f4b8cd7b729316f4ed9fa0f7bf26f6cdaea2d14` is this PR's head.

## Red checks

none

## Forward-carry

- Part 2, the group half of the P3 listing, is ruled by the orchestrator as this group's second pull request (topic r11-pre-round-check-gate-p2). It needs no finder start, only the end of the finders. It adds a boolean `gates_finders` on a roster group, read through roster_lib, linted by brief_lint and set by a roster_edit op. `--open-cards` gains `open_groups` (the open groups whose `gates_finders` is not true). A group with no `gates_finders` is listed and flagged `UNMARKED <group>`, and the listing exits non-zero while any open group is unmarked, so no group drops out of P3 unseen. Part 2 also builds the refusal in `audit-plan.js` of a plan that leaves an open card or group in no group. No roster group carries a structured finder-critical fact today, which is why part 1 lists cards only. Carry: R11-PRE-ROUND-CHECK-GATE


## Friction

none

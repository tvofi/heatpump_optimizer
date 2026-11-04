Triage batch 122 records one ruling, P387, on the root-cause seat's meter band for the published savings row, under the owner's ruling that the reference assumes no wood.

- **P387: ACCEPT narrowed.** The band's ceiling is rejected, because wood can raise booked over metered without limit (`wood-full` 7.70, sound). The floor is accepted as a new group, R10-SAV-METER-FLOOR, because wood cannot lower that ratio and the floor fires on November's 0.188. It catches 1 of the 3 measured instances, and the ruling says so.
- **A finding for the hotfix:** calibration cancels metered kWh on the published row, so heat the plan did not foresee earns no saving. Carried to R10-HOTFIX-SAV-ESTIMATE before it merges.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. The new group and the two carries are held for the orchestrator to route through `roster_edit.py`.

## Head

`b220737af92e693a782b9af6d80b9ae3a0b7c0d7`; the one file is the whole diff against `783d8dc72811ab75ae4ffca367456f44896f47d3`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P387 `ACCEPT`, and the three cited texts are not refused.
- With the verdict flipped to DEFER, the carry text is refused: `is not an ACCEPT ruling (DEFER)`.

## Null control

- P388 reads `None`: no such entry.
- With the file absent, the carry text is refused: `the triage ruling dev/programme/triage/s6-batch122.md is not on the roster branch or origin/main`.

## Figures

- `git diff --stat 783d8dc72811ab75ae4ffca367456f44896f47d3...b220737af92e693a782b9af6d80b9ae3a0b7c0d7`: 1 file changed, 93 insertions(+).
- The ruling's figures are cited beside their sources in its `Instances:`. Those read from the fix seat's work-in-progress commit are provisional, and the group's acceptance re-measures them.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none

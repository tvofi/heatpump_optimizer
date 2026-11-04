Triage batch 122 records one ruling, P387, on the root-cause seat's meter band for the published savings row, under the owner's ruling that the reference assumes no wood.

- **P387: ACCEPT narrowed.** The band's ceiling is rejected, because wood can raise booked over metered without limit (`wood-full` 7.70, sound). The floor is accepted as a new group, R10-SAV-METER-FLOOR, because wood cannot lower that ratio and the floor fires on November's 0.188. It catches 1 of the 3 measured instances, and the ruling says so. The arm table is corrected to the fix seat's re-take at `39143c38f`; the ratios did not change.
- **A finding for the hotfix, now answered:** calibration cancelled metered kWh on the published row, so heat the plan did not foresee earned no saving. The fix's wood floor answers it on wood-configured rows.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. The new group and the two carries are held for the orchestrator to route through `roster_edit.py`.

## Head

`99a6db4a827bebdb295845462db8b513ce2e0707`; the one file is the whole diff against `783d8dc72811ab75ae4ffca367456f44896f47d3`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P387 `ACCEPT`, and the three cited texts are not refused.
- With the verdict flipped to DEFER, the carry text is refused: `is not an ACCEPT ruling (DEFER)`.

## Null control

- P388 reads `None`: no such entry.
- With the file absent, the carry text is refused: `the triage ruling dev/programme/triage/s6-batch122.md is not on the roster branch or origin/main`.

## Figures

- `git diff --stat 783d8dc72811ab75ae4ffca367456f44896f47d3...99a6db4a827bebdb295845462db8b513ce2e0707`: 1 file changed, 96 insertions(+).
- The ruling's figures are cited beside their sources in its `Instances:`. Those read from the fix seat are not re-run here, and the group's acceptance re-measures them.
- No capped file is touched; the diff is one markdown file.

## Red checks

- `tests / ci-ratchet` and `tests / nightly-status` read red in this ref's ancestry, at the base `783d8dc72`, whose `gate` also failed. Neither comes from this diff, which is one markdown file under `dev/programme/triage/` that neither check reads. No cheaper detector is owed here: the red is the base's, and this ref has no pull request and no checks of its own.

## Forward-carry

none

## Friction

none

Triage batch 123 records one ruling, P388, on a pre-flight park that cannot rejoin the live train at the same verdict after its cause is cured.

- **P388: ACCEPT, already owned.** R10-TRAIN-MERGE-LOOP carry 3 holds the item. One carry widens its instances to 6 of the 9 same-verdict refusals in the train log and sets the form: re-run the pre-flight read at the add rather than add a class to `READMIT_SAME_VERDICT`, because `admit_add` has no `findings` rule.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. The carry is held for the orchestrator to route through `roster_edit.py`.

## Head

`7f56ffb03e46c8adadaf08bc3575c3a9648a445d`; the one file is the whole diff against `783d8dc72811ab75ae4ffca367456f44896f47d3`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P388 `ACCEPT`, and the carry text is not refused.
- With the verdict flipped to DEFER, the carry text is refused: `is not an ACCEPT ruling (DEFER)`.

## Null control

- P389 reads `None`: no such entry.
- With the file absent, the carry text is refused: `the triage ruling dev/programme/triage/s6-batch123.md is not on the roster branch or origin/main`.

## Figures

- `git diff --stat 783d8dc72811ab75ae4ffca367456f44896f47d3...7f56ffb03e46c8adadaf08bc3575c3a9648a445d`: 1 file changed, 42 insertions(+).
- The ruling's figures are cited beside their sources in its `Instances:`.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none

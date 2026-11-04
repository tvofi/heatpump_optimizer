Triage batch 125 records one ruling, P390, on a body lost when `body_push.sh` refuses in a cloud seat, and on the frugal guard in the cloud env.

- **P390: ACCEPT narrowed.** R10-BODY-CONTRACT takes one carry: `body_push.sh` keeps a refused body on its own orphan ref. The proposed push to `handoff-wip/<topic>` would put the body in the code's ancestry. Disabling the guard was DEFER as the owner's call; the owner then ruled "Turn it off in the cloud" (2026-11-04), which the entry records, routed to R10-FLY-CLOUD-FRUGAL-OFF.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. The carry is held for the orchestrator to route through `roster_edit.py`.

## Head

`03f7d25c19b39cbd02e317286197483117473fe3`; the one file is the whole diff against `086a59da409fc634bfbf7882c97367cf2ad8bc5f`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P390 `ACCEPT`, and the carry text is not refused.
- With the verdict flipped to DEFER, the carry text is refused: `is not an ACCEPT ruling (DEFER)`.

## Null control

- P391 reads `None`: no such entry.
- With the file absent, the carry text is refused: `the triage ruling dev/programme/triage/s6-batch125.md is not on the roster branch or origin/main`.

## Figures

- `git diff --stat 086a59da409fc634bfbf7882c97367cf2ad8bc5f...03f7d25c19b39cbd02e317286197483117473fe3`: 1 file changed, 35 insertions(+).
- The ruling's figures are cited beside their sources in its `Instances:`.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none

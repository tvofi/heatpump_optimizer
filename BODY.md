Triage batch 121 records one ruling, P386, on the owner's directive of 2026-11-04 that a fixer's prepr is not repeated at pull-request open or update, filed in the queue as P377.

- **P386: ACCEPT, routing and form only.** R10-HANDOFF-PATH already holds the item as carries 3 and 4. It moves to the front of the queue with part 1 cut to this reuse. The form is a receipt from the fixer's own prepr, a fail-closed `app_push.sh --reuse` verdict, and the merged-tree checks kept, including `tests/structure.py` and `ci predict`.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. The carry and the `set-files` op are held for the orchestrator to route through `roster_edit.py` once this file is on the roster branch or main.

## Head

`5996dcf63390265662bf2f9fe48ad527252d5bef`; the one file is the whole diff against `2a9cd3476`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P386 `ACCEPT`, and the carry text is not refused.
- With the verdict flipped to DEFER, the carry text is refused: `is not an ACCEPT ruling (DEFER)`.

## Null control

- P387 reads `None`: no such entry.
- With the file absent, the carry text is refused: `the triage ruling dev/programme/triage/s6-batch121.md is not on the roster branch or origin/main`.

## Figures

- `git diff --stat 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e...5996dcf63390265662bf2f9fe48ad527252d5bef`: 1 file, 124 insertions.
- The ruling's figures are cited beside their sources in its `Instances:`.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none

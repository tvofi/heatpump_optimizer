Triage batch 118 records one ruling, P382, on the orchestrator's message of 2026-11-04 proposing a cloud seat escalation ref.

- **P382: ACCEPT, narrowed.** The `escalate/<topic>` ref family is refused, because the question already reaches origin as `BLOCKED.md` on `handoff-wip/<topic>` and nothing reads it. One carry on R10-TICK-LEVELS adds the reader, stops two arms reading that push as healthy, and adds one sentence to the fixer brief.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. The carry is held for the orchestrator to route through `roster_edit.py` once this file is on the roster branch or main.

## Head

`9526e320bf1d8242b22a511a6a030ca6fc4025a7`; the one file is the whole diff against `d7582ed40`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P382 `ACCEPT`, and a text citing `s6-batch118.md#P382` is not refused.
- With the verdict flipped to DEFER, the citing text is refused: `is not an ACCEPT ruling (DEFER)`.

## Null control

- P383 reads `None`: no such entry.
- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch118.md is not on the roster branch or origin/main`.

## Figures

- `git diff --stat d7582ed40...9526e320bf1d8242b22a511a6a030ca6fc4025a7`: 1 file.
- The ruling's figures are cited beside their sources in its `Instances:`.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none

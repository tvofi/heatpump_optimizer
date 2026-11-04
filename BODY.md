Triage batch 116 records one ruling, P378, on the orchestrator s10's message of 2026-11-02, about 20:30Z.

- **P378: DEFER (LOG).** The dispatch seat lists already-fired payloads as fire-owed. The FIRE-OWED tick level of R10-TICK-PR-BUCKETS already owns the item, with the payload-file key from `s6-batch115.md#P375`. No carry, no group and no policy edit.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`df0c264cccbe2a9777e7c1c016619c2a044a84b7`; the one file is the whole diff against its merge base with main, `b8e823699`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P378 `DEFER`. A text citing `s6-batch116.md#P378` is refused: `is not an ACCEPT ruling (DEFER)`.

## Null control

- P379 reads `None` in this file: no such entry.
- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch116.md is not on the roster branch or origin/main`.

## Figures

- `git diff --stat b8e823699...df0c264cc`: 1 file, 69 insertions.
- The ruling's figures are cited beside their sources in its `Instances:`.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none

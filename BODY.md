Triage batch 116 records one ruling, P378, on the orchestrator s10's message of 2026-11-02, about 20:30Z.

- **P378: DEFER (LOG).** The dispatch seat lists already-fired payloads as fire-owed. The FIRE-OWED tick level of R10-TICK-LEVELS owns the item, since R10-TICK-PR-BUCKETS was absorbed into it, with the payload-file key from `s6-batch115.md#P375`. No carry, no group and no policy edit.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`a7b0e93f0ff8e989985688e790cfa52eb87c9f58` adds one commit to the previous head `b2499f12d1cb100b36a1820717fbf623566ebd24`, answering verdict `blocked` `owner-stale`: it changes only `dev/programme/triage/s6-batch116.md`. The ruling's owner and condition now name R10-TICK-LEVELS; its verdict is unchanged. The authored code head before this repair is `df0c264cccbe2a9777e7c1c016619c2a044a84b7`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P378 `DEFER`. A text citing `s6-batch116.md#P378` is refused: `is not an ACCEPT ruling (DEFER)`.

## Null control

- P379 reads `None` in this file: no such entry.
- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch116.md is not on the roster branch or origin/main`.

## Figures

- `git diff --stat d7582ed40...a7b0e93f0ff8e989985688e790cfa52eb87c9f58`: 2 files, this ruling and the pull request's delivery row.
- The ruling's figures are cited beside their sources in its `Instances:`.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none


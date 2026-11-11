Triage batch 194 rules P616, P617 and P618 (queue lines 294-296, the cloud fixer's stop record), 2026-11-11. All three land on R10-RELAY-NOBODY-STALL, which is queued and has no fixer yet.

- **P616, ACCEPT narrowed: PREPR-SKIP-CLOSURES-IN-PROMPT.** The owner's standing ruling goes into `cloud_dispatch.py`'s rendered fixer text, inside P617's STOP-TO-BLOCKED carry.
  - 197 of 1,240 dispatch commits since 11-04, over 49 of 202 topics (24%), already carry it by hand, and the template names it nowhere.
  - The prepr interpreter-probe arm is rejected. The cloud closures failure has at least two shapes: a throwaway_git `git init` exit 128, and the R10-RCA-CLOUD-ENTITIES-ENV shape B misdiagnosis. A homeassistant probe keys on neither.
- **P617, ACCEPT: the R10-RCA-FIXER-NOBODY-STALL countermeasures.** C1 (route every cloud stop to BLOCKED.md; `cloud_dispatch.py:236` and `:363` route it to a result nobody reads) and C2 (`keep_refused` writes REFUSAL.txt and the fold arm reads it) become carries.
  - C2 supersedes P611's indent-regex arm. The group goes from S to M, after R10-REVIEW-DISPATCH-RESIDUE, and the RCA lands with it.
  - Re-measured: `tick-loop.log` owes carry-folds for 65 topics against 6 folded.
  - Together the two cover 32-58 of about 96 stalls a week (33-60%), each 125-196 min silent against a healthy 10.
- **P618, DEFER the turn-end prompt line; REJECT FRUGAL_ALLOW_INLINE.** One session log, and that session was not silent. The frugal setting reverses the owner's directive rendered at `cloud_dispatch.py:137-141`. The line re-opens if two of three read SILENT sessions ended a turn on a background job.

The diff is one file against the merge base: `dev/programme/triage/s6-batch194.md`, the ruling. No product behaviour changes.

## Head

`ed9c2a421ed938edf40dd2899c6e70da96ff488b`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P616 and P617 as ACCEPT, and citations of each pass (`None`). It reads P618 as DEFER, and a citation of P618 is refused as "not an ACCEPT ruling (DEFER)".
- With the verdict flipped to REJECT in the file text, the P616 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P619 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat ee64358be7...ed9c2a421ed938edf40dd2899c6e70da96ff488b`: 1 file, 1 commit. `tests/layout.py --guard`: 0 refusals.
- The figures come from the dispatch and handoff-wip refs fetched by the root-cause seat, the relay's `tick-loop.log`, `cloud_dispatch.py`, `cloud_relay.sh` and `body_push.sh` at `ee64358be7`, and the roster at `9e1a9d5395`, as cited in each ruling.

## Red checks

none

## Forward-carry

none

## Friction

none

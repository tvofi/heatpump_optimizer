Triage batch 117 records three rulings, P379 to P381, on the orchestrator's queue lines of 2026-11-04T16:45:50Z. The queue filed them as P372 to P374, numbers that already name other rulings on main, so they take the next free numbers. It opens early, under the 8 to 10 size, because P381's carry bears on #3200's repair round.

- **P379: DEFER.** A hotfix path for red main. CI priority is owned by R10-CI-PRIORITY-PAUSE. The prepr half is unmeasured, and `prepr.sh --body-check` already answers the one retry the filer classified.
- **P380: REJECT.** Classifying main's red in merge-train admission. The refusal it answers does not occur on default flags: 0 `nothing more lands` lines, 14 logged and passed. A `ci-ratchet` red runs only on a main push and cannot reach an entry.
- **P381: ACCEPT, narrowed.** One carry on R10-TICK-LEVELS: BODY-AHEAD clears on a ledger disposition, because `body_patch.sh` does not move a head. The refire itself is a one-line defect in the session-local wake loop, which stays with the orchestrator.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. The carry is held for the orchestrator to route through `roster_edit.py` once this file is on the roster branch or main.

## Head

`01df01e4881c6b939bc08a9c58874020acb3350e`; the one file is the whole diff against `d7582ed40`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P379 `DEFER`, P380 `REJECT` and P381 `ACCEPT`. A text citing `s6-batch117.md#P381` is not refused.
- A text citing `#P379` is refused: `is not an ACCEPT ruling (DEFER)`. One citing `#P380` is refused: `is not an ACCEPT ruling (REJECT)`.

## Null control

- P382 reads `None`: no such entry.
- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch117.md is not on the roster branch or origin/main`.

## Figures

- `git diff --stat d7582ed40...01df01e4881c6b939bc08a9c58874020acb3350e`: 1 file.
- The per-ruling figures are cited beside their commands in each entry's `Instances:`.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none

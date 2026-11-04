Triage batch 119 records one ruling, P383, on session 11's owed proposal that a liveness check read a loop whose cwd directory is gone as DEAD.

- **P383: ACCEPT, narrowed.** One carry on R10-CLOSEOUT-CLEANUP applies `worktree_gc.sh`'s existing `cwd_inside` guard to every removal arm. One carry on R10-FLY-STANDING-CONTRACTS part 3 adds a `loop-cwd` digest row for long-lived loops outside the job table. The hook edit stays local to the orchestrator.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. The two carries are held for the orchestrator to route through `roster_edit.py` once this file is on the roster branch or main.

## Head

`debc62a56b798f3cd5f3d72180bba429465a5cc4`; the one file is the whole diff against `d1e7dbbbb`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P383 `ACCEPT`, and neither carry text is refused.
- With the verdict flipped to DEFER, the citing text is refused: `is not an ACCEPT ruling (DEFER)`.

## Null control

- P384 reads `None`: no such entry.
- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch119.md is not on the roster branch or origin/main`.

## Figures

- `git diff --stat d1e7dbbbbe3339de86f4651fdbd97d00a12716b2...debc62a56b798f3cd5f3d72180bba429465a5cc4`: 1 file, 163 insertions.
- The ruling's figures are cited beside their sources in its `Instances:`.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none

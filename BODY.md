Triage batch 90 rules two of the orchestrator s8's slip proposals of 2026-10-31. Both route to R10-FLY-TICK-APPROVAL-OWED, the group that owns the tick's verdict-level lines. This is the next rolling batch after batch 89, with two rulings and two held roster ops.

- **P327: ACCEPT as already ruled.** Six PRs (#3022 HOTFIX, #3029, #3030, #3031, #3033, #3034) had merge verdicts at their head in BLOCKED/REVIEW_REQUIRED and no level line, because the train posts the approval itself.
  - This is P294 (`s6-batch64.md`), whose `APPROVAL-OWED` arm and `UNLEVELLED` catch-all are this group's whole brief. The group was ruled on 2026-10-30 and never dispatched.
  - The carry adds the instances and a priority note: dispatch ahead of every other instrument fly-in, without waiting for the carry to land.
  - It keeps P294's name `APPROVAL-OWED`, whose action is to queue the PR for the train. MERGE-READY means the approval already exists.
  - REJECTED: a `(needs tvofi)` suffix. That is a per-PR files read for a stop the train already names.
- **P328: ACCEPT narrowed.** #3027's cloud reviewer died in setup and sat unflagged for 5 h 15 min.
  - The new arm is git-only: `REVIEW STALLED: #N <head8> <minutes>m` when the bus dispatch record holds the current head, no verdict names it, and the reviewer dispatch ref is more than 90 minutes old.
  - Measured over 231 dispatches, the latency to the first verdict is p50 17 min and p95 70 min. At 90 min the line flags 6 (2.6%). The filing's 45 min would flag 34 (15%).
  - REJECTED: reading the RemoteTrigger run log, which P280 already rejected because the tick has no session API.
  - This arm must not delay P327's APPROVAL-OWED arm.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`960606581c6ab0cce20a3fc511a3003399d97cdb`; the file is the whole diff against `cabfaadc3`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P327 and P328 as `ACCEPT`. `triage_refusal` passes both carries, which cite `triage: dev/programme/triage/s6-batch90.md#P327` and `#P328`: it returns None.
- With P328's verdict changed to `REJECT`, its carry is refused: `dev/programme/triage/s6-batch90.md#P328 is not an ACCEPT ruling (REJECT)`. The same change on P327 refuses its carry.

## Null control

- With the file absent, the citations do not resolve, and the gate refuses them as not on the roster branch or origin/main. Both carries, appended to the live roster's R10-FLY-TICK-APPROVAL-OWED, give `brief_lint.mjs` `TOTAL: 0 error(s)`.

## Figures

- `tools/audit/seat/orchestrator_tick.py` at `cabfaadc3`:
  - line 554: the `gh pr list --json` fields carry no `reviewDecision`;
  - line 689: MERGE-READY requires `ms in ("CLEAN", "UNSTABLE")`;
  - line 712: `_dispatched` reads the bus dispatch record.
- `git ls-remote origin 'refs/heads/dispatch/*'` shows 232 `reviewer-<N>-<sha8>` refs and 100 `reviewer-rev-<N>` refs, `cloud_dispatch.py` `dispatch_ref`'s current form.
- Latency from each `reviewer-<N>-<sha8>` ref's commit to the first later `Fix review:` commit on `verdict/<N>`, n = 231: p50 17, p75 32, p90 56, p95 70, max 959 min. 34 of them took 45 min or more, 21 took 60 or more, 6 took 90 or more and 4 took 120 or more.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none

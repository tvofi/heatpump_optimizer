Triage batch 102 rules two items that the orchestrator s9 sent on 2026-11-01, both from #3080's park by the train: a queue proposal on `carry_audit`, and four held carries aimed at a done group. This is the rolling batch after batch 101, which was pushed first and left at its head.

- **P358: ACCEPT, narrowed to part (1), as one carry on R10-BODY-CONTRACT; part (2) REJECTED.**
  - **The defect.** `carry_audit`'s `seg_dests` reads `Carry: G | dismissed: <reason>` as G alone and stops at `dismissed:`. So a dismissed verdict note whose pointer group is done parks the PR. #3080's item bd9082e1 is the instance.
  - **How common the form is.** The bus's local verdict store holds 50 such markers in 11 PRs.
  - **The change.** About 5 lines and four self-test arms: read the form as a dismissal whose pointer may name any roster group.
  - **Why part (2) is rejected.** Part (2), a later body `Carry:` superseding a verdict's destination, lets an author override the reviewer's routing, which is a policy change. No instance of it has been measured, and part (1) alone clears #3080.
- **P359: ACCEPT. R10-FLY-TRAIN-DEFAULTS is not reopened.** Its four held carries (`census-3`, `strand-31`, `strand-32` and `strand-60`) go verbatim to R10-TRAIN-MERGE-LOOP.
  - **The group's state.** It is done at #3010. Its part 2 is #3090, open under the old name, which is R10-TRAIN-POSTMERGE's work.
  - **Why not reopen.** Reopening would make two live owners of one seam, and the four would be stranded again when #3090 merges.
  - **Why R10-TRAIN-MERGE-LOOP.** It is the train's live residue group, it is not in flight, and its brief already runs after R10-TRAIN-POSTMERGE.

Roster ops are queued `#held` in the session's roster queue, five `append-carry` lines released when this file is on main. The four old lines are marked `#superseded`. No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`d20776bb8e821af5e25fbf05dd09a6e06a556039`; the file is the whole diff against `c3b7c964f`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P358 and P359 as `ACCEPT`, and `triage_refusal` passes all five carries.
- With P359's verdict flipped to `REJECT`, its carry is refused: `dev/programme/triage/s6-batch102.md#P359 is not an ACCEPT ruling (REJECT)`.
- On roster branch `3f6dc470f`, the five appends apply. R10-BODY-CONTRACT goes from 6 carries to 7, and R10-TRAIN-MERGE-LOOP from 4 to 8.

## Null control

- With the file absent, a carry citing it is refused: `the triage ruling dev/programme/triage/s6-batch102.md is not on the roster branch or origin/main`.

## Figures

- `python3 -I tools/audit/carry_audit.py pr 3080`: `1 routed, 0 unrouted, 1 bad destination(s)`, with the bad one being `R10-FLY-ABORT-OWN-MERGE is done`.
- `grep -rhoE 'Carry: [A-Z0-9-]+ \| dismissed:'` over the bus's local verdict store (651 PR directories): 50 markers in 11 PRs.
- `gh pr view 3090`: OPEN, "R10-FLY-TRAIN-DEFAULTS (part 2)", at `41790e2b8`.
- `node tools/policy/brief_lint.mjs` on the roster after the ops: `TOTAL: 0 error(s)`.
- No capped file is touched (`grep -n carry_audit tests/*_budgets.json` prints nothing).

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none

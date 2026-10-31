Triage batch 85 rules the orchestrator s8's slip proposal of 2026-10-31. The sweep printed `REVIEW OWED: #3028 9e688830` on three consecutive sweeps for an APPROVED record/autofix PR, while `record_row.py --automerge-check --require-green` printed `AUTOMERGE OK #3028`. This is the next rolling batch under V182, after batch 84. It holds one ruling and one held roster op.

- **P322: ACCEPT as already ruled.** This is P241 (`s6-batch49.md`, the owner's words "record PRs should not need a review at all").
  - Its carry is stranded on R10-RECORD-HOLD-APPROVE, done at #2918, and is now re-routed to R10-FLY-TICK-APPROVAL-OWED. The code half may be dispatched alone.
  - `ledger.review_owed` skips a PR whose `headRefName` is `record/autofix`, with the constant passed in from the tick.
  - P241's one-sentence `standing-dispatch.md` rule travels with it. It is policy, merged on tvofi's review or under mandate 6329234399.
  - Neither half is on main: no `RECORD_BRANCH` in `ledger.py` or `orchestrator_tick.py`, and no record/autofix sentence in `standing-dispatch.md`.
  - REJECTED: the filing's variant of running `--automerge-check` in the tick. That is a GitHub read per record PR per tick, for a guard the train's `sweep_bots` already runs and logs. The measured `AUTOMERGE OK` shows the line was an over-fire, not a hidden failure.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`1faa29906da28ca3cc8a3624fc8b83c8b05913b6`; the file is the whole diff against `861f949ae`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P322 as `ACCEPT`. `triage_refusal` passes the carry text, which cites `triage: dev/programme/triage/s6-batch85.md#P322`: it returns None.
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same carry is refused: `dev/programme/triage/s6-batch85.md#P322 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main. The carry, appended to the live roster, gives `brief_lint.mjs` `TOTAL: 0 error(s)`.

## Figures

- `gh pr view 3028 --json headRefName,state,isDraft,reviewDecision,author` gives `record/autofix OPEN draft=false APPROVED app/hpo-author`.
- `git grep -n RECORD_BRANCH origin/main -- tools/audit/seat/ledger.py tools/audit/seat/orchestrator_tick.py` prints nothing. `git grep -n -i 'record/autofix' origin/main -- dev/governance/roles/standing-dispatch.md` prints nothing.
- `git show origin/main:tools/audit/seat/ledger.py` at `861f949ae`: `def review_owed` at line 618, with no `headRefName` test. The tick calls it at `orchestrator_tick.py:701`.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none

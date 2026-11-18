# Proposal triage, session s8, batch 85 (P322)

The rolling batch (V182) after batch 84 (handoff `triage-s8-batch84`). Facts were read at
origin/main `861f949ae`, on the roster branch, and from `gh pr view 3028`.

## P322: the tick prints `REVIEW OWED` for record/autofix PRs, which never take a review

Verdict: ACCEPT as already ruled. This is P241 (`s6-batch49.md#P241`, V155, the owner's words "record
PRs should not need a review at all"), whose carry is **stranded on a done group** and is now
re-routed to **R10-FLY-TICK-APPROVAL-OWED** (`not-started`, S). That group owns the tick's
verdict-level lines (`orchestrator_tick.py`). The carry adds `tools/audit/seat/ledger.py` to its
files and may be dispatched alone.
- **The fix, as P241 specified it.** `ledger.review_owed` skips a PR whose `headRefName` equals
  `record_row.RECORD_BRANCH` (`"record/autofix"`, `record_row.py:619`). The tick passes the
  constant in, and `ledger.py` never imports `record_row`.
- **P241's policy sentence travels with it, unchanged.** One sentence in
  `dev/governance/roles/standing-dispatch.md`: a record/autofix PR is never dispatched a reviewer.
  Its oracle is `record_row.py --plan` equality, `tests/delivery_status.py --require-rows` and
  `--automerge-check --require-green`. Policy: it merges on the owner's approving review, or under
  mandate 6329234399 as P241 recorded.
- **REJECTED: the filing's variant, "the predicate runs `--automerge-check` and prints
  AUTOMERGE-READY or the refusal".**
  - It adds a GitHub read per record PR per tick for a result the train already acts on.
  - `merge_train.py`'s `sweep_bots` runs that same guard and logs `BOT #N pending` or
    `refused by the guard` (lines 1229-1271).
  - The measurement shows the guard passing (below), so the line was an over-fire, not a failure
    the tick needed to surface.

Source: the orchestrator s8's message of 2026-10-31 (slip), and its measurement.

Instances:
- **#3028** (`record/autofix`, author `app/hpo-author`, OPEN, not draft, `reviewDecision`
  APPROVED, per `gh pr view 3028`). The sweep printed `REVIEW OWED: #3028 9e688830` on at least
  three consecutive sweeps (02:51Z, 03:00Z, 03:12Z).
- **The guard passes.** `record_row.py --automerge-check --require-green` at `9e688830b7d4` prints
  `AUTOMERGE OK #3028` (the merge seat's run). So the line was an over-fire.
- **Why it over-fires: P241 was never built.**
  - `ledger.review_owed` (`ledger.py:618-634`) has no `headRefName` test, and
    `git grep -n RECORD_BRANCH origin/main -- tools/audit/seat/ledger.py tools/audit/seat/orchestrator_tick.py`
    prints nothing.
  - `standing-dispatch.md` has no record/autofix sentence.
  - The carry sits on R10-RECORD-HOLD-APPROVE, which is `done` (#2918, `593f57c44`). Its forward
    reference also sits on R10-ORCH-BEATD, also `done`.
  - That is the stranded-carry class P305 (`s6-batch71.md`) rules on, and this re-route repairs
    one instance of it.

Cost: as P241 sized it. About 3 lines in `review_owed`, the constant passed from
`orchestrator_tick.py:701`, three fixture rows, and one policy sentence under its zero-headroom cap
paid by cutting text. No new file, check or API call.

Binding: a standing false `REVIEW OWED` line on every record PR (three sweeps on #3028 alone) costs
an investigation per sweep and teaches the reader to skip OWED lines. The owner ruled the fix
four days ago, and it was lost when its group closed. Re-routing it costs a roster op.

Carry text (for `roster_edit.py append-carry R10-FLY-TICK-APPROVAL-OWED`, citing
`triage: dev/programme/triage/s6-batch85.md#P322`): "P322 re-routes P241 (`s6-batch49.md#P241`, V155,
the owner: 'record PRs should not need a review at all'), stranded on R10-RECORD-HOLD-APPROVE, done
at #2918. Adds tools/audit/seat/ledger.py and dev/governance/roles/standing-dispatch.md to this
group's files. The code half may be dispatched alone.
- `ledger.review_owed` (`ledger.py:618` at 861f949ae) skips a PR whose `headRefName` equals
  `record_row.RECORD_BRANCH` (`record/autofix`, `record_row.py:619`). Pass the constant in from
  `orchestrator_tick.py:701`, and never import `record_row` into `ledger.py`.
- `standing-dispatch.md` gains one sentence: a record/autofix PR is never dispatched a reviewer.
  Its oracle is `record_row.py --plan` equality, `tests/delivery_status.py --require-rows` and
  `--automerge-check --require-green`. Pay the zero-headroom cap by cutting text. Policy: it merges
  on tvofi's approving review or under mandate 6329234399.
- Not changed: `app_approve.sh` and `merge_train.py`'s `sweep_bots`, which already merges the record
  PR on the guard alone.
- Observed 2026-10-31: `REVIEW OWED: #3028 9e688830` on three consecutive sweeps (02:51Z, 03:00Z,
  03:12Z), while `--automerge-check --require-green` printed `AUTOMERGE OK #3028`.
- Controls:
  - A record/autofix PR at an unverdicted head prints no REVIEW OWED.
  - Null: a fix/ PR in the same state prints it.
  - One mutant: drop the skip, and the record row fails."

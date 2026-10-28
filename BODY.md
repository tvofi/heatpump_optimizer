Triage batch 54 rules V179, the orchestrator's owner-approved card filed at 2026-10-28T19:02:58Z, as P265: ACCEPT narrowed, into R10-ORCH-LEDGER. That group owns the obligations ledger and states "an obligation with no ledger kind is a refusal".

- **The gap.** The tick's OWED handoffs key on handoff refs (`bus.sh orphans`), and its throughput stall covers queued entries only (`orchestrator_tick.py:1850`). An open PR that is neither queued nor stranded gets at most an unowned flag line.
- **The instances, read from git.**
  - #2906's newest `verdict/2906` is **blocked** at its live head `fb2f3de86`, committed 09:00Z, and no repair followed in about 9 h. There is no line for it at all. It is this seat's batch 47, so the owed repair is a triage fixer's.
  - #2917 (DIRTY) and #2919 (red unanswered) show only as flags.
- **The carry.** Each open PR gets exactly one bucket: train, verdict-pending, fixer-round, waiting-on #N, or owed.
  - Buckets come from data the PRS pass already reads, plus git refs. It adds no new GitHub calls.
  - An owed PR prints one OWED line with its reason, keyed (kind, PR) in the ledger.
  - Critical-path PRs come first.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`dad80f2551e5caad8df0bd18f2b0bffb83747945`; the file is the whole diff against `beb570c817c4efcae0d5f6f4bba52f3383baf8db`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate.
- On the committed file, `ruling_verdict` reads P265 as `ACCEPT`, and the queued carry citing `#P265` passes.
- Mutant (the verdict rewritten to `DEFER` in a copy): the carry is refused, `#P265 is not an ACCEPT ruling (DEFER)`, so the gate reads this line.

## Null control

With the file absent, the same call returns `the triage ruling dev/programme/triage/s6-batch54.md is not on the roster branch or origin/main`.

## Figures

- `git log -1 FETCH_HEAD` after `git fetch origin verdict/2906`: "verdict: #2906 Fix review: blocked fb2f3de86... carry-missing", committed 2026-10-28T09:00:27Z; `refs/pull/2906/head` `fb2f3de86`.
- `git fetch origin verdict/2917` and `verdict/2919`: no such ref.
- `orchestrator_tick.py`: DIRTY line at 855; THROUGHPUT STALL at 1850; the file is 4066 lines.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

- P265 ACCEPT narrowed (V179): the tick gives every open PR one bucket, from data it already reads plus git refs, and prints an OWED line with its reason for any PR in none, keyed in the obligations ledger (`tools/audit/seat/orchestrator_tick.py`; roster `dev/programme/rosters/wave-r10-groups.json`). Carry: R10-ORCH-LEDGER

## Friction

none

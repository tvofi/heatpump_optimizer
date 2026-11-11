Triage batch 188 rules P610 (queue line 289, roster-branch writer concurrency), 2026-11-11. It holds one ruling.

- **P610, REJECT: ROSTER-WRITER-CONCURRENCY.** Contention on `handoff/audit-r10-roster` is real, but it measures under the bar.
  - Over 7 days there is one `roster_edit` writer, the beatd drain, with 1,181 commits. Two other writers, the triage records and `roster_sync`, made 213 commits, 1.23 an hour.
  - A foreign commit lands inside 3.4% of drain ops. The null-corrected excess is 6.8% of drain time, and the upper bound with no correction is 16.9%.
  - The retained reports hold 943 ops with no lost-push-race refusal.
  - Carry latency comes from serial per-op cost (43 to 48 s) and queue depth. `roster_queue.py run --batch` already exists for bursts.

The diff is one file against the merge base: `dev/programme/triage/s6-batch188.md`, the ruling. No product behaviour changes.

## Head

`b9226067f967d9ebad268ff488373fe9991725e8`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P610 as REJECT.
- A citation of P610 is refused as "not an ACCEPT ruling (REJECT)", so no carry can cite it.

## Null control

- P611 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat ee64358be7...b9226067f967d9ebad268ff488373fe9991725e8`: 1 file, 1 commit.
- The figures come from the first-parent history of `handoff/audit-r10-roster` (2026-11-04 to 2026-11-11T11:25Z), the drain's retained reports, and the drain state at 11:25Z, as cited in P610.

## Red checks

none

## Forward-carry

none

## Friction

none

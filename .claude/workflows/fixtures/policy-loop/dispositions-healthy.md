Delivery-status, with every merge in the window dispositioned.

| item | state |
|---|---|
| linter | landed as #9001 |
| contrast and geometry | landed as #9002 |
| docs merge | landed as #9003 |

Two tables in a row, separated by one blank line, which is the shape the check
must NOT refuse. It is told apart by the delimiter row under the second header.

| lane | state |
|---|---|
| first | recorded |

| lane | note |
|---|---|
| second | its own table |

The sentences below name a capped file near the word cap and state no cap, and
the cap rule must NOT read them as claims. No count of them is given: it went
stale twice while they were being added, which is the defect the rule exists
for. The rule reads one line at a time, so each sits on its own line, and a
deleted line is a control lost. The first two put an issue number where a cap would go;
they stay silent because no shape of the rule consumes a `#`, and a shape that
did -- the mutation arm inserts `#?` before the number -- reports 608 here.
capped `docs/HANDOVER.md` at #608, and that is an issue number, not a cap.
`docs/HANDOVER.md` was capped at #608, and that is an issue number too.
#607 added 43 lines to `docs/HANDOVER.md` and merged 56 minutes later, a plain number off the cap word.
`README.md` has a cap of 999, but that name resolves to two files, so it is nobody's claim.
`docs/HANDOVER.md` at 999 lines exceeds its cap, and a length before the word lines is not a cap.
#608 raised `docs/HANDOVER.md`'s cap from 273 to 406, which is true, because the claim is the number after "to".
the #608-line cap on `docs/HANDOVER.md`, where the number-first form meets an issue number.
#608 capped `docs/HANDOVER.md` on 2026-09-07, and a date after the file name is not a cap.
the cap on `docs/HANDOVER.md` refused 24 lines, and a count after the file name is not a cap either.

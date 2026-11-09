Triage batch 138 records five rulings, P459 to P463. They cover every unruled proposal line of the session's triage queue (lines 143 to 147, all after batch 137's RULED line), oldest first. It applies `proposal-triage.md` as batch 137 did: a low or normal machinery repair meets the bar; medium and above, root-cause countermeasures and owner directives skip it.

- **P459 ACCEPT** CARRY-STATUS-DISAGREE (low) to R10-DISPATCH-AT-HANDOFF. Both readers already call `carry_audit.py landed`; `bus.sh` passes `--pr` and no `--topic`, so the own group never resolves.
- **P460 REJECT** CI-PRIORITY-PAUSES-AWAITING-REVIEW: its destination R10-CI-PRIORITY-PAUSE is refused (P428, 2.7 %), and the stop-gap is session-local.
- **P461 ACCEPT** PLAN-PAGE-NONE-LEAK (low) to R10-OUTSIDE-INTAKE, beside its carry 1 in the same render seam.
- **P462 ACCEPT** OPENER-LOST-HANDOFF, the `ledger.py` half (low), to R10-TICK-LEVELS: a closed PR's surviving `fix/*` branch discharges a successor handoff by `merges-only`. The opener half is session-local and rejected.
- **P463 ACCEPT, re-scoped** CODEQL-HEADROOM-PREMISE-FAILED: R10-HOTFIX-CODEQL-HEADROOM stays the python-leg cap change its roster brief and design `e64e8fdb` set. The wrap handoff `2d7bc354` is refused and not opened. File exclusion stays banned.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`226818f593f8ef66ba979aaff3983ad11df031cf`; one file against origin/main `3fdaa9da9a`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py` (`ruling_verdict`, `triage_refusal`), run from the head's worktree.
- Each of the 4 carry texts gets refusal `None`, and `op_append_carry` applies each to the roster at `ccc3286441`.
- With P463's verdict flipped to REJECT, its citing carry is refused: `is not an ACCEPT ruling (REJECT)`.
- A carry citing P460 (REJECT) is refused.
- The simulated roster, with the 4 carries and the one file widening, passes `node tools/policy/brief_lint.mjs`: `TOTAL: 0 error(s)`.

## Null control

- P464 reads `None` (no such entry).
- With the file absent, a citing text is refused: `not on the roster branch or origin/main`.
- A planted `triage P999` text with no citation is refused.

## Figures

- `git diff --stat 3fdaa9da9a...226818f593`: 1 file.
- Every ruling figure is cited beside its command or log in its entry's `Instances:`.

## Red checks

`none`. No pull request is opened for a triage record; it rides the stamp.

## Forward-carry

none

## Friction

none

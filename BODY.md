Triage batch 136 records twelve rulings, P425 to P436. They apply the owner's two rulings of 2026-11-08: a new proposal needs more than 20 %, a planned group needs at least 10 % to stay, and minor instrument or machinery defects take the bar. The batch covers the KEEP-TEST-20261108 set and the ROSTER-GATE-LINEPIN and GATE-DEFERRAL-NO-RECHECK proposals. CLOUD-SEAT-CHANNEL was already ruled, as P424 (batch 135).

- **P425 DROP** R10-CI-EDIT-RUNNER: CI saving at most 2.8 %, and 0.4 % since C3. Applied by the orchestrator; #3303 closed.
- **P426 DROP** R10-FLY-KEYED-MERGE-DRIVERS: one conflict round on its two files in the last seven days.
- **P427 KEEP narrowed** R10-FLY-DISPATCH-RULINGS: carry 0, the owner directive, stays; the `--preamble` flag is dropped as unmeasured.
- **P428 DROP** R10-CI-PRIORITY-PAUSE: queue time is 2.7 % of main CI wall time.
- **P429** R10-POLICY-ROLE-PACK: KEEP carry 4, the owner directive; DROP carry 5, 2.0 % of fires.
- **P430 DROP** R10-PLANTED-DEFECT-AUDIT's residue carries 3 to 5; the group closes on #3240.
- **P431 DROP** R10-REPLAY-COST-2: minor, 1.3 % of replay draws.
- **P432** R10-REPLAY-COST-BUDGET is not done: `2407ff613` set only the commit, and carry 3 is unmarked.
- **P433 KEEP** R10-HOTFIX-SELFTEST-TIMEOUT: classified major, 11.0 % of CI time. Its fix is merged, and the job now takes 10m48s.
- **P434 ACCEPT** the severity mapping, amended: severity exempts only defect repairs.
- **P435 ACCEPT changed** ROSTER-GATE-LINEPIN: the roster write gate refuses only errors the write adds. Carry to R10-ROSTER-WRITE-SWEEP.
- **P436 ACCEPT changed** GATE-DEFERRAL-NO-RECHECK: the sweep does re-run the deferring gate. The defect is readers that take the deferral red as final. A barrier carry goes to R10-HOTFIX-TRAIN-DEFER-WAIT and a root-cause addendum to R10-RCA-GATE-BUSY-DEFER-2.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`284709701d39f23dc6090167d953932b71b04220`; one file against origin/main `48af0864a`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py` (`ruling_verdict`, `triage_refusal`), run from the head's worktree.
- P434, P435 and P436 read `ACCEPT`. P425 to P433 read `unreadable` (KEEP, DROP and "not done" are not gate verdicts), so a text citing them is refused: `is not an ACCEPT ruling (unreadable)`.
- With P435's verdict flipped to REJECT, it reads `REJECT` and its citing carry is refused.
- The carry texts for P435 and P436 (two) get refusal `None`, and privacy `None`.
- A simulated roster at `439aebb50`, with the three carries and P427's new brief applied, passes `node tools/policy/brief_lint.mjs`: `TOTAL: 0 error(s)`.

## Null control

- P437 reads `None` (no such entry).
- With the file absent, a citing text is refused: `not on the roster branch or origin/main`.
- A planted `triage P999` text with no citation is refused.

## Figures

- `git diff --stat 48af0864a...284709701`: 1 file.
- Every ruling figure is cited beside its command or log in its entry's `Instances:`.

## Red checks

`none`. No pull request is opened for a triage record; it rides the stamp.

## Forward-carry

none

## Friction

none

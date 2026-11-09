Triage batch 137 records twenty-two rulings, P437 to P458, over every unruled proposal line of the session's triage queue (lines 106 to 141), newest first. It applies `proposal-triage.md` as merged by R10-FLY-TRIAGE-BAR (#3310): a low or normal machinery repair meets the bar; medium and above, root-cause countermeasures and owner directives skip it.

- **P437 ACCEPT** REVIEWER-NO-RETURN-WAIT (RCA countermeasure): C2 prompt terminal edges to R10-FLY-DISPATCH-RULINGS, C1 reviewer no-return arm to R10-RELAY-SWEEP; C3 rejected.
- **P438 ACCEPT** UNBLOCKED-UNDISPATCHED (medium) to R10-TICK-LEVELS.
- **P439 ACCEPT** CLOUD-DISPATCH-DESIGN-REF-CASE (low) to R10-FLY-DISPATCH-RULINGS.
- **P440 ACCEPT** CARRY-AUDIT-NONBLOCK-FP (medium) to R10-BODY-CONTRACT part 5, beside carry 47.
- **P441 ACCEPT** OUTSIDE-CHAIN-STALL: already R10-TICK-LEVELS carry 19; no op.
- **P442 REJECT** DISPATCH-PAST-THREE-QUOTING: a session-local wrapper; `bus.sh` is not at fault.
- **P443 ACCEPT** CODEQL-PY-CAP: already R10-HOTFIX-CODEQL-HEADROOM's scope; no op.
- **P444 ACCEPT** TRAIN-UNDRAFT-GAP (medium) to R10-TRAIN-MERGE-LOOP-2.
- **P445 ACCEPT** CI-ATTEMPT-ALARM (RCA countermeasure) to R10-TICK-LEVELS; the `fixer.md` line DEFERs to R10-RCA-SWEEP-SETTLE-LOOP (`fixer.md` has no token headroom).
- **P446 ACCEPT** RELAY-HANDOFF-STARVATION: routed to R10-RCA-RELAY-HANDOFF-STARVATION; no op.
- **P447 ACCEPT** TRAIN-PAUSE-DURING-STAMP (owner directive) to R10-TRAIN-MERGE-LOOP-2.
- **P448 ACCEPT** DESIGN-RECUT-UNREVIEWED (low) to R10-TICK-LEVELS.
- **P449 ACCEPT** GH-BUCKET-UNATTRIBUTED (low) to R10-FLY-GH-READ-RETRY.
- **P450 ACCEPT** LEDGER-CLOSE-WRONG-SHA (low) to R10-TICK-LEVELS.
- **P451 ACCEPT** PREFLIGHT-POLICY-ORDER (major) to R10-RAISE-GATE-SHIM.
- **P452 ACCEPT** POSTMERGE-ROSTER-RC3 residue (low) to R10-ROSTER-READ-SWEEP; half built by `39a735d8f8`.
- **P453 ACCEPT** GC-LIVE-TRAIN-CHECKOUT (major, audit class) to R10-CLOSEOUT-INSTRUMENTS; `--keep-dir` is the evidence destination, not a keep list.
- **P454 ACCEPT** PREPR-SLOT-LIVELOCK (major) to R10-PREPR-CAP; `HPO_SLOT_LABEL` already exists, so no new marker.
- **P455 ACCEPT** RED-UNOWNED-OVERFIRES (low) to R10-TICK-LEVELS.
- **P456 ACCEPT** OWED-UNACTIONED-CAP-LINE (major) to R10-TICK-LEVELS.
- **P457 DEFER** RELAY-SERIAL-UPDATES to R10-RCA-RELAY-HANDOFF-STARVATION.
- **P458 REJECT** CARRY-CONTEXT-ONLY: at most 5 of 281 recarries (1.8 %).

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`4cd0a64e6d0ff03acc00ebeea6c91350275029e7`; one file against origin/main `6457496aba`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py` (`ruling_verdict`, `triage_refusal`), run from the head's worktree.
- The 17 carry texts each get refusal `None`, and `op_append_carry` applies each to the roster at `9a4a04d55`.
- With P437's verdict flipped to REJECT, its citing carry is refused: `is not an ACCEPT ruling (REJECT)`.
- A carry citing P442 (REJECT) is refused.
- The simulated roster with the 17 carries and 7 file widenings passes `node tools/policy/brief_lint.mjs`: `TOTAL: 0 error(s)`.

## Null control

- P459 reads `None` (no such entry).
- With the file absent, a citing text is refused: `not on the roster branch or origin/main`.
- A planted `triage P999` text with no citation is refused.
- A planted `set-files --add` of a path not in the tree is refused.

## Figures

- `git diff --stat 6457496aba...4cd0a64e6d`: 1 file.
- Every ruling figure is cited beside its command or log in its entry's `Instances:`.

## Red checks

`none`. No pull request is opened for a triage record; it rides the stamp.

## Forward-carry

none

## Friction

none

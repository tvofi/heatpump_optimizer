Triage batch 139 records twelve rulings, P464 to P475. They cover every unruled proposal line of the session's triage queue: lines 148, 149 and 151 to 160, after batch 138's RULED line 150. It applies `proposal-triage.md` with the owner's 2026-11-08 rulings. A new proposal needs a measured gain over 20 %. A low or normal machinery repair takes that bar. Medium and above, root-cause countermeasures and owner directives skip it.

- **P464 REJECT** HOLD-MASKS-NEW-VERDICT: the sweep runner is session-local, and the masked delay is 2.7 % of the blocked-verdict cycle.
- **P465 REJECT** DEFERRAL-RERUN-INSTRUMENT, a duplicate of `tools/ci/sweep.py` `settle`. `gate-sweep.yml` has been `disabled_manually` since 11-08 11:54Z, though #3327 merged at 22:02Z. 46 hand deferral re-runs followed. Turning it back on is the orchestrator's call.
- **P466 REJECT** PACKET-READS-RUN-ID-AS-SHA: reproduced, but it hits 1 of 35 open bodies (2.9 %).
- **P467 DEFER** RELAY-MINTS-UNPUBLISHED (owner R10-RELAY-SWEEP): the share of fire latency it costs is unmeasured.
- **P468 DEFER** BODY-PATCH-LEAVES-STALE-REDS (owner R10-BODY-CONTRACT): same cause as P465. Re-measure with the sweep on.
- **P469 REJECT** OWED-UNKEYABLE-FIXER-ROUND: already built at open #3345 (R10-TICK-LEVELS carry 16).
- **P470 DEFER** SKIP-DEFERRAL-NOT-ENVIRONMENT (owner R10-TRAIN-REJOIN-NO-RECARRY): #3359's rejoin and P465 come first.
- **P471 REJECT** PREFLIGHT-PATH-MASKED: one harmless hand-pipe slip.
- **P472 REJECT** MANDATE-APPROVE-INSTRUMENT: 3 % to 7 % of merge latency, and approval authority is the owner's.
- **P473 ACCEPT** PLAN-PAGE-NONE-LEAK extension (owner directive) to R10-OUTSIDE-INTAKE beside P461, with `set-files --add tools/audit/seat/plan_page.py`.
- **P474 REJECT** OPENER-STRIPPED-TOPIC-MISREAD: the tracked `open_driver.py` `resolve` handles the body. The defect is in the session-local opener.
- **P475 ACCEPT** REVIEWER-BLOCKS-ON-WAIT (medium, third instance) to R10-DISPATCH-AT-HANDOFF: build its carry 12 (pending-ci) next.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`dec4667d5e8a12ae83e8978a0e5f666116b21727`; one file against origin/main `0a8033305d`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py` (`ruling_verdict`, `triage_refusal`), copied from origin/main and run against the head's file.
- Both carry texts get refusal `None`. `op_append_carry` applies each to the roster at `b1de33a83a`: R10-OUTSIDE-INTAKE goes from 2 to 3 carries and R10-DISPATCH-AT-HANDOFF from 18 to 19. `op_set_files` adds `tools/audit/seat/plan_page.py` to R10-OUTSIDE-INTAKE.
- With P475's verdict flipped to REJECT, its citing carry is refused: `is not an ACCEPT ruling (REJECT)`.
- A carry citing P472 (REJECT) is refused, and so is one citing P467 (DEFER).
- The simulated roster, with the 2 carries and the one file widening, passes `node tools/policy/brief_lint.mjs`: `TOTAL: 0 error(s)`. The unmodified roster reads the same.

## Null control

- P476 reads `None` (no such entry), and a text citing it is refused.
- With the file absent, a citing text is refused: `not on the roster branch or origin/main`.
- A planted `triage P999` text with no citation is refused.

## Figures

- `git diff --stat 0a8033305d...dec4667d5e`: 1 file.
- Every ruling figure is cited beside its command or log in its entry's `Instances:`.

## Red checks

`none`. No pull request is opened for a triage record; it rides the stamp.

## Forward-carry

none

## Friction

none

Triage batch 133 rules on queue lines 81 to 95: 15 lines in 13 rulings, P406 to P418. Line 88 is folded into P406 and line 83 into P409.

- **P406, ACCEPT changed: the red-checks retake class.** This is an audit-class barrier, with 7 instances on 2026-11-07, and P405 did not cover it. Four refusals were caused by one fact: `policy_lint.mjs` voids the main-graded exemption of both reporters on one shared REPORTER_INPUTS set. So a diff that touches only `governance.yml` owes `tests / nightly-status`, a `tests.yml` job that runs the base-pinned script. The barrier keys the inputs per reporter. It is a carry to R10-BODY-CONTRACT. The cancelled-self-test and codescan-wait instances go to their owners. The known-cause registry and the relay re-take are rejected.
- **P407, ACCEPT: CLOSEOUT-CLEANUP carry 2 is implemented.** The code is at 9f7487299, merged by PR 3085 at 6125b263d. The self-test passes, 74 checks. The bare mark cannot land, because the carry names "Triage P-A" and a mark value must be a bare sha. The route is drop, re-append with the citation, then mark by match. It was simulated through the gate.
- **P408, ACCEPT changed: the author-email push guard (owner hotfix tier).** The allowlist is a grammar. The writers of `seat@` and `hpo-fixer@users.noreply.github.com` are fixed too: 529 such commits have landed since 11-05 12:00Z. It is a new group, R10-HOTFIX-AUTHOR-EMAIL.
- **P409, ACCEPT: roster_edit's on-origin guard reads stale tracking refs.** The fix is fetch-and-recheck, plus update-ref after its own push. It is a carry to R10-ROSTER-WRITE-SWEEP.
- **P410, REJECT: the drain mispair.** The tracked beat row already marks each op from its own report. The defect is the host-local drain script, which the orchestrator retires.
- **P411, ACCEPT changed: the relay auto carry-fold.** It is a carry to R10-CARRY-RESIDUE-2, the same class as its carry 3.
- **P412, ACCEPT narrowed: the file-overlap cap.**
  - The per-file cap is rejected: +1124 h in the replay.
  - A keyed merge driver goes on the roster JSON and INSTRUMENTS.md, as a new group, R10-FLY-KEYED-MERGE-DRIVERS.
  - Drivers for the Python files and the warn-only check are deferred.
- **P413, ACCEPT: the fixer.md sentence.** The owner-mandate route already exists as R10-FIXER-MD-SPELLING-CORPUS, so no op is owed.
- **P414, REJECT: the body-only alarm.** The tick already prints `OWED body-ahead`. It was lost in owed_unactioned (P416).
- **P415, DEFER: bottleneck mutation-vacuous.** The RCA and its countermeasures exist, and prepr's diff-mutant arm is report-only. The open question is whether it would have caught the 11 blocks.
- **P416, ACCEPT: owed_unactioned has no body-ahead key.** One such line makes the whole run UNREADABLE. It is a carry to R10-TICK-LEVELS.
- **P417, ACCEPT: roster_queue's batch swallows the refusal.** It is a carry to R10-ROSTER-WRITE-SWEEP.
- **P418, ACCEPT: set-files keeps only the last `--add`.** The fix is `action=extend`, as a carry to R10-ROSTER-WRITE-SWEEP.

The diff is one file against the merge base: `dev/programme/triage/s6-batch133.md`, the ruling. No product behaviour changes.

## Head

`671a3f7140d0ce7647c549062bce959bbc81ea40`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads ACCEPT for P406 to P409, P411 to P413 and P416 to P418, REJECT for P410 and P414, and DEFER for P415.
- Each of the 8 carry and brief texts in the rulings' `Binding:` passes `triage_refusal`.
- With P409's verdict flipped to REJECT, its carry is refused as "not an ACCEPT ruling (REJECT)".
- A citation of P410 is refused as REJECT.
- For P407, a simulation over the roster at 3069eaa49: the bare `mark-carry` is refused as "proposal-sourced text cites no triage ruling". The drop and re-append with the P407 citation passes. The mark by match on the cited entry passes, with the mark `implemented 6125b263d94e`.

## Null control

P419 reads `None`. With the file absent, a carry citing P409 is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 364353e67...671a3f7140d0ce7647c549062bce959bbc81ea40`: 1 file.
- Every ruling figure is printed by the command the ruling names beside it.
- No capped file is touched. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`, and `tests/closure.py select` prints `MODE: SCOPED -- 0 script(s) run`.

## Red checks

`none`. The merge base is main `364353e67`, whose 50 check-runs include no failure. This head's checks run after its push.

## Forward-carry

none

## Friction

none

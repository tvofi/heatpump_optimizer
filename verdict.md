Fix review: merge a6d49999a4c6bdf0b0bd1c8ce1dfef9eeba503a7

bus-nonce: 15b9d0655bcec062f14e714d5fb5fd56

Round 1. Record PR: triage s9 batch 102 (P358 narrowed ACCEPT, P359 ACCEPT). Measured and judged at head a6d49999a4c6bdf0b0bd1c8ce1dfef9eeba503a7.

## Findings

none.

## Evidence

- RESULT head: PR head is a6d49999a4c6bdf0b0bd1c8ce1dfef9eeba503a7; the body's `## Head` names it and the authored code head d20776bb8; the extra commit adds only dev/programme/delivery/3096.md.
- RESULT record-PR: the three-dot diff (`git diff $(git merge-base origin/main HEAD)...HEAD`, base c3b7c964f) is 2 files, +127: dev/programme/delivery/3096.md and dev/programme/triage/s6-batch102.md. No production code, no VERSION, manifest, RELEASE_NOTES heading, golden or claim file touched (ev/protected.txt empty).
- RESULT delivery-row: dev/programme/delivery/3096.md is in the diff, one row, matching the PR number and title.
- RESULT merge: `git merge-tree --write-tree origin/main a6d49999a4c6bdf0b0bd1c8ce1dfef9eeba503a7` rc=0, tree 89c6fdce, no conflict (ev/merge-tree.txt, origin/main e4c9e2016).
- RESULT code-claim (P358): at the head tree, seg_dests("Carry: R10-FLY-ABORT-OWN-MERGE | dismissed: suggestion for the fixer to state.") returns ['R10-FLY-ABORT-OWN-MERGE'] only; the dismissal is dropped (tools/audit/carry_audit.py seg_dests, the token loop breaks at "dismissed"), while the bare form "Carry: dismissed: two words here" returns the dismissal token. So the form parks a PR once its pointer group is done, as the triage says. The cost claim holds: carry_audit.py is 1103 lines and `grep -n carry_audit tests/*_budgets.json` prints nothing.
- RESULT part-2-rejection: reasoned. A later body Carry superseding a verdict's destination would let an author override a reviewer's routing, which is a finding-propagation policy matter; no instance with a live (non-dismissed) carry to a done group is measured; part (1) clears the one observed instance. I judge the rejection sound.
- RESULT carry-text: the P358 carry text states the change, the pointer rule (any roster group, live or done), a no-dismissed segment read as today, and four controls including the null control and the mutant. It meets the carry-with-control standard.
- RESULT destinations (roster branch handoff/audit-r10-roster, wave-r10-groups.json via roster_lib.is_open): R10-BODY-CONTRACT open and lists tools/audit/carry_audit.py; R10-TRAIN-MERGE-LOOP open and lists tools/audit/seat/merge_train.py; R10-FLY-TRAIN-DEFAULTS and R10-FLY-ABORT-OWN-MERGE are done; R10-TRAIN-POSTMERGE open. PR #3090 is OPEN at 41790e2b8 (git ls-remote refs/pull/3090/head). The four P359 carries therefore have a live destination, and the reopen alternative is correctly refused. Carries are not on the roster by design for a triage batch and I did not block on that.
- RESULT figures: the body's 50 markers in 11 PRs come from the bus's local verdict store on the dispatcher's host. This cloud seat has no such store, so I could not re-derive that count and I did not verify it. Nothing in the ruling turns on the exact number: one observed instance (#3080) carries part (1). The other body figures (#3080 audit line, #3090 state, 651 PR directories) are likewise host-local or live-state reads I re-checked only where stated above. figure_lint in the packet: 3 resolved, 0 not verified, 0 refused.
- RESULT red-checks: the whole check-run set at this head (43 runs from get_check_runs, all concluded or skipped, none red); the body's `## Red checks` says none, which is correct. governance / instrument-self-tests concluded success at 14:55:40Z. A second workflow run's prelude job was still in progress but is not a required context.
- RESULT ci: merge_train.py classify a6d49999a4c6bdf0b0bd1c8ce1dfef9eeba503a7 exits 0, "GREEN ... pending: none red: none" (ev/classify.txt).
- RESULT mutation/null/both-ends: not applicable to a record PR with no production code (the body's mutation proof is of the roster gate in roster_edit.py, a consumer; I did not re-run it). The mutation lane is green and was not re-run, per the contract.
- RESULT claims: claim files not in the diff, so byte-identical to origin/main.
- RESULT contract-currency: roles/fix-review.md read from origin/main.
- RESULT forward-carry: the body states none; the P358 and P359 carries are the ruling's own output on the held roster ops and are written in the triage file.
- This is round 1.

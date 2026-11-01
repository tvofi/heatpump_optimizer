Fix review: merge aae5e0190a7733813e94509c108e8103b82f71bf

bus-nonce: a65cd3a006e6a1f5c46cd244f7c8a8ef

Round 1. Record PR (one ruling file plus delivery row); no production code, no policy file. Measured head aae5e0190a7733813e94509c108e8103b82f71bf, base 61b0076f4; origin/main now c89de2f62.

## Findings

- Suggestion, not a block: the carry keeps `$B.push.log` when nothing was pushed and prints its path, but does not say what the log may hold. app_push output can carry remote URLs or tokens; the precedent `pr_push_failed` (pr_args.sh line 180) also keeps and tails its log unscrubbed, so the carry matches it. The fixer should state in the carry/body that the kept log sits beside the body in the seat's state dir and is not scrubbed, or print only the FAIL/REFUSE/full-log lines (as the carry does) and leave the log unredacted knowingly. Carry: R10-FLY-ABORT-OWN-MERGE | dismissed: suggestion for the fixer to state; no ruling change needed.
- Nit: the ruling says merge_train.py quotes remerge's stdout "at the raise(Stop("recarry"...)) after line 1837"; the raise is at line 1856 (`o.strip()[-2000:]`; line 1837 is the `self.run` call). The cited text is right, only the line anchor is loose. Also `[-2000:]` is a tail, so extra printed lines could push the REFUSE line out of the quote on a long output; the fixer should keep the added lines short. Carry: R10-FLY-ABORT-OWN-MERGE | dismissed: line anchor only; the fixer reads merge_train.py itself.
- Ownership, said not decided: R10-PREPR-CAP (#3051, prepr.sh slots) and the batch-96 P351 carry touch prepr.sh/body_push.sh; the P353 fix edits only remerge_main.sh and its pr_args.sh self-test and reads prepr's existing `full log:` line, so there is no file overlap with them. R10-FLY-ABORT-OWN-MERGE lists exactly those two files. Carry: R10-FLY-ABORT-OWN-MERGE | dismissed: no conflict found; orchestrator may still prefer another owner.

## Evidence

- (a) Locations confirmed at 61b0076f4: remerge_main.sh line 39 is `grep -E 'RECARRY|REFUSE|PUSHED'`; line 19 is `PL=$B.push.log; pr_exit_trap 'rm -f "$PL"'`; file is 40 lines. prepr.sh line 3502 is the `mktemp "${TMPDIR:-/tmp}/prepr-log.XXXXXXXX"`, line 3508 the `PRE-PR: ... full log: $PREPR_LOG`. pr_args.sh (under tools/audit/seat, not tools/pr) line 180 is `pr_push_failed`, which greps REFUSE else tails the log and names it. merge_train.py line 1856 is the Stop("recarry") quote. The self-test lines 705-717 are reap arms; the stubbing remerge_main arms are at 1336-1370 (stub app_push prints stub-push-refused). All as the ruling says.
- (b) Roster: origin/handoff/audit-r10-roster wave-r10-groups.json has R10-FLY-ABORT-OWN-MERGE with files remerge_main.sh and pr_args.sh, stage done, PR 2947 merged. roster_edit.op_set_stage only checks the stage word against roster_lib.STAGES; carries-open is in STAGES (True) and nothing forbids done to carries-open (55 groups already use it).
- (c) Not re-derivable: rm3052.log, prepr-log.h6GW1PlY, the 2 h 19 min wall time, the 22 min heavy slot, the 6-log grep and slot=2 lease times rest on the orchestrator's session state and TMPDIR, which this container cannot reach (checked: no prepr-log.h6GW1PlY here). Taken on the ruling's word; the code-level claims above are independently confirmed.
- (d) Null: there is no remerge_main `--self-test` (it dies on $2 unbound; the self-test is pr_args.sh --self-test). At the head, pr_args.sh and remerge_main.sh contain no arm or code for FAIL lines, `full log:` or `push log kept`: the carry is not already built.
- Gate: roster_edit.triage_refusal on the head ruling returns None; with the Verdict flipped to REJECT in memory it returns "dev/programme/triage/s6-batch98.md#P353 is not an ACCEPT ruling (REJECT)".
- merge-tree origin/main with the head: exit 0, no conflict. Three-dot diff is two files (ruling, delivery row dev/programme/delivery/3080.md naming #3080); claim files, VERSION and goldens untouched. python3 tests/structure.py: STRUCTURE RATCHET PASSED. review_packet figure_lint: 1 resolved, 0 refused; carry_audit 0 items.
- CI: merge_train.py classify at this head: GREEN, pending none, red none (rc 0). No red check, so no root-cause answer is owed. Mutation proof and both-ends harness do not apply to a record PR with no code.
- Roster carries are absent from the roster branch by design (not a finding).

Fix review: merge 8e828d854e06e5ec9458e1831c27f4c293912c8c

bus-nonce: 691c04df64ec9b32794a7192990056c5

## Summary
Round 1. Measured at head 8e828d854e06e5ec9458e1831c27f4c293912c8c (the live head of refs/pull/3063/head).

## Findings
- Instrument carry (the body's dismissal): the body names no finder harness for the instrument carries; the self-test arms and the group's mutant harness model the instances. Acceptable for an instrument whose own self-test is the measurement. Carry: dismissed: no finder harness exists for instrument carries; fixtures model the instances (confirmed against the body)

## Evidence
- Self-test at head: 400 checks, 0 failed. At fork 7539d167: 381 checks, 0 failed (matches body).
- Mutant harness dev/audit/harnesses/r10_train_overlap_grade_p4_mutants.py: 13 run, M0 PASS, M1-M12 KILLED, 0 not as required (matches body).
- My own mutants of the self-test, each killed by exactly the arms aimed at it: mA (--remove drops unreadable lines) -> 1 failed; mB (batch admit reverted to main's req) -> P34 batch arm red (PR-only pr-contract red head admitted); mC (--front on a new live-train entry not moved first) -> 1 failed; mD (no QUEUE_LOCK on spool_edit) -> 2 failed (concurrent add lost, so the lock null is real). Outputs in ev/.
- Bug 1 shown: non-empty PR_ONLY, red pr-contract at head: refused at head (head_req), the fork's main-set req admits; null with pr-contract green admits both and merges.
- Class rule: self.required( sites are 4 at head (1946, 2135, 3119 main set, 3129 head set) vs 3 at fork; the only main-set site is the one grading main_green/settle; no site missed. Spool writers: spool_append, spool_rewrite, the two unlinks, no writer outside merge_train.py (grep over tools, .claude, dev/governance).
- Carry 11 not built: log=print at Train.__init__, train log lines carry no timestamp; the body's reason is true.
- archscore: dS +0.0000 NULL. tests/structure.py: STRUCTURE RATCHET PASSED, no budget touched.
- merge-tree origin/main vs head: exit 0, only LEDGER-MERGE resolved tests/closures.json; no conflict.
- Diff touches no VERSION, manifest, notes, golden or claim file. Delivery row dev/programme/delivery/3063.md is in the three-dot diff; new harness is in tests/closures.json.
- CI: merge_train.py classify 8e828d854e06e5ec9458e1831c27f4c293912c8c -> GREEN, pending none, red none; review-packet gate digest green.
- No red gate check, so the root-cause answer is not owed.

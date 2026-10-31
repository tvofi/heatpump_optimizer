Fix review: merge db4fdd8176047acf404d5c738664b85a37f47b4e

bus-nonce: 2e0ea58f0138b1ffe21ad39b2c3935b2

Round 1, a triage record PR (two files: s6-batch93.md, delivery/3053.md; no production code). Head measured: db4fdd8176047acf404d5c738664b85a37f47b4e.

## Findings

None the PR leaves open. The carries (P334's roster_edit.py change) land after merge by design, so their absence from the roster branch is not a finding.

## Evidence

- (a) P333: roster_lib.group_for_branch (origin/main) does an exact resume.branch match, then last-segment equality, "never a prefix". design/r10-audit-coverage therefore returns None for R10-AUDIT-COVERAGE-ENDGAME. designs_owed skips a stage outside UNBLOCKABLE_STAGES + ("design",) and UNBLOCKABLE_STAGES = (None, "", "not-started"). queued is a STAGE_KIND word (derivable). 12 design/* refs on origin; design/r10-audit-coverage (ae3d86dc0) and design-verdict/r10-audit-coverage (5b77e98dd) exist. The roster branch already shows the group at stage queued, with next_step saying the fixer waits on R10-FLY-MUTANT-RESTORE and R10-996-RUNNER-CLAIMS. The ruling asks for queued, not fixing. Confirmed.
- (b) P334: op_append_group passes json_file straight to Path().read_text; op_edit_brief goes through _text, which strips a leading @. Confirmed. The carry lists the bare-path null, the @missing null (rc 2, unreadable JSON) and one mutant. The 9 refusals sit in out-of-tree roster reports; I could not re-derive that count in-tree and did not try. Minor: the ruling cites roster_queue.py line 149 for the append-carry readback; the line is about 148. Cosmetic.
- (c2) P335: on the roster branch, a396c2a83 set R10-ORCH-ROSTER-SCHEMA in-progress, and 52aea59b1 (roster_sync, 16:53+01:00) rewrote it to done. 6aea809f6 is not an ancestor of origin/main, and git grep -ci mark-carry origin/main -- tools gives 0 matches. The WOOD-NOTIFY commits 00e74d290 (carry) and dd3779695 (carries-open) exist on the roster branch; a7dd7f50 exists. Rejecting the merge-seat-only check holds: roster_sync closed the group with no merge seat involved, so it covers one of two writers. The roster now shows ROSTER-SCHEMA at carries-open.
- (c) Triage gate: ruling_verdict at the head reads P333 REJECT, P334 ACCEPT, P335 ACCEPT. With P334 flipped to REJECT, triage_refusal refuses with "s6-batch93.md#P334 is not an ACCEPT ruling (REJECT)". Unflipped returns None.
- (d) dev/programme/delivery/3053.md is in the three-dot diff in open-row shape for PR 3053. The row names the PR, not a SHA; the shape carries no head field.
- Merge: git merge-tree --write-tree origin/main at the head exits 0.
- CI: merge_train classify returned GREEN for the head. No gate check was red, so root-cause-answer (step 11) does not apply.
- Steps 1-4, 6, 14: a record PR with no production lines, no claim, budget, closure or version movement, so there is no mutant to run. carry_audit at the head reports 0 findings.
- The packet's finder's-harness section reads "none named", and the PR needs none.

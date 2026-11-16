Result of the first R11-PRE-BRIEFS-CENSUS repair seat (dispatch 7134577cf0), stopped on finding the re-fire (dispatch ea92ac5cd8) already working from handoff-wip at c09aedf614.

- Code: 4d2172c804, 6deab5ebeb, cc66a6cf85 (tools/audit/enumerate.py), then 2e1adb82e3 (merge of origin/main e30408f788; policy_budgets.json corpus_tokens re-recorded). c09aedf614 already merges 2e1adb82e3 into 6a32d9035a.
- BODY.md: the body written for head 2e1adb82e3; prepr.sh at that head rc 0 (PREPR_SKIP_CLOSURES=1 PREPR_SKIP_CODE=1, after a full scoped run whose only refusals were body steps, since repaired). Its Head, merge paragraph, budget figures and prepr lines describe 2e1adb82e3 and must be re-taken at the head that is handed off.
- ev/mutants_final.json: the reviewer's ev/mutants.json less M7, plus M7r, M0, M0b, M0c, N1-N4, N5b, N6-N9, N11, N12. ev/mutant_run_at_2e1adb82e3.txt: SURVIVED NULL, 50 KILLED, rc 0.
- ev/diff-mode file: --report-only survivors of the round's delta; one production line (314, answered by cc66a6cf85), the rest self-test lines.

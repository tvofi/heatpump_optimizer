Fix review: merge 37555ea332a069d698366d7c41341d971ce3a613

bus-nonce: f0286c7c60b235415e29273ddd736313

Round 2. Scope (owner ruling 2026-11-09): only `git diff 34a9cf1251fa6046f3182a21aea60a84b477609f 37555ea332a069d698366d7c41341d971ce3a613`. The PR's own commits in that range are 27a61185f and a8563e945. The rest is origin/main merged in by 44c77b585 (#3341, #3397, #3416). The PR-own delta past that merge touches three files: `tools/audit/carry_audit.py`, `tools/pr/ci_predict.py` and `dev/audit/harnesses/r10_carry_sink_barrier.py` (ev/pr_own_delta.diff). Nothing under custom_components/ changed, so the review was not widened.

## Evidence

- Previous block (class-open, issue token bypass): resolved. I re-ran the previous reviewer's own census script (verdict/3417 evidence/issue_bypass.py.txt) against roster origin/handoff/audit-r10-roster d32a844665b0. At 34a9cf125, all 5 issues owned only by an unreceivable group were `accepted_without_state=True` (#2505, #2727, #2728, #3313, #3314). At 37555ea33, all 5 read `False` (ev/issue_bypass_both_ends.txt).
- CLI at both ends, using the body's rule (one `## Forward-carry` item, `--roster-ref origin/handoff/audit-r10-roster`): `Carry: #3313` and `Carry: #2728` were rc 0 (routed) at 34a9cf125 and are rc 1 BAD-DEST at the head. The message names the owner, the stage and the owner-approved rule. `Carry: R10-REVIEW-ENUMERATE` is rc 1 at both ends (ev/issue_token_cli_both_ends.txt).
- Previous finding (ci_predict self-test broke): resolved. `ci_predict.py --self-test` reads `0 failed` at the head. The pick now uses `carry_audit.Dests.live`.
- Instrument enforces the policy. The issue arm calls the same `self.live` (`roster_lib.carry_receivable`) as the group arm, so there is one rule. The exceptions are a carry file or an O-brief, which matches the previous verdict's prescribed repair. `owned`/`owns` are unchanged, so `sweep --issues` and `orphaned` are unaffected. This is no widening beyond the owner-approved rule. The policy text is unchanged in this delta.
- Mutation, my own runs at the head (ev/mutants.txt), all killed:
  - M1, the receiving refusal disabled: 2 FAIL.
  - M2, every open owner receives: 2 FAIL.
  - M3, the O-brief no longer receives: 2 FAIL, including null control #906.
  - M4, a carry file no longer receives: 3 FAIL.
  - M5, the ci_predict pick back to `is_open`: 1 FAIL.
  - These match the body's M1-M4 and its ci_predict figures.
- Failing-then-passing and null control, from the harness issue arm at roster d32a844665b0 (ev/harness_three_revs.txt):
  - At 34a9cf125: `issue_accepted[carries-open]=5 of 5`, `issue_accepted[live]=23 of 23`.
  - At the head: `issue_accepted[carries-open]=0 of 5`, `issue_accepted[live]=23 of 23`. The null control is flat.
  - The group-arm figures are unchanged from round 1 (carries-open 0 of 6, in-progress 17 of 17, not-started 17 of 17).
  - These match the body's 5→0 and 23/23. My roster ref differs from the body's 2e749ce5 and reads the same.
- Self-test null controls #902, #903, #905 and #906 pass. `carry_audit.py --self-test`: 415 checks, 0 failed.
- The ci_predict mutant is killed only while the in-tree roster's first open group is unreceivable. The body states this. It pins a self-test fixture, not a production site.
- CI: `merge_train.py classify 37555ea33... --pr 3417` printed `GREEN 37555ea332a069d698366d7c41341d971ce3a613 pending: none red: none` (rc 0), first and final run (ev/classify.txt, ev/classify_final.txt). The owed-reds set is in ev/owed_reds.txt. No owed red is open.
- `git merge-tree --write-tree origin/main <head>`: rc 0, clean, at origin/main 45adb0c3b (ev/merge_tree.txt).
- The three-dot diff touches none of VERSION, RELEASE_NOTES.md, custom_components/, tests/golden/ or `*_budgets.json` (ev/untouched.txt).
- Archscore dS +0.0000, STRUCTURE RATCHET PASSED and 2707 entity checks are taken from CI's green arch-score, gate and tests lanes. I did not re-run them.
- Owner approval of the policy change is still owed at merge, as the body's `## Approval` states. This seat holds none.

## Findings

none

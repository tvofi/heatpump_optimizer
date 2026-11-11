Fix review: merge fe859f3563735327627c5de908b8fb95cde42e7f

bus-nonce: a0d3b45c8d1dc1ad074aa233a951a751
pending-ci: gate

Round 3 (delta 63c3886a..fe859f35: `fbca7fe78`/`c8e4a3daf` add four self-test checks and the `SHR` fixture to tools/audit/seat/mutant_run.py, and merge main). I reviewed from a detached worktree at the head (`ev/HEAD.txt`). Every mutant the round-2 block named is now killed, and none of the fix's lines has a known survivor left.

## Findings

none

## Evidence

- RESULT the round-2 block is answered. I applied the reviewer's own diffs from verdict/3475@59e4eca to the head unchanged (`ev/mut_2_*.diff`, `ev/mut_3_*.diff`, `ev/mut_4_*.diff`) and ran the self-test under `ulimit -u` with timeout 500:
  - `diff_forkcap_branch`: KILLED, 59 checks, 2 failed (the diff-mode FORKCAP check and the `--report-only` FORKCAP check), rc 1 (`ev/mut_diff_forkcap_branch.txt`).
  - `null_forkcap`: KILLED, 1 failed (`FORKCAP NULL, rc 3, no mutant run`), rc 1 (`ev/mut_null_forkcap.txt`).
  - `headtail`: KILLED, 1 failed (the STMT_DEL shared-line check), rc 1 (`ev/mut_headtail.txt`).
  These match the body's "2 / 1 / 1 failed".
- RESULT partial mutants of the shared-line guard (my own, written beyond the block's list so that any remaining survivor shows up in this round): I dropped the head clause (`ev/mut_headtail_nohead.*`), dropped the tail clause (`ev/mut_headtail_notail.*`), and dropped the trailing-comment exemption (`ev/mut_headtail_comment.*`). Each was KILLED with 1 failed, the same shared-line check. The fixture's expected `sites == [4]` separates all three: line 2 tests the head and the tail, line 3 tests the head, and line 4 tests the comment exemption.
- RESULT self-test at the head: 59 checks, 0 failed, rc 0 (`ev/selftest_head.txt`). This matches the body's 59 (55 + the 4 new checks).
- RESULT delta review: the new checks assert exact outputs (`["FORKCAP NULL"]` with the stderr reason, rc 3; two `FORKCAP lib.py:N OP` lines, rc 1, in under 40 s; rc 0 under `--report-only`). They are not loose assertions, and the mutant kills above confirm that each one pins its branch. The delta touches only test code inside the self-test, with no production change. The body's other mutants were settled in rounds 1 and 2, and I did not re-run them.
- RESULT `git merge-tree --write-tree origin/main fe859f35`: rc 0, no conflict (`ev/merge_tree.txt`).
- RESULT figures: I re-derived the self-test count (59) and the three mutants' failure counts at this head. I did not re-run the body's `tools/pr/prepr.sh` line or the finder's E1/E2 harness at this head. The delta is self-test only, and those results were settled in round 2. The `## Figures` line "55 checks, 0 failed" is the pre-repair count. The body labels it as such in `## Mutation proof` ("55 ... before the third block's four checks; 59 now"), so it is stale wording, not a false claim.
- RESULT carry: the body's `Carry: R10-MUTANT-RUN-FORKCAP` residual (MUTVAC-STMT-DEL acceptance, which has not been measured) is unchanged from round 2. The review packet's carry_audit reports 1 routed, 0 unrouted.
- RESULT owed-reds set: `ev/owed_reds.txt`.
- RESULT CI: `merge_train.py classify fe859f35... --pr 3475` polled every ~70 s from 21:54 to 22:26Z, always `WAIT fe859f3563735327627c5de908b8fb95cde42e7f pending: gate red: none` (`ev/classify_last.txt`). No required check is red. I stopped waiting after 30 minutes, as the brief allows, and the relay posts this verdict only once CI is green at this head.

Fix review: merge 8c008227a25192fc542bca64abbd4098a2862d1a

PR #2569 (R10-ROSTER-PUSH-RACE), round 2: re-review after the fixer's main merge d729496d9 (resolving tools/audit/seat/roster_edit.py) and the automatic main merge 8c008227a. Measured head 8c008227a25192fc542bca64abbd4098a2862d1a, the PR head at the start and at the end of the review; origin/main 49c222280 is its merge base (0 behind). Roles diff merge-base...origin/main -- dev/governance/roles/ is empty, so this contract is current.

RESULT merge-tree origin/main..head: exit 0, tree 92550c62bf == the head's own tree (ev/merge_tree.txt)
RESULT self-test head: roster_edit self-test: 106 checks, 0 failed; origin/main: 94 checks, 0 failed (ev/selftest_*.txt)
RESULT failing-test-first e19bda54f: 82 checks, 7 failed, the 7 race/non-race FAILs the body quotes (ev/failing_test_first_e19bda54f.txt)
RESULT mutants M1-M7 (the body's exact replacements; I wrote the driver myself, ev/mut.py): M1 7 failed, M2 7, M3 2, M4 1, M5 4, M6 AttributeError before the tally, M7 TypeError before the tally. All match the body. File restored, git diff --exit-code clean.
RESULT my own extra mutants: R1 push by branch name: self-test aborts rc 1. R3 no discard: 7 failed. R4 return 0 after exhausting: 1 failed. R5 'pushed' ignoring rc: 7 failed. R6 set-after dropped from apply_op: 18 failed. R7 no lint on re-apply: 3 failed. R2 (drop the re-fetch before classifying a rejection) SURVIVES the self-test (106/0), because the self-test's rival pushes through the same checkout and so updates origin/<branch> itself. See the R2 note below.
RESULT reviewer race harness, base 49c222280 vs head 8c008227a (5 runs per race arm with B delayed 2/4/6/8/12 s, 2 solo runs; ev/rev_race_tally.txt):
  base shared: 5/5 rcA=0 silent_losses=1 false_reports=1 pushes=1 (the 2026-10-21 shape, reproduced)
  head shared: 5/5 silent_losses=0 false_reports=0 refused=0 pushes=2, 'lost a race' said
  base separate: 5/5 silent_losses=0 refused=1 (a loud rc 2)
  head separate: 5/5 silent_losses=0 false_reports=0 refused=0 pushes=2, 'lost a race' said
  solo (null control), both trees: 2/2 silent_losses=0 refused=0 pushes=1, no race said
RESULT head+R2 under my harness: separate arm rcB=2 refused (no silent loss, no false report); shared arm still pushes=2.
RESULT checkout -B / branch -f / update-ref in tools/: only the two comments at roster_edit.py:32 and :1110; no code path creates or moves a local branch (ev/class_rule.txt)
RESULT cheap checks at head (venv-ci 3.14.7, PYTHONPATH=tests/hastub): closure select vs 49c222280 and vs e9febe622: MODE: SCOPED -- 1 script(s) run, 32 scoped out, RUN tests/entities.py; entities ALL 2375 ENTITY CHECKS PASSED; structure STRUCTURE RATCHET PASSED; harness_headers ALL 109 PASSED; layout ok; env_drift --claims-only ok; tmp_paths 0 refused; ref_privacy self-test 66/0; closure selftest ALL 124 PASSED (ev/cheap_checks.txt, ev/closure_select*.txt)

Harness (step 9). No finder harness is committed. The roster brief at origin/handoff/audit-r10-roster (f424d993d, group R10-ROSTER-PUSH-RACE, read with jq) prescribes a procedure: "reproduce with two concurrent edits in a scratch bare repo". dev/audit/harnesses/r10_roster_push_race.sh is the fixer's own instrument. It is visible as added in this diff, but the body calls it "The harness" without saying the fixer built it. I did not use it. I built my own reproduction from the brief's words, ev/rev_race.sh, and disclose it as mine. It uses a real bare repo, the real r10 roster from the handoff branch, the real brief_lint (a ~16 s lint window) and two concurrent roster_edit.py --push processes. Its figures above agree in direction and shape with the body's (base shared loses edits and reports false shas; head loses none; separate clones never lose silently).

Re-verification after the conflict resolution (brief):
- --push never prints 'pushed' with rc 0 for a commit not on origin: false_reports=0 in all 10 head race runs. The 'pushed' print sits only on r.returncode == 0 of a '<sha>:refs/heads/<branch>' push. R5 and R1 are killed.
- Re-fetch/re-apply on a moved tip, at most 3 attempts, then rc 2: head shared and separate both re-apply and land both edits. The bound and the rc 2 are pinned by the self-test's race-on-every-attempt arm (M3, R4 and R7 are killed).
- No local checkout -B or branch -f of the shared roster branch remains: prepare_worktree checks out '--detach base_sha' only (M5 is killed).
- Main's code in roster_edit.py is intact. I diffed the merged file against origin/main's version (ev/roster_edit_vs_main.diff). Every hunk is the fix's own: the docstring, PUSH_ATTEMPTS, apply_op, prepare_worktree, the attempt loop in main(), and the self-test additions, plus one tally line. apply_op carries main's nine-way dispatch verbatim: set-stage, wire-issue, unwire-issue, append-group, edit-brief, set-resume, set-after, drop-carry, and the else branch append-carry. The arguments are unchanged, including match to drop-carry (M6, M7 and R6 are killed). The lint gate, the ref_privacy refusal, the no-op 'no change' path and roster_lib.roster_path are unchanged. Every attempt re-runs the lint gate. The tally change from passed+len(failed) to passed is correct, because check() increments passed on every call (line 630).

Class (step 6). I ran the body's rule at head. The file set equals the set at 5d433771a (diff exits 0). I opened each hit the body leaves as 'remaining' (ev/class_remaining.txt): audit-find.js has push instructions in agent prompts; cloud_dispatch.py's hit is a prompt string; r10_deeplink_mutants, fragments_sync, cancel_superseded, codeql_scope and contract_rerun are fixtures or the word 'push'; r9_rc_bus_fetchhead.sh is a harness; ref_privacy.py hits are its self-test. One correction: merge_train.py:1794 is a production 'git push --delete' (line 2969 is a self-test stub). It reports 'deleted' only on rc 0 and otherwise logs NOT deleted, so it is guarded and outside this class. The body's 'none is a production push' is therefore slightly overstated, but no seam is left open.

Non-blocking notes:
1. Survivor R2: the self-test does not pin the re-fetch, so the separate-clone retry is unpinned. Without the re-fetch, a rival from another clone turns the run into a loud rc 2 refusal, which the brief permits ("re-applies ... or refuses with a non-zero exit"). The fixer's separate arm and mine both catch it. Worth one self-test case with a rival from a second clone in a later touch.
2. prepare_worktree's docstring has a garbled clause: "a HEAD the base does no origin ref contains".

Step 4/5: no fixture, claim file, VERSION, manifest or RELEASE_NOTES heading is in the diff. Step 7: the body's head paragraph names 8c008227a and its parents correctly. Step 8: the body's harness counts are the fixer's harness's, at d729496d9. I re-derived only their direction with my own harness; I did not re-run its exact 10-run tallies. Step 10: the forward-carry is 'n/a' and INSTRUMENTS.md in this diff carries the seat-facing change; no later stage is affected. Step 14: tests/closures.json gains only the new harness path under harness_headers, and no budget moved.

Step 11 (CI, read once at the end; ev/checks_final.txt):
- Still running: closures and Analyze (python). I judged on the rest.
- The one red check is nightly-status, which grades main's last scheduled Tests run. This diff does not reach what it reads, and the body names and answers it.
- The earlier-round pr-contract red at aff55f82 is answered in the body.
- Both pr-contract runs at this head are green (16:20:27Z, 16:23:13Z). Both started before nightly-status concluded at 16:25:36Z, so no pr-contract run postdates the head's last workflow yet. The body's red-check section already names nightly-status, so nothing is unanswered.
- mutation is green; I did not read its log, and my targeted mutants stand in for it.

Round 2.

bus-nonce: 060a085f4ed98e9def007eee9b4aa4d7

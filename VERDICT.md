Fix review: merge 194a75594646a73e2f55facf8f63071b5b7e346c

bus-nonce: 8de97aa0fdcc04d96fdc1a747a2674e0

Round 1, full scope. Reviewed from detached worktrees at the head, at origin/main 921214bf4246338c1a83fbc5269eaa0bfe91b7d5 (the merge base) and at p2's commits. The role contract is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Evidence

- Diff, three-dot from 921214bf42: `tools/audit/prepare_baseline.sh` (+5 -2: `ISOLATED_DIMS` gains D16, one comment line names it, three explain it) and the delivery row `dev/programme/delivery/3646.md`. No production, test, budget, closure, golden or claim file; `VERSION`, `RELEASE_NOTES.md`, `custom_components/` and both claim files are byte-identical to the merge base (ev/untouched.txt).
- Mutation proof, re-run with the committed grader `node tools/policy/check-wave-script.mjs` (identical on main and in p2's tree), on p2's tree 910986a0bc:
  - RESULT p2 tree with main's copy of prepare_baseline.sh: 221 passed, 2 failed; the two failing lines are the ones the body names, the first quoting `ISOLATED_DIMS [D0,D3,D9,D11,D13,D14,D15] != audit-find.js ISOLATED [D0,D3,D9,D11,D13,D14,D15,D16]` (ev/wave-p2-maincopy.txt).
  - RESULT p2 tree with this head's copy: 223 passed, 0 failed (ev/wave-p2-headcopy.txt).
- My own mutants of the added entry:
  - RESULT M1, p2 tree, head's copy with D16 replaced by D17: 221 passed, 2 failed (ev/mut-M1.txt).
  - RESULT M2, p2 tree, head's copy with D16 deleted: 221 passed, 2 failed (ev/mut-M2.txt).
  - RESULT M3, this head with D16 replaced by D2, a declared dimension: 221 passed, 2 failed (ev/mut-M3.txt).
  - RESULT M4, this head with D16 deleted: 223 passed, 0 failed, pending: none (ev/mut-M4.txt). Flat by design: at this head nothing but p2 depends on the entry, so the proof is the p2-tree pair above and its companions M1 and M2.
- Null control, both ends: RESULT head 194a755946: 223 passed, 0 failed, `(pending: D16)`; RESULT origin/main 921214bf42: 223 passed, 0 failed, `(pending: none)` (ev/wave-head.txt, ev/wave-main.txt). The body's two commits re-derive the same: 4d381a338f 223/0 pending D16, 98847b99d7 223/0 pending none (ev/wave-figures.txt). `bash -n tools/audit/prepare_baseline.sh` exits 0 at the head.
- Scope line re-derived: `python3 tests/closure.py select --diff 921214bf42` at the head prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` (ev/scope.txt). `git diff --stat 98847b99d7 4d381a338f`: 1 file, 5 insertions, 2 deletions, as the body states.
- Class: one seam. `git grep ISOLATED` at the head returns the driver's set (`.claude/workflows/audit-find.js:65`, p2's to move), this file's list and its three loops over it, and the grader; no other tracked list of the isolated dimensions exists outside the round archives and the register. The script's loops read the one list, so the worktree, the start check and BASELINE.md follow the entry with no second edit.
- Design: the note at a9377bcf47 section 3.4 gives D16's isolation for the two reasons the comment states and keeps D17 in the export; its build order says to report a base-copy refusal as the split, so the three own-group carries name a split part the approved design names, and the fourth names a pending orchestrator decision (`fixer.md`).
- Merge: `git merge-tree --write-tree origin/main 194a75594646a73e2f55facf8f63071b5b7e346c` exits 0, tree 9c25e12532788222f0106d2daec759397674c015.
- Claims: `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 921214bf42` at the head: rc 0, `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`; the branch claims nothing and both claim files are unchanged (ev/env_drift.txt).
- Finder's harness: none named, and none is owed a build: the group is pre-round instrument work and its judge is the committed grader above, run here at both ends.
- Not re-derived: the body's `tools/pr/prepr.sh` rc 0 at 4d381a338f (not re-run), and its `ci_predict.py` quote for p2. The predictor run today on p2's head 4f73a0c5e8 prints `GRADER UNMERGED` on every arm, because p2 no longer merges with main (ev/predict-p2-base-main.txt); the grader run with main's copy, above, reproduces the string the body quotes from it.
- CI at this head: `python3 tools/audit/seat/merge_train.py classify 194a75594646a73e2f55facf8f63071b5b7e346c --pr 3646` exits 0 with `GREEN 194a75594646a73e2f55facf8f63071b5b7e346c pending: none red: none` (ev/classify.log). The head's check runs, read from the pull request, show no failure on any run of any check; `governance / wave-script` and `governance / instrument-self-tests` concluded success. `tests / mutation` is green and evaluated nothing here (the diff writes no production line); nothing above rests on it. No red is owed an answer.

## Findings

- Follow-up: p2 at 4f73a0c5e8 does not merge with main at 921214bf42 nor with this head: `git merge-tree --write-tree 4f73a0c5e8 194a75594646a73e2f55facf8f63071b5b7e346c` exits 1 with one conflict, `CLAUDE.md`; `tools/audit/prepare_baseline.sh` auto-merges, as the body says (ev/merge-p2.txt). The merge of main into p2 that the body's forward-carry owes therefore needs a hand resolution in `CLAUDE.md` before `prepr.sh` can run there. Carry: R11-PRE-NEW-DIMENSIONS

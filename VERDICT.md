Fix review: blocked 37d1d0d38fd0ef449c55abe49f6c70b0604b8e4b merge-conflict: dev/audit/harnesses/r10_seat_selftests_mutants.py conflicts with origin/main 8a4c438e7

bus-nonce: 4c799023a1d8027c0080d2363644d4f8

Round 3, a re-review of a moved head. I measured head 37d1d0d38fd0ef449c55abe49f6c70b0604b8e4b from detached worktrees. `git ls-remote` at 08:51Z still shows the PR head and `fix/r10-flow-main-gate` at that SHA (ev/head_reread.txt). The contract is current: the role diff from the merge base to origin/main is empty, both at b787c7d45 and at 8a4c438e7. Every figure below was taken at this head. K15 commits no finder harness, so I used the fixer's own e7c66485 replay, which the body now labels as the fixer's, together with my own perturbations, which I disclose here.

## Block

- fix-review.md step 13. While this review was running, main moved from b787c7d45, the base the body absorbed and that my measurements started against, to 8a4c438e7. `git merge-tree --write-tree origin/main 37d1d0d38` now exits 1 with `CONFLICT (content): Merge conflict in dev/audit/harnesses/r10_seat_selftests_mutants.py`, and that is not a claim file. GitHub's merge, with no driver, also lists `tests/closures.json`, which the local ledger driver resolves (`LEDGER-MERGE: resolved tests/closures.json`, inert_reads merged as a set) (ev/merge_tree.txt). The conflicting change on main is ab80640b8 (#2578, r10-flow-body-patch). It adds the mutant `body_patch-1` before `tick_loop-1` and rewrites the docstring line this PR also rewrote (ev/main_moved.txt). The repair is to merge origin/main and keep every tuple from both sides: S01..S38, this PR's 23 per-file ids, `body_patch-1`, `tick_loop-1..2` and `heartbeat-1..4`. That makes 65 by my count. The general docstring wording must still be true of the merged list. Then re-take the harness run. As a trial I merged the auto-merged files only (the harness left conflicted) into 8a4c438e7: the tick gives `194 checks, 0 failed` (main's #2585 MAIN D-1 arm included), merge_train gives `219 checks, 0 failed`, and merge_pr gives `18 checks, 0 failed` (ev/trial_merge_selftests.txt). So I found no semantic conflict in the files git merged. Per step 12, the next round judges the resolution delta only. Carry: dismissed: blocks this PR, fixer re-absorbs 8a4c438e7 (item 2584f3a1)

## Findings

- None beyond the block. Every item below re-measured as the body states, at this head. Carry: dismissed: nothing owed beyond the block (item 2584f3b2)

## Evidence

- The round-2 block (carry-missing) is cleared. `carry_audit.py check --body <PR body>` prints `CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)`. With `--roster-ref origin/handoff/audit-r10-roster` it prints the same line, and carry_audit.py is byte-identical on main and at the head (ev/carry_audit.txt). The roster SHA the body names, e5d5c508465fd5a5c279ae87e12350fd0f7f082f, is an ancestor of origin/handoff/audit-r10-roster. At that SHA, and at the branch tip, R10-ORCH-MACHINERY's `carry` holds both entries:
  - The pre-dispatch entry: `merge_train.py classify <head>` must exit 0 or 3. Its control is the exit codes.
  - The readers entry: the beat, the sweep, record_row.py, ci-watch.sh and proof_watch.py read `merge_train.classify`, and no third red rule is written. It states as a build precondition the e7c66485 replay through each reader: `--pending mutation typing closures` must read a wait, and the null control, no `--pending`, must print only END.

  The control-less entry from cb5a00e1a is gone. R10-ORCH-MACHINERY is a live, not-started group on main's roster, both at b787c7d45 and at 8a4c438e7. At 8a4c438e7, main's own roster already carries both #2584 entries (ev/roster_carry.txt).
- The main-absorb resolutions (b787c7d45) are sound:
  - The mutants harness: I parsed `MUTANTS` with `ast` at bf10abe6 (54), at b787c7d45 (41) and at the head (64). No tuple from either side is dropped or altered, and the head adds none of its own, so the head is their union.
  - INSTRUMENTS.md's merge_pr.sh entry keeps both sentences: this PR's `merge_train.py unstale`, and #2444's offline flow.
  - closures.json gains exactly two lines: this PR's harness entry, and the tick inert read.
  - `git diff b787c7d45 37d1d0d38` touches only the PR's own 8 files. The PR-side delta of orchestrator_tick.py and merge_pr.sh is the same as at bf10abe6 against 57f0c9c77, apart from the 70a1a1fb copy line (ev/closures_diff.txt, ev/diff_vs_main_stat.txt).
- 70a1a1fb is architecturally sound. `unstale_head` calling `merge_train.py` is the K15 "one owner" design this PR implements. The scratch clone stands in for a checkout, so copying the real file reproduces the production dependency and does not mask it. At the head the merge_pr self-test gives `18 checks, 0 failed`. With the copy line deleted it gives `18 checks, 1 failed` (`FAIL null control: the merge records the reviewed head (STALE: a re-run did not clear #42's head)`). Replacing the copy with an exit-0 stub gives 18/0, which bears out the body's reason for rejecting a stub. Both `merge_pr-1` and `S38` are KILLED, and the unit arm of `unstale_head` drives a fake run list (ev/merge_pr_copy_mutant.txt).
- 37d1d0d3 is correct. `closure.is_inert("tools/audit/seat/orchestrator_tick.py")` is True: the file is under the `tools/audit/` prefix and on no INERT_EXCEPT line. The entry sits under `inert_reads`, not in a closure, so `inert_closure_violations` is not engaged. The read is real. Under strace, `tests/entities.py` at the head spawns `node tools/policy/policy_lint.mjs`, which opens the head's `tools/audit/seat/orchestrator_tick.py` and 54 other seat files (ev/entities_reads_tick.txt). At 70a1a1fb, ci_predict predicted `INERT READS tests/entities.py: tools/audit/seat/orchestrator_tick.py (a new file beside 8 it lists)`. That came from its siblings arm, keyed on a changed file. Main's 188c5728b has since narrowed that arm. The entry is accurate either way (ev/ci_predict.txt).
- The mutation proof, re-run in full at the head (ev/selftests_and_mutants.txt): `M0: 0 seat step(s) red`, 71 `KILLED`, `RESULT survivors=0`, exit 0, and the tree is clean afterwards. Each failed count for merge_train-1..18, merge_pr-1 and orchestrator_tick-1..4 equals the body's: 6/12/1/1/2/2/3/1/1/4/1/2/2/1/1/1/1/1, then 1, then 3/2/3/1. The null control for each mutant is the same step on the unmutated file, which the harness runs first.
- Self-tests at the head: merge_train `219 checks, 0 failed`, orchestrator_tick `190 checks, 0 failed`, merge_pr `18 checks, 0 failed`, and `selftest_wiring: 76 self-testing, 76 wired, 0 unwired`. These equal the body. The null controls are the mutant runs above.
- The e7c66485 replay, re-run. I re-ran it rather than relying on the byte-unchanged claim. That claim also holds: merge_train.py is blob 5e8af935 at both bf10abe6 and the head, and the replay harness is blob b0de602e, sha1 266e441f, at both. Against a `git archive origin/main` export (merge_train.py d09c3072), no `--pending` prints only `END`, and `--pending mutation typing closures` prints `... is not green (closures, mutation, typing) ... revert it first`. At the head, no `--pending` prints only `END`, and with `--pending` it prints `... is still running (closures, mutation, typing): a wait, not red`. These equal the body (ev/replay_e7c66485.txt).
- The cheap checks at the head equal the body (ev/cheap_checks.txt):
  - `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, and `scope.run` is `tests/entities.py`.
  - `ALL 2382 ENTITY CHECKS PASSED` (venv-ci, under strace; ev/entities_head.txt).
  - `STRUCTURE RATCHET PASSED`.
  - `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `ALL 124 closure shrink pins PASSED`.
  - `layout self-test: ok`.
  - `claims hygiene: origin/main ok`.
  - `Architecture score: dS +0.0000 NULL`.
  - throwaway_git, tmp_paths and ref_privacy each refused 0.

  VERSION, the manifest, RELEASE_NOTES, both claim files and every `*_budgets.json` are untouched.
- CI from the check-runs API at the head (46 runs; ev/ci_head.txt): no run concluded failure. `closures` (119716569668, which needs `coverage`) was still in progress at 08:51Z. It is the lane that re-records the inert read, so I could not cite its conclusion. The local strace reading above is my evidence for that entry. nightly-status is green at this head, so `## Red checks` answers a red from an earlier head. That is not a gap.
- Class rules: the CI-state code is unchanged since round 2, where both rules were re-run and dispositioned. Merge_train.py is byte-identical, and the tick's PR-side delta is unchanged. I did not re-run them here.
- The body's statements about its own record (`Group: ... (registration pending: roster PR-B)`, and "R10-FLOW-DISPATCH is not on the roster yet") are out of date at 8a4c438e7, where both groups are on main's roster. The carry destination is unaffected: R10-ORCH-MACHINERY is still not started, and main's roster holds both carries.

Fix review: blocked 2a1a7de05b0c080029817dd4208864c5ef7e9f6a mutation-vacuous: P13-main-uses-inline-receipt-line P12-codesteps-drops-scoped-test G6-cli-ignores-ref unanswered at this head

bus-nonce: 9fffe9d4e11c3fdce028dc32afaa4b0c

## Block

This is the third round, a delta round over the reviewed head b53bbf1604a3720aeb665a3b51219eb54df1fe6a. The packet's scope reads `delta`. The delta is one commit, 2a1a7de0 "ci: merge main", whose parents are b53bbf16 and origin/main 7aac3e7c. The PR's own diff against its merge base is byte-identical before and after it: `git diff 7eadd75f b53bbf16 -- tools/pr` equals `git diff 7aac3e7c 2a1a7de0 -- tools/pr` (`ev/own-diff-compare.txt`, empty). The one dropped hunk is the `tests/closures.json` `harness_headers.py` rc line, which main now carries. The delta adds no PR-authored `custom_components/` line, so the review is not widened.

The previous verdict blocked on three surviving mutants, and none of them is resolved. Nothing in the code addresses them, and the PR body, read live at this head, neither pins nor answers them. Its `## Mutation proof` still covers only round 1's survivors.

- P13-main-uses-inline-receipt-line: re-run at this head. The mutant replaces `tools/pr/prepr.sh:4273` `code_steps_line "$REUSE"` with the pre-PR inline receipt line (`ev/P13.diff`). `prepr.sh --self-test` still prints 550 passed, 0 failed, rc 0 (`ev/P13.log`): SURVIVED.
- G6-cli-ignores-ref: re-run at this head. The mutant changes `tools/pr/gate_priority.py:367` from `ref=args.ref` to `ref=None` (`ev/G6.diff`). `gate_priority.py --self-test` still prints 21 checks, 0 failed, rc 0 (`ev/G6.log`): SURVIVED.
- P12-codesteps-drops-scoped-test: not re-run. `code_steps_line` at `tools/pr/prepr.sh:1784-1787` is unchanged, and no `hs` row passes a caller value of `hotfix`, so the round-2 survival stands.

To clear the block, pin each survivor or answer it in the body. Round 2's verdict gives the cheap pins: an awk row asserting the main flow calls `code_steps_line "$REUSE"`; an `hs` row with `PREPR_SKIP_CODE=hotfix`; and a fixture whose `--ref` differs from the local roster ref. An equivalence argument in `## Mutation proof` suffices for P12 and G6.

## Evidence

- `date -u` at start: Fri Nov 13 22:25:27 UTC 2026.
- RESULT head: `git ls-remote origin refs/pull/3547/head` printed 2a1a7de05b0c080029817dd4208864c5ef7e9f6a (`ev/HEAD.txt`).
- RESULT merge: `git merge-tree --write-tree origin/main 2a1a7de0` exited 0 with tree d82afdfe and no conflict (`ev/merge-tree.txt`). origin/main is 7aac3e7c, which is this head's own second parent.
- RESULT CI: `merge_train.py classify 2a1a7de0 --pr 3547` printed `WAIT ... pending: gate red: none` (rc 3, `ev/classify-1.txt`). I did not wait for CI to finish, because the block is mutation-vacuous and CI cannot clear it. The round-2 note on an INTRODUCED `instrument-self-tests` red needs the train to re-prove it at a green head.
- RESULT owed reds: `ev/owed-reds.txt`.
- Mutant drivers: in-place `sed` edits in detached worktrees at the head. These are the same mutants as round 2's `ev/driver.py`, re-applied by hand, not the finder's harness (none is named).
- No figure in the body changed in the delta, so none was re-derived beyond the G6 run's 21 checks and the P13 run's tally.

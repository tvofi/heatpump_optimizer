Fix review: blocked fca6e07bb4189f6cb9768ea499a9ff818c7f8ea9 body-stale: the body describes the previous change (ROWLESS on a refused row push, 144 checks, no mut:rowclose), not this diff's close-on-refusal

bus-nonce: 00451e136f519ed599922e9b8d976097

## Round

Round 1 for this head. Measured head: fca6e07bb4189f6cb9768ea499a9ff818c7f8ea9. Merge base and origin/main: 039eee1dc9c210edd31a6e1a806f4ceb9c0d048b. The roles diff from the merge base to main is empty, so the contract is current.

## Block

The diff (46d225b21, then the row commit fca6e07bb) makes a refused row push **close** the PR, after posting a comment that gh_comment.py reads back, and print `open_pr: CLOSED: #N`. ROWLESS is now printed only when the close itself fails. The PR body describes the change that already merged before this one:

- Paragraph 2 and carry 1 say a refused row push "prints `open_pr: ROWLESS: #N is open ...`" and that `update_pr.sh fix/r -` then "exits 0 with `dev/programme/delivery/5.md` on origin". At this head the self-test asserts the opposite. The main `rowless -` arm requires `! grep -qF ROWLESS`, `no open pull request at fix/r` and `rowpushed = 0`.
- `## Mutation proof` does not name `mut:rowclose`, which is this diff's one new production mutant. It still describes `mut:rowreset` as "`update_pr.sh` refuses `(unpushed work`", but this diff removed that assertion from the arm.
- `## Figures` says "144 checks, 0 failed" at the head and says "5 changed files". At this head I measured `pr_args self-test: 152 checks, 0 failed` (ev/self-test-head.txt), and the three-dot diff has 4 files. The figures were taken at `f2f569d4c`/`0ce0c6f8b`, and neither commit is in this PR's range.
- `## Head` names dispatch base `ed1c9045` and figures taken at `f2f569d4c`, not this range.

Under fix-review.md step 8, none of the body's figures is verified at this head. Its stated behaviour contradicts the code and the tests, so the body has to be re-cut for this diff before it can be reviewed.

## Findings

- A re-run after a CLOSED exit cannot open, but the closing comment and the CLOSED line tell the seat to do exactly that ("Re-run `open_pr.sh <topic>` once the handoff body answers it"). After the close, `pr_release_wt` (pr_args.sh:150) detaches the worktree and keeps both `$D/wt` and the local branch, because origin holds the branch. On the re-run, `open_pr.sh:37` either renames BR to `$BR-pr` or keeps it, and `open_pr.sh:52` `git worktree add -q -b $BR $WT $C` then fails. It fails with `'…/wt' already exists` when BR was renamed, and with `a branch named … already exists` under BR_FIXED (ev/rerun-repro.sh and ev/rerun-repro.txt reproduce this with real git). Even once both are cleared, the re-run pushes again to a branch whose closed PR still exists. The old recovery path (`update_pr.sh … -` plus ensure_row) is also gone for a closed PR: the arm asserts that `update_pr.sh` answers `no open pull request at fix/r`. So the fix turns a recoverable rowless PR into a closed PR with no scripted recovery. The `rowless -` arm should run the prescribed re-run and require it to open, or the close path should remove the worktree and local branch and the re-run path should handle an existing remote branch. Carry: R10-FLY-OPENPR-ATOMIC
- The rewritten `mut:rowreset` arm now asserts only `opwt = branch` and `rowpushed = 0`. Because the fixed path also leaves `rowpushed = 0`, only `opwt` discriminates the mutant. That is adequate today, but the arm no longer pins the #2625 refusal it is named for. The body should say so, or the arm should keep a discriminating second assertion. Carry: R10-FLY-OPENPR-ATOMIC

## Evidence

- RESULT self-test head: `bash tools/audit/seat/pr_args.sh --self-test` at fca6e07bb gives `pr_args self-test: 152 checks, 0 failed`, exit 0. The arms `open_pr: a refused row push closes the PR with a read-back comment naming the refusal…`, `mutant mut:rowclose` and `mutant mut:rowreset` read ok (ev/self-test-head.txt). The built-in mutant arm deletes the `# mut:rowclose` line and requires that the PR stays open, so mutation step 1 is not vacuous for that line.
- RESULT merge: `git merge-tree --write-tree origin/main fca6e07bb` exits 0 with tree 5dc093db27d1822650a7aee9edd372dd5c859a24 and no conflict, because the head already contains origin/main 039eee1dc (ev/merge-tree.txt).
- RESULT VERSION: VERSION, the manifest version and the RELEASE_NOTES heading are untouched. The diff covers only tools/audit/seat/{open_pr.sh,pr_args.sh,instruments/open_pr.sh.md} and dev/programme/delivery/2989.md. No golden or claim file is touched, so `env_drift` has nothing to compare.
- RESULT CI at review time: 39 check-runs on the head and none red. These were still in progress: tests / fast (3.14), tests / closures, tests / browser, tests / graders-head-copy, governance / env-matrix, governance / instrument-self-tests, codeql / Analyze (python) and prelude. No pr-contract run was listed. Step 11 therefore has nothing to answer yet. I did not wait for completion because the block does not turn on CI.
- No finder's harness is named (the packet says "none named"). The finding is a tooling flow, and the self-test fixture is the fixer's own instrument.
- The packet's carry_audit reports 1 item, routed to R10-FLOW-BODY-ONLY (the V64 auto-open carry, unchanged by this diff). figure_lint resolves 15 of 15, but only checks that the paths exist, not the numbers.
- The head is unchanged at verdict time: the PR API reports head.sha fca6e07bb4189f6cb9768ea499a9ff818c7f8ea9.

Fix review: blocked 50b1956485ea01e78d97a0619a32cdc9dd923cdd class-open: open_pr.sh:80-87 a step failing after the PR is created exits under errexit and leaves it open without its row, unclosed

bus-nonce: 50e1c8a1ef2b25c1685ed4027bfb79fa

## Block

Issue #2719 sets the class: open_pr.sh must "close the draft with a comment saying why when a later step still fails". The body says "Closing is the smallest change that keeps every open PR with its row". The diff closes on only one later step: a refused row push (p2). The steps between creating the PR (p1) and p2 run under `set -Eeo pipefail` (`pr_trap`). These are `gh pr edit $N --title` (line 80), `commit_row` (81) and the head_note prefix (83-87). When one of them fails, the ERR trap stops the script, and the EXIT trap only writes the ledger, reaps the tree and releases the worktree. Nothing closes the PR. A stop signal at that point has the same effect. The body neither dispositions these sites nor names an enumeration rule.

Demonstrated at this head with the PR's own harness (patch in ev/demo-patch.txt). In the `rowless -` arm, the stub's `gh pr edit` exits 1 and p2 is allowed to succeed. Result: `open_pr: STOPPED: line 80 exited 1: gh pr edit $N --title "$TITLE" > /dev/null`, closed=0, and open_pr exits 1. The stub's `pr list` still lists #5 as open, with no row from open_pr. The arm's later update_pr.sh is the only reason rowpushed=1 (ev/demo-edit-fails-state.txt, ev/demo-edit-fails-outo.txt). Fix: run the close-with-comment path for any non-zero exit after N is known, for example from the EXIT trap while PR_ATTEMPT is unset and N is set. Alternatively, disposition each site in the body.

## Findings

- open_pr.sh:96-101 posts the comment "Closed by open_pr.sh: ..." before `gh pr close` runs. When the close fails (the ROWLESS branch), the PR stays open under a comment that says it was closed. Post the comment only after the close succeeds, or word it for both outcomes. Carry: R10-FLY-OPENPR-ATOMIC

## Evidence

RESULT head-measured: 50b1956485ea01e78d97a0619a32cdc9dd923cdd. It is still the head of fix/r10-fly-openpr-atomic-pr (git ls-remote at verdict time). Round 1 for this reviewer.
RESULT self-test-head: `bash tools/audit/seat/open_pr.sh --self-test` exits 0: `pr_args self-test: 154 checks, 0 failed`, `delivery_row self-test: 6 checks, 0 failed`, 160 lines matching `^  ok`. This matches the body's 154 and 160 (ev/selftest-head.txt).
RESULT mutation: the in-tree mutants mut:rowclose, mut:rowreset and mut:mergeabort each print ok in that run, so each deleted line turns its arm's assertion. They are not vacuous.
RESULT failing-test-first: head pr_args.sh with base fe709cbd open_pr.sh exits 1. The only two FAILs are the close arm and the merge-conflict arm, as the body claims (ev/selftest-base-openpr.txt).
RESULT merge: `git merge-tree --write-tree origin/main 50b1956485ea01e78d97a0619a32cdc9dd923cdd` exits 0 against origin/main 559134e (ev/merge-tree.txt).
RESULT figures not re-derived: the 151/157 counts at the merge base, closure.py's "MODE: SCOPED -- 0 script(s) run", and structure.py's PASSED were not re-run. figure_lint resolves all 3 in the packet.
RESULT CI on this head (check-runs API, ~11:57Z): no check concluded failure. Two `gate` runs and one `pr-contract` run were still in progress, and the `Red checks: none` answer was not re-checked once they concluded. That does not change this block.
RESULT VERSION, manifest version and RELEASE_NOTES heading are untouched. The diff is 4 files and changes no claim or budget file.

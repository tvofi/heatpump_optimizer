Fix review: blocked 50b1956485ea01e78d97a0619a32cdc9dd923cdd figure-wrong: body says the head self-test has one arm more than the merge base; it has three more (151 to 154)

bus-nonce: 81a3f6d8784483c8ba64d7d64969fdb4

Round: 1 (first review of this PR). Measured head: 50b1956485ea01e78d97a0619a32cdc9dd923cdd, base fe709cbd269c7c53eb1c846a0be7f39c7dab06ac (merge base = origin/main at review time).

## Block

The body's Figures section says: "self-test at the head: ... exits 0, and every arm prints `ok` (one arm more than at the merge base, the new close arm)". Re-derived: the merge base prints `pr_args self-test: 151 checks, 0 failed` and the head prints `pr_args self-test: 154 checks, 0 failed`, so the head has three arms more. That fits the diff: the base had two arms (rowless and its rowreset mutant). The head has five: the close arm, the rowclose mutant, the rowreset mutant, the merge-conflict arm and the mergeabort mutant. The figure is false, and the record must not carry it (fix-review.md step 8). A body edit fixes it without moving the head. Fix the finding below in the same round.

## Findings

- Surviving mutant: deleting `PR_ATTEMPT=closed,PR=$N` (open_pr.sh:104) leaves the head self-test at 154 checks, 0 failed, exit 0 (ev/mutant-attempt.txt). The body claims "The ledger attempt records `closed,PR=<n>`", but no test pins it. Without that line, a closed PR's handoff ref records `unopened` in the ledger. The tick's DISPATCH line (`last attempt ...,unopened`) would then tell the dispatcher that no PR was ever opened. Pin it with a `# mut:` marker and an arm in the rowless replay that reads the ledger attempt, or drop the claim from the body. Carry: R10-FLY-OPENPR-ATOMIC
- Weak pin: replacing the reason extraction `{ grep -E 'REFUSE' $D/p2.log || tail -n 20 $D/p2.log; }` (open_pr.sh:97) with a bare `tail -n 20` survives (ev/mutant-whyreason.txt, 154 checks, 0 failed). The stub's p2.log is shorter than 20 lines, so the tail fallback quotes the refusal anyway. In this test the mutant is equivalent, but against a real prepr log longer than 20 lines it is not. Make the stub's p2.log longer than 20 lines with the REFUSE line early, or record that the case is accepted as equivalent. Carry: R10-FLY-OPENPR-ATOMIC

## Evidence

- RESULT head self-test: `bash tools/audit/seat/open_pr.sh --self-test` at 50b1956485ea01e78d97a0619a32cdc9dd923cdd: pr_args 154 checks, 0 failed; delivery_row 6 checks, 0 failed; exit 0 (ev/selftest-head.txt).
- RESULT base self-test at fe709cbd2: pr_args 151 checks, 0 failed; exit 0 (ev/selftest-base.txt).
- RESULT failing test first: the head's tree with origin/main's open_pr.sh gives 154 checks, 2 failed, exit 1. The only FAILs are the close arm and the merge-conflict arm (ev/selftest-main-openpr.txt). This matches the body.
- RESULT named mutants (rowclose, rowreset, mergeabort): their arms pass at the head, so each mutant produces the defect the body describes.
- RESULT own mutants at the head: deleting the `pr_refuse` line after the merge abort (line 63) gives 1 FAIL, the merge-conflict arm (killed). Deleting the gh_comment.py post (lines 100-101) gives 1 FAIL, the close arm (killed). The ledger-attempt mutant and the reason-grep mutant survive (see Findings). Files: ev/mutant-*.txt.
- Finder's harness: none is named, and the review packet says so. The finding is tooling, and the in-tree self-test with `# mut:` markers is the instrument.
- Merge with main: `git merge-tree --write-tree origin/main 50b1956485ea01e78d97a0619a32cdc9dd923cdd` exits 0 (tree cde818d4f13026683050c79c3e5d2b62ceb7aa16), with no conflict.
- The role diff `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- VERSION, the manifest and RELEASE_NOTES.md are untouched (three-dot diff empty). No golden or claim files are touched, and no budget is moved.
- The body's Head section names 50b1956485ea01e78d97a0619a32cdc9dd923cdd and the code head f32c80504, which is an ancestor of the head. Confirmed.
- CI on this head, read live from check-runs: no check concluded red. tests / closures, governance / instrument-self-tests and codeql / Analyze (python) were still in progress at read time. tests / mutation is green, but a shell-only diff draws no Python mutant, so it says nothing about these lines. The body's "Red checks: none" is consistent so far.
- Forward-carry: none claimed. The out-of-group carries 4, 6 and 7, and carry 8's handoff_push.sh seams, are stated as staying on the roster.

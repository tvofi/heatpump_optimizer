Fix review: blocked b8353012f530fe3d5f30606b60283d9b399c7712 root-cause-unanswered: governance / instrument-self-tests concluded red at this head and the body's ## Red checks does not answer this head's failure

bus-nonce: e8b87b408f786f7ae1bc342a922bf889

## Block

`governance / instrument-self-tests` (job 124797544268, run 41289450815) concluded `failure` at b8353012f530fe3d5f30606b60283d9b399c7712. The failing step is `prepr.sh --self-test`'s pr_args block: `pr_args self-test: 158 checks, 2 failed`, on `null control: a normal successful update_pr leaves nothing behind and stops nothing it did not start` and `open_pr: the null control -- an unrelated sleeper survives`. The body's `## Red checks` entry for this check covers other heads (e24686de4679, 0c38d4ccd648) and a different cause (the unrecorded structure gain, failing `body_push.sh` arms). It does not name or answer this head's failure. This diff touches only tests/structure_budgets.json, so the failure reads like a process-hygiene flake on a loaded runner, but I cannot tell that from the log, so the class is unanswered, not detectable. A re-run or a body answer clears it. The remaining alert-list `BAD` lines in the log are mutant output; that step printed `ALERT-LIST MUTANTS: every mutant refused`.

CI was not fully concluded when I wrote this: `tests / mutation` and `codeql / Analyze (python)` were still in_progress, and no `pr-contract` run existed at this head. `merge_train.py classify` printed `WAIT ... pending: gate red: none` (rc 3) at every poll over about 90 minutes. This verdict is on the evidence in hand, and the contract wants the root-cause class posted only after every workflow concluded, so the orchestrator should re-review the red and not treat this as final.

## Findings

- None beyond the Block; the delta checks below all pass. Carry: dismissed: no finding outside the Block.

## Evidence

- Delta: `git diff 0c38d4ccd648..b8353012f530fe3d5f30606b60283d9b399c7712 --stat` is tests/structure_budgets.json alone (2 insertions, 2 deletions). `git log --no-merges` over the range is one commit, "structure: record class_excess_loc 17653 -> 17651 after merging main". The diff moves class_excess_loc 17653 to 17651 and recorded_at to 61b0076f.
- Structure, detached worktrees: at the head `RESULT class_excess_loc=17651`, `ok class_excess_loc 17651 <= 17651`, rc 0. At main 61b0076f48546fe29cae35dfdb5949ad6d0c6feb `RESULT class_excess_loc=17653`, rc 0, so the 17653 baseline reproduces. The move is down (ev/structure_head.txt, ev/structure_main.txt).
- Merge: main 61b0076f is an ancestor of the head. `git merge-tree --write-tree origin/main b8353012f530fe3d5f30606b60283d9b399c7712` printed only a LEDGER-MERGE auto-resolve note for tests/closures.json (the inert_reads set merge), with no conflict. origin/main has since moved to 92588d58.
- Red checks at the head (all pages of check-runs read): `governance / instrument-self-tests` failure (the Block). `tests / fast (3.14)` success, so the earlier "not yet recorded" red is gone. `tests / mutation`, `codeql / Analyze (python)` and one `prelude` were in_progress. No `pr-contract` run was listed. Every other check was success, skipped or neutral.
- Earlier approved review of 0c38d4ccd648 still covers the code: the delta holds no production, test or fixture file. Not re-reviewed.

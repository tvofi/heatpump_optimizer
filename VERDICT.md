Fix review: merge 2972c73e494f6e976abb8ce1dd43dfad9944a432

bus-nonce: 7fc310b7fe07bdfe7f26ef35abbd9cce

## Scope

Minimal delta review of #2837 (R10-PROOF-CODEQL), round 2, at head 2972c73e494f6e976abb8ce1dd43dfad9944a432. Round 1 (comment 6404318957, head bff57cc0cd336b1f9c9b8a0ceec645d15c0c865d) blocked on the body alone. This round checks the three items in the brief and nothing else. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract read from the head is current.

## Findings

none

## Evidence

- RESULT item 1 (code unchanged): pass. `git log --first-parent bff57cc0..2972c73e494f6e976abb8ce1dd43dfad9944a432` is one commit, the merge of origin/main 63a1c5fe8 into bff57cc0. `git log --no-merges bff57cc0..2972c73e494f6e976abb8ce1dd43dfad9944a432 --not origin/main` is empty, so the branch carries no commit of its own since bff57cc0. `git merge-tree --write-tree bff57cc0 63a1c5fe8` gives tree 335619508f2a, equal to the head's tree, so the merge is mechanical and adds no hand resolution. The branch's own diff (merge-base..head) is the same 7 files, +257/-15, as at bff57cc0. Diffing the two own-diffs, only blob ids and hunk offsets in governance.yml and tests/entities.py differ, from main's context lines. ev/delta.txt.
- RESULT item 2 (Red checks answers delivery-status honestly): pass. The section names `governance / delivery-status` and gives its cause: OVERDUE rows that all belong to other merged PRs. It gives its state, which is not a required context and blocks no merge. It says why the check reads nothing this diff reaches: tests/delivery_status.py and tests/layout.py are restored from PINNED and untouched, and the ci.yml and governance.yml edits sit in other jobs. It claims no fix: it says the drain belongs to the orchestrator's record step. At this head the job (121353719244) still fails for the same cause. Its log prints `DELIVERY STATUS OVERDUE — 146 rowed, 12 pending, 18 overdue`, every overdue row is another PR's (#2821 … #2795), #2837 is not among them, and the log states \"This check is NOT a required context and a red here blocks no merge\". The body's figure of 8 overdue is dated to bff57cc0 and main 5261ba84; the rise to 18 is main's backlog growing, not a misstatement. ev/delivery-status.log.
- RESULT item 3 (pr-contract green at this head, from the check-runs API): pass. `pr-contract / pr-contract` succeeded in run 121362080310 (02:05:53Z–02:06:23Z) and run 121362611061 (02:08:01Z–02:08:32Z). Both started after the last red to conclude, delivery-status at 01:37:15Z, and after both CI runs (40254158438, 40254157632) had concluded. `gate` succeeded in 121362218260 and 121362751988. At this head `governance / delivery-status` is the only check run that is not success, skipped or neutral. It is not a required check and does not block. ev/check-runs.tsv.
- Merge: `git merge-tree --write-tree origin/main 2972c73e494f6e976abb8ce1dd43dfad9944a432` at origin/main 7d2056970e08135bdc7c2cab4063427a2efa1c30 exits 0 with no conflict. ev/merge-tree.txt.
- Head re-read before return: the PR head is still 2972c73e494f6e976abb8ce1dd43dfad9944a432.
- Code-path claims (mutation proof, null control, figures) were not re-measured this round. The brief scopes this round to the delta, and round 1 judged that code, which is unchanged.

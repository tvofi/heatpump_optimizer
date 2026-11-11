Fix review: blocked a47cddfebf07840156d6f6dfa64b29ade3371d67 merge-conflict: git merge-tree --write-tree origin/main a47cddfebf07840156d6f6dfa64b29ade3371d67 reports a conflict in tests/golden/claimed_drift.txt (claimnotes driver: CONFLICTING CLAIMS on config_flow)

bus-nonce: a837f391e30d0e6eec71225582ac6c75

Round 2, scoped by the owner's later-round ruling to `git diff 249d76dd62bdab432e2c671edba7d5e96313bf80 a47cddfebf07840156d6f6dfa64b29ade3371d67`. Measured at head `a47cddfebf07840156d6f6dfa64b29ade3371d67` (the live `refs/pull/3398/head` at the final read), origin/main `45adb0c3b425dc44e72fd9ce4ef51f480b5a3af6`.

## Block

- `git merge-tree --write-tree origin/main a47cddfebf07840156d6f6dfa64b29ade3371d67` exits with a conflict (`ev/merge_tree.txt`). The only conflicted path is `tests/golden/claimed_drift.txt`, at stages 1 and 2. The claimnotes driver prints `MERGE-CLAIM: refused` and `CONFLICTING CLAIMS: both sides rewrote the same scenario's claims` for `config_flow`. Main (`3e31f5c1c7`, R10-GENERIC-HEAT-CURVE-PERSISTENT) now claims `config_flow` for the persistent heat-curve option. The head claims it twice: once for R10-HOTFIX-COP-UNMEASURED and once for R10-COMBI-TANK (#3225). The head is 58 commits behind origin/main. CI is green at this head, but the train cannot apply it without a hand resolution.
- To resolve, merge origin/main and resolve the claim file by hand, following claim-files.md and the driver's own text ("keep the lines that describe THIS branch's diff and delete the rest"). Keep this branch's six `R10-COMBI-TANK (#3225)` lines. Do not carry `R10-HOTFIX-COP-UNMEASURED` or `R10-GENERIC-HEAT-CURVE-PERSISTENT` lines over as this branch's claims unless `env_drift.py --all origin/main` shows the merged tree still moves those leaves against main. The head carries six inherited COP-UNMEASURED lines (`ev/head_claims.txt`), which already sit on main (`ev/main_claims.txt`). After the merge, re-run `env_drift.py --all origin/main` (no unclaimed drift, no stale claim) and `prepr.sh`, and re-state the body's `## Resolution` section 3. It currently describes keeping 12 lines, while `## Merge resolution only` says main's GENERIC-HEAT-CURVE `config_flow` line was dropped.

## Evidence

- Delta 249d76dd6..a47cddfebf07840156d6f6dfa64b29ade3371d67: three first-parent merges of origin/main (`e020a1d23`, `5572a5f57`, `a47cddfebf07840156d6f6dfa64b29ade3371d67`) and no authored code commit on the branch line. This branch's own diff against its merge base fell from 124 files (at 249d76dd6) to 56 files, because PR A's production files landed on main through the merged main (`ev/branch_diff_delta.txt`). The branch_diff_delta also shows no new hand edit to `custom_components/` beyond the merge resolutions the body describes. No production change in the delta puts already-reviewed code at a non-obvious risk, so I did not widen the review.
- CI: `merge_train.py classify a47cddfebf07840156d6f6dfa64b29ade3371d67 --pr 3398` printed `GREEN a47cddfebf07840156d6f6dfa64b29ade3371d67 pending: none red: none`, rc 0, at the start and again at the end (`ev/classify1.txt`, `ev/classify.txt`). `merge_train.py owed-reds` lists the required set (`ev/owed_reds.txt`), and none of it is red.
- Previous verdict (`probe/rev-3398-6a7a49cb`, merge at 249d76dd6) had one finding: the residual on `thermal_model.py:328`'s `or not self.combi_tank_active` arm, dismissed as a non-blocking test gap. That line is unchanged at this head (`git diff 249d76dd6 a47cddfebf07840156d6f6dfa64b29ade3371d67 -- thermal_model.py` has no combi hunk), so the dismissal stands as recorded and nothing new is owed on it.
- I re-ran no mutants this round. The delta adds no authored code, and the block is the merge conflict.
- Figures in the body that name heads other than this one (`a1b268838`, `27fa6918c`, `d1975b5b7`) were not re-derived. They are superseded by the resolution this block requires.

## Findings

none

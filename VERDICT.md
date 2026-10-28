Fix review: blocked e6455b8fe617ec28d6916977778e7499a6d2fd27 root-cause-unrecorded: tests / nightly-ha (stable) is red at the head and the post-red pr-contract run refuses the body for not naming it under ## Red checks

bus-nonce: 91726484ee94e683682f43f3efb79372

Round: delta review of #2753 (R10-THERMAL-POWER-OPTION) after reviewer aeedca3b's `merge 0303eae4` (origin/review/2753). Measured head: `e6455b8fe617ec28d6916977778e7499a6d2fd27` (`ev/HEAD.txt`), the bot's `ci: merge main` with parents 0303eae4 and 662a3809 (origin/main at review time). The role contract is current: the roles diff from the head's merge base to origin/main is empty (`ev/merge_delta.txt`). Only the merge delta was judged; everything else carries from aeedca3b's verdict.

## Block

- The merge delta itself is sound (see Evidence). The block is rule 11 alone: `tests / nightly-ha (stable)` (job 121042556914) concluded `failure` at this head on `hb:positive_control` ("a 600 ms spin read as 5290.1 ms; ... py-spy rc=0 names it: False; try 3 of 3") and on `run:exit_status`, the container exit that follows from it. Two `pr-contract` runs, 121053606313 and 121055642825, started after that red concluded. Both refuse the body: "check `tests / nightly-ha (stable)` is red and `## Red checks` does not name it" (`ev/ci_pr_contract.txt`).
- Diagnosis to answer it with: the red is not this PR's. Main's side of the merge (#2711, #2776, #2704) changes no integration code and nothing `nightly_ha.py` exercises (`ev/merge_delta.txt`). The identical integration code passed this check at 0303eae4 (job 121023292089). The failing probe is the heartbeat instrument's own positive control timing out on a slow runner, which no cheaper pre-handoff detector could have shown. The fix is a `## Red checks` entry that names the check and records that finding, or one re-run of the lane per ci-autofix.md and steward. Either way no code change is owed. Carry: dismissed: answered by the body edit or re-run named here, nothing to hand on

## Findings

- none: the merge delta raises no defect, survivor or deferral. The single item above is the block. Carry: dismissed: no finding to carry

## Evidence

- Merge is the main merge alone: `git merge-tree --write-tree 0303eae4 662a3809` (the repo's ledger driver resolved tests/structure_budgets.json and tests/closures.json, rc=0) builds a tree whose diff against the head is empty. The only paths both sides touched are those two ledgers (`ev/merge_delta.txt`).
- Ledgers: the head's tests/structure_budgets.json against main differs only in the branch's own lowered `class_excess_loc` (18209 -> 18202) and `max_class_loc` (8449 -> 8442). It keeps main's lowered `seam_cut_total` 420 and main's `recorded_at`. No budget moved up. tests/closures.json against main adds only the branch's own `dev/audit/harnesses/r10_thermal_power_option.py` entry (`ev/ledgers.txt`). `tests/structure.py` at the head prints STRUCTURE RATCHET PASSED (`ev/structure_head.txt`).
- Claim files: `git diff 0303eae4 e6455b8 -- tests/golden/*claimed_drift.txt` is empty, so the merge left them alone. Three-dot against main shows only the branch's own `config_flow` line from the reviewed code. card_claimed_drift.txt is untouched. `claims-for: 7.0.4` equals VERSION 7.0.4. VERSION, the manifest and RELEASE_NOTES are untouched three-dot. pr-contract prints "no version edit" (`ev/claims_version.txt`).
- `git merge-tree --write-tree origin/main e6455b8` exits 0, so there is no conflict.
- CI at the head (`ev/ci_state.txt`): 51 success, 24 skipped, 3 failure (nightly-ha (stable) and the two pr-contract refusals of the same item), and 2 `gate` runs still queued at write time. pr-contract's CARRY-AUDIT routes 5 of 5 items. Its HEAD check accepts e6455b8 as an autofix on top of `## Head` 0303eae.

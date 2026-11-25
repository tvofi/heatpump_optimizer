Fix review: merge 498708251b6d122add9aae8ae8542afe27bef5ba

bus-nonce: a0f438d8fb25531a3e5a29833010ab31
pending-ci: gate

Round 3 (delta re-review over the reviewed head 8681cc72f623c825054b81b7ffb2dca70fc4c189). Scope: the orchestrator's hand-fix `git diff f2f9e3f5d5 b272d01ecb` and the `update_pr` merge to the head `498708251b`, plus the previous verdict's block (`tests-red`, two stale counts) and its one note. The delta touches no production file (`custom_components/`), so nothing widens the scope (fix-review.md step 12).

## Findings

- Note: stale-body: the figures line has been refreshed (103 modules, 66 HA-free, 122 package files, 184 of 561), and all four figures now agree with the tree. One item from the previous note is still stale: "tests/features.py: the `_repair_dhw_floor` stand-in `_lg_whole_tail_repair` takes `charge_running`". Commit `875dfbc86f` removed that keyword, as the body's own `## Head` section says. The "Merge of main" paragraph (64 to 65, "102 modules less the 37") describes the history before `f2f9e3f5d5`. Refresh before the merge. Paperwork only, not a block. Carry: dismissed: PR-body paperwork, settled by editing the body before the merge, nothing owed after it

## Evidence

- Head reviewed: `498708251b6d122add9aae8ae8542afe27bef5ba` (`ev/HEAD.txt`), equal to the live PR head. Its parents are `8681cc72f6` (the reviewed head) and `b272d01ecb`, whose parent is `f2f9e3f5d5`. The trees of `8681cc72f6` and `f2f9e3f5d5` are identical (`809274347c`). So the head is the reviewed tree plus exactly `b272d01ecb`'s two lines: `git diff 8681cc72f6 498708251b` touches 2 files, +2/-2 (`ev/delta.diff`).
- The delta:
  - `docs/architecture.md:306` changes "The other 65 modules" to 66.
  - `tests/deployment_shape.py:60` changes "182 of the 561 script pairs" to 184.
  - These are the two owed changes the previous block named, and nothing else.
- Prior block resolved, re-run at the head on a clean detached worktree:
  - `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2763 ENTITY CHECKS PASSED`, rc=0 (`ev/entities.txt`). It was `2 of 2763` at `8681cc72f6`.
  - The two formerly failing checks now read `ok   architecture.md's HA-free count is the tree's` (line 58) and `ok   and the lane's docstring records those measured numbers as the selection-cost note (#1218)` (line 1591).
  - The 54 indented `FAIL` lines carry the script's own nested-control prefixes (`a3:`-`a10:`, `hb:`). They are controls, not failures, as at the main control last round.
  - `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: `ALL 443 checks PASSED`, rc=0 (`ev/doc_claims.txt`). This agrees with the orchestrator's run.
  - `PYTHONPATH=tests/hastub python3 tests/deployment_shape.py`: `ALL DEPLOYMENT SHAPE CHECKS PASSED`, rc=0 (`ev/deployment_shape.txt`). Last round this was not run.
- Perturbation: the reverse of this delta (65 and 182) is the reviewed head's tree. At that tree, last round's `entities.py` and `doc_claims.py` failed on exactly these two checks. So both checks move with the two numbers, and their passing now is not vacuous.
- `git merge-tree --write-tree origin/main 498708251b`: rc=0, no conflict (`ev/merge-tree.txt`). origin/main is still `d3d66c40408e76351ffc528686353cadf815a05c`, equal to the PR base.
- `VERSION`, `RELEASE_NOTES.md`, `manifest.json` and both claim files are untouched three-dot against the merge base (`git diff --quiet` rc=0).
- The previous round's M1, M8 and M9 evidence stands: the production delta is unchanged since `8681cc72f6`.
- CI: `merge_train.py classify 498708251b6d122add9aae8ae8542afe27bef5ba --pr 3863` printed `WAIT ... pending: gate red: none` on every poll from 14:00:50Z to 14:30:55Z (`ev/classify.log`). No red, so no `## Red checks` answer is owed. The verdict is returned with `pending-ci: gate` for the relay.
- `carry_audit.py` on the PR body at render (review packet): `CARRY-AUDIT: 0 finding item(s)`. On this verdict: see the run before return.

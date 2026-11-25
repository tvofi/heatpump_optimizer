Fix review: merge 5825777c2b4dcdb2a84f9628877fa91f91d56abe

bus-nonce: 81826059ac6f120b3c75bb3e161ebfa1
pending-ci: gate

Delta round over the reviewed head `d7029ade34c87eb0baaad0313a90d352edb99f2f` (packet `## Review scope: delta`). Per the orchestrator's delta ruling, I reviewed `git diff d7029ade34c8 2869f172b0`, the code delta. The head `5825777c2b` is `2869f172b0` plus two main merges that change nothing of the PR's own.

## Prior findings

- Round at `d7029ade34`, `tests-red` (the #1218 selection-cost note says 182, the merged closures derive 184): resolved.
  - `2869f172b0` changes only `tests/deployment_shape.py`. It sets 182 to 184 in both places, "184 of the 561" and "all 184 among the 435". The history clause names the two new pairs.
  - I re-derived the count with entities.py's `_d308_pairs` predicate (`ev/pairs.py`).
    - origin/main `0e1eba2b4a`: 182 of 561.
    - The head: 184.
    - The head merged with origin/main (tree `ea80d08249`, via `git merge-tree --write-tree`): 184 (`ev/pairs.txt`).
    - The two pairs added against main are exactly `tests/env_drift.py`/`tests/manual_plan.py` and `tests/golden.py`/`tests/manual_plan.py`, the ones the history clause names. No pair is removed.
  - The note's other markers hold at the merged tree (`ev/markers.txt`): `all 122 files`, `435 pairs`, `D3-08`, `#1218`, `selection cost`, and the four scripts with no production closure. Those four are re-derived as `tests/arch_score.py`, `tests/ha_contract.py`, `tests/layout.py` and `tests/md_tables.mjs` (`ev/empty.txt`). `182 of the 561` no longer appears.
  - Detector shown both ways:
    - At the head merged with main, `PYTHONPATH=tests/hastub python3 tests/entities.py` reads `ok and the lane's docstring records those measured numbers as the selection-cost note (#1218)` and `ALL 2763 ENTITY CHECKS PASSED`, rc 0 (`ev/entities_head_main.txt`).
    - The mutant is the previous head's text (182), which this check failed with missing marker `184 of the 561`, as the previous verdict reproduced.
- Same verdict, the note `root-cause-unanswered: tests / fast (3.14)`: resolved. The body's `## Red checks` now answers this red at `d7029ade34`: the cause, the cheaper detector (a seconds-long re-derivation from `tests/closures.json`) and that `ci_predict.py` does not run it. The proposal for an instrument is routed to round-end, under the tooling freeze.
- Same verdict, residual K8: unchanged by this delta, already carried (dismissed: a pre-existing guard moved unchanged).

## Evidence

- Head `5825777c2b4dcdb2a84f9628877fa91f91d56abe` (`ev/HEAD.txt`): `git ls-remote origin refs/pull/3838/head` printed it. The body's `## Head` names it.
- Merges with main: `git merge-tree --write-tree origin/main 5825777c2b` rc 0 at origin/main `0e1eba2b4a` (`ev/merge_tree.txt`). The ledger driver unions `tests/closures.json`.
- Body figures re-derived (`ev/pairs_body.txt`):
  - 182 at `bb6377b4da`, 184 at `d7029ade34`, and 184 at `2869f172b0`.
  - The comparable pairs stay at 435. The production file count is 122, against 121 at main.
- `tests/deployment_shape.py` at the merged tree: `ALL DEPLOYMENT SHAPE CHECKS PASSED` (`ev/deployment_shape.txt`). This matches the body.
- Production widening (step 12): none. The delta is a docstring in `tests/`, with no production code.
- Protected files, three-dot against the merge base (`ev/protected.txt`):
  - `VERSION`, `RELEASE_NOTES.md`, the manifest and `tests/golden` are untouched.
  - `tests/structure_budgets.json` only falls: `class_excess_loc` 17290 -> 17274 and `module_excess_loc` 21763 -> 21754. No raise.
- The repair commit's message carries no trailer (`ev/repair_commit.txt`).
- CI: `merge_train.py classify 5825777c2b --pr 3838` read `WAIT 5825777c2b4dcdb2a84f9628877fa91f91d56abe pending: gate red: none` from 15:06 to 15:35 UTC (`ev/classify.log`). This verdict therefore carries `pending-ci: gate`.
- Owed reds: the set is listed in `ev/owed_reds.txt`. None is red at this head per classify (`red: none`). The packet digest's `tests / nightly-status` failure is outside the set.

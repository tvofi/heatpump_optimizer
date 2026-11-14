Fix review: merge ced9b233580709f530d5dc402dc12344697fef87

bus-nonce: c9556b39d7b37bfaa51404e9602f3dea
pending-ci: gate

## Scope

Round 3 of this branch's review, a delta review of PR #3562 at head ced9b233580709f530d5dc402dc12344697fef87. The reviewed head is 7db7de155fef49a36118c10ca5747b1804babf32, which has a merge verdict on review/3562. The predecessor's unposted round-2 draft at probe/rev-3562-abeeafaa (commit bc3c715d51) reviewed head 04f8ab9f and found it a clean merge. I read that draft and confirm it below.

The review packet's `## Review scope` line reads `full`, because no verdict on verdict/3562 names 7db7de15. The dispatch scopes this round as a delta, and fix-review.md step 12 agrees: `review_carry.py` prints FRESH-REVIEW for both 7db7de15..ced9b233 and 04f8ab9f..ced9b233, so this round is its delta. ced9b233 has the parents 04f8ab9f and main c987209cc7, and 04f8ab9f is its ancestor. The new delta is that one merge of origin/main.

## Evidence

- RESULT head: measured at ced9b233580709f530d5dc402dc12344697fef87 in a detached worktree (ev/HEAD.txt). The PR body's `## Head` names the same SHA as an automatic main merge with no resolution.
- RESULT roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` printed nothing.
- RESULT merge resolution: `git show --remerge-diff ced9b233` shows no content resolution. Its only output is the ledger driver's `LEDGER-MERGE: resolved tests/closures.json` (merged as a set). See ev/remerge-diff.txt.
- RESULT branch patch unchanged: I diffed the branch's own diff before the merge (`e23124ff..04f8ab9f`) against its own diff after it (`c987209c..ced9b233`). The two differ only in index lines, hunk offsets, and the context lines of one `_flow_target` hunk, where main's `start_flow_min_lift_k` replaced `configured_flow_min_lift_k`. No added or removed line of the PR changed (ev/branch-own-diff-before-after.txt).
- RESULT predecessor draft confirmed: its 04f8ab9f findings stand on the unchanged patch. Those findings are: the production delta's equivalence, which inlines `_space_boosted`; the 61-check arbiter block; prior finding 1, #3404's harness re-anchored; the survivor triage; and the coord_footprint payment. I did not re-run its R1-R4 reviewer mutants or the #3404 harness. They are cited from ev/ on bc3c715d51.
- RESULT production risk from main (step 12 widening): main's delta to custom_components/ (ev/delta-production-stat.txt, ev/delta-pump_arbiter.diff) touches pump_arbiter.py at two points where the PR's boost ceiling passes:
  - `_bounded`, which the boost write goes through with `hi=heat_c`, is rewritten onto `inputs.SetpointGrid.bounded`.
  - The heating floor's lift is now `start_flow_min_lift_k(config, space_start_hysteresis_k)`.

  Both change already-reviewed boost behaviour without a textual conflict. The path is `custom_components/heatpump_optimizer/pump_arbiter.py` `_flow_target`/`_bounded`, and the risk is that the boost ceiling is clamped or floored differently. I re-measured it at the merged head:
  - The arbiter block (`features_block.py` from `R.section("pump-duty arbiter — mode and set-points per plan step` to `_pa_subs = _PaCoord(`) prints `ALL 61 FEATURES BLOCK PASSED` at rc=0 (ev/arbiter-block-head.txt). That includes the R10-HOTFIX-BOOST-FLOW-CEILING rows: maxima 55, 60 and 70, the stored 50, the stored default 55, limit 52, the limit at the gate, 90, no maximum, and a return maximum of 45.
  - Reviewer mutant: I replaced pump_arbiter.py:948 `heat_c = _heat_ceiling_c(inp.config) if boost_c is None else boost_c` with `heat_c = _heat_ceiling_c(inp.config)`, so the boost ceiling is dropped. The block went to rc=1 with 6 FAIL lines, among them every R10-HOTFIX-BOOST-FLOW-CEILING row (ev/mutant-boost-ceiling-dropped.txt). I restored the line and `git status` is clean. The fix is still load-bearing and still tested after main's `_bounded` rewrite.
- RESULT merge-tree: `git merge-tree --write-tree origin/main ced9b233` exits 0 against origin/main 513a07dfdc. There is no conflict (ev/merge-tree.txt).
- RESULT version untouched: the three-dot range from merge base c987209cc7 touches none of VERSION, manifest.json, the RELEASE_NOTES.md headings or either claim file (ev/version-untouched.txt). The two-dot delta's manifest.json line is main's own stamp.
- RESULT carry audit at the head (packet): 1 finding item: 1 routed, 0 unrouted. The body's Forward-carry is dismissed under the owner's 2026-11-13 ruling.
- RESULT owed reds: `merge_train.py owed-reds` prints `tests / coverage-ratchet`, `tests / fast (3.14)`, `tests / mutation`, `tests / typing` and `validate / validate-hacs`. At render, the packet digest shows fast, typing and validate-hacs as success, and mutation and coverage in progress. `tests / nightly-status` reads failure, but it is outside the owed set and is main's (the body's Red checks), so it blocks nothing. `instrument-self-tests` is success.
- RESULT CI: I ran `merge_train.py classify ced9b233580709f530d5dc402dc12344697fef87 --pr 3562` about every 65 s from 03:37 to 04:10 UTC, 30 runs (ev/classify-log.txt). Every run printed `WAIT ced9b233580709f530d5dc402dc12344697fef87 pending: gate red: none`, rc=3. CI had not concluded when the review was complete, so this verdict carries `pending-ci: gate`. I re-read the head before the push and it has not moved.

## Findings

none

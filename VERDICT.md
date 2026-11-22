Fix review: merge c931e99404d39ceaf9c8d84a68b5e24b7dec5f11

bus-nonce: 055f0ca05bc8c21ef910dc8ec5d8f7c9
pending-ci: gate

Note: stale-figure: the body's `## Figures` quotes `features.py: ALL 6041 FEATURE CHECKS PASSED` at 4e5de6ba; at this head the same command prints ALL 6047 FEATURE CHECKS PASSED, rc 0 (ev/features.log), the six more being main's after the f269ecccb5 merge. The `## Architecture score` still quotes `--diff 6fdc15354f`, a base back; the PR's production lines are identical at this base (ev/delta.txt). Carry: dismissed: paperwork on body figures, the substance holds at this head
Note: owed-red: `tests / coverage-ratchet` (job 137084971528) is red at this head with `3 module(s) below the 95.0 % per-module floor: room_history.py 66.09 %, room_record.py 86.96 %, draw_range.py 91.65 %`, the same three figures the body's `## Red checks` answers at 2df609237b (no cheaper detector; none of the three modules is in this diff). Answered by the body, so not a block; whether it holds the merge is classify's, read below. Carry: dismissed: answered in the body's Red checks

Round 5, delta only: reviewed head 827fa67eb6ee84d8874524557cdd540ca1b54593 (round-4 verdict, merge, probe/rev-3738-bee67cf7) -> c931e99404d39ceaf9c8d84a68b5e24b7dec5f11. `review_carry.py 827fa67e c931e994` prints FRESH-REVIEW, so the delta was read by hand. No earlier round's block is open (round 1's was repaired and reviewed in round 2), so the fourth-round re-cut rule does not bite.

## Delta
- Production: the `+`/`-` lines of `git diff <merge-base> <head> -- custom_components/` are identical at 827fa67e (base 63c6d1cff9) and at this head (base f269ecccb5): PROD-LINES-IDENTICAL; null control, dropping the head's first line, differs in 2 lines (ev/delta.txt).
- Non-production: only `tests/features.py` and `tests/structure_budgets.json` change their PR hunks, plus eight new `killed_by` pins (ev/delta.txt). The budgets keep the PR's own -2 on `class_excess_loc` and `max_class_loc` against the new base. The features.py interdiff (ev/features_interdiff.txt) is test-only: the #1754 rig's nested run request as a bounded task with a new check, a T2 payload check, the D9-s1-03 three-asks check, the four-quarter horizon check, and bounded waits in the #1753 borrow arm and the solve_gate slot burst.
- Merges in the delta (`git show --remerge-diff`, ev/remerge_*.txt): 4e5de6bad8 and b57ac2851e keep both appended blocks (this branch's solve_gate block, then main's R10-DRAW-MAP-EVIDENCE part A); 9b50e5b588 takes the bounded `background_entry` rig over the unbounded one; 6b74444ae4 resolves the five count conflicts to 99 modules / 34 HA importers / 118 package files, which doc_claims and deployment_shape confirm at this head; 66fbd97fd2 and c931e99404 are the LEDGER-MERGE driver's resolutions only (c931e994's tree equals 66fbd97f's, a2f90d98d5ce).
- Widening considered and declined: main's production delta 63c6d1cff9..f269ecccb5 (19 files) has no `+`/`-` line naming `async_run_optimization`, `async_simulate`, `async_optimize_now`, `async_request_refresh`, `async_refresh(`, `_optimization_running` or `solve_gate` (grep rc 1, ev/main_delta_callers.txt), so no reviewed solve-gate behaviour is put at a risk CI would not detect.

## Prior findings
- Note mutation-red (rounds 3-4, six unpinned added sites): resolved. `tests / mutation` is success at this head (job 137067809746), and the eight sites are pinned by the delta; the six I re-ran below each fail a named check.
- Note stale-figure (architecture score base): still one base back, carried above.
- Note figure-unreproduced (round 4, a merge-tree id): superseded by this head's own merges.

## Evidence
- RESULT merge_tree_rc=0: `git merge-tree --write-tree origin/main c931e994`, origin/main at 35c3e31cc954 (ev/merge_tree.txt).
- RESULT version files: `git diff --name-only f269ecccb5...HEAD -- VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json` prints nothing.
- RESULT structure: STRUCTURE RATCHET PASSED rc 0 at the head (ev/structure.log).
- RESULT doc_claims: ALL 441 checks PASSED rc 0; deployment_shape: ALL DEPLOYMENT SHAPE CHECKS PASSED rc 0; `git ls-files custom_components/heatpump_optimizer | wc -l` prints 118 (ev/doc_claims.log, ev/deployment_shape.log).
- RESULT scope: `tests/closure.py select --diff f269ecccb5` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`, the body's figure block (ev/closure_select.txt).
- RESULT features: `PYTHONPATH=tests/hastub python3 tests/features.py` at the head: ALL 6047 FEATURE CHECKS PASSED, rc 0 (ev/features.log).
- RESULT block A (`from heatpump_optimizer import manual_plan as _g1754_mp` to `async def _whatif_scratch_config():`, prelude from `--emit-prelude` at the head): unmutated ALL 13 FEATURES BLOCK PASSED (ev/blockA_unmutated.log).
- RESULT block B (`async def _sg_slot_burst(k):` to `async def _sg_trailing():`): unmutated ALL 3 FEATURES BLOCK PASSED (ev/blockB_unmutated.log).
- RESULT mutant M4 (coordinator.py:11193 `len(horizon.prices) < 4` -> `<= 4`, CMP_BOUND 91e008d2): KILLED, 1 of 13, "a what-if needs four priced quarters ..." (ev/block_M4.log).
- RESULT mutant M5 (coordinator.py:11250 `and simulated.predictive_info` -> `or`, BOOLOP 6c3e48ee): KILLED, 1 of 13, "T2: a what-if that capped no power carries no power_cap_breach_c ..." (ev/block_M5.log).
- RESULT mutant M6 (coordinator.py:11180 `if not admitted:` -> `if False:`, GUARD_OFF 1f48017b): KILLED, 1 of 13, "D9-s1-03: of three user what-ifs overlapping one solve ..." (ev/block_M6.log).
- RESULT mutant M7 (solve_gate.py:76 `if gate.solving:` -> `if False:`, GUARD_OFF d99b351e): KILLED, 1 of 13, "a run request during an in-flight solve returns at once ... (#1754, the solve gate)", ending rather than deadlocking (ev/block_M7.log).
- RESULT mutant M8 (solve_gate.py:129 `if not user:` -> `if False:`, GUARD_OFF 9a253a03): KILLED, 1 of 3, "D9-s1-03: of four overlapping user what-ifs ... a background caller never waits ..." (ev/block_M8.log).
- RESULT mutant M9 (solve_gate.py:90 `if absorb_request(gate, False):` -> `if False:`, GUARD_OFF 53abf7e8): KILLED, 1 of 13, the #1754 nested-request check (ev/block_M9.log). Each production file was restored with `git checkout` after its run.
- CI at this head (ev/check_runs.txt): success: tests / fast (3.14), tests / mutation, tests / typing, tests / closures, tests / coverage, tests / browser, tests / arch-instrument, tests / nightly-ha (stable and 2025.2.0), tests / closure-scope, tests / briefs, tests / lane-proofs, governance / env-matrix, instrument-self-tests, policy-docs, wave-script, validate-hacs, hassfest, codeql (3), arch-score, budget-raise-gate; failure: tests / coverage-ratchet (Note above) and `gate` (job 137074832914, 03:08Z: `FAIL run(s) [44975634532] at this head are still being judged; their gate decides`, a run that ended before the tests run did); cancelled: tests / replay; queued: pr-contract / pr-contract. `merge_train.py owed-reds` (ev/owed_reds.txt) holds coverage-ratchet, fast, mutation, typing and validate-hacs.
- `merge_train.py classify c931e994 --pr 3738` printed `WAIT c931e99404d39ceaf9c8d84a68b5e24b7dec5f11 pending: gate red: none` (rc 3) on every run from 04:41Z to 05:10Z, 75 s apart (ev/classify.log), hence the pending-ci line; it reads no red at this head.
- RESULT carry_audit: `carry_audit.py check` over this verdict prints `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)` rc 0; the packet's run over the body at this head printed 8 routed, 0 unrouted (ev/carry_audit.txt).
- Head re-read before return: refs/pull/3738/head and refs/heads/fix/r11-seam-cycle-solve are c931e99404d39ceaf9c8d84a68b5e24b7dec5f11 at 05:11Z.

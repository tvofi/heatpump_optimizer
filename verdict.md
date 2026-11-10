Fix review: blocked d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211 ci-red: merge_train classify reads RED at this head (required pr-contract failed closed on a GitHub HTTP 502 deriving the red history, and gate followed it); no code change owed

bus-nonce: f55e96e6a33ea4fd7074aad9d2d67a2c

## Scope

This is review round 4 of #3358, a delta re-review under the owner's 2026-11-09 scope ruling. The previous verdict, at `577c6974205926e7dbaa178b91af96a229ea02f3` (`probe/rev-3358-c8197a4b`), was blocked on CI state alone and raised no code finding. The head `d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211` adds two merges of main over 577c69742: `88f4d521e` (ci: merge main) and `d07f8e9ea`, which merges the authored head `625426279`. `review_carry.py 577c69742 d07f8e9ea` prints `CARRY`, because none of the three branch-only commits is a non-merge (`ev/review_carry.txt`). The PR's own three-dot patch is the same 75 files at both heads. Compared line by line, it differs only in the unchanged context of `tests/structure_budgets.json`, which was rebased onto main's values. The PR's two moves are the same downward deltas: `class_excess_loc` -12 (17549 to 17537) and `max_class_loc` -2 (7925 to 7923) (`ev/patch-interdiff.txt`). No production code in the delta comes from this PR, so the review did not widen.

## Block

- `python3 tools/audit/seat/merge_train.py classify d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211 --pr 3358` read WAIT from 02:57Z to 04:35Z. It exited 1 at 04:36:33Z, printing `RED d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211 pending: none red: gate` (`ev/classify.txt`, `ev/classify-log.txt`).
- The red is the required `pr-contract / pr-contract` 129632709530 in run 42745781214. Its policy_lint step failed closed with `ERROR [pr-body] the red history could not be derived: check-runs at 5e50b92: HTTP 502 from /repos/tvofi/heatpump_optimizer/commits/5e50b92.../check-runs`, which is a GitHub API error and not a body refusal. Every other step of that job passed: preflight `clean`, figure_lint `0 refused`, `no version edit`, and carry_audit `5 routed, 0 unrouted`. The code-kind `gate` 129633034164 then failed behind it. The edit-kind `gate` 129602434404 had already failed at 03:09Z, deferring to run 42745781214 (`ev/ci-runs.txt`). Carry: dismissed: evidence, not a finding
- Every required unit job concluded success, including `tests / fast (3.14)` 129602133122, `tests / mutation` 129599532966, `tests / closures`, `tests / coverage`, all three codeql legs, arch-score and budget-raise-gate.
- Under fix-review.md step 12 a red CI never carries a merge verdict, and this red has concluded, so it is not a pending block.
- What re-dispatch owes: re-run `pr-contract / pr-contract` and the gate in run 42745781214, or whatever re-attempt the train uses for a transient API failure, then classify again at this head. A re-run of the code run's pr-contract may meet the step-less codeql listing that this PR's own `R10-FLY-GH-READ-RETRY` carry describes, in which case an edit run is needed instead. No code or body change is owed. Every substantive check below passed at this head.

## Findings

- Follow-up: in three consecutive review rounds of this PR (`f744ac599`, `577c69742`, `d07f8e9ea`), the review blocked on CI state alone, each time with every unit job green: twice on a standing deferral gate, and this time on pr-contract failing closed on one GitHub 502. This round did not measure the cause beyond the log in `ev/ci-runs.txt`. Carry: dismissed: a CI-infrastructure condition at this head and not a defect of this pull request; it is reported in this verdict's Block for the orchestrator's re-dispatch, which reads it

## Evidence

- Head: `d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211`, still the branch head when this verdict was written (`ev/HEAD.txt`). Every number below was taken there.
- Step 1, mutation proof, re-run at this head (`ev/mutant-MA.diff` and `ev/mutant-MB.diff`, round 3's mutants of `thermal_model.py:329`):
  - Unmutated: `PYTHONPATH=tests/hastub python3 tests/features.py` prints `ALL 5131 FEATURE CHECKS PASSED`, rc 0 (`ev/features-head.txt`). The body's 5071 was counted at `625426279`, and the difference is main's checks merged since.
  - MA prints `1 of 5131 FEATURE CHECKS FAILED`, rc 1: `off the combi option the buffer's store volume ... evaluate no combi predicate`, `[off: 3 predicate evaluation(s) ...]`.
  - MB prints `1 of 5131`, rc 1, failing the same check by its null arm `[off: 0 ...]`.
  - Both match the body's account.
- Steps 2 and 3, harness: `dev/audit/harnesses/r10_combi_tank.py` has sha1 `e47dc605d1d95abd50b796d52730bd3394c36702`, matching the body, and runs with rc 0 (`ev/harness-head.log`). Every RESULT the body quotes is equal at this head: `workaround_tank_kwh_per_c=1.1693`, `combi_tank_kwh_per_c=0.6310`, `combi_store_ua_w_per_k=2.4667`, `off_store_bitwise=1`, `balance_residual_kwh=-7.105e-15`, `ua_zero_residual_kwh=3.553e-15`, `eps_0.6_end_c` = `eps_1.0_end_c` = `62.088350802154`, `lp_flux_separate_none_kwh` = `lp_flux_separate_draw_kwh` = `3.1405`, `exchange_rounds=3`, `exchange_worst_shortfall_c=-1.455`, `null_worst_shortfall_c=28.767`, `exchange_dhw_kwh=22.135`, `null_dhw_kwh=5.327`, and `equiv_{eps,step,floor}_differ=0`. The packet names no finder's harness. The instrument is the fixer's own committed harness, disclosed as such, and I built no instrument.
- Steps 4 and 5: the three-dot diff touches no claim file and none of `VERSION`, `manifest.json` or `RELEASE_NOTES.md`. pr-contract prints `no version edit`.
- Step 7: the body's `## Head` names `d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211`.
- Step 8, figures not re-derived: the body's `2399`-line patch-identity count, its scoped-gate figures (`27 script(s) run`, `29 TEST SCRIPT(S) PASSED`, the 56 golden scenarios and `114 STRESS CHECKS`) and `dS +0.0000` were not re-taken. CI's `tests / closures`, `tests / fast (3.14)` and `arch-score` concluded success at this head. My own patch identity is the interdiff above. Carry: dismissed: evidence, not a finding
- Step 10, forward-carry: the four R10-COMBI-TANK items (body items 7907dbfa, cc665630, c45c9022, 54ed3e93) are in `dev/programme/rosters/wave-r10-groups.json` on `origin/handoff/audit-r10-roster` at `2496ad634`, lines 17754-17757. The R10-FLY-GH-READ-RETRY item d678abfc is at line 7539. pr-contract's carry_audit prints `5 routed, 0 unrouted, 0 bad destination(s)`.
- Step 11: `merge_train.py owed-reds` lists the required set (`ev/owed-reds.txt`). Of that set, only `pr-contract / pr-contract` and `gate` are red at this head (Block). The body answers the earlier heads' reds.
- Step 13: `git merge-tree --write-tree origin/main d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211` at main `b07627250` exits 0, tree `73028f99f` (`ev/merge-tree.txt`). There is no conflict.
- Step 14: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`, rc 0 (`ev/structure.txt`). The budget moves only down.
- The role contract is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

Fix review: blocked 577c6974205926e7dbaa178b91af96a229ea02f3 ci-red: merge_train classify reads RED at this head (two deferral gates failed and pr-contract re-attempt failed closed on the codeql wait); no code change owed

bus-nonce: c8197a4bd2c4d8f9dc4a474bc9728697

## Scope

This is review round 3 for #3358. Round 1 blocked `64d4e7dbc` on the `tests / fast (3.14)` stress red. Round 2 blocked `f744ac599` on CI state alone and found every substantive check passing. This round measured head `577c6974205926e7dbaa178b91af96a229ea02f3`, a github-actions `ci: merge main` commit. `tools/audit/seat/review_carry.py` prints `CARRY` from both `7bad175e1` and `f744ac599` to this head (`ev/review-carry.txt`). The reviewed patch is therefore round 2's, and this round re-took its key measurements at this head. The role contract is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Block

- `python3 tools/audit/seat/merge_train.py classify 577c6974205926e7dbaa178b91af96a229ea02f3 --pr 3358` exited 1 at 16:24:35Z and again at 17:50:06Z, printing `RED 577c6974205926e7dbaa178b91af96a229ea02f3 pending: none red: gate` (`ev/classify.log`).
- Behind it are two deferral gates, which `latest_runs` keeps as the worst suite (A5) and which GitHub's ruleset also reads as non-success (`ev/ci-runs.txt`):
  - gate 129247913713 (run 42636985416, edit kind), `failure`, log `FAIL run(s) [42635950938, 42636336860] at this head are still being judged; their gate decides`.
  - gate 129283823160 (run 42636336860, code kind), `failure`, log `FAIL run(s) [42635950938] at this head are still being judged; their gate decides`.
- The run they deferred to, 42635950938, was cancelled at 16:24 when main moved to `ebf90bd27`. Its re-attempt concluded gate 129334713797 `success` at 17:44. In the same re-attempt, the required `pr-contract / pr-contract` 129328706084 failed. The failure was `tools/ci/codescan_wait.py`'s fail-closed `this run's codeql jobs were not listed finished after 600 s`, not a body or code refusal: its figure_lint, preflight and carry_audit steps all passed. `pr-contract / pr-contract` 129283238729 in run 42636336860 concluded `success`. Carry: dismissed: evidence, not a finding
- None of these reds is the PR's code. Every unit job concluded success or skipped, including `tests / fast (3.14)` (129226098164, 129228196968) and `tests / mutation` 129225705858. Under fix-review.md step 12, though, a red CI never carries a merge verdict, and the brief makes classify rc 1 RED.
- What re-dispatch owes: re-run the two failed deferral gates, or whatever the orchestrator's train uses to clear a superseded defer red, and the pr-contract re-attempt. Then classify again at this head. No code or body change is asked for. Every check below passed at this head.

## Findings

- Follow-up: in two consecutive review rounds of this PR (round 2 at `f744ac599`, this round at `577c69742`), the only red was a `gate` deferral ("still being judged; their gate decides") left standing after the run it deferred to later went green or was cancelled by a main move. Each time the review had to block on CI alone, with no defect in the PR. This is the orchestrator's CI-state handling, not this PR's to settle, and this round does not measure its cause beyond the logs in `ev/ci-runs.txt`. Carry: dismissed: a CI-state condition of the train at this head and not a defect of this pull request; it is reported in this verdict's Block for the orchestrator's re-dispatch, which reads it

## Evidence

- Head: `577c6974205926e7dbaa178b91af96a229ea02f3`, still the PR head at 17:50Z (`ev/HEAD.txt`). Every number below was taken at it.
- Step 1, mutation proof, re-run at this head (`ev/mutant-MA.diff`, `ev/mutant-MB.diff`). The suite now holds 5031 checks, against the body's 5017 at `8944540ca`; the difference is main's checks merged since.
  - Unmutated: `PYTHONPATH=tests/hastub python3 tests/features.py` prints `ALL 5031 FEATURE CHECKS PASSED`, rc 0 (`ev/features-head.txt`).
  - MA (`if self.combi_tank_active:` at `thermal_model.py:329`) prints `1 of 5031 FEATURE CHECKS FAILED`, the FAIL being `off the combi option the buffer's store volume, capacity and UA evaluate no combi predicate; ...` `[off: 3 predicate evaluation(s) ...]`.
  - MB (`if self.dhw_combi_tank_enabled:`) prints `1 of 5031 FEATURE CHECKS FAILED`, the same check by its null arm, `[off: 0 ...; on: 0, 544.0]`. Both match the body.
- Steps 2 and 3, harness: `dev/audit/harnesses/r10_combi_tank.py` has sha1 `e47dc605d1d95abd50b796d52730bd3394c36702`, matching the body. At this head every RESULT line the body quotes is equal (`ev/harness-head.log`): `combi_tank_kwh_per_c=0.6310`, `workaround_tank_kwh_per_c=1.1693`, `combi_store_ua_w_per_k=2.4667`, `off_store_bitwise=1`, `balance_residual_kwh=-7.105e-15`, `ua_zero_residual_kwh=3.553e-15`, `eps_0.6_end_c` = `eps_1.0_end_c` = `62.088350802154`, `exchange_rounds=3`, `exchange_worst_shortfall_c=-1.455`, `null_worst_shortfall_c=28.767`, `exchange_dhw_kwh=22.135`, `null_dhw_kwh=5.327`. The packet names no finder's harness. The issue is an outside user's (#3225), and the instrument is the fixer's own committed harness, disclosed as such. I built no instrument.
- The stress channel: I did not re-run `tests/stress.py` locally. CI's `tests / fast (3.14)` concluded success at this head in both runs (129226098164, 129228196968), and round 2 re-derived the MA counts to the call. Carry: dismissed: evidence, not a finding
- Steps 4 and 5: the three-dot diff `72a2acee5...HEAD` touches neither claim file nor `VERSION`, `manifest.json` or `RELEASE_NOTES.md`. pr-contract's version-edit step prints `no version edit`.
- Step 6, class: the three censuses (`combi_store_view`, `combi_flux_live`, `combi_tap_limit`) run inside `tests/features.py` and pass at this head. I did not re-derive their base enumeration. Carry: dismissed: evidence, not a finding
- Step 7: the body's `## Head` names `577c6974205926e7dbaa178b91af96a229ea02f3`.
- Step 8, figures not re-derived: the per-scenario production-call totals and the `+5882` split, which come from the fixer's scratch probe and which stress.py prints no number for on a pass, and the `--pin-killed` counts. Carry: dismissed: evidence, not a finding
- Step 10, forward-carry: the four `## Forward-carry` items (unwired-combi-set, exchange-accounting, exo-seed-census-only, bankaifan-trailer) are in group R10-COMBI-TANK's carries in `dev/programme/rosters/wave-r10-groups.json` on `origin/handoff/audit-r10-roster` (`d3d52f3ee` when read), each with its control. carry_audit prints `4 routed, 0 unrouted, 0 bad destination(s)`.
- Step 11, red checks: `merge_train.py owed-reds` lists the required set (`ev/owed-reds.txt`). Of that set, only `gate` and the one `pr-contract / pr-contract` re-attempt are red at this head, as covered under Block. The body answers the earlier heads' `tests / fast (3.14)`, `tests / mutation` and `tests / mutation-autofix` reds. `governance / delivery-status` is not owed.
- Step 13: `git merge-tree --write-tree origin/main 577c6974205926e7dbaa178b91af96a229ea02f3` at main `2f6d699e5` exits 0, tree `5699ee7d8` (`ev/merge-tree.txt`). There is no conflict.
- Step 14: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` (`ev/structure.txt`). The three-dot diff of `tests/structure_budgets.json` moves only down (`class_excess_loc` 17554 to 17542, `max_class_loc` 7931 to 7929). arch-score and budget-raise-gate concluded success.

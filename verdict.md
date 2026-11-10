Fix review: merge d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211

bus-nonce: 5f3e299001d43cbb29deb7cceb9c643b

## Round

Round 4, second review at the same head (the first was blocked on a pr-contract HTTP 502, which is infrastructure only and carries nothing). The body already carries the round-4 re-cut section that `fixer.md` owes from the fourth round.

## Evidence

- Head measured: `d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211` (ev/HEAD.txt). It is a merge of `88f4d521e` (github-actions "ci: merge main" of `577c69742` with main `20d96598c`) and the authored head `625426279`. The PR base is `20d96598c`. `review_carry.py 577c69742 d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211` prints `CARRY`.
- Patch identity: `git diff -U0 72a2acee..577c6974` and the three-dot `20d96598c...d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211`, each filtered to +/- lines, give 2399 lines apiece. They differ only in the four `tests/structure_budgets.json` lines, because main moved those numbers. The deltas are the same in both: `class_excess_loc` 17549 -> 17537 (-12) and `max_class_loc` 7925 -> 7923 (-2). Both budgets only go down (ev/patch_identity.txt).
- Merge with main: `git merge-tree --write-tree origin/main d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211` exits 0 with no conflict, against origin/main `e3295ba46` (ev/merge_tree.txt).
- CI: `merge_train.py classify d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211 --pr 3358` exited 0 with `GREEN d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211 pending: none red: none` (ev/classify.log). It read WAIT twice while the re-run gate job 129641034375 was queued. The live check-runs list has nothing red. pr-contract / pr-contract 129638755980 started 04:53Z, after the re-run, and concluded success, so it is the body check of record. budget-raise-gate is success. The owed-reds set is in ev/owed_reds_contexts.txt, and no context in it is red at this head.
- Red checks: the body's `## Red checks` answers every red on the branch's earlier heads. The pr-contract 502 on the first attempt at this head was infrastructure, and its re-run is green, so this head owes no answer.
- Mutation proof (step 1). Every run below is `PYTHONPATH=tests/hastub python3 tests/features.py` in a detached worktree at this head:
  - Unmutated: `ALL 5131 FEATURE CHECKS PASSED`, rc 0.
  - MA, `thermal_model.py:329` changed to `if self.combi_tank_active:`: `1 of 5131 FEATURE CHECKS FAILED`, rc 1. The failing check is the off-option predicate count, `[off: 3 predicate evaluation(s) ...; on: 1, 544.0]`.
  - MB, line 329 changed to `if self.dhw_combi_tank_enabled:`: `1 of 5131` failed, rc 1, the same check at `[off: 0 ...; on: 0, 544.0]`.
  - Both match the body's failure readings.
  - MC, my own mutant: `optimizer.py:1457` changed from `tank_exo_kw=space_net` to `tank_exo_kw=None`, so the exchange no longer sees the space flux. Result: `2 of 5131` failed, rc 1, on the exchange shortfall check `[worst shortfall 28.767...]` and the build-count check.
  - Diffs and logs: ev/mutant_*.diff, ev/features_*.log.
- Feature count: the body quotes 5071, which was taken at `625426279`. I measured 5131 at `d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211`. Main's `b8f67a7..20d9659` adds 849 lines to `tests/features.py` (65 added `check(` lines), which explains the +60. I did not rebuild `625426279` to re-derive the exact figure of 5071.
- Harness (steps 2-3): `dev/audit/harnesses/r10_combi_tank.py` has sha1 `e47dc605d1d95abd50b796d52730bd3394c36702`, which matches the body. At the head it exits rc 0, and every RESULT the body quotes reproduces exactly (ev/harness_head.log):
  - store: `workaround_tank_kwh_per_c=1.1693`, `combi_tank_kwh_per_c=0.6310`, `combi_store_ua_w_per_k=2.4667`, `off_store_bitwise=1`
  - residuals: `balance_residual_kwh=-7.105e-15`, `ua_zero_residual_kwh=3.553e-15`
  - effectiveness: `eps_0.6_end_c` = `eps_1.0_end_c` = 62.088350802154; `legionella_eps_*=(True,4,1.0)`
  - LP flux: `lp_flux_separate_none/draw_kwh=3.1405/3.1405`, `lp_flux_combi_none/draw_kwh=3.0285/6.7956`
  - exchange vs null: `exchange_rounds=3`, `exchange_worst_shortfall_c=-1.455`, `exchange_dhw_kwh=22.135`; `null_rounds=0`, `null_worst_shortfall_c=28.767`, `null_dhw_kwh=5.327`
  - equivalence: `equiv_eps/step/floor_differ=0` over 11/53/56 cases; tie controls `1/3/3` on ties and `0` off ties
  - The harness cannot run at the base, where the combi fields do not exist. The body discloses this, so it is measured at the head only. The harness is committed in the tree, and the review packet notes "Finder's harness: none named". It is the fixer's instrument and is disclosed as such.
- Golden drift (step 4): `env_drift.py --all 20d96598c` printed `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56 committed fixture(s)`, rc 0. No claim file is touched (ev/env_drift.log).
- Versions (step 5): `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched in the three-dot diff.
- Structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`, and the budgets only go down.
- Architecture score: `score.py --diff 20d96598c` printed `Architecture score: dS +0.0000 NULL`.
- Class (step 6): the body names three censuses as its enumeration rules, `combi_store_view`, `combi_tap_limit` and `combi_flux_live`, and `tests/features.py` at the head carries all three. Combi cannot be reached by any loader in this PR, and the off-option configurations are pinned bitwise and by golden drift.
- Forward-carry (step 10): on `origin/handoff/audit-r10-roster`, `wave-r10-groups.json` carries all four R10-COMBI-TANK items (unwired-combi-set, exchange-accounting, exo-seed-census-only, bankaifan-trailer); the first three are marked moved to PR-B. The `codescan_wait.py` `settled()` carry is on R10-FLY-GH-READ-RETRY. The packet's carry_audit reads `5 routed, 0 unrouted`.
- I did not re-run the gate or the mutation table, which is CI's heavy work. The CI `gate` and `tests / mutation` runs at this head are success.

## Findings

none

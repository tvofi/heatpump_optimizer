Fix review: blocked ce4cdb2271c3a3883c422e228f55d526d93827e2 ci-red: gate red, tests codeql governance hassfest validate never ran at this head and pr-contract failed closed on codeql

bus-nonce: 04b43806e2e3e6d45158d0e5f57f4d85

Round 1. Measured head ce4cdb2271c3a3883c422e228f55d526d93827e2; the body's measurements were taken at 85acb2c184e685e2289af52ad39a8def1b3995dc, and `review_carry.py 85acb2c ce4cdb2` prints CARRY (only a main merge and the delivery row lie between them; no diff in custom_components, tests/features.py or the harnesses).

## Block

`merge_train.py classify ce4cdb2271c3a3883c422e228f55d526d93827e2 --pr 3371` exited 1: `RED ... pending: none red: gate`. Neither run at this head (42597670888, 42598782881) ran `tests`, `codeql`, `governance`, `hassfest`, `validate` or `kernel-points`. All were `skipped`, and the PR is `draft: true`. The `gate` job (`KIND: edit`) printed `FAIL tests: no run at this head judged base 'main'`, the same for codeql/governance/hassfest/validate, and `pr-contract / pr-contract: failure`. Both `pr-contract` runs failed closed: `FAIL closed: no run at this head owns a finished codeql unit for base 'main' after 600 s`. The red does not come from the authored code. But the heavy suite (full gate, goldens, stress memory probe, mutation lane) has never run at this head, and fix-review step 11 has me cite CI's heavy runs, not re-run them. Every check I could run myself passes (Evidence). Once a run at this head (or a carried head) runs `tests` and `codeql` and the gate is green, a re-review needs only CI and the step-11 answer for `pr-contract`'s red. Note the body's own local `tests/run.sh` read `1 TEST SCRIPT(S) FAILED` (`tests/stress.py` memory peaks). The body attributes that to the base's bimodal traced peak, and I did not re-derive it; CI's `tests` lane has to settle it. Also, `## Red checks` reads `none`, but `pr-contract` is now red at this head. The cause is outside the diff (no codeql run), but the body has to answer that red once the head's workflows conclude (defect-root-cause.md enforcement).

## Findings

- Follow-up: the finding's harnesses `dev/audit/harnesses/r10_cop_gate_slab.py` and `r10_cop_gate_band.py` were built by the fixer in this PR. The packet reads `Finder's harness: none named` (fix-review step 9). The body discloses them as this branch's files and runs them at both ends from an export; they land in the tree and are in the closure. I ran both myself at base and head. Carry: dismissed: harness disclosed as the fixer's own and committed by this PR (fixer.md 18), measured independently below
- Follow-up: Carry 2 (set-point-to-draw linearity) stays open, carried to #3106. Its control (≥3 distinct space-only flow set-points strictly inside 25.25–54.5 degC, the `--synthetic` null reading `gain_kw_per_k=0.1 max_resid_kw=0.0`) is stated in the committed harness docstring and the PR body, not in the #3106 issue body or the roster brief. When R10-COP-GATE-E goes `done` at merge, the carry needs a live destination, e.g. `dev/programme/carries/carry-3106.json`, holding that precondition. Carry: #3106

## Evidence

- Merge with main: `git merge-tree --write-tree origin/main ce4cdb2` exit 0 at origin/main 806e952ca (`LEDGER-MERGE: resolved tests/closures.json`, no conflict), in `ev/merge-tree.txt`.
- Role currency: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Block at head (`BLOCK_CMD` from the body): `ALL 17 FEATURES BLOCK PASSED` (`ev/block-head.txt`).
- Mutation proof, all restored, `git status --short` empty after:
  - M1 `(a.space, a.dhw),` -> `coord._commanded_split(),`: `2 of 17 FEATURES BLOCK FAILED`, switch-back `24.1700/23.5050/24.1700`, switch-out `24.1700/23.5050/22.8400`. Matches the body.
  - M2 drop `a.observed or`: `1 of 17`, switch-out `22.8400/23.5050/22.8400`. Matches the body.
  - M3 (mine) `space_served=True`: `2 of 17`, kills the #2499 dhw-only check and switch-out. The `space_served` gate is pinned on both arms.
- Finder-shape harness, my own RESULT lines (`ev/harness-both-ends.txt`, sha1 slab 746454bbf9a3e19b89c263ef7a98bb2f187f5d2d, band 02129ef0ca51334e432e34e50150ea29dd49e2a7, as in the body):
  - At base ba6fd7e8b, 4.0 kW: all_space `over_kw=0.0 slab=24.1700`; switch_back `booked_kw=4.0 over_kw=2.0 slab=24.1700`; switch_out `booked_kw=0.0 over_kw=-2.0 slab=22.8400`; truth `slab=23.5050`.
  - At head, 4.0 kW: all_space identical (the null holds at both ends); switch_back and switch_out `booked_kw=2.0 over_kw=0.0 slab=23.5050`, equal to truth.
  - Perturbation `--drawn 6.0`: base `over_kw` 3.0 / -3.0 (scales with the draw); head 0.0 / 0.0, slab 23.8375 vs truth 23.8475. That is the 0.01 K the body attributes to learner folds on truth's clean interval; I did not re-derive that attribution.
- Rule comparison re-derived from these lines: base 24.1700-23.5050 = +0.665 K; plan fall-back 25.0000-23.5050 = +1.495 K; prorate 0.000 K. Matches.
- Band harness at both ends: `owner-2026-10-30-away.json steps=1 distinct_c=1 fit=none`, `synthetic-dhw-only.json steps=0 ... fit=none`, `synthetic-linear steps=4 distinct_c=4 gain_kw_per_k=0.1 max_resid_kw=0.0`. Matches. I did not re-derive the 47 degC / 1.55 kW step or the 35 degC exclusion.
- Other configurations: `heat_energy.observed_duty` maps only MODE_HEAT/MODE_DHW to a duty; a combined, off or stale mode is an unobserved segment, so `ModeDwell.shares` returns None and the plan-split / live-mode rule stands unchanged. An observed attribution therefore always sums to the window's hours > 0, so `space_share`'s total-0 fallback to 1.0 cannot pair with the new `a.observed` arm.
- Class rule `git grep -n "_commanded_split()" -- custom_components`: 8 sites at head, all in coordinator.py (`_fold_flow_lift`, `_interval_measured_heat_kw`, `_propagated_slab`, `_async_learn_heat_span`, `_commanded_power`, `_interval_space_power`, `_cop_reference_curve`, `_record_accuracy`). These match the body's eight dispositions, and I read `_fold_flow_lift` and `_interval_space_power` (route through `meter.attribution` / `ran_hot_water`). No open seam (`ev/class-rule.txt`).
- Ratchet: `tests/structure.py` at head `STRUCTURE RATCHET PASSED`, `class_excess_loc 17557 <= 17557`. Step 14: with the payment reverted (`_interval_measured_heat_kw` back to three statements) it reads `FAIL class_excess_loc 17559 > 17557 (+2)` (`ev/structure-payment-removed.txt`), so the movement comes from the named mechanism. The fold inlines two single-use locals and makes that line identical to its two siblings; I judge it a sound simplification, not packing. The body's `+3` at 214c0e22f was not re-derived at that commit.
- Arch score: CI `arch-score` success in both runs. The body reports `dS -0.0012 WORSENS (coord_footprint 2489->2491)` with no budget raised; `git diff --stat` of `*_budgets.json`, VERSION, the manifest, RELEASE_NOTES.md and both claim files over the merge base prints nothing. CI `pr-contract` printed `no version edit`.
- `tests/closure.py select --diff a5dce6b9e`: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
- carry_audit (CI, at head): `CARRY-AUDIT: 1 finding item(s): 1 routed`. figure_lint (CI): `FIGURES: 10 resolved, 3 not verified, 0 refused`.
- CI: `ev/ci-red.txt`, `ev/classify-final.txt`, `ev/classify-poll.log`.

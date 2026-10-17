Fix review: blocked 13c98d851e1e63002c951629590fbec95b5a6693 root-cause-unanswered: fast (3.14), mutation, mutation-autofix went red, unanswered

bus-nonce: e9a77dea498c95f8dd86f772de3d1814

Measured head: 13c98d851e1e63002c951629590fbec95b5a6693 (the head this dispatch named).
Head re-read before posting: the PR head has moved to 3f961c51674f097a722426a71b37046764a10f87
("ci: merge main", pulling #2340). That merge does not touch optimizer.py, the golden
fixtures, or the mutation ledger pin at optimizer.py:1883, so every number below survives
at the new head; the CI check-runs below are this head's own runs and are per-head.

## Blocking findings

### 1. root-cause-unanswered (fix-review step 11): three checks red, body silent
pr-contract itself refuses, at this head:
  red checks the body must answer: fast (3.14),mutation,mutation-autofix
  ERROR [pr-body] check `fast (3.14)` is red and `## Red checks` does not name it
  ERROR [pr-body] check `mutation` is red and `## Red checks` does not name it
  ERROR [pr-body] check `mutation-autofix` is red and `## Red checks` does not name it
The body's `## Red checks` names only tests/structure.py, archscore and the D2-s2-01
features sub-check (all now green). None of the three live red checks is named or answered.

### 2. Unclaimed golden drift — the cause of `fast (3.14)` red (fix-review step 4)
`env_drift.py --all` reports 3 UNCLAIMED DRIFT(S) vs origin/main: valve_storage_flat_prices,
valve_storage_low_target, valve_storage_small_tank. Each moves
predictive_info.solar_reduction_factor 0.98877 -> 0.991134 and predictive_info.pre_heat_urgency
0.15754 -> 0.162269 (plus small displace_schedule leaves). CI's `fast (3.14)` failed on
env_drift (1 TEST SCRIPT(S) FAILED).

The body claims the fix "is a no-op on the fixture corpus" because "the two-zone golden's
upper/lower losses are the defaults whose sum equals heat_loss_coefficient". That is false:
the two-zone golden house is profiles.house(two_zone=True) -> upper=0.10, lower=0.09
(sum 0.19), but heat_loss_coefficient stays at its 0.15 default. The typical_heat_loss fix
replaces heat_loss_coefficient (0.15) with upper+lower_floor_heat_loss_learned (0.19), a
26.7% change in the forecast summary's whole-house UA, so solar_reduction_factor and
pre_heat_urgency move in every two-zone plan fixture. The moved fixtures are unclaimed in
tests/golden/claimed_drift.txt. This is a claim-files violation, not machine drift (the
direction and the causal chain are deterministic; ratio is 1.0 throughout).

### 3. Unpinned mutation site — the cause of `mutation`/`mutation-autofix` red
`mutation` (mutation_table.py) REFUSED: "4348 unpinned site(s) against 4348 at the ratchet
base 10d00fe0f, 1 of them added by this diff". `mutation-autofix` failed with
"skip-measure-failed -- THE REPAIR DID NOT HAPPEN. Pin the new sites yourself and commit
tests/mutation_ledger/". The body's "Unpinned sites" section claims optimizer.py:1883
RETURN_DEL was "pinned by mutation-autofix after the push" — that autofix did not run; the
site is still unpinned and must be recorded under killed_by or survivor_triage.

## Verified clean (the five dispatch items)

1. optimizer.py:2982 class-open: fixed, not just dispositioned. `_house_ua_kw_per_c` is
   extracted and typical_heat_loss/hold_demand_kw/_buffer_charge_ceiling all call it. The
   enumeration `grep -rn "heat_loss_coefficient" custom_components/heatpump_optimizer/*.py`
   returns nothing undispositioned: the single-zone/upper-zone arms, the slab cap, the
   dimensionless weather factor (coefficient cancels), the sysid fit base (refused D-2) and
   the helper's own single-zone arm are all correct-by-construction; mixing_valve.py:81/108
   is a parameter (all callers pass upper+lower_learned). The one open seam is
   coordinator.py:10403, forwarded to R10-SCORES.
2. carry-missing: fixed. The envelope-score carry is in R10-SCORES' `brief` string as
   item (4), carrying the mechanism, the split-1.0 null arm and a re-measure instruction;
   `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` -> 0 errors,
   0 warnings.
3. Mutation proof M0/M1' and both-ends harnesses: M0 `ALL 1 FEATURES BLOCK PASSED`; M1'
   (call site -> `p.heat_loss_coefficient * p.house_heat_loss_scale`) `1 of 1 FEATURES BLOCK
   FAILED` with the body's exact rows. reparam_sites space_demand_rel_diff 0.4367 -> 0.0000;
   ratio_v2 space_demand_vs_dynamics -0.2213 -> +0.0000; D-2 rows flat at both ends.
4. Step 14 metric-gamed: earned. Removing the helper reverses structure.py duplication_copies
   34 -> 35 (FAIL 35 > 34) and archscore dS +0.1937 -> NULL. No other metric moved.
5. VERSION/manifest/notes untouched (diff touches none; pr-contract "no version edit").

## RESULT lines

RESULT reparam_sites.space_demand_rel_diff baseline=0.4367 (A 7.741 kW -> 11.122 kW model-consistent)
RESULT reparam_sites.space_demand_rel_diff head=0.0000 (A 11.122 kW)
RESULT reparam_sites.--ratio-1.0 space_demand_rel_diff=0.0000 at both ends
RESULT ratio_v2.space_demand_vs_dynamics baseline=-0.2213 head=+0.0000 (r=1.6)
RESULT ratio_v2 D-2 fit heat_loss_kw_per_c=189.9 true effective=244.0 (r=1.6) flat at both ends
RESULT features_block "#2239 (class widened)" M0=ALL 1 FEATURES BLOCK PASSED
RESULT features_block M1'=1 of 1 FEATURES BLOCK FAILED (rows [(False,1.0,0.9487,0.9487),(True,1.0,0.9487,0.9595),(True,1.6,0.9487,0.9685)])
RESULT brief_lint wave-r10-groups.json=0 errors, 0 warnings
RESULT structure.py=STRUCTURE RATCHET PASSED duplication_copies 34<=34 (all else at budget)
RESULT archscore=+0.1937 IMPROVES (66->65); helper removed -> NULL (earned)
RESULT env_drift --all=3 UNCLAIMED DRIFT(S): valve_storage_flat_prices, valve_storage_low_target, valve_storage_small_tank (solar_reduction_factor 0.98877->0.991134, pre_heat_urgency 0.15754->0.162269)
RESULT _house_ua_kw_per_c vs old on two-zone golden house=0.19 vs 0.15 (body's "no-op" premise false)
RESULT check-runs@13c98d851 RED=fast (3.14), mutation, mutation-autofix, pr-contract
RESULT merge-tree origin/main HEAD=exit 0 (no conflict; structure_budgets resolved by ledger-merge)

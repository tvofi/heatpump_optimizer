Fix review: blocked b7a34f98aa6013a542e21d28a76bc5159fe7e14f claims: tests/optimality.py retires the one|summer_negative|shoulder cert claim, CI fast (3.14) measures ladder +10.55 % at this head; also carry-missing to O13 and the residual's cause misstated

bus-nonce: 8d07421b422ab1400098fe357c7be0ff
PR: #2411 (R10-SAV-BASELINE, #2255). Round 1 (no earlier verdict on the PR).
Reviewed head: b7a34f98aa6013a542e21d28a76bc5159fe7e14f (still the head at writing). Merge base 413944b6772fa7f2f38cef7ea2f667a64d79251a.
Evidence: ~/hpo-seats/r10s3/review-2411/evidence/
Contract: dev/governance/roles/ diff merge-base...origin/main empty (current).

## What holds

- Step 1, the mutation proof: `r10_sav_baseline_mutants.py` on a scratch copy of the head. M0 0 failing; M1 to M16 all killed (M1 6 failing, M2 5, M3 5, M4 3, M5 1, M6 2, M7 1, M8 3, M9 1, M10 3, M11 2, M12 1, M13 1, M14 1, M15 1, M16 1). M1 and M2 kill one more check each than the body's table (taken at e86c2085d). That is the steady-state check d2220949d adds, which matches the body's "the head adds only checks". `evidence/mutants-head.txt`.
- Steps 2 and 3, the harness at both ends: `r10_sav_baseline.py` at the head and at the merge base 413944b67 (the harness copied into the base tree). Both print what the body quotes.
  RESULT head transient spread 0.00 kW (2.06 kW x4); base 6.00 kW (0.00/6.00/6.00/0.00)
  RESULT head cost row actual 15.0 = receipt 15.0; base 3.0 vs 15.0
  RESULT head coverage scale 28.00; base 2.80
  RESULT head null 10.83 % (thermostat 128.4 kWh, plan 114.5 kWh, room 18.79 vs target 20.44 C), DEFECT; base 43.66 % (203.6 / 114.7 kWh), DEFECT
  Step 9: the finding had no committed harness (the owner's screenshot). Both harnesses are the fixer's own, and the body discloses that.
- Step 5: pr-contract's version-edit step at this head prints "moves none of VERSION, the manifest version or a notes heading".
- Step 7: the body names b7a34f98a as the head. That is the live head.
- Step 13: `git merge-tree --write-tree origin/main HEAD` (main f1b21daab) exits 0 and prints nothing to stderr.

## Blocking

0. **claims: the retired optimality claim still has its gap on CI.** The body says the held baseline closed the two #1294 claims ("Head: 0.0000 % for all three", measured on the arm64 seat), and the diff deletes `one|summer_negative|shoulder` and `one|winter_narrow|shoulder` from `_CERT_CLAIMS`. CI's `fast (3.14)` (check-run 117692786859, concluded failure 14:11:11Z) runs `tests/optimality.py` at this head:
   RESULT ci cert one|summer_negative|shoulder obj 0.305809 re-polish +0.0051% ladder +10.5544% claimed=False -> FAIL "no unclaimed gap above the bar" (bar 0.1000 %); "1 of 84 OPTIMALITY CHECKS FAILED"
   RESULT ci cert one|winter_narrow|shoulder re-polish +0.0000% ladder +0.0000% (that retirement holds on CI)
   The body's 0.0000 % for summer_negative does not survive CI's platform. The arm64 figure is not the gate's. That cell's claim must stay, or the gap has to close on CI's platform. `evidence/ci-fast-117692786859-optimality.txt`. This is also a red the body's `## Red checks: none` does not answer.

1. **carry-missing: O13 has no in-tree carry.** The body sends the flat-price residual and the `summer_dhw_only` start-bound limit to "O13 (orchestrator's brief)". O13 has no roster group. `git grep -w O13 origin/main` finds only a PNG, and no `dev/programme/carries/carry-<N>.json` exists for it. The one copy is `~/hpo-orch/r10s3/orch/briefs/O13-comfort-matched-baseline.md`, out of tree. `finding-propagation.md` says a stage with no live roster group needs its own carry file, and "the producing PR does not merge until the carry is in the tree". The out-of-tree brief also omits the `summer_dhw_only` limit (-12.74 % at head, -3.17 % on main), which the body says went "to O13 beside the comfort-matched baseline". The second carry is not in the tree either. At origin/main and at the orchestration worktree, the R10-SCORES and R10-ADVISOR roster briefs do not hold the row semantics ("carry appended by the orchestrator"); `test("actual_sek|baseline_sek|receipt total")` is false for both briefs.

2. **The residual is not fully explained, and the carry states the wrong cause.** The body says the 10.83 % is "comfort traded for money ... not a pricing or accounting error", and the O13 brief inherits that premise ("drive the null to ~0" by matching comfort). I built my own instrument (`evidence/null_explain.py`, disclosed as the reviewer's, not the finder's). It replays the harness's null loop exactly and prices a steady thermostat both at the comfort target and at the room the plan delivered, with the production `_floor_demand_at_target` and `compute_cop`. The plan's thermal energy balance closes exactly (240.0 = 240.0 kWh_th), so the decomposition is not an approximation artefact.
   RESULT probe steady thermostat at target 128.4 kWh = booked 128.4 kWh (the held baseline is exact)
   RESULT probe steady at the delivered room 121.7 kWh: comfort gap 6.6 of the 13.9 kWh gap (about 5 of the 10.83 points)
   RESULT probe power-weighted COP plan 2.096 vs thermostat 1.787 (+17.3 %): the plan runs in the warmer hours of winter_cold (outdoor -16 to -8 C), about 19.8 kWh_e
   RESULT probe the plan ends with +23.7 kWh_th more stored heat than it started with (room 21.00/slab 22.00 -> 19.36/30.01), about -13.3 kWh_e that the 2-day month row does not settle
   Control, the same loop at a constant outdoor temperature (`evidence/null_const_outdoor.py`): COP gain +0.00 %, gap 15.6 kWh = comfort 5.1 + start stored-heat drawdown 10.1 (net 18.6 kWh_th drawn from the 21/22 C start).
   So the residual has three terms. (a) The comfort trade the body names, about half. (b) A COP-timing gain at a flat price. That is a real saving: a flat-price null is not about 0 while COP varies with outdoor temperature, so a comfort-matched baseline alone cannot reach 0 without hiding it. (c) The stored-heat change across the harness's 2-day window. Only predicted_savings settles that term; the month row does not. Here it offsets (b). The carry to O13, and R10-ADVISOR's own carried null ("savings about 0 on a flat-price profile"), must state the control that separates these terms: a constant-outdoor arm, or COP-flat, plus a window long enough, or settled at both ends, for (c). Otherwise O13 pursues an unattainable target. This finding changes a later stage, so it is carried, not noted.

3. **pr-contract is red at this head, and the body's `## Red checks` says "none".** Both pr-contract runs (117692504964, 117692618046) print `REFUSE 'Closes #2255' closes #2255; not in the intended list`. The roster group has `fixes: []`, and its own brief says "a closing keyword only for those in `fixes`, and Part of for the rest". The roster and the issue body disagree here (#2255 asks for a closing keyword). Whether to add 2255 to `fixes` or rewrite to "Part of" is the orchestrator's call. But the red is unanswered in the body (step 11).
   Other reds at this head: `mutation` (117692723200) is `MUTATION TABLE REFUSED -- 4324 unpinned site(s) against 4303 at the ratchet base, 23 of them added by this diff`. Those are the sites `## Unpinned sites` lists: 22 lines, with 5326 CLAMP_DROP*2 counted twice. They are answered there, and `mutation-pins (1-3)` were still running when I posted. When I posted, the head's workflows had not all concluded, and no pr-contract run had started after the fast red. So I do not post `root-cause-unanswered`. The fixer owes the body an answer for pr-contract and fast.

## Not verified by me

- The golden drift with claims (50 claimed fixtures, 19 suspended may-drift entries), the structure rows and the archscore figure: cited from CI (env-matrix, arch-score and budget-raise-gate are green at this head), not re-run.
- The `tests/optimality.py` figures: I did not re-run them locally. They are cited from CI's fast run (blocking item 0).
- Step 6, other configurations: the null arm runs single-zone only. I ran no two-zone or zero-evidence null. The constant-outdoor arm above is the only extra configuration.

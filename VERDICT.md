Fix review: merge 3b6e599df04ece95e9615addb19c86d9339328a3

bus-nonce: 1333f82e3d257a2e55e22c2ac90d2d1e
PR: #2411 (R10-SAV-BASELINE, #2255). Round 2. Round 1 was comment 6251182230, blocked at b7a34f98a.
Reviewed head: 3b6e599df04ece95e9615addb19c86d9339328a3, still the head at writing (17:02Z). Merge base 211c8290eda31038fcfe70cd526ab912cf92b103. origin/main 5a41a56696c6bd6245b7cc1261a39a5057ba6bb0.
Evidence: ~/hpo-seats/r10s3/review-2411/evidence-r2/
Contract: the `dev/governance/roles/` diff from the merge base to origin/main is empty, so the contract is current.

## Round 1's blocks, re-checked

- Item 0 (claims): fixed. CI's `fast (3.14)` at this head (117721570437, success) prints these lines:
  RESULT ci cert one|summer_negative|shoulder obj 0.305809 ladder +10.5539% claimed=True; "no unclaimed gap" ok; "a recorded claim still has a gap (not stale)" ok
  RESULT ci cert one|winter_narrow|shoulder ladder +0.0000% claimed=False; ok
  The earlier fast reds at 36723a969 (117704407882, 117704447188) sit on b7a34f98a without eeb607dd6, which is not an ancestor. In both runs only `tests/optimality.py` failed (1 of 84). The `FAIL a3:*` lines in those logs are a self-test's negative controls.
- Item 1 (carry-missing): fixed. All three carries are at `origin/handoff/audit-r10-roster` 97344315a, the branch where `roster_edit append-carry` lands carries by design, never main (`evidence-r2/roster-diff.txt`):
  - New group R10-SAV-COMFORT (69f670ca8, a5f7df8f4). Its carry holds the three null terms, the `const`-arm control, an acceptance stated as a precondition (the const arm with stored heat settled reads about 0; the varying arm reads the timing term, not 0), and the `summer_dhw_only` limit (-12.74 % / -3.17 % / 1.95 % / away_setback 60.71 %).
  - R10-ADVISOR gets the restated null with the `const` arm as its control, marked "restating carry (1)", plus the row semantics.
  - R10-SCORES gets the row semantics.
  R10-SAV-BASELINE's roster `fixes` is [2255] on main and on the roster branch.
- Item 2 (the residual's cause): fixed. The body and the carries now state the three terms, not "comfort traded for money".
- Item 3 (unanswered pr-contract): fixed. pr-contract is green at this head (117721379068, 117721492074). Its body check prints `record red-history 35 commit(s) ... fast (3.14), mutation, nightly-ha (stable)`, and the body answers all three.

## Measured at this head

- Step 2, the finder's harness. No committed harness existed for the finding (the owner's screenshot), and the body discloses `r10_sav_baseline.py` as the fixer's own. I ran it at the head and at the merge base, with the harness copied into the base tree:
  RESULT head transient 2.06 kW x4, spread 0.00 SOUND; base 0.00/6.00/6.00/0.00, spread 6.00 DEFECT
  RESULT head cost row actual 15.0 = receipt 15.0 SOUND; base 3.0 vs 15.0 DEFECT
  RESULT head coverage scale 28.00 SOUND; base 2.80 DEFECT
  RESULT head null 10.83 % (thermostat 128.4 kWh, plan 114.5 kWh, room 18.79 vs target 20.44 C) DEFECT; base 43.66 % (203.6 / 114.7) DEFECT
  These are the body's figures exactly. The null stays DEFECT by design, and the body says so.
- Step 3, `r10_sav_null_terms.py`, both arms, at the head:
  RESULT varying: gap 13.9 = comfort 6.6 + (plan vs steady at delivered room) 7.2; timing +17.27 %; stored -23.7 kWh_th (-13.3 kWh_e); balance 240.0 = 240.0 kWh_th
  RESULT const (outdoor -12.0 / -12.0 C): gap 15.6; comfort 5.1; drawdown 18.6 kWh_th = 10.1 kWh_e; timing +0.00 %; balance 200.9 = 200.9 kWh_th
  These match the body. The probe does not run at the base: it imports `_floor_demand_at_target`, which this diff creates. It is a head-only decomposition, not a both-ends check.
  - The const arm's +0.00 % timing holds by construction, because `compute_cop` reads only the outdoor temperature. It is a valid control for the timing term, not evidence about the other two.
  - The const arm closes to 0.4 kWh: 5.1 + 10.1 = 15.2 against a gap of 15.6.
  - Instrument nit, not blocking: the printed "power_weighted_cop" absolutes are Σp·cop / Σp·DT, so they are 1/DT = 4x too large (8.383 / 4 = 2.096). The ratio the body and the carries quote is unaffected.
- Step 1, the mutation proof: production code is unchanged since round 1 (`git diff b7a34f98a HEAD -- custom_components/` is empty). Round 1's run of M0 to M16 at b7a34f98a (all killed) therefore covers this head. The head's `mutation` red (117721384169) is `MUTATION TABLE REFUSED -- 4321 unpinned ... 20 of them added by this diff`. Those are the 20 sites `## Unpinned sites` lists, counting 5326 CLAMP_DROP*2 twice. `mutation-pins (1)` and `(2)` were still running at writing. A pin commit they push carries this verdict under orchestrator.md section 11.
- Step 6, other configurations (my own probe, `evidence-r2/transient_configs.py`, not the finder's): the transient arm across single- and two-zone houses, with and without DHW, in winter_cold (flat and winter_narrow prices) and shoulder (flat):
  RESULT head 12/12 SOUND, spread 0.00 everywhere (booked step 0.37 to 3.04 kW)
  RESULT base 12/12 DEFECT, spread 5.98 to 6.00 kW
  - Class: the body lists the seams but names no mechanical rule. My own enumeration greps custom_components for `savings_actual|savings_sek|baseline_sek|actual_sek|_compute_baseline_power(|baseline_power_schedule|predicted_savings =|billed_total(` (`evidence-r2/class-enum-head.txt`, 38 hits). Its only producers are ledger.py and optimizer.py, both in the diff. sensor.py, notifier.py, payload.py and the card only read row fields. One booking path remains: `add_savings_settlement` is reached only through `settle_interval_savings`, which passes spot plus the fee.
- Step 5: pr-contract prints "moves none of VERSION, the manifest version or a notes heading".
- Step 7: the body names 3b6e599df as the head, and it is the live head.
- Step 13: `git merge-tree --write-tree origin/main HEAD` (main 5a41a5669) exits 0 with empty stderr.
- Check-runs at this head (`evidence-r2/checkruns-head-final.txt`): 33 success, 12 skipped, 1 failure (`mutation`, answered), 2 in progress (`mutation-pins (1)` and `(2)`). `closures`, `fast (3.14)`, `coverage` and `Analyze (python)` all concluded success.

## Red checks (step 11)

All three reds across the range are answered in the body.
- `nightly-ha (stable)` 117704407933 at 36723a969: the job log confirms the body's account.
  - `FAILED: 2 of 64 checks: ['hb:positive_control', 'run:exit_status']`.
  - The positive control reads `a 600 ms spin read as 600.2 ms; dump names the spin: True; py-spy rc=0 names it: False`, and the only failing leg is `py-spy did not run: TimeoutExpired ... timed out after 30 seconds`.
  - `run:all_checks_ran` reads 64 of 64. The runner is at fault, not this diff.
- Finding for the orchestrator (not this PR's to fix; RCA owed): the body declines to file because "one timeout is not yet a recurrence". That premise is false. The same failure, with the same py-spy TimeoutExpired line, hit `fix/r10-sensor-payload` fe4d15d76 at 10:19Z (job 117649075688), 4.5 h earlier. That is two occurrences on two PRs in the 25 most recent failed runs of the workflow (`evidence-r2/nightly-scan/summary.txt`). The trigger is answered (a cheaper detector is named), so this does not block. But the measured frequency now meets the recurrence trigger, and the root cause should be dispatched: the py-spy leg's timeout fails the positive control instead of being reported as that leg's skip.
- Minor: pr-contract 117704370126 (36723a969) is the same `Closes #2255` REFUSE. The body answers it by name but does not list its run id.

## Not verified by me

- The golden drift with claims (50 fixtures, 19 suspended may-drift entries), the structure rows and the archscore figure. These are cited from CI and not re-run.
- The `summer_dhw_only` and golden-matrix savings percentages. These are carried, not re-derived.
- `mutation-pins (1)` and `(2)` had not concluded.

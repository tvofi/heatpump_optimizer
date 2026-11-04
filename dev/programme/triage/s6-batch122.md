# Proposal triage, session s12, batch 122 (P387)

The rolling batch after batch 121. Facts were read at the root-cause seat's head `d8eeae8f8`
(`handoff/r10-rca-sav-estimate`), at the fix seat's local work-in-progress commit `4fff42664` of
R10-HOTFIX-SAV-ESTIMATE and its run files, and in the owner's diagnostics export (derived ratios only).
The fix has no handoff ref yet, so its figures are provisional and the group below re-measures them.

## P387: a meter band on the published savings row, under the no-wood reference

Verdict: ACCEPT narrowed. A two-sided band no longer separates defect from wood. Its ceiling is rejected, and
its floor is accepted as the meter-reading part of the barrier class N-unmetered-reference owes. Destination: a
new group, R10-SAV-METER-FLOOR, after R10-HOTFIX-SAV-ESTIMATE, plus one carry on R10-RCA-SAV-ESTIMATE. A
finding from this ruling also goes to R10-HOTFIX-SAV-ESTIMATE as a carry before that group merges. The class mint is
not a proposal and keeps its route.

Source: the root-cause seat's queue line of 2026-11-04T20:55:16Z, on part 2 of `dev/audit/rca/R10-RCA-SAV-ESTIMATE.md`
at `d8eeae8f8` (`METER_BAND` 0.5 to 2.0 on booked thermostat kWh over metered kWh). The later owner ruling, as carried on
R10-HOTFIX-SAV-ESTIMATE: the reference assumes no wood at all and actuals stay metered, so wood and fire timing count in
the saving.

Instances:
- **Why the two sides differ.** R is booked over metered. With a wood share w of the heat and a true saving s, R is
  about 1 / ((1 - w)(1 - s)). Wood only shrinks the denominator, and at `4fff42664` the reference holds no wood term
  (`_compute_baseline_power`, and `dhw_planner.py` drops the refill coil). So wood can raise R without limit and cannot
  lower it. R above 2 means a stated saving above 50 %, and R below 0.5 means below -100 %.
- **Sound arms, from `r10_sav_wood_reference.py` run files at `4fff42664`, R as booked over plan kWh.** The plant
  equals the model there, so metered equals plan and calibration is 1.0. The wood arms ran `--quick`.

  | arm | R | ceiling 2.0 | floor 0.5 |
  |---|---|---|---|
  | `valve-vary` | 1.03 | no | no |
  | `valve-flat` (flat-price null) | 1.04 | no | no |
  | `wood-cold` | 1.08 | no | no |
  | `wood-stale` | 1.13 | no | no |
  | `wood-coast` | 1.70 | no | no |
  | `wood-fire` | 1.78 | no | no |
  | `wood-full` | 7.70 | **false fire** | no |

  `valve-flat` read DEFECT on the harness's own residual rule in that run (+5.87 % against 3.0), which is the fix seat's
  open item; its R is far from the floor either way. `valve-vary` read SOUND.
- **The rule on each class instance.** Ratios for 2026-09 to 2026-11 come from the owner's export, exported
  2026-11-04T20:07Z, whose config has `wood_furnace_enabled` true.

  | instance | R | ceiling | floor |
  |---|---|---|---|
  | #2255 item 1, 2026-09 | 3.295 | fires, but sits between `wood-fire` 1.78 and `wood-full` 7.70 on a wood install, so it cannot be told from wood | no |
  | the wood branch at step 0, 2026-10 | 0.719 | no | no |
  | `valve_charge_demand` at step 0, 2026-11 | 0.188 (the RCA's table prints 0.18) | no | **fires** |
  | #2463, #2492 meter basis, #2887 reference | not checked in the RCA, not measured here | unknown | unknown |

  The floor catches 1 of the 3 measured instances, and the ceiling's only firing is the one wood now explains. A pre-fix
  no-wood arm at R 0.63 (`base-nowood`) is also above the floor, so the floor is coarse.
- **A ceiling gated to installs with no wood: no measured instance.** The only row above 2.0 is on a wood install, and
  #2411's pre-fix null reads 1.78 per the RCA. Unmeasured, so not taken.
- **What the floor adds to the hotfix.** The hotfix removes the percent clip, so a collapsed reference already prints a
  figure far below -100 % on the card. The floor adds withholding that figure, the stated reason, and keeping it out of the monthly
  receipt (`notifier.py`). Taken alone that is a thin margin: the RCA's 6.8 h per release times 1 of 6 instances bounds it at
  about 1.1 h per release. It is accepted because the class owes a barrier (`defect-root-cause.md`), the census covers
  enumerated installs only and the RCA says so, and this is the only meter reading that survives the owner's ruling.
- **What remains uncovered.** An inflated reference on a wood house now has no meter oracle: R10-SAV-WOOD-MEASURED was withdrawn by the
  same ruling, and metered actuals cannot separate it from wood. This is a consequence of the owner's ruling and is stated, not solved.
- **Finding for the hotfix: calibration cancels the meter on the published row.** `savings_months` multiplies the
  reference by metered over plan, so the published baseline over actual is booked over plan and the metered kWh cancels. Driven through
  `MonthlyLedger` at `4fff42664`, reference 2 kW, plan 1 kW, one day: metered equal to plan gives 50.0 %, calibration 1.0;
  metered half the plan gives 50.0 %, calibration 0.5. So heat the plan did not foresee, which is what an unforecast fire is, earns
  no saving, while the owner's ruling says it counts. The wood arms cannot see this because their plant equals the model. How large
  it is on a real wood house is not measured: the export reads metered over plan 0.68 in 2026-11, on the defective month. The same
  cancellation means a band on the published row reads no meter, so the floor must read the booked lines.
- **The class mint.** `fold_ledger.py check` on a whole-tree export of `d8eeae8f8`: 48 classes, 0 violations. `fold_ledger.py sync`
  there: already carried, so the `audit-find.js` hunk is the generated block and the schema line is the enum `fold` requires. #2625 and
  #2696 touched the same two files the same way.

Cost:
- **The band as filed: not "about zero".** The RCA counts the CI lane only. The floor is one S group, one fixer and one reviewer, with
  one more field through the seam the hotfix's basis marker opens. That marker measures `ledger.py` +44 -8, `payload.py` +3 -1 and the card +14 -2
  at `4fff42664`, for the whole hotfix; the floor is estimated at under a third of that, plus tests in `tests/features.py`, `tests/card.mjs` and two card
  strings (English, Swedish). No standing CPU: one division per published row. No new CI lane, file or check.
- **The ceiling's binding cost:** it withholds a true row. `wood-full`'s 87 % is what the owner ruled the row should say, with its disclaimer.
- **Capped files.** None of these is a policy file, so none has a `policy_lint.mjs --budgets` row. `tests/structure_budgets.json` applies to
  the group's production diff, and `tests/structure.py` is its check. `ledger.py` is the hotfix's hot file, hence `after`.

Binding:
- **Do not build a ceiling**, wood-gated or otherwise, without a measured instance above it on an install with no wood.
- **New group R10-SAV-METER-FLOOR**, kind fix, size S, `after: [R10-HOTFIX-SAV-ESTIMATE]`, files `ledger.py`, `payload.py`, `notifier.py`, the card. Brief: A
  month row states no saving when its booked `savings_baseline` kWh over its `savings_actual` kWh is below a floor constant in `ledger.py`,
  starting at 0.5, on rows of the current reference basis with at least `MIN_CALIBRATION_KWH` metered. Read the booked lines, never the calibrated column:
  calibration cancels the meter on the published row. The two columns stay, the percent and saving read none like `old_basis`, the row carries a
  stated reason on the card in both languages, and the monthly receipt says so too. Wood cannot trip it, because the reference holds no wood term. Acceptance, re-measured at the
  merge base: the wood arms and the valve arms of the hotfix's `r10_sav_wood_reference.py` all publish; the flat-price null publishes; a mutant that zeroes the booked
  reference in the closed loop withholds the row, and dropping the check publishes it; a resistive-heavy month (immersion in the metered lines) is measured and its result stated, since
  the floor's false-fire margin on it is unmeasured; a month under the kWh guard publishes. Name the floor's limit in the docs' savings section: a low-side check, not a validation of the figure. triage: dev/programme/triage/s6-batch122.md#P387
- **Carry on R10-RCA-SAV-ESTIMATE:** Triage rewrites part 2 of the countermeasure under the owner's no-wood ruling: the meter band's ceiling is rejected and its floor goes to R10-SAV-METER-FLOOR. Before the pull request opens, change part 2 and the harness's `METER_BAND` and `ledger` arm to a floor; correct "about zero" to the group's cost; correct the 2026-11 ratio to what the arm prints; in `bugclasses.json`, change `parts_missing` from "the meter band" to "the meter floor", add "an inflated reference on a wood house has no meter oracle (owner ruling)", and update `countermeasure`. Keep the class mint: it is generated by `fold_ledger.py`, and `audit-find.js` is code-owned, so the pull request takes the code-owner route. Do not claim the class fully barriered while that high side is open. The census reads no meter, so this ruling does not change it. triage: dev/programme/triage/s6-batch122.md#P387
- **Carry on R10-HOTFIX-SAV-ESTIMATE, before it merges:** `savings_months` scales the no-wood reference by metered over plan, so the published percent is booked over plan and metered kWh cancels: at the work-in-progress commit `4fff42664`, metered at half the plan reads the same 50.0 % as metered equal to the plan, so heat the plan did not foresee earns no saving, against the owner's ruling that wood counts. The wood arms cannot see it, because their plant equals the model. Add an arm with metered below plan on a wood house, state the result, and decide in the body whether calibration stays on wood houses; if the two owner rulings (2026-10-24 calibration, 2026-11-04 no wood) cannot both hold there, ask the owner through the orchestrator. triage: dev/programme/triage/s6-batch122.md#P387

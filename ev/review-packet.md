# Review packet #3212
head: 33a345901352189f67afe91df1db27970b25aa46
base: c679f4b692f483959769ec5b5147aa4d624c45f4

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=127676955437 success
arch-score / arch-score id=127688754122 success
arm id=127676500042 skipped
budget-raise-gate / budget-raise-gate id=127688754233 success
cancel-superseded id=127687120845 success
codeql id=127688755901 skipped
codeql / Analyze (actions) id=127676643576 success
codeql / Analyze (javascript-typescript) id=127676643546 success
codeql / Analyze (python) id=127676643603 success
gate id=127689370015 success
governance id=127688755738 skipped
governance / delivery-status id=127676643689 success
governance / delivery-status-publish id=127676645212 skipped
governance / env-matrix id=127676643669 success
governance / instrument-self-tests id=127676643584 success
governance / policy-docs id=127676643642 success
governance / record id=127676645006 skipped
governance / wave-script id=127676643680 success
hassfest id=127688755795 skipped
hassfest / hassfest id=127676643550 success
kernel-points id=127688755920 skipped
pr-contract / pr-contract id=127689158112 success
prelude id=127687121208 success
refresh id=127687121162 success
tests id=127688755347 skipped
tests / arch-instrument id=127677624697 success
tests / briefs id=127676643640 success
tests / browser id=127677624683 success
tests / ci-ratchet id=127679798082 skipped
tests / claims-autofix id=127679171999 skipped
tests / closure-scope id=127676643784 success
tests / closures id=127677624851 success
tests / closures-autofix id=127679798785 skipped
tests / coverage id=127677624778 success
tests / coverage-ratchet id=127678484819 success
tests / fast (3.14) id=127677624723 success
tests / graders-head-copy id=127678484906 success
tests / lane-proofs id=127679206162 success
tests / mutation id=127676643624 success
tests / mutation-autofix id=127677424708 skipped
tests / mutation-pins id=127677425061 skipped
tests / nightly-ha id=127677626866 skipped
tests / nightly-status id=127676643712 failure
tests / replay id=127677626583 skipped
tests / typing id=127677624757 success
validate id=127688755946 skipped
validate / validate-hacs id=127676643565 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick <arm>
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  unverified git archive
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git show 750a6001a:custom_components/heatpump_optimizer/ledger.py | sed -n 458,466p
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n '"group": "R10-SAV-METER-FLOOR"' origin/handoff/audit-r10-roster
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head

FIGURES: 2 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3212.md b/dev/programme/delivery/3212.md
new file mode 100644
index 000000000..26a5dc5db
--- /dev/null
+++ b/dev/programme/delivery/3212.md
@@ -0,0 +1 @@
+- [#3212](https://github.com/tvofi/heatpump_optimizer/pull/3212) — **open**, triage: batch 122, P387 ACCEPT (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch122.md b/dev/programme/triage/s6-batch122.md
new file mode 100644
index 000000000..762260c83
--- /dev/null
+++ b/dev/programme/triage/s6-batch122.md
@@ -0,0 +1,98 @@
+# Proposal triage, session s12, batch 122 (P387)
+
+The rolling batch after batch 121. Every figure below is cited to a pushed ref: `d8eeae8f8`
+(`handoff/r10-rca-sav-estimate`, the root-cause seat's head) or `750a6001a` (origin/main, which carries
+the merged R10-HOTFIX-SAV-ESTIMATE, #3220). An earlier text of this ruling read four commits that exist on no ref of origin
+(`git cat-file -t` says "Not a valid object name"); that text, its arm table and its derived
+figures are withdrawn and the figures are re-taken or struck below. The ACCEPT stands on the class-barrier duty
+(`defect-root-cause.md`) and the owner's rulings it cites, not on a carried figure.
+
+## P387: a meter band on the published savings row, under the no-wood reference
+
+Verdict: ACCEPT narrowed. A two-sided band no longer separates defect from wood. Its ceiling is rejected, and
+its floor is accepted as the meter-reading part of the barrier class N-unmetered-reference owes. Destination: a
+new group, R10-SAV-METER-FLOOR, after R10-HOTFIX-SAV-ESTIMATE, plus one carry on R10-RCA-SAV-ESTIMATE. A
+carry also goes to R10-HOTFIX-SAV-ESTIMATE (restated below against main). The class mint is
+not a proposal and keeps its route.
+
+Source: the root-cause seat's queue line of 2026-11-04T20:55:16Z, on part 2 of `dev/audit/rca/R10-RCA-SAV-ESTIMATE.md`
+at `d8eeae8f8` (`METER_BAND` 0.5 to 2.0 on booked thermostat kWh over metered kWh; the part is at its line 270). The later owner ruling, as carried on
+R10-HOTFIX-SAV-ESTIMATE: the reference assumes no wood at all and actuals stay metered, so wood and fire timing count in
+the saving.
+
+Instances:
+- **Why the two sides differ.** R is booked reference over metered. With a wood share w of the heat and a true saving s, R is
+  about 1 / ((1 - w)(1 - s)). Wood only shrinks the denominator, and the reference holds no wood term, so wood can raise R without limit and cannot
+  lower it. R above 2 means a stated saving above 50 %, and R below 0.5 means below -100 %. This is arithmetic, not a measurement.
+- **Arm table, re-taken at origin/main `750a6001a`.** Command, from a `git archive 750a6001a` export:
+  `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick <arm>`
+  (all eight arms, one day, `--quick`). The harness prints the booked reference (72.28 kWh, every arm) and the plan kWh; R below is booked
+  reference over plan kWh, which equals booked over metered because the plant equals the model in these arms (`wood-unforeseen` meters
+  half the plan from 17:00, so its metered kWh is lower than the plan and its R on the meter is higher than printed here).
+
+  | arm | plan kWh (printed) | R = 72.28 / plan | ceiling 2.0 | floor 0.5 | harness row % |
+  |---|---|---|---|---|---|
+  | `valve-vary` | 67.47 | 1.07 | no | no | 29.84 |
+  | `valve-flat` (flat-price null) | 66.51 | 1.09 | no | no | 0.47 |
+  | `wood-cold` | 66.89 | 1.08 | no | no | 0.34 |
+  | `wood-stale` | 63.35 | 1.14 | no | no | 6.84 |
+  | `wood-coast` | 41.76 | 1.73 | no | no | 38.48 |
+  | `wood-unforeseen` | 40.63 | 1.78 (on plan) | no | no | 45.71 |
+  | `wood-fire` | 40.70 | 1.78 | no | no | 42.32 |
+  | `wood-full` | 8.76 | 8.25 | **false fire** | no | 89.04 |
+
+  The harness reads `valve-vary` and `valve-flat` SOUND (its flat rule: absolute percent under 10). Null control: the flat-price arm, whose
+  row is 0.47 %, is the arm where a saving has no source but volume, and it is neither above 2 nor below 0.5. No arm is below the floor, and
+  only `wood-full` is above the ceiling. These ratios replace the earlier table, whose values were read at commits that no ref carries.
+- **The rule on each class instance.** From the RCA at `d8eeae8f8` (its table at line 38 and line 162, and part 2 at line 273): 2026-09 reads R about 3.30,
+  and 2026-11 (`valve_charge_demand` at step 0) reads 0.18. The ceiling fires on 2026-09, whose install has wood, so on a wood install it cannot be told from `wood-full`'s
+  8.25 or `wood-fire`'s 1.78 by the meter; the floor fires on 2026-11. The earlier text's 2026-10 ratio and its counts of instances caught ("1 of 3", "1 of 6") are
+  struck: their source was the owner's export and runs that are not on any ref, and no command here re-derives them. #2463, #2492 meter basis and #2887 reference are not
+  checked in the RCA and not measured here.
+- **A ceiling gated to installs with no wood: no measured instance.** The only measured row above 2.0 is on a wood install (the RCA's 2026-09 and the harness's `wood-full`).
+  Unmeasured, so not taken.
+- **What the floor adds to the hotfix.** The hotfix removes the percent clip, so a collapsed reference already prints a
+  figure far below -100 % on the card. The floor adds withholding that figure, the stated reason, and keeping it out of the monthly
+  receipt (`notifier.py`). Its benefit is not quantified here: the earlier "about 1.1 h per release" and "1 of 3 instances" are struck, because the first multiplies an RCA
+  cost (6.8 h per release, RCA line 217) by an instance fraction that has no command behind it. The ACCEPT does not rest on a margin. It rests on
+  the class owing a barrier (`defect-root-cause.md`), the census covering enumerated installs only (the RCA says so), and this being the only meter reading that survives
+  the owner's ruling.
+- **What remains uncovered.** An inflated reference on a wood house now has no meter oracle: R10-SAV-WOOD-MEASURED was withdrawn by the
+  same ruling, and metered actuals cannot separate it from wood. This is a consequence of the owner's ruling and is stated, not solved.
+- **Finding for the hotfix, restated against main: the wood floor on calibration.** The original finding: `savings_months` multiplies the
+  reference by metered over plan, so the published baseline over actual is booked over plan and the metered kWh cancels; heat the plan did not foresee (an unforecast fire)
+  would then earn no saving, against the owner's ruling that wood counts. Read at origin/main:
+  `git show 750a6001a:custom_components/heatpump_optimizer/ledger.py | sed -n 458,466p` shows, at lines 461 to 465,
+  `if wood_configured and calibration is not None:` ... `calibration = max(1.0, calibration)`, with the comment "scaling down by it would cancel wood's heat from the saving";
+  the coordinator passes `wood_configured=wood_furnace_on(...)` at `coordinator.py:7903`. **Answered by the floor:** on a wood-configured install the calibration can only raise the reference, so a meter
+  under the plan no longer scales the saving down. **Pinned** by `tests/features.py` (a helper at its line 42826 drives `savings_months(..., wood_configured=wood)`) and by the mutation ledger's two killed
+  mutants of that line (`tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.BOOLOP.c9f8a17d.json` and `...GUARD_OFF.c9f8a17d.json`).
+  **Not re-taken, so struck:** the earlier drive numbers (50.0 % at both meters; 50, 75, 87.5 %) came from a commit on no ref. The pre-fix cancellation cannot be re-taken at main, because the floor is in the code; the no-wood
+  path keeps the cancellation by specification, so the floor must still read the booked lines. **What remains open:** the harness arm `wood-unforeseen` meters under the plan on a wood house, but its plant equals
+  its model apart from the 17:00 hour and it prints calibration 1.0 (post-floor) beside an "uncalibrated" row (49.10 %) that cannot tell the floor from no calibration, so it does not
+  show how much a real unforeseen fire earns on a real wood house. That size is not measured and cannot be driven from the data on any ref; no number is claimed.
+- **The class mint.** `fold_ledger.py check` on a whole-tree export of `d8eeae8f8`: 48 classes, 0 violations. `fold_ledger.py sync`
+  there: already carried, so the `audit-find.js` hunk is the generated block and the schema line is the enum `fold` requires. #2625 and
+  #2696 touched the same two files the same way. (Not re-run here; the claim is the root-cause seat's at that ref.)
+
+Cost:
+- **The band as filed: not "about zero".** The RCA counts the CI lane only. The floor is one S group, one fixer and one reviewer, with
+  one more field through the seam the hotfix's basis marker opens, plus tests in `tests/features.py`, `tests/card.mjs` and two card
+  strings (English, Swedish). The earlier line counts for that marker (+44 -8, +3 -1, +14 -2) were read at a commit on no ref and are struck; the
+  group's real diff is measured by `tests/structure.py` at its own pull request. No standing CPU: one division per published row. No new CI lane, file or check.
+- **The ceiling's binding cost:** it withholds a true row. `wood-full`'s row (89.04 % in the table above) is what the owner ruled the row should say, with its disclaimer.
+- **Capped files.** None of these is a policy file, so none has a `policy_lint.mjs --budgets` row. `tests/structure_budgets.json` applies to
+  the group's production diff, and `tests/structure.py` is its check. `ledger.py` is the hotfix's hot file, hence `after`.
+
+Binding:
+- **Do not build a ceiling**, wood-gated or otherwise, without a measured instance above it on an install with no wood.
+- **New group R10-SAV-METER-FLOOR** (queued by the dispatch seat: `git grep -n '"group": "R10-SAV-METER-FLOOR"' origin/handoff/audit-r10-roster` reads `wave-r10-groups.json:17024` at `7cfdd9cc1`), kind fix, size S, `after: [R10-HOTFIX-SAV-ESTIMATE]`, files `ledger.py`, `payload.py`, `notifier.py`, the card. Brief: A
+  month row states no saving when its booked `savings_baseline` kWh over its `savings_actual` kWh is below a floor constant in `ledger.py`,
+  starting at 0.5, on rows of the current reference basis with at least `MIN_CALIBRATION_KWH` metered. Read the booked lines, never the calibrated column:
+  calibration cancels the meter on the published row. The two columns stay, the percent and saving read none like `old_basis`, the row carries a
+  stated reason on the card in both languages, and the monthly receipt says so too. Wood cannot trip it, because the reference holds no wood term. Acceptance, re-measured at the
+  merge base: the wood arms and the valve arms of the wood-reference harness the hotfix lands under `dev/audit/harnesses/` all publish; the flat-price null publishes; a mutant that zeroes the booked
+  reference in the closed loop withholds the row, and dropping the check publishes it; a resistive-heavy month (immersion in the metered lines) is measured and its result stated, since
+  the floor's false-fire margin on it is unmeasured; a month under the kWh guard publishes. Name the floor's limit in the docs' savings section: a low-side check, not a validation of the figure. triage: dev/programme/triage/s6-batch122.md#P387
+- **Carry on R10-RCA-SAV-ESTIMATE:** Triage rewrites part 2 of the countermeasure under the owner's no-wood ruling: the meter band's ceiling is rejected and its floor goes to R10-SAV-METER-FLOOR. Before the pull request opens, change part 2 and the harness's `METER_BAND` and `ledger` arm to a floor; correct "about zero" to the group's cost; correct the 2026-11 ratio to what the arm prints; in `bugclasses.json`, change `parts_missing` from "the meter band" to "the meter floor", add "an inflated reference on a wood house has no meter oracle (owner ruling)", and update `countermeasure`. Keep the class mint: it is generated by `fold_ledger.py`, and `audit-find.js` is code-owned, so the pull request takes the code-owner route. Do not claim the class fully barriered while that high side is open. The census reads no meter, so this ruling does not change it. triage: dev/programme/triage/s6-batch122.md#P387
+- **Carry on R10-HOTFIX-SAV-ESTIMATE:** the wood floor is on main (`ledger.py` lines 461 to 465 at `750a6001a`: `calibration = max(1.0, calibration)` when wood is configured), and it answers the finding that calibration cancels wood's unforeseen heat from the saving. What is open: no measured size of that heat on a real wood house (the `wood-unforeseen` arm's plant equals its model), so the body of the next savings pull request states it unmeasured rather than as a number. Whether the two owner rulings (2026-10-24 calibration, 2026-11-04 no wood) hold together on wood houses is answered by the floor as built: calibration may only raise the reference there. triage: dev/programme/triage/s6-batch122.md#P387

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.

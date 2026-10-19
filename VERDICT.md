Fix review: merge 67b8659dac9a550ab3edae856568b56f8cfcbd58

Round 1 (no earlier `Fix review:` on #2463). Measured head 67b8659dac9a550ab3edae856568b56f8cfcbd58 (code head 2d1758154), merge base = origin/main 4a3cbcf62e6f5e7b6594d376d714388caf2915cf. Role contracts current: `git diff <mb>...origin/main -- dev/governance/roles/` is empty.

**Head moved after measurement**, to a3f7c328d826430776c61b036551a21c3c08bfe2. That commit is `github-actions[bot]` `ci: pin killed mutants` and adds only three `tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger._coverage_factor.{BOOLOP,CMP_BOUND,GUARD_OFF}.0966076a.json` files, which the body's `## Unpinned sites` predicted (`ev/head-move.diff`). There was no reviewer turn and none of those paths is in the branch's own diff, so it is carry-shaped under orchestrator.md section 11. Running `app_approve.sh --carry` is for the orchestrator. None of my numbers depends on those files.

## RESULT lines

- RESULT mutation-proof: these are my own mutants of ledger.py:328, each run through `tests/features.py` in an archive export (`ev/features.*.log`). Every export also fails one check that is not this PR's: "and the path that proceeds still stamps a resolvable recorded_at (#363)" (`recorded_at = 'unknown'`). It needs a 40-char git SHA and an archive has no `.git`, so the unmutated head `orig` reads 1 of 4232 FAILED for that check alone. Net of that check:
  - delete predicate (`if settled > 0:`): +1 FAIL, "a month booked before its coverage began scales by the calendar-day ratio", savings_sek -726096.0. This matches the body.
  - BOOLOP (`or`): killed, ZeroDivisionError.
  - CMP_BOUND `settled >= 0`: killed, ZeroDivisionError.
  - CMP_BOUND `folds > spot_folds`: +4 FAIL ("the open month scales by the month's hours…", "the capacity line…", "a month that settled more hours…", "a negative month covered from its first settlement…").
  - GUARD_OFF `if False:`: +4 FAIL, the same four.
  - GUARD_ON `if True:`: killed, ZeroDivisionError.
  - Not a table operator, my probe: `folds == spot_folds` survives (+0). See note 2.
- RESULT harness (`dev/audit/harnesses/r10_savings_upgrade_month.py`): this is the fixer's harness, disclosed as synthetic. The finding came from the owner's private report and there is no finder-committed harness (step 9). I ran it as committed at both ends (`ev/harness.{base,head}.txt`):
  - base: upgrade factor=6720.000 savings_sek=-363048.00, null 28.000 / -168.00, fresh 2.800 / -151.20.
  - head: upgrade 2.800 / -151.27, null 28.000 / -168.00, fresh 2.800 / -151.20.
  - Every figure in the body's `## Null control` reproduces.
- RESULT null control (flat price, spot = 1.0 everywhere): the null arm is identical at both ends (factor 28.000, -168.00, -33.33 %). The features.py null check "a negative month covered from its first settlement keeps the hours' scale" passes on the delete mutant and fails on CMP_BOUND(`>`) and GUARD_OFF, so it reads behaviour.
- RESULT store histories: my own sweep through the production ledger, `ev/sweep.py`, built by me as a reviewer instrument. It prints the open-month factor at both ends (`ev/sweep.{base,head}.txt`):
  - Unchanged at both ends: full coverage from the 1st (2.909), fresh v7.0.1 install mid-month (24.889, which is #2411's intended hours scale), upgrade at the month's first settlement (2.909), every third day missing (4.226), 30 % unpriced intervals (2.909, folds > spot_folds), DST March full (1.016) and DST October full (1.216).
  - Fixed: Feb upgrade 672.0 → 2.800, March upgrade on the 30th 20.667 → 1.000, October upgrade on the 19th 4.709 → 1.192. Each is the calendar ratio, i.e. the v7.0.0 behaviour for that month.
  - The predicate counts folds, not hours, so DST cannot move it (`month_hours` ignores the DST hour by design).
  - The normal case is not under- or over-stated.
- RESULT predicate soundness: the coverage fold (`dt > 0`) and the spot fold (finite spot only) share one call, `observe_spot_and_settle_savings`. Its only caller is `coordinator._accumulate_energy`, reached only under `0.05 <= elapsed <= 2.0` (coordinator.py, the settle block). So a v7.0.1+ month always has folds >= spot_folds.
  - v7.0.0 (tag) folded `spot_price` on every settlement under the same 0.05–2.0 gate and never folded `settled_hours`. So any v7.0.0-booked priced interval makes spot_folds > folds, and the month falls back to `pro_rata_factor`.
  - No other writer of either meta exists. `from_dict` keeps counts as stored.
- RESULT pins: `mutation` at 67b8659 is red, `MUTATION TABLE REFUSED`, with `4 of them added by this diff`: ledger.py:328 BOOLOP, CMP_BOUND*2, GUARD_OFF (`ev/mutation-job.log`). That matches `## Unpinned sites`.
  - `mutation-pins (1)` concluded success: `PIN KILLED: 4 pinned, 0 left unpinned`, each killed by tests/features.py. The bot pushed them as a3f7c328d.
  - The two deleted pins (`*.3ffba7d3`) were on the old `if settled > 0:` text. The table did not refuse on stale pins after their removal, which is earned by the line change.
- RESULT CI at 67b8659 (check-runs API, every run, `ev/check-runs-67b8659.tsv`): 34 success, 13 skipped, 1 failure, all concluded. The one failure is `mutation`, which the body's `## Red checks` names and answers. A second `pr-contract` run started at 23:07:56Z for the moved head; the 22:12:40Z and 22:13:15Z runs are success.
  - fast, coverage, browser, closures, typing, scope, arch-score, budget-raise-gate: success.
- RESULT merge: `git merge-tree --write-tree origin/main 67b8659…` exits 0, tree a86e40288de2cda4da6fc496a862f69a5047d557, no conflict (`ev/merge-tree.txt`).
- RESULT untouched: VERSION, manifest, RELEASE_NOTES.md and tests/golden have no change in the three-dot diff. No claim-file change, so there is nothing for env_drift to compare.
- RESULT archscore: `Architecture score: dS +0.0000 NULL` (`ev/archscore.txt`). `closure.py no-copies` is clean.
- RESULT class (step 6): the body's rule is `grep -n "_coverage_factor\|pro_rata_factor\|SETTLED_HOURS_META" custom_components/heatpump_optimizer/*.py`. Run at head, it returns only ledger.py: the constant, its one writer, its one reader and its one caller `savings_months`. All are in the diff or dispositioned. No open seam.
- RESULT forward-carry: `none`, and no finding here changes a later stage.
- RESULT body figures:
  - "ALL 4232 FEATURE CHECKS PASSED" is consistent: my export fails only the git-SHA check, which a real checkout passes, and CI `fast` is green.
  - I did not re-run `MODE: SCOPED -- 22 script(s) run`, structure, guard_pins or finite_boundary locally. CI's heavy runs are cited instead (step 11).

## Notes, not blocking

1. **The predicate leans on the caller's interval bound, not on a ledger invariant.** The ledger API accepts dt <= 0 (features.py's "an interval of no length settles no hours" feeds 0.0 and -1.0): it folds spot but not hours. One such call would silently put that month on pro_rata. Production cannot reach this today because of the 0.05–2.0 gate. The fallback is bounded either way (the v7.0.0 behaviour, not an explosion).
2. **Test gap on the unpriced case.** Nothing pins that a month with unpriced intervals (folds > spot_folds, #2229) keeps the hours scale. The non-table mutant `folds == spot_folds` survives the suite, though the code is right (sweep row "unpriced 30%").
3. **Edges I accept, bounded:**
   - An upgraded month whose post-upgrade unpriced intervals come to outnumber its pre-upgrade priced ones flips back to the hours scale. By then the coverage spans at least about half the elapsed month, so the factor is at most about 2× the calendar ratio, not thousands.
   - A v7.0.0 month with no priced interval at all keeps spot_folds = 0 and still takes the hours scale: the sweep's "legacy all unpriced" row reads 672 at both ends. Only kWh lines can be booked there; savings needs a price.
4. **pro_rata is the right fallback, not a mask.** It is exactly v7.0.0's figure for a month whose lines span the whole elapsed month. The docstring already promised it. It is not surfaced as a distinct attribute, but `estimated: True` stays on the row.

bus-nonce: c275b5643b5e7be8d0edfbd4202d16ee

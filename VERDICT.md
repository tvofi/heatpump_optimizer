Fix review: merge 4e85c6a50e3e234e428fad8402bbcdf623a796cb

bus-nonce: f8de0f74b82a440badcc27f6f52592e7
pending-ci: gate

## Scope

Round 1, full review (no prior verdict). Head 4e85c6a50e3e234e428fad8402bbcdf623a796cb, merge base 54cb7211642364d762ba47f42d5f7b8a5953f742. The three-dot diff touches only `dev/audit/harnesses/r10_advisor_steady_seams.py`, `dev/audit/harnesses/r11_advisor_measures.py` and `dev/programme/delivery/3691.md`: no production line, no budget, closure, claim or golden file. `git diff <mb>...origin/main -- dev/governance/roles/` is empty. `custom_components/` is identical between the body's measurement base c82f014a63 and this merge base 54cb72.

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main 4e85c6a5` exit 0, no conflict (ev/merge-tree.txt).
- RESULT mutation (classifier `zero_kind`, by hand; harness-only diff draws no CI mutant): probe ev/mutants-probe.txt on this head merged with handoff/r11-valve-reference c60b23450f. Unmutated: valve one-tank `night-1 21:00` figure 0.0 `idle`; saturated house (`max_electrical_power` 0.05) `day-1`/`day+1 09:00` figure 0.0 `binds`. M1 moved-step mask dropped: `binds` on the idle row, killed. M2 every step moved: `binds`, killed. M4 `IDLE_KW` 1e9: saturated rows read `idle`, killed by the body's null. M3 live side only: survives (disclosed in the body). M5 first thermostat pass instead of the second, M6 Monday only instead of the week: survive (not disclosed; Findings).
- RESULT fields arm, four trees (ev/fields-*.txt): base 54cb72 `valve, one tank` `at 0 or against the ask 24`; head `missed 24 (pair 0, against 5, binds 19)`, correct zero 0. Base+c60b234 `at 0 or against the ask 1`; head+c60b234 `missed 0`, correct zero 1 = `night-1 21:00`. Single-zone, two-zone, two-zone valve two-tank: 0 at base, `missed 0` with no zeros at head. Largest-move columns byte-identical base vs head.
- RESULT weekday arm base/head: Friday rows 96, against 0, 0.00 0 (idle 0 at head); the two weekday lines identical.
- RESULT valve arm base/head: weekend comfort days against 7, at 0.00 0; Friday rows 96, against 8, at 0.00 4, idle 0 at head; holds 22.10/22.07 at 23.0; non-RESULT per-day rows and holds identical base vs head (`cmp`).
- RESULT carry 0/1 re-derived at the head: `asks` 8/10/0 (+58.0..+102.0)/6/5/8/3, null −11.2..+7.1; `loop` +99.8, +23.9, −0.8, −17.3, +7.9, +3.8, +10.9, null −23.1; `pv` 8 of 8 rows outside the range; `pvloop` −25.2 (−63.2/−8.0), −10.5 (+73.6/+9.3), null −24.9 (−63.2/−26.8), +19.2 (+73.6/+31.0), own-price end closer in all four. All equal the body's figures (ev/r11_*-head.txt).
- RESULT `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `zero_kind` mirrors `HeatPumpOptimizer.reference_day` (optimizer.py:6187): same `_day_mean_weather`/`_step_clock`/`_build_comfort_bounds`/two-pass `_compute_baseline_power`; harness `N` = `int(24/DT)` = reference_day's `day`. Dedup is on the pair of target tuples, a superset of each side's own dedup, so no day is skipped.
- VERSION, manifest and RELEASE_NOTES untouched (not in the diff).
- Forward carry opened: `dev/programme/rosters/wave-r11-groups.json` on handoff/audit-r10-roster at 1303ed51c8 holds the R11-VALVE-REFERENCE item fcac48c8 with its control (the fields before/after pair).
- Class rule: the body's class is the harness counting rule for a 0 figure; the three arms that count 0s (`fields`, `weekday`, `valve`) are all in the diff. No other harness calls `seams.figure` with a 0 count (one-seam per arm set).
- CI: `merge_train.py classify` polled 23:58-00:29 UTC every ~90 s, last line `WAIT 4e85c6a50e3e234e428fad8402bbcdf623a796cb pending: gate red: none` (ev/classify.log); runners queued, no red. Returned with `pending-ci: gate` per the brief. Head re-read at 00:29: still 4e85c6a5.

## Findings

- Follow-up: `zero_kind` survives two mutants no measured row kills: M5 (count the first thermostat pass, not reference_day's second) and M6 (read only the start day, not the week's distinct days); M3 (live side only) is the body's disclosed survivor. Each would misread only a 0 whose idle/binding differs between passes or between weekdays, and no fixture here produces one; the classifier's per-day and second-pass reads are therefore pinned by structure, not by a value. Carry: dismissed: harness-only instrument, no fixture yields a distinguishing row and the classifier is a line-for-line mirror of reference_day; recorded here for any seat editing zero_kind

## Notes

- Note: carry-sha: the Forward-carry names the roster branch but not its SHA (finding-propagation.md asks for it); I opened it at 1303ed51c8. Carry: dismissed: paperwork, carry verified in the tree

Fix review: merge de27770e25e05704a02b61cc7e0acc845e1da0e9

PR #1834, R9-F1.11 (P2 one fact one owner, P6 every read has a producer; D14-s1-02). Round 1.
Reviewed: code dfab4c6e3661f6a6e242ea3995846c0dffb1b3bf, then the live head de27770e (main 8a0ca90a merged into dfab4c6e). de27770e's tree is 99ee5a82, identical to my own git merge-tree of origin/main with dfab4c6e, which I measured. tests/entities.py changed on both sides, so I judged that delta myself by running the merged tree.

RESULT entities.py at dfab4c6e: ALL 2050 ENTITY CHECKS PASSED, rc 0 (venv-ci Python 3.14.7). The body says 2048; the difference is not material.
RESULT entities.py at tree 99ee5a82 (= de27770e): ALL 2051 ENTITY CHECKS PASSED, rc 0
RESULT M1 (set_channel probes boost_calls again): rc 1, 4 failing: P6 G [boost.py:244 boost_calls] and the three boost persist checks. Matches the body.
RESULT M2b (horizon_hours dropped from _plan_settings_view): rc 1, 2 failing: the D14-s1-02 horizon check and P6 K [sensor.py:1531, 1564 horizon_hours]. Matches the body.
RESULT M4 (heat_pump_on fallback back to p > 0.1): rc 1, 2 failing: P2 plan_running_rule SEAM coordinator.py:2004 and the P2 null-control check. Matches the body.
RESULT merge-tree origin/main(8a0ca90a) dfab4c6e: clean, rc 0
RESULT VERSION, manifest and RELEASE_NOTES untouched; claims-for 6.7.13 = VERSION; 5 coord_* claims, each moved by one key, horizon_hours
RESULT structure_budgets: every changed key goes down (coordinator_loc 9014->9006, cut_views 109->104, max_class_loc 9014->9006); no raise. The restructure (_plan_settings_view out of the class) pays for the new key.
RESULT CI mutation on dfab4c6e: "MUTATION TABLE PASSED (empty pool)"; unpinned 3919 against 3920 at ratchet base 8a0ca90a. No new unpinned site, so the deferral to mutation-autofix is moot.
RESULT code-owned paths touched: none (boost.py, coordinator.py, tests/entities.py, tests/features.py, tests/golden/*, structure_budgets.json, bugclasses.json)

Judgement:
- Barriers are correct and sound for the instances they name. The P6 arms take their universes from production and each has a planted defect. The P2 registry refuses SEAM, OWNER-MISSING, DEAD-RULE, STALE-DISPOSITION and CENSUS-MISSING, with a planted sibling per fact.
- Residual reach, not blocking, and stated in bugclasses.json's own barrier text:
  - K counts a key as produced if any dict literal anywhere outside the consumer modules names it.
  - G counts an attribute as defined if any Name, arg or keyword in production uses that name.
  - plan_running_rule matches only the literal 0.1 or MIN_RUNNING_DRAW_KW.
  - A coincidental name, or a different literal threshold, escapes.
- Production change: the fallback is now planned_draw_runs(space, dhw) (space+dhw > MIN_RUNNING_DRAW_KW). It is reached only when a result has no heat_pump_on_schedule. Indexing is guarded for a None or short dhw schedule.
- Closure deferral is legitimate. ci-autofix.md assigns UNDER-SCOPED to closures-autofix and forbids duplicating it. Condition: closures-autofix must report `changed`. A red autofix means no bot commit, and the fixer then re-derives tests/entities.py.
- Carry: no stage that has not started owns the stored-instant rule (the roster groups naming it, F1.6, F1.9, F3.1, F3.2 and F10.1b, are all done). The roster brief allowed "record the measurement". It is recorded in the body and in-tree in the P2 barrier text. No carry is owed.
- Not verified: the body's "about 16" parse sites. I count 19 fromisoformat occurrences in the package, 1 of them in drift.py; I did not re-derive the 16.
- CI on de27770e was still running when I posted (fast, typing, coverage, closures, browser, env-matrix). Merge only on green.

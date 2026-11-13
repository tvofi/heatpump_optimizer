# BLOCKED: r10-closeout-prep-p2 repair round 1

Question: tests/entities.py's #2227 cited-program arm (and its companion "the cited-program arm: ... codeowners_gap" check) needs at least 3 historical programs, one cited by a carry, and codeowners_gap.py among them. Every such citation came from carry-201 entries 0, 1, 3, 4 and 6, which are delivered to roster group R11-INTAKE-R10-RESIDUE (the review re-derived 31 of 31 re-homed entries there). No deleted carry is still live in a way that feeds the arm, so the arm's premise, that a carry cites a historical program, no longer holds. Which repair does the orchestrator rule: (a) extend the arm to read carry text from roster groups' `carry` lists as well as dev/programme/carries/, or (b) re-scope its floors with a recorded reason? Either one edits a gate check, which the brief reserves to the orchestrator.

## Evidence (PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py)

- Merge base 2a083d235e: `ok ... (#2227)`, ALL 2711 ENTITY CHECKS PASSED. Cited: dora_keys.py (D13.md, carry-201), units.py (COMMON.md), corpus_churn.py, dora_cfr.py, codeowners_gap.py (each carry-201 only).
- PR head b560375dbd: `FAIL ... (#2227) [policy files 51, carries 1, cited 2 ...]`, plus `FAIL the cited-program arm ... [units.py faults []; codeowners_gap holds 4 stale literal(s), opens-faults []]` (it requires codeowners_gap.py in _SP_CITED). 2 of 2711 failed.
- Repair head db5861c0ae: carry-201 restored with its live entry 22 only, so carries=2. Both FAILs are unchanged (`cited 2`), because _sp_cited counts only paths under _SP_HIST and entry 22's remeasure cites tools/audit/seat/probe_bridge.py. Restoring entries 0/1/3/4/6 would mean keeping delivered carries only to feed the check, which the brief forbids.

## Done on this ref (tree = db5861c0ae, descends from b560375dbd)

1. carry-1645: both `answered_by` = 16e8fef927d65b5893b947afdcc2a94acaa3cd9d (ancestor of origin/main; adds `_section(...)` / `if m is None` guards and folds the F8.3 arms). Fixes block item 1.
2. carry-201.json restored holding entry 22 whole and unanswered, byte-identical to the merge base. Its second item (window_work_minutes keeps only declared `needs:` edges) is unbuilt and was on no roster group. The carry-201 lines in tests/closures.json and tools/ci/selftest_closures.json are restored. Fixes block item 2. Re-homing it to R11-INTAKE-R10-RESIDUE instead is the alternative if (a) or (b) makes keeping the file pointless.
3. tools/policy/legacy_control_files.json: carry-201.json dropped (LEGACY-LISTED-CLEAN refused it as vacuous). brief_lint.mjs's assertCarryControl takes its legacy example from the set instead of naming carry-201.json. `node tools/policy/brief_lint.mjs`: rc 0, TOTAL 0 error(s) across 41 file(s).

Not run, pending the ruling: carry_audit.py, ci_predict.py, prepr.sh, the body.

Fix review: blocked b9a499e4ba5abf8d537f8e93b75595385caa2976 ci-red: gate red on tests / fast (3.14, 1/4), the PR's own freeze section fails on the merge with main cb2026c3 (tests/features.py 104695 lines over the manifest's 104573)

bus-nonce: 1463c2ddb71881017a665a1276ba1515

## Block

- `merge_train.py classify b9a499e4ba5abf8d537f8e93b75595385caa2976 --pr 3940` printed `RED b9a499e4ba5abf8d537f8e93b75595385caa2976 pending: none red: gate` (rc=1). The red under `gate` is `tests / fast (3.14, 1/4)` (job 140920667426, merge ref 031fad164d over main cb2026c3): `3 of 2800 ENTITY CHECKS FAILED`, all three in this PR's new section "The tests/features.py freeze (R11-OWNER-FEATURES-SPLIT)": the live check (`lines: tests/features.py has 104695 lines, above the 104573 tests/features_frozen_budgets.json records`), `null control (span ids)` and `null control (seam home)`. `tests / fast (3.14)` and `gate` are both in `merge_train.py owed-reds`.
- Cause: #3914 (R11-SEAM-wallclock-dst, merged as cb2026c3) grew `tests/features.py` from 104573 to 104695 lines after the manifest was recorded. It adds no new span. On a local `git archive` of the clean merge tree 8c0eac53, `features_freeze.py --check` printed the same single `lines:` refusal and `FEATURES FREEZE: REFUSED (1 refusal(s))`. The body's own "At the merge" paragraph predicted this. The repair is a `--record` on a head that merges main. That re-record is itself a `lines` raise, which budget-raise-gate reads and which needs approval at the new head.
- `git merge-tree --write-tree origin/main <head>` is clean (rc 0, `LEDGER-MERGE: resolved tests/closures.json`), so this is not a conflict block. It is a test red on this head's merge ref, from a check this PR adds.

## Findings

- The null controls in the new entities section are not isolated from the live tree. `null control (span ids)` gives the loose manifest `lines + 50` room, and `null control (seam home)` uses the live `_FFZ_MAN`, so any drift of the live file past the manifest also reddens them. On main cb2026c3 one `lines` drift turned into three FAIL lines, though the section's comment says each control isolates one condition. Building each control's manifest from `_ffz.measure(_FFZ_SRC)` rather than the recorded manifest would leave the live check as the only one that moves on drift. Carry: R11-OWNER-FEATURES-SPLIT
- Two seam-rule mutants survive, so the step-A rule in `home()` that the body and docstring state is pinned only in part: R1 (`next(p for p in ORDER ...)` changed to `reversed(ORDER)`, the tie-break) and R2 (`MOD2SEAM.get(m, "surface")` changed to `"cycle"`, the unlisted-module default). Each printed `ALL 6 ENTITY CHECKS PASSED`. The body names neither as a pinned mutant (its six target `refusals`). The seam-table-drift carry relies on the `surface` default ("adding a module moves no placed span"), and no check reads that default. Carry: R11-OWNER-FEATURES-SPLIT

## Evidence

- Head reviewed: b9a499e4ba5abf8d537f8e93b75595385caa2976 (`ev/HEAD.txt`). Merge base 265e061f65. origin/main is cb2026c3b5. Review scope: full (the packet says no verdict names 3f7c5c52). This is the first verdict at this head.
- At the head, the freeze span alone printed `ALL 6 ENTITY CHECKS PASSED` (`ev/span_unmutated.txt`), `features_freeze.py --check` printed `HOLDS (0 refusal(s))`, and `budget_raise_gate.py --self-test` printed `305 checks, 0 failed`.
- Figures re-derived at the head (`ev/figures.txt`): `wc -l` is 104573, equal to the manifest's `lines`. Spans: 252, equal to the 252 manifest ids. `seam_pins` is `{}`. The `--seam` counts are actuation 15, cycle 28, dhw 9, inputs 37, model 92, plan 48 and surface 23, which sum to 252. `--check-body` on the live body printed `the body's arch_score figure is the measured one, dS +0.0000 NULL`.
- Mutation proof (`ev/mutants.txt`, driver `ev/mut_driver.py`, each mutant restored, tree clean afterwards): the body's M1–M6 were all KILLED, each by the named null control. Also KILLED: M2b (`>` changed to `>=`), R3 (the import branch of `_names_frozen`), R4 (line count minus 1), M8 (`lines` MAX changed to FROZEN) and M10 (`spans` FROZEN changed to FREE). R1 and R2 SURVIVED (Findings).
- No `VERSION`, manifest-version, `RELEASE_NOTES.md`, golden or claim-file change in the three-dot diff. No `custom_components/` line changed. `dev/governance/roles/` has not moved on main since the merge base.
- CI log excerpt of the three freeze reds: `ev/ci_fast1_freeze_reds.txt`. The classify poll history is in `ev/classify_poll.log`.
- `budget-raise-gate / budget-raise-gate` is red pending a raise approval at the head, as the body says. That red is not the block.

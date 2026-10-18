Fix review: blocked 8d76a9edf1ec3356ba7d8e55601e8e8c17553977 metric-gamed: closures INERT READS: the solver-closure census is a harness (fixer.md 18) placed in tools/audit/seat/ only so harness_headers' inert read cannot see it; ci-autofix.md has the bot merge INERT READS from CI recordings

bus-nonce: 946d78e265621033d164095a4acebbe3

PR #2371, R10-LEAF-IMPORTS (Part of #2247). Review round 1 by this seat. Measured head 8d76a9edf1ec3356ba7d8e55601e8e8c17553977, which was still the PR head when this verdict was written. Merge base 811df3cf3362ea0c626bcfdf8bf4a3cf2937c846. Detached worktrees: head, merge base, and the finder's own trees b202335e2 (arch2-s4) and 532d8d09d (arch3-s6).

## What holds (re-derived, not taken from the body)

- The moves are verbatim. `_utc_step_starts` at the base equals `drift.utc_step_starts` at the head, apart from the name (RESULT clock_body_identical_modulo_name=True). There are 18 REASON_* codes at the base optimizer and 18 in the head payload, with identical values. The head optimizer assigns none of them, and the base payload had none. Script: evidence/verbatim_moves.py. No production module re-exports: the optimizer uses all 18 codes it imports (each name appears at least twice in optimizer.py).
- Runtime census, under the body's rule, rebuilt by me (evidence/census_own.py, my instrument, not the fixer's). Every package module except `__init__` is imported in a fresh interpreter, and I check whether `heatpump_optimizer.optimizer` is then in sys.modules.
  - Base: RESULT modules=76 solver_in=17 scipy_in=18 import_failures=0
  - Head: RESULT modules=76 solver_in=10 scipy_in=11 import_failures=0
  - The seven that leave are early_cutoff, legionella, pump_arbiter, quiet_windows, repairs, setpoint_check and silent_mode. None enters. This reproduces the body's 17 -> 10 at my own merge base.
- Finder's harness, P1 (arch2-s4/layering.py at b202335e2, sha1 314f35a4…). Base: setpoint_check 23 IN, quiet_windows 21 IN, silent_mode 20 IN, store 18 out, private_cross_module_names 16. Head: 14 out, 11 out, 8 out, 18 out, 13. This matches the body.
- Finder's harness, P4 (arch3-s6/runtime_closure.py at 532d8d09d, K=3). The body does not cite it.
  - legionella: pkg_modules 29, solver IN, scipy IN at the base; 22, out, out at the head.
  - setpoint_check, repairs, silent_mode and quiet_windows: IN at the base, out at the head.
  - solver_in_count: 5 of 9 at the base, 0 of 9 at the head.
  - Null control `const`: pkg_modules=6, solver out at both ends.
  - Timing was taken at load1 of about 40, so no timing figure is verified. The body claims none.
- Mutation proof, re-run with features_block.py on the committed head and restored each time:
  - M1 (silent_mode), M2 (legionella), M3 (optimizer REASON_IDLE) and M4 (quiet_windows) each fail exactly their named check (1 of 5).
  - Reviewer mutant M5, `import scipy` in payload.py, fails 4 of 5: the scipy arm is live.
  - Revert arm, the base's custom_components under the head's checks: 4 of 5 fail, and store passes at both ends, as the body says.
- Ledger pins at drift.py:
  - GUARD_OFF `if tz is None:` -> `if False:` fails `R9-P3/#1741: a naive start walks the wall clock and stays naive`.
  - RETURN_DEL `pass` makes tests/guard_pins.py exit rc=1 (TypeError).
  - Both bot pins kill, and the two deleted optimizer.py anchors no longer exist.
- VERSION, the manifest, RELEASE_NOTES.md and both claim files are byte-identical to the merge base. `git merge-tree --write-tree origin/main <head>` exits 0 at origin/main 52f698905.
- Red checks: `mutation` was red at 29ccddab0. pr-contract at 3b76e0b08 logged that it was unanswered (`check mutation is red and ## Red checks does not name it`). The body now names it under ci-autofix.md, and pr-contract at the head is success. The trigger is answered.
- CI at the head when this verdict was written: fast (3.14), mutation, coverage and Analyze (python) were in_progress. Every other latest run per name was success, skipped or neutral (evidence/checkruns_head.tsv). Nothing here rests on those four.

## Why blocked

1. **Census placement (headline, fix-review step 14).** `tools/audit/seat/solver_closure_census.py` produces a body figure (17 -> 10) that a later seat reruns, so it is a harness. fixer.md 18 says such a harness lands in `dev/audit/harnesses/`, and tools/audit/seat/INSTRUMENTS.md says the same of `harnesses/`. Its own docstring says it sits in tools/audit/seat only to avoid the INERT READS that harness_headers.py's read of `dev/audit/harnesses/` would predict.
   - The body says no Darwin seat can record that read. ci-autofix.md refutes that as a reason: the bot "merges INERT READS from CI recordings too (#1886)". Every sibling harness there carries exactly that `inert_reads` row; `archscore_layering_seam_census.py`, for one, sits under `inert_reads/tests/harness_headers.py` in closures.json.
   - The placement also exempts the file from harness_headers' header contract. It has no metric, baseline or machine header.
   - Repair: move it to `dev/audit/harnesses/` with a conforming header, and let closures-autofix record the inert read.
2. **Moved-symbol references left at the old home (architect note 1: "import lines and moved-symbol references, re-exporting nothing").** `tests/features.py:25622` imports 8 REASON_* codes, and `tests/features.py:60240` imports 6, from `heatpump_optimizer.optimizer`. They resolve only because the optimizer happens to import them from payload.
   - This contradicts the body's "Tests … import the moved names from their new owners".
   - The fixer did repoint four other features.py sites and manual_plan.py.
   - The optimizer.py group next in the chain is R10-SAV-REASONS. It will break those two imports in an unrelated block if it changes which codes the optimizer imports.
   - `tests/dst_checks.py` reads the clock through coordinator and optimizer on purpose: its identity check `_utc_step_starts is _opt_utc_step_starts` needs it. That one is fine.
3. **Archscore attribution (step 14).** dS +0.4646 splits as layer_violations +0.2016 and private_cross_module +0.2630.
   - Removing the named mechanism: silent_mode and quiet_windows import `utc_step_starts` from `.optimizer` again, and legionella imports `REASON_LEGIONELLA` from `.optimizer` again (evidence/armA.patch). This gives `dS +0.2630, private_cross_module 17 -> 14`. layer_violations returns, so that half is earned. The private_cross_module half survives.
   - Planting a rename only on the merge base (`_utc_step_starts` -> `utc_step_starts`, left in optimizer.py, evidence/armB.patch) reproduces `dS +0.2630, private_cross_module 17 -> 14` with nothing moved.
   - So that half is earned by the private -> public rename, not by "the two moved owners", and the body's "putting either import back undoes it (M1, M4)" is false for it.
   - The rename is a sound part of a sound move, so this is not a code defect. It is an instrument finding: archscore credits a bare rename. Correct the body's attribution, and carry the finding to archscore's owner (finding-propagation.md).
4. **The vocabulary check has a hole.** Reviewer mutant M6 removes `REASON_PUMP_MODE` from the optimizer's payload import and adds `REASON_PUMP_MODE: str = "pump_mode"` to optimizer.py. The result is `ALL 5 FEATURES BLOCK PASSED`.
   - `_leaf_own` walks only `ast.Assign`, so an annotated (or nested) second definition passes.
   - The `is` comparison cannot catch it either, because the literal is interned.
   - Repair: count `ast.AnnAssign` targets too, or refuse any binding of a REASON_ name in optimizer.py other than the payload ImportFrom.
5. **Forward-carry (step 10, noted, not the block class).** The second UTC owner, `accuracy.utc_shift`, is "reported to the orchestrator for the roster". `utc_shift` appears 0 times in dev/programme/rosters/wave-r10-groups.json on origin/main. The orchestrator owes it a destination.

## RESULT lines

RESULT clock_body_identical_modulo_name=True
RESULT reason_codes base_optimizer=18 head_payload=18 head_optimizer_assigns=0 values_identical=True
RESULT census_own base modules=76 solver_in=17 import_failures=0
RESULT census_own head modules=76 solver_in=10 import_failures=0
RESULT finder_layering base setpoint_check=23(IN) quiet_windows=21(IN) silent_mode=20(IN) store=18(out) private_cross_module_names=16
RESULT finder_layering head setpoint_check=14(out) quiet_windows=11(out) silent_mode=8(out) store=18(out) private_cross_module_names=13
RESULT finder_runtime_closure solver_in_count base=5/9 head=0/9 null_const pkg_modules=6/6 solver=out/out
RESULT mutants M1..M4 killed 1/5 each; M5 (reviewer) killed 4/5; M6 (reviewer, AnnAssign) SURVIVED 0/5
RESULT revert_arm 4 of 5 FEATURES BLOCK FAILED
RESULT ledger drift.py GUARD_OFF killed (features); RETURN_DEL killed (guard_pins rc=1)
RESULT archscore head dS=+0.4646 (layer_violations 22->19 +0.2016, private_cross_module 17->14 +0.2630)
RESULT archscore mechanism_removed dS=+0.2630 (private_cross_module survives)
RESULT archscore rename_only_plant dS=+0.2630 (reproduces private_cross_module)
RESULT old_home_test_imports tests/features.py:25622 (8 codes) tests/features.py:60240 (6 codes)
RESULT merge_tree rc=0 vs origin/main 52f698905

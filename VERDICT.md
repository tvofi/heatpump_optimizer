Fix review: blocked ecdcc466d343421f091bcc9b5b159149bfaf36eb carry-missing: not carried to R10-LIVESTATE (accuracy.utc_shift second UTC owner; 0 occurrences in the roster at origin/main 9a1ce39c3 or handoff/audit-r10-roster)

bus-nonce: 194c58fdcefebf42b36b06bf3de4d3ae

PR #2371, R10-LEAF-IMPORTS. Review round 2. This is a delta re-review of the five items from round 1 (review/2371 ddd9a7d30).
- Measured head: ecdcc466d343421f091bcc9b5b159149bfaf36eb. It was still the PR head when this verdict was written.
- Merge base: 52f698905868c9140ed213ea542c44053fca7096.
- Fresh detached worktrees: head (two copies, so that mutation and measurement never shared a tree) and merge base.
- Production is unchanged since round 1. The custom_components +/- lines of merge-base...head are identical to round 1's 811df3cf3...8d76a9edf.

The blocking item is the only open one. Items 1-4 are cleared. Placing the carry needs no head move: a re-dispatch at this same head that finds the carry in R10-LIVESTATE's roster entry clears it.

## Round-1 items

1. **Census placement: cleared.** The harness is now `dev/audit/harnesses/r10_leaf_solver_closure.py`, with Metric, Command, Perturbation, Expected and Baseline headers.
   - Commit a70d4a3b6 adds one line to `inert_reads[tests/harness_headers.py]`.
   - That list stays sorted. Every one of the 43 `.py` files under dev/audit/harnesses/ is in it, and so is the new one. That is the shape a recording of a whole-directory read writes, and it matches precedent 2f7aafdc8.
   - It is not a silencing. An inert_reads row widens what runs: touching the file now selects harness_headers.py.
   - CI at this head: `closures` success, with "committed closures cover every file this run touched". `closures-autofix` was skipped, so no repair was owed.
   - The log notes that harness_headers.py lists 3 files its Linux run did not touch (safe: over-scoped). It does not name them, and I did not download the recording artifact to identify them. So I have not verified that CI's strace itself touched the new file. Either way the row errs wide, not narrow.
   - Local `tests/harness_headers.py` at the head: `ALL 109 HARNESS HEADER CHECKS PASSED`, rc=0.
2. **Old-home imports: cleared.** An AST walk over every tracked .py finds 0 REASON_* imports from optimizer or coordinator. Four clock imports remain:
   - tests/dst_checks.py:31 and :45 are deliberate: its `_utc_step_starts is _opt_utc_step_starts` identity check needs both namespaces.
   - round8 s2_fee_dst.py and round9 m4_probes.py are closed-round evidence, read only as inert text.
3. **Archscore attribution: cleared.** The body now credits only layer_violations (+0.2016). It names private_cross_module (+0.2630) as the rename, reproduced by the rename-only plant. My re-run at this head: `dS +0.4646` (layer_violations 22->19 +0.2016, private_cross_module 17->14 +0.2630).
   - The instrument finding is already in the tree: tools/audit/archscore/ABOUT.md line 225 says `a3_private_cross_module_fix` is a pure private-to-public rename. The R10-BRIEFS-FOLD carry repeats it. So the archscore Forward-carry line has a destination.
4. **Vocabulary-check hole: cleared.** Mutants at this head, each restored:
   - M1, M2, M3 and M4 are each killed (1 of 5).
   - M5 (scipy in payload) is killed 4 of 5.
   - M6 (AnnAssign redefinition) is now killed.
   - Reviewer M8 (a tuple-unpack redefinition `REASON_PUMP_MODE, _x = "pump_mode", 0`) is killed.
   - Residual, not blocking: reviewer M7, `globals()["REASON_IDLE"] = "idle"`, survives. It is a dynamic write that no static walk sees, and the literal is interned. The check's comment claims static binding forms only.
5. **Forward-carry for utc_shift: BLOCKING.** The body sends it to R10-LIVESTATE, and the orchestrator said it would place the carry. It is not there yet: `utc_shift` occurs 0 times in dev/programme/rosters/wave-r10-groups.json at origin/main 9a1ce39c3 and at handoff/audit-r10-roster. R10-LIVESTATE's carry list is in evidence. fix-review step 10 and finding-propagation.md require the carry to exist at its destination before the producing PR merges.

## Re-measured at this head

- Census (my evidence/census_own.py, not the fixer's harness):
  - Base 52f698905: `modules=76 solver_in=17 scipy_in=18 import_failures=0`
  - Head: `modules=76 solver_in=10 scipy_in=11 import_failures=0`
  - The same seven leaves leave, and none enters. This matches the harness's EXPECTED lines.
- CI: the latest run per name at the head is success, skipped or neutral for all checks (evidence/r2_checkruns_head.tsv), including fast (3.14), closures, mutation and pr-contract.

## RESULT lines

RESULT census_own base modules=76 solver_in=17 scipy_in=18 import_failures=0
RESULT census_own head modules=76 solver_in=10 scipy_in=11 import_failures=0
RESULT mutants M1..M4 killed 1/5; M5 killed 4/5; M6 killed; M8 (reviewer) killed; M7 (reviewer, globals() write) survived
RESULT old_home_imports REASON_*=0; clock=4 (dst_checks x2 deliberate identity check; round8/round9 inert evidence x2)
RESULT archscore head dS=+0.4646 (layer_violations +0.2016 credited; private_cross_module +0.2630 named a rename)
RESULT harness_headers ALL 109 HARNESS HEADER CHECKS PASSED rc=0
RESULT ci closures=success closures-autofix=skipped fast=success mutation=success
RESULT carry utc_shift occurrences in roster at origin/main 9a1ce39c3 = 0

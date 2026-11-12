Residue of R10-PREPR-CAP and R10-FLY-CIPREDICT-RESTORING on the pre-open prediction seam. This head lands Carry 4 (the `.gitignore` anchor, pinned by a `gitignore_config` arm of `tests/layout.py` (its self-test carries the null control: an unanchored `config/` rule yields 2 findings, the anchored `/config/` rule 0)) and repairs Carry 6 (PREPR-SLOT-LIVELOCK): the first review blocked the dismissal because its null control could not fail; the harness is rebuilt with a discriminating bare arm and a real `take_slot` path. Carries are numbered 0-based, as the brief and the handoff check number them (`Carry N`); the fix review's "carry 7" is this body's Carry 6 (PREPR-SLOT-LIVELOCK) and its "carry 5" is Carry 4 (`.gitignore`), the same two items counted from 1.

Status: Carry 4 landed in this head (the `.gitignore` anchor); Carry 6 is dismissed below with the discriminating controls named; untouched in this part: Carry 0, Carry 1, Carry 2, Carry 3, Carry 5, Carry 7, Carry 8, Carry 9, Carry 10, Carry 11, Carry 12, Carry 13, Carry 14, Carry 15, Carry 16, Carry 17, Carry 18, Carry 19, Carry 20, Carry 21, Carry 22, Carry 23, Carry 24.

## Head

bdc2e986fa5f8f72c7194c685b20b0c0041f66a2, measured with `tools/pr/prepr.sh` on the committed tree. `git merge-tree --write-tree origin/main HEAD` at origin/main 2cfa3d7d6 reports no conflict (exit 0). `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/ci_budgets.json tests/deployment_shape.py` is empty: 37d7082ae and 2c9defdc2 are net-reverted by bdc2e986f, so no budget is raised.

## Mutation proof

Carry 4: reverting the `.gitignore` anchor to the unanchored `config/` rule turns the `tests/layout.py` gitignore arm red (its self-test with rule `config/` expects 2 findings). Carry 6: `python3 dev/audit/harnesses/prepr_slot_nested.py --mutant` deletes the `export HPO_SLOT_LABEL` line from the cut `take_slot`; the nested arm then queues (nested_finished=0, nested_queue_empty=0, outer_exported_label=0) and the harness exits 1.

## Mutant run

`python3 tools/audit/seat/mutant_run.py --diff $(git merge-base origin/main HEAD)...HEAD` generates zero mutants: the three-dot diff holds no production line, only `.gitignore`, `tests/layout.py` and harness/ledger files. The mutation proofs above are therefore the manual ones.

## Null control

Carry 4: `git check-ignore` still ignores a root-level `config/`. Carry 6: the bare arm (the same nested `take_slot` call without the label, pool 4/4 held) is still waiting at its bound AND `slot-status` lists its ticket (`queue=prepr-741`, bare_queued=1); the labelled nested arm prints `heavy slot joined prepr-733`, finishes in 0.1 s and leaves `queue=-`. The two arms differ by a slot-status queue entry, not by a bound both miss. The harness never sets HPO_SLOT_LABEL itself: the outer shell runs prepr's real `take_slot` against the real `tests/gate_lock.py` with 3 of 4 slots held and exports the label on the take path (prepr.sh:4184). The WARN path (:4192, unusable lock dir) exports none and the nested call only warns, it does not queue (warn_no_label=1, warn_finished=1). Static control: prepr's `--self-test` branch holds no real `take_slot` call (selftest_branch_takes_slot=0), so the nested self-test cannot queue in any arm.

## Figures

- `python3 dev/audit/harnesses/prepr_slot_nested.py` (figures recorded at 79c063dcda07232b5773c4502a7c16af616fe4b3; the harness since inlines the canonical repo_root walk, `python3 tests/harness_headers.py` 112/112 pass): verdict=ok; pool_full=1, outer_exported_label=1, nested_finished=1, nested_queue_empty=1, nested_joined=1, bare_finished=0, bare_queued=1, warn_no_label=1, warn_finished=1, selftest_branch_takes_slot=0.
- `--mutant`: verdict=FAIL, rc 1.
- `python3 tests/layout.py`: ends `layout self-test: ok`, including `gitignore self-test: rule 'config/': 2 finding(s), want 2` and `rule '/config/': 0 finding(s), want 0`; Carry 4's pin. `python3 tests/entities.py`: 2707/2707 pass. `python3 tests/structure.py`: passes.

## Red checks

Reds on the old head 433536b65 of `fix/r10-prepr-residue`. `python3 tools/audit/seat/merge_train.py owed-reds` lists `tests / arch-instrument`, `tests / closures` and `tests / fast (3.14)` among the owed contexts and does not list `tests / closures-autofix`.

- tests / arch-instrument (owed): `UNWIRED TEST: tests/gitignore_config.py is not referenced by tests/run.sh`. The branch's own: carry 4 added a new script that `tests/run.sh` never ran. Cheaper detector: the `UNWIRED TEST` loop in `tests/run.sh` (line 522 prints it), sub-second, run scoped before the handoff; it existed and was not run on that head. No new countermeasure owed; it stands at nil standing cost. Fix: bdc2e986f deleted the script and folded the check into `tests/layout.py`, so there is nothing to wire.
- tests / closures (owed): `UNDER-SCOPED: tests/entities.py really reads` `tests/gitignore_config.py`, the same cause. Cheaper detector: `tools/pr/prepr.sh` step 6d (`tools/pr/ci_predict.py` over the three-dot diff), which is already standing in prepr. Fixed by the same deletion: no new file is read, so the closure is unchanged.
- tests / fast (3.14) (owed): `FAILED tests/entities.py` and `tests/harness_headers.py`. entities.py read the new script (same cause); harness_headers.py failed on `dev/audit/harnesses/prepr_slot_nested.py`, whose repo_root walk is now inlined in the canonical form (fe9beb2bf). After the fixes `tests/entities.py` passes 2707/2707 and `tests/harness_headers.py` 112/112. Cheaper detector for the header failure: `python3 tests/harness_headers.py` run on the touched harness, seconds; recorded as nothing new to build.
- tests / closures-autofix (not owed): `AUTOFIX: skip-failed-recording`, downstream of tests / closures; it clears when that does.

## Forward-carry

- PREPR-SLOT-LIVELOCK: Carry: dismissed: not reproducible, nested heavy steps join the outer slot (dev/audit/harnesses/prepr_slot_nested.py at 79c063dcda07232b5773c4502a7c16af616fe4b3)

## Friction

none

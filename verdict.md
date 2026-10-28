Fix review: merge 39e5a3df4aa76b5d13099fe2ef20dcdbd66f2295

bus-nonce: c6f567dd46624c765e3e97b5315cc207

## Scope

PR #2912, R10-CONFIGFLOW-PAGES arm A + A3' (D7-s2-56). Round 2: the previous verdict blocked `4fc6a4c51`. Reviewed head `39e5a3df4aa76b5d13099fe2ef20dcdbd66f2295`, merge base `b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa`. Interpreter: `/opt/hpo/venv-ci` Python 3.14.7. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the role contract is current. The review packet rendered with `Refusals: none`. The head was re-read just before return and is still `39e5a3df4`.

## Findings

- Arms B (D7-s2-55), C/C2 (ARCH2-s5-F1) and D, plus the design carries this PR does not discharge (`ledger-rekey` for arm B, `c19-dr`, `literal-clones`, `dr1-b-c2-conflict`, `close-2238`, `dr1-close-2238-disposition`), are deferred to the group's later pull requests. #2238 stays open. The roster on origin/main, `dev/programme/rosters/wave-r10-groups.json` group R10-CONFIGFLOW-PAGES, already states the c19-dr and literal-clones carries as preconditions. Carry: R10-CONFIGFLOW-PAGES

## Evidence

- RESULT mutation proof (step 1). Each mutant is a single-site edit in a `git archive` of the head, followed by `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` (`ev/mut.sh`, `ev/mut_*.txt`):
  - M1, re-render over `flat`: 7 of 531 FAILED.
  - M2, `check(flat, …)`: 3 of 531 FAILED.
  - M3, `if True:`: 38 of 524 FAILED.
  - M4, `finish` dropped: 4 of 531 FAILED.
  - M5, placeholders `None`: 4 of 531 FAILED.
  - M6, `_clear_absent(…, current)`: 1 of 531 FAILED, the wood-block check.
  - A3'-M1: 1 of 531 FAILED.
  - A3'-M2: 1 of 531 FAILED.
  - Null mutant, comment only: ALL 531 PASSED.
  - The 8 of 8 count and every named failing check match the body. The body's 530 and 523 were measured at earlier commits; this head has 531 checks.
- RESULT suite at the head: `ALL 531 checks PASSED`, rc 0. The head's tests over the base `config_flow.py` give `6 of 531 checks FAILED`, rc 1. They are exactly the six named in the body: still_stored 9/9/1/1/7, and the price-entity check `type=menu errors=None stored=None` (`ev/head_cfs.txt`, `ev/base_cfs.txt`).
- RESULT defect harness `dev/audit/harnesses/r10_configflow_pages.py`, base → head:
  - main run: `stale_slots=27` → `stale_slots=0`, with `pages=9 rejected=9 stored_rows=30` at both ends.
  - `--null`: `rejected=7 stored_rows=30 shown_stored=19` at both ends.
  - `--clear-required`: `type=menu errors=None stored_price_entity=None` → `type=form errors=price_entity_required stored_price_entity='sensor.price'`.
  - `--accepted`: `cases=11 exceptions=1 digest=071e7ad04eb0` at both ends.
  - Source: `ev/base_harness.txt`, `ev/head_harness.txt`. This harness is the fixer's own port, disclosed as such in the body.
- RESULT finder's harness (step 2): `bash dev/audit/rounds/round10/D7/arch-s2/run_findings.sh 04_suggested 08_page`. I ran it from a worktree at `01d9d0be2` (branch `handoff/audit-r10-arch-s2`), because the script is not in the tree at `554e2ecfa` itself.
  - `08_page`: `delta_S=+1.1717`, `duplication_copies=68->62`, `perturbed_delta_S=+0.0000`, `perturbed_vector_equals_baseline=1`.
  - `04_suggested`: `+0.1880`, `68->67`.
  - Both match the body (`ev/finder_run_findings.txt`). The harness runs at the finder's base, so its reading at the PR head is not applicable. The head side is covered by archscore below and by the defect harness above.
- RESULT class (step 6): every options step holding a `_STORED` row (entities, entities_metering, entities_pump, comfort, hot_water, hot_water_tank, hot_water_pumps, building, grid_fees, solar_pv, away) now routes through `_page(..., clear=True)`. The pages that still re-render over raw `user_input` are thermal_model and thermal_model_zones (`_try_thermal_model_save`), and they hold 0 `_STORED` rows. The pages with `clear=True` and no `check` never reject. `grep -c 'when=' config_flow.py` = 15, as the body states. No class seam is left open.
- RESULT survivor triage: reading `_entities_errors` at the head confirms the second `return errors` is equivalent. Its arm runs only when `submit`'s token is falsy, so `submitted` is falsy and `if submitted and …` is skipped, which returns the same dict. The `survivor_triage` row's reasoning matches the code.
- RESULT figures re-taken at this head (`ev/checks.txt`):
  - `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc 0. `class_excess_loc` moves 18037 → 17991, down only, and no budget was raised.
  - `tests/entities.py`: `ALL 2467 ENTITY CHECKS PASSED`.
  - `score.py --diff b6f6ceca4`: `Architecture score: dS +2.3483 IMPROVES`, `duplication_copies 35 -> 29`.
  - `GOLDEN_MODE=drift tests/golden.py`: `NO UNCLAIMED DRIFT: 56`, `NO STALE FIXTURE: 56`, config_flow byte-identical.
  - `ci_predict.py`: no red predicted.
  - `closure.py select`: `MODE: SCOPED -- 13 script(s) run, 20 scoped out`.
- RESULT claims and versions (steps 4, 5): both claim files are byte-identical to the base, and golden drift is clean, so nothing moved and nothing is claimed. `VERSION`, `RELEASE_NOTES.md`, the manifest and both claim files are untouched: the three-dot diff over them is 0 lines.
- RESULT merge (step 13): `git merge-tree --write-tree origin/main 39e5a3df4` exits 0 against origin/main `b0b2d7697`, which has moved past the base by triage-only records. No conflict (`ev/merge_tree.txt`).
- RESULT CI on this head (step 11, check-runs API, every run listed in `ev/checks_final.txt`): every check concluded success or skipped except one `gate` run, 123101876777 (`CI code`). That run printed `FAIL run(s) [40762415902] at this head are still being judged; their gate decides`, and the `CI edit` gate it names, 123109181671, concluded success. It is a sequencing hand-over, not a content red. `pr-contract` 123105959019 started at 21:21:38Z, after that red concluded at 21:21:36Z, and is green, so it is the evidence. `tests / mutation` 123078855071 is a real pass, not INCONCLUSIVE: `PIN RE-VERIFICATION: 3 reproduced`, `0 survivor(s) of 3 evaluated`, `MUTATION TABLE PASSED`. The earlier `tests / mutation` red at `4fc6a4c51` is answered in the body's `## Red checks` with a named cheaper detector.
- RESULT head in body (step 7): `## Head` names `39e5a3df4aa76b5d13099fe2ef20dcdbd66f2295`. The production code, the test and the harness are byte-identical between `9d043f781` and the head. The body's "this head" figures were taken at `1373f6820`; the `39e5a3df4` merge brings in only main's tools changes, and I re-took the figures at `39e5a3df4` myself.
- RESULT forward-carry (step 10): the roster group R10-CONFIGFLOW-PAGES on origin/main carries the c19-dr and literal-clones items as preconditions. The body names the rest under its Forward-carry section, routed to the same group (see Findings).
- Not re-derived: the body's per-mutant ledger re-key re-verification (`--anchor` runs at `71938ca71`). CI's mutation lane re-verified 3 pins at this head, and I did not re-run the table, per fix-review.md step 11.

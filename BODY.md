R11-SEAM-ratchets (ADR-009; D7-s1-02, D7-s1-03, D14-s2-03): two `tests/structure.py` rows and one `tests/entities.py` barrier that now read the property they name. Both new rows are new caps recorded at their measured value at the base; no existing row moves and no budget is raised. All three findings reproduce at the base, so none is "not reproduced at main".

- `in_function_copies` (D7-s1-02): a statement window written at two or more non-overlapping places of ONE function and in no other function. The row counts places past the first, the rule `duplication_copies` uses for members ("a third copy costs one more"). `duplicate_clones` joins functions, so such a copy moved no row. Both rows read one window enumerator, `function_windows`, which was cut out of `duplicate_clones`' body. `duplicate_clones`' window and output are unchanged (Null control). ADR-009 part 3's list of functions the score reads is therefore untouched in behaviour.
- `unused_package_imports` (D7-s1-03): a `from .<module> import N [as A]` binding that the importing module never loads, that no module re-imports from it, and that no string in it names. The re-export arm reads `import_bindings`' own symbol bindings. Under ADR-009 part 1 this PR deletes nothing; `R11-SEAM-dead-state`'s deletions re-record this row downward.
- N-log-flood barrier (D14-s2-03): `_r10_unlatched_logs` counts every `_LOGGER` call at WARNING or above. Before, it counted only `.warning` and `.error`; it now also counts `.warn` (the WARNING alias), `.exception`, `.critical`, `.fatal` (the CRITICAL alias), and `.log` at an int level of at least 30 or at any level other than `logging.DEBUG`, `INFO` or `NOTSET`. The level test is nested inside the function because `logflood_shape.py` execs that function alone.
- The barrier reads the text `_LOGGER`, so a second check, `_r11_logger_aliases`, refuses every way a package line can log through anything else. It refuses:
  - a name bound to `_LOGGER`, to a `getLogger` or `getChild` result, or to `import logging as x`;
  - any other `getLogger` or `getChild` call, bound or inline, with an Attribute or a bare-Name callee (`from logging import getLogger`);
  - an import of `_LOGGER` from anywhere, and an import of `logging`'s level functions, `getLogger`, `root`, `Logger` or `LoggerAdapter`;
  - a root-logger call or reference: `logging.<level>`, `logging.root`, `logging.Logger`, `logging.LoggerAdapter`;
  - any use of `_LOGGER` other than `_LOGGER.<method>(...)`: passed as an argument, returned, put in a container, or a bound method taken. That is the only way a logger reaches a parameter, because every other source of one is refused above.
- One live escape is listed with its reason and exact count in `_R11_LOGGER_HANDOVERS`: `coordinator.py` hands `_LOGGER` to Home Assistant's `DataUpdateCoordinator.__init__`. That class logs a failed refresh at ERROR only on the success-to-failure transition (its `last_update_success` latch), so it cannot flood. A stale or extra entry fails the check, as the R10 lists do. The one live site the barrier was blind to, `sysid.py` `_finish`, joins the once-per-event group: the raising fit sets the phase done and publishes a refusal in the same call.

Design choices a later seat should not read as bugs:
- `in_function_copies` excludes a window that a second function also holds. That window is already a clone class, priced once by `duplication_copies`.
- Overlapping spans merge, so a statement repeated in a row is one place.
- `unused_package_imports` counts every relative from-import, `from . import m` included. The finder's harness counted only `from .<module>` at level 1. At this base the two read the same value (Figures).

Alternatives not taken:
- A second copy of the window loop inside `in_function_copies`: it would duplicate the rule this row exists to price.
- Keying the new row per window, as the harness's count does: a third place would then move nothing.
- Folding the place count into `duplicate_clones`: ADR-009 part 3 keeps that function's window and output, which the score reads.
- Following a logger into a parameter by type inference: the check refuses the escape at its source instead, which needs no inference.

## Review block repaired

Two commits answer the review and the red at fc2daf48: f027a1b2 (the barrier and the comment) and c8950908 (a census for the new `unused_package_imports` row in `tools/policy/field_coverage.mjs`; see Red checks).

Review at fc2daf48 (round 1, class-open): the barrier did not read `_LOGGER.warn`, `_LOGGER.fatal`, a bare-callee `getLogger` binding, an inline `logging.getLogger(...).warning`, a root `logging.warning`, a from-import alias of `_LOGGER`, or a logger passed as a parameter.
- Every shape is now closed and pinned by a planted control in the existing checks, as listed above. No shape is left open.
- The test-side note is also fixed. The `# One window, three spellings` comment returns to `DUP_SELF_CHECK_BODY`, which it describes. `IN_FUNCTION_SELF_CHECK_SOURCES` gets a comment of its own. `UNUSED_IMPORT_SELF_CHECK_SOURCES`' comment now says five names, the count it lists.
- Probe: the reviewer's shapes, plus a keyword-argument handover, were planted in the live `coordinator.py`. Each is seen by the barrier or the binding check at head (warn, fatal, from_logging_getLogger, inline_getLogger, root_warning, from_import_alias, param, kwparam = 1). Controls: `_LOGGER.warning` is seen (1) and `_LOGGER.info` is not (0).

## Head

c8950908d2858a6d5791e97c7aad30cc87e20193, measured on base `origin/main` ae0ed64af898d8923ac35afe6e9c031ac1e6b111 at 2026-11-18T15:40:00Z.

## Mutation proof

Each mutant edits one predicate and runs the script's own checks. Names below are the FAIL lines printed.

`tests/structure.py`, counting-rule self-check (scratch copy `tests/_mutant_structure.py`, run as `PYTHONPATH=tests/hastub python3 tests/_mutant_structure.py`):
- M1 `if len(places) > 1 and len(owners[digest]) == 1:` -> `if len(places) > 1:`: `FAIL  a window one function writes twice and another once is a clone class, not an in-function copy`. This mutant survived my first self-check, whose two-function case had no function holding the window twice. That case was strengthened.
- M2 `if not places or span[0] > places[-1][1]:` -> `if True:`: `FAIL  a statement repeated in a row is one place, not two`.
- M3 drop `or (mod, bound) in reexported`: `FAIL  a package from-import nothing loads is unused`.
- M4 drop `or bound in words`: `FAIL  a package from-import nothing loads is unused`.
- M5 drop `or bound in loads`: `FAIL  a package from-import nothing loads is unused`.

`tests/entities.py`, full run per mutant (`PYTHONPATH=tests/hastub python3 tests/entities.py`, each result `1 of 2733 ENTITY CHECKS FAILED`):
- E1 `("warning", "error", "exception", "critical")` -> `("warning", "error")`: `FAIL R10 N-log-flood barrier: every unlatched WARNING/ERROR is on the reasoned list with its exact count`.
- E2 `return level.value >= 30` -> `return False`: the same check fails.
- E3 `not in ("logging.DEBUG", ...)` -> `in (...)`: the same check fails.
- E4 drop `targets[0].id == "_LOGGER"` from the canonical test: `FAIL R11 N-log-flood barrier reach: every package logger is a module-level _LOGGER = logging.getLogger(...)`.
- E5 drop `and node.value is not None`: survived as an equivalent mutant, because a valueless assignment already fails the logger test. The guard was deleted at d99bc4bc rather than pinned.

The review repair at f027a1b2 adds six more mutants. Each was run by exec'ing `tests/entities.py`'s barrier section, the check code verbatim, against the live package:
- R1 `("warning", "warn", "error", "exception", "critical", "fatal")` -> the old four: `FAIL R10 N-log-flood barrier`.
- R2 the ImportFrom rule -> `if False:`: `FAIL R11 N-log-flood barrier reach`.
- R3 the non-canonical `getLogger`/`getChild` call rule disabled: `FAIL R11 N-log-flood barrier reach`.
- R4 the `logging.<level>`/`root` rule disabled: `FAIL R11 N-log-flood barrier reach`.
- R5 the `_LOGGER` escape rule disabled: `FAIL R11 N-log-flood barrier reach`.
- R6 the `DataUpdateCoordinator` handover entry deleted: `FAIL R11 N-log-flood barrier reach`.

`prepr.sh`'s `MUTANT_CMD` draws only added `.py` lines outside `tests/` and `dev/`, and this diff has none.

## Null control

- `duplicate_clones(module_trees())` serialised as JSON at the base worktree and at head: `cmp` exits 0, the same 1157 bytes. The window refactor moves no clone class.
- The finder's null-control perturbations read flat at both ends: `--perturb use-import` keeps `unused_package_imports` at 14, and `--perturb clone-two-fns` keeps `in_function_copies` at 6 (harness) and moves only `duplication_copies` 8 -> 9.
- Every in-tree check carries its own planted control:
  - `tests/structure.py`: a window in two functions reads no in-function copy, and a statement run reads one place.
  - `tests/structure.py`: of the five planted bindings, the loaded, string-named and re-exported ones are not rows.
  - `tests/entities.py`: `_LOGGER.log(logging.DEBUG, ...)` and `_LOGGER.info` are not sites.
  - `tests/entities.py`: the canonical module-level `_LOGGER = logging.getLogger(__name__)`, calls of its methods (`.warning`, `.isEnabledFor(logging.DEBUG)`) and an annotated class field are not refused.
- Package reading at head: `_r11_logger_aliases` finds exactly the one listed handover, `coordinator.py:3541` (check `R11 N-log-flood barrier reach` passes).

## Figures

Harnesses are run from `git archive 819aa2e354b4e5baaf824b8568fd72bea8168a75 dev/audit/rounds/round11` exported to `$EXPORT`, at the base worktree (bc658f9d) and at head (d99bc4bc; the logflood figures re-run at f027a1b2), with `PYTHONPATH=tests/hastub`:
- `$EXPORT/dev/audit/rounds/round11/D14/s2/logflood_shape.py` (sha1 ef9a2072891916165b2096e6613d0d4637ad6dfd). Key: the barrier function's own Counter total over each planted shape.
  - Base: counted_warning=1, counted_exception=0, counted_critical=0, counted_log_level=0, counted_alias=0, barrier_sites_baseline=71.
  - Head: counted_warning=1, counted_exception=1, counted_critical=1, counted_log_level=1, counted_alias=0, barrier_sites_baseline=72. The +1 is `sysid.py:1850`, now dispositioned on the once-per-event list.
  - `counted_alias` reads 0 at both ends by design: an alias is refused by `_r11_logger_aliases`, which the harness does not exec. The companion is that check's planted `alias.py` (`log = _LOGGER` inside a function, the harness's alias shape), refused at head.
  - `live_blind_sites` reads 1 at both ends: the harness enumerates the shapes, not undispositioned ones.
- `$EXPORT/dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py` (sha1 e2f94c69129a1e2840e5b4b83e67dab96b576f7b):
  - Base and head, unperturbed: unused_package_imports=14, in_function_copies=6, ratchet_duplication_copies=8, recount_mismatches=0, ratchet_rows_off_budget=0.
  - `--perturb unused-import`: base ratchet_rows_off_budget=0; head ratchet_rows_off_budget=1 (`unused_package_imports 14->15`).
  - `--perturb clone-same-fn`: base off-budget reads only `dead_top_level_symbols 1->2`; head adds `in_function_copies 11->12`.
- `python3 tests/structure.py` at head: `in_function_copies` reads 11 and `unused_package_imports` reads 14.
  - `in_function_copies` is the places past the first summed over the windows the "duplication inside one function" table prints. That table prints the same six functions the harness counts, one window each; the harness counts windows, the row counts places.
  - `unused_package_imports` matches the harness's 14.
- Budgets: `python3 tests/structure.py --record` at head adds both keys at their measured value. `regression_rows` reports no loosening, and every other key is unchanged (`git diff origin/main...HEAD -- tests/structure_budgets.json`).
- Architecture score: `python3 tools/audit/archscore/score.py --diff bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f` printed `Architecture score: dS +0.0000 NULL`. The repair at f027a1b2 edits only `tests/`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` reads `MODE: SCOPED`. Every script `scope.run` names passed at d99bc4bc: `tests/arch_score.py`, `tests/arch_score_head.py`, `tests/doc_claims.py`, `tests/entities.py`, `tests/features.py`, `tests/harness_headers.py`, `tests/stress.py`, `tests/structure.py`. The repair at f027a1b2 edits only `tests/entities.py` and `tests/structure.py`, and both were re-run there: `ALL 2733 ENTITY CHECKS PASSED` and `STRUCTURE RATCHET PASSED`.

<!-- figure-block: scope-line mb=ae0ed64af898d8923ac35afe6e9c031ac1e6b111 head=c8950908d2858a6d5791e97c7aad30cc87e20193 -->
~~~text
MODE: SCOPED -- 8 script(s) run, 25 scoped out.
~~~
<!-- /figure-block -->

## Red checks

- `governance / policy-docs`, red at fc2daf48 (job 134870283400), the only owed red:
  - It printed `REFUSED  census registry: row unused_package_imports counts unreached definitions and no census plants it`.
  - Cause: this PR added a liveness-named row (`/dead|kept|unused|unread|orphan/`) to `tests/structure_budgets.json`, and `field_coverage.mjs` requires every such row to carry a census. I registered none.
  - Fixed at c8950908. The census `structure.py unused_package_imports` plants one unloaded `from .const import DOMAIN as _census_unused_package_import` in `away.py`, which already imports from `.const`, so the plant adds no new edge.
  - Checks at c8950908:
    - `node tools/policy/field_coverage.mjs --only census`: `RESULT read=9 ... blind=0 dead=0 refused=0`, `FIELD COVERAGE ok` (8 censuses read at fc2daf48's copy, one refused).
    - `--self-test`: `FIELD COVERAGE SELF-TEST ok`.
  - Which copy CI runs: the comment at the field-coverage step of `governance.yml` says that step always runs the base's pinned copy. On this PR it therefore runs without the new census until c8950908's file is on main. The PR's own copy runs in `tests.yml` ("The pull request's field_coverage.mjs").
  - Cheaper detector: `field_coverage.mjs --only census` at the head, about 220 s here. It would have refused before the first handoff. `prepr.sh`'s `ci predict` printed no governance red predicted because it does not run this arm. Standing cost: one run of about 4 minutes per prepr whose diff adds a row to `tests/structure_budgets.json` or `tests/ci_budgets.json`.
  - Countermeasure: not built in this group, which may not change `prepr.sh`. Recorded here for the root-cause seat.

## Forward-carry

none

## Friction

dispatch-brief-inline: contradiction: the brief's "Do your work inline, with no subagents" met the frugal PreToolUse hook's per-prompt inline-read cap, and the first fire stopped (BLOCKED.md at b430bc7e); the orchestrator's inbox ruling (mandate 6893738184) corrected the brief for this seat. Carry: dismissed: corrected by that ruling before this run, pending owner confirmation as the ruling states

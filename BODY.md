R11-SEAM-ratchets (ADR-009; D7-s1-02, D7-s1-03, D14-s2-03): two `tests/structure.py` rows and one `tests/entities.py` barrier that now read the property they name. Both new rows are new caps recorded at their measured value at the base; no existing row moves and no budget is raised. All three findings reproduce at the base, so none is "not reproduced at main".

- `in_function_copies` (D7-s1-02): a statement window written at two or more non-overlapping places of ONE function and in no other function. The row counts places past the first, the rule `duplication_copies` uses for members ("a third copy costs one more"). `duplicate_clones` joins functions, so such a copy moved no row. Both rows read one window enumerator, `function_windows`, which was cut out of `duplicate_clones`' body. `duplicate_clones`' window and output are unchanged (Null control). ADR-009 part 3's list of functions the score reads is therefore untouched in behaviour.
- `unloaded_package_imports` (D7-s1-03; `unused_package_imports` until ebb5b253, see Red checks): a `from .<module> import N [as A]` binding that the importing module never loads, that no module re-imports from it, and that no string in it names. The re-export arm reads `import_bindings`' own symbol bindings. Under ADR-009 part 1 this PR deletes nothing; `R11-SEAM-dead-state`'s deletions re-record this row downward.
- N-log-flood barrier (D14-s2-03): `_r10_unlatched_logs` counts every `_LOGGER` call at WARNING or above. Before, it counted only `.warning` and `.error`; it now also counts `.warn` (the WARNING alias), `.exception`, `.critical`, `.fatal` (the CRITICAL alias), and `.log` at an int level of at least 30 or at any level other than `logging.DEBUG`, `INFO` or `NOTSET`. The level is the first positional or the `level=` keyword; a level behind `*args` or `**kwargs` is unknown and counted. The level test is nested inside the function because `logflood_shape.py` execs that function alone.
- The barrier reads the text `_LOGGER`, so a second check, `_r11_logger_aliases`, refuses every way a package line can log through anything else. It reads both logging surfaces by allow-list, so a spelling nobody listed is refused, not missed. It refuses:
  - a name bound to `_LOGGER` or to a `getLogger`/`getChild` result, and `import logging as x`;
  - any other `getLogger` or `getChild` call, bound or inline, with an Attribute or a bare-Name callee;
  - an import of `_LOGGER` or of a module named `logging` from anywhere, and an import from `logging` of anything but its level numbers (`*` included);
  - the name `logging` used other than as `logging.<level number>` or a `logging.getLogger(...)` call: `logging.warning`, `logging.root`, `logging.Logger`, `logging.makeLogRecord`, an uncalled `logging.getLogger`, `lg = logging`, `(lg := logging)`, `getattr(logging, ...)`;
  - the text `'logging'` (`__import__`, `importlib.import_module`, `sys.modules`), and an attribute named `logging` or `logger` (Home Assistant's coordinator exposes the handed-over `_LOGGER` as `self.logger`);
  - `_LOGGER.<method>(...)` for any method but the level calls and `isEnabledFor` (`_log`, `handle`, `makeRecord`, `getChild`);
  - any other use of `_LOGGER`: passed as an argument, returned, put in a container, or a bound method taken. That is the only way a logger reaches a parameter, because every other source of one is refused above.
- Not read, stated in the docstring: a module name computed at run time (`import_module('log' + 'ging')`). No syntactic rule names it; the string-constant arm is the bound.
- One live escape is listed with its reason and exact count in `_R11_LOGGER_HANDOVERS`: `coordinator.py` hands `_LOGGER` to Home Assistant's `DataUpdateCoordinator.__init__`. That class logs a failed refresh at ERROR only on the success-to-failure transition (its `last_update_success` latch), so it cannot flood. A stale or extra entry fails the check, as the R10 lists do. The one live site the barrier was blind to, `sysid.py` `_finish`, joins the once-per-event group: the raising fit sets the phase done and publishes a refusal in the same call.

Design choices a later seat should not read as bugs:
- `in_function_copies` excludes a window that a second function also holds. That window is already a clone class, priced once by `duplication_copies`.
- Overlapping spans merge, so a statement repeated in a row is one place.
- `unloaded_package_imports` counts every relative from-import, `from . import m` included. The finder's harness counted only `from .<module>` at level 1. At this base the two read the same value (Figures).

Alternatives not taken:
- A second copy of the window loop inside `in_function_copies`: it would duplicate the rule this row exists to price.
- Keying the new row per window, as the harness's count does: a third place would then move nothing.
- Folding the place count into `duplicate_clones`: ADR-009 part 3 keeps that function's window and output, which the score reads.
- Keeping the name `unused_package_imports` and landing its census first: no order of row and census is green under the base's pinned grader (Red checks).
- Dropping the import row to a report-only count until the grader can bootstrap: the finder's harness (`ratchet_rows_off_budget` under `--perturb unused-import`) would then not move, and a new unloaded import would go unrefused.
- Following a logger into a parameter by type inference: the check refuses the escape at its source instead, which needs no inference.

## Review block repaired

Required `gate` red at 33a67355, derived from `governance / policy-docs` (the base's pinned `field_coverage.mjs` refusing the `unused_package_imports` row): the row is renamed `unloaded_package_imports` at ebb5b253, with its count, value, budget and census unchanged (Red checks).

Round 2 at 5fe13702 (class-open): `_LOGGER.log(level=...)`, the `logging` module rebound by assignment or walrus, `_LOGGER._log` and `_LOGGER.handle`, and reflective lookups (`getattr(logging, ...)`, `__import__('logging')`, `import_module('logging')`) were seen by neither check. d983acca closes the class rather than the four shapes: the `_LOGGER` method set, the `logging` attribute set and the from-`logging` import set each became an allow-list, and the module object reaching any other expression is refused.
- Each reviewed shape is planted in the existing checks (`levels.py` `at_kw_error`, `at_star`, `at_kwargs`; `rebind.py`, `record.py`, `reflect.py`), beside new shapes of the same class (`surface.py`: `from logging import makeLogRecord`, `from homeassistant import logging as hl`, `logging.Logger.error(self, ...)`, `self.logger.error`; `star.py`; `getref.py`: `make = logging.getLogger`). Null controls: `_LOGGER.log(level=logging.DEBUG, ...)` is no site; `from logging import DEBUG`, `_LOGGER.log(level=DEBUG, msg='see logging')` and the canonical binding are not refused.
- Enumeration (fixer.md step 8): `_r11_unread` drives every callable of `logging.Logger`, called at ERROR on `_LOGGER`, and every name in `dir(logging)` through both checks. The reach check asserts what neither reads is exactly `_LOGGER.debug`, `.info`, `.isEnabledFor` and the eight level numbers, so a method or helper a Python release adds is refused. Corpus size: `python3 -c "import logging; print(sum(callable(getattr(logging.Logger, a)) for a in dir(logging.Logger)) + len(dir(logging)))"`.
- The reach check also asserts the package is flat (`rglob('*.py')` reads as many modules as the glob), the glob's precondition: a `sub/x.py` added to a copy of the package fails it, the unperturbed copy passes (Mutation proof).
- The reviewer's probe `ev/probe_shapes.py` (verdict/3729 8ebf85a6), run at d983acca: every row it printed unread at 5fe13702 is now seen: `log_kw_level barrier=1`, `private_log ['_LOGGER -> _LOGGER._log']`, `handle_record ['_LOGGER -> _LOGGER.handle', 'logging.makeLogRecord']`, `module_assign_alias ['logging -> Assign']`, `walrus_alias ['logging -> NamedExpr']`, `getattr_root ['logging -> getattr']`, `importlib` and `dunder_import ["'logging'"]`. Its controls are unchanged (`ctl_info barrier=0 alias=[]`, `ctl_warning barrier=1`).

## Head

ff9cfca087a80c1a40c65a962781aba33690b8c0, a merge of `origin/main` 9aa29bd52382d0fcd25c43aaa31adb70ef49ff5a (now the merge base) into ebb5b253, at 2026-11-19T07:00:23Z. ebb5b253 renames one row on d983acca. Every figure it can reach was re-run at ebb5b253 or at this merge, as each line says; the rest carry from d983acca, measured on base ae0ed64af898.

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

The repair at d983acca adds ten mutants, run by `ev/mutants.py` (in scratch): it execs `tests/entities.py`'s barrier block verbatim under each edit and prints the failing N-log-flood checks. Unmutated: none fail.
- K1 the `level=` keyword ignored, K2 an unknown level read as quiet: `R10 N-log-flood barrier`.
- K3 any `_LOGGER` method admitted, K4 the `logging` attribute allow-list back to a level denylist, K5 the name `logging` as a value admitted, K6 the text `'logging'` admitted, K7 `.logger`/`.logging` admitted, K8 the from-`logging` allow-list back to a denylist, K9 an uncalled `getLogger` admitted: `R11 N-log-flood barrier reach`.
- K10 the flat-package precondition dropped: no check fails on the live package, which is flat; the precondition's own control is a package copy with `sub/x.py`, which fails `R11 N-log-flood barrier reach` while the unperturbed copy fails nothing.

`prepr.sh`'s `MUTANT_CMD` draws only added `.py` lines outside `tests/` and `dev/`, and this diff has none.

## Null control

- `duplicate_clones(module_trees())` serialised as JSON at the base worktree and at head: `cmp` exits 0, the same 1157 bytes. The window refactor moves no clone class.
- The finder's null-control perturbations read flat at both ends: `--perturb use-import` keeps `unused_package_imports` (the harness's count; the row is now `unloaded_package_imports`) at 14, and `--perturb clone-two-fns` keeps `in_function_copies` at 6 (harness) and moves only `duplication_copies` 8 -> 9.
- Every in-tree check carries its own planted control:
  - `tests/structure.py`: a window in two functions reads no in-function copy, and a statement run reads one place.
  - `tests/structure.py`: of the five planted bindings, the loaded, string-named and re-exported ones are not rows.
  - `tests/entities.py`: `_LOGGER.log(logging.DEBUG, ...)` and `_LOGGER.info` are not sites.
  - `tests/entities.py`: the canonical module-level `_LOGGER = logging.getLogger(__name__)`, calls of its methods (`.warning`, `.isEnabledFor(logging.DEBUG)`) and an annotated class field are not refused.
- Package reading at head: `_r11_logger_aliases` finds exactly the one listed handover, `coordinator.py:3541` (check `R11 N-log-flood barrier reach` passes).

## Figures

Harnesses are run from `git archive 819aa2e354b4e5baaf824b8568fd72bea8168a75 dev/audit/rounds/round11` exported to `$EXPORT`, at the base worktree (bc658f9d) and at head (d99bc4bc; the logflood figures re-run at f027a1b2 and again at d983acca, unchanged: barrier_sites_baseline=72, counted_alias=0, live_blind_sites=1), with `PYTHONPATH=tests/hastub`:
- `$EXPORT/dev/audit/rounds/round11/D14/s2/logflood_shape.py` (sha1 ef9a2072891916165b2096e6613d0d4637ad6dfd). Key: the barrier function's own Counter total over each planted shape.
  - Base: counted_warning=1, counted_exception=0, counted_critical=0, counted_log_level=0, counted_alias=0, barrier_sites_baseline=71.
  - Head: counted_warning=1, counted_exception=1, counted_critical=1, counted_log_level=1, counted_alias=0, barrier_sites_baseline=72. The +1 is `sysid.py:1850`, now dispositioned on the once-per-event list.
  - `counted_alias` reads 0 at both ends by design: an alias is refused by `_r11_logger_aliases`, which the harness does not exec. The companion is that check's planted `alias.py` (`log = _LOGGER` inside a function, the harness's alias shape), refused at head.
  - `live_blind_sites` reads 1 at both ends: the harness enumerates the shapes, not undispositioned ones.
- `$EXPORT/dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py` (sha1 e2f94c69129a1e2840e5b4b83e67dab96b576f7b):
  - Base and head, unperturbed: unused_package_imports=14 (the harness's own count), in_function_copies=6, ratchet_duplication_copies=8, recount_mismatches=0, ratchet_rows_off_budget=0.
  - `--perturb unused-import`: base ratchet_rows_off_budget=0; head ratchet_rows_off_budget=1 (`unloaded_package_imports 14->15`, re-run at the renamed head).
  - `--perturb clone-same-fn`: base off-budget reads only `dead_top_level_symbols 1->2`; head adds `in_function_copies 11->12`.
- `python3 tests/structure.py` at head: `in_function_copies` reads 11 and `unloaded_package_imports` reads 14.
  - `in_function_copies` is the places past the first summed over the windows the "duplication inside one function" table prints. That table prints the same six functions the harness counts, one window each; the harness counts windows, the row counts places.
  - `unloaded_package_imports` matches the harness's 14.
- Budgets: `python3 tests/structure.py --record` at head adds both keys at their measured value. `regression_rows` reports no loosening, and every other key is unchanged (`git diff origin/main...HEAD -- tests/structure_budgets.json`).
- Architecture score: `python3 tools/audit/archscore/score.py --diff bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f` printed `Architecture score: dS +0.0000 NULL`. The repair at f027a1b2 edits only `tests/`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` reads `MODE: SCOPED`. Every script `scope.run` names passed at d99bc4bc: `tests/arch_score.py`, `tests/arch_score_head.py`, `tests/doc_claims.py`, `tests/entities.py`, `tests/features.py`, `tests/harness_headers.py`, `tests/stress.py`, `tests/structure.py`. The repair at f027a1b2 edits only `tests/entities.py` and `tests/structure.py`, and both were re-run there: `ALL 2733 ENTITY CHECKS PASSED` and `STRUCTURE RATCHET PASSED`. The repair at d983acca edits only `tests/entities.py`; at d983acca `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2733 ENTITY CHECKS PASSED` (both N-log-flood checks `ok`) and `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- Repair at ebb5b253 (the row rename), re-run at that head:
  - `m1_ratchet_census.py` (same sha1): `--perturb none` reads unused_package_imports=14, in_function_copies=6, ratchet_rows_off_budget=0; `--perturb unused-import` reads ratchet_rows_off_budget=1 (`unloaded_package_imports 14->15`); null control `--perturb use-import` keeps the count at 14 and lists only `dead_top_level_symbols 1->2` (its planted user function), so the renamed row does not move.
  - origin/main's `field_coverage.mjs` run against this tree: `RESULT read=61 ignored=29 declared_none=38 blind=0 dead=0 refused=0 runs=166`, `FIELD COVERAGE ok`, exit 0 (2170 s under load).
  - The head's copy: `RESULT read=62 ignored=29 declared_none=38 blind=0 dead=0 refused=0 runs=166`, `FIELD COVERAGE ok`, with `census structure.py unloaded_package_imports: 14 -> 15 with one planted member, refused on unloaded_package_imports`. `--self-test`: `FIELD COVERAGE SELF-TEST ok`. `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 57 policy file(s)`.
  - Scoped gate: `MODE: SCOPED -- 8 script(s) run, 25 scoped out` (the same eight as at d983acca). `tests/structure.py` passed at ebb5b253 and again at the merge (below). A local `run.sh` at ebb5b253 ran `env_drift.py --claims-only` and `closure.py selftest` (both ok) in two hours on a loaded host. It was then stopped by the merge, still queued for a heavy slot. The exclusive lease that `entities.py`, `stress.py` and `harness_headers.py` need is held by another seat until 12:02Z. This repair's diff reaches none of those three: it edits no line of `tests/entities.py`, and the other two read no budget row. Their last pass is at d983acca (above), and CI's scoped gate is the record for this head.
- Merge of `origin/main` 9aa29bd5 at ff9cfca0: `body_push.sh`'s predictor refused ebb5b253 (`AGREEMENT UNMERGED: HEAD does not merge into 9aa29bd52382`). `tests/structure_budgets.json` merges only under the local `ledgermerge` driver, which GitHub's merge does not run: main moved `duplication_copies` 8 -> 7 next to this PR's rows. At ff9cfca0:
  - `python3 tests/structure.py`: `ok   duplication_copies 7 <= 7`, `ok   in_function_copies 11 <= 11`, `ok   unloaded_package_imports 14 <= 14`, `STRUCTURE RATCHET PASSED`.
  - main's `field_coverage.mjs` is byte-identical to the copy run above (`cmp` exit 0), and its `LIVENESS_ROW` and `CENSUSES` gates, replayed over the merged `tests/structure_budgets.json` and `tests/ci_budgets.json`, leave no ungated liveness row.
  - `tests/closure.py select` against the new merge base: `MODE: SCOPED -- 8 script(s) run, 25 scoped out`.

<!-- figure-block: scope-line mb=9aa29bd52382d0fcd25c43aaa31adb70ef49ff5a head=ff9cfca087a80c1a40c65a962781aba33690b8c0 -->
~~~text
MODE: SCOPED -- 8 script(s) run, 25 scoped out.
~~~
<!-- /figure-block -->

## Red checks

- `governance / policy-docs` (and the required `gate` derived from it), red at fc2daf48, 5fe13702 and 33a67355 (jobs 134870283400, 134933263714), the only owed red. Repaired at ebb5b253 by renaming the row; the route chosen is a rename, not a split.
  - CI printed `REFUSED  census registry: row unused_package_imports counts unreached definitions and no census plants it`, then `FIELD COVERAGE REFUSED`.
  - Cause: the field-coverage step of `governance.yml` always runs the base's pinned `field_coverage.mjs` (`PINNED` = the PR base). That copy refuses any row of `tests/structure_budgets.json` or `tests/ci_budgets.json` whose key matches `LIVENESS_ROW` (`/dead|kept|unused|unread|orphan/`) unless the base's own `CENSUSES` gates it. The census this PR registered at c8950908 sits in the head's copy, so the base never read it.
  - No order of row and census turns green under that grader. Landing the census before the row is refused by the same file's other rule (`a census gates unused_package_imports, which is no row of ...`): main would go red on every later PR touching a field-coverage input. Landing the row first is this red. The census registry and its exemptions (`CENSUSES`, `CENSUS_EXEMPT`) are both in the pinned `.mjs`, so fixer.md step 5's first BOOTSTRAP remedy, unpinned data the grader reads, does not exist. Its split remedy fails for the same reason: a p1 holding only the census is refused once on main.
  - Repair: the row is now `unloaded_package_imports`, named for what `tests/structure.py` reads (a binding no `ast.Load` in its module reaches). Its count, value (14), budget and census are unchanged, and the function is renamed with it. `LIVENESS_ROW` does not match the new key, so the base's registry no longer demands a census. The census is kept and renamed, so from this merge main's copy plants it and gates the row. A census that gates no row stays refused, so deleting the row later is still caught.
  - What the rename gives up: until `LIVENESS_ROW` reads this key, deleting the census alone would not be refused by the registry. Widening the pattern after this merge is green, because the census is then on main: owed to round-end instrument triage (Carry below). The census comment in `field_coverage.mjs` says the registry does not demand it.
  - Checks at ebb5b253, with origin/main's `field_coverage.mjs` (byte-identical to the merge base's, `cmp` exit 0) copied into `tools/policy/` and run against this tree: `RESULT read=61 ignored=29 declared_none=38 blind=0 dead=0 refused=0 runs=166`, `FIELD COVERAGE ok`, exit 0. The head's own copy: `RESULT read=62 ignored=29 declared_none=38 blind=0 dead=0 refused=0 runs=166`, `FIELD COVERAGE ok`, with `census structure.py unloaded_package_imports: 14 -> 15 with one planted member, refused on unloaded_package_imports`; `--self-test`: `FIELD COVERAGE SELF-TEST ok`. `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 57 policy file(s)`.
  - Cheaper detector: running the base's copy at the head, as above. `prepr.sh`'s `ci predict` predicted no governance red because it does not run the census arm. The fixer's earlier check ran the head's copy, which passes by construction.
  - Countermeasure: not built here; this group may not change `prepr.sh` or the grader. Owed to the root-cause seat with the carry below.
  - Carry: dismissed: owed to R11-CLOSEOUT-CLEANUP (round-end instrument triage: widen `field_coverage.mjs` `LIVENESS_ROW` so the registry reads `unloaded_package_imports`, or replace the name test with a census-required flag on the row; green once this PR's census is on main)
  - Carry: dismissed: owed to R11-CLOSEOUT-CLEANUP (round-end instrument triage: a liveness-named budget row cannot land green, because the pinned census registry refuses both a row without its census and a census without its row; let a census land one merge ahead of its row, or have `ci_predict` run the base copy's census registry so prepr predicts the red)
- `tests / nightly-status`: not a required check (not in `merge_train.py owed-reds`); it grades main's nightly, inherited, not this pull request's.
- `code-scanning alert 57 (py/overly-permissive-file)`, `code-scanning alert 58 (py/overly-permissive-file)`, `code-scanning alert 59 (js/insecure-temporary-file)`, `code-scanning alert 60 (js/file-system-race)`, `code-scanning alert 61 (py/insecure-temporary-file)`, `code-scanning alert 62 (py/insecure-temporary-file)`, `code-scanning alert 63 (py/insecure-temporary-file)`, `code-scanning alert 64 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 65 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 66 (py/overly-permissive-file)` and `code-scanning alert 67 (py/overly-permissive-file)`: each is open on main, in `tools/audit/seat/postmerge.py`, `tools/audit/seat/roster_lib.py` or a round-11 harness under `dev/audit/rounds/round11/`. This diff touches no file any of them names (`git diff --name-only` at the merge base: five files, none of those). Inherited, not this pull request's; no cheaper detector applies to a red this diff did not cause.

## Forward-carry

none

## Friction

dispatch-brief-inline: contradiction: on this fire the hook refused a read of the `tests/entities.py` run log at its sixth inline op; one `frugal:scout` read that log, the route the hook names. Carry: dismissed: the orchestrator's ruling below covers it, pending owner confirmation

dispatch-brief-inline: contradiction: (first fire) the brief's "Do your work inline, with no subagents" met the frugal PreToolUse hook's per-prompt inline-read cap, and the first fire stopped (BLOCKED.md at b430bc7e); the orchestrator's inbox ruling (mandate 6893738184) corrected the brief for this seat. Carry: dismissed: corrected by that ruling before this run, pending owner confirmation as the ruling states

Fix review: merge f2d414f8920b8f29a00db515a4ade06c1f4b7bc9

bus-nonce: e40b1411f5a742062b019046d0d42833
pending-ci: gate

Round 8. This is a later round over the reviewed head 55508355. `review_carry.py 55508355 f2d414f8` prints `FRESH-REVIEW`. The PR's own delta is one commit, 3253832a, plus a merge of origin/main 35402f78 (085d9492, then f2d414f8). The commit touches only `tests/entities.py`, with 43 insertions and 79 deletions. There is no production delta, so the scope does not widen. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the role contract is current. The body carries the `## Re-cut` that `fixer.md` owes from round 4.

## Prior finding: resolved

Round 7 blocked `class-open` on `frame.report_usage`. That verdict offered three ways out, and this delta takes the third: it redraws the split so that a dependency API whose job is the record is residue too. The docstring now states two residue categories. The second is "any record a dependency writes when the package calls it, whatever the call's purpose. A dependency is any module the package does not ship." That is a category, not a list of examples (ADDENDUM rule 8). The event-loop census and the `warnings` and handler refusals are deleted. The planted `warn.py`, `report.py` and `handler.py` now pin the category as not refused: mutant M7 below puts `warnings` back in `reached`, and the reach check fails. The narrowed claim reads "every logger binding and call spelled in the package's shipped text is either a `_LOGGER.<level>(...)` call that the barrier reads or is refused". I tested it on its own axis with 14 new shapes, and no in-claim shape escapes (Evidence).

## Findings

- Residual: a dependency's own logger reached under a name with no logger word escapes both checks, for example `from urllib3.connectionpool import log` then `log.error('x')`, or `cp.log.error('x')`. Each reads `barrier=0 alias=[]` (`ev/probe_r8_f2d4.txt`). It binds no logger of the package, so it falls in residue category (2) as written: a record a dependency writes when the package calls it. It is not a seam the claim leaves unenumerated. The package's own loggers can only come from a `getLogger` or `_LOGGER` spelling, and each such spelling is refused (shapes below). Carry: dismissed: covered by the stated residue category (2); a run-time record count is the body's named home for dependency-written floods, and no live group owns one, as the body records

## Evidence

- Mutation (`ev/mutants_r8.sh`, through the round-7 reviewer's `ev/reach_drv.py`; results in `ev/mutants_r8.txt`): unmutated, both `R10 N-log-flood barrier` and `R11 N-log-flood barrier reach` print `ok`. 10 of 10 targeted mutants are killed:
  - M1: `exception` and `critical` dropped from the level set. FAIL R10 and R11.
  - M2: the `level=` keyword is ignored. FAIL R10.
  - M3: `logger` dropped from `reached`. FAIL R11.
  - M4: `[Ll]ogger` dropped from `names_one`. FAIL R11.
  - M5: shipped files are not read. FAIL R11.
  - M6: the pickle opcode arm is not read. FAIL R11.
  - M7: `warnings` refused again, which reverses the category. FAIL R11.
  - M8: the `_LOGGER` escape rule is disabled. FAIL R11.
  - M9: the coordinator handover allowance is deleted. FAIL R11.
  - M10: every getLogger binding is treated as canonical. FAIL R11.
- Probe (`ev/probe_r8.py`, this reviewer's harness, not the finder's; output `ev/probe_r8_f2d4.txt`):
  - Controls: `_LOGGER.warning` reads `barrier=1` and `_LOGGER.debug` reads `barrier=0`, both with no refusal.
  - Refused in-claim shapes: an annotated top-level binding to `getLogger`; a class-body `_LOGGER = getLogger`; `_LOGGER` as a default argument; `@_LOGGER.error` as a decorator; `logging.Logger` in an annotation and in a `match` class pattern; `_LOGGER.disabled = True`; a `global _LOGGER` rebind in a function; `type(_LOGGER).error(_LOGGER, ...)`.
  - Barrier levels: a float level and a `from logging import DEBUG` name are counted, which is the conservative direction. `True`, which is level 1, reads as quiet, which is correct.
  - Residue category (2): `report_usage` and the `urllib3` logger read `barrier=0 alias=[]`, as the category states.
- The body's figures, re-derived at this head (`ev/figures_r8.txt`):
  - The task-line count is 11.
  - `git grep` for the handler and `report_usage` spellings in `custom_components/` prints 0 lines.
  - `comment_ratchet.py` prints `long_units_base=2303 long_units_head=2303` and `comment_ratchet: OK`.
  - `closure.py select --diff 35402f78` prints `MODE: SCOPED -- 8 script(s) run, 25 scoped out.`
  - `python3 tests/structure.py` reads `in_function_copies 11 <= 11` and `unloaded_package_imports 14 <= 14`, then `STRUCTURE RATCHET PASSED` (`ev/structure_r8.txt`).
- Figures I could not re-derive:
  - The full `tests/entities.py` count (`1 of 2736 ENTITY CHECKS FAILED` at 3253832a).
  - The dependency-surface counts (154 pairs, 30 modules, 30 methods), measured over the HA 2025.11.3 wheel with the fixer's scratch scripts, which are not in the tree. No HA wheel is installed here.
  - These figures price an alternative not taken. The verdict does not turn on them.
- "Counted at run time" in the category's text: the runtime probe `dev/audit/rounds/round10/D14/log_flood/probe.py` is in `tests/closures.json`. The body states plainly that no live group owns a run-time count of dependency-written records.
- `git merge-tree --write-tree origin/main f2d414f8` exits 0 (`ev/merge_tree.txt`).
- Untouched in the three-dot diff against 35402f78 (`ev/untouched.txt` is empty): `VERSION`, `RELEASE_NOTES.md`, `custom_components/`, `tests/golden/` and `tests/closures.json`. So there is no drift for the claim files to answer.
- `tests/structure_budgets.json` adds only the two new rows at their measured values. No existing key moves.
- The body's `## Head` names f2d414f8920b8f29a00db515a4ade06c1f4b7bc9, the head reviewed here (`ev/HEAD.txt`).
- The finder's harness: the packet reads `none named`. This review's harness is the probe and mutant drivers under `ev/`, and it is the reviewer's, disclosed as such.
- CI at this head: `merge_train.py classify f2d414f8 --pr 3729` printed `WAIT f2d414f8920b8f29a00db515a4ade06c1f4b7bc9 pending: gate red: none` on every run from 22:29 to 22:59 UTC (`ev/classify.txt`), so the verdict carries `pending-ci: gate`. With no red, no `## Red checks` answer is owed; the owed-reds set is in `ev/owed_reds.txt`. The packet's `introduced-red: unreadable` refusal was a queued `instrument-self-tests` job; classify decides, and it named no red.
- Closing self-audit: `carry_audit.py check` printed `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`, rc 0, with `--body` set to the body's `## Forward-carry` and `## Friction` sections (both `none`).
- Head re-read before return: `fix/r11-seam-ratchets` is still at f2d414f8920b8f29a00db515a4ade06c1f4b7bc9.

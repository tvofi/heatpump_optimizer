# R11-RCA-3729-OPEN-AXIS: a claim over a set no rule enumerates gets one block per round

Seat: round-11 root-cause, read-only; countermeasure built by the `rca-open-axis` fixer and
approved by the owner on 2026-11-21 under mandate 6893738184 (scope all). Measured
2026-11-21 at `origin/main` 63c6d1cf, PR #3729 head 55508355, `verdict/3729` 0ade4a59.

## The instance

`verdict/3729` holds six blocked verdicts, all `class-open`, all on `tests/entities.py`
`_r11_logger_aliases`, the fixer's extension of D14-s2-03 (severity low). None found a
defect in shipped code; each verdict calls the seam "a predicate's unguarded domain".

| block | round | head | open | axis |
|---|---|---|---|---|
| 1 | 2 | 5fe13702 | `.log(level=)`, `logging` rebound, `_LOGGER._log`/`.handle`, reflective lookups | spelling |
| 2 | 3 | b950a390 | sibling `_LOGGER` attribute, `'_LOGGER'` string, `warnings.warn`, `exec` | spelling/evaluator |
| 3 | 4 | 8b68ba21 | `builtins.exec`, `getattr(builtins,'exec')`, `__builtins__` | evaluator |
| 4 | 5 (re-cut) | 148254e8 | `typing.get_type_hints`, `ForwardRef`, `inspect.get_annotations(eval_str)`, `pickle.loads` | evaluator |
| 5 | 6 | f2d21754 | asyncio `call_exception_handler` / `default_exception_handler` | dependency entry point |
| 6 | 7 | 55508355 | Home Assistant `helpers.frame.report_usage` | dependency entry point |

Block 1 to block 6: 51.9 h wall clock, mean 10.4 h and median 7.6 h per round
(`git log --format='%cI %s' origin/verdict/3729`).

## Cause

**The claim quantifies over a set no enumerator reads.** It ranges over two axes:

1. **The spellings of package text that reach a logger.** Rounds 2-5 walked it one
   evaluator per round. The round-5 re-cut closed it by rule (the evaluators' own front
   ends, `ast.parse` and `pickletools.genops`, plus computed text as residue). **No block
   since has been on this axis** — the control: an axis closed by a rule stops its run.
2. **The dependency APIs that write a record on the package's behalf.** Enumerated only
   by example (`warnings` refused, `system_log` residue, two asyncio handlers refused, a
   census of one loop class), split by a judgement ("the handler's effect is the record"
   against "a side effect of other work"). Rounds 6 and 7 are its first two members.
   The round-7 reviewer: *"Nothing enumerates the Home Assistant or aiohttp helpers that
   the residue names, so I owe no hunt past this one."*

The axis is also live, not only planted: `git grep -nE
'create_task|create_background_task|ensure_future' custom_components/heatpump_optimizer`
at 63c6d1cf returns 16 lines, and CPython 3.14.7 `Future.__del__` calls
`call_exception_handler` for an unretrieved exception, an ERROR record from text naming
no logger. Refusal by spelling cannot close axis 2 without refusing production code. A
stdlib census of functions whose own body logs at WARNING or above returns 37 in 10
modules on 3.14.7 (direct writers only: a lower bound).

## Process state: (c)

Every step existed and was obeyed: the body named an enumerator (`fixer.md` step 8),
each reviewer reported every seam it found and stopped (`fix-review.md` step 6), a
`## Re-cut` body exists from round 5, and the orchestrator commissioned a bounded-scope
report before round 6. Their **unit** was wrong:

- Steps 8 and 6 test that *a rule exists and its output is dispositioned*, not that
  *every set the claim quantifies over is some rule's output or wholly a stated residue
  category*. `class-rule-missing` fires only when no rule is named: one rule for axis 1
  satisfied it while axis 2 had none.
- On an axis with no enumerator, step 6's "no hunt past it owed" makes one member per
  round the contract-compliant outcome.
- The re-cut escalation's text named `claims` only, so rounds 6 and 7 had no text
  stopping them. `bus.sh dispatch`'s count refuses a re-cut blocked again on any judgement
  class; how those two rounds were dispatched past it was not read.
- The bounded-scope report closed axis 1 and inherited axis 2 as a list.

Prior records: `R10-RCA-CLASS-OPEN.md` (generated corpus, now `fixer.md` step 2) binds
text classifiers only; `R11-RCA-CLASS-OPEN.md`'s recall at the base passes #3729, since
its fixtures recall every prior instance. Neither reaches an axis absent from the claim's
enumerators.

## How far the class reaches

All 1129 `verdict/*` and `archive/verdict/*` refs (2026-10-06 to 2026-11-21, about 46 days):
108 PRs carry a `class-open` block, 11 carry three or more distinct blocked heads, and by
first-line subject 8 of those are static guards over an open reach or spelling set:
#3729 (6), #2697 (6, `gh` merge spellings), #3499 (4, classify readers through alias and
`getattr`), #3049 (3), #3223 (3), #3520 (3), #2345 (3), #2283 (3). That is **31 blocks, 23
repeat rounds**. The subject classification is the RCA seat's reading, not re-verified per
verdict body.

## Cost test

Unit: wall-clock hours per programme day.

- `cost(defect) x P`: 23 repeat rounds in 46 days at `R11-RCA-CLASS-OPEN.md`'s median
  6.2 h from block to next verdict = 142.6 h, **3.1 h/day** (seat time excluded, which
  favours building nothing).
- Removal (estimate, retrospective): each open axis costs at most two blocks under an axis
  block; #3729 four instead of six, the other seven two each: 31 blocks become 18, 13
  rounds x 6.2 h = 80.6 h, **about 1.75 h/day**.
- Standing cost: about 5 min per `class-open` block to classify instance or axis, at
  about 3.4 such blocks a day = **0.28 h/day**; the fixer-side line per quantified set is
  bounded by the same, so 0.28 to 0.56 h/day. Induced work: two role-file clauses (roles
  are not synced into `.mdc`) and one `bus.sh` arm with its self-test.
- **Passes**: positive down to a removal rate of about 16 to 32% of the estimate.

## Countermeasure (narrow; built)

Delete is not possible (steps 8 and 6 are the barrier for missed sites); self-repair is
not (no instrument decides whether a set is enumerable). The rung is narrow:

- `fixer.md` step 8: every set the claim quantifies over is a named rule's output, or
  wholly residue by a category the claim states; a set named by examples is neither.
- `fix-review.md` step 6: a seam of such a set blocks the set once,
  `class-open: axis <set> unenumerated (e.g. <seam>)`, the set's words verbatim in a later
  block.
- `fixer.md` "Past three rounds": a re-cut blocked again, or a second block on one axis at
  any round, goes to the orchestrator to narrow, split or close.
- `bus.sh` `axis_repeat`: `dispatch` refuses when the latest block is an axis block and an
  earlier head was blocked on the same set, unless `--past-three <reason>`; self-test arms
  with null controls (different axes, one head re-posted, a later non-axis block), mutant
  `mut:axisrepeat`.

**Shadow measure.** Over round 12, count PRs with three or more distinct `class-open`
heads (this window: 8 in about 46 days). If the count does not fall, withdraw the clauses.

## For #3729

Close axis 2 by category: restate the claim over the logger bindings and calls spelled in
the shipped tree, with the residue *any record a dependency writes when the package calls
it*. Do not refuse `report_usage` by spelling: the 16 live task-creation sites guarantee
another member on the same axis.

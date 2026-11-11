Plan-page group r10-plan-page-residue: the closure rule, review-stage pricing, 20 slots, and the plan_page render defects the carries name. Closes no issue.

## Head

428aa56b7cdc5ce86f27b34e22498734aa145de3

## Mutation proof

Each predicate was mutated in place and `plan_page.py --self-test` / `replan.py --self-test` run; every mutant fails a named check: sort-key null guard, wave dash guard, strip partial predicate, singular/plural, zero-orphan clause, heading-marker strip, line join (plan_page + roster_lib); in `replan.py` the in-tree mutants `closure-later-of`, `closure-check-later-of`, `live-review-stage` all exit rc=1.

## Null control

A plan with no post-stamp group keeps closure equal to the stamp's `at`; an explicit `--slots 7` keeps 7 with seats at the default; a group at wave N renders `wave N` and `data-wave="N"`; a description with no heading is unchanged; a plan with no part-merged group counts 0; an in-progress group is not priced as in review.

## Figures

- `python3 tools/plan/replan.py --self-test` and `python3 tools/audit/seat/plan_page.py --self-test`: 0 failed.
- Not done: `tools/plan/durations.json` was not re-measured. `replan.py --measure-sizes` fails here (`gh api graphql` is refused in this environment, HTTP 403). Owed to the relay, which has GraphQL, before merge: run `replan.py --measure-sizes --out-durations` at the merge base and commit the output. Carry: R10-PLAN-PAGE-RESIDUE (next part: durations re-measure).
- Carry 1 item 1 (outside tiering): `dispatch_tier` already reads `roster_lib.is_outside` and critical-path membership (existing arms pin it); COMBI-TANK/OUTSIDE-INTAKE rendering tier 3/4 is roster data (`source` unset), not code. Not changed.

Carries (all from the brief): Carry 0 (closure rule, 20 slots; durations owed, above), Carry 1 (items 2, 3, 4, 5 built; item 1 above), Carry 2 (count sentence), Carry 3 (wave and sort-key None), Carry 4 (strip and row share one predicate; heading marker stripped and lines joined), Carry 5 (also read 1-based as Carry 6; items 1 filter and 4 done-row blockers built; item 2 shares Carry 1 item 3's sentence; item 3 hotfix-on-critical-path marking not built; item 5 does not apply, the page template has no html or body open tag). Two further mutants: done-row blocker clear and the partial filter, both kill the self-test. Carry: R10-PLAN-PAGE-RESIDUE (next part: Carry 5 item 3).

## Red checks

none

## Forward-carry

none

## Friction

none

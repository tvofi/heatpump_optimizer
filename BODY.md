Triage batch 140 records 24 rulings, P476 to P499. It answers the owner's question, "does all remaining instrument fixes in the plan pass the 10% bar?", over the 43 live non-absorbed machinery groups on the roster at `b1de33a83a`. It also re-checks the batch 137 and 138 low repairs that were read as an automatic pass.

- **P476 KEEP-REVIEW.** The answer is no. 2 groups keep on a measured gain: HOTFIX-CODEQL-HEADROOM (9 of 19 main python jobs capped) and FLY-STAMP-FLUSH-COST (22.3 % of a day's CI before its merged fix). 36 keep on a skip route (a medium-or-above observed repair, RCA, closeout or owner directive), 6 of them narrowed. 4 hold no unbuilt work and close. R10-SUITE-HOST-DETERMINISM is DEFER-TO-MEASURE. No whole group is dropped.
- **P477 to P487** test each group's pending carries. Many merged PRs built carries that nobody marked: 42 of them. 14 carries are dropped below the bar, and the rest are duplicates or moves.
- **P488 REJECT** reverses P459 (1.8 %). **P489 ACCEPT** upholds P461 on the owner-directive route. **P490 REJECT** reverses P462 (0.49 %).
- **P491 DEFER** SKIP-DEFERRAL-NOT-ENVIRONMENT, second instance: `gate-sweep.yml` has been active again since 07:33Z. **P492 REJECT** REENABLE-CONDITION-UNWATCHED duplicates R10-TICK-LEVELS carry 18. **P493 ACCEPT** TRIAGE-140-NOTE.
- **P494 to P499** re-check batch 137's low ACCEPTs: P439 reversed; P448, P450 and P452 deferred to a measurement; P449 (owner directive) and P455 (P436 barrier) upheld.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`2cca1b1a7d97997a5ea22cea5339ec954afd9111`; one file against origin/main `0a8033305d`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py` (`ruling_verdict`, `triage_refusal`), together with the batch's mark-carry and set-stage ops, copied from origin/main and run against the roster at `b1de33a83a`.
- All 80 held ops apply, and none is refused. Pending carries move as the entries state: R10-PREPR-CAP goes from 16 to 9, and R10-FLOW-TOOLKIT-MODEL from 11 to 1. R10-CARRY-RESIDUE-2, R10-TRAIN-MERGE-LOOP-2, R10-FLY-STAMP-FLUSH-COST, R10-FLY-DISPATCH-RULINGS and R10-FRICTION-OTHER-FAMILY reach `done` with 0 pending.
- A second mark on an already marked carry is refused, and so is an `implemented` mark without a sha.
- `ruling_verdict` reads P488, P492 and P494 as REJECT, P489, P493, P496 and P499 as ACCEPT, and P491 as DEFER.
- The simulated roster passes `node tools/policy/brief_lint.mjs`: `TOTAL: 0 error(s)`. The unmodified roster reads the same.

## Null control

- P500 reads `None` (no such entry).
- The dismissal texts cite "triage batch 140 entry N", and `triage_refusal` returns `None` for them.
- A planted `triage P999` text with no citation is refused.

## Figures

- `git diff --stat 0a8033305d...2cca1b1a7d`: 1 file.
- Every ruling figure is cited beside its command or log in its entry.

## Red checks

`none`. No pull request is opened for a triage record; it rides the stamp.

## Forward-carry

none

## Friction

none

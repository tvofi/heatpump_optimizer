Fix review: blocked 2eee862d2d61b2fe2431c979048360d1b4392cfa class-open: the cards key is unvalidated, so any string makes a group rank 1 and a plan relabelling all 46 rank-2 groups passes objective-check; baseline.record is unconstrained, so the NO-READ refusal is bypassed; the settlement's status choices are unpinned

bus-nonce: 2d310002fec999a397bb0ddf65308a91

Round 1. Reviewed from detached worktrees at the head and at the merge base ada9da5c7bf542b8cdedb2d5fbe878edd1b3a8ae. Contract current (`git diff <merge base>...origin/main -- dev/governance/roles/` empty).

## Block

Each item was measured at the head; commands and output are in `ev/`.

1. **class-open: `cards` (and `escapes`) rank a group 1 on any string.** `derived_rank` returns 1 when `cards`, `escapes` or `classes` is non-empty; only `classes` is checked against a register (`UNKNOWN class`), and `removes` against the judge register (`UNKNOWN finding`). Real run (`ev/attacks.txt`, attack `fake-card`): the fixture plan with every rank-2 group rewritten to `{"rank": 1, "cards": ["NO-SUCH-CARD"]}` and `edges` emptied prints `OBJECTIVE PASS`, rc 0, `dropped 0`. That one edit removes the three refusals keyed to rank 2 (`UNEXAMINED move`, `RANK edge`, the floor reduction) for the whole plan. It is the sibling of the design's planted row "no-finding group claims an unregistered finding id (unexamined)", which is refused. The guide's "Not caught" names an escape's seam, not a card's existence; the body dispositions neither. A source exists in the tree: `tools/audit/check_scopes.py` prints P3's `open_cards`, which `audit-plan.js`'s read step already returns.
2. **class-open: `baseline.record` and `baseline.tree` are the plan's own and unconstrained.** The design note section 3 states the baseline as "the previous round's record under `dev/audit/yardstick/`". `objective_check` reads `_json_at(base.get("tree", ref), base.get("record"))` with no check on the path or on the record's `round`. Real run (`ev/attacks.txt`, attack `doctored-baseline`): a copy of the round-10 record with a `value` on every term, committed beside the plan and named as `baseline.record`, lets all 13 terms predict `hold`: `OBJECTIVE PASS`, rc 0. Against the real record 12 of those 13 are NO-READ and refuse. The "free credit" refusal is bypassed by the object under check choosing its own reference.
3. **The settlement's status choice, a mutation target the design names (section "Harness"), is unpinned on most arms.** The body's 21 mutants all die (`ev/mutants-plan_audit.txt`, b01 to b21; b21 by TypeError as disclosed). The in-tree driver over every added line (`mutant_run.py --diff ada9da5c...HEAD --max-mutants 2000 --in-place`, `ev/mutant_run-diff-full.txt`) and my own spec (`ev/driver-mut.py`, r01 to r29) report these survivors in `settle`, `moved` and `check_block`, the self-test's own lines and the command-line layer set aside:
   - `tools/audit/seat/plan_audit.py:778` (reviewer r20): a term predicted `up`/`down` that moved the other way settles HELD under `line(key, "HELD", ...)`. The perturbation arm does not catch it: the flipped line still differs, by its `detail` text, so `len(diff) == 1` holds with the status wrong.
   - `:779`, `:780` (GUARD_OFF, CALL_DEL, reviewer r10): `hold` predicted and the term moved the worse way; no arm predicts `hold` on a read term.
   - `:742` (GUARD_OFF, CONST_SWAP, reviewer r27), `:745`, `:748`, `:749` (STMT_DEL, reviewer r12 `seen = True`): the `examined_by` line's HELD, MISSED and UNDECIDED.
   - `:754`, `:756` (CALL_DEL): the `escapes` and `classes` keys never reach `next_round` in any arm; only `injected` is driven.
   - `:759`, `:760` (GUARD_OFF, RETURN_DEL): the next-round settlement returning before the term lines.
   - `:772`, `:773`, `:774`, `:782`: the UNDECIDED lines for an unread band and an `undecided` prediction.
   - `:673` (CONST_SWAP), `:690`, `:693` (CONST_SWAP, reviewer r26 `width = 0`), `:695`, `:696`, `:698`: the band widths and the integer-count band; `:718` (CONST_SWAP).
   - `:620` (GUARD_OFF) and `:642` (GUARD_OFF, reviewer r18), reviewer r19 (`(entries.get(waits) or {}).get("rank") == 2` to `True`): the rank-edge loop's own guards.
   - reviewer r29 (`kept_in_floor`: `if rank == 1:` to `if True:`): the reduced-roster filter, the design's other named target, keeps a rank-2 group only another rank-2 group reaches; the fixture has no rank-2 to rank-2 edge.
   - reviewer r24 (`if name in production and`) and r28 (`if group in production:`): lead time over production groups only, and the `injected` line for production groups only; the fixture's percentiles are the same with and without the filter.
   - `.claude/workflows/audit-plan.js`, reviewer m3 (`ev/mutants-audit-plan-js.txt`): `'objective'` dropped from the moves schema's `required` leaves `254 passed, 0 failed`.
   The body's "No `## Unpinned sites` entry is owed" rests on `prepr.sh` step 6d's first 40 mutants, which end before `settle`.
4. **A ranked done group makes `replan.py` refuse projection B** (`ev/realrun-done-ranked.txt`). `kept_in_floor` reads reachability off projection A's `after`, and A omits a done predecessor: with `R10-COP-LEARNER-DRAW-FLOOR` (done) ranked 2 and `R10-DRAW-MAP-EVIDENCE` ranked 1, B drops the first while the roster entry of the second still names it: `replan.py refused (rc=2): ... after-edge names no group`. Fail-closed, but the refusal names no rule; the guide says a done group "is kept unranked" and nothing refuses a rank on one.

## Evidence

- RESULT self-test at the head: `plan_audit self-test: 76 checks, 0 failed`; at the merge base `27 checks, 0 failed` and `objective-check` is argparse's "invalid choice" (`ev/selftest-head.txt`, `ev/base.txt`).
- RESULT `node tools/policy/check-wave-script.mjs`: `254 passed, 0 failed` at the head, `249 passed, 0 failed` at the merge base, and the base's grader over the head's workflow `249 passed, 0 failed` (`ev/wave-head.txt`, `ev/mutants-audit-plan-js.txt`). Both body mutants of `audit-plan.js` print `253 passed, 1 failed` on the named arm.
- RESULT `policy_lint.mjs --budgets`: `architect-planner.md` 89/89 lines, 1325/1325 words; `plan-review.md` 27/27, 360/360 (`ev/budgets-head.txt`). The raise equals the added text and leaves no headroom; `tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- RESULT real run on my own fixture (the builder's is out of tree, so its 96.13 h, 26.8/83.83 h, 139.94 h and 1.645 s figures are not re-derived): the head plus the roster at `origin/handoff/audit-r10-roster` cfafa28d3edf8169db080d1cccd7970e3fa8bf41, 48 open groups, 2 rank 1 by a fixture card. `--write`, then the check at the commit holding the record: `projection A: critical path 88.7 h, wall 90.7 h`, `floor cost ... dropped 43`, `OBJECTIVE PASS`, rc 0 (`ev/realrun-pass.txt`). Edges deleted, one pin character edited and an authored `hours` key each print their named FAIL, rc 1 (`ev/attacks.txt`).
- A `durations_blob` that is not the plan SHA's `tools/plan/durations.json` is accepted; my doctored sizes did not move the hours, so no effect is shown.
- The command-line layer (`objective_check`, `run_projections`, `production_groups`, `objective_settle`, lines 798 to 919 and 1375 to 1423) is run by no in-tree check, as the design's "one real run, outside the self-test" allows; the driver's survivors there and on the self-test's own lines are in `ev/mutant_run-diff-full.txt` (188 SURVIVED lines in all).
- `VERSION`, `custom_components/`, `RELEASE_NOTES.md` and `tests/golden/` are untouched by the three-dot diff; no claim file moves.
- `git merge-tree --write-tree origin/main <head>` exits 0 at origin/main 69053da4f99c4e90952f6947c169aa6e96129dc6 (`ev/merge-tree.txt`).
- The body's head line names 2eee862d2d61b2fe2431c979048360d1b4392cfa, the head measured; `git ls-remote` read it again before this verdict (`ev/head-readback.txt`).
- Architecture score and the entity count are CI's (`arch-score / arch-score` and `tests / fast (3.14)` success at this head), not re-run.

## Red checks

- `merge_train.py classify --pr 3703` at the head: `APPROVAL-OWED 2eee862d2d61b2fe2431c979048360d1b4392cfa 4 budget raise(s), first .claude/workflows/policy_budgets.json: files.dev/governance/roles/architect-planner.md: 85 -> 89 (a cap went up): a raise is the owner's (0013): no decisive review by tvofi (id 70032254) on this pull request`, rc 4 (`ev/classify.txt`). `gate` and `budget-raise-gate / budget-raise-gate` are red only on that; the body answers it.
- `governance / instrument-self-tests` and `tests / nightly-status` are red and outside the `owed-reds` set; classify prints no INTRODUCED line.

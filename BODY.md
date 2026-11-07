# r10-ci-grader-batch-study (probe, head a37c58e5)

**Recommendation: do not build.** Under any safe rule I could measure, 0 to 2 of the 24 distinct grader entries that merged in the window could have shared a batch proof, so the saving is about zero.

## What I could and could not measure
- The train log (the "85 serial routings", "73 grader") lives on the train runner. It is not in the tree, on any ref, or in this container. I did NOT reproduce the 73 or the 71 recarries, and the minutes below are not measured from that log.
- What I measured is merge history. Window 2026-11-05 13:26Z to 2026-11-07 13:26Z: 60 first-parent commits on origin/main, 52 of them "Merge pull request". Each was classified with `merge_fastpath.file_class` and `grader_specs` read from HEAD's workflows (56 restore pathspecs, 159 tracked grader files).
- Result: 24 PRs touch a grader, 6 a workflow, 4 a budget, 3 a claim, and 24 none. Only **24 distinct grader entries merged against 73 logged grader routings**, about 3 routings per entry. Most of the routings are therefore re-routings of the same entries (recarries and retries after main moved). Batching would not remove those.
- Grader files most often touched: tests/entities.py (5), bus.sh, tools/ci/gate.py (3 each), then many files touched once or twice.

## Proposed rule (the strictest safe one)
A grader-touching entry may join a batch only if all of these hold:
1. It has no workflow, claim, budget or bot-head class.
2. It touches no *universal* grader: tests/entities.py, tools/ci/gate.py, tools/ci/prelude.py, tools/ci/codescan_wait.py, tests/gate_lock.py, tools/coverage/coverage_tree.sh. These grade the whole tree.
3. Every grader it touches has a measured footprint. The footprint is the union of `tests/closures.json` closures that contain the grader, plus those scripts. A grader that appears in no closure has no measured footprint and counts as universal (strict variant).
4. No other entry in the batch changes a file inside that footprint, and (reverse check) no other grader entry's footprint holds this entry's files.

Null control: entry A changes a grader and entry B is graded by it. B's files fall in A's footprint, so rule 4 refuses the pair and both stay serial.

## Replay against merged history (consecutive merges grouped by N)
| N | variant | grader entries | would batch | refused: other class / universal or unmeasured / graded by another entry |
|---|---|---|---|---|
| 2 | strict | 24 | 1 | 5 / 13 / 5 |
| 2 | lenient (unmeasured = self only) | 24 | 2 | 5 / 7 / 10 |
| 3 | strict | 24 | 0 | 5 / 13 / 6 |
| 3 | lenient | 24 | 1 | 5 / 7 / 11 |
| 4 | strict | 24 | 0 | 5 / 13 / 6 |
| 4 | lenient | 24 | 0 | 5 / 7 / 12 |

At the assumed batch size of 4, **0 of 24 (0%)** would batch. The best case, pairs under the lenient variant, is 2 of 24 (8%).
- Savings at 98 runner-minutes per entry: 0 min/day at N=4, and at most about 2 x 98 / 2 days ≈ 98 min/day at N=2 lenient. That is far below the 2,600 estimate, which assumed all 73 batch.
- The replay can only be self-consistent. I found no batch the rule would have judged wrongly because it refuses whenever a footprint overlaps. I did not check main's CI outcome for the merged batches, so "no wrongly judged batch" means only that the rule is consistent with the footprint data.
- Batch grouping by consecutive merges is my assumption, because the real batch composition sits in the missing log.

## Why so little batches
- Over half of the grader entries (13 of 24) touch a universal or unmeasured grader.
- The footprint of the rest (the closures of tests that use the grader) overlaps files that other PRs in the same window change. The shared files are not diagnosed here; I ran out of inline-search budget.
- Closure measurement is coarse: a grader in a closure grades every file in that closure.

## Cases the rule must refuse (any build would keep these serial)
- Any entry with a workflow, claim, budget or bot-head class.
- Any entry touching tests/entities.py, gate.py, prelude.py, codescan_wait.py, gate_lock.py or coverage_tree.sh.
- Any pair where one entry changes a grader and the other's files are in that grader's closure (the null control above).
- Any grader with no measured closure, under the strict variant.

## Reasons not to build
- The measured eligible share is 0 to 8% of grader entries, not the roughly 100% the 2,600 min/day estimate needs.
- The 73-to-24 gap says the cost is re-routing, not missing batching. A better lever is probably cutting recarries (main moving under a settled head), which this study did not examine.
- A build would add a footprint rule that must stay in step with closures.json, for a saving of at most about 100 min/day.
- If the owner wants a firmer number, first export the train log (the runner's `serial:` and `recarry` lines) and rerun this replay on real batch compositions. That is the one measurement this probe could not make.

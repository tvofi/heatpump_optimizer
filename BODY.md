The merge-main bot (`tools/pr/merge_main_bot.py`, run by `.github/workflows/merge-main.yml` on every push to main) re-merged main into #2282 twice while its mutation pin chain was still running. At 532eb85d3 the check-runs API shows `mutation-pins (2)` and `mutation-autofix` concluding `cancelled` at 18:17:23Z, the moment of the bot's push. The chain takes about two hours, so on a busy main it never finishes. This is the "main moved" problem of #2266 seen from the pull request's side. It lands as its own pull request in group R10-TICK-TRAIN, split from the train change because the mechanism and the file class differ.

The bot now leaves a head alone while any pin-chain job is still queued or running there: `mutation`, `mutation-pin-plan`, `mutation-pins (*)` or `mutation-autofix`. The status is `skip-pins-running <jobs>`. If the chain cannot be read, the status is `skip-pins-unread` (fail closed). The first push to main after the chain settles merges the head as before. The chain is read from the Actions runs at the head sha and their jobs. The job's existing `actions: write` grant covers that read, so the workflow does not change. The read happens only for a head that every existing condition would already merge. Every existing guard decides first and is unchanged.

**Design: defer rather than carry.** Carrying the pin result from h0 to the main-only merge h, the way approval-carry does, was rejected. An approval judges the branch's own content, and a main-only delta does not touch that. A mutant kill is different: it is a property of the whole tree, main's half included. Main's commits can change the tests that kill a mutant, and they can shift the lines the written pins anchor to (the line-pinned `mutation_budgets.json` and `carry-*.json` class). So a pin measured at h0 is not a measurement of h. Deferral adds no new trust. Its cost: a DIRTY head stays DIRTY until the chain ends, which the jobs' own `timeout-minutes` (350 for `mutation-pins`) bounds, plus the wait for the next push to main.

Part of #2266.

## Head

`8c9da374f1eccd662960165e5490ed8ce988de9d`, on main `8747bbfc4d46` (2026-10-15T19:54Z).

## Mutation proof

The arms were written first. Against the unmodified bot they raised `TypeError: decide() got an unexpected keyword argument 'pins'`. Each mutant below was killed by `python3 tools/pr/merge_main_bot.py --self-test`:

- `if pins:` -> `if False:`: 2 FAIL, `decide: a mergeable-by-driver head whose pin chain still runs is left alone` and `the same head with its pin chain running is not merged (plan_one asks the chain)`.
- `if pins is None:` -> `if False:`: 1 FAIL, `decide: a pin-chain read that failed is left alone too (fail closed)`.
- `if run_.get("status") == "completed":` -> `if False:`: 1 FAIL, `pins_running names the pin-chain jobs of a run still in progress at the head, and no other job (a completed run's jobs are not read)`.
- `and j.get("status") != "completed"` deleted: 1 FAIL, the same `pins_running` arm.
- `if status == "merge":` (plan_one's chain read) -> `if False:`: 1 FAIL, `the same head with its pin chain running is not merged (plan_one asks the chain)`.

## Null control

`decide(**base, pins=[])` is `merge`: a settled chain merges as before. A clean head is `skip-not-dirty` with pins running or not: the earlier refusals decide first. `plan_one` on a head already containing main never reads the chain; the arm's `pins` callable raises if it is called.

## Figures

- `python3 tools/pr/merge_main_bot.py --self-test`: `merge_main_bot self-test: 33 checks, 0 failed` at the head. The 31 arms that existed before are unchanged.
- `python3 tests/closure.py select --diff 8747bbfc4d46`: `MODE: SCOPED -- 0 script(s) run`. `governance.yml` runs this self-test.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- `python3 tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- `gh api repos/tvofi/heatpump_optimizer/commits/532eb85d3/check-runs`: at 532eb85d3, `mutation-pins (2)` and `mutation-autofix` are `cancelled` at 18:17:23Z. The other five shards concluded `success` between 16:46 and 17:54Z.

## Red checks

none

## Unpinned sites

Every new predicate is pinned by a value check in the self-test (the five mutants above). `mutation-autofix` pins any killed mutant the gate reports.

## Forward-carry

none. The sibling train change (`handoff/r10-tick-train`) answers the train's side of the same problem.

## Friction

none

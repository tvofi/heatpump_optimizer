The merge-main bot (`tools/pr/merge_main_bot.py`, run by `.github/workflows/merge-main.yml` on every push to main) re-merged main into #2282 twice while its mutation pin chain was still running. At 532eb85d3 the check-runs API shows `mutation-pins (2)` and `mutation-autofix` concluding `cancelled` at 18:17:23Z, the moment of the bot's push. The chain takes about two hours, so on a busy main it never finishes. This is the "main moved" problem of #2266 seen from the pull request's side. It lands as its own pull request in group R10-TICK-TRAIN, split from the train change because the mechanism and the file class differ.

The bot now leaves a head alone while any pin-chain job is still queued or running there: `mutation`, `mutation-pin-plan`, `mutation-pins (*)` or `mutation-autofix`. The status is `skip-pins-running <jobs>`. If the chain cannot be read, the status is `skip-pins-unread` (fail closed). The first push to main after the chain settles merges the head as before. The chain is read from the Actions runs at the head sha, every page of them, and their jobs. The job's existing `actions: write` grant covers that read, so the workflow does not change. The read happens only for a head that every existing condition would already merge. Every existing guard decides first and is unchanged. `run()`'s per-pull-request step is now `plan_pr`, the one production caller of the pin read. `plan_one` without a read fails closed: its default is an unread chain. `PIN_CHAIN` is tied to `tests.yml`'s job ids by an arm, so renaming a job, or giving one a `name:` override, reddens the self-test instead of silently disabling the guard.

**Design: defer rather than carry.** Carrying the pin result from h0 to the main-only merge h, the way approval-carry does, was rejected. An approval judges the branch's own content, and a main-only delta does not touch that. A mutant kill is different: it is a property of the whole tree, main's half included. Main's commits can change the tests that kill a mutant, and they can shift the lines the written pins anchor to (the line-pinned `mutation_budgets.json` and `carry-*.json` class). So a pin measured at h0 is not a measurement of h. Deferral adds no new trust. Its cost: a DIRTY head stays DIRTY until the chain ends and then until the next push to main or a dispatch. The chain's own timeouts sum to `mutation` 160 + `mutation-pin-plan` 5 + `mutation-pins` 350 + `mutation-autofix` 10 minutes, plus queue time. In a quiet period nothing re-triggers the bot, so the head stays DIRTY until main moves. Residual: GitHub lists a job only once its `needs` are met, so between one stage concluding and the next being created there are seconds in which no chain job is listed, and a push in that window still cancels the chain.

Part of #2266.

## Head

`4792a3d14df943c588a3a374ae5fbf8590bf01c6` merges the authored code head `0c439ce78f6a1c9cc6908549dad7faf827ad0cad` and then merges origin/main `39b77a467` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`0c439ce78f6a1c9cc6908549dad7faf827ad0cad`: round 2 on the PR head `1c385e456`, whose main is `323fc7c48` (2026-10-15T21:0xZ).

## Mutation proof

Round 1's arms were written first. Against the unmodified bot they raised `TypeError: decide() got an unexpected keyword argument 'pins'`. Each mutant below was applied in place, run through `python3 tools/pr/merge_main_bot.py --self-test`, and restored. All 12 were killed:

- `if pins:` -> `if False:`: 2 FAIL (`decide: a mergeable-by-driver head whose pin chain still runs is left alone`, `the same head with its pin chain running is not merged (plan_one asks the chain)`).
- `if pins is None:` -> `if False:`: 1 FAIL (`decide: a pin-chain read that failed is left alone too (fail closed)`).
- `if run_.get("status") == "completed":` -> `if False:`: 1 FAIL (`pins_running names the pin-chain jobs of a run still in progress ...`).
- `and j.get("status") != "completed"` deleted: 1 FAIL (the same arm).
- `if status == "merge":` -> `if False:`: 1 FAIL (`the same head with its pin chain running is not merged`).
- Round 2, the reviewer's survivors and the new arms:
  - M11, `plan_pr`'s `pins=` read deleted: 3 FAIL (`plan_pr (run()'s per-PR step) reads the head's pin chain`, its null control, the paging arm). All three read `skip-pins-unread`, never merge.
  - M11b, `plan_one`'s default back to `lambda: []`: 1 FAIL (`plan_one with no pin read passed fails CLOSED`).
  - M9, `mutation-pin-plan` dropped from `PIN_CHAIN`: 2 FAIL (`while mutation-pin-plan runs it is the ONLY chain job listed`, `PIN_CHAIN matches exactly tests.yml's four pin-chain jobs`).
  - M16, `TypeError` dropped from the except: rc 1. The `a malformed runs page (no list) is unread` arm raises an uncaught `TypeError`, so this mutant is killed by a crash, not by a named FAIL line.
  - M18, runs read on page 1 only: 1 FAIL (`the runs read pages past the first 100 runs`).
  - M19, `mutation-pin-plan:` renamed in `tests.yml`: 1 FAIL (`PIN_CHAIN matches exactly ...`).
  - M20, a job-level `name:` added to `mutation-pins` in `tests.yml`: 1 FAIL (the same arm).

## Null control

`decide(**base, pins=[])` is `merge`. `plan_pr` with every chain job completed is `merge`. A clean head is `skip-not-dirty`, pins or not, because the earlier refusals decide first. `plan_one` on a head already containing main never reads the chain: the arm's callable raises if it is called.

## Figures

- `python3 tools/pr/merge_main_bot.py --self-test`: `merge_main_bot self-test: 40 checks, 0 failed` at the head. The base had 24.
- `python3 tests/closure.py select --diff 323fc7c48`: `MODE: SCOPED -- 0 script(s) run`. `governance.yml` runs this self-test.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- `gh api repos/tvofi/heatpump_optimizer/commits/532eb85d3/check-runs`: at 532eb85d3, `mutation-pins (2)` and `mutation-autofix` are `cancelled` at 18:17:23Z.

## Red checks

none at round 1's head; round 2 is not yet measured by CI.

## Unpinned sites

The twelve sites above are each killed by a named arm, apart from M16, which is killed by a crash. That covers the sites I mutated, not every line of the diff. The gate's own mutation pass and `mutation-autofix` cover the rest.

## Forward-carry

none. The sibling train change (`handoff/r10-tick-train`) answers the train's side of the same problem.

## Friction

none

Fix review: blocked fd973e035d6044ac55a105a7156af5b46ce5838f semantic-conflict: the merge of main makes governance / instrument-self-tests red; the new topic_grammar step is ungated under main's selftest_scope

bus-nonce: 569d8518b37bf7b3ab928471152b63e3

## Block

The head's merge of origin/main has no textual conflict, but it combines two changes that break each other. Main brought in `tools/ci/selftest_scope.py` and `tools/ci/selftest_closures.json` (R10-CI-SELFTEST-SCOPE, between `1c29e5ab7` and `806e952ca`). That code requires every instrument-self-tests step to have an `id:` and an `if:` that reads `steps.scope.outputs.<id>`. This branch's governance.yml step "Show the topic grammar refusing a bare number and a prefix as family members" has no id and is gated only on `!cancelled()`.

- CI at this head: `governance / instrument-self-tests` (check-run 129104657944, run 42600800913) fails with `FAIL the live job parses (115 steps) and its gating is consistent` / `selftest_scope self-test: 90 checks, 1 failed`.
- Reproduced here: `python3 tools/ci/selftest_scope.py --self-test` at this head gives 90 checks, 1 failed. At origin/main `f365ce757` and at the merge base `806e952ca` it gives 90 checks, 0 failed. `wiring_gaps` at the head returns exactly `UNGATED step 'Show the topic grammar refusing a bare number and a prefix as family members'`, and `selftest_scope.py static` reports 1 problem (ev/selftest_scope_*.txt, ev/wiring_gaps_head.txt).
- The context is not in `gate_required` (ev/required_contexts.txt), so `merge_train.py classify` reads GREEN and the gate is green. But the job runs on pushes to main (only product-only PRs skip it). Merging this head would turn main's instrument-self-tests red, and that red would belong to this PR.
- The body's `## Red checks` says `governance / instrument-self-tests` was "repaired at the previous head". At this head that is no longer true, and the body does not name this new cause.

Repair: I probed this in a scratch worktree only; nothing was pushed. Adding `id: topic-grammar` and `if: ${{ !cancelled() && steps.scope.outputs.topic-grammar == 'true' }}` makes the self-test pass (90 checks, 0 failed). `static` then reports one remaining STALE line: `tools/ci/selftest_closures.json` lacks `topic-grammar`, re-record with `python3 tools/ci/selftest_scope.py record --step topic-grammar`. That command needs strace, on Linux. The launcher may also need a `sel topic-grammar` arm if the step is meant to run in the background; the fixer should check how the other gated foreground steps are wired (ev/repair_probe.txt). After the repair, the fixer should re-run steps 2-8 and update the body's Red checks entry.

## Findings

none

## Evidence

- Round: this PR has been verdicted before. The previous verdict, at `1c29e5ab7733d9c72d1773b649c97291b8b5dfb2`, was blocked ci-pending only. This review covers the resolution delta from `1c29e5ab` to `fd973e03`; `review_carry.py` prints FRESH-REVIEW (632b3764 is not an automatic merge).
- Head: `fd973e035d6044ac55a105a7156af5b46ce5838f` is the PR head (pull request read and `refs/pull/3345/head`) and the head the body names in `## Head`. Its merge base with origin/main is `806e952ca`. origin/main has since moved to `f365ce757`.
- Merges with main: `git merge-tree --write-tree origin/main fd973e03` exits 0 (tree `52188550a`), with no conflict.
- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Resolution delta, merge by merge. I compared each merge's tree with `git merge-tree --write-tree` of its parents:
  - `f3633ad2a` (1c29e5ab + main 79b7356f3): the only hand-resolved hunks are `.claude/workflows/audit-find.js` (FINDING-SCHEMA block lines 184-185, CLASS_GUESS and FINDING_REPORT) and `dev/audit/config/finding.schema.json` (the class_guess enum line). `dev/audit/config/bugclasses.json` was resolved by the driver (`LEDGER-MERGE: resolved`).
  - `632b37641`: its tree equals `f3633ad2a`'s. The automatic merge would have added `BLOCKED.md`; `-s ours` dropped it, as the body says.
  - `0b8d0c2b4` and `fd973e035`: their trees equal the automatic merge of their parents, so neither has a hand-resolved hunk.
- Both parents' clauses are present (ev/union.txt). I compared JSON leaves against the merge base of the two parents:
  - bugclasses.json: the branch added 31 leaves and main added 44. None is missing, and no head leaf is absent from both parents.
  - finding.schema.json: each side added 1 leaf (`R10-TOPIC-FAMILY` and `N-relay-handoff-starvation`). Neither is missing, and nothing extra was added.
  - audit-find.js CLASS_GUESS: the branch added `R10-TOPIC-FAMILY` and main added `N-relay-handoff-starvation`. Nothing is missing or extra.
  - `fold_ledger.py check`: 0 violations. `fold_ledger.py --self-test` passes.
- Scoped gate: `tests/closure.py select --diff 806e952ca` prints `MODE: FULL -- every test script runs` (`tests/closure.py changes the gate itself`). The suite is CI's and I did not re-run it. CI's `gate` (check-run 129126185452) reads success.
- Self-tests at this head (ev/cheap.txt):
  - `tests/structure.py`: STRUCTURE RATCHET PASSED.
  - orchestrator_tick 297/0, topic_grammar ok, owed_unactioned 57/0, open_driver 79/0, pr_cap 22/0, cloud_dispatch 132/0, ledger 102/0, cloud_relay 397/0, roster_queue 62/0.
  - `tests/closure.py selftest`: ALL 118 closure shrink pins PASSED.
- The body's figures say each self-test "exits 0, 0 failed" without giving counts, so there are no counts to re-derive. The counts above are my own.
- Mutation pins re-taken at this head, where main moved their files (ev/mutants_head.txt). Each mutant matched once and the tree was restored clean:
  - Mutant A (the fixer's BLOCKED.md clause) fails "the fixer is told to push BLOCKED.md with a Question line before stopping on a question" (132 checks, 1 failed).
  - Mutant B (the reviewer's "never on a head ... merges cleanly" clause) fails "the reviewer blocks on main only for a merge-tree conflict, never a clean head behind main" (132 checks, 1 failed).
  - Deleting the `handoff-wip/` blocked-stop arm makes ledger's self-test exit 2 with `refused: 'refs/heads/handoff-wip/x' matches no ledger arm`.
  - The closure.py `INERT_EXCEPT` pin was not re-taken. Its entry (line 626) is untouched by main's delta, which is the body's own reasoning.
- VERSION, the manifest, RELEASE_NOTES and both claim files are untouched in the three-dot diff (ev/untouched.txt).
- CI: `merge_train.py classify fd973e03 --pr 3345` exited 0: `GREEN ... pending: none red: none` (ev/classify1.txt). Non-required reds at this head:
  - `governance / instrument-self-tests`: the block above.
  - `governance / delivery-status`: not this PR's (defect-root-cause.md).
- Review packet: rendered with refusal `hot-file: #3326 holds an unboarded merge verdict and shares tools/audit/seat/orchestrator_tick.py`, with the advisory that HPO_BUS_TRAIN_STATE is unset. It is the train's concern and not a defect of this head. The packet's carry_audit reads 4 routed, 0 unrouted, and figure_lint reads 19 resolved, 0 not verified.
- CI was re-read with a second `merge_train.py classify` run, more than 60 s after the first, and again read GREEN, `red: none` (ev/classify2.txt).
- I did not get a local result for `tests/entities.py` (`PYTHONPATH=tests/hastub`): it hit this seat's own 230 s timeout (rc=124; ev/entities.txt holds the partial log). Its result is cited from CI's green `tests / closures` and `gate` instead.
- Head re-read before return: `refs/pull/3345/head` is still `fd973e035d6044ac55a105a7156af5b46ce5838f` (ev/head_at_post.txt).

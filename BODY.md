R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3, part 1 of 2 (topic r11-outside-contributor-cycle-p3): the outside contract (decision 0017, `tools/pr/outside.py`) is asked on every path that merges a fork head, and only from origin/main's copy.

Carry 4 (merge_pr.sh app mode merged a cross-repository head without the contract): `gates` now reads whose head it is in both modes; app mode on a fork head merges only where outside.py's `check` at origin/main admits that exact head (`outside_contract`), its refusal printed before anything posts. Carry 5 (`Train.fork_head` executed the checkout's outside.py before comparing it): `fork_head` calls `outside_is_mains((OUTSIDE_PATH,))` before the read, so a stale copy answering "ours" stops there. Carry 6 (`Train.land` asked the contract only when the base is main): a fork head is put to `outside_contract` on a `batch/` base too, where the contract's base rule refuses it. Step 8's sibling seam, built: merge_pr.sh executed its checkout's outside.py uncompared as well, and now applies the train's rule, reading the train's `OUTSIDE_MAIN_COPIES` (no second list). Carry 0 (the interface between the parts): part 2 landed after part 1 and already calls the real `pull_facts`, `cross_repository` and `check`, driven by the train's "the real outside.py" cases; this part adds merge_pr.sh's pin binding each call it makes on the real module, and re-ran the three self-tests (Figures). Carry 1: `tools/ci/selftest_closures.json` re-recorded for merge-train, pr-merger and outside-contract. Carry 3: the four instrument guides carry `--head-repo`, the `[OUTSIDE]` class, the fork-head fetch sentence and this part's merge paths; decision 0017's text is the owner's and is not edited here. Carry 2, the live checks on a test fork, is not run: Forward-carry.

Alternatives: merge_pr.sh could refuse every fork head and route it to the train (decision 0017 gives the merge to the train), which removes its contract call; not taken, because this part's brief names merge_pr.sh app mode as a path that asks the contract. Comparing only outside.py before the contract in merge_pr.sh would leave the contract's other program inputs (policy_lint.mjs's policy set, closure.py's gate files, the mandate gate) a stale checkout's, which the train refuses; the train's list is read instead.

## Head

0e21330c6488f91041fc82b5f5db29dea16efad2, measured at origin/main b3831ff64eca1936f0b618193ee86c3e337b51a9, 2026-11-15T13:59:21Z.

## Mutation proof

Each line deleted or weakened alone, the self-test re-run, restored:
- `merge_train.py` `fork_head`'s `self.outside_is_mains((OUTSIDE_PATH,))` replaced by `pass`: `merge_train self-test: 825 checks, 3 failed`, `FAIL fork head: a checkout whose tools/pr/outside.py is not origin/main's blob stops before that copy is executed, on a head of ours too, and nothing is approved`, the same `on a head a fork's too`, and `FAIL fork head null control: a head of ours read from main's outside.py is ours, whatever another of the contract's copies says ...`.
- `land`'s `if fork is not None and not self.real:` to `if False:`: 1 failed, `FAIL fork head on a batch/ base: the outside contract is asked before the pinned merge, and its refusal parks the entry [OUTSIDE] naming the fork, nothing merged`.
- `merge_pr.sh` `gates`' `CONTRACT_WHY=$(outside_contract ...)` line replaced by `:`: `merge_pr self-test: 50 checks, 4 failed`, among them `FAIL app mode on a cross-repository head the outside contract refuses refuses with outside.py's reason (decision 0017)` and `FAIL app mode end to end: a fork head the contract refuses posts nothing and merges nothing (merged deadbeef)`.
- `outside_contract`'s admission predicate without `f" at {sha}: " in`: 1 failed, `FAIL app mode on a cross-repository head the contract admits at ANOTHER head refuses, naming both`.
- `HEAD_WHY=$(outside_is_mains outside)` replaced by `:`: 4 failed, `FAIL app mode with a checkout whose outside.py is not origin/main's refuses before executing it, on a head of ours` and its owner-mode twin, each with `... having read no pull request`.
- `CONTRACT_WHY=$(outside_is_mains contract)` replaced by `:`: 2 failed, `FAIL app mode on a fork head refuses when a file the contract reads is not origin/main's, though the contract would admit`.
- `outside_is_mains`'s `&& [ "$want" = "$have" ]` deleted: 6 failed (the three cases above).

## Null control

At the merge base the new train cases read: the two stale-copy cases and the batch-base fork case FAIL (`merge_train self-test: 825 checks, 4 failed`, the fourth the read-order null control, which needs the fetch before the read); the batch-base head of ours passes (merged, contract never asked). merge_pr.sh at the merge base with the new cases: app mode on a fork head the contract refuses exits 0 and the end-to-end flow prints `merged deadbeef` (6 failed); app mode on a head of ours, and with a contract admitting this head, pass at both ends. A renamed `check` (`sed 's/^def check(/def check_renamed(/'` on a copy) makes the signature pin's own read exit 1 (`AttributeError: module 'outside' has no attribute 'check'`).

## Unpinned sites

`prepr.sh` with `MUTANT_CMD="python3 -I tools/audit/seat/merge_train.py --self-test"` printed 10 `SURVIVED` lines on the diff's added lines, each disposed:
- `queue_pre_flight.py:341` GUARD_OFF and CONST_SWAP (`argv[:3]`), `:342` RETURN_DEL and CONST_SWAP (`return 1`): drawn under the train's self-test, which does not run this fixture. Each re-run alone under `python3 tools/audit/seat/queue_pre_flight.py --self-test` fails `FAIL a policy head with no review yet passes under the train's --mandate in force for policy merging ...` and the mandate null controls: killed by the file's own self-test (`carry-check-and-the`).
- `merge_train.py:6366`, `:6372`, `:6381`, `:6387` STMT_DEL: each deletes one of this diff's own `check(...)` calls in the self-test; no production line moves, and each production predicate those checks pin is killed above (Mutation proof).
- `merge_train.py:6375` CMP_BOUND (`<` to `<=`): the two indices are of two different calls in one list, never equal, so the mutant is equivalent.
- `merge_train.py:6385` CONST_SWAP (`(False, "never asked")` to `(True, ...)`): the null control asserts the stub is never asked, so its answer is never read; equivalent.

## Figures

<!-- figure-block: scope-line mb=b3831ff64eca1936f0b618193ee86c3e337b51a9 head=0e21330c6488f91041fc82b5f5db29dea16efad2 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- Self-tests at the head: `python3 -I tools/audit/seat/merge_train.py --self-test` ends `merge_train self-test: 825 checks, 0 failed`; `bash tools/audit/seat/merge_pr.sh --self-test` ends `merge_pr self-test: 50 checks, 0 failed`; `python3 -I tools/pr/outside.py --self-test` ends `outside self-test: 266 checks, 0 failed`.
- `python3 tools/audit/seat/queue_pre_flight.py --self-test` ends `queue_pre_flight self-test: 57 checks, 0 failed`; before its fixture answered `git hash-object` (the new comparison in `fork_head`, which its pulls read reaches) its five mandated-policy cases failed, the red `prepr.sh`'s CI predict named on `instrument-self-tests` (`carry-check-and-the`), repaired before the handoff. `python3 -I tools/audit/carry_audit.py --self-test` ends `carry_audit self-test: 449 checks, 0 failed`.
- Seams, by `git grep -n "outside\.py" -- '*.sh' '*.py' '*.mjs' '*.yml' '*.js'` less outside.py's own lines, every site that executes it: `bus.sh adopt` (main's copy from a throwaway checkout, already guarded by its `MAIN-COPY-RAN` case); `policy_lint.mjs` in pr-contract (the base's restored copy, by design); governance.yml's `outside-contract` step (its own self-test, no gate); `merge_train.py` `_outside_gate` (closed in this diff); `merge_pr.sh` `head_is_ours` and `outside_contract` (closed in this diff).
- `tools/ci/selftest_closures.json`: `python3 -I tools/ci/selftest_scope.py record --step merge-train --step pr-merger --step outside-contract --out <copy of the table>` (strace, Linux), unioned by `union_entries`: merge-train gains `tools/policy/policy_lint.mjs` and `tools/pr/outside.py` in `files`; pr-merger and outside-contract flat, and pr-merger flat again re-recorded at 436ee9878e. Selection is unchanged: `selftest_scope.py select --change M:tools/pr/outside.py` runs merge-train and pr-merger at both the merge base's table and the head's (merge-train reads the object store).
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; `python3 tools/audit/archscore/score.py --diff <merge base> HEAD` prints `Architecture score: dS +0.0000 NULL`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL` (`tools/ci/selftest_closures.json` is a gate file), left to CI; the `run_always` lines pass: `tests/env_drift.py --claims-only <merge base>` prints `claims hygiene: b3831ff64eca1936f0b618193ee86c3e337b51a9 ok`, `tests/closure.py selftest` prints `ALL 118 closure shrink pins PASSED`.

## Red checks

none

## Forward-carry

- Carry 2, the three live checks on a test fork: (a) whether the hpo-author installation token may call `update-branch` on a maintainer-editable fork pull request and which identity the merge commit carries, (b) app_approve.sh approving an adopted verdict end to end after that merge, (c) which `commit_id` a class-O approval reports before and after it. Not run: this seat has no `gh`, no App key and no fork pull request. Control: if (a) is refused the train parks `[OUTSIDE] ... no personal token is tried without the owner`, the designed stop; run all three before the owner adds an allowlist entry. Part 2 of this group holds the same checks as its carry 8. Carry: R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3
- Carry 3's decision-0017 half: the decision's text owes remerge_main.sh's `--head-repo`, the `[OUTSIDE]` class and the sentence that no tool of ours pushes a fork head to a branch of origin (true at this head: the train fetches it to `refs/remotes/pull/<pr>/head` only); the decision is policy, drafted for the owner's review by part 2, which holds it as its carry 7. Carry: R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3

## Friction

none

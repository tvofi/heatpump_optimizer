Fix review: blocked bef58ed281d0de8be0b95cc25016f1cd199fb128 harness: design-trace-missing part-1 job red on a planted unrecorded read and green after the bot commit

bus-nonce: 2284baf7957fcace2f0f63d6409cadf3

Round 3. This round covers the changes since the round-2 head `9e9c74fac7a1ad6cc27dddbc58d422883b650cec`, as the packet's scope (`delta`) sets. The delta is `tools/pr/ci_predict.py` `gated_arms_self_test` only. It comes from commit `1ced8e9b3b`, merged at `bef58ed281`, and the merge leaves the tree unchanged: `git diff 1ced8e9b3b bef58ed281` is empty. It touches no `custom_components/` file, so the review does not widen.

## Block

- **harness: design-trace-missing (fix-review.md step 9, #1588). Carried over from rounds 1 and 2, unchanged.** The approved note (design/R11-PRE-SHARED-FILES at `20cafac7df`, `design.md` line 137) names part 1's demonstration: "the job red on a planted unrecorded read and green after the bot commit; null: a green push writes nothing". The job is still not built, and the body still routes it to the owner as D1/D2 ("pending owner confirmation"). Nothing the owner has written lifts the block:
  - The pull request has no reviews. Its two comments are the round-1 and round-2 verdicts from `hpo-approver[bot]`.
  - `dev/programme/RULINGS.md` at `origin/main` was last changed at `d360d1c125` (2026-11-15) and has no ruling on R11-PRE-SHARED-FILES or D1/D2.

  The block lifts only when the owner rules on D1/D2, or waives the job for part 1 on this pull request. A fixer cannot clear it.

## Evidence

Round-2 items, each re-checked at this head:

- **Block (design-trace-missing):** still open. See Block.
- **Finding: `gated_arms_self_test` pinned only `selftest-scope`:** resolved. The check now asserts the literal set, and the default-call case takes its expected value from that literal, not from `GATED_ARMS`. I ran my own mutants in a detached worktree of `bef58ed281` with `python3 tools/pr/ci_predict.py --self-test`, restoring the file after each one (`ev/own_mutants.txt`). Unmutated, the self-test reads `0 failed`.

  | Mutant | Result |
  |---|---|
  | `self-test-reads` taken out of `GATED_ARMS` | `2 failed` (the exact-set check and the default-call check) |
  | `graders` taken out of `GATED_ARMS` | `2 failed` (same two checks) |
  | `step-replay` taken out of `GATED_ARMS` | `2 failed` (same two checks) |
  | `selftest-scope` taken out of `GATED_ARMS` | `2 failed` (same two checks) |
  | ungated `orphans` added to `GATED_ARMS` | `2 failed` (same two checks) |
  | null: the set-equality case made `True` with `GATED_ARMS` unchanged | `0 failed`, as expected |

  This matches the body's Mutation proof for `1ced8e9b3b` (each arm removed: `2 failed`).
- **Note: stale-body (the overlay departure's acceptance):** resolved. The body now records the orchestrator's written acceptance (mandate 6893738184).

Head, merge and CI:

- Head reviewed: `bef58ed281d0de8be0b95cc25016f1cd199fb128` (`ev/HEAD.txt`). It is still the branch tip (`git ls-remote`), and the body's `## Head` names it. Merge base: `5e2ef89b4e7348b190aa917dc032da73ba04998e`.
- `git diff <merge base> origin/main -- dev/governance/roles/` changes only `architect-planner.md` and `plan-review.md`. `fix-review.md` is unchanged.
- `git merge-tree --write-tree origin/main bef58ed281` exits 0 with empty stderr (`ev/mergetree.err`).
- The three-dot diff touches none of `VERSION`, `custom_components/`, `RELEASE_NOTES.md` or `tests/golden/`.
- CI: `merge_train.py classify bef58ed281d0de8be0b95cc25016f1cd199fb128 --pr 3708` printed `GREEN bef58ed281d0de8be0b95cc25016f1cd199fb128 pending: none red: none`. It exited 0 at the start of the review and again at 06:33:20 UTC (`ev/classify.log`).
- Red checks: the only red in the packet digest is `tests / nightly-status`. It is not in the `merge_train.py owed-reds` set, so it is not answered.
- carry_audit at the head (from the packet): `9 finding item(s): 9 routed, 0 unrouted, 0 bad destination(s)`.
- Not re-taken: the body's heavy strace figures (`precheck --base origin/main`, 22 min 39 s) and its `prepr: passed rc=0 at 1ced8e9b3b`. They are the body's figures, not mine, and that commit's tree equals this head's.
- I ran the self-audit of this verdict against a stub body, because this seat has the body only through MCP.

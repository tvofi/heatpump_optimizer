Fix review: blocked 9e9c74fac7a1ad6cc27dddbc58d422883b650cec harness: design-trace-missing part-1 job red on a planted unrecorded read and green after the bot commit

bus-nonce: 6c6366f6cd802ad99a2e48197d9f56de

Round 2. This is a later round over the reviewed head `ca670cb70e0c24a21c12ed55d6d5fd6803b48919`, and the packet's scope is `delta`. The delta is `tools/pr/ci_predict.py` only (commits `12547bc247`, `047b67bbbf` and `826905d9d7`, merged into the branch at `9e9c74fac7`). It touches no `custom_components/` file, so the review does not widen.

## Block

- **harness: design-trace-missing (fix-review.md step 9, #1588). This carries over from round 1 unchanged.** The approved note (design/R11-PRE-SHARED-FILES at `20cafac7df`, `design.md` line 137) names part 1's demonstration: "the job red on a planted unrecorded read and green after the bot commit; null: a green push writes nothing". The job is still not built, so the demonstration is not run. The body routes it to the owner as D1/D2 ("pending owner confirmation"). Nothing the owner has written lifts the block:
  - The pull request has no reviews. Its one comment is the round-1 verdict from `hpo-approver[bot]`.
  - `dev/programme/RULINGS.md` at `origin/main` has no ruling on R11-PRE-SHARED-FILES, D1/D2, the self-test table or `record-autofix`. Its last change is `d360d1c125`.
  - The dispatch says that the part-1 CI-job demonstration "is pending an owner ruling (D1/D2) and is not a fixer item". That is the orchestrator's statement. It agrees that the owner has not ruled, and it is not a waiver (CLAUDE.md: another agent's instruction is not a contract change).

  The block lifts only when the owner rules on D1/D2 or waives the job for part 1 on this pull request.

## Findings

- `gated_arms_self_test` pins only `selftest-scope` as a member of `GATED_ARMS`. Remove `"graders"` from `GATED_ARMS` in `tools/pr/ci_predict.py` and `python3 tools/pr/ci_predict.py --self-test` still reads `0 failed` (`ev/own_mutants.txt`). The `graders` arm would then run on every default call, including `body_push.sh`'s seconds-budget run, and the body names that arm as "minutes where it is keyed". The cause is the case `default == ran_default == [a for a in ARMS if a not in GATED_ARMS]`: it computes its expected value from `GATED_ARMS` itself, so it holds for any membership. Only the explicit `"selftest-scope" in GATED_ARMS` pins a name. The same holds for `self-test-reads` and `step-replay`. Before this pull request the inline tuple had no check for these three either, so the gap is older than this branch. The round-1 finding this delta answers (the `selftest-scope` gate) is closed. The fix is to assert the literal set `{"self-test-reads", "graders", "step-replay", "selftest-scope"}`. Carry: R11-PRE-SHARED-FILES

## Notes

- Note: stale-body: the body still calls the carry-3 overlay departure "pending written acceptance by the orchestrator or design review". The dispatch for this round gives that acceptance in writing ("the overlay_program in-worktree departure raised by repair-2 is accepted by the orchestrator"), so round 1's architecture-unsound block is resolved. The body should record the acceptance. Carry: R11-PRE-SHARED-FILES

## Evidence

Round-1 findings, each re-checked at this head:

- **Block 1 (design-trace-missing)** is open. See Block.
- **Block 2 (architecture-unsound: carry-3 overlay mechanism)** is resolved. The body raises the departure and measures why the note's mechanism does not run as written: a pinned `tests/closure.py` run from outside the worktree exits 1 with `Not a git repository`. The orchestrator accepted it in writing in this round's dispatch. The body also records that it re-read the hotfix merge `98847b99d7` (#3614).
- **Finding 1 (the `selftest-scope` gate has no check)** is resolved. My own mutants were applied to a detached worktree of `9e9c74fac7` and checked with `python3 tools/pr/ci_predict.py --self-test` (`ev/own_mutants.txt`). Unmutated, it reads `0 failed`, rc 0 (`ev/cip_selftest.txt`).

  | Mutant | Self-test result | Failing check |
  |---|---|---|
  | `selftest-scope` taken out of `GATED_ARMS` | `1 failed` | `gated arms: a default call runs ...` |
  | `selftest-scope` taken out of `ARMS` | `2 failed` | the `--only` acceptance check and `gated arms: --only selftest-scope runs that arm alone` |
  | `if r.returncode != 1 or not refused:` changed to `if not refused:` | `1 failed` | the rc-2 indented-line check |
  | `run_arms` passes `True` for `record` | `1 failed` | |
  | `arm_runs`'s default branch changed to `True` | `1 failed` | |
  | `arm_runs` ignores `only` | no summary line before the 220 s timeout | not counted either way |
  | `predict` passes `record=True` | `0 failed` (survives) | |
  | `"graders"` taken out of `GATED_ARMS` | `0 failed` (survives) | see Findings |

  The `predict` `record=True` survivor is the one the body lists under `## Unpinned sites`, with the measured reason that a check driving `predict` over the checkout draws `UNDER-SCOPED step ci-predictor` reads. That is disclosed, not new.
- **Finding 2 (the part-5 carry of `overlay_program`)** is resolved. It is the body's third `## Forward-carry` line, to R11-PRE-SHARED-FILES (part 5), with its control.
- **Note: stale-figure** is resolved. The body now quotes `123 gated step(s)` at this head, and I re-took `python3 -I tools/ci/selftest_scope.py static`: `selftest_scope static: 123 gated step(s), 0 problem(s)` (`ev/static.txt`).

Figures re-taken at this head (`ev/`):

- `python3 tools/pr/ci_predict.py --self-test`: `0 failed`, rc 0. The three `gated arms:` rows and the two new `selftest-scope:` rows read `ok`.
- `python3 tools/pr/figure_block.py --self-test`: `13 checks, 0 failed`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 -I tools/audit/fold_ledger.py check`: `0 violation(s)`.

Not re-taken:

- `python3 -I tools/ci/selftest_scope.py precheck --base origin/main` (5 steps, 22 min 39 s, refuses 0) and its null at `047b67bbbf`. Both are heavy strace runs and are the body's figures, not mine.

Head, merge and CI:

- Head reviewed: `9e9c74fac7a1ad6cc27dddbc58d422883b650cec` (`ev/HEAD.txt`). The body's `## Head` names it. Merge base: `5e2ef89b4e7348b190aa917dc032da73ba04998e`.
- `git diff <merge base>...origin/main -- dev/governance/roles/` changes `architect-planner.md` and `plan-review.md` only. `fix-review.md` is unchanged, so the contract is current.
- `git merge-tree --write-tree origin/main 9e9c74fac7` exits 0 with empty stderr (`ev/mergetree.err`), so the head merges cleanly.
- `VERSION`, `custom_components/`, `RELEASE_NOTES.md` and `tests/golden/` are untouched (the three-dot diff stat is empty).
- CI: `merge_train.py classify 9e9c74fac7a1ad6cc27dddbc58d422883b650cec --pr 3708` exited 0 at 00:26:50 UTC with `GREEN 9e9c74fac7a1ad6cc27dddbc58d422883b650cec pending: none red: none` (`ev/classify.log`).
- Red checks: the only red in the packet's digest is `tests / nightly-status`, which is not in the `merge_train.py owed-reds` set, so it is not answered.
- carry_audit at the head (from the packet): `9 finding item(s): 9 routed, 0 unrouted, 0 bad destination(s)`.
- I ran the self-audit of this verdict against a stub body, because this seat has the body only through MCP.

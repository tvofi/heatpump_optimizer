Fix review: blocked d0db3e30b84652af833d13f7f708a45704fdd6c8 mutation-vacuous: worktree removal on a final refusal and the refresh_lint HEAD check and refusal survive deletion under the harness and the self-test

bus-nonce: c9e20e4178d1ef1aeddd594740eb5dfb

Round: first fix review of PR 3337 (R10-HOTFIX-ROSTER-LINT-REFRESH), from a detached worktree at d0db3e30b84652af833d13f7f708a45704fdd6c8.

## Block

- The body names two mechanisms: (1) `refresh_lint` detaches the lint clone at the edit checkout's origin/main, verifies HEAD equals it and refuses by name; (2) "a final refusal removes the worktree", which is the fix for the 172-line "is on no origin ref" cascade. Only the detach SHA is pinned. When I delete each of these production lines in `tools/audit/seat/roster_queue.py`, both `dev/audit/harnesses/roster_queue_stale_lint.py` and `roster_queue.py --self-test` (54 checks, 0 failed) still pass: M4 (drop `sh("git", "-C", a.edit_checkout, "worktree", "remove", ...)` before `return False`), M5 (`if c.returncode != 0 or head != sha:` set to `if False:`) and M6 (`if err:` in `_run_op` set to `if False:`). The committed harness drops the cascade line only because op1 no longer refuses. It never sends a refusal through the fixed code. My own variant of the finder's harness (lint fresh, the stub refuses op1 once for an unrelated reason, op2 must push) shows that mechanism (2) works and that the harness can pin it: base FAIL, head PASS, M4 FAIL (ev/variants.txt). The fixer owes a check that pins M4, M5 and M6: a refusal followed by a push in the harness, and a `_run_op` case whose refresh fails and must report "lint clone not refreshed" without running the editor. Each check must fail on its mutant.
  Carry: built-here

## Findings

- Surviving mutants M3 (no `fetch origin main` in the edit checkout inside `refresh_lint`) and M7 (no fallback fetch in the lint clone before the retried checkout). These are minor. In the harness, EC's origin/main moves by EC's own push, and the clone shares EC's store through `--reference`, so neither line runs on a path that matters. The real drain's EC sees main move only through other seats' pushes. M3 is partly covered by the "not origin/main" retry. Pin them in the same re-cut, or disposition them in the body.
  Carry: dismissed: folded into this PR's re-cut owed by the block

- The body's `## Red checks` says none. The head carries one concluded red, the deferral `gate` in run 42499187718, and review_packet refuses on it (red-unanswered, required-red). The re-cut body should name it and give the answer: a deferral superseded by run 42499185929's green gate. Separately, `merge_train.py classify` reports RED on a deferral red whose deciding run is green. That is an instrument defect that belongs to the merge train, not to this PR.
  Carry: dismissed: the body half is folded into this PR's re-cut owed by the block; the classify half is an instrument observation for the orchestrator, recorded here as evidence and not filed

## Evidence

- RESULT harness at base (merge base 8a4974d152, which byte-equals the body's bb7dfb9bd6 copy): FAIL. The run shows the stale-worktree refusal, then the "is on no origin ref" cascade (ev/harness_base.txt).
- RESULT harness at head: PASS, both ops pushed (ev/harness_head.txt).
- RESULT null control (my variant: the lint clone's fetch works and is fresh): PASS at base, PASS at head (ev/variants.txt). A non-stale queue is unaffected at both ends.
- RESULT cascade variant (mine, disclosed as my own instrument and not the finder's): base FAIL, head PASS, M4 FAIL.
- Mutation table (ev/mutation.txt, ev/mutation_selftest.txt). M1 (refresh no-op) and M2 (detach at the clone's own origin/main) fail the harness and are killed. M3, M4, M5, M6 and M7 survive both the harness and the self-test.
- Self-test at head: 54 checks, 0 failed. This matches the body.
- Loop and masking: a `refresh_lint` error returns at once with a named refusal, and the retry loop stays bounded at 4 attempts. With the HEAD check in place, a clone that cannot be moved cannot pass silently. Without the check (M5), nothing in the tree would notice, which is the block above.
- Seam: the change is in `tools/audit/seat/roster_queue.py` `_run_op`, the drain that feeds the roster_edit lint gate. That seam owns the queue's lint refresh.
- Classification: the harness sits in tests/closures.json under `inert_reads` / `tests/harness_headers.py`. That is a one-line, minimal, deliberate entry. The tree's tests/entities.py did not run locally because homeassistant is not installed; CI's tests lanes cover it.
- No `*_budgets.json` change, and structure.py reports STRUCTURE RATCHET PASSED. VERSION, the manifest and RELEASE_NOTES.md are untouched. The delivery row dev/programme/delivery/3337.md is in the diff.
- `## Head` names d0db3e30b84652af833d13f7f708a45704fdd6c8, the head I measured.
- Merge with origin/main: `git merge-tree --write-tree` exited 0 with tree abe03aada0aeb997a91665cf42b578d3a59826f4, so there is no conflict.
- Figures not re-derived: 1327/786/172/2/30 come from roster-rep.txt, which is outside the tree. The cost-test minutes are also not verified. "About 40 lines": the roster_queue.py diff is +39/-2.
- CI at this head, read once from the check-runs listing (55 runs, one page). In workflow run 42499185929, `gate` (job 128795807992) concluded success at 16:49:05Z, and `pr-contract / pr-contract` concluded success. Every tests/governance/codeql/hassfest/validate/arch-score/budget-raise-gate lane is success or skipped, including tests / closures, fast (3.14), coverage, mutation and instrument-self-tests. The one concluded red is `gate` in run 42499187718 (job 128788451757, 16:20:25Z). Its log is a deferral, not a defect: "FAIL run(s) [42499185929] at this head are still being judged; their gate decides". That run's gate later went green. `merge_train.py classify` still keys on the stale deferral red: rc=1, `RED d0db3e30b84652af833d13f7f708a45704fdd6c8 pending: none red: gate` (ev/classify.txt, ev/classify_poll.txt). The block above does not rest on CI.

Fix review: merge 7eedd204446228d22533f91c05edd688bc0d6fd7
bus-nonce: 2d2d3f8b98b94d5efd8c44403c23f1c1

Round 2. I reviewed from a fresh detached worktree, `review-2044/wt2`, at 7eedd204. That head is 79ca6b47 merged with the fixer's commit 8911527f. 7eedd204 already contains origin/main 2d8cab3f. The policy files are current against origin/main: the three-dot diff of `dev/governance/roles/` is empty. Evidence is in `review-2044/evidence2/`.

## Round-1 blockers, re-checked
- **Blocker 1, D unbounded.** Closed.
  - RESULT `probe_red_main.py`, my own instrument re-run unchanged at the head: lone entry rc=1 merged=[]; pair rc=1 merged=[] pushed=0; null control (main green) merged=[1, 2]; 82 checks, 0 failed.
  - Before admission, `main_green` waits on every required context at main's tip, less PR_ONLY. It ignores `--ignore-red`. The first merge's guard re-reads it. After a lone D merge with later serial entries, the train waits for main's run on that merge.
  - Main's own push writes all 14 contexts the gate waits on, so the gate cannot strand on main. I read main's tip 2d8cab3f; all 14 are present and completed green (`evidence2/main-required.txt`).
- **Blocker 2, policy disagreement.** Closed. nudge.md sections 9 and 18 and orchestrator.md section 11 all name `merge_train.py batch` as the only bypass. `grep merge_fastpath` finds no other bypass claim in CLAUDE.md, AGENTS.md, `dev/governance` or `.claude/skills`. `policy_lint --budgets`: orchestrator.md 4096/4096, nudge.md 3776/3814.

## Mutants and self-tests (re-run by me at the head)
- RESULT merge_train self-test 80 checks, 0 failed; merge_fastpath 35 checks, 0 failed; app_push 60 checks, 0 failed.
- RESULT mutation drive: M0 80/0. M1–M14 are all red.
  - 1 failed each: M1, M2, M3, M7, M8, M9, M10, M11, M12, M13.
  - 3 failed: M4. 4 failed: M14.
  - M5 and M6 end in IndexError.
  - Output is in `evidence2/mutants.txt`.

## Trying to land on a red main another way (`evidence2/probe_round2.py`, my own instrument)
- **R2-A: a proved pair where main's run on merge 1 turns red** after the merge. RESULT merged=[1, 2], TRAIN DONE. Merge 2 lands before merge 1's FULL push run finishes. This is not a regression and not a block:
  - The proof graded P_2, the exact tree main reaches. It is the same required set, judged on a scoped `fast` against the batch's merge base.
  - The old `run` also landed entry 2 without waiting for main's FULL run on entry 1.
  - Option B as chosen accepts this risk.
- **R2-B: a lone D merge with nothing later, red after.** RESULT merged=[1], TRAIN DONE without waiting. Nothing more lands through `batch`, because the next invocation's admission gate waits for main's tip run to complete green. Gate checks: M11 and probe PROBE-1.
- **Other routes I checked:**
  - Serial `run` re-merges main into its head, so a red main reddens the head. That code is unchanged.
  - A `--base batch/` rehearsal cannot target main; PR target must equal base.
  - An autofix push or force-push to an entry is stopped by `head(pr) != h` and `--match-head-commit`.
  - A stamp or record merge mid-batch is stopped by the tree guard.

## Carried from round 1 (code paths unchanged in the delta)
- **Live proofs.** Null control cb9b1831: tree equality and all 14 contexts green. Perturbation d8f8d050: env-matrix and policy-docs red, at 60358 tokens against a cap of 60091.
- **Text-merge build** and **the ruleset**: `strict: false` on main-protect-checks.
- **Bisect.** These were measured at 79ca6b47, in round-1 `evidence/`. The round-2 delta (`evidence2/round2.diff`) leaves build, settle and culprit untouched.

## CI at the head (CI's check-runs, read 2026-10-08, 36 runs)
- Green: fast (3.14), mutation, policy-docs, closure-scope, and pr-contract (both runs).
- budget-raise-gate: cancelled, with a success twin. Rerun the twin if the merge gate keys on it.
- delivery-status and nightly-status: red. The body's Red checks section answers both: nightly-status grades main's last scheduled run, and delivery-status reads only this PR's own row.
- Analyze (python) and coverage were still in progress when I read them. The orchestrator must see both complete before merging.
- `git merge-tree --write-tree origin/main HEAD` exits 0. VERSION, the manifest and the notes heading are untouched. Claim files are untouched.

## Body nits (non-blocking, fix at the orchestrator's discretion)
- Line 33 still says M6 gives "10 checks FAIL". Line 42 and my run both show IndexError.
- `## Approval` names nudge.md section 18 only. Section 9 changed too.
- The R2-A residual (a proved batch's later merges do not wait for main's FULL run on earlier ones) is not listed under Residual risks.
- `batch/` branch deletion uses the orchestrator's git credential and its return code is unchecked. It runs only on success.

This PR changes policy (orchestrator.md and nudge.md), so it still needs tvofi's own approving review.

Fix review: merge 3d46d033d9a00219b9e7895b61281200a6c9dba0

bus-nonce: 31a5075dda3b0560b3f68d336a78e56c

## Round

Round 2 (the re-review after repair round 1's mutation-vacuous verdict). This is not the fourth round, so no re-cut is owed. I reviewed from a detached worktree at 3d46d033d9a00219b9e7895b61281200a6c9dba0. Diffs are three-dot against merge base dee8b413fd7d. `dev/governance/roles/` has no change between the merge base and origin/main.

## Verdict

The `graders` arm now enumerates every job holding `RESTORE_STEP` across `.github/workflows/`. I re-derived that set at the head and at the merge base: six jobs, which is #2952's own rule. The null control holds: of 95 jobs, no job without the step is listed. A PARTIAL run is never reported as a pass. Every mutant on the delta's added lines is killed, except one disclosed survivor and one equivalent mutant (Findings). The merge into origin/main is clean, CI at the head is GREEN, and no budget, VERSION, closure or claim file moved.

## Evidence

- RESULT enumeration: `restoring_jobs` returns briefs, budget-raise-gate, env-matrix, policy-docs, pr-contract and wave-script (6) at the head and at merge base dee8b413. An independent awk over the workflow text gives the same six (job, file) pairs. The null control scans 95 jobs with 0 mismatches. The seven other base-restoring steps (ci.yml prelude, refresh and gate; tests.yml closures-, claims- and mutation-autofix; codeql.yml) use other step names. The body dispositions them as outside #2952's stated six-job rule, and #2952's body states that rule (ev/enumeration.txt).
- RESULT real-tree run keys: pr-contract grades policy_lint.mjs, figure_lint.mjs, preflight.sh, prepr.sh and carry_audit.py, which is #2952's list. codescan_wait.py is exempt. `grader_gaps` over all six workflow texts is empty (ev/realkeys.txt).
- RESULT self-test: `python3 -I tools/pr/ci_predict.py --self-test` prints `ci_predict self-test: 0 failed`, rc 0, in 89 s (ev/selftest.txt).
- RESULT fixer's mutant table (`dev/audit/rca/prepr-head-graders/mutants.py .`), re-run: M1 11, M2 1, M3 2, M4 1, M5 4, M6 6, M7 10, R1-I 4, R1-K 1, R1-L 1, R1-O 1, R1-P 1, R1-E 1, R1-H 1, R1-F 5, R1-N 1, R1-S 1. Every figure matches the body (ev/mutants_fixer.txt).
- RESULT reviewer mutants on added lines the table does not name (my own instrument, ev/rev_mutants.py):
  - Killed by FAIL count: V1 (BOOTSTRAP on every refusal: Carry 3(c)'s membership control) 2, V2 3, V3 (partial annotation dropped) 1, V4 (PARTIAL note never written) 2, V5 (notes never returned) 3, V8 1, V9 1, V10 3, V11 1, V12 1, V14 1 of 2, V15 6, V16 1, V17 1, V18 1, V20 1.
  - Killed by crash (rc 1): V6 (backslash continuation not joined: shlex ValueError) and V7 (keyed by bare job: KeyError 'gate') (ev/v6v7.txt).
  - Carry 2's mutant R1 (grade under the file's own key) is killed by `self_test_reads_self_test` (1 FAIL).
  - V13 and V19 survive (Findings).
- RESULT PARTIAL is never a pass, on real-tree plants with the PR's own `plant_jobs.sh`:
  - The budget_raise_gate.py plant prints `GRADER PARTIAL budget-raise-gate: ... its result is not a pass`, with rc 0 and no PREDICT line.
  - The preflight.sh plant with a stub body runs every pr-contract program. Its policy_lint refusal carries `(partial: ran without ...)`, and the closing line owes a repair. BOOTSTRAP is correctly absent, because the refusing policy_lint.mjs is not in the over-list.
  - The same plant with no body skips the four body readers with `GRADER SKIPPED` notes.
  - prepr.sh:618 passes `--body` when it has one (ev/plant_*.txt).
- RESULT tmp_paths: `--check` gives 0 refused and 0 stale. Dropping any one of the seven ci_predict.py ALLOW entries refuses 1 line, or 3 lines for the bare `/tmp/pr-author.txt` entry. The delta's two entries are exact single-line literals, so the narrowest that works (ev/tmp_paths_narrow.txt).
- RESULT structure: `tests/structure.py` prints STRUCTURE RATCHET PASSED. No `*_budgets.json`, `tests/closures.json`, `tests/closure.py`, golden or claim file is in the diff. VERSION, the manifest and RELEASE_NOTES.md are untouched.
- RESULT closure classification: plant_jobs.sh and dev/programme/delivery/3301.md fall under the INERT prefixes `dev/audit/` and `dev/programme/`. `tests/entities.py` ends `3 of 2655 ENTITY CHECKS FAILED`, as the body states. The three are a5:pages_ok, the release ZIP build and the Pages workflow probe (HA-stub and environment gaps in this cloud seat). No orphan "force the FULL suite" failure (ev/entities_tail.txt).
- RESULT head: the PR head is 3d46d033, a merge of 926a0149 and 038e0ba5 whose tree is identical to 038e0ba5's. `## Head` names both correctly, and the delta 926a0149...3d46d033 is 94 insertions and 4 deletions, as briefed. `git merge-tree --write-tree origin/main 3d46d033` (main d2e4d2d10cfe) exits 0 and runs no claim driver (ev/HEAD.txt).
- RESULT CI: `merge_train.py classify 3d46d033... --pr 3301` printed `GREEN 3d46d033d9a00219b9e7895b61281200a6c9dba0 pending: none red: none`, rc 0. One `gate` run (128624770721, 04:13Z) failed with `FAIL run(s) [42445115104] at this head are still being judged`. Two later `gate` runs (04:30Z and 04:31Z) succeeded, and `pr-contract / pr-contract` 128628111684 started after that red and succeeded. Under fix-review.md rule 11, that green run is the evidence. The packet's earlier `arch-score` and `gate` entries were cancelled superseded runs; `arch-score` has three green runs (ev/checkruns.txt, ev/gate_128624770721_tail.txt).
- RESULT forward-carry: roster handoff/audit-r10-roster 54ec9464 states Carry 1, Carry 3(a)/(b) and Carry 4 on this group with their controls as preconditions. Carry 2 and Carry 3(c) land here.
- Figures I did not re-derive: the prepr wall time (36 m 8 s) and its 14 diff-mutant survivors. Per rule 11 I cite CI's mutation lane (`tests / mutation` success) and did not re-run the gate or prepr.
- Architecture: arch-score is green at the head. The widening reuses `restore_jobs`, `job_text` and `ci_tree_run`, with one new enumerator and no list of names. The self-test mutates module globals (`GRADER_PARTIAL`) and pops them after its `finally`, so an exception inside it leaves them set. That is confined to the self-test process and is not a breach.

## Findings

- Residual: the production counting expression `boot = sum(... "BOOTSTRAP:" in l)` in `main` (tools/pr/ci_predict.py:1236) is unpinned. Reviewer mutant V19 (count every red) survives `graders_self_test` with 0 FAIL. `summary_line` itself is pinned by direct calls, and the body discloses this site under `## Unpinned sites` as a stated gap. It affects closing-line text only, never a verdict or rc. Carry: R10-FLY-CIPREDICT-RESTORING | dismissed: disclosed under the body's ## Unpinned sites at this head; closing-line text only, no verdict or rc depends on it
- Residual: the `GRADER_PARTIAL` prefix match (`key_[:len(k)] == k`) is not distinguished from an exact match by any case. Reviewer mutant V13 (exact match) survives with 0 FAIL. It is equivalent today: every real `GRADER_PARTIAL` key equals its run's whole key (ev/realkeys.txt). Carry: R10-FLY-CIPREDICT-RESTORING | dismissed: equivalent mutant on the measured table; the prefix matters only for a run line with more flags than its registered key, and none exists
- Residual: the `$INTENDED` stand-in is every issue the body closes. CI's list also drops roster `issues` that no group `fixes`, so a body closing such an issue passes the predictor's preflight and fails CI's. Carry: R10-FLY-CIPREDICT-RESTORING | dismissed: preflight.sh is in GRADER_PARTIAL ("ran without the intended-file list"), so its clean run is already noted as not a pass, by design
- Residual: the pre-delta ALLOW entry `/tmp/pr-author.txt` in tools/audit/seat/tmp_paths.py is a bare literal covering three ci_predict.py lines (643, 811, 1576), where the other six entries each cover one. Carry: R10-FLY-CIPREDICT-RESTORING | dismissed: per-file and per-literal for the one runner-side path the predictor stands in for; three exact entries would add two rows for no safety gain, and the delta's own two entries are exact

## Friction

none

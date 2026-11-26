Two countermeasures from `dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md` section 6, both on `tools/pr/prepr.sh`'s step 6d path, placed by the round-10 round-end triage (`dev/programme/triage/r10-round-end.md#P768`).

C3, Carry 0 (R10-PREPR-RESIDUE item fab9d1da). Each `prepr.sh` step line now leads its detail with `[Ns]`, the step's elapsed seconds: bash's `$SECONDS` minus `STEP_MARK`, which `say` resets at every verdict line, so no process is spawned. The `PRE-PR:` result line, and the summary line `summary_end` writes, carry `elapsed=Ns` for the whole run.

C4, Carry 1 (R10-PREPR-RESIDUE item e0b30357). The comment over `predict_line` said step 6d "costs seconds". It is corrected: the fifth argument adds `ci_predict.py`'s `GATED_ARMS`, which run code (SELF-TEST READS, GRADER, STEP REPLAY, SELFTEST SCOPE), and only a diff keying none of them costs seconds. The comment at `predict_line`'s `rec=` call site said the same thing and is corrected too. Of the arms CI already runs, the bounded one is STEP REPLAY: it replays `instrument-self-tests` steps one after another. Now it replays first the steps whose run text names a changed file (#3245's shape), then recorded readers, then the rest. Once `STEP_REPLAY_BUDGET` (600 s, override `HPO_STEP_REPLAY_BUDGET_S`) is spent, it starts no further replay; the unreplayed steps go into one `LEFT TO CI <k> of <n>` note that names each. SELF-TEST READS is untouched. The shared parse of a positive-seconds variable is `env_seconds`, and `step_replay_timeout` now uses it too.

Alternatives considered. Leaving STEP REPLAY wholly to CI lost because it would drop #3245's red class, which the budget keeps by replaying file-naming steps first. Bounding GRADER lost because its jobs already run side by side, so the slowest job bounds it (`env-matrix`, 351 s below). A per-step timeout already exists (`HPO_STEP_REPLAY_TIMEOUT_S`) and bounds one step, not the sum.

## Head

0d8cac00c781223f2d7b0914ce80b3a1dd1399bb, merge base dbdc71faea358a95a7b33840ed252b0d8a646a31. 0d8cac00c7 merges the reviewed head a0250fc36517a51c90b2f36046ed1ca1253ca153 into 6403d464191d73c4e3ff8b4231d7f5f87d38c251, so `git diff a0250fc365 0d8cac00c7` is 6403d46419's `tools/pr/prepr.sh` hunk alone. `tools/pr/prepr.sh` and `tools/pr/ci_predict.py` are byte-identical at afbc0bc485 and a0250fc365, and `tools/pr/prepr.sh` at 6403d46419 and 0d8cac00c7, so the measurements at 6403d46419 and afbc0bc485 below hold for this head. Earlier evidence was taken against merge base e3cb5c019b464a770cc7c6fe2fbc858ed29debf7. 6403d46419 changes only `tools/pr/prepr.sh`'s self-test, over afbc0bc485: the run elapsed is now pinned as a clock read (review block on a0250fc365, mutants pp4b and pp5). The C4 timings were taken at 026ea0ea9b3dc32ee9f672e7bc78f4b6aeaffd96. `git diff 026ea0ea9b3dc32ee9f672e7bc78f4b6aeaffd96 afbc0bc4858956f822bb499bf22cc5e8a57e5269 --stat` lists one comment line in `tools/pr/prepr.sh` and, in `tools/pr/ci_predict.py`, only `step_replay_self_test`, which the timed `ci_predict.py --base ... --record-self-tests` call never runs. After d2fbbf2d00, prepr's diff-mutant step left five survivors on that self-test's hand-rolled environment save, pop and restore. `mock.patch.dict` replaces them, so those lines are gone rather than dispositioned. A sixth survivor at abf6facdd7, the budget check's `good = ...` deletion, inherited the previous check's `True`. Under its own name, `held`, that deletion is a NameError: self-test rc=1, against rc=0 and 114 ok unmutated.

## Mutation proof

Each mutant was applied in a fresh worktree of the head (the two `ci_predict.py` mutants at abf6facdd7, which the last commit changes only by the `held` rename, the three `prepr.sh` ones at d2fbbf2d00, whose `prepr.sh` is the head's) and its self-test run in full; the unmutated runs are under `## Null control`.

- `ci_predict.py`, `if spent >= budget:` changed to `if False:` (the budget predicate). `python3 tools/pr/ci_predict.py --self-test` rc=1, FAIL `a spent replay budget replays the step naming the changed file first and leaves the rest to CI, named`.
- `ci_predict.py`, the replay order `sorted(hit, key=...)` changed to `sorted(hit)[::-1]`. rc=1, FAIL on the same check.
- `prepr.sh`, `STEP_MARK=$SECONDS` in `say` changed to `:` (the per-step reset). `bash tools/pr/prepr.sh --self-test`: 573 passed, 1 failed, FAIL `and a no-op step after it prints 0 or 1, so the field times the step, not the run (C3's null control)`.
- `prepr.sh`, `step`'s ok branch printing `${3:-}` without `$t`. 572 passed, 2 failed: FAIL `a step stubbed to sleep 2 s prints an elapsed of at least 2 (C3)` and the null-control check.
- `prepr.sh`, `summary_end` without ` elapsed=${SECONDS}s` (at d2fbbf2d00). 572 passed, 2 failed: FAIL `the last line is the result with rc, naming a unique log under TMPDIR` and the result-line elapsed check.
- pp4b, `prepr.sh` `summary_end`'s `elapsed=${SECONDS}s` replaced by the constant `elapsed=2s`, at 6403d46419 in a fresh worktree, run alone. The fixture now sets `SECONDS=1000` before `summary_end` and requires 1000 or 1001. FAIL `and the result line carries the run's elapsed read from the clock: SECONDS set to 1000 before summary_end prints 1000 or 1001, so a constant fails`. Before 6403d46419 the check accepted any value of 2 or more, and this mutant survived (574 passed, 0 failed).
- pp5, the main flow's final `echo "PRE-PR: $(git rev-parse HEAD) $digest elapsed=${SECONDS}s"` with ` elapsed=${SECONDS}s` deleted, at 6403d46419 in a fresh worktree, run alone. The self-test now extracts that line from the flow, then runs it with `git` stubbed and `SECONDS` set to 730 and to 40. FAIL `the main flow's stdout PRE-PR line carries the run's elapsed from the clock (SECONDS=730 prints 730 or 731)` and `and a different clock (SECONDS=40) prints 40 or 41, so the field tracks the clock`. Before 6403d46419 no check read this line, and the mutant survived.
- pp4b and pp5 each add FAIL lines only on their own new checks. Their other FAIL lines also appear in the unmutated runs on the same host (`## Null control`).

The `env_seconds` bound (empty, junk, 0 and negative keep the default) is pinned by 026ea0ea9b's self-test, which kills prepr's CMP_BOUND survivor at `v if v > 0`.

## Null control

- Unmutated: `python3 tools/pr/ci_predict.py --self-test` rc=0 with no FAIL line (114 ok) at the head, and `bash tools/pr/prepr.sh --self-test` 574 passed, 0 failed, at d2fbbf2d00, whose `prepr.sh` is the head's.
- C3: the self-test's no-op step, run after the 2 s step, prints `[0s]` or `[1s]`, so the field times the step and not the run.
- C3, the run elapsed: at 6403d46419, unmutated, the three clock-driven checks pass (`summary_end` at SECONDS=1000, and the main-flow line at 730 and at 40). Two settings of the clock print two different values, so the field reads the clock and holds no constant.
- `bash tools/pr/prepr.sh --self-test` on the macOS host that ran pp4b and pp5, at afbc0bc485 unmutated: 572 passed, 2 failed. The two FAILs are `an ancestry no commit of which carries any check run skips, never refuses` and `and the skip line names the boundary`. At 6403d46419: 572 passed, 4 failed. These are the same two FAILs, plus `reds_arm refuses a body that leaves an ancestry red unanswered (P351)` and its sentence check, which fail in some runs on this host and pass in others (pp4b's run passes them). None of these checks reads a line this PR changes. The reviewer's container ran afbc0bc485's `prepr.sh` at 574 passed, 0 failed.
- C4, in-tree: under the default budget, the self-test's two-step fixture replays both steps and leaves none to CI (`null control: under the default budget both steps are replayed and none is left`).
- C4, timed: a diff under the budget, `currency.py` alone, gives the same timings at both commits (`## Figures`, the null-control line).
- At the merge base, `git show e3cb5c019b464a770cc7c6fe2fbc858ed29debf7:tools/pr/prepr.sh | grep -c 'elapsed=${SECONDS}s'` prints 0, and the same for `STEP_REPLAY_BUDGET =` in `ci_predict.py`. Neither countermeasure exists there; the head prints 2 and 1.

## Figures

The instrument is `python3 dev/audit/harnesses/prepr_6d_arms.py <commit> [<file> ...]`, landed in this PR. It runs <commit>'s own `ci_predict.py --base <commit> --record-self-tests` (prepr's 6d call) on one fixed diff: a comment line appended to each file of slim-p2's diff at 6671786843 that a gate cannot scope. It prints `wall_s`, each arm's seconds, the `predict_sha1` identity, and `left_to_ci`. The brief names `dev/audit/rca/open_prepr_6d.sh 6671786843` instead. That script runs 6671786843's own predictor, which this branch does not change, so it cannot read the fix. The arms harness holds the diff fixed and varies the predictor. Both commits were timed on one 4-CPU cloud container, one after the other (05:43–07:21 UTC 2026-11-25), while self-test and gate runs shared the host for part of each.

- `python3 dev/audit/harnesses/prepr_6d_arms.py e3cb5c019b464a770cc7c6fe2fbc858ed29debf7` (before): wall_s=3202, ARM step-replay 1440.4, ARM graders 351.5, ARM selftest-scope 1389.9, left_to_ci=0, predict_sha1=667f424865b4edf1d61868b956d64ea4ae23d7ab predict_lines=4.
- `python3 dev/audit/harnesses/prepr_6d_arms.py 026ea0ea9b3dc32ee9f672e7bc78f4b6aeaffd96` (after): wall_s=2670, ARM step-replay 808.1, ARM graders 371.8, ARM selftest-scope 1467.8, left_to_ci=49, predict_sha1=667f424865b4edf1d61868b956d64ea4ae23d7ab predict_lines=4.
- After the fix the PREDICT set is unchanged (same sha1). STEP REPLAY's own time falls by 632 s; the rest of the wall time is the arms this PR does not touch.
- The budget gates when a replay may start; it does not interrupt one. The arm can therefore pass 600 s by one step's replay, here 808 s, a bound `HPO_STEP_REPLAY_TIMEOUT_S` sets per step.
- The harness's `REPLAY` lines count base-side replays as well as head ones (`step_replay_preds`'s second `replay_step` call): 77 before, 22 after.
- SELFTEST SCOPE (1390–1468 s) is the remaining large arm. It is outside both countermeasures; this PR's harness times it per arm.
- Null control: `python3 dev/audit/harnesses/prepr_6d_arms.py <commit> custom_components/heatpump_optimizer/currency.py` touches one production file. At e3cb5c019b464a770cc7c6fe2fbc858ed29debf7: wall_s=334, ARM step-replay 331.6, left_to_ci=0. At 026ea0ea9b3dc32ee9f672e7bc78f4b6aeaffd96: wall_s=340, ARM step-replay 336.8, left_to_ci=0. Both have predict_sha1=da39a3ee5e6b4b0d3255bfef95601890afd80709 and predict_lines=0. Under the budget nothing is left and the timings agree, so the full diff's 632 s drop is the budget, not the host. The same run shows that even one keyed production file costs STEP REPLAY minutes, not seconds, which is the premise the corrected comment states.
- Scoped gate: `python3 tests/closure.py select --diff e3cb5c019b464a770cc7c6fe2fbc858ed29debf7` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. `tests/doc_claims.py` rc=0 and `tests/entities.py` rc=0, both with `PYTHONPATH=tests/hastub`. `python3 tests/structure.py` rc=0.

## Unpinned sites

On `tools/pr/prepr.sh`, every added line now has a check that kills its mutant: the per-step `[Ns]` field (pp1 to pp3 in review), `summary_end`'s elapsed (pp4b), and the main flow's `PRE-PR:` line elapsed (pp5). `mutant_run.py` generates no mutant on shell lines, so these were applied by hand (`## Mutation proof`).

prepr's diff-mutant step (`mutants_line`, `MUTANT_CMD="env PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --self-test"`, `MUTANT_IN_PLACE=1`) was re-run at 6403d46419 and on a local, unpushed merge of 6403d46419 into origin/main 1d3077736d4a. Both runs printed `mutant_run rc=3 measured nothing: BASELINE FAILS: the command fails on the unedited tree; no mutant was run`. On that macOS host, the unmutated `ci_predict.py --self-test` fails five wave-script cases. Each shows `AGREEMENT DIVERGENT raise-justification` (`budget_raise_gate.py justification=false`, `policy_lint.mjs raiseJustification=true`), and the merged tree fails them too. The reviewer's container ran the same `ci_predict.py` at 114 ok. 6403d46419 does not change `ci_predict.py`, so the four survivors below stand as triaged at afbc0bc485.


prepr's diff-mutant step (`MUTANT_CMD="env PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --self-test"`, `MUTANT_IN_PLACE=1`) left these survivors on the head's added lines; each is a written triage:

- `tools/pr/ci_predict.py:596 CONST_SWAP` (`STEP_REPLAY_BUDGET = 601`): a tuning value, not a behaviour. A value check would only restate the constant. The value is the measured choice in 18c2df3b6a's message: 300 s left to CI the recorded-reader step whose replay predicted slim-p2's one STEP REPLAY red, and 600 replays it. The behaviour, a budget spent or not, is driven through `HPO_STEP_REPLAY_BUDGET_S` at both ends by the self-test.
- `tools/pr/ci_predict.py:647 CMP_BOUND` (`spent > budget`): equivalent. `spent` is a sum of `time.monotonic()` deltas, so only exact float equality with the budget tells `>=` from `>`, and no input reaches that deterministically.
- `tools/pr/ci_predict.py:835 STMT_DEL` and `tools/pr/ci_predict.py:850 STMT_DEL` (`bad += not good`, `bad += not held`): the self-test's failure counters, read only when their check fails, so on a green tree deleting one changes nothing. Line 850 is the count behind the budget and order mutants' rc=1 under `## Mutation proof`, so it counts when its check fails.

## Red checks

none

## Forward-carry

none

## Friction

none

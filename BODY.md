Main-red hotfix: `governance / instrument-self-tests` red on main. Its step "Refuse a self-test read set the committed table misses" refuses read sets the committed `tools/ci/selftest_closures.json` misses. There are two causes, and this PR closes both.

**Cause 1: a racily clean git index (prepr's moving read set).** A fresh checkout leaves every file it wrote in the index's own mtime second "racily clean". Those are the alphabetical tail of the checkout, because git writes files in index order. The first index-refreshing git command (`git status`) run in the real checkout opens and hashes each racy file. Under strace those opens fold into whichever traced step ran that command first. In run 42780661829 that was prepr's `WIRE_PORC=$(git status --porcelain)`, in the red-check-arm wiring block of `tools/pr/prepr.sh`. The read set moves with scheduling and checkout timing, not with the tree.

**Fix 1: `selftest_scope.py settle`.** It waits until the clock is past the newest tracked file's mtime second, then runs `git update-index -q --really-refresh --force-write-index`. It verifies with `racy_entries`, retries up to three times with a 1.1 s margin, and refuses (rc 1) if any entry is left or a file is stamped in the future. It runs untraced in CI's `strace` step, before `launch`, and as `record`'s first act.

**Repair for the round-1 block (mutation-vacuous).** Two lines were pinned by nothing: the CI settle call in `governance.yml` and the `settle` CLI dispatch. They are pinned now:
- `settle_gaps()` refuses a job in which no untraced step ordered before the first traced one runs `python3 -I tools/ci/selftest_scope.py settle` on a line of its own. The first traced step is a gated step, or `launch`, which starts traced steps. A swallowed `|| true` is refused too.
- `static_check` (the pull-request side) and the self-test's live-job check run `settle_gaps`. The self-test reads the job file passed with `--self-test --workflow PATH`, so `selftest_scope_mutants.sh` can hand it a mutated `governance.yml`.
- The self-test drives `main(["settle"])` over the racy fixture.

Design choice: the settle call is pinned by a static read because the strace step runs only when `SELFTEST_TRACE` is set, which it never is on a pull request.

**Cause 2: steps whose read sets main's own changes widened.** Many steps read files their committed entries miss. `post-merge-record-line`, `plan-page`, `handover-prompt`, `state-doc-writer`, `roster-queue-runner` and `post-merge-bookkeeping` miss `tests/layout.py` and `tools/policy/budget_raise_gate.py`. `open-pr`, `update-pr`, `pr-args`, `hooks-setup`, `field-coverage` and `selftest-wiring` miss `tools/audit/seat/survivor_list.py`. `beat-job-rows`, `cloud-relay`, `verdict-bus` and others miss other files. **Fix 2:** each refused step is re-recorded by the instrument's own path (`python3 -I tools/ci/selftest_scope.py record --step ID ...`, Linux, strace). Each was recorded in a fresh worktree of this branch merged with origin/main, so it measures the tree main will have after the merge. No read set was hand-edited, and `tests/closures.json` was not derived.

Alternatives that lost:
- **Re-record prepr from a run's `selftest-closures` artifact, without `settle`.** That bakes one run's racy tail into the table, and the next run's tail starts elsewhere.
- **Scope `WIRE_PORC` to its fixture directory.** That weakens the whole-worktree guard and only moves the first index refresh to another step.
- **Drop opens by `git status` in `fold_trace`.** That hides real content reads in a dirty tree, and `git diff` pays the same racy reads.
- **Commit main's uploaded `selftest-closures` artifact via `check --write`.** That replaces every entry with one CI run's measurement, which carries cause 1's racy tail (no settle on main). `record --step` re-measures only the refused steps.

Root cause: `dev/audit/rca/R10-RCA-MAIN-SELFTESTS-RED.md` (group R10-RCA-MAIN-SELFTESTS-RED, already run). Cause 1 is its shape 2 (a read set that moves between runs of one tree).

## Head

6eaabd8038151452dc9496ec38c2eb82befe8953. It sits on 245ddf7876bf9662937d4e9077172e1e3cd2275a (the round-1 head) plus three commits: the settle pins (33ace0c69c), the 20-step re-record (dffd0d7e92), and the `verdict-bus` re-record against d08ed31049. The merge base with origin/main is 30c785330fc727ae26d6a6d2d51b38f1856fe87c. `git merge-tree --write-tree origin/main HEAD` is clean at origin/main d08ed31049cd3636cde4d2fdeb3bd7cd4b3c842a. Stamped 2026-11-11T03:10Z.

## Mutation proof

`sh tools/ci/selftest_scope_mutants.sh --self-test` at 33ace0c69c ends `SELFTEST-SCOPE MUTANTS: every mutant refused`. Its unmutated baseline must pass first; that is the null control. The new mutants and the checks that go red:
- `the settle command a no-op` (`return settle_index(root)` → `return 0`, the reviewer's surviving mutant 2): `FAIL the \`settle\` command settles that racy index (rc=0; racy before it, none after)`.
- `CI never settles the index` (the governance.yml line → `true`, the reviewer's surviving mutant 1, handed in through `--workflow`): `FAIL the live job settles the index in an untraced step before its first traced one`.
- `CI swallows a failed settle` (→ `... settle || true`): the same check fails.
- `static skips the settle check` (`problems = wiring_gaps(steps) + settle_gaps(steps)` → `problems = wiring_gaps(steps)`): `FAIL static: a job that never settles the index is refused (UNSETTLED)`.
- `settle_gaps reads no job` (its `if any(...)` → `if True or any(...)`): 5 checks fail (`static: ... UNSETTLED` and the four `settle_gaps: ... is refused` fixtures).
- `settle never rewrites the index` (from round 1) is still killed: 10 checks fail, including `FAIL settle: no index entry is left racily clean (rc=1)`.

The re-recorded table needs no mutant of its own: the job's drift step is its check. A replay at the pre-re-record head refuses (34 refusals, Figures), and one at the re-recorded head does not.

## Null control

- The `settle_gaps` fixtures start with a job that settles in an untraced step before the first traced one, which passes. Each refused shape varies that one job.
- The self-test's racy fixture: `racy_entries` names all three files stamped in the index's own second, and a traced `git status` opens all three. After `settle` (or `main(["settle"])`) none is racy, and the status opens none.
- Re-record: the same full traced replay and `check`, run against the unmodified table at the merge base and at the pre-re-record head. Both refuse (Figures).

## Figures

Every refusal count below is the last line of `selftest_scope check`. It is one per `UNDER-SCOPED`/`STALE`/`UNRECORDED`/`UNMEASURED`/`EXTRA` line, `drift()`'s rule, printed by `python3 -I tools/ci/selftest_scope.py check --traces <dir>/selftest-trace` in the worktree named. `<dir>` is a full traced replay of the job. It comes from a 13-line scratch driver: `record`'s own loop (`selftest_scope.record(root, None, out)`), with `tempfile.mkdtemp` pointed at `<dir>` and its `rmtree` skipped, so the traces outlive the record. Then `check_cli` runs over them. The driver is not in the tree, and the replay is what CI's traced job does.

- Merge base 30c785330f, its own code and table: `111 gated step(s), 12 refusal(s)`. The brief's 32 (main 45adb0c3b4, CI) is a different tree; it is not carried.
- This branch at 33ace0c69c merged with origin/main 45adb0c3b4 (scratch merge 1c20949189), before any re-record: `111 gated step(s), 34 refusal(s)` across 20 steps. That covers main's 32-line family (post-merge-record-line, plan-page, handover-prompt, beat-job-rows, hooks-setup, open-pr, update-pr and the rest). It also covers `selftest-scope`/`selftest-scope-mutants` probing `.github` (this PR's `--workflow` read) and `prepr` reading `tools/policy/fixtures/required-contexts.json`. That last one is the environment read disclosed in round 1, read only when the live ruleset requires `gate`; recording it is an over-approximation.
- Those 20 steps were re-recorded there: `python3 -I tools/ci/selftest_scope.py record --step beat-job-rows --step carry-check-and-the --step cloud-relay --step field-coverage --step handover-prompt --step hooks-setup --step open-pr --step plan-page --step post-merge-bookkeeping --step post-merge-record-line --step pr-args --step prepr --step roster-queue-runner --step self-tests-outside-seat --step selftest-scope --step selftest-scope-mutants --step selftest-wiring --step state-doc-writer --step update-pr --step verdict-bus` printed `recorded 20 step(s) ... 1 failed ['verdict-bus'], 0 broken trace(s)` (see Friction).
- This branch at dffd0d7e92 merged with origin/main d08ed31049 (scratch merge eed6918ec8, fresh worktree), full replay: `recorded 111 step(s) ... 0 failed [], 0 broken trace(s)`, then `111 gated step(s), 3 refusal(s)`. All three are `verdict-bus` reading `dev/programme/rosters/`, which main's #3366 added after 45adb0c3b4. `record --step verdict-bus` there printed `recorded 1 step(s) ... 0 failed`.
- **Done criterion:** `check` over that same replay's traces against the re-recorded table, in that merged tree: `selftest_scope check: 111 gated step(s), 0 refusal(s)`. The `verdict-bus` entry is from its own re-record run, and the other 110 steps' traces are the replay's. The same table is committed at 6eaabd8038 (byte-identical to the merged tree's: `cp`, then `diff` printed the three `dev/programme/rosters` lines only against the parent).
- `python3 -I tools/ci/selftest_scope.py static` at 6eaabd8038: `111 gated step(s), 0 problem(s)`.
- `python3 -I tools/ci/selftest_scope.py --self-test` at 6eaabd8038, untraced with strace on PATH: `117 checks, 0 failed`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL` (`tools/ci/selftest_closures.json changes the gate itself`), so the full suite is CI's.

## Red checks

none

## Forward-carry

- `dev/audit/rca/R10-RCA-MAIN-SELFTESTS-RED.md`, class R10-RCA-MAIN-SELFTESTS-RED shape 2 (a read set that moves between runs of one tree): here the moving part was the index state the checkout left, and this PR builds that countermeasure (`settle`, now pinned in the job by `settle_gaps`). Carry: dismissed: R10-RCA-MAIN-SELFTESTS-RED is resume.stage done, and the countermeasure lands in this PR

## Friction

- selftest-scope-record: cost: `bash tools/audit/seat/bus.sh --self-test` failed one check when traced under local load, in two replays (`1 failed ['verdict-bus']`, 131.5 s and 152.9 s). It passed in the d08ed31049 replay and untraced (`bus self-test: 164 checks, 0 failed`); its trace was whole (`0 broken trace(s)`), so the measured read set stands. Carry: dismissed: a local timing failure under strace, not reproduced untraced or on the final replay, and the job's own traced run on main is its detector
